---
type: "thread"
status: "draft"
summary: ""
title: "2 Gcd Grand Central Dispatch"
---

# 2. GCD (Grand Central Dispatch)


### Dispatch Queues

#### Serial Queues
```swift
let serialQueue = DispatchQueue(label: "com.app.serial")
serialQueue.async {
    // Task 1
}
serialQueue.async {
    // Task 2 (waits for Task 1)
}
```

#### Concurrent Queues
```swift
let concurrentQueue = DispatchQueue(label: "com.app.concurrent", 
                                    attributes: .concurrent)
concurrentQueue.async {
    // Task 1
}
concurrentQueue.async {
    // Task 2 (runs in parallel)
}
```

#### Global Queues
- `.userInteractive` - highest priority
- `.userInitiated` - high priority
- `.default` - default priority
- `.utility` - low priority
- `.background` - lowest priority

#### Main Queue
```swift
DispatchQueue.main.async {
    // Update UI
}
```

### Dispatch Work Items
```swift
let workItem = DispatchWorkItem {
    // Task
}
queue.async(execute: workItem)
workItem.cancel()
```

### Quality of Service (QoS)
- User Interactive
- User Initiated
- Utility
- Background

### DispatchGroup
```swift
let group = DispatchGroup()

group.enter()
task1 { group.leave() }

group.enter()
task2 { group.leave() }

group.notify(queue: .main) {
    print("All tasks completed")
}

// Or wait synchronously
group.wait()
```

### DispatchSemaphore
```swift
let semaphore = DispatchSemaphore(value: 3) // Max 3 concurrent

semaphore.wait()
// Critical section
semaphore.signal()
```

### Barriers
```swift
queue.async(flags: .barrier) {
    // Exclusive access
}
```

### Dispatch Once (deprecated, use lazy/static)
```swift
// Old way
var token: dispatch_once_t = 0
dispatch_once(&token) { }

// New way
static let shared = MyClass()
```

### DispatchSource
- Timers
- File monitoring
- Process monitoring
- Memory pressure

## Вопросы собеседований
- Какие бывают очереди для GCD?
- Какие бывают серийные системные очереди?
- Как работает dispatch sync?
- Зачем нужны барьеры?
- Писал ли когда-то свой семафор?


