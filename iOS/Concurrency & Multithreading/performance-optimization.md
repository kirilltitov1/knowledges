---
type: "thread"
status: "draft"
summary: ""
title: "Performance & Optimization"
---

# Performance & Optimization

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

### Ограничение параллелизма
```swift
let semaphore = DispatchSemaphore(value: 4)
for job in jobs {
    DispatchQueue.global().async {
        semaphore.wait()
        defer { semaphore.signal() }
        process(job)
    }
}
```

### Инструменты
- Instruments: Time Profiler, Allocations, Concurrency Template
- Thread Sanitizer (TSan) для гонок данных
- os_signpost для измерений разделов

### Рецепты
- Снижайте количество executor hops
- Минимизируйте критические секции
- Разгружайте main от тяжёлых операций


