"""
AI栏目大改造 - 2026-06-09
1. SIDEBAR_MAP ai:[] → 单模型子工具 + 多模型协作
2. pageAI HTML重设计：协作banner + 历史记录 + 语音选择 + 发文件
3. 新增pageAIChat单模型对话页面
4. I18N新增/更新条目
5. ai-page.js重构：单模型对话 + 多模型协作 + 历史 + 语音 + 文件上传
"""

import re

p = r'C:\工作场地\geo-logistics-app\index.html'
with open(p, 'rb') as f:
    raw = f.read()
d = raw[3:].decode('utf-8') if raw[:3] == b'\xef\xbb\xbf' else raw.decode('utf-8')
has_bom = raw[:3] == b'\xef\xbb\xbf'
print(f'File: {len(d)} chars, BOM: {has_bom}')

# ══════════════════════════════════════════════════════
# STEP 1: Update SIDEBAR_MAP
# ══════════════════════════════════════════════════════
old_sidebar_ai = "  home:[],ai:[],"
new_sidebar_ai = """  home:[],
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

cnt = d.count(old_sidebar_ai)
print(f'SIDEBAR_MAP ai:[], found: {cnt}')
if cnt == 1:
    d = d.replace(old_sidebar_ai, new_sidebar_ai)
    print('[OK] SIDEBAR_MAP updated')
else:
    # Try with \n variations
    print('[WARN] Could not find exact pattern, trying fuzzy...')

# ══════════════════════════════════════════════════════
# STEP 2: Update navigateTo to handle ai sub-tools
# ══════════════════════════════════════════════════════
# Find navigateTo and insert ai sub-tool handling
nav_sig = "function navigateTo(nav){"
nav_idx = d.find(nav_sig)
if nav_idx < 0:
    print('[ERROR] navigateTo not found')
else:
    # Find the end of the ai block we added earlier
    # The ai block starts with: if(nav==='ai'||nav==='ai-ai-chat')
    # Replace it with a more complete version
    old_ai_block = "  if(nav==='ai'||nav==='ai-ai-chat'){\n    showPage('pageAI');\n    currentNav='ai';\n    renderSidebar('ai');\n    return;\n  }"
    new_ai_block = """  // AI sub-tool routing
  if(nav==='ai'||nav==='ai-multi'){
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
    
    cnt2 = d.count(old_ai_block)
    print(f'Old ai block found: {cnt2}')
    if cnt2 == 1:
        d = d.replace(old_ai_block, new_ai_block)
        print('[OK] navigateTo ai routing updated')
    else:
        print('[WARN] Could not find old ai block, trying alternative...')
        # Just add after the first ai if
        alt = "  if(nav==='ai'){"
        if alt in d:
            idx2 = d.find(alt)
            end = d.index('{', idx2)
            # Find matching }
            depth = 0
            i = end
            while i < len(d):
                if d[i] == '{': depth += 1
                elif d[i] == '}': 
                    depth -= 1
                    if depth == 0: break
                i += 1
            # Insert before the closing }
            insert_at = i
            inject = """  if(nav.startsWith('ai-')&&nav!=='ai'&&nav!=='ai-multi'){
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
  }
  """
            d = d[:insert_at] + inject + d[insert_at:]
            print('[OK] navigateTo ai routing injected (alternative)')

# ══════════════════════════════════════════════════════
# STEP 3: Replace pageAI HTML
# ══════════════════════════════════════════════════════
# Find the pageAI div
pageai_start = d.find('<div class="page" id="pageAI">')
pageai_end = d.find('</div>\n    <div class="page" id="pageGeo">', pageai_start)
if pageai_start < 0 or pageai_end < 0:
    print(f'[ERROR] pageAI markers not found: start={pageai_start}, end={pageai_end}')
else:
    new_pageai = '''<div class="page" id="pageAI">
  <div class="ai-multi-layout">
    <!-- Left: Model Selector Panel -->
    <div class="ai-model-panel" id="aiModelPanel">
      <div class="ai-mp-header">
        <div class="ai-mp-title" data-i18n="aiMultiTitle">多模型协作</div>
      </div>
      <div class="ai-mp-search">
        <svg viewBox="0 0 14 14" fill="none" stroke="var(--text3)" stroke-width="1.5" style="width:14px;height:14px;flex-shrink:0"><circle cx="6" cy="6" r="4.5"/><path d="M10.5 10.5L13 13"/></svg>
        <input class="ai-mp-input" id="aiModelSearch" placeholder="搜索模型" data-placeholder="aiSearchModels">
      </div>
      <div class="ai-mp-list" id="aiModelList"></div>
      <div class="ai-mp-footer">
        <span id="aiSelectedCount" class="ai-sel-count">已选 0 个模型</span>
        <button class="ai-mp-clear" id="aiClearModels" data-i18n="aiClearAll">清空</button>
      </div>
    </div>
    <!-- Right: Chat Area -->
    <div class="ai-chat-area" id="aiChatArea">
      <!-- Welcome / Feature Cards -->
      <div class="ai-welcome" id="aiWelcome">
        <div class="ai-welcome-title">
          <h2 data-i18n="aiWelcomeTitle">多模型协作 · 智能对话</h2>
          <p data-i18n="aiWelcomeSub">同时调用多个顶尖AI模型，融合最佳答案</p>
        </div>
        <div class="ai-feature-cards">
          <div class="ai-fc-card" data-qs="deep">
            <div class="ai-fc-icon" style="background:rgba(124,106,239,0.12)"><svg viewBox="0 0 20 20" fill="none" stroke="#7c6aef" stroke-width="1.5"><circle cx="10" cy="10" r="7"/><circle cx="7" cy="9" r="2"/><circle cx="13" cy="9" r="2"/><circle cx="10" cy="13" r="2"/></svg></div>
            <h4 data-i18n="aiFcMulti">多元视角</h4>
            <p data-i18n="aiFcMultiDesc">GPT、Claude、Gemini 等多模型同时回答，覆盖不同思维角度</p>
          </div>
          <div class="ai-fc-card" data-qs="fusion">
            <div class="ai-fc-icon" style="background:rgba(34,197,94,0.12)"><svg viewBox="0 0 20 20" fill="none" stroke="#22c55e" stroke-width="1.5"><path d="M4 10h12M10 4l6 6-6 6"/></svg></div>
            <h4 data-i18n="aiFcFusion">智能融合</h4>
            <p data-i18n="aiFcFusionDesc">AI 自动分析对比各模型回复，提炼共识与分歧点</p>
          </div>
          <div class="ai-fc-card" data-qs="parallel">
            <div class="ai-fc-icon" style="background:rgba(245,158,11,0.12)"><svg viewBox="0 0 20 20" fill="none" stroke="#f59e0b" stroke-width="1.5"><path d="M13 2L5 10l4 4 8-8-4-4z"/><path d="M2 18l4-4"/></svg></div>
            <h4 data-i18n="aiFcParallel">并行加速</h4>
            <p data-i18n="aiFcParallelDesc">多模型同时响应，大幅缩短等待时间</p>
          </div>
          <div class="ai-fc-card" data-qs="quality">
            <div class="ai-fc-icon" style="background:rgba(59,130,246,0.12)"><svg viewBox="0 0 20 20" fill="none" stroke="#3b82f6" stroke-width="1.5"><path d="M10 2l2 6h6l-5 4 2 6-5-4-5 4 2-6-5-4h6z"/></svg></div>
            <h4 data-i18n="aiFcQuality">质量保障</h4>
            <p data-i18n="aiFcQualityDesc">交叉验证减少幻觉，提高回答可信度</p>
          </div>
        </div>
        <div class="ai-quick-start">
          <div class="ai-qs-label">✦ <span data-i18n="aiQuickStart">快捷指令</span></div>
          <div class="ai-qs-items">
            <button class="ai-qs-btn" data-qs="deep"><svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.3"><circle cx="7" cy="4" r="2.5"/><path d="M2 12c0-2.5 2-4 5-4s5 1.5 5 4"/></svg><span data-i18n="aiQsDeep">深度分析</span></button>
            <button class="ai-qs-btn" data-qs="code"><svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M4 4l6 6M10 4l-6 6"/><rect x="2" y="2" width="10" height="10" rx="1"/></svg><span data-i18n="aiQsCode">代码设计</span></button>
            <button class="ai-qs-btn" data-qs="creative"><svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M7 2l1.5 4.5L13 8l-4.5 1.5L7 14l-1.5-4.5L1 8l4.5-1.5z"/></svg><span data-i18n="aiQsCreative">创意写作</span></button>
            <button class="ai-qs-btn" data-qs="compare"><svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.3"><rect x="2" y="3" width="4" height="8" rx="0.5"/><rect x="8" y="1" width="4" height="10" rx="0.5"/></svg><span data-i18n="aiQsCompare">对比分析</span></button>
          </div>
        </div>
      </div>
      <!-- Messages area -->
      <div class="ai-messages" id="aiMessages" style="display:none"></div>
      <!-- Input area -->
      <div class="ai-input-area" id="aiInputArea">
        <div class="ai-input-box">
          <button class="ai-upload-btn" id="aiUploadBtn" title="上传文件">
            <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 2v10M4 6l4-4 4 4"/><path d="M2 14h12"/></svg>
          </button>
          <input type="file" id="aiFileInput" style="display:none" accept="*/*">
          <textarea class="ai-textarea" id="aiTextarea" rows="1" placeholder="输入消息..." data-placeholder="aiInputPh"></textarea>
          <select class="ai-voice-select" id="aiVoiceSelect" title="选择语音">
            <option value="">🔇 无语音</option>
            <option value="alloy">🎙️ Alloy</option>
            <option value="echo">🎙️ Echo</option>
            <option value="fable">🎙️ Fable</option>
            <option value="onyx">🎙️ Onyx</option>
            <option value="nova">🎙️ Nova</option>
            <option value="shimmer">🎙️ Shimmer</option>
          </select>
          <button class="ai-send-btn" id="aiSendBtn" disabled>
            <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 8l12-6-6 12-2-4-2z"/></svg>
          </button>
        </div>
        <div class="ai-input-options">
          <label class="ai-opt-label"><input type="checkbox" id="aiPriceFirst" checked> <span data-i18n="aiPriceFirst">价格优先</span></label>
        </div>
      </div>
    </div>
  </div>
</div>

    <!-- Single Model Chat Page -->
    <div class="page" id="pageAIChat">
      <div class="ai-single-layout">
        <!-- Top bar with model name + actions -->
        <div class="ai-single-topbar">
          <div class="ai-single-model-info">
            <span class="ai-single-icon" id="aiSingleIcon"></span>
            <div class="ai-single-name-wrap">
              <div class="ai-single-name" id="aiSingleName">—</div>
              <div class="ai-single-sub" data-i18n="aiSingleSub">单模型对话 · 选择最合适的AI</div>
            </div>
          </div>
          <div class="ai-single-actions">
            <button class="ai-action-btn" id="aiNewChatBtn" data-i18n="aiNewChat" title="新建对话">
              <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 2v12M2 8h12"/></svg>
            </button>
            <button class="ai-action-btn" id="aiHistoryBtn" data-i18n="aiChatHistory" title="对话历史">
              <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="6"/><path d="M8 5v3.5l2.5 1.5"/></svg>
            </button>
          </div>
        </div>
        <!-- Chat history panel (slides in) -->
        <div class="ai-history-panel" id="aiHistoryPanel">
          <div class="ai-hp-header">
            <span data-i18n="aiChatHistory">对话历史</span>
            <button class="ai-hp-close" id="aiHistoryClose">✕</button>
          </div>
          <div class="ai-hp-list" id="aiHistoryList"></div>
        </div>
        <!-- Messages -->
        <div class="ai-single-messages" id="aiSingleMessages">
          <div class="ai-single-welcome" id="aiSingleWelcome">
            <div class="ai-sw-icon" id="aiSingleWelcomeIcon"></div>
            <h3 id="aiSingleWelcomeTitle">开始对话</h3>
            <p id="aiSingleWelcomeSub">选择一个模型，开始智能对话</p>
          </div>
        </div>
        <!-- Input -->
        <div class="ai-single-input-area">
          <div class="ai-input-box">
            <button class="ai-upload-btn" id="aiSingleUploadBtn" title="上传文件">
              <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 2v10M4 6l4-4 4 4"/><path d="M2 14h12"/></svg>
            </button>
            <input type="file" id="aiSingleFileInput" style="display:none" accept="*/*">
            <textarea class="ai-textarea" id="aiSingleTextarea" rows="1" placeholder="输入消息..." data-placeholder="aiInputPh"></textarea>
            <select class="ai-voice-select" id="aiSingleVoiceSelect" title="选择语音">
              <option value="">🔇 无语音</option>
              <option value="alloy">🎙️ Alloy</option>
              <option value="echo">🎙️ Echo</option>
              <option value="fable">🎙️ Fable</option>
              <option value="onyx">🎙️ Onyx</option>
              <option value="nova">🎙️ Nova</option>
              <option value="shimmer">🎙️ Shimmer</option>
            </select>
            <button class="ai-send-btn" id="aiSingleSendBtn">
              <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 8l12-6-6 12-2-4-2z"/></svg>
            </button>
          </div>
        </div>
      </div>
    </div>
'''
    d = d[:pageai_start] + new_pageai + d[pageai_end + len('\n    <div class="page" id="pageGeo">'):]
    print(f'[OK] pageAI replaced, new len={len(d)}')

# ══════════════════════════════════════════════════════
# STEP 4: Update I18N
# ══════════════════════════════════════════════════════
new_i18n_entries = """,
aiMultiMode:'多模型协作',aiOpenAI:'OpenAI Chat',aiClaude:'Claude AI',aiGemini:'Gemini AI',
aiDeepSeek:'DeepSeek AI',aiQwen:'通义千问',aiKimi:'Kimi AI',aiZhipu:'智谱 GLM',
aiYi:'零一万物',aiMistral:'Mistral AI',aiMeta:'Meta AI',
aiMultiTitle:'多模型协作',aiSingleSub:'单模型对话 · 选择最合适的AI',
aiVoicePh:'选择语音',aiNoVoice:'无语音',aiUploadFile:'上传文件',
aiSelectedModels:'已选 {n} 个模型',aiSelAll:'全选',aiSend:'发送',
aiThinking:'正在思考...',aiNoModelSelected:'请先选择至少一个模型',"""

# Inject before the closing } of zh{}
# Find the end of zh{} object
zh_match = re.search(r"aiPriceFirst:'[^']*'\s*\}\s*\}", d)
if zh_match:
    insert_at = zh_match.start()
    d = d[:insert_at] + "aiPriceFirst:'价格优先',aiVoicePh:'选择语音',aiNoVoice:'无语音',aiUploadFile:'上传文件',aiSelectedModels:'已选 {n} 个模型',aiSelAll:'全选',aiSend:'发送',aiThinking:'正在思考...',aiNoModelSelected:'请先选择至少一个模型',aiMultiMode:'多模型协作',aiOpenAI:'OpenAI',aiClaude:'Claude',aiGemini:'Gemini',aiDeepSeek:'DeepSeek',aiQwen:'通义千问',aiKimi:'Kimi',aiZhipu:'智谱GLM',aiYi:'零一万物',aiMistral:'Mistral',aiMeta:'Meta',aiMultiTitle:'多模型协作',aiSingleSub:'单模型对话 · 选择最合适的AI'" + d[insert_at:]
    print('[OK] zh{} I18N updated')
else:
    print('[WARN] Could not find I18N injection point')

# en{}
en_match = re.search(r"aiPriceFirst:'[^']*'\s*\}\s*\}\s*\};", d)
if en_match:
    insert_at = en_match.start()
    d = d[:insert_at] + "aiPriceFirst:'Price Priority',aiVoicePh:'Voice',aiNoVoice:'No Voice',aiUploadFile:'Upload File',aiSelectedModels:'{n} selected',aiSelAll:'Select All',aiSend:'Send',aiThinking:'Thinking...',aiNoModelSelected:'Please select at least one model',aiMultiMode:'Multi-Model',aiOpenAI:'OpenAI',aiClaude:'Claude',aiGemini:'Gemini',aiDeepSeek:'DeepSeek',aiQwen:'Qwen',aiKimi:'Kimi',aiZhipu:'GLM',aiYi:'Yi',aiMistral:'Mistral',aiMeta:'Meta',aiMultiTitle:'Multi-Model Collaboration',aiSingleSub:'Single Model Chat'" + d[insert_at:]
    print('[OK] en{} I18N updated')
else:
    print('[WARN] Could not find en{} injection point')

# ══════════════════════════════════════════════════════
# STEP 5: Add CSS for new AI layout
# ══════════════════════════════════════════════════════
# Find </style> and inject before it
style_end = d.rfind('</style>')
if style_end < 0:
    print('[ERROR] </style> not found')
else:
    new_css = """

/* ═══ AI Multi-Model Layout ═══ */
.ai-multi-layout{display:flex;height:100%;gap:0}
.ai-model-panel{flex-shrink:0;width:220px;background:var(--surface);border-right:1px solid var(--border);display:flex;flex-direction:column;overflow:hidden}
.ai-mp-header{padding:16px 14px 10px;border-bottom:1px solid var(--border)}
.ai-mp-title{font-size:13px;font-weight:700;color:var(--text)}
.ai-mp-search{display:flex;align-items:center;gap:8px;padding:8px 12px;border-bottom:1px solid var(--border)}
.ai-mp-input{flex:1;background:transparent;border:none;outline:none;color:var(--text);font-size:12px}
.ai-mp-input::placeholder{color:var(--text3)}
.ai-mp-list{flex:1;overflow-y:auto;padding:6px 8px}
.ai-mp-list::-webkit-scrollbar{width:3px}
.ai-mp-list::-webkit-scrollbar-thumb{background:var(--border2);border-radius:2px}
.ai-mp-group{padding:6px 8px 2px;font-size:10px;font-weight:600;color:var(--text3);letter-spacing:.5px;text-transform:uppercase;position:sticky;top:0;background:var(--surface)}
.ai-mp-item{display:flex;align-items:center;gap:8px;padding:7px 8px;border-radius:7px;cursor:pointer;transition:all .15s;font-size:12px;color:var(--text2)}
.ai-mp-item:hover{background:var(--surface2);color:var(--text)}
.ai-mp-item.selected{background:rgba(124,106,239,0.15);color:var(--accent2)}
.ai-mp-item input[type=checkbox]{accent-color:var(--accent);width:13px;height:13px;cursor:pointer}
.ai-mp-item .ai-mp-name{flex:1}
.ai-mp-item .ai-mp-icon{width:18px;height:18px;flex-shrink:0}
.ai-mp-item .ai-mp-icon svg{width:18px;height:18px}
.ai-mp-footer{display:flex;align-items:center;justify-content:space-between;padding:10px 12px;border-top:1px solid var(--border)}
.ai-sel-count{font-size:11px;color:var(--text3)}
.ai-mp-clear{background:none;border:none;color:var(--text3);font-size:11px;cursor:pointer;padding:3px 6px;border-radius:4px;transition:all .15s}
.ai-mp-clear:hover{color:var(--accent);background:rgba(124,106,239,0.1)}
.ai-chat-area{flex:1;display:flex;flex-direction:column;overflow:hidden}
.ai-welcome{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px 32px;max-width:680px;margin:0 auto;width:100%;gap:28px}
.ai-welcome-title{text-align:center}
.ai-welcome-title h2{font-size:22px;font-weight:700;margin-bottom:8px}
.ai-welcome-title p{font-size:13px;color:var(--text2)}
.ai-feature-cards{display:grid;grid-template-columns:1fr 1fr;gap:12px;width:100%}
.ai-fc-card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:16px;cursor:pointer;transition:all .2s}
.ai-fc-card:hover{border-color:var(--accent);transform:translateY(-2px);box-shadow:0 4px 16px var(--accent-glow)}
.ai-fc-icon{width:36px;height:36px;border-radius:8px;display:flex;align-items:center;justify-content:center;margin-bottom:10px}
.ai-fc-card h4{font-size:13px;font-weight:600;margin-bottom:4px}
.ai-fc-card p{font-size:11px;color:var(--text2);line-height:1.5}
.ai-quick-start{width:100%}
.ai-qs-label{font-size:11px;color:var(--text3);margin-bottom:10px;letter-spacing:.5px}
.ai-qs-items{display:flex;gap:8px;flex-wrap:wrap}
.ai-qs-btn{display:flex;align-items:center;gap:6px;padding:8px 14px;background:var(--surface);border:1px solid var(--border2);border-radius:20px;font-size:12px;color:var(--text2);cursor:pointer;transition:all .15s}
.ai-qs-btn:hover{border-color:var(--accent2);color:var(--text);background:var(--surface2)}
.ai-qs-btn svg{width:14px;height:14px;opacity:.7}
.ai-messages{flex:1;overflow-y:auto;padding:20px 32px;display:flex;flex-direction:column;gap:16px}
.ai-messages::-webkit-scrollbar{width:4px}
.ai-messages::-webkit-scrollbar-thumb{background:var(--border2);border-radius:2px}
.ai-msg{display:flex;gap:10px;animation:fadeUp .2s ease}
.ai-msg.user{flex-direction:row-reverse}
.ai-msg-avatar{width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:13px;font-weight:700}
.ai-msg.user .ai-msg-avatar{background:rgba(124,106,239,0.2);color:var(--accent2)}
.ai-msg.ai .ai-msg-avatar{background:rgba(34,197,94,0.15);color:var(--green)}
.ai-msg-bubble{max-width:75%;padding:10px 14px;border-radius:12px;font-size:13px;line-height:1.7;color:var(--text);word-break:break-word}
.ai-msg.user .ai-msg-bubble{background:var(--surface2);border:1px solid var(--border)}
.ai-msg.ai .ai-msg-bubble{background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2)}
.ai-msg-model-tag{font-size:10px;color:var(--text3);margin-bottom:4px;font-weight:600}
.ai-msg-loading{display:flex;align-items:center;gap:6px;color:var(--text3);font-size:12px;padding:8px 14px}
.ai-msg-loading::before{content:'';width:6px;height:6px;border-radius:50%;background:var(--accent);animation:ai-pulse 1s ease infinite}
@keyframes ai-pulse{0%,100%{opacity:.4;transform:scale(.8)}50%{opacity:1;transform:scale(1)}}
.ai-input-area{padding:12px 20px 16px;border-top:1px solid var(--border)}
.ai-input-box{display:flex;align-items:flex-end;gap:8px;background:var(--surface2);border:1px solid var(--border2);border-radius:12px;padding:8px 10px;transition:border .15s}
.ai-input-box:focus-within{border-color:var(--accent)}
.ai-upload-btn{background:none;border:none;color:var(--text3);cursor:pointer;padding:4px;display:flex;align-items:center;transition:color .15s;flex-shrink:0}
.ai-upload-btn:hover{color:var(--accent)}
.ai-upload-btn svg{width:18px;height:18px}
.ai-textarea{flex:1;background:transparent;border:none;outline:none;color:var(--text);font-size:13px;resize:none;line-height:1.5;max-height:120px;overflow-y:auto}
.ai-textarea::placeholder{color:var(--text3)}
.ai-voice-select{background:var(--surface);border:1px solid var(--border2);border-radius:6px;color:var(--text2);font-size:11px;padding:4px 6px;cursor:pointer;outline:none;flex-shrink:0}
.ai-send-btn{width:34px;height:34px;border-radius:8px;background:var(--accent);border:none;color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .15s;flex-shrink:0}
.ai-send-btn:hover:not(:disabled){background:var(--accent2);box-shadow:0 2px 10px var(--accent-glow)}
.ai-send-btn:disabled{opacity:.4;cursor:not-allowed}
.ai-send-btn svg{width:16px;height:16px}
.ai-input-options{display:flex;align-items:center;gap:12px;margin-top:8px;padding:0 2px}
.ai-opt-label{display:flex;align-items:center;gap:5px;font-size:11px;color:var(--text3);cursor:pointer}
.ai-opt-label input{accent-color:var(--accent)}

/* ═══ AI Single Model Chat Layout ═══ */
.ai-single-layout{display:flex;flex-direction:column;height:100%}
.ai-single-topbar{display:flex;align-items:center;justify-content:space-between;padding:12px 20px;border-bottom:1px solid var(--border);background:var(--surface);flex-shrink:0}
.ai-single-model-info{display:flex;align-items:center;gap:12px}
.ai-single-icon{width:38px;height:38px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px}
.ai-single-name-wrap{}
.ai-single-name{font-size:15px;font-weight:700;color:var(--text)}
.ai-single-sub{font-size:11px;color:var(--text3)}
.ai-single-actions{display:flex;gap:6px}
.ai-action-btn{width:34px;height:34px;border-radius:8px;background:var(--surface2);border:1px solid var(--border);color:var(--text2);cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .15s}
.ai-action-btn:hover{border-color:var(--accent);color:var(--accent)}
.ai-action-btn svg{width:16px;height:16px}
.ai-history-panel{position:fixed;top:0;left:0;bottom:0;width:280px;background:var(--surface);border-right:1px solid var(--border);z-index:300;display:none;flex-direction:column;transform:translateX(-100%);transition:transform .25s ease}
.ai-history-panel.open{display:flex;transform:translateX(0)}
.ai-hp-header{display:flex;align-items:center;justify-content:space-between;padding:16px 14px;border-bottom:1px solid var(--border);font-size:14px;font-weight:600}
.ai-hp-close{background:none;border:none;color:var(--text3);cursor:pointer;font-size:14px;padding:4px 6px}
.ai-hp-list{flex:1;overflow-y:auto;padding:8px}
.ai-hp-item{display:flex;align-items:center;gap:8px;padding:10px 10px;border-radius:8px;cursor:pointer;font-size:12px;color:var(--text2);transition:all .12s;margin-bottom:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ai-hp-item:hover{background:var(--surface2);color:var(--text)}
.ai-hp-item.active{background:var(--surface3);color:var(--accent2)}
.ai-hp-time{font-size:10px;color:var(--text3);margin-left:auto;flex-shrink:0}
.ai-single-messages{flex:1;overflow-y:auto;padding:24px 32px;display:flex;flex-direction:column;gap:16px}
.ai-single-messages::-webkit-scrollbar{width:4px}
.ai-single-messages::-webkit-scrollbar-thumb{background:var(--border2);border-radius:2px}
.ai-single-welcome{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;height:100%;gap:10px;padding-top:60px}
.ai-sw-icon{font-size:48px;margin-bottom:8px}
#aiSingleWelcomeTitle{font-size:20px;font-weight:700}
#aiSingleWelcomeSub{font-size:13px;color:var(--text2)}
.ai-single-input-area{padding:12px 20px 16px;border-top:1px solid var(--border);flex-shrink:0}
"""
    d = d[:style_end] + new_css + d[style_end:]
    print(f'[OK] AI CSS injected, new len={len(d)}')

# ══════════════════════════════════════════════════════
# Write back
# ══════════════════════════════════════════════════════
out = (b'\xef\xbb\xbf' if has_bom else b'') + d.encode('utf-8')
with open(p, 'wb') as f:
    f.write(out)
print(f'\n[DONE] Written: {len(out)} bytes')
