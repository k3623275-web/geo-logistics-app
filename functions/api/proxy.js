/**
 * Cloudflare Function - API Proxy
 * Forwards requests to AI platforms with user's own API key
 * No API keys stored on server - pure pass-through
 */

const PLATFORM_CONFIGS = {
    openai: {
        endpoint: 'https://api.openai.com/v1/chat/completions',
        buildBody: (model, messages) => ({
            model,
            messages,
            stream: false,
            max_tokens: 500
        }),
        parseResponse: (data) => data.choices?.[0]?.message?.content || '',
        authHeader: (key) => ({ 'Authorization': `Bearer ${key}` })
    },
    deepseek: {
        endpoint: 'https://api.deepseek.com/v1/chat/completions',
        buildBody: (model, messages) => ({
            model,
            messages,
            stream: false,
            max_tokens: 500
        }),
        parseResponse: (data) => data.choices?.[0]?.message?.content || '',
        authHeader: (key) => ({ 'Authorization': `Bearer ${key}` })
    },
    gemini: {
        endpoint: 'https://generativelanguage.googleapis.com/v1beta/models',
        buildBody: (model, messages) => ({
            contents: [{ parts: [{ text: messages[0].content }] }],
            generationConfig: { maxOutputTokens: 500 }
        }),
        parseResponse: (data) => data.candidates?.[0]?.content?.parts?.[0]?.text || '',
        buildUrl: (endpoint, model, apiKey) => `${endpoint}/${model}:generateContent?key=${apiKey}`,
        authHeader: () => ({}) // Gemini uses URL parameter
    },
    grok: {
        endpoint: 'https://api.x.ai/v1/chat/completions',
        buildBody: (model, messages) => ({
            model,
            messages,
            stream: false,
            max_tokens: 500
        }),
        parseResponse: (data) => data.choices?.[0]?.message?.content || '',
        authHeader: (key) => ({ 'Authorization': `Bearer ${key}` })
    },
    qwen: {
        endpoint: 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
        buildBody: (model, messages) => ({
            model,
            messages,
            stream: false,
            max_tokens: 500
        }),
        parseResponse: (data) => data.choices?.[0]?.message?.content || '',
        authHeader: (key) => ({ 'Authorization': `Bearer ${key}` })
    },
    claude: {
        endpoint: 'https://api.anthropic.com/v1/messages',
        buildBody: (model, messages) => ({
            model,
            messages: messages.filter(m => m.role !== 'system'),
            system: messages.find(m => m.role === 'system')?.content || '',
            stream: false,
            max_tokens: 500
        }),
        parseResponse: (data) => data.content?.[0]?.text || '',
        authHeader: (key) => ({
            'x-api-key': key,
            'anthropic-version': '2023-06-01'
        })
    },
    mistral: {
        endpoint: 'https://api.mistral.ai/v1/chat/completions',
        buildBody: (model, messages) => ({
            model,
            messages,
            stream: false,
            max_tokens: 500
        }),
        parseResponse: (data) => data.choices?.[0]?.message?.content || '',
        authHeader: (key) => ({ 'Authorization': `Bearer ${key}` })
    },
    zhipu: {
        endpoint: 'https://open.bigmodel.cn/api/paas/v4/chat/completions',
        buildBody: (model, messages) => ({
            model,
            messages,
            stream: false,
            max_tokens: 500
        }),
        parseResponse: (data) => data.choices?.[0]?.message?.content || '',
        authHeader: (key) => ({ 'Authorization': `Bearer ${key}` })
    },
    moonshot: {
        endpoint: 'https://api.moonshot.cn/v1/chat/completions',
        buildBody: (model, messages) => ({
            model,
            messages,
            stream: false,
            max_tokens: 500
        }),
        parseResponse: (data) => data.choices?.[0]?.message?.content || '',
        authHeader: (key) => ({ 'Authorization': `Bearer ${key}` })
    },
    baidu: {
        endpoint: 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat',
        buildBody: (model, messages) => ({
            messages: messages.map(m => ({ role: m.role, content: m.content }))
        }),
        parseResponse: (data) => data.result || '',
        buildUrl: (endpoint, model, apiKey) => `${endpoint}/${model}?access_token=${apiKey}`,
        authHeader: () => ({}) // Baidu uses URL parameter
    }
};

export async function onRequestPost({ request, env }) {
    try {
        const { platform, model, messages, apiKey } = await request.json();

        if (!platform || !apiKey) {
            return new Response(JSON.stringify({ error: 'Missing platform or apiKey' }), {
                status: 400,
                headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
            });
        }

        const config = PLATFORM_CONFIGS[platform];
        if (!config) {
            return new Response(JSON.stringify({ error: `Unsupported platform: ${platform}` }), {
                status: 400,
                headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
            });
        }

        let url = config.endpoint;
        const headers = {
            'Content-Type': 'application/json',
            ...config.authHeader(apiKey)
        };

        const body = config.buildBody(model, messages);

        // Special handling for platforms that need API key in URL
        if (config.buildUrl) {
            url = config.buildUrl(config.endpoint, model, apiKey);
        }

        const controller = new AbortController();
        const timeoutId = setTimeout(()=>(controller.abort()), 30000);
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
                error: `API call failed: ${response.status}`,
                details: errText.substring(0, 500)
            }), {
                status: response.status,
                headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
            });
        }

        const data = await response.json();
        const content = config.parseResponse(data);

        return new Response(JSON.stringify({ content }), {
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
