---
title: Вопросы по многопоточности и асинхронности для собеседований iOS
type: guide
topics: [Concurrency, Multithreading, Interview Preparation]
subtopic: ios-concurrency-questions
status: draft
level: advanced
platforms: [iOS, macOS, watchOS, tvOS]
ios_min: "13.0"
duration: 75m
tags: [concurrency, multithreading, gcd, async-await, actors, thread-safety, interview-questions]
---

# ⚡ Вопросы по многопоточности и асинхронности для собеседований iOS

Комплексный сборник вопросов по concurrency в iOS, включая GCD, async/await, actors и thread safety - критически важные темы для senior iOS разработчиков.

## 📋 Основные темы concurrency в iOS

### 🎯 Ключевые концепции
- **GCD (Grand Central Dispatch)** - низкоуровневая многопоточность
- **Async/await** - современный синтаксис асинхронности (iOS 13+)
- **Actors** - изоляция данных для потокобезопасности (iOS 15+)
- **Thread safety** - предотвращение race conditions
- **QoS (Quality of Service)** - приоритизация задач

## 🔄 GCD (Grand Central Dispatch)

### Базовые концепции

**Вопрос:** Что такое GCD и зачем он нужен?

**Ответ:** GCD - библиотека для выполнения задач асинхронно и управления очередями в iOS/macOS. Позволяет эффективно использовать многоядерные процессоры без управления потоками вручную.

**Вопрос:** Объясните разницу между serial и concurrent очередями.

**Ответ:**
- **Serial queue**: задачи выполняются последовательно, одна за другой
- **Concurrent queue**: задачи выполняются параллельно, если ресурсы позволяют

```swift
// Serial очередь
let serialQueue = DispatchQueue(label: "com.app.serial")

// Concurrent очередь
let concurrentQueue = DispatchQueue(label: "com.app.concurrent",
                                   attributes: .concurrent)
```

**Вопрос:** Что такое main queue и почему важно выполнять UI обновления только в ней?

**Ответ:** Main queue ассоциирована с главным потоком приложения. Все обновления пользовательского интерфейса должны выполняться в main queue для избежания race conditions и крашей.

```swift
// ✅ Правильно - обновление UI в main queue
DispatchQueue.main.async {
    self.label.text = "Updated"
}

// ❌ Неправильно - обновление UI в фоновой очереди
DispatchQueue.global().async {
    self.label.text = "Updated" // Может вызвать краш
}
```

### Кастомные очереди и группы

**Вопрос:** Как создать кастомную очередь с определенным QoS?

**Ответ:** Качество сервиса (QoS) определяет приоритет задачи в системе.

```swift
let userInitiatedQueue = DispatchQueue(
    label: "com.app.userInitiated",
    qos: .userInitiated
)

let backgroundQueue = DispatchQueue(
    label: "com.app.background",
    qos: .background
)
```

**Вопрос:** Объясните DispatchGroup и когда его использовать.

**Ответ:** DispatchGroup позволяет синхронизировать выполнение группы асинхронных задач.

```swift
let group = DispatchGroup()

// Добавляем задачи в группу
group.enter()
networkService.fetchUser { group.leave() }

group.enter()
networkService.fetchPosts { group.leave() }

// Ждем завершения всех задач
group.notify(queue: .main) {
    print("Все данные загружены")
}
```

## 🎭 Async/Await (iOS 13+)

### Основы async/await

**Вопрос:** Что такое async/await и чем он лучше completion handlers?

**Ответ:** Async/await - современный синтаксис для асинхронного программирования, который делает код более читаемым и менее подверженным ошибкам по сравнению с callback hell.

```swift
// ❌ Callback hell
networkService.fetchUser { userResult in
    networkService.fetchPosts(userId: userResult.id) { postsResult in
        // Вложенные замыкания
    }
}

// ✅ Async/await
func loadUserData() async throws -> UserData {
    let user = try await networkService.fetchUser()
    let posts = try await networkService.fetchPosts(userId: user.id)
    return UserData(user: user, posts: posts)
}
```

**Вопрос:** Объясните разницу между async и async throws функциями.

