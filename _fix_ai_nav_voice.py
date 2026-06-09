"""修复 AI 栏目导航高亮 + 语音输入功能 + 移除多模型面板"""

p = r'C:\工作场地\geo-logistics-app\index.html'
with open(p, 'rb') as f:
    raw = f.read()
d = raw[3:].decode('utf-8') if raw[:3] == b'\xef\xbb\xbf' else raw.decode('utf-8')
has_bom = raw[:3] == b'\xef\xbb\xbf'
print(f'File: {len(d)} chars')

import re

# ══════════════════════════════════════════════════════
# 1. 修复 navigateTo：AI 分支也要更新 nav-item active 状态
# ══════════════════════════════════════════════════════
old_ai_block = """  if(nav==='ai'||nav==='ai-multi'){
    showPage('pageAI');
    currentNav='ai';
    renderSidebar('ai');
    return;
  }
  if(nav.startsWith('ai-')){
    const modelId=nav;
    showPage('pageAIChat');
    currentNav='ai';
    renderSidebar('ai');
    window.aiChatModel=modelId;
    window.aiChatHistory=aiChatHistories[modelId]||[];
    window.aiChatMessages=[];
    renderAIChatHistory();
    renderAIChatMessages();
    return;
  }"""

new_ai_block = """  // AI 导航高亮
  const isAI = nav === 'ai' || nav === 'ai-multi' || nav.startsWith('ai-');
  document.querySelectorAll('.nav-item').forEach(n => n.classList.toggle('active', n.dataset.nav === (isAI ? 'ai' : nav)));
  
  if(nav === 'ai' || nav === 'ai-multi'){
    currentNav = 'ai';
    renderSidebar('ai');
    showPage('pageAIChat');
    window.aiChatModel = null;
    window.aiChatMessages = [];
    renderAIChatMessages();
    return;
  }
  if(nav.startsWith('ai-')){
    const modelId = nav;
    currentNav = 'ai';
    renderSidebar('ai');
    showPage('pageAIChat');
    window.aiChatModel = modelId;
    window.aiChatHistory = aiChatHistories[modelId] || [];
    window.aiChatMessages = [];
    renderAIChatHistory();
    renderAIChatMessages();
    aiSetModelInfo(modelId);
    return;
  }"""

cnt = d.count(old_ai_block)
print(f'Old AI block found: {cnt}')
if cnt == 1:
    d = d.replace(old_ai_block, new_ai_block)
    print('[OK] navigateTo AI block replaced')

# ══════════════════════════════════════════════════════
# 2. 修改 SIDEBAR_MAP：ai 子工具列表（仅单模型）
# ══════════════════════════════════════════════════════
old_sidebar = """  home:[],
  ai:[
    {id:'ai-multi',icon:'<svg viewBox="0 0 16 16" fill="none" stroke="#7c6aef" stroke-width="1.5"><circle cx="5" cy="8" r="2.5"/><circle cx="11" cy="5" r="2"/><circle cx="11" cy="11" r="2"/><path d="M7 8h2M10 6l2-1.5M10 10l2 1.5"/></svg>',labelKey:'aiMultiMode'},
    {id:'ai-openai',icon:'<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6" stroke="#10a37f" stroke-width="1.5"/><path d="M8 4v4l3 1.5" stroke="#10a37f" stroke-width="1.5"/></svg>',labelKey:'aiOpenAI'},
    {id:'ai-claude',icon:'<svg viewBox="0 0 16 16" fill="none"><polygon points="8,2 14,13 2,13" stroke="#d97706" stroke-width="1.5" fill="none"/></svg>',labelKey:'aiClaude'},
    {id:'ai-gemini',icon:'<svg viewBox="0 0 16 16" fill="none"><path d="M8 2L2 6l6 4 6-4L8 2zM2 11l6 3 6-3M2 8.5l6 3 6-3" stroke="#4285f4" stroke-width="1.2"/></svg>',labelKey:'aiGemini'},
    {id:'ai-deepseek',icon:'<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6" stroke="#4d6bfe" stroke-width="1.5"/><path d="M8 2v12M2 8h12" stroke="#4d6bfe" stroke-width="1.5"/></svg>',labelKey:'aiDeepSeek'},
    {id:'ai-qwen',icon:'<svg viewBox="0 0 16 16" fill="none"><rect x="2" y="2" width="12" height="12" rx="2" stroke="#6366f1" stroke-width="1.5"/><path d="M6 8h4M8 6v4" stroke="#6366f1" stroke-width="1.5"/></svg>',labelKey:'aiQwen'},
    {id:'ai-kimi',icon:'<svg viewBox="0 0 16 16" fill="none"><path d="M8 2l3 6h5l-4 3.5 1.5 5.5L8 13.5 2.5 17l1.5-5.5L1 8h5z" stroke="#8b5cf6" stroke-width="1.2"/></svg>',labelKey:'aiKimi'},
    {id:'ai-zhipu',icon:'<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="5.5" stroke="#3b82f6" stroke-width="1.5"/><path d="M6 8h4M8 6v4" stroke="#3b82f6" stroke-width="1.5"/></svg>',labelKey:'aiYiYi'},
    {id:'ai-yi',icon:'<svg viewBox="0 0 16 16" fill="none"><polygon points="8,2 14,8 8,14 2,8" stroke="#06b6d4" stroke-width="1.5" fill="none"/></svg>',labelKey:'aiYi'},
    {id:'ai-mistral',icon:'<svg viewBox="0 0 16 16" fill="none"><path d="M8 2L2 6v4l6 4 6-4V6L8 2z" stroke="#f97316" stroke-width="1.5" fill="none"/></svg>',labelKey:'aiMistral'},
    {id:'ai-meta',icon:'<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6" stroke="#0081fb" stroke-width="1.5"/><circle cx="6" cy="7" r="1.5" stroke="#0081fb" stroke-width="1.2"/><circle cx="10" cy="7" r="1.5" stroke="#0081fb" stroke-width="1.2"/><path d="M6 10a4 4 0 01-2-3" stroke="#0081fb" stroke-width="1.2"/></svg>',labelKey:'aiMeta'},
  ],"""

