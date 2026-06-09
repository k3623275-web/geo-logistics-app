/* ai-page.js — 科AI 多模型对话页面 Logic
 * 由 index.html 通过 <script src="ai-page.js"> 引入
 * 依赖：PROVIDERS, MODELS, I18N, lang, API /api/proxy
 */

(function(){
  'use strict';

  /* ── State ── */
  let aiSelectedModels = new Set();
  let aiChatMessages   = [];
  let aiCurrentChatId   = null;

  /* ── Provider SVG Icons ── */
  const AI_MODEL_ICONS = {
    openai : '<svg viewBox="0 0 24 24" fill="none" stroke="#10a37f" stroke-width="1.5"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/><path d="M12 6v6l4 2"/></svg>',
    claude : '<svg viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="1.5"><polygon points="12,2 22,20 2,20"/></svg>',
    gemini : '<svg viewBox="0 0 24 24" fill="none" stroke="#4285f4" stroke-width="1.5"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>',
    deepseek:'<svg viewBox="0 0 24 24" fill="none" stroke="#4d6bfe" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><path d="M12 3v18M3 12h18"/></svg>',
    qwen  : '<svg viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="3"/><path d="M9 12h6M12 9v6"/></svg>',
    kimi  : '<svg viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="1.5"><path d="M12 2l4 8h8l-6 5 2 9-8-5-8 5 2-9-6-5h8z"/></svg>',
    zhipu : '<svg viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="1.5"><circle cx="12" cy="12" r="8"/><path d="M9 12h6M12 9v6"/></svg>',
    yi    : '<svg viewBox="0 0 24 24" fill="none" stroke="#06b6d4" stroke-width="1.5"><polygon points="12,2 22,12 12,22 2,12"/></svg>',
    mistral:'<svg viewBox="0 0 24 24" fill="none" stroke="#f97316" stroke-width="1.5"><path d="M12 2L2 7v10l10 5 10-5V7L12 2z"/></svg>',
    meta  : '<svg viewBox="0 0 24 24" fill="none" stroke="#0081fb" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><circle cx="9" cy="10" r="2"/><circle cx="15" cy="10" r="2"/><path d="M12 15a4 4 0 01-4-4"/></svg>'
  };

  function getProviderIcon(pid){
    return AI_MODEL_ICONS[pid] || AI_MODEL_ICONS['openai'];
  }

  /* ── Render Model List ── */
  function renderAIModelList(){
    const list   = document.getElementById('aiModelList');
    const search = (document.getElementById('aiModelSearch').value||'').toLowerCase();
    const groups = {};

    MODELS.forEach(function(m){
      if(search){
        var nameMatch   = (m.name||'').toLowerCase().indexOf(search) >= 0;
        var provMatch    = ((PROVIDERS[m.provider]||{}).name||'').toLowerCase().indexOf(search) >= 0;
        if(!nameMatch && !provMatch) return;
      }
      if(!groups[m.provider]) groups[m.provider] = [];
      groups[m.provider].push(m);
    });

    var html = '';
    Object.keys(groups).forEach(function(pid){
      var prov = PROVIDERS[pid] || {name:pid, color:'#888'};
      html += '<div class="ai-mp-group">' + escHtml(prov.name) + '</div>';
      groups[pid].forEach(function(m){
        var sel = aiSelectedModels.has(m.id);
        var tag = m.in <= 0.2 ? 'free' : m.in >= 2 ? 'paid' : '';
        var tagLabel = tag === 'free' ? '\u514d\u8d39' : tag === 'paid' ? '\u4ed8\u8d39' : '';
        var tagClass = tag === 'free' ? 'tag-free' : tag === 'paid' ? 'tag-paid' : '';
        html +=
          '<div class="ai-mp-item' + (sel?' selected':'') + '" data-ai-mid="' + escAttr(m.id) + '">' +
            '<div class="ai-mp-check"><svg viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 5l2 2 4-4"/></svg></div>' +
            '<div class="ai-mp-icon">' + getProviderIcon(m.provider) + '</div>' +
            '<div class="ai-mp-info">' +
              '<div class="ai-mp-name">' + escHtml(m.name) + '</div>' +
              '<div class="ai-mp-desc">' + escHtml(m.positioning||'') + '</div>' +
            '</div>' +
            (tagLabel ? '<span class="ai-mp-tag ' + tagClass + '">' + tagLabel + '</span>' : '') +
          '</div>';
      });
    });

    if(!html) html = '<div style="padding:20px;text-align:center;color:var(--text3);font-size:12px">\u65e0\u5339\u914d\u6a21\u578b</div>';
    list.innerHTML = html;

    /* bind click */
    list.querySelectorAll('.ai-mp-item').forEach(function(item){
      item.addEventListener('click', function(){
        var mid = item.getAttribute('data-ai-mid');
        if(aiSelectedModels.has(mid)){
          aiSelectedModels.delete(mid);
          item.classList.remove('selected');
        } else {
          aiSelectedModels.add(mid);
          item.classList.add('selected');
        }
        updateAISelectedCount();
      });
    });

    updateAISelectedCount();
  }

  function updateAISelectedCount(){
    var n = aiSelectedModels.size;
    var el = document.getElementById('aiSelectedCount');
    if(el) el.textContent = '\u5df2\u9009 ' + n + '/' + MODELS.length;
    var mi = document.getElementById('aiMiText');
    if(mi) mi.textContent = n + ' \u6a21\u578b';
    var sb = document.getElementById('aiSendBtn');
    if(sb) sb.disabled = (n === 0);
  }

  /* ── Chat Functions ── */
  function aiNewChat(){
    aiChatMessages  = [];
    aiCurrentChatId = 'chat_' + Date.now();
    var msgsEl = document.getElementById('aiMessages');
    var welcomeEl = document.getElementById('aiWelcome');
    if(msgsEl){ msgsEl.style.display = 'none'; msgsEl.innerHTML = ''; }
    if(welcomeEl) welcomeEl.style.display = 'block';
    var ta = document.getElementById('aiTextarea');
    if(ta) ta.value = '';
  }

  function escapeHtml(s){
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }
  function escHtml(s){ return escapeHtml(s); }
  function escAttr(s){
    return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/'/g,'&#39;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  async function aiSendMessage(){
    var textarea = document.getElementById('aiTextarea');
    var msg = textarea ? textarea.value.trim() : '';
    if(!msg || aiSelectedModels.size === 0) return;

    var msgsEl    = document.getElementById('aiMessages');
    var welcomeEl = document.getElementById('aiWelcome');
    if(msgsEl) msgsEl.style.display = 'flex';
    if(welcomeEl) welcomeEl.style.display = 'none';

    /* user bubble */
    var userEl = document.createElement('div');
    userEl.className = 'ai-msg-user';
    userEl.innerHTML = '<div class="ai-msg-user-bubble">' + escHtml(msg) + '</div>';
    msgsEl.appendChild(userEl);

    textarea.value = '';
    msgsEl.scrollTop = msgsEl.scrollHeight;

    /* model response container */
    var modelsEl = document.createElement('div');
    modelsEl.className = 'ai-msg-models';
    msgsEl.appendChild(modelsEl);

    var selected = [];
    aiSelectedModels.forEach(function(id){
      var m = MODELS.find(function(x){ return x.id === id; });
      if(m) selected.push(m);
    });

    var priceFirst = document.getElementById('aiPriceFirst') ? document.getElementById('aiPriceFirst').checked : true;
    if(priceFirst) selected.sort(function(a,b){ return (a.in||0) - (b.in||0); });

    var timeout = parseInt((document.getElementById('aiTimeout')||{}).value||'30') * 1000;

    /* create loading rows */
    selected.forEach(function(m){
      var prov = PROVIDERS[m.provider] || {};
      var row = document.createElement('div');
      row.className = 'ai-msg-model-row';
      row.innerHTML =
        '<div class="ai-msg-model-avatar" style="background:' + (prov.color||'#888') + '22">' + getProviderIcon(m.provider) + '</div>' +
        '<div class="ai-msg-model-bubble">' +
          '<div class="ai-msg-model-header"><span class="ai-msg-model-name">' + escHtml(m.name) + '</span><span class="ai-msg-model-provider"> ' + escHtml(prov.name||'') + '</span></div>' +
          '<div class="ai-msg-model-body"><div class="ai-msg-model-loading"><span class="dot"></span><span class="dot"></span><span class="dot"></span> \u7b49\u5f85\u54cd\u5e94...</div></div>' +
        '</div>';
      modelsEl.appendChild(row);
    });

    msgsEl.scrollTop = msgsEl.scrollHeight;

    /* send requests */
    var promises = selected.map(function(m, idx){
      return new Promise(function(resolve){
        setTimeout(function(){}, 0); /* yield to UI */
        var rowEl  = modelsEl.children[idx];
        var bodyEl = rowEl ? rowEl.querySelector('.ai-msg-model-body') : null;
        var key = localStorage.getItem('key_' + m.provider) || '';
        if(!key){
          if(bodyEl) bodyEl.innerHTML = '<span style="color:var(--orange)">\u26a0 \u672a\u914d\u7f6e API Key\uff0c\u8bf7\u5230 \u4e2a\u4eba\u4e2d\u5fc3 \u2192 API\u5bc6\u94a5 \u4e2d\u8bbe\u7f6e</span>';
          resolve();
          return;
        }
        var controller = new AbortController();
        var timer = setTimeout(function(){ controller.abort(); }, timeout);
        fetch('/api/proxy', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ provider:m.provider, model:m.id, apiKey:key, prompt:msg, max_tokens:1024 }),
          signal: controller.signal
        }).then(function(res){
          clearTimeout(timer);
          if(!res.ok) throw new Error('HTTP ' + res.status);
          return res.text();
        }).then(function(text){
          var content = text || '(\u7a7a\u56de\u590d)';
          try {
            var j = JSON.parse(text);
            content = j.content || j.response || j.text || text;
          } catch(e){}
          if(bodyEl) bodyEl.innerHTML = '<span>' + escHtml(content) + '</span>';
        }).catch(function(err){
          if(bodyEl){
            if(err.name === 'AbortError'){
              bodyEl.innerHTML = '<span style="color:var(--orange)">\u23f0 \u8bf7\u6c42\u8d85\u65f6 (' + (timeout/1000) + 's)</span>';
            } else {
              bodyEl.innerHTML = '<span style="color:var(--red)">\u2716 \u8bf7\u6c42\u5931\u8d25: ' + escHtml(err.message) + '\u3002\u8bf7\u68c0\u67e5\u7f51\u7edc\u548c API Key\u3002</span>';
            }
          }
        }).finally(function(){
          resolve();
          if(msgsEl) msgsEl.scrollTop = msgsEl.scrollHeight;
        });
      });
    });

    Promise.allSettled(promises).then(function(){
      aiChatMessages.push({ role:'user', content:msg, models:selected.map(function(m){return m.id;}), time:Date.now() });
    });
  }

  /* ── Bind Events ── */
  function bindAIEvents(){
    var newChatBtn = document.getElementById('aiNewChat');
    if(newChatBtn) newChatBtn.addEventListener('click', aiNewChat);

    var clearBtn = document.getElementById('aiClearModels');
    if(clearBtn) clearBtn.addEventListener('click', function(){
      aiSelectedModels.clear();
      renderAIModelList();
    });

    var searchInput = document.getElementById('aiModelSearch');
    if(searchInput) searchInput.addEventListener('input', function(){ renderAIModelList(); });

    var sendBtn = document.getElementById('aiSendBtn');
    if(sendBtn) sendBtn.addEventListener('click', function(){ aiSendMessage(); });

    var ta = document.getElementById('aiTextarea');
    if(ta){
      ta.addEventListener('keydown', function(e){
        if(e.key === 'Enter' && !e.shiftKey){ e.preventDefault(); aiSendMessage(); }
      });
      ta.addEventListener('input', function(){
        ta.style.height = 'auto';
        ta.style.height = Math.min(ta.scrollHeight, 120) + 'px';
      });
    }

    /* quick-start buttons */
    document.querySelectorAll('.ai-qs-btn').forEach(function(btn){
      btn.addEventListener('click', function(){
        var qs = btn.getAttribute('data-qs') || '';
        var prompts = {
          deep:    '\u8bf7\u5bf9\u4ee5\u4e0b\u4e3b\u9898\u8fdb\u884c\u6df1\u5ea6\u591a\u7ef4\u5206\u6790\uff0c\u5305\u62ec\u80cc\u666f\u3001\u73b0\u72b6\u3001\u8d8b\u52bf\u548c\u5f71\u54cd\u3002',
          code:    '\u8bf7\u5e2e\u6211\u8bbe\u8ba1\u5e76\u5b9e\u73b0\u4ee5\u4e0b\u529f\u80fd\uff0c\u63d0\u4f9b\u5b8c\u6574\u4ee3\u7801\u548c\u8bf4\u660e\u3002',
          creative:'\u8bf7\u4ee5\u5bcc\u6709\u521b\u610f\u7684\u65b9\u5f0f\u64b0\u5199\u5173\u4e8e\u4ee5\u4e0b\u4e3b\u9898\u7684\u5185\u5bb9\u3002',
          compare: '\u8bf7\u4ece\u591a\u4e2a\u7ef4\u5ea6\u5bf9\u6bd4\u5206\u6790\u4ee5\u4e0b\u4e24\u4e2a\u6216\u591a\u4e2a\u9009\u9879\u7684\u4f18\u52a3\u3002'
        };
        var target = document.getElementById('aiTextarea');
        if(target){
          target.value = prompts[qs] || '';
          target.focus();
        }
      });
    });

    /* initial render */
    renderAIModelList();
  }

  /* ── Expose for index.html inline handlers ── */
  window.bindAIEvents   = bindAIEvents;
  window.renderAIModelList = renderAIModelList;
  window.aiNewChat       = aiNewChat;
  window.aiSendMessage   = aiSendMessage;

  /* auto-init when DOM ready */
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', bindAIEvents);
  } else {
    bindAIEvents();
  }

})();
