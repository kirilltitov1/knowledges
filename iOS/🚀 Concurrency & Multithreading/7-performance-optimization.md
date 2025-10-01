---
title: 7. Performance & Optimization
type: thread
topics: [Concurrency & Multithreading]
subtopic: 7-performance-optimization
status: draft
---

# 7. Performance & Optimization


### Thread Pool Management
- Avoid thread explosion
- Reuse queues
- Appropriate QoS

### Avoiding Main Thread Blocking
```swift
// Bad
DispatchQueue.main.sync { } // Deadlock risk

// Good
DispatchQueue.main.async { }
await MainActor.run { }
```

### Efficient Task Cancellation
```swift
Task {
    try Task.checkCancellation()
    await work()
}
```

### Memory Management
- Weak/unowned references
- Cancel subscriptions
- Dispose bags
- Task cancellation

