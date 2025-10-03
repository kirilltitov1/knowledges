---
title: 4. Swift Concurrency (Modern Approach)
type: thread
topics: [Concurrency & Multithreading]
subtopic: 4. Swift Concurrency
status: draft
---

# 4. Swift Concurrency (Modern Approach)


### Async/Await

#### Basic Async Function
```swift
func fetchData() async throws -> Data {
    let (data, _) = try await URLSession.shared.data(from: url)
    return data
}

// Calling
Task {
    let data = try await fetchData()
}
```

#### Sequential Execution
```swift
let result1 = await operation1()
let result2 = await operation2() // Waits for operation1
```

#### Parallel Execution
```swift
async let result1 = operation1()
async let result2 = operation2() // Runs in parallel
let results = try await [result1, result2]
```

### Tasks

#### Task
```swift
let task = Task {
    await doSomething()
}
task.cancel()
```

#### Task with Priority
```swift
Task(priority: .high) {
    await importantWork()
}
```

#### Detached Task
```swift
Task.detached {
    // Independent task
    await backgroundWork()
}
```

#### Task Groups
```swift
await withTaskGroup(of: String.self) { group in
    for i in 1...10 {
        group.addTask {
            await fetchData(id: i)
        }
    }
    
    for await result in group {
        print(result)
    }
}
```

#### Throwing Task Groups
```swift
try await withThrowingTaskGroup(of: Data.self) { group in
    group.addTask { try await fetch1() }
    group.addTask { try await fetch2() }
    
    for try await data in group {
        process(data)
    }
}
```

### Actors

#### Actor Definition
```swift
actor BankAccount {
    private var balance: Double = 0
    
    func deposit(amount: Double) {
        balance += amount
    }
    
    func withdraw(amount: Double) -> Bool {
        guard balance >= amount else { return false }
        balance -= amount
        return true
    }
}
```

#### Actor Usage
```swift
let account = BankAccount()
await account.deposit(amount: 100)
let success = await account.withdraw(amount: 50)
```

#### Nonisolated
```swift
actor MyActor {
    nonisolated func publicMethod() {
        // No await needed, but no access to actor state
    }
}
```

### @MainActor

#### Main Actor Isolation
```swift
@MainActor
class ViewModel: ObservableObject {
    @Published var data: [String] = []
    
    func loadData() async {
        // Already on main actor
        data = await fetchData()
    }
}
```

#### Individual Methods
```swift
class MyClass {
    @MainActor
    func updateUI() {
        // Runs on main thread
    }
}
```

### Continuations

#### Bridging Callbacks to Async/Await
```swift
func legacyAPI(completion: @escaping (Result<Data, Error>) -> Void) { }

func modernAPI() async throws -> Data {
    try await withCheckedThrowingContinuation { continuation in
        legacyAPI { result in
            continuation.resume(with: result)
        }
    }
}
```

#### Unsafe Continuations
```swift
await withUnsafeContinuation { continuation in
    // Must call resume exactly once
    continuation.resume(returning: value)
}
```

### AsyncSequence

#### Async Stream
```swift
let stream = AsyncStream<Int> { continuation in
    Task {
        for i in 1...10 {
            continuation.yield(i)
            try? await Task.sleep(nanoseconds: 1_000_000_000)
        }
        continuation.finish()
    }
}

for await number in stream {
    print(number)
}
```

#### Custom AsyncSequence
```swift
struct AsyncCountdown: AsyncSequence {
    typealias Element = Int
    let count: Int
    
    func makeAsyncIterator() -> AsyncCountdownIterator {
        AsyncCountdownIterator(count: count)
    }
}
```

### Structured Concurrency

#### Automatic Cancellation
```swift
func processData() async {
    await withTaskGroup(of: Void.self) { group in
        group.addTask { await task1() }
        group.addTask { await task2() }
        // If parent is cancelled, all child tasks are cancelled
    }
}
```

#### Task Cancellation Handling
```swift
func longRunningTask() async {
    while !Task.isCancelled {
        await doWork()
    }
    // Cleanup
}
```