**Ответ:**
- **async**: функция может приостановиться и возобновиться позже
- **async throws**: функция может как приостановиться, так и выбросить ошибку

**Вопрос:** Что такое Task и как его использовать?

**Ответ:** Task - единица асинхронной работы в Swift Concurrency.

```swift
// Создание задачи
Task {
    do {
        let data = try await fetchData()
        updateUI(with: data)
    } catch {
        handleError(error)
    }
}

// Task с приоритетом
Task(priority: .high) {
    await performImportantWork()
}
```

### Структурированная многозадачность

**Вопрос:** Что такое структурированная многозадачность?

**Ответ:** Структурированная многозадачность обеспечивает правильную отмену и очистку ресурсов для группы асинхронных задач.

```swift
func loadUserProfile() async throws -> UserProfile {
    async let user = fetchUser()
    async let posts = fetchPosts()
    async let followers = fetchFollowers()

    return try await UserProfile(
        user: user,
        posts: posts,
        followers: followers
    )
}
```

**Вопрос:** Объясните TaskGroup и когда его использовать.

**Ответ:** TaskGroup позволяет динамически создавать и управлять множеством задач.

```swift
func loadMultipleUsers(_ userIds: [Int]) async throws -> [User] {
    return try await withThrowingTaskGroup(of: User.self) { group in
        for userId in userIds {
            group.addTask {
                return try await fetchUser(id: userId)
            }
        }

        var users = [User]()
        for try await user in group {
            users.append(user)
        }

        return users
    }
}
```

## 🛡️ Actors (iOS 15+)

### Основы actors

**Вопрос:** Что такое actors в Swift и зачем они нужны?

**Ответ:** Actors - тип данных для безопасного доступа к изменяемому состоянию из нескольких потоков без race conditions.

```swift
@MainActor
class ViewModel: ObservableObject {
    @Published private(set) var users = [User]()

    func loadUsers() async {
        do {
            users = try await fetchUsers()
        } catch {
            // Handle error
        }
    }
}

// Actor для изоляции данных
actor UserManager {
    private var users = [User]()

    func addUser(_ user: User) {
        users.append(user)
    }

    func getUsers() -> [User] {
        return users
    }
}
```

**Вопрос:** Объясните разницу между @MainActor и обычными actors.

**Ответ:**
- **@MainActor**: гарантирует выполнение в главном потоке
- **Actor**: обеспечивает изоляцию данных, но может выполняться в любом потоке

**Вопрос:** Что такое actor isolation и как она работает?

**Ответ:** Actor isolation гарантирует, что изменяемое состояние actor'а доступно только из того же actor'а.

```swift
actor Counter {
    private var value = 0

    func increment() { // ✅ Изоляция работает
        value += 1
    }

    func getValue() -> Int {
        return value
    }
}

// ❌ Нарушение изоляции (компилятор выдаст ошибку)
let counter = Counter()
Task {
    await counter.increment() // ✅ Корректно
    counter.value += 1 // ❌ Ошибка компиляции
}
```

## 🛡️ Thread Safety

### Race Conditions

**Вопрос:** Что такое race condition и как его избежать?

**Ответ:** Race condition - ситуация, когда результат программы зависит от порядка выполнения операций в разных потоках.

```swift
// ❌ Race condition
class Counter {
    private var value = 0

    func increment() {
        let current = value      // Чтение
        value = current + 1      // Запись
    }
}

// ✅ Thread-safe решение
class ThreadSafeCounter {
    private var value = 0
    private let queue = DispatchQueue(label: "counter")

    func increment() {
        queue.sync {
            value += 1
        }
    }

    func getValue() -> Int {
        return queue.sync { value }
    }
}
```

**Вопрос:** Объясните разницу между atomic и non-atomic свойствами.

**Ответ:**
- **Atomic**: гарантирует атомарность операции чтения/записи
- **Non-atomic**: быстрее, но не thread-safe

### Потокобезопасные коллекции

**Вопрос:** Как сделать Dictionary thread-safe?

**Ответ:** Использовать DispatchQueue для синхронизации доступа.

