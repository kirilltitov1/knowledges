---
title: UserDefaults
type: thread
topics: [Persistence]
subtopic: userdefaults
status: draft
---

# UserDefaults


### Basics
- Key-value storage
- Simple data types
- Property list types
- Synchronization

### Usage
```swift
UserDefaults.standard.set(value, forKey: "key")
let value = UserDefaults.standard.string(forKey: "key")
```

### Data Types
- Bool, Int, Float, Double
- String, Data
- Array, Dictionary
- URL, Date

### Best Practices
- Avoid storing sensitive data
- Small amounts of data
- Settings and preferences
- App state

### Property Wrappers
- @AppStorage (SwiftUI)
- Custom wrappers
- Type safety

