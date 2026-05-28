"""Knowledge base API routes: upload, list, delete, search, RAG chat, RAG generate."""

from __future__ import annotations

import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from config import UPLOAD_DIR, LLM_API_KEY, LLM_BASE_URL
from database import (
    save_kb_doc,
    load_kb_docs,
    delete_kb_doc,
    save_kb_chunks,
    load_kb_chunk_texts,
)
from knowledge.embeddings import DashScopeEmbedding
from knowledge.chunker import TextChunker, Chunk
from knowledge.vectorstore import FAISSVectorStore
from knowledge.loader import DocumentLoader

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}

embedding_client = DashScopeEmbedding()
chunker = TextChunker()
loader = DocumentLoader()
vector_store = FAISSVectorStore()


KB_RAG_SYSTEM_PROMPT = """\
你是知识库AI助手。以下是从知识库中检索到的相关文档片段，请基于这些内容回答用户问题。

规则：
- 严格基于知识库内容回答，不得编造知识库中未提及的信息
- 引用知识库内容时，标注来源文件名
- 如果知识库中没有相关信息，请明确说明"知识库中暂无相关信息"
- 回复使用中文
"""

KB_GENERATE_SYSTEM_PROMPT = """\
你是资深财经内容创作者。以下是从知识库中检索到的相关内容，请基于这些内容生成文章。

规则：
- 严格基于知识库内容，不得编造数据
- 引用数据标注来源文件
- 回复使用中文
"""


# ── Upload ──────────────────────────────────────────────────────

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "No filename")

    ext = Path(file.filename).suffix.lower()
    if ext not in loader.SUPPORTED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {ext}. Supported: {loader.SUPPORTED_EXTENSIONS}")

    upload_dir = Path(UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    doc_id = uuid.uuid4().hex[:16]
    save_path = upload_dir / f"{doc_id}{ext}"

    content = await file.read()
    save_path.write_bytes(content)

    try:
        doc = loader.load(save_path, doc_id=doc_id)
    except Exception as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(500, f"Failed to parse document: {e}")

    if not doc.text.strip():
        save_path.unlink(missing_ok=True)
        raise HTTPException(400, "Document has no extractable text")

    chunks = chunker.chunk_with_pages(doc.pages, doc_id=doc_id)
    if not chunks:
        save_path.unlink(missing_ok=True)
        raise HTTPException(400, "Document too short to chunk")

    try:
        texts = [c.text for c in chunks]
        vectors = embedding_client.embed(texts)
    except Exception as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(500, f"Embedding failed: {e}")

    chunk_ids = [c.chunk_id for c in chunks]
    vector_store.add(chunk_ids, vectors)

    chunk_dicts = [
        {
            "chunk_id": c.chunk_id,
            "doc_id": doc_id,
            "chunk_index": c.chunk_index,
            "page": c.page,
            "text": c.text,
        }
        for c in chunks
    ]
    await save_kb_chunks(chunk_dicts)

    doc_record = {
        "doc_id": doc_id,
        "filename": file.filename,
        "file_type": ext,
        "chunk_count": len(chunks),
        "file_size": len(content),
        "upload_time": "",
        "status": "ready",
    }
    await save_kb_doc(doc_record)

    return {
        "doc_id": doc_id,
        "filename": file.filename,
        "chunk_count": len(chunks),
        "file_size": len(content),
    }


# ── List ────────────────────────────────────────────────────────

@router.get("/documents")
async def list_documents():
    docs = await load_kb_docs()
    total_chunks = sum(d.get("chunk_count", 0) for d in docs)
    return {"documents": docs, "total_chunks": total_chunks}


# ── Delete ──────────────────────────────────────────────────────

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    deleted_chunk_ids = await delete_kb_doc(doc_id)
    if deleted_chunk_ids:
        vector_store.remove_by_doc(set(deleted_chunk_ids))

    upload_dir = Path(UPLOAD_DIR)
    for ext in loader.SUPPORTED_EXTENSIONS:
        p = upload_dir / f"{doc_id}{ext}"
        if p.exists():
            p.unlink()

    return {"deleted": True, "doc_id": doc_id, "chunks_removed": len(deleted_chunk_ids)}


# ── Search ──────────────────────────────────────────────────────

class KBSearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)


