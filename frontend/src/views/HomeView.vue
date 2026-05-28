<template>
  <div class="home">
    <div class="home-header">
      <span class="logo">📰</span>
      <h1>新闻爬取 · AI解读 · 发布系统</h1>
    </div>
    <div class="cards-row">
      <div class="entry-card" @click="$router.push('/kb')">
        <div class="card-icon">📚</div>
        <h2>知识库</h2>
        <p class="card-desc">上传文档资料，AI智能检索问答</p>
        <ul class="card-features">
          <li>上传 PDF / Word / TXT</li>
          <li>RAG 语义检索</li>
          <li>多风格文章生成</li>
        </ul>
        <div class="card-arrow">→</div>
      </div>
      <div class="entry-card" @click="$router.push('/news')">
        <div class="card-icon">📰</div>
        <h2>新闻</h2>
        <p class="card-desc">爬取实时新闻，AI深度解读</p>
        <ul class="card-features">
          <li>多源新闻爬取</li>
          <li>AI 深度解读</li>
          <li>多平台一键发布</li>
        </ul>
        <div class="card-arrow">→</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.home {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0f2f5 0%, #eef2ff 50%, #f0f9ff 100%);
  gap: 48px;
}

.home-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.home-header .logo {
  font-size: 36px;
}

.home-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
}

.cards-row {
  display: flex;
  gap: 32px;
}

.entry-card {
  width: 320px;
  padding: 36px 32px;
  background: #fff;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.entry-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 40px rgba(99, 102, 241, 0.12);
  border-color: #a5b4fc;
}

.entry-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #818cf8, #6366f1);
  opacity: 0;
  transition: opacity 0.3s;
}

.entry-card:hover::before {
  opacity: 1;
}

.card-icon {
  font-size: 42px;
  margin-bottom: 16px;
}

.entry-card h2 {
  font-size: 22px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px;
}

.card-desc {
  font-size: 14px;
  color: #64748b;
  margin: 0 0 16px;
}

.card-features {
  list-style: none;
  padding: 0;
  margin: 0;
}

.card-features li {
  font-size: 13px;
  color: #94a3b8;
  padding: 4px 0;
  padding-left: 16px;
  position: relative;
}

.card-features li::before {
  content: '✦';
  position: absolute;
  left: 0;
  color: #a5b4fc;
  font-size: 11px;
}

.card-arrow {
  position: absolute;
  right: 24px;
  bottom: 24px;
  font-size: 20px;
  color: #c7d2fe;
  transition: all 0.3s;
}

.entry-card:hover .card-arrow {
  color: #6366f1;
  transform: translateX(4px);
}
</style>
