---
title: Task Context Storage
type: thread
topics: [Concurrency & Multithreading]
subtopic: Swift Concurrency Internals
status: draft
---

# Task Context Storage - Где хранится информация о Task

## Основная концепция

Когда вы вызываете `Task.checkCancellation()` или обращаетесь к `Task.isCancelled`, Swift Runtime знает о текущей задаче благодаря **Task-Local Storage** (хранилище локальное для задачи).

## Как это работает внутри

### 1. Thread-Local Storage (TLS)

Swift Runtime использует **thread-local storage** для хранения ссылки на текущую задачу:

```swift
// Концептуально внутри Swift Runtime:
// Каждый поток имеет указатель на текущую задачу
@_silgen_name("swift_task_getCurrent")
func _getCurrentTask() -> UnsafeRawPointer?

// Когда вы вызываете Task.checkCancellation():
extension Task {
    static func checkCancellation() throws {
        // 1. Runtime получает текущую задачу из TLS
        if let currentTask = _getCurrentTask() {
            // 2. Проверяет флаг отмены в структуре задачи
            if taskIsCancelled(currentTask) {
                throw CancellationError()
            }
        }
    }
}
```

### 2. Task Structure

Каждая задача представлена структурой в памяти (упрощенно):

```swift
// Внутреннее представление (концептуально)
struct TaskStorage {
    var priority: TaskPriority
    var isCancelled: Bool
    var parent: UnsafeRawPointer?      // Родительская задача
    var childTasks: [UnsafeRawPointer] // Дочерние задачи
    var continuation: UnsafeContinuation? // Точка возврата
    var taskLocalValues: [AnyKeyPath: Any] // Task-local значения
    
    // Executor information
    var preferredExecutor: SerialExecutor?
    var currentExecutor: SerialExecutor?
}
```

### 3. Процесс выполнения

```
┌──────────────────────────────────────────────────────┐
│  Thread 1                                             │
│  ┌─────────────────────────────────────────────────┐ │
│  │ Thread-Local Storage (TLS)                      │ │
│  │  currentTask -> 0x12345678                      │ │
│  └─────────────────────────────────────────────────┘ │
│                        │                              │
│                        ▼                              │
│  ┌─────────────────────────────────────────────────┐ │
│  │ Task Memory @ 0x12345678                        │ │
│  │ ┌─────────────────────────────────────────────┐ │ │
│  │ │ priority: .medium                           │ │ │
│  │ │ isCancelled: false                          │ │ │
│  │ │ parent: 0x12340000                          │ │ │
│  │ │ continuation: ...                           │ │ │
│  │ │ taskLocalValues: [...]                      │ │ │
│  │ └─────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

### 4. Context Switch при await

Когда код достигает точки `await`, происходит следующее:

```swift
func fetchData() async -> Data {
    print("Before await - Task context: \(Task.currentPriority)")
    
    // При await:
    let data = await URLSession.shared.data(from: url).0
    
    // 1. Runtime сохраняет текущее состояние (continuation)
    // 2. Освобождает поток
    // 3. Когда результат готов, может продолжить на другом потоке
    // 4. Но контекст задачи (Task context) остаётся тем же!
    
    print("After await - Task context: \(Task.currentPriority)")
    // Тот же приоритет, хотя возможно другой поток
    return data
}
```

**Важно**: Хотя выполнение может продолжиться на другом потоке, Swift Runtime автоматически восстанавливает правильный Task context в TLS нового потока.

## Task-Local Values

Swift также поддерживает хранение значений, специфичных для задачи:

```swift
enum UserContext {
    @TaskLocal static var userId: String?
    @TaskLocal static var requestId: UUID?
}

func processRequest() async {
    UserContext.$userId.withValue("user123") {
        UserContext.$requestId.withValue(UUID()) {
            await doWork() // Внутри doWork доступны userId и requestId
        }
    }
}

func doWork() async {
    // Эти значения "магически" доступны благодаря task-local storage
    print("User: \(UserContext.userId ?? "unknown")")
    print("Request: \(UserContext.requestId?.uuidString ?? "unknown")")
    
    // Они хранятся в taskLocalValues словаре текущей задачи
}
```

### Внутреннее устройство @TaskLocal

```swift
// Упрощенная концепция
@propertyWrapper
struct TaskLocal<Value> {
    private let key: AnyKeyPath
    
    var wrappedValue: Value? {
        get {
            // 1. Получить текущую задачу из TLS
            guard let currentTask = _getCurrentTask() else { return nil }
            // 2. Прочитать значение из её словаря taskLocalValues
            return getTaskLocalValue(currentTask, forKey: key) as? Value
        }
    }
    
