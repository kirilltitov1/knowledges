---
type: "thread"
status: "draft"
summary: ""
title: "Error Handling"
---

# Error Handling


### Error Types
- Network errors
- Server errors
- Parsing errors
- Timeout errors

### URLError
- `.notConnectedToInternet`
- `.timedOut`
- `.cannotFindHost`
- `.badServerResponse`

### Custom Errors
```swift
enum NetworkError: Error {
    case invalidURL
    case noData
    case decodingError
    case serverError(statusCode: Int)
}
```

### Retry Logic
- Exponential backoff
- Max retry count
- Idempotent requests

