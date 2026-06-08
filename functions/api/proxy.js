/**
 * Cloudflare Function - API Proxy (GEO Detection)
 * Forwards requests to AI platforms with user's own API key.
 * Internal: builds GEO prompt from brand name, returns mentioned/snippet.
 * No API keys stored on server - pure pass-through.
 */

// ── Provider → platform + API config mapping ──
const PLATFORM_CONFIGS = {
    openai: {
        platform: 'openai',
        endpoint: 'https://api.openai.com/v1/chat/completions',
        buildBody: (model, messages) => ({ model, messages, stream: false, max_tokens: 300 }),
        parseResponse: (data) => data.choices?.[0]?.message?.content || '',
        authHeader: (key) => ({ 'Authorization': `Bearer ${key}` })
    },
    deepseek: {
        platform: 'deepseek',
        endpoint: 'https://api.deepseek.com/v1/chat/completions',
        buildBody: (model, messages) => ({ model, messages, stream: false, max_tokens: 300 }),
        parseResponse: (data) => data.choices?.[0]?.message?.content || '',
        authHeader: (key) => ({ 'Authorization': `Bearer ${key}` })
    },
    gemini: {
        platform: 'gemini',
        endpoint: 'https://generativelanguage.googleapis.com/v1beta/models',
        buildBody: (model, messages) => ({
            contents: [{ parts: [{ text: messages[0].content }] }],
            generationConfig: { maxOutputTokens: 300 }
        }),
        parseResponse: (data) => data.candidates?.[0]?.content?.parts?.[0]?.text || '',
        buildUrl: (endpoint, model, apiKey) => `${endpoint}/${model}:generateContent?key=${apiKey}`,
        authHeader: () => ({})
    },
    claude: {
        platform: 'claude',
        endpoint: 'https://api.anthropic.com/v1/messages',
        buildBody: (model, messages) => ({
            model,
            max_tokens: 300,
            system: messages[0].content,
            messages: [{ role: 'user', content: messages[0].content }]
        }),
        parseResponse: (data) => data.content?.[0]?.text || '',
        authHeader: (key) => ({
            'x-api-key': key,
            'anthropic-version': '2023-06-01'
        })
    },
    grok: {
        platform: 'grok',
        endpoint: 'https://api.x.ai/v1/chat/completions',
        buildBody: (model, messages) => ({ model, messages, stream: false, max_tokens: 300 }),
        parseResponse: (data) => data.choices?.[0]?.message?.content || '',
        authHeader: (key) => ({ 'Authorization': `Bearer ${key}` })
    },
    qwen: {
        platform: 'qwen',
        endpoint: 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
        buildBody: (model, messages) => ({ model, messages, stream: false, max_tokens: 300 }),
        parseResponse: (data) => data.choices?.[0]?.message?.content || '',
        authHeader: (key) => ({ 'Authorization': `Bearer ${key}` })
    },
    glm: {
        platform: 'glm',
        endpoint: 'https://open.bigmodel.cn/api/paas/v4/chat/completions',
        buildBody: (model, messages) => ({ model, messages, stream: false, max_tokens: 300 }),
        parseResponse: (data) => data.choices?.[0]?.message?.content || '',
        authHeader: (key) => ({ 'Authorization': `Bearer ${key}` })
    },
    kimi: {
        platform: 'kimi',
        endpoint: 'https://api.moonshot.cn/v1/chat/completions',
        buildBody: (model, messages) => ({ model, messages, stream: false, max_tokens: 300 }),
        parseResponse: (data) => data.choices?.[0]?.message?.content || '',
        authHeader: (key) => ({ 'Authorization': `Bearer ${key}` })
    },
    mistral: {
        platform: 'mistral',
        endpoint: 'https://api.mistral.ai/v1/chat/completions',
        buildBody: (model, messages) => ({ model, messages, stream: false, max_tokens: 300 }),
        parseResponse: (data) => data.choices?.[0]?.message?.content || '',
        authHeader: (key) => ({ 'Authorization': `Bearer ${key}` })
    },
    yi: {
        platform: 'yi',
        endpoint: 'https://api.lingyiwanwu.com/v1/chat/completions',
        buildBody: (model, messages) => ({ model, messages, stream: false, max_tokens: 300 }),
        parseResponse: (data) => data.choices?.[0]?.message?.content || '',
        authHeader: (key) => ({ 'Authorization': `Bearer ${key}` })
    }
};

