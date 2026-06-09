/* ai-page.js - 科AI 多模型/单模型对话逻辑
 * 通过 <script src="ai-page.js"> 注入 index.html
 * 依赖: PROVIDERS, MODELS, I18N, lang, /api/proxy
 */

(function () {
  'use strict';

  /* ── State ── */
  let aiSelectedModels = new Set();
  let aiChatMessages = [];         // current multi-model messages
  let aiCurrentChatId = null;
  let aiChatHistories = {};        // modelId -> [{id, title, time, messages}]
  let aiCurrentHistoryId = null;

  /* ── Icons ── */
  const ICONS = {
    openai: '<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke="#10a37f" stroke-width="1.5"/></svg>',
    claude: '<svg viewBox="0 0 24 24" fill="none"><polygon points="12,3 21,20 3,20" stroke="#d97706" stroke-width="1.5" fill="none"/></svg>',
    gemini: '<svg viewBox="0 0 24 24" fill="none"><path d="M12 3L3 8l9 5 9-5-9-5zM3 15l9 5 9-5M3 11l9 5 9-5" stroke="#4285f4" stroke-width="1.5"/></svg>',
    deepseek: '<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke="#4d6bfe" stroke-width="1.5"/><path d="M12 3v18M3 12h18" stroke="#4d6bfe" stroke-width="1.5"/></svg>',
    qwen: '<svg viewBox="0 0 24 24" fill="none"><rect x="3" y="3" width="18" height="18" rx="3" stroke="#6366f1" stroke-width="1.5"/><path d="M9 12h6M12 9v6" stroke="#6366f1" stroke-width="1.5"/></svg>',
    kimi: '<svg viewBox="0 0 24 24" fill="none"><path d="M12 2l3 6h6l-5 4 2 8-6-4-6 4 2-8-5-4h6z" stroke="#8b5cf6" stroke-width="1.5"/></svg>',
    zhipu: '<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="8" stroke="#3b82f6" stroke-width="1.5"/><path d="M9 12h6M12 9v6" stroke="#3b82f6" stroke-width="1.5"/></svg>',
    yi: '<svg viewBox="0 0 24 24" fill="none"><polygon points="12,2 22,12 12,22 2,12" stroke="#06b6d4" stroke-width="1.5" fill="none"/></svg>',
    mistral: '<svg viewBox="0 0 24 24" fill="none"><path d="M12 2L3 7v10l9 5 9-5V7L12 2z" stroke="#f97316" stroke-width="1.5" fill="none"/></svg>',
    meta: '<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke="#0081fb" stroke-width="1.5"/><circle cx="9" cy="10" r="2" stroke="#0081fb" stroke-width="1.2"/><circle cx="15" cy="10" r="2" stroke="#0081fb" stroke-width="1.2"/><path d="M9 14a4 4 0 01-2-3" stroke="#0081fb" stroke-width="1.2"/></svg>'
  };

  function getIcon(pid) {
    return ICONS[pid] || ICONS['openai'];
  }

  function getModelName(mid) {
    for (var pid in PROVIDERS) {
      var models = MODELS.filter(function(m) { return m.provider === pid; });
      for (var i = 0; i < models.length; i++) {
        if (models[i].id === mid) return PROVIDERS[pid].name + ' ' + models[i].name;
      }
    }
    return mid;
  }

  /* ── Render Model List (multi-model panel) ── */
  function renderAIModelList() {
    var list = document.getElementById('aiModelList');
    if (!list) return;
    var search = (document.getElementById('aiModelSearch').value || '').toLowerCase();
    var groups = {};
    MODELS.forEach(function(m) {
      if (search) {
        var nm = (m.name || '').toLowerCase().indexOf(search) >= 0;
        var pm = ((PROVIDERS[m.provider] || {}).name || '').toLowerCase().indexOf(search) >= 0;
        if (!nm && !pm) return;
      }
      if (!groups[m.provider]) groups[m.provider] = [];
      groups[m.provider].push(m);
    });
    var html = '';
    Object.keys(groups).forEach(function(pid) {
      var prov = PROVIDERS[pid] || { name: pid, color: '#888' };
      html += '<div class="ai-mp-group">' + escHtml(prov.name) + '</div>';
      groups[pid].forEach(function(m) {
        var sel = aiSelectedModels.has(m.id) ? 'selected' : '';
        var icon = getIcon(pid);
        html += '<div class="ai-mp-item ' + sel + '" data-mid="' + escAttr(m.id) + '">' +
          '<input type="checkbox" ' + (sel ? 'checked' : '') + ' data-mid="' + escAttr(m.id) + '">' +
          '<span class="ai-mp-name">' + escHtml(m.name) + '</span>' +
          '<span class="ai-mp-icon">' + icon + '</span>' +
          '</div>';
      });
    });
    if (!html) html = '<div style="padding:16px;text-align:center;color:var(--text3);font-size:12px">未找到模型</div>';
    list.innerHTML = html;
    updateAISelectedCount();
  }

  function updateAISelectedCount() {
    var el = document.getElementById('aiSelectedCount');
    if (!el) return;
    var total = MODELS.length;
    var sel = aiSelectedModels.size;
    var label = I18N[lang] || {};
    var txt = sel > 0
      ? (label.aiSelectedModels || '已选 {n} 个模型').replace('{n}', sel) + ' / ' + total
      : '已选 0 个模型 / ' + total;
    el.textContent = txt;

    var sendBtn = document.getElementById('aiSendBtn');
    if (sendBtn) sendBtn.disabled = sel === 0;
  }

  function toggleModel(mid) {
    if (aiSelectedModels.has(mid)) {
      aiSelectedModels.delete(mid);
    } else {
      aiSelectedModels.add(mid);
    }
    renderAIModelList();
  }

  /* ── Send Message (multi-model) ── */
  function aiSendMessage() {
    var textarea = document.getElementById('aiTextarea');
    var msg = textarea ? textarea.value.trim() : '';
    if (!msg || aiSelectedModels.size === 0) return;

    var msgsEl = document.getElementById('aiMessages');
    var welcomeEl = document.getElementById('aiWelcome');
    var inputEl = document.getElementById('aiInputArea');
    if (!msgsEl) return;

    if (welcomeEl) welcomeEl.style.display = 'none';
    msgsEl.style.display = 'flex';

    // Save to history
    var chatId = Date.now().toString();
    aiCurrentChatId = chatId;
    var modelIds = Array.from(aiSelectedModels);
    aiChatMessages = [{ role: 'user', content: msg, id: chatId + '-u' }];
    aiChatHistories[chatId] = { id: chatId, title: msg.substring(0, 30), time: new Date().toLocaleString(), messages: aiChatMessages.slice(), modelIds: modelIds };
    renderAIHistory();

    // Render user message
    msgsEl.innerHTML += '<div class="ai-msg user"><div class="ai-msg-avatar">&#x1F916;</div><div class="ai-msg-bubble">' + escHtml(msg) + '</div></div>';
    msgsEl.scrollTop = msgsEl.scrollHeight;

    textarea.value = '';
    var sendBtn = document.getElementById('aiSendBtn');
    if (sendBtn) sendBtn.disabled = true;

    // Loading indicator
    var loadingId = 'ai-msg-loading-' + Date.now();
    msgsEl.innerHTML += '<div class="ai-msg ai" id="' + loadingId + '"><div class="ai-msg-avatar">&#x1F916;</div><div class="ai-msg-bubble ai-msg-loading">正在调用 ' + aiSelectedModels.size + ' 个模型...</div></div>';
    msgsEl.scrollTop = msgsEl.scrollHeight;

    // Send to each selected model
    var completed = 0;
    var replies = {};
    aiSelectedModels.forEach(function(mid) {
      var ctrl = new AbortController();
      var timeout = setTimeout(function() { ctrl.abort(); }, 35000);

      fetch('/api/proxy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          platform: mid2platform(mid),
          model: mid,
          messages: [{ role: 'user', content: msg }],
          max_tokens: 512
        }),
        signal: ctrl.signal
      }).then(function(r) { return r.json(); })
        .then(function(data) {
          clearTimeout(timeout);
          replies[mid] = data.content || data.choices && data.choices[0] && data.choices[0].message.content || '（无回复）';
        })
        .catch(function() {
          replies[mid] = '（请求超时或失败，请检查 API Key）';
        })
        .finally(function() {
          completed++;
          if (completed === aiSelectedModels.size) {
            var loadingEl = document.getElementById(loadingId);
            if (loadingEl) loadingEl.remove();
            Object.keys(replies).forEach(function(mid) {
              var m = MODELS.find(function(x) { return x.id === mid; });
              var pname = (PROVIDERS[mid2platform(mid)] || {}).name || mid;
              msgsEl.innerHTML += '<div class="ai-msg ai"><div class="ai-msg-avatar">' + getIcon(mid2platform(mid)) + '</div><div class="ai-msg-bubble"><div class="ai-msg-model-tag">' + pname + (m ? ' ' + m.name : '') + '</div>' + escHtml(replies[mid]) + '</div></div>';
            });
            msgsEl.scrollTop = msgsEl.scrollHeight;
            aiChatMessages.push({ role: 'assistant', content: JSON.stringify(replies), id: chatId + '-a' });
            aiChatHistories[chatId].messages = aiChatMessages.slice();
          }
        });
    });
  }

  function mid2platform(mid) {
    var pid = mid.split('-')[0];
    if (PROVIDERS[pid]) return pid;
    for (var p in PROVIDERS) {
      if (MODELS.some(function(m) { return m.id === mid && m.provider === p; })) return p;
    }
    return 'openai';
  }

  /* ── Quick Start ── */
  function injectQuickStart(qs) {
    var prompts = {
      deep: '请对以下主题进行深度分析，涵盖核心问题、关键变量、潜在风险和机会：',
      code: '请用专业的代码设计方案回答以下问题，包括实现思路、关键代码示例和技术选型建议：',
      creative: '请围绕以下主题进行创意写作，提供3个不同风格的方案：',
      compare: '请对比分析以下内容的不同方案/产品/观点，从多个维度给出详细对比表格：'
    };
    var textarea = document.getElementById('aiTextarea');
    if (!textarea) return;
    textarea.value = prompts[qs] || '';
    textarea.focus();
    var sendBtn = document.getElementById('aiSendBtn');
    if (sendBtn) sendBtn.disabled = aiSelectedModels.size === 0;
  }

  /* ── File Upload ── */
  function bindFileUpload(btnId, inputId) {
    var btn = document.getElementById(btnId);
    var input = document.getElementById(inputId);
    if (!btn || !input) return;
    btn.addEventListener('click', function() { input.click(); });
    input.addEventListener('change', function() {
      if (input.files.length > 0) {
        var f = input.files[0];
        var textarea = document.getElementById(btnId.replace('Btn', 'Textarea').replace('Single', '').replace('aiUpload', 'aiTextarea'));
        if (textarea) textarea.value += '[文件: ' + f.name + ' (' + Math.round(f.size / 1024) + ' KB)]';
      }
    });
  }

  /* ── History (single model chat) ── */
  function renderAIHistory() {
    var list = document.getElementById('aiHistoryList');
    if (!list) return;
    var html = '';
    var histories = window.aiChatHistories || aiChatHistories;
    Object.keys(histories).forEach(function(id) {
      var h = histories[id];
      if (!h) return;
      html += '<div class="ai-hp-item" data-id="' + escAttr(id) + '">' +
        '<span>' + escHtml(h.title || '无标题') + '</span>' +
        '<span class="ai-hp-time">' + (h.time || '').split(' ')[1] + '</span>' +
        '</div>';
    });
    list.innerHTML = html || '<div style="padding:16px;text-align:center;color:var(--text3);font-size:12px">暂无对话历史</div>';
  }

  function loadHistory(id) {
    var h = aiChatHistories[id];
    if (!h) return;
    aiCurrentHistoryId = id;
    aiChatMessages = h.messages || [];
    renderAIChatMessages();
    var panel = document.getElementById('aiHistoryPanel');
    if (panel) panel.classList.remove('open');
  }

  function renderAIChatMessages() {
    var msgsEl = document.getElementById('aiSingleMessages');
    if (!msgsEl) return;
    var welcomeEl = document.getElementById('aiSingleWelcome');
    if (aiChatMessages.length === 0) {
      if (welcomeEl) welcomeEl.style.display = '';
      return;
    }
    if (welcomeEl) welcomeEl.style.display = 'none';
    var html = '';
    aiChatMessages.forEach(function(msg) {
      if (msg.role === 'user') {
        html += '<div class="ai-msg user"><div class="ai-msg-avatar">&#x1F464;</div><div class="ai-msg-bubble">' + escHtml(msg.content) + '</div></div>';
      } else {
        html += '<div class="ai-msg ai"><div class="ai-msg-avatar">' + getIcon(window.aiChatModel ? mid2platform(window.aiChatModel) : 'openai') + '</div><div class="ai-msg-bubble">' + escHtml(msg.content) + '</div></div>';
      }
    });
    msgsEl.innerHTML = html;
    msgsEl.scrollTop = msgsEl.scrollHeight;
  }

  /* ── Single Model Chat Send ── */
  function aiSingleSend() {
    var textarea = document.getElementById('aiSingleTextarea');
    var msg = textarea ? textarea.value.trim() : '';
    if (!msg || !window.aiChatModel) return;

    var msgsEl = document.getElementById('aiSingleMessages');
    var welcomeEl = document.getElementById('aiSingleWelcome');
    if (!msgsEl) return;
    if (welcomeEl) welcomeEl.style.display = 'none';

    var chatId = window.aiChatModel + '_' + (aiCurrentHistoryId || Date.now().toString());
    aiCurrentHistoryId = chatId;

    if (!aiChatHistories[chatId]) {
      aiChatHistories[chatId] = { id: chatId, title: msg.substring(0, 30), time: new Date().toLocaleString(), messages: [] };
    }
    aiChatHistories[chatId].messages.push({ role: 'user', content: msg });
    aiChatMessages.push({ role: 'user', content: msg });
    renderAIChatMessages();
    renderAIHistory();

    textarea.value = '';

    var loadingId = 'ai-msg-loading-' + Date.now();
    msgsEl.innerHTML += '<div class="ai-msg ai" id="' + loadingId + '"><div class="ai-msg-avatar">' + getIcon(mid2platform(window.aiChatModel)) + '</div><div class="ai-msg-bubble ai-msg-loading">正在思考...</div></div>';
    msgsEl.scrollTop = msgsEl.scrollHeight;

    var ctrl = new AbortController();
    var timeout = setTimeout(function() { ctrl.abort(); }, 35000);

    fetch('/api/proxy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        platform: mid2platform(window.aiChatModel),
        model: window.aiChatModel,
        messages: aiChatHistories[chatId].messages.map(function(m) { return { role: m.role, content: m.content }; }),
        max_tokens: 1024
      }),
      signal: ctrl.signal
    }).then(function(r) { return r.json(); })
      .then(function(data) {
        clearTimeout(timeout);
        var reply = data.content || data.choices && data.choices[0] && data.choices[0].message.content || '（无回复）';
        aiChatHistories[chatId].messages.push({ role: 'assistant', content: reply });
        aiChatMessages.push({ role: 'assistant', content: reply });
        var el = document.getElementById(loadingId);
        if (el) el.remove();
        msgsEl.innerHTML += '<div class="ai-msg ai"><div class="ai-msg-avatar">' + getIcon(mid2platform(window.aiChatModel)) + '</div><div class="ai-msg-bubble">' + escHtml(reply) + '</div></div>';
        msgsEl.scrollTop = msgsEl.scrollHeight;
        renderAIHistory();
      })
      .catch(function() {
        clearTimeout(timeout);
        var el = document.getElementById(loadingId);
        if (el) el.remove();
        msgsEl.innerHTML += '<div class="ai-msg ai"><div class="ai-msg-avatar">' + getIcon(mid2platform(window.aiChatModel)) + '</div><div class="ai-msg-bubble">（请求超时，请检查 API Key 或网络）</div></div>';
        msgsEl.scrollTop = msgsEl.scrollHeight;
      });
  }

  function aiNewChat() {
    aiChatMessages = [];
    aiCurrentHistoryId = null;
    renderAIChatMessages();
    var welcomeEl = document.getElementById('aiSingleWelcome');
    if (welcomeEl) welcomeEl.style.display = '';
  }

  function aiSetModelInfo(modelId) {
    var nameEl = document.getElementById('aiSingleName');
    var iconEl = document.getElementById('aiSingleIcon');
    var wIconEl = document.getElementById('aiSingleWelcomeIcon');
    if (nameEl) nameEl.textContent = getModelName(modelId);
    if (iconEl) iconEl.innerHTML = getIcon(mid2platform(modelId));
    if (wIconEl) wIconEl.innerHTML = getIcon(mid2platform(modelId));
  }

  /* ── Utils ── */
  function escHtml(s) {
    s = s || '';
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function escAttr(s) {
    s = s || '';
    return s.replace(/"/g, '&quot;');
  }

  /* ── Bind All Events ── */
  function bindAIEvents() {
    // Multi-model: model list
    renderAIModelList();
    document.getElementById('aiModelList').addEventListener('click', function(e) {
      var item = e.target.closest('.ai-mp-item');
      if (item) { toggleModel(item.dataset.mid); return; }
      var cb = e.target.closest('input[type=checkbox]');
      if (cb) { toggleModel(cb.dataset.mid); }
    });
    document.getElementById('aiClearModels').addEventListener('click', function() {
      aiSelectedModels.clear();
      renderAIModelList();
    });
    document.getElementById('aiModelSearch').addEventListener('input', function() {
      renderAIModelList();
    });

    // Multi-model: send
    document.getElementById('aiSendBtn').addEventListener('click', aiSendMessage);
    document.getElementById('aiTextarea').addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        aiSendMessage();
      }
    });

    // Quick start
    document.querySelectorAll('.ai-fc-card[data-qs]').forEach(function(card) {
      card.addEventListener('click', function() { injectQuickStart(card.dataset.qs); });
    });
    document.querySelectorAll('.ai-qs-btn[data-qs]').forEach(function(btn) {
      btn.addEventListener('click', function() { injectQuickStart(btn.dataset.qs); });
    });

    // File upload
    bindFileUpload('aiUploadBtn', 'aiFileInput');
    bindFileUpload('aiSingleUploadBtn', 'aiSingleFileInput');

    // Single model: send
    document.getElementById('aiSingleSendBtn').addEventListener('click', aiSingleSend);
    document.getElementById('aiSingleTextarea').addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        aiSingleSend();
      }
    });

    // Single model: new chat
    document.getElementById('aiNewChatBtn').addEventListener('click', aiNewChat);

    // History panel
    document.getElementById('aiHistoryBtn').addEventListener('click', function() {
      renderAIHistory();
      var panel = document.getElementById('aiHistoryPanel');
      if (panel) panel.classList.add('open');
    });
    document.getElementById('aiHistoryClose').addEventListener('click', function() {
      var panel = document.getElementById('aiHistoryPanel');
      if (panel) panel.classList.remove('open');
    });
    document.getElementById('aiHistoryList').addEventListener('click', function(e) {
      var item = e.target.closest('.ai-hp-item');
      if (item) loadHistory(item.dataset.id);
    });

    // Textarea auto-resize
    ['aiTextarea', 'aiSingleTextarea'].forEach(function(id) {
      var ta = document.getElementById(id);
      if (!ta) return;
      ta.addEventListener('input', function() {
        ta.style.height = 'auto';
        ta.style.height = Math.min(ta.scrollHeight, 120) + 'px';
      });
    });
  }

  /* ── Expose to window ── */
  window.aiChatHistories = aiChatHistories;
  window.aiSetModelInfo = aiSetModelInfo;
  window.aiNewChat = aiNewChat;
  window.renderAIChatMessages = renderAIChatMessages;
  window.renderAIHistory = renderAIHistory;

  document.addEventListener('DOMContentLoaded', bindAIEvents);
})();