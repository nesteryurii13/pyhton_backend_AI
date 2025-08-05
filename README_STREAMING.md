# 🚀 Complete Streaming Guide for GPT Query API

## 📋 **Available Endpoints**

Your API now supports **3 types of GPT interactions**:

| Endpoint | Type | Use Case | Frontend |
|----------|------|----------|----------|
| `POST /api/v1/query` | Standard | Testing, Simple apps | Any HTTP client |
| `POST /api/v1/query/stream` | Server-Sent Events | Web applications | JavaScript EventSource |
| `WebSocket /api/v1/query/ws` | WebSocket | Real-time apps | WebSocket clients |

---

## 🌐 **1. Server-Sent Events (SSE) - Recommended for Web Apps**

### **Frontend JavaScript Example:**
```javascript
async function streamGPTQuery(query) {
    const response = await fetch('http://localhost:8001/api/v1/query/stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query: query,
            model: 'gpt-4o-mini',
            temperature: 0.7
        })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullResponse = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = line.slice(6);
                if (data === '[DONE]') {
                    console.log('✅ Stream completed!');
                    return fullResponse;
                }

                try {
                    const parsed = JSON.parse(data);
                    
                    switch (parsed.type) {
                        case 'start':
                            console.log(`🚀 Started with model: ${parsed.model}`);
                            break;
                        case 'content':
                            process.stdout.write(parsed.chunk); // Real-time display
                            fullResponse += parsed.chunk;
                            break;
                        case 'end':
                            console.log(`\n✅ Completed! Tokens: ${parsed.tokens_used}, Time: ${parsed.processing_time}s`);
                            break;
                        case 'error':
                            console.error(`❌ Error: ${parsed.error}`);
                            break;
                    }
                } catch (e) {
                    // Skip malformed JSON
                }
            }
        }
    }
}

// Usage
streamGPTQuery("Explain quantum computing in simple terms");
```

### **cURL Testing:**
```bash
curl -X POST "http://localhost:8001/api/v1/query/stream" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is artificial intelligence?", "model": "gpt-4o-mini"}' \
  --no-buffer
```

---

## 🔄 **2. WebSocket - Perfect for Interactive Apps**

### **Frontend JavaScript Example:**
```javascript
class GPTWebSocketClient {
    constructor(url = 'ws://localhost:8001/api/v1/query/ws') {
        this.url = url;
        this.ws = null;
    }

    connect() {
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(this.url);
            
            this.ws.onopen = () => {
                console.log('🔗 WebSocket connected!');
                resolve();
            };
            
            this.ws.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                reject(error);
            };
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            };
            
            this.ws.onclose = () => {
                console.log('🔒 WebSocket disconnected');
            };
        });
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'start':
                console.log(`🚀 Starting response with ${data.model}`);
                break;
            case 'content':
                process.stdout.write(data.chunk); // Real-time streaming
                break;
            case 'end':
                console.log(`\n✅ Response complete! Tokens: ${data.tokens_used}`);
                break;
            case 'error':
                console.error(`❌ Error: ${data.error}`);
                break;
        }
    }
    
    async sendQuery(query, options = {}) {
        if (this.ws.readyState !== WebSocket.OPEN) {
            await this.connect();
        }
        
        const message = {
            query,
            model: options.model || 'gpt-4o-mini',
            temperature: options.temperature || 0.7,
            max_tokens: options.max_tokens || 1000
        };
        
        this.ws.send(JSON.stringify(message));
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Usage
const client = new GPTWebSocketClient();

async function runChat() {
    await client.connect();
    
    // Send multiple queries in the same session
    await client.sendQuery("What is machine learning?");
    
    setTimeout(() => {
        client.sendQuery("Give me a Python example");
    }, 3000);
    
    setTimeout(() => {
        client.disconnect();
    }, 10000);
}

runChat();
```

### **Python WebSocket Client:**
```python
import asyncio
import websockets
import json

async def websocket_client():
    uri = "ws://localhost:8001/api/v1/query/ws"
    
    async with websockets.connect(uri) as websocket:
        print("🔗 Connected to WebSocket!")
        
        # Send query
        query_data = {
            "query": "Explain neural networks briefly",
            "model": "gpt-4o-mini",
            "temperature": 0.8
        }
        
        await websocket.send(json.dumps(query_data))
        print(f"📤 Sent: {query_data['query']}")
        
        # Receive streaming response
        full_response = ""
        async for message in websocket:
            data = json.loads(message)
            
            if data['type'] == 'start':
                print(f"🚀 Started with model: {data['model']}")
            elif data['type'] == 'content':
                print(data['chunk'], end='', flush=True)
                full_response += data['chunk']
            elif data['type'] == 'end':
                print(f"\n✅ Complete! Tokens: {data['tokens_used']}")
                break
            elif data['type'] == 'error':
                print(f"❌ Error: {data['error']}")
                break

# Run the client
asyncio.run(websocket_client())
```

---

## 📊 **3. Standard Endpoint - For Testing & Simple Use**

### **Postman/cURL:**
```bash
curl -X POST "http://localhost:8001/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello, how are you?", "model": "gpt-4o-mini"}'
```

---

## 🎯 **When to Use Each Method:**

### **✅ Use Server-Sent Events (SSE) when:**
- Building web applications
- Need real-time text streaming 
- Want simple HTTP-based streaming
- Building ChatGPT-like interfaces

### **✅ Use WebSocket when:**
- Need bidirectional communication
- Building interactive chat applications  
- Want persistent connections
- Need to send multiple queries per session

### **✅ Use Standard POST when:**
- Simple API integrations
- Testing with Postman/Swagger
- Don't need real-time streaming
- Building simple request-response apps

---

## 🔧 **Stream Response Format**

All streaming endpoints return these message types:

```javascript
// Start message
{
    "type": "start",
    "model": "gpt-4o-mini",
    "timestamp": 1704067200.123
}

// Content chunks (multiple)
{
    "type": "content", 
    "chunk": "Hello! I'm an AI assistant...",
    "accumulated_length": 42
}

// End message
{
    "type": "end",
    "full_response": "Complete response text...",
    "model_used": "gpt-4o-mini", 
    "tokens_used": 150,
    "processing_time": 2.45,
    "finish_reason": "stop"
}

// Error message (if any)
{
    "type": "error",
    "error": "Error description",
    "timestamp": "error"
}
```

---

## 🚀 **Quick Start Testing**

1. **Open Swagger UI:** http://localhost:8001/docs
2. **Test Standard Endpoint:** Try `/api/v1/query` 
3. **Test SSE:** Use the HTML file: `streaming_examples.html`
4. **Test WebSocket:** Use browser dev tools or Python script above

---

## 🏆 **Congratulations!** 

You now have a **production-ready streaming GPT API** with:

- ✅ **3 different interaction methods**
- ✅ **Real-time streaming responses** 
- ✅ **Professional error handling**
- ✅ **Complete documentation**
- ✅ **WebSocket & SSE support**
- ✅ **Ready for any frontend framework**

**Your API is ready for:**
- React/Vue/Angular apps
- Node.js backends  
- Python clients
- Mobile applications
- Real-time chat interfaces

🎉 **Happy coding!**