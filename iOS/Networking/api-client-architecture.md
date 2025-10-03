---
title: API Client Architecture
type: thread
topics:
  - Networking
subtopic: Architecture
status: draft
---

# API Client Architecture


### Service Layer
```swift
protocol APIService {
    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T
}
```

### Endpoint Definition
- Base URL
- Path
- Method
- Parameters
- Headers

### Request Builder
- URL construction
- Parameter encoding
- Header injection
- Authentication

### Response Handler
- Status code validation
- Data validation
- Error mapping
- Logging

## Вопросы собеседований
- Когда ты делал сетевой слой, каким инструментарием пользовался?
- Какие есть части http запроса? (связь с конструктором запросов)