new_sidebar = """  home:[],
  ai:[
    {id:'ai-openai',icon:'<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6" stroke="#10a37f" stroke-width="1.5"/></svg>',labelKey:'aiOpenAI'},
    {id:'ai-claude',icon:'<svg viewBox="0 0 16 16" fill="none"><polygon points="8,2 14,13 2,13" stroke="#d97706" stroke-width="1.5" fill="none"/></svg>',labelKey:'aiClaude'},
    {id:'ai-gemini',icon:'<svg viewBox="0 0 16 16" fill="none"><path d="M8 2L2 6l6 4 6-4L8 2z" stroke="#4285f4" stroke-width="1.5"/></svg>',labelKey:'aiGemini'},
    {id:'ai-deepseek',icon:'<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6" stroke="#4d6bfe" stroke-width="1.5"/></svg>',labelKey:'aiDeepSeek'},
    {id:'ai-qwen',icon:'<svg viewBox="0 0 16 16" fill="none"><rect x="2" y="2" width="12" height="12" rx="2" stroke="#6366f1" stroke-width="1.5"/></svg>',labelKey:'aiQwen'},
    {id:'ai-kimi',icon:'<svg viewBox="0 0 16 16" fill="none"><path d="M8 2l3 6h5l-4 3.5 1.5 5.5L8 13.5" stroke="#8b5cf6" stroke-width="1.5"/></svg>',labelKey:'aiKimi'},
    {id:'ai-zhipu',icon:'<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6" stroke="#3b82f6" stroke-width="1.5"/></svg>',labelKey:'aiZhipu'},
    {id:'ai-yi',icon:'<svg viewBox="0 0 16 16" fill="none"><polygon points="8,2 14,8 8,14 2,8" stroke="#06b6d4" stroke-width="1.5" fill="none"/></svg>',labelKey:'aiYi'},
    {id:'ai-mistral',icon:'<svg viewBox="0 0 16 16" fill="none"><path d="M8 2L2 6v4l6 4 6-4V6L8 2z" stroke="#f97316" stroke-width="1.5" fill="none"/></svg>',labelKey:'aiMistral'},
    {id:'ai-meta',icon:'<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6" stroke="#0081fb" stroke-width="1.5"/></svg>',labelKey:'aiMeta'},
  ],"""

cnt2 = d.count(old_sidebar)
print(f'Old SIDEBAR_MAP found: {cnt2}')
if cnt2 == 1:
    d = d.replace(old_sidebar, new_sidebar)
    print('[OK] SIDEBAR_MAP ai updated')

# ══════════════════════════════════════════════════════
# 3. 移除 pageAI，仅保留 pageAIChat
# ══════════════════════════════════════════════════════
pageai_start = d.find('<div class="page" id="pageAI">')
pageai_end = d.find('</div>\n    <div class="page" id="pageGeo">', pageai_start)
if pageai_start > 0 and pageai_end > 0:
    d = d[:pageai_start] + d[pageai_end + len('</div>\n    '):]
    print(f'[OK] Removed pageAI, new len={len(d)}')

