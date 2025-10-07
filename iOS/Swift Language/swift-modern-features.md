---
title: Современные возможности Swift - async/await, actors, property wrappers
type: guide
topics: [Swift Language, Modern Swift, Concurrency]
subtopic: swift-modern-features
status: draft
level: advanced
platforms: [iOS, macOS, watchOS, tvOS]
ios_min: "13.0"
duration: 120m
tags: [swift-modern, async-await, actors, property-wrappers, result-builders, swift-5-5, swift-concurrency]
---

# ⚡ Современные возможности Swift - async/await, actors, property wrappers

Комплексное руководство по современным возможностям Swift 5.5+: структурированной многозадачности, акторам и property wrappers.

## 📋 Содержание
- [Async/await и структурированная многозадачность](#asyncawait-и-структурированная-многозадачность)
- [Actors и изоляция данных](#actors-и-изоляция-данных)
- [Property Wrappers](#property-wrappers)
- [Result Builders](#result-builders)
- [AsyncSequence и AsyncStream](#asyncsequence-и-asyncstream)
- [Практические примеры](#практические-примеры)

## Async/await и структурированная многозадачность

### Основы async/await

```swift
// Асинхронная функция
func fetchUser(id: String) async throws -> User {
    let (data, _) = try await URLSession.shared.data(from: URL(string: "https://api.example.com/users/\(id)")!)
    return try JSONDecoder().decode(User.self, from: data)
}

// Использование
Task {
    do {
        let user = try await fetchUser(id: "123")
        print("Пользователь: \(user.name)")
    } catch {
        print("Ошибка: \(error)")
    }
}
```

### Структурированная многозадачность

#### Task Groups

```swift
func loadMultipleUsers(_ userIds: [String]) async throws -> [User] {
    return try await withThrowingTaskGroup(of: User.self) { group in
        // Добавляем задачи в группу
        for userId in userIds {
            group.addTask {
                return try await fetchUser(id: userId)
            }
        }

        // Собираем результаты
        var users = [User]()
        for try await user in group {
            users.append(user)
        }

        return users
    }
}
```

#### Async let

```swift
func loadUserData() async throws -> UserProfile {
    async let user = fetchUser(id: "123")
    async let posts = fetchPosts(userId: "123")
    async let followers = fetchFollowers(userId: "123")

    return try await UserProfile(
        user: user,
        posts: posts,
        followers: followers
    )
}
```

### Обработка ошибок

```swift
enum NetworkError: Error {
    case invalidURL
    case noData
    case decodingError
    case serverError(statusCode: Int)
}

// Асинхронная функция с обработкой ошибок
func fetchData() async throws -> Data {
    guard let url = URL(string: "https://api.example.com/data") else {
        throw NetworkError.invalidURL
    }

    let (data, response) = try await URLSession.shared.data(from: url)

    guard let httpResponse = response as? HTTPURLResponse else {
        throw NetworkError.noData
    }

    guard (200..<300).contains(httpResponse.statusCode) else {
        throw NetworkError.serverError(statusCode: httpResponse.statusCode)
    }

    return data
}

// Использование с различными типами ошибок
Task {
    do {
        let data = try await fetchData()
        // Обработка данных
    } catch NetworkError.invalidURL {
        print("Некорректный URL")
    } catch NetworkError.serverError(let statusCode) {
        print("Ошибка сервера: \(statusCode)")
    } catch {
        print("Неизвестная ошибка: \(error)")
    }
}
```

## Actors и изоляция данных

### Основы actors

```swift
// Actor для безопасного доступа к изменяемому состоянию
actor UserManager {
    private var users = [String: User]()

    func addUser(_ user: User) {
        users[user.id] = user
    }

    func getUser(id: String) -> User? {
        return users[id]
    }

    func getAllUsers() -> [User] {
        return Array(users.values)
    }
}

// Использование actor'а
let userManager = UserManager()

Task {
    await userManager.addUser(User(id: "1", name: "Alice"))

    if let user = await userManager.getUser(id: "1") {
        print("Найден пользователь: \(user.name)")
    }
}
```

### Global actors

```swift
@globalActor
actor NetworkActor {
    static let shared = NetworkActor()
}

@NetworkActor
func fetchData() async throws -> Data {
    // Эта функция выполняется в контексте NetworkActor
    return try await URLSession.shared.data(from: URL(string: "https://api.example.com")!).0
}

// Автоматическая изоляция
class ViewModel: ObservableObject {
    @Published private(set) var users = [User]()

    @NetworkActor
    func loadUsers() async {
        do {
            let data = try await fetchData()
            let users = try JSONDecoder().decode([User].self, from: data)

            // Обновление UI должно быть в main actor
            await MainActor.run {
                self.users = users
            }
        } catch {
            print("Ошибка загрузки: \(error)")
        }
    }
}
```

### Actor isolation

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
        // Проверка изоляции
        try await withdraw(amount)
        await otherAccount.deposit(amount)
    }

    func getBalance() -> Double {
        return balance
    }
}

// Использование
let account1 = BankAccount()
let account2 = BankAccount()

Task {
    await account1.deposit(1000)

    do {
        try await account1.transfer(500, to: account2)
        print("Перевод выполнен успешно")
    } catch {
        print("Ошибка перевода: \(error)")
    }
}
```

## Property Wrappers

### Базовые property wrappers

```swift
// Кастомный property wrapper
@propertyWrapper
struct Clamped<Value: Comparable> {
    private var value: Value
    private let range: ClosedRange<Value>

    init(wrappedValue: Value, range: ClosedRange<Value>) {
        self.range = range
        self.value = min(max(wrappedValue, range.lowerBound), range.upperBound)
    }

    var wrappedValue: Value {
        get { value }
        set { value = min(max(newValue, range.lowerBound), range.upperBound) }
    }
}

struct User {
    @Clamped(range: 0...100) var age: Int = 0
    @Clamped(range: 0...200) var height: Double = 0
}

// Использование
var user = User()
user.age = 150  // Автоматически станет 100
user.age = -10  // Автоматически станет 0
```

### @Published для Combine

```swift
import Combine

class ViewModel: ObservableObject {
    @Published var userName = ""
    @Published var isLoading = false
    @Published var users = [User]()

    private var cancellables = Set<AnyCancellable>()

    init() {
        // Автоматическая подписка на изменения
        $userName
            .debounce(for: 0.5, scheduler: DispatchQueue.main)
            .sink { [weak self] name in
                self?.searchUsers(with: name)
            }
            .store(in: &cancellables)
    }

    private func searchUsers(with name: String) {
        isLoading = true

        NetworkManager.shared.searchUsers(name: name)
            .receive(on: DispatchQueue.main)
            .sink { [weak self] completion in
                self?.isLoading = false
            } receiveValue: { [weak self] users in
                self?.users = users
            }
            .store(in: &cancellables)
    }
}
```

### @State и @Binding для SwiftUI

```swift
struct CounterView: View {
    @State private var count = 0

    var body: some View {
        VStack {
            Text("Count: \(count)")

            Button("Increment") {
                count += 1
            }

            ChildView(count: $count)  // Binding к State
        }
    }
}

struct ChildView: View {
    @Binding var count: Int

    var body: some View {
        Button("Decrement") {
            count -= 1
        }
    }
}
```

## Result Builders

### Кастомные result builders

```swift
@resultBuilder
struct StringBuilder {
    static func buildBlock(_ components: String...) -> String {
        return components.joined(separator: " ")
    }

    static func buildOptional(_ component: String?) -> String {
        return component ?? ""
    }

    static func buildEither(first component: String) -> String {
        return component
    }

    static func buildEither(second component: String) -> String {
        return component
    }

    static func buildArray(_ components: [String]) -> String {
        return components.joined(separator: ", ")
    }
}

// Использование
@StringBuilder
func buildGreeting(name: String, isFormal: Bool) -> String {
    "Hello"
    if isFormal {
        "Mr./Ms."
    }
    name
    if name.count > 10 {
        "!"
    } else {
        "!!"
    }
}

let greeting = buildGreeting(name: "Alice", isFormal: true)
// Результат: "Hello Mr./Ms. Alice !!"
```

### Result builders в SwiftUI

```swift
// SwiftUI использует result builders для построения View
struct ContentView: View {
    var body: some View {
        VStack {  // Result builder собирает компоненты
            Text("Hello")
            Text("World")
        }
    }
}

// Эквивалентно:
struct ContentView: View {
    var body: some View {
        VStack(content: {
            Text("Hello")
            Text("World")
        })
    }
}
```

## AsyncSequence и AsyncStream

### AsyncSequence протокол

```swift
// Кастомная асинхронная последовательность
struct Countdown: AsyncSequence {
    typealias Element = Int
    let start: Int

    func makeAsyncIterator() -> CountdownIterator {
        return CountdownIterator(start: start)
    }
}

struct CountdownIterator: AsyncIteratorProtocol {
    typealias Element = Int
    private var current: Int

    init(start: Int) {
        self.current = start
    }

    mutating func next() async -> Element? {
        guard current > 0 else { return nil }

        try? await Task.sleep(nanoseconds: 1_000_000_000)  // 1 секунда
        defer { current -= 1 }
        return current
    }
}

// Использование
Task {
    for await number in Countdown(start: 5) {
        print("Обратный отсчет: \(number)")
    }
    print("Старт!")
}
```

### AsyncStream

```swift
// Создание асинхронного потока
func generateNumbers() -> AsyncStream<Int> {
    return AsyncStream { continuation in
        Task {
            for i in 1...10 {
                try? await Task.sleep(nanoseconds: 500_000_000)  // 0.5 секунды
                continuation.yield(i)
            }
            continuation.finish()
        }
    }
}

// Использование
Task {
    for await number in generateNumbers() {
        print("Получено: \(number)")
    }
}
```

### AsyncThrowingStream

```swift
func fetchUsersStream() -> AsyncThrowingStream<User, Error> {
    return AsyncThrowingStream { continuation in
        Task {
            do {
                let users = try await NetworkManager.shared.fetchUsers()

                for user in users {
                    continuation.yield(user)
                }

                continuation.finish()
            } catch {
                continuation.finish(throwing: error)
            }
        }
    }
}

// Использование
Task {
    do {
        for try await user in fetchUsersStream() {
            print("Пользователь: \(user.name)")
        }
    } catch {
        print("Ошибка: \(error)")
    }
}
```

## Практические примеры

### 1. Современный сетевой менеджер

```swift
@globalActor
actor NetworkActor {
    static let shared = NetworkActor()
}

class ModernNetworkManager {
    @NetworkActor
    func fetchUser(id: String) async throws -> User {
        let (data, _) = try await URLSession.shared.data(from: URL(string: "https://api.example.com/users/\(id)")!)
        return try JSONDecoder().decode(User.self, from: data)
    }

    @NetworkActor
    func fetchUsers(ids: [String]) async throws -> [User] {
        return try await withThrowingTaskGroup(of: User.self) { group in
            for id in ids {
                group.addTask {
                    return try await self.fetchUser(id: id)
                }
            }

            return try await group.reduce(into: [User]()) { result, user in
                result.append(user)
            }
        }
    }
}

// Использование
Task {
    do {
        let users = try await NetworkManager.shared.fetchUsers(ids: ["1", "2", "3"])
        await MainActor.run {
            self.users = users
        }
    } catch {
        await MainActor.run {
            self.showError(error)
        }
    }
}
```

### 2. Actor для управления состоянием

```swift
actor AppState {
    private var users = [User]()
    private var isLoading = false
    private var lastError: Error?

    func setLoading(_ loading: Bool) {
        isLoading = loading
    }

    func addUser(_ user: User) {
        users.append(user)
    }

    func getUsers() -> [User] {
        return users
    }

    func setError(_ error: Error) {
        lastError = error
    }

    func getState() -> (users: [User], isLoading: Bool, error: Error?) {
        return (users, isLoading, lastError)
    }
}

// ViewModel с использованием actor'а
@MainActor
class UserViewModel: ObservableObject {
    @Published private(set) var users = [User]()
    @Published private(set) var isLoading = false
    @Published private(set) var error: Error?

    private let appState = AppState()

    func loadUsers() async {
        await appState.setLoading(true)

        do {
            let fetchedUsers = try await NetworkManager.shared.fetchUsers(ids: ["1", "2", "3"])

            for user in fetchedUsers {
                await appState.addUser(user)
            }

            let state = await appState.getState()
            updateUI(with: state)

        } catch {
            await appState.setError(error)
            let state = await appState.getState()
            updateUI(with: state)
        }
    }

    private func updateUI(with state: (users: [User], isLoading: Bool, error: Error?)) {
        users = state.users
        isLoading = state.isLoading
        error = state.error
    }
}
```

### 3. Property wrapper для валидации

```swift
@propertyWrapper
struct Validated<Value> {
    private var value: Value
    private let validator: (Value) -> Bool

    init(wrappedValue: Value, validator: @escaping (Value) -> Bool) {
        self.validator = validator
        self.value = wrappedValue

        if !validator(wrappedValue) {
            assertionFailure("Invalid initial value")
        }
    }

    var wrappedValue: Value {
        get { value }
        set {
            if validator(newValue) {
                value = newValue
            } else {
                assertionFailure("Invalid value")
            }
        }
    }
}

struct User {
    @Validated(validator: { $0.count >= 2 })
    var name: String

    @Validated(validator: { $0 >= 0 && $0 <= 150 })
    var age: Int
}

// Использование
var user = User(name: "Alice", age: 25)
user.age = 160  // Assertion failure
user.name = "A"  // Assertion failure
```

## Заключение

Современные возможности Swift значительно улучшают безопасность, читаемость и производительность кода:

### Async/await обеспечивает:
- **Структурированную многозадачность** с правильной отменой задач
- **Безопасность типов** для асинхронного кода
- **Лучшую читаемость** по сравнению с callback hell

### Actors обеспечивают:
- **Потокобезопасность** без ручной синхронизации
- **Изоляцию данных** для предотвращения race conditions
- **Простоту использования** по сравнению с DispatchQueue

### Property wrappers позволяют:
- **Инкапсулировать логику** в переиспользуемые компоненты
- **Расширять поведение свойств** без изменения типа
- **Создавать декларативный код** (@Published, @State, etc.)

### Рекомендации по использованию:
1. **Используйте async/await** для нового асинхронного кода
2. **Применяйте actors** для изменяемого состояния в многопоточном коде
3. **Создавайте property wrappers** для повторяющейся логики валидации и трансформации
4. **Изучайте result builders** для создания DSL-подобного синтаксиса

Помните: "Современный Swift - это не только новые возможности, но и новый способ мышления о коде."