// ── Model name mapping: frontend shorthand → actual API model name ──
const MODEL_MAP = {
    'gpt-5.5': 'o1-pro',
    'gpt-5.4': 'gpt-4.1',
    'gpt-5.1': 'gpt-3.5-turbo',
    'deepseek-v4': 'deepseek-chat',
    'deepseek-v3.2': 'deepseek-chat',
    'gemini-3.1-pro': 'gemini-2.5-pro',
    'gemini-3.1-ultra': 'gemini-2.5-pro',
    'gemini-3.0-flash': 'gemini-2.5-flash',
    'claude-opus-4.7': 'claude-sonnet-4-20250514',
    'claude-sonnet-4.6': 'claude-sonnet-4-20250514',
    'grok-3': 'grok-3-beta',
    'grok-2': 'grok-2-1212',
    'qwen-3.7-max': 'qwen-max',
    'qwen-3.5-plus': 'qwen-plus',
    'glm-5': 'glm-4-plus',
    'glm-4-plus': 'glm-4-plus',
    'kimi-2.6': 'moonshot-v1-8k',
    'yi-lightning-2': 'yi-lightning',
    'mistral-large-2': 'mistral-large-latest'
};

// ── Build GEO detection prompt ──
function buildPrompt(brand) {
    return {
        role: 'user',
        content: `请简要回答：你是否了解品牌"${brand}"？如果了解，请用一两句话概括它的主要业务或特点。如果不了解，请明确说"不知道"或"不了解"。只返回答案，不要额外解释。`
    };
}

// ── Analyze response: determine if brand is mentioned ──
function analyzeResponse(text, brand) {
    if (!text) return { mentioned: false, snippet: '' };

    const lower = text.toLowerCase();
    const brandLower = brand.toLowerCase();

    // Negative indicators - model explicitly says it doesn't know
    const negativePhrases = [
        '不知道', '不了解', '不清楚', '不熟悉', '没有相关信息',
        'i don\'t know', 'i\'m not familiar', 'no information',
        'i cannot', 'not aware', '没有找到', '无法回答', '抱歉'
    ];

    const isNegative = negativePhrases.some(p => lower.includes(p));

    if (isNegative) {
        return { mentioned: false, snippet: text.substring(0, 200) };
    }

    // Check if brand name appears in response
    const brandMentioned = lower.includes(brandLower);
    return {
        mentioned: brandMentioned || (!isNegative && text.length > 20),
        snippet: text.substring(0, 200)
    };
}

export async function onRequestPost({ request, env }) {
    try {
        const { provider, brand, apiKey, model } = await request.json();

        if (!provider || !brand || !apiKey) {
            return new Response(JSON.stringify({ error: 'Missing provider, brand, or apiKey' }), {
                status: 400,
                headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
            });
        }

        const config = PLATFORM_CONFIGS[provider];
        if (!config) {
            return new Response(JSON.stringify({ error: `Unsupported provider: ${provider}` }), {
                status: 400,
                headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
            });
        }

        // Map frontend model name to actual API model name
        const apiModel = MODEL_MAP[model] || model;

        const messages = [buildPrompt(brand)];

        let url = config.endpoint;
        const headers = {
            'Content-Type': 'application/json',
            ...config.authHeader(apiKey)
        };

        const body = config.buildBody(apiModel, messages);

        // Special handling for platforms that need API key in URL (Gemini)
        if (config.buildUrl) {
            url = config.buildUrl(config.endpoint, apiModel, apiKey);
        }

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 25000);
        let response;
        try {
            response = await fetch(url, {
                method: 'POST',
                headers,
                body: JSON.stringify(body),
                signal: controller.signal
            });
        } finally {
            clearTimeout(timeoutId);
        }

        if (!response.ok) {
            const errText = await response.text();
            return new Response(JSON.stringify({
                error: `API ${response.status}: ${errText.substring(0, 200)}`
            }), {
                status: response.status,
                headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
            });
        }

        const data = await response.json();
        const content = config.parseResponse(data);
        const { mentioned, snippet } = analyzeResponse(content, brand);

        return new Response(JSON.stringify({ mentioned, snippet }), {
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        });

    } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
            status: 500,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
        });
    }
}

export async function onRequestOptions() {
    return new Response(null, {
        status: 204,
        headers: {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
    });
}