# ══════════════════════════════════════════════════════
# 4. pageAIChat 增加语音输入按钮
# ══════════════════════════════════════════════════════
# 找到 aiSingleTextarea 附近的输入框，插入语音按钮
old_input = '''<textarea class="ai-textarea" id="aiSingleTextarea"'''
new_input = '''<button class="ai-voice-btn" id="aiSingleVoiceBtn" title="点击说话">
            <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10 2a3 3 0 00-3 3v5a3 3 0 006 0V5a3 3 0 00-3-3z"/><path d="M5 10a5 5 0 0010 0M10 15v3"/></svg>
          </button>
          <textarea class="ai-textarea" id="aiSingleTextarea"'''

cnt3 = d.count(old_input)
print(f'Old input pattern found: {cnt3}')
if cnt3 >= 1:
    d = d.replace(old_input, new_input, 1)
    print('[OK] Voice button injected into pageAIChat input')

# ══════════════════════════════════════════════════════
# 5. CSS：添加 .ai-voice-btn 样式 + 修复 sidebar 高度
# ══════════════════════════════════════════════════════
style_end = d.rfind('</style>')
if style_end > 0:
    voice_css = """
.ai-voice-btn{width:36px;height:36px;border-radius:8px;background:var(--surface2);border:1px solid var(--border2);color:var(--text2);cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .15s;flex-shrink:0}
.ai-voice-btn:hover{border-color:var(--accent);color:var(--accent);background:rgba(124,106,239,0.08)}
.ai-voice-btn.recording{background:rgba(239,68,68,0.15);border-color:#ef4444;color:#ef4444;animation:voice-pulse 1s ease infinite}
.ai-voice-btn svg{width:18px;height:18px}
@keyframes voice-pulse{0%,100%{transform:scale(1);opacity:1}50%{transform:scale(1.1);opacity:.7}}
.sidebar{height:calc(100vh - var(--topbar-h));display:flex;flex-direction:column;background:var(--surface);border-right:1px solid var(--border);width:180px;flex-shrink:0}
"""
    d = d[:style_end] + voice_css + d[style_end:]
    print(f'[OK] Voice CSS injected')