```swift
class ThreadSafeDictionary<Key: Hashable, Value> {
    private var dict = [Key: Value]()
    private let queue = DispatchQueue(label: "dict")

    func set(_ value: Value, for key: Key) {
        queue.sync {
            dict[key] = value
        }
    }

    func get(_ key: Key) -> Value? {
        return queue.sync {
            return dict[key]
        }
    }
}
```

## 🔄 Operation Queue

### Основы Operation Queue

**Вопрос:** Что такое Operation и OperationQueue?

**Ответ:** Operation - абстракция над задачей, OperationQueue - очередь для управления выполнением операций.

```swift
// Создание операции
class FetchUserOperation: Operation {
    override func main() {
        // Выполнение задачи
        fetchUserFromServer()
    }
}

// Использование очереди
let queue = OperationQueue()
queue.maxConcurrentOperationCount = 3

let operation = FetchUserOperation()
queue.addOperation(operation)
```

**Вопрос:** Объясните зависимости между операциями.

**Ответ:** Операции могут зависеть друг от друга для контроля порядка выполнения.

```swift
let fetchUserOp = FetchUserOperation()
let fetchPostsOp = FetchPostsOperation()
let updateUIOp = UpdateUIOperation()

// fetchPostsOp зависит от fetchUserOp
fetchPostsOp.addDependency(fetchUserOp)

// updateUIOp зависит от обеих операций
updateUIOp.addDependency(fetchUserOp)
updateUIOp.addDependency(fetchPostsOp)

queue.addOperations([fetchUserOp, fetchPostsOp, updateUIOp], waitUntilFinished: false)
```

## 📊 Инструменты диагностики concurrency

### 1. Thread Sanitizer

**Вопрос:** Что такое Thread Sanitizer и как его включить?

**Ответ:** Thread Sanitizer обнаруживает race conditions и другие проблемы многопоточности.

```bash
// В Build Settings
ENABLE_THREAD_SANITIZER = YES

// Или через схему запуска
Edit Scheme → Diagnostics → Enable Thread Sanitizer
```

### 2. Main Thread Checker

**Вопрос:** Что делает Main Thread Checker?

**Ответ:** Main Thread Checker обнаруживает попытки обновления UI из фоновых потоков.

```bash
// Включение
Edit Scheme → Diagnostics → Main Thread Checker
```

## 🎯 Вопросы для собеседований

### Базовый уровень

**Вопрос:** Объясните разницу между sync и async в GCD.

**Ответ:**
- **sync**: блокирует текущий поток до завершения задачи
- **async**: не блокирует, выполняется параллельно

**Вопрос:** Что такое deadlock и как его избежать?

**Ответ:** Deadlock - ситуация, когда два или более потоков ждут друг друга.

```swift
// ❌ Deadlock
DispatchQueue.main.sync {
    DispatchQueue.main.sync {
        // Внутренний блок ждет main queue, которая уже занята внешним блоком
    }
}
```

**Вопрос:** Что такое QoS в GCD?

**Ответ:** Quality of Service определяет приоритет задачи в системе.

```swift
enum DispatchQoS {
    case userInteractive    // Высокий приоритет, UI
    case userInitiated      // Пользовательские действия
    case utility           // Длительные операции
    case background        // Фоновые задачи
}
```

### Средний уровень

**Вопрос:** Объясните разницу между DispatchQueue и OperationQueue.

**Ответ:**
- **DispatchQueue**: низкоуровневый API для управления очередями
- **OperationQueue**: высокоуровневый API с поддержкой зависимостей и отмены

**Вопрос:** Что такое actor reentrancy?

**Ответ:** Actor reentrancy - ситуация, когда actor вызывает асинхронный метод на себе же.

```swift
actor BankAccount {
    private var balance = 0

    func transfer(amount: Int, to other: BankAccount) async {
        balance -= amount
        await other.deposit(amount) // ✅ Не вызывает себя рекурсивно

        // ❌ Неправильно - вызов себя
        // await self.updateBalance()
    }
}
```

**Вопрос:** Объясните global actor isolation.

**Ответ:** Global actor обеспечивает изоляцию данных для всего приложения.

```swift
@globalActor
actor NetworkActor {
    static let shared = NetworkActor()
}

@NetworkActor
func fetchData() async -> Data {
    return try await networkRequest()
}
```