    func withValue<R>(_ value: Value, operation: () async throws -> R) async rethrows -> R {
        // 1. Сохранить старое значение
        // 2. Установить новое в taskLocalValues текущей задачи
        // 3. Выполнить operation
        // 4. Восстановить старое значение
    }
}
```

## Structured Concurrency и иерархия задач

```swift
Task {  // Parent Task @ 0x1000
    print(Task.isCancelled) // false
    
    await withTaskGroup(of: Int.self) { group in
        group.addTask {  // Child Task @ 0x2000
            // parent: 0x1000
            try Task.checkCancellation() // Проверит свой флаг
        }
        
        group.addTask {  // Child Task @ 0x3000
            // parent: 0x1000
            try Task.checkCancellation()
        }
    }
}

// Если отменить Parent Task:
// 1. Устанавливается флаг isCancelled в структуре @ 0x1000
// 2. Runtime автоматически устанавливает флаги для @ 0x2000 и @ 0x3000
// 3. Следующий checkCancellation() в дочерних задачах выбросит ошибку
```

## Cooperative Cancellation

Важно понимать, что отмена кооперативная:

```swift
Task {
    // Runtime установил isCancelled = true
    // Но код продолжает выполняться!
    
    await heavyWork() // Выполнится
    
    // Только явная проверка останавливает выполнение:
    try Task.checkCancellation() // ❌ Throws CancellationError
    
    await moreWork() // Не выполнится
}
```

## Executor Context

Помимо Task context, также есть Executor context:

```swift
actor MyActor {
    func doWork() async {
        // Здесь:
        // - Task context: текущая задача из TLS
        // - Executor context: SerialExecutor этого актора
        // Runtime гарантирует, что код выполняется на правильном executor
    }
}

@MainActor
func updateUI() {
    // Task context: из TLS
    // Executor context: MainActor.shared.executor
    // Runtime гарантирует выполнение на main thread
}
```

## Ключевые моменты

1. **TLS (Thread-Local Storage)** - каждый поток знает, какую задачу он сейчас выполняет
2. **Task Structure** - вся информация о задаче (приоритет, отмена, родитель и т.д.) хранится в куче
3. **Context Switch** - при переключении потоков Runtime восстанавливает правильный Task context
4. **Иерархия** - parent/child связи позволяют автоматически распространять отмену
5. **Task-Local Values** - хранятся в словаре внутри структуры задачи

## Практический пример

```swift
func demonstrateTaskContext() async {
    let mainTask = Task {
        print("Main task on thread: \(Thread.current)")
        // TLS thread 1: currentTask = mainTask
        
        let result = await withTaskGroup(of: String.self) { group in
            group.addTask {
                print("Child 1 on thread: \(Thread.current)")
                // TLS thread 2: currentTask = childTask1
                // childTask1.parent = mainTask
                
                try? Task.checkCancellation() // Проверяет childTask1.isCancelled
                return "Result 1"
            }
            
            group.addTask {
                print("Child 2 on thread: \(Thread.current)")
                // TLS thread 3: currentTask = childTask2
                // childTask2.parent = mainTask
                
                try? Task.checkCancellation() // Проверяет childTask2.isCancelled
                return "Result 2"
            }
            
            var results: [String] = []
            for await result in group {
                // Может выполняться на разных потоках
                // Но всегда в контексте mainTask
                results.append(result)
            }
            return results
        }
        
        return result
    }
    
    // Отмена распространяется по иерархии:
    mainTask.cancel()
    // mainTask.isCancelled = true
    // childTask1.isCancelled = true (автоматически)
    // childTask2.isCancelled = true (автоматически)
}
```

## Связь с Operation Queue

Для сравнения, в старом подходе с GCD/Operation:

```swift
let operation = BlockOperation {
    // Здесь нет автоматического "текущего контекста"
    // Нужно вручную передавать состояние
    
    if operation.isCancelled { return }
    // ^^^^^^^ Нужно знать конкретный экземпляр!
}
```

С Task:
```swift
Task {
    // Не нужно знать конкретный экземпляр
    try Task.checkCancellation() // Автоматически находит текущую задачу
}
```

## Ссылки

- [Swift Evolution: Task Local Values](https://github.com/apple/swift-evolution/blob/main/proposals/0311-task-locals.md)
- [Swift Concurrency Manifesto](https://gist.github.com/lattner/31ed37682ef1576b16bca1432ea9f782)
- [Understanding Swift Concurrency's Task](https://www.donnywals.com/understanding-swift-concurrencys-task/)