@router.post("/search")
async def search_knowledge(req: KBSearchRequest):
    if vector_store.total_vectors == 0:
        return {"results": [], "total": 0}

    try:
        query_vec = embedding_client.embed_query(req.query)
    except Exception as e:
        raise HTTPException(500, f"Embedding query failed: {e}")

    hits = vector_store.search(query_vec, top_k=req.top_k)
    if not hits:
        return {"results": [], "total": 0}

    chunk_ids = [cid for cid, _ in hits]
    score_map = {cid: score for cid, score in hits}
    chunk_data = await load_kb_chunk_texts(chunk_ids)

    results = []
    for cid in chunk_ids:
        if cid in chunk_data:
            cd = chunk_data[cid]
            preview = cd["text"][:120] + ("..." if len(cd["text"]) > 120 else "")
            results.append({
                "chunk_id": cid,
                "doc_id": cd["doc_id"],
                "filename": cd["filename"],
                "page": cd["page"],
                "text": cd["text"],
                "preview": preview,
                "score": round(score_map.get(cid, 0), 4),
            })

    return {"results": results, "total": len(results)}


# ── RAG Chat (SSE stream) ──────────────────────────────────────

class KBChatRequest(BaseModel):
    message: str
    doc_ids: list[str] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=10)


@router.post("/chat/stream")
async def kb_chat_stream(req: KBChatRequest):
    if vector_store.total_vectors == 0:
        raise HTTPException(400, "Knowledge base is empty. Please upload documents first.")

    try:
        query_vec = embedding_client.embed_query(req.message)
    except Exception as e:
        raise HTTPException(500, f"Embedding failed: {e}")

    hits = vector_store.search(query_vec, top_k=req.top_k)
    chunk_ids = [cid for cid, _ in hits]
    chunk_data = await load_kb_chunk_texts(chunk_ids)

    context_parts = []
    for cid in chunk_ids:
        if cid in chunk_data:
            cd = chunk_data[cid]
            page_info = f", 第{cd['page']}页" if cd.get("page", 0) > 0 else ""
            context_parts.append(f"[来源: {cd['filename']}{page_info}]\n{cd['text']}")

    context_text = "\n\n".join(context_parts) if context_parts else "（未检索到相关内容）"

    full_system = KB_RAG_SYSTEM_PROMPT + f"\n\n【知识库内容】\n{context_text}"

    async def event_stream():
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import SystemMessage, HumanMessage

        llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=0.7,
            openai_api_key=LLM_API_KEY,
            openai_api_base=LLM_BASE_URL,
            request_timeout=120,
            max_retries=2,
        )

        prompt_text = f"[System]\n{full_system}\n\n[User]\n{req.message}"
        yield f"data: {json.dumps({'type': 'prompt', 'content': prompt_text}, ensure_ascii=False)}\n\n"

        sources = [{"filename": chunk_data[cid]["filename"], "page": chunk_data[cid].get("page", 0), "score": round(score, 4), "text": chunk_data[cid]["text"], "preview": chunk_data[cid]["text"][:80] + ("..." if len(chunk_data[cid]["text"]) > 80 else "")}
                   for cid, score in hits if cid in chunk_data]
        if sources:
            yield f"data: {json.dumps({'type': 'sources', 'sources': sources}, ensure_ascii=False)}\n\n"

        messages = [
            SystemMessage(content=full_system),
            HumanMessage(content=req.message),
        ]

        try:
            async for chunk in llm.astream(messages):
                if chunk.content:
                    data = json.dumps({"type": "chunk", "content": chunk.content}, ensure_ascii=False)
                    yield f"data: {data}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )


# ── RAG Generate Article (SSE stream) ──────────────────────────

class KBGenerateRequest(BaseModel):
    message: str = ""
    style: str = "wechat_mp"
    doc_ids: list[str] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=10)


