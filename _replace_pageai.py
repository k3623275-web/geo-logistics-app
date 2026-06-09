p = r'C:\工作场地\geo-logistics-app\index.html'
with open(p, 'rb') as f:
    raw = f.read()
d = raw[3:].decode('utf-8') if raw[:3] == b'\xef\xbb\xbf' else raw.decode('utf-8')
has_bom = raw[:3] == b'\xef\xbb\xbf'
print(f'File: {len(d)} chars')

# Find <div class="page" id="pageAI">
start = d.find('<div class="page" id="pageAI">')
print(f'pageAI start: {start}')

# Find pageGeo marker (for end)
geo_start = d.find('<div class="page" id="pageGeo">')
print(f'pageGeo start: {geo_start}')

# Find closing </div> of pageAI - it's the </div> just before pageGeo
# Search backward from geo_start for the first </div>
end = d.rfind('</div>', 0, geo_start)
print(f'pageAI end: {end} (char at end: {repr(d[end:end+6])})')

# Also find old ai-layout class for CSS
old_css_start = d.find('.ai-layout{display:flex')
old_css_end = d.find('}', old_css_start) + 1
print(f'Old .ai-layout CSS: {old_css_start}-{old_css_end}')

# New HTML for pageAI
new_pageai = '''<div class="page" id="pageAI">
  <div class="ai-multi-layout">
    <!-- Left: Model Panel -->
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
      <!-- Messages -->
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
        <!-- Top bar -->
        <div class="ai-single-topbar">
          <div class="ai-single-model-info">
            <span class="ai-single-icon" id="aiSingleIcon">🤖</span>
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
        <!-- History panel -->
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
            <div class="ai-sw-icon" id="aiSingleWelcomeIcon">🤖</div>
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

    # Replace pageAI section
    d = d[:start] + new_pageai + '\n\n' + d[end + 6:]
    print(f'[OK] pageAI replaced, new len={len(d)}')

    # Remove old .ai-layout CSS
    d = d[:old_css_start] + d[old_css_end:]
    print(f'[OK] Removed old .ai-layout CSS, new len={len(d)}')

# Update I18N - inject into zh{} and en{}
import re

# zh{}
zh_end = d.rfind("  };")
# Find the last aiPriceFirst entry
zp_match = re.search(r"aiPriceFirst:'[^']*',", d)
if zp_match:
    insert_at = zp_match.end()
    zh_entries = ("aiMultiMode:'多模型协作',aiOpenAI:'OpenAI',aiClaude:'Claude',"
                  "aiGemini:'Gemini',aiDeepSeek:'DeepSeek',aiQwen:'通义千问',aiKimi:'Kimi',"
                  "aiZhipu:'智谱GLM',aiYi:'零一万物',aiMistral:'Mistral',aiMeta:'Meta',"
                  "aiMultiTitle:'多模型协作',aiSingleSub:'单模型对话 · 选择最合适的AI',"
                  "aiVoicePh:'选择语音',aiNoVoice:'无语音',aiUploadFile:'上传文件',"
                  "aiSelectedModels:'已选 {n} 个模型',aiSelAll:'全选',aiSend:'发送',"
                  "aiThinking:'正在思考...',aiNoModelSelected:'请先选择至少一个模型',")
    d = d[:insert_at] + zh_entries + d[insert_at:]
    print('[OK] zh{} I18N injected')
else:
    print('[WARN] Could not find aiPriceFirst in zh{}')

# en{}
en_start = d.find('  en:{')
en_end = d.rfind('  };')
en_last_ai = re.search(r"aiPriceFirst:'[^']*',", d[en_start:en_end])
if en_last_ai:
    abs_pos = en_start + en_last_ai.end()
    en_entries = ("aiMultiMode:'Multi-Model',aiOpenAI:'OpenAI',aiClaude:'Claude',"
                  "aiGemini:'Gemini',aiDeepSeek:'DeepSeek',aiQwen:'Qwen',aiKimi:'Kimi',"
                  "aiZhipu:'GLM',aiYi:'Yi',aiMistral:'Mistral',aiMeta:'Meta',"
                  "aiMultiTitle:'Multi-Model',aiSingleSub:'Single Model Chat',"
                  "aiVoicePh:'Voice',aiNoVoice:'No Voice',aiUploadFile:'Upload File',"
                  "aiSelectedModels:'{n} selected',aiSelAll:'Select All',aiSend:'Send',"
                  "aiThinking:'Thinking...',aiNoModelSelected:'Please select at least one model',")
    d = d[:abs_pos] + en_entries + d[abs_pos:]
    print('[OK] en{} I18N injected')
else:
    print('[WARN] Could not find aiPriceFirst in en{}')

# Write back
out = (b'\xef\xbb\xbf' if has_bom else b'') + d.encode('utf-8')
with open(p, 'wb') as f:
    f.write(out)
print(f'\n[DONE] Written: {len(out)} bytes')
