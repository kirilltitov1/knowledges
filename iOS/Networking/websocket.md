---
type: "thread"
status: "draft"
summary: ""
title: "websocket"
---

# WebSocket


### Basics
- URLSessionWebSocketTask
- Connection lifecycle
- Sending messages
- Receiving messages

### Implementation
```swift
let webSocketTask = URLSession.shared.webSocketTask(with: url)
webSocketTask.resume()
```

### Use Cases
- Real-time updates
- Chat applications
- Live data feeds
- Bi-directional communication

### Best Practices
- Reconnection logic
- Heartbeat/ping-pong
- Error handling
- Resource management

