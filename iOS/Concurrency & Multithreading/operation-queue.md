---
type: "thread"
status: "draft"
summary: ""
title: "Очереди операций (OperationQueue)"
---

# Очереди операций (OperationQueue)


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

## Подводные камни и решения

### Неправильные флаги isExecuting/isFinished
Обновляйте их с KVO-уведомлениями и потокобезопасно.
```swift
final class ProperAsyncOperation: Operation {
    override var isAsynchronous: Bool { true }
    private let state = DispatchQueue(label: "op.state")
    private var _executing = false
    private var _finished = false
    override private(set) var isExecuting: Bool {
        get { state.sync { _executing } }
        set { willChangeValue(forKey: "isExecuting"); state.sync { _executing = newValue }; didChangeValue(forKey: "isExecuting") }
    }
    override private(set) var isFinished: Bool {
        get { state.sync { _finished } }
        set { willChangeValue(forKey: "isFinished"); state.sync { _finished = newValue }; didChangeValue(forKey: "isFinished") }
    }
    override func start() {
        if isCancelled { finish(); return }
        isExecuting = true
        main()
    }
    func finish() { isExecuting = false; isFinished = true }
}
```

### Игнорирование отмены
Проверяйте `isCancelled` в ключевых точках и завершайте быстро.

### Циклические зависимости
Валидируйте граф перед запуском; используйте тесты на deadlock зависимостей.

## Чек-лист
- Настройте `maxConcurrentOperationCount`.
- Используйте зависимости вместо ручного ожидания.
- Реализуйте корректную отмену и завершение.


