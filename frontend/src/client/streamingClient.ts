/**
 * Hardcoded API base URL for streaming endpoints
 * 
 * Note: While other endpoints use OpenAPI.BASE configuration,
 * the streaming client uses a direct URL to avoid timing issues
 * with configuration loading. This ensures the streaming endpoints
 * work reliably regardless of when OpenAPI.BASE is initialized.
 * 
 * If you need to change the API URL, update both:
 * 1. This constant
 * 2. The VITE_API_URL in your .env file
 */
const API_BASE = 'http://localhost:8000';
console.log('streamingClient loaded with API_BASE:', API_BASE);
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
    const url = `${API_BASE}/api/v1/learn/chat/stream`;
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
            try {
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
                            } else if (data.type === 'done') {
                                console.log('Stream completed successfully');
                                return;
                            } else if (data.type === 'error') {
                                throw new StreamingError(500, data.content || 'Stream error');
                            }
                        } catch (e) {
                            // Ignore JSON parse errors from incomplete chunks
                            if (line.trim()) {
                                console.debug('Skipping malformed SSE data:', line);
                            }
                        }
                    }
                }
            } catch (e) {
                // If we've received any content, consider the stream complete
                // rather than throwing an error
                console.debug('Stream ended early:', e);
                return;
            }
        }
    } finally {
        reader.releaseLock();
    }
} 