---
title: Codable
type: thread
topics: [Persistence]
subtopic: codable
status: draft
---

# Codable


### Encoding
```swift
let encoder = JSONEncoder()
let data = try encoder.encode(object)
```

### Decoding
```swift
let decoder = JSONDecoder()
let object = try decoder.decode(MyType.self, from: data)
```

### Custom Coding
- CodingKeys
- Custom init(from:)
- Custom encode(to:)

### Strategies
- Date encoding
- Data encoding
- Key encoding
- Non-conforming float

