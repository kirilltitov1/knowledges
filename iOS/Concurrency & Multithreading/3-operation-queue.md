---
title: 3. Operation Queue
type: thread
topics: [Concurrency & Multithreading]
subtopic: 3. Operation Queue
status: draft
---

# 3. Operation Queue


### NSOperation / Operation

#### Basic Operation
```swift
let operation = BlockOperation {
    // Task
}
operationQueue.addOperation(operation)
```

#### Custom Operation
```swift
class MyOperation: Operation {
    override func main() {
        guard !isCancelled else { return }
        // Task
    }
}
```

### NSOperationQueue
```swift
let queue = OperationQueue()
queue.maxConcurrentOperationCount = 3
queue.qualityOfService = .userInitiated
```

### Dependencies
```swift
let op1 = BlockOperation { }
let op2 = BlockOperation { }
op2.addDependency(op1) // op2 waits for op1
queue.addOperations([op1, op2], waitUntilFinished: false)
```

### Cancellation
```swift
operation.cancel()
queue.cancelAllOperations()

// Check in operation
guard !isCancelled else { return }
```

### Completion Blocks
```swift
operation.completionBlock = {
    print("Operation completed")
}
```

### Priority
- `.veryHigh`
- `.high`
- `.normal`
- `.low`
- `.veryLow`

### Asynchronous Operations
```swift
class AsyncOperation: Operation {
    override var isAsynchronous: Bool { true }
    override var isExecuting: Bool { _isExecuting }
    override var isFinished: Bool { _isFinished }
    
    private var _isExecuting = false
    private var _isFinished = false
}
```

## Вопросы собеседований
- Расскажи про Operation queue. В чем его плюсы по сравнению с GCD?
- Что такое семафор? (сравнение использования в GCD и Operation)
- Как работает context switch в многопоточности внутри операционки?
- Что нужно удерживать в контексте, чтобы продолжить работу в потоке с того же места?

