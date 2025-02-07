import { OpenAPI } from './index';

interface ChatStreamRequest {
    message: string;
    system_prompt?: string;
    model?: 'anthropic' | 'openai';
}

export class StreamingError extends Error {
    constructor(public status: number, message: string) {
        super(message);
        this.name = 'StreamingError';
    }
}

export async function* createChatStream(request: ChatStreamRequest) {
    // Debug logging
    console.log('OpenAPI config:', {
        BASE: OpenAPI.BASE,
        TOKEN: OpenAPI.TOKEN
    });
    
    const url = `${OpenAPI.BASE}/api/v1/learn/chat/stream`;
    console.log('Request URL:', url);

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(request)
    });

    if (!response.ok) {
        throw new StreamingError(
            response.status,
            `HTTP error! status: ${response.status}`
        );
    }

    const reader = response.body!.getReader();
    const decoder = new TextDecoder();

    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        if (data.type === 'content' && data.content) {
                            yield data.content;
                        }
                    } catch (e) {
                        console.error('Error parsing SSE data:', e);
                    }
                }
            }
        }
    } finally {
        reader.releaseLock();
    }
} 