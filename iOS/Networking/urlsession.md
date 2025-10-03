---
title: URLSession
type: thread
topics: [Networking]
subtopic: URLSession
status: draft
---

# URLSession


### Основы
- URLSession configuration
  - `.default`
  - `.ephemeral`
  - `.background`
- URLRequest
- URLResponse
- Data tasks, Download tasks, Upload tasks

### Data Tasks
```swift
let task = URLSession.shared.dataTask(with: url) { data, response, error in
    // Handle response
}
task.resume()
```

### Async/Await (iOS 15+)
```swift
let (data, response) = try await URLSession.shared.data(from: url)
```

### Configuration
- Timeouts
- Cache policy
- Cookie handling
- HTTP headers
- Protocols

### Background Sessions
- Background downloads
- Background uploads
- Session delegation
- Handling callbacks