### Продвинутый уровень

**Вопрос:** Что такое continuation в async/await?

**Ответ:** Continuation - механизм для интеграции callback-based API с async/await.

```swift
func fetchDataWithContinuation(_ completion: @escaping (Data?) -> Void) {
    // Legacy callback-based API
    networkService.fetchData { data in
        completion(data)
    }
}

// Мост к async/await
func fetchData() async -> Data? {
    return await withCheckedContinuation { continuation in
        fetchDataWithContinuation { data in
            continuation.resume(returning: data)
        }
    }
}
```

**Вопрос:** Объясните Task cancellation и как с ней работать.

**Ответ:** Task cancellation позволяет отменять асинхронные операции.

```swift
Task {
    do {
        let data = try await fetchData()
        // Проверяем отмену задачи
        try Task.checkCancellation()
        processData(data)
    } catch {
        if error is CancellationError {
            print("Задача была отменена")
        }
    }
}

// Отмена задачи
let task = Task { await longRunningOperation() }
task.cancel()
```

## 🧪 Практические задания

### 1. Thread-safe коллекция

**Задание:** Реализуйте thread-safe версию массива с использованием actor.

```swift
actor ThreadSafeArray<Element> {
    private var array = [Element]()

    func append(_ element: Element) {
        array.append(element)
    }

    func remove(at index: Int) -> Element? {
        guard index < array.count else { return nil }
        return array.remove(at: index)
    }

    func getAll() -> [Element] {
        return array
    }

    func count() -> Int {
        return array.count
    }
}
```

### 2. Async/await с legacy API

**Задание:** Создайте мост между callback-based API и async/await.

```swift
class LegacyNetworkService {
    func fetchUser(id: Int, completion: @escaping (User?) -> Void) {
        // Имитация сетевого запроса
        DispatchQueue.global().asyncAfter(deadline: .now() + 1) {
            completion(User(id: id, name: "User \(id)"))
        }
    }
}

// Мост к async/await
extension LegacyNetworkService {
    func fetchUser(id: Int) async -> User? {
        return await withCheckedContinuation { continuation in
            fetchUser(id: id) { user in
                continuation.resume(returning: user)
            }
        }
    }
}
```

### 3. Actor для банковского счета

**Задание:** Реализуйте actor для управления банковским счетом с защитой от race conditions.

```swift
actor BankAccount {
    private var balance: Double = 0

    func deposit(_ amount: Double) {
        balance += amount
    }

    func withdraw(_ amount: Double) throws {
        guard balance >= amount else {
            throw BankError.insufficientFunds
        }
        balance -= amount
    }

    func transfer(_ amount: Double, to otherAccount: BankAccount) async throws {
        try withdraw(amount)
        await otherAccount.deposit(amount)
    }

    func getBalance() -> Double {
        return balance
    }
}
```

## 📈 Производительность и оптимизация

### Бенчмаркинг concurrency

**Вопрос:** Как измерить производительность многопоточного кода?

**Ответ:** Использовать Instruments для анализа потоков и времени выполнения.

```swift
// Измерение производительности
func benchmarkConcurrentOperations() {
    let startTime = DispatchTime.now()

    DispatchQueue.concurrentPerform(iterations: 1000) { index in
        // Выполнение задачи
        performTask(index)
    }

    let endTime = DispatchTime.now()
    let duration = Double(endTime.uptimeNanoseconds - startTime.uptimeNanoseconds) / 1_000_000_000
    print("Время выполнения: \(duration) секунд")
}
```

## 🎓 Подготовка к вопросам по concurrency

### 1. Теоретическая подготовка
- Изучите основы GCD и очередей
- Практикуйте async/await и actors
- Понимайте thread safety концепции

### 2. Практическая подготовка
- Создайте проекты с многопоточным кодом
- Практикуйте отладку race conditions
- Изучите Instruments для анализа производительности

### 3. Глубокое понимание
- Знайте различия между разными подходами к concurrency
- Умейте объяснять trade-offs решений
- Практикуйте объяснение сложных концепций простыми словами

Помните: "Многопоточность - это не только производительность, но и безопасность данных."