@router.post("/generate/stream")
async def kb_generate_stream(req: KBGenerateRequest):
    if vector_store.total_vectors == 0:
        raise HTTPException(400, "Knowledge base is empty. Please upload documents first.")

    query = req.message or "总结知识库核心内容"
    try:
        query_vec = embedding_client.embed_query(query)
    except Exception as e:
        raise HTTPException(500, f"Embedding failed: {e}")

    hits = vector_store.search(query_vec, top_k=req.top_k)
    chunk_ids = [cid for cid, _ in hits]
    chunk_data = await load_kb_chunk_texts(chunk_ids)

    context_parts = []
    for cid in chunk_ids:
        if cid in chunk_data:
            cd = chunk_data[cid]
            page_info = f", 第{cd['page']}页" if cd.get("page", 0) > 0 else ""
            context_parts.append(f"[来源: {cd['filename']}{page_info}]\n{cd['text']}")

    context_text = "\n\n".join(context_parts) if context_parts else "（未检索到相关内容）"

    style_labels = {"xiaohongshu": "小红书", "wechat_mp": "微信公众号", "douyin": "抖音"}
    style_label = style_labels.get(req.style, req.style)

    full_system = KB_GENERATE_SYSTEM_PROMPT + f"\n\n【知识库内容】\n{context_text}"

    style_hints = {
        "xiaohongshu": "请用小红书风格生成：emoji开头标题、短段落口语化、关键数字用类比、结尾互动引导+话题标签、800字以内",
        "wechat_mp": "请用公众号风格生成：简洁有力标题、开头用数据切入、分2-4节含事实+逻辑+数据、影响研判、前瞻判断、1200-1800字",
        "douyin": "请用抖音风格生成：极简数字标题、短平快每句不超20字、3个要点节奏感、数字口语化、200-300字",
    }
    human = req.message or f"请基于知识库内容生成一篇{style_label}风格的文章"
    if req.style in style_hints:
        human += f"\n\n{style_hints[req.style]}"

    async def event_stream():
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import SystemMessage, HumanMessage

        llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=0.7,
            openai_api_key=LLM_API_KEY,
            openai_api_base=LLM_BASE_URL,
            request_timeout=120,
            max_retries=2,
        )

        prompt_text = f"[System]\n{full_system}\n\n[User]\n{human}"
        yield f"data: {json.dumps({'type': 'prompt', 'content': prompt_text}, ensure_ascii=False)}\n\n"

        sources = [{"filename": chunk_data[cid]["filename"], "page": chunk_data[cid].get("page", 0), "score": round(score, 4), "text": chunk_data[cid]["text"], "preview": chunk_data[cid]["text"][:80] + ("..." if len(chunk_data[cid]["text"]) > 80 else "")}
                   for cid, score in hits if cid in chunk_data]
        if sources:
            yield f"data: {json.dumps({'type': 'sources', 'sources': sources}, ensure_ascii=False)}\n\n"

        messages = [
            SystemMessage(content=full_system),
            HumanMessage(content=human),
        ]

        try:
            async for chunk in llm.astream(messages):
                if chunk.content:
                    data = json.dumps({"type": "chunk", "content": chunk.content}, ensure_ascii=False)
                    yield f"data: {data}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )


# ── Internal search (for agent tool) ──────────────────────────

async def kb_search_internal(query: str, top_k: int = 5) -> str:
    if vector_store.total_vectors == 0:
        return "知识库为空，暂无可用文档。"

    try:
        query_vec = embedding_client.embed_query(query)
    except Exception as e:
        return f"检索知识库失败：{e}"

    hits = vector_store.search(query_vec, top_k=top_k)
    if not hits:
        return "未在知识库中找到与查询相关的内容。"

    chunk_ids = [cid for cid, _ in hits]
    chunk_data = await load_kb_chunk_texts(chunk_ids)

    results = []
    for cid, score in hits:
        if cid in chunk_data:
            cd = chunk_data[cid]
            page_info = f", 第{cd['page']}页" if cd.get("page", 0) > 0 else ""
            results.append(f"[来源: {cd['filename']}{page_info}, 相关度: {score:.2f}]\n{cd['text']}")

    return "\n\n".join(results)