# ══════════════════════════════════════════════════════
# 6. ai-page.js：语音输入逻辑
# ══════════════════════════════════════════════════════
# 重写 ai-page.js 的关键部分
js_path = r'C:\工作场地\geo-logistics-app\ai-page.js'
js_new = '''/* ai-page.js - 科AI 单模型对话 + 语音输入 */

(function () {
  'use strict';

  let aiChatHistories = {};
  let aiChatMessages = [];
  let aiCurrentHistoryId = null;

  const ICONS = {
    openai: '🟢', claude: '🟠', gemini: '🔵', deepseek: '🔵',
    qwen: '🟣', kimi: '🟣', zhipu: '🔵', yi: '🔵',
    mistral: '🟠', meta: '🔵'
  };

  function getIcon(pid) { return ICONS[pid] || '🤖'; }

  function getModelName(mid) {
    for (var pid in (typeof PROVIDERS !== 'undefined' ? PROVIDERS : {})) {
      var models = typeof MODELS !== 'undefined' ? MODELS.filter(function(m){ return m.provider===pid; }) : [];
      for (var i=0;i<models.length;i++) if(models[i].id===mid) return (PROVIDERS[pid]||{}).name+' '+models[i].name;
    }
    return mid;
  }

  function escHtml(s){ return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
  function escAttr(s){ return String(s||'').replace(/"/g,'&quot;'); }

  /* ── 语音输入 ── */
  let mediaRecorder = null;
  let audioChunks = [];
  let isRecording = false;

  async function startVoiceRecording(btnId, textareaId) {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert('您的浏览器不支持语音录制');
      return;
    }
    const btn = document.getElementById(btnId);
    if (!btn) return;

    if (isRecording) {
      stopRecording();
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.ondataavailable = e => { if (e.data.size > 0) audioChunks.push(e.data); };
      mediaRecorder.onstop = async () => {
        const blob = new Blob(audioChunks, { type: 'audio/webm' });
        stream.getTracks().forEach(t => t.stop());
        btn.classList.remove('recording');
        isRecording = false;
        await transcribeAudio(blob, textareaId);
      };

      mediaRecorder.start();
      btn.classList.add('recording');
      isRecording = true;
    } catch (err) {
      console.error('录音失败:', err);
      alert('无法访问麦克风，请检查权限设置');
    }
  }

  function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }
  }

  async function transcribeAudio(blob, textareaId) {
    const textarea = document.getElementById(textareaId);
    if (!textarea) return;
    
    // 显示转写中状态
    const btn = document.getElementById(textareaId.replace('Textarea', 'VoiceBtn'));
    if (btn) btn.title = '正在转写...';

    try {
      const formData = new FormData();
      formData.append('audio', blob, 'recording.webm');
      formData.append('model', 'whisper-1');

      const resp = await fetch('/api/proxy', {
        method: 'POST',
        body: formData
      });
      const data = await resp.json();
      const text = data.text || '';
      if (text) {
        textarea.value += (textarea.value ? ' ' : '') + text;
        textarea.dispatchEvent(new Event('input'));
        textarea.focus();
      }
    } catch (err) {
      console.error('转写失败:', err);
      // 降级：浏览器原生 SpeechRecognition
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SR();
        recognition.lang = 'zh-CN';
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.onresult = (event) => {
          const t = event.results[0][0].transcript;
          textarea.value += (textarea.value ? ' ' : '') + t;
          textarea.dispatchEvent(new Event('input'));
        };
        recognition.start();
      }
    } finally {
      if (btn) btn.title = '点击说话';
    }
  }

  /* ── 单模型对话 ── */
  function aiSingleSend() {
    const textarea = document.getElementById('aiSingleTextarea');
    const msg = textarea ? textarea.value.trim() : '';
    if (!msg || !window.aiChatModel) return;

    const msgsEl = document.getElementById('aiSingleMessages');
    const welcomeEl = document.getElementById('aiSingleWelcome');
    if (!msgsEl) return;
    if (welcomeEl) welcomeEl.style.display = 'none';

    const chatId = window.aiChatModel + '_' + (aiCurrentHistoryId || Date.now().toString());
    aiCurrentHistoryId = chatId;

    if (!aiChatHistories[chatId]) {
      aiChatHistories[chatId] = { id: chatId, title: msg.substring(0, 30), time: new Date().toLocaleString(), messages: [] };
    }
    aiChatHistories[chatId].messages.push({ role: 'user', content: msg });
    aiChatMessages.push({ role: 'user', content: msg });
    renderAIChatMessages();
    renderAIHistory();

    textarea.value = '';

    const loadingId = 'ai-msg-loading-' + Date.now();
    msgsEl.innerHTML += '<div class="ai-msg ai" id="' + loadingId + '"><div class="ai-msg-avatar">' + getIcon(window.aiChatModel.split('-')[0]) + '</div><div class="ai-msg-bubble ai-msg-loading">正在思考...</div></div>';
    msgsEl.scrollTop = msgsEl.scrollHeight;

    const ctrl = new AbortController();
    const timeout = setTimeout(() => ctrl.abort(), 35000);

    fetch('/api/proxy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        platform: window.aiChatModel.split('-')[0],
        model: window.aiChatModel,
        messages: aiChatHistories[chatId].messages.map(m => ({ role: m.role, content: m.content })),
        max_tokens: 2048
      }),
      signal: ctrl.signal
    }).then(r => r.json())
      .then(data => {
        clearTimeout(timeout);
        const reply = data.content || (data.choices && data.choices[0] && data.choices[0].message.content) || '（无回复）';
        aiChatHistories[chatId].messages.push({ role: 'assistant', content: reply });
        aiChatMessages.push({ role: 'assistant', content: reply });
        const el = document.getElementById(loadingId);
        if (el) el.remove();
        msgsEl.innerHTML += '<div class="ai-msg ai"><div class="ai-msg-avatar">' + getIcon(window.aiChatModel.split('-')[0]) + '</div><div class="ai-msg-bubble">' + escHtml(reply) + '</div></div>';
        msgsEl.scrollTop = msgsEl.scrollHeight;
        renderAIHistory();
      })
      .catch(() => {
        clearTimeout(timeout);
        const el = document.getElementById(loadingId);
        if (el) el.remove();
        msgsEl.innerHTML += '<div class="ai-msg ai"><div class="ai-msg-avatar">' + getIcon(window.aiChatModel.split('-')[0]) + '</div><div class="ai-msg-bubble">（请求超时，请检查 API Key）</div></div>';
        msgsEl.scrollTop = msgsEl.scrollHeight;
      });
  }

  function aiNewChat() {
    aiChatMessages = [];
    aiCurrentHistoryId = null;
    renderAIChatMessages();
    const welcomeEl = document.getElementById('aiSingleWelcome');
    if (welcomeEl) welcomeEl.style.display = '';
  }

  function aiSetModelInfo(modelId) {
    const nameEl = document.getElementById('aiSingleName');
    const iconEl = document.getElementById('aiSingleIcon');
    const wIconEl = document.getElementById('aiSingleWelcomeIcon');
    if (nameEl) nameEl.textContent = getModelName(modelId);
    if (iconEl) iconEl.textContent = getIcon(modelId.split('-')[0]);
    if (wIconEl) wIconEl.textContent = getIcon(modelId.split('-')[0]);
  }

  function renderAIChatMessages() {
    const msgsEl = document.getElementById('aiSingleMessages');
    if (!msgsEl) return;
    const welcomeEl = document.getElementById('aiSingleWelcome');
    if (aiChatMessages.length === 0) {
      if (welcomeEl) welcomeEl.style.display = '';
      return;
    }
    if (welcomeEl) welcomeEl.style.display = 'none';
    let html = '';
    aiChatMessages.forEach(m => {
      if (m.role === 'user') {
        html += '<div class="ai-msg user"><div class="ai-msg-avatar">👤</div><div class="ai-msg-bubble">' + escHtml(m.content) + '</div></div>';
      } else {
        html += '<div class="ai-msg ai"><div class="ai-msg-avatar">' + getIcon(window.aiChatModel ? window.aiChatModel.split('-')[0] : 'openai') + '</div><div class="ai-msg-bubble">' + escHtml(m.content) + '</div></div>';
      }
    });
    msgsEl.innerHTML = html;
    msgsEl.scrollTop = msgsEl.scrollHeight;
  }

  function renderAIHistory() {
    const list = document.getElementById('aiHistoryList');
    if (!list) return;
    let html = '';
    Object.keys(aiChatHistories).forEach(id => {
      const h = aiChatHistories[id];
      if (!h) return;
      html += '<div class="ai-hp-item" data-id="' + escAttr(id) + '"><span>' + escHtml(h.title || '无标题') + '</span><span class="ai-hp-time">' + (h.time || '').split(' ')[1] + '</span></div>';
    });
    list.innerHTML = html || '<div style="padding:16px;text-align:center;color:var(--text3);font-size:12px">暂无对话历史</div>';
  }

  function loadHistory(id) {
    const h = aiChatHistories[id];
    if (!h) return;
    aiCurrentHistoryId = id;
    aiChatMessages = h.messages || [];
    renderAIChatMessages();
    const panel = document.getElementById('aiHistoryPanel');
    if (panel) panel.classList.remove('open');
  }

  function bindEvents() {
    // 语音输入
    const voiceBtn = document.getElementById('aiSingleVoiceBtn');
    if (voiceBtn) {
      voiceBtn.addEventListener('click', () => startVoiceRecording('aiSingleVoiceBtn', 'aiSingleTextarea'));
    }

    // 发送
    const sendBtn = document.getElementById('aiSingleSendBtn');
    if (sendBtn) sendBtn.addEventListener('click', aiSingleSend);
    const textarea = document.getElementById('aiSingleTextarea');
    if (textarea) {
      textarea.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); aiSingleSend(); }
      });
      textarea.addEventListener('input', () => {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
      });
    }

    // 新建对话
    const newBtn = document.getElementById('aiNewChatBtn');
    if (newBtn) newBtn.addEventListener('click', aiNewChat);

    // 历史面板
    const histBtn = document.getElementById('aiHistoryBtn');
    if (histBtn) histBtn.addEventListener('click', () => {
      renderAIHistory();
      const panel = document.getElementById('aiHistoryPanel');
      if (panel) panel.classList.add('open');
    });
    const closeBtn = document.getElementById('aiHistoryClose');
    if (closeBtn) closeBtn.addEventListener('click', () => {
      const panel = document.getElementById('aiHistoryPanel');
      if (panel) panel.classList.remove('open');
    });
    const histList = document.getElementById('aiHistoryList');
    if (histList) histList.addEventListener('click', e => {
      const item = e.target.closest('.ai-hp-item');
      if (item) loadHistory(item.dataset.id);
    });
  }

  window.aiChatHistories = aiChatHistories;
  window.aiSetModelInfo = aiSetModelInfo;
  window.aiNewChat = aiNewChat;
  window.renderAIChatMessages = renderAIChatMessages;
  window.renderAIHistory = renderAIHistory;

  document.addEventListener('DOMContentLoaded', bindEvents);
})();
'''
with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js_new)
print('[OK] ai-page.js rewritten with voice input')

# Write back index.html
out = (b'\xef\xbb\xbf' if has_bom else b'') + d.encode('utf-8')
with open(p, 'wb') as f:
    f.write(out)
print(f'\n[DONE] index.html: {len(out)} bytes')
