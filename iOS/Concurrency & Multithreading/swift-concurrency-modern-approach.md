---
type: "thread"
status: "draft"
summary: ""
title: "Swift Concurrency (современный подход)"
---

# Swift Concurrency (современный подход)

## Ключевые идеи
- **Structured concurrency**: `async let`, `withTaskGroup` — дочерние задачи привязаны к жизненному циклу родителя (ожидание/отмена каскадно).
- **Unstructured concurrency**: `Task {}` / `Task.detached` — живут отдельно; ответственность за отмену/менеджмент на разработчике.
- **Actors**: изоляция состояния (serial execution); `@MainActor` — UI‑актор; учитывать **reentrancy** (на `await` актор может обрабатывать другие сообщения).
- **Cancellation**: кооперативная — проверяйте `Task.isCancelled` / `Task.checkCancellation()`, используйте `withTaskCancellationHandler`.
- **Sendable**: типы, которые безопасно передавать между исполнителями. Значимые типы обычно `Sendable` из коробки; классы — нет (если только `final` + поля `Sendable`).
- **Global actors**: аннотации областей кода одним актором, напр. `@MainActor`, собственные глобальные акторы.
- **AsyncSequence/AsyncStream**: асинхронные последовательности, буферизация и завершение, мосты к Combine/notifications.
- **Continuations**: мост от callback/делегатов к async/await через `withChecked(Throwing)Continuation`.
- **Task-Local values**: контекстные значения, наследуемые дочерними задачами (трассировка, локаль, авторизация).

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

#### Наследование контекста и когда `detached`
- `Task {}` наследует приоритет, локальные значения задачи, акторный контекст (если вызван внутри исполнителя актора).
- `Task.detached {}` запускает задачу вне контекста: приоритет, cancellation, актор — не наследуются. Используйте редко: для низкоприоритетных/системных задач, аналитики, изолированных вычислений.

```swift
// Запуск в контексте текущего актора (например, @MainActor)
Task { @MainActor in
    updateUI()
}

// Выполнить тяжёлую работу вне UI-актора и вернуться назад
Task { @MainActor in
    let result = await Task.detached(priority: .utility) { heavyCompute() }.value
    updateUI(with: result)
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

##### Ограничение конкуренции (скользящее окно)
```swift
func fetchMany(ids: [Int], limit: Int = 4) async throws -> [Int: Data] {
    try await withThrowingTaskGroup(of: (Int, Data).self) { group in
        var next = 0
        var output: [Int: Data] = [:]

        for _ in 0..<min(limit, ids.count) {
            let id = ids[next]; next += 1
            group.addTask { (id, try await fetch(id)) }
        }

        while let (id, data) = try await group.next() {
            output[id] = data
            if next < ids.count {
                let id = ids[next]; next += 1
                group.addTaskUnlessCancelled { (id, try await fetch(id)) }
            }
        }
        return output
    }
}
```

##### Гонки: «операция против таймаута»
```swift
func fetchWithTimeout<T>(timeout: Duration, operation: @escaping () async throws -> T) async throws -> T {
    try await withThrowingTaskGroup(of: T.self) { group in
        group.addTask { try await operation() }
        group.addTask {
            try await Task.sleep(for: timeout)
            throw URLError(.timedOut)
        }
        defer { group.cancelAll() }
        return try await group.next()!
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

##### Сохранение порядка результатов
```swift
func inOrder<T>(_ inputs: [Int], work: @escaping (Int) async throws -> T) async throws -> [T] {
    try await withThrowingTaskGroup(of: (Int, T).self) { group in
        for id in inputs { group.addTask { (id, try await work(id)) } }
        var tmp: [Int: T] = [:]
        for try await (id, value) in group { tmp[id] = value }
        return inputs.compactMap { tmp[$0] }
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

#### Reentrancy и инварианты
- Актор может временно отпустить эксклюзивный доступ на `await`, обработав другие сообщения. Держите инварианты в корректном состоянии ДО `await`.
- Минимизируйте окно между изменением состояния и `await`; при необходимости копируйте локальные снимки.

```swift
actor Cart {
    private var items: [Item] = []

    func add(_ item: Item) async throws {
        items.append(item)              // состояние консистентно
        let price = try await fetchPrice(item) // здесь возможна реэнтерабельность
        items[items.count-1].price = price
    }
}
```

#### Global actors
```swift
@globalActor
struct DatabaseActor {
    static let shared = DatabaseExecutor()
}

actor DatabaseExecutor {}

@DatabaseActor
final class Repository {
    func query() async -> [Row] { /* ... */ }
}
```

#### Sendable и изоляция данных
- Отмечайте типы, пересекающие границы исполнителей, `Sendable`.
- Избегайте незащищённых ссылок на классы между акторами.

```swift
struct Config: Sendable {
    let apiBase: String
    let timeout: Duration
}

final class NotSendableRef { var value = 0 }

// Нельзя передавать между акторами без синхронизации:
// NotSendableRef не соответствует Sendable
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

#### Делегаты → async/await (checked continuations)
```swift
final class LocationDelegate: NSObject, CLLocationManagerDelegate {
    private var continuation: CheckedContinuation<CLLocation, Error>?

    func request() async throws -> CLLocation {
        try await withCheckedThrowingContinuation { cont in
            continuation = cont
            manager.requestLocation()
        }
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        if let loc = locations.first { continuation?.resume(returning: loc) }
        continuation = nil
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        continuation?.resume(throwing: error)
        continuation = nil
    }
}
```

Советы:
- Используйте `withChecked*` для верификации единственного `resume`.
- Избегайте долгого удержания continuation; завершая — зануляйте ссылки.

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

#### Буферизация, backpressure и завершение
- `AsyncStream` и `AsyncThrowingStream` поддерживают буфер `.bufferingPolicy` (например, `.bufferingOldest(50)`).
- Производитель должен корректно вызывать `finish()`/`finish(throwing:)` для закрытия потребителя.

```swift
let stream = AsyncStream<Int>(bufferingPolicy: .bufferingOldest(100)) { cont in
    producer.onEvent { value in cont.yield(value) }
    producer.onComplete { cont.finish() }
}

for await v in stream { /* потребление с естественным backpressure */ }
```

#### Мост к Combine
```swift
extension Publisher where Failure == Never {
    func values() -> AsyncStream<Output> {
        AsyncStream { cont in
            let c = self.sink { _ in } receiveValue: { cont.yield($0) }
            cont.onTermination = { _ in c.cancel() }
        }
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

#### withTaskCancellationHandler
```swift
func download() async {
    await withTaskCancellationHandler(operation: {
        // Основная операция
        await startDownload()
    }, onCancel: {
        // Быстрый и безопасный cleanup
        cancelNetwork()
    })
}
```

#### Cooperative cancellation patterns
- Проверяйте `Task.isCancelled` в циклах и между блоками работы.
- Используйте `try Task.checkCancellation()` чтобы прервать выполнение через бросок `CancellationError` и корректно пройти `defer`.
- Делегируйте отмену в нижележащие API (URLSession, AsyncSequence), которые поддерживают кооперативность.

```swift
func indexing() async throws {
    for batch in batches {
        try Task.checkCancellation()
        try await index(batch)
    }
}
```

## Best Practices
- Предпочитайте `Task {}` вместо `Task.detached {}`.
- Обновления UI — `@MainActor` или `await MainActor.run {}`.
- В долгих операциях проверяйте отмену (`Task.isCancelled` / `Task.checkCancellation()`).
- Изолируйте общий изменяемый стейт в `actor`.
- Объявляйте кросс-поточные типы как `Sendable`.

### Task-Local values
```swift
@TaskLocal static var traceID: String?

func handleRequest(id: String) async {
    await Task.$traceID.withValue(id) {
        await serviceA()
        await serviceB()
    }
}

func log(_ message: String) {
    if let id = Task.traceID { print("[trace:\(id)] \(message)") }
    else { print(message) }
}
```

Использование: прокидывайте контекст (трассировка, локализация, флаги A/B) в дочерние задачи без глобального состояния. Доступ к значению — через `Task.traceID`.

## Частые ошибки
- Блокировка исполнителя тяжёлой работой → вынесите на фоновый исполнитель.
- Двойной `resume` в continuation → используйте `withChecked*` и строго один вызов.
- Потеря контекста при `Task.detached` → пропадает наследование приоритета/отмены.
- Нарушение изоляции актора через `nonisolated` доступ к состоянию.

## SwiftUI и XCTest

### SwiftUI
- `.task` для запуска асинхронной работы при появлении View.
- `.refreshable` для pull-to-refresh (автоматически оборачивает в Task и отменяет при уходе).

```swift
struct FeedView: View {
    @StateObject var vm: VM

    var body: some View {
        List(vm.items) { item in Row(item) }
        .task { await vm.load() }
        .refreshable { await vm.refresh() }
    }
}
```

### XCTest
```swift
final class APITests: XCTestCase {
    func testFetch() async throws {
        let data = try await api.fetch()
        XCTAssertFalse(data.isEmpty)
    }
}
```

## Миграция к строгой конкурентности (Swift 6 режим)
- Включите строгую конкурентность в настройках проекта и поэтапно исправляйте предупреждения.
- Пометьте кросс-исполнительные типы как `Sendable` или устраняйте расшаренное изменяемое состояние.
- Аннотируйте UI‑объекты `@MainActor`.
- Явно указывайте `nonisolated` для чистых методов акторов без доступа к состоянию.
- Проверяйте reentrancy-инварианты, переносите долгие операции за пределы акторов.


## Справочник API (коротко: зачем и как)

### withTaskGroup / withThrowingTaskGroup
- Создаёт структурированную группу задач. Дочерние задачи отменяются при отмене родителя.
- Используйте для динамического числа подпроцессов.
```swift
try await withThrowingTaskGroup(of: Output.self) { group in
    group.addTask { try await work() }
    for try await value in group { consume(value) }
}
```

### addTask / addTaskUnlessCancelled
- `addTask` добавляет подпроцесс в группу.
- `addTaskUnlessCancelled` не добавит задачу, если группа/родитель уже отменены — полезно в «скользящем окне».
```swift
group.addTask { try await fetch(id) }
group.addTaskUnlessCancelled { try await fetch(nextId) }
```

### group.next()
- Асинхронно возвращает следующий готовый результат (в порядке завершения задач), либо `nil`, когда все задачи завершены/отменены.
```swift
while let value = try await group.next() { results.append(value) }
```

### group.cancelAll()
- Отменяет все ещё выполняющиеся дочерние задачи (кооперативно). Используйте после получения первого результата в гонках.
```swift
defer { group.cancelAll() }
```

### async let
- Лёгкий параллелизм фиксированного набора операций в области видимости; отменяется вместе с родителем.
```swift
async let a = a1()
async let b = b1()
let (x, y) = try await (a, b)
```

### Task { } и Task.detached { }
- `Task {}` наследует приоритет/контекст/actor; `detached` — нет. `detached` используйте редко, для полностью изолированных задач.

### Task.sleep
- Приостанавливает задачу; бросает `CancellationError` при отмене (удобно для кооперативной отмены).
```swift
try await Task.sleep(for: .seconds(1))
```

### withTaskCancellationHandler
- Регистрирует быстрый cleanup при отмене.
```swift
await withTaskCancellationHandler(operation: run, onCancel: cancel)
```

### Task.isCancelled / Task.checkCancellation()
- `isCancelled` — опрос флага; `checkCancellation()` — бросает `CancellationError` и выходит через `defer`.

### MainActor.run
- Выполнить небольшой участок на главном акторе, когда вы уже вне `@MainActor`.
```swift
await MainActor.run { render(model) }
```

### @MainActor
- Изоляция UI/моделей представления. Избегайте тяжёлых операций внутри; используйте hop на фоновые исполнители для работы, затем возвращайтесь на `@MainActor`.

### Actor / nonisolated / globalActor
- `actor` изолирует состояние; `nonisolated` — методы без доступа к состоянию (без `await`); `@globalActor` — область кода под одним актором.

### Sendable
- Маркер безопасной передачи между исполнителями. Проверяется компилятором в строгом режиме.

### Continuations
- `withChecked(Throwing)Continuation` — безопасный мост из callback/делегатов, гарантирует один `resume`.

### AsyncStream / AsyncThrowingStream
- Асинхронные последовательности с буфером и завершением; хороши для event‑источников/мостов.

### @TaskLocal
- Контекстные значения, наследуемые дочерними задачами: трейс‑ID, локаль, токены и т.п.

## Исполнители (Executors) и hops
- Исполнитель — это очередь выполнения для конкретного изолированного контекста (например, актор, `@MainActor`).
- «Hop» — переключение на другой исполнитель (потенциально затратная операция). Избегайте лишних hops.

Рекомендации:
- Сгруппируйте UI‑обновления в один `await MainActor.run { ... }` вместо множественных вызовов.
- Не вызывайте тяжёлую работу внутри `@MainActor` — вынесите в detached/фоновый исполнитель, затем вернитесь.
- Используйте `isolated` параметры при передаче акторов в функции, чтобы не делать лишний hop внутри функции.

Пример минимизации hops:
```swift
@MainActor func render(_ vm: VM) { /* ... */ }

func loadAndRender() async {
    let vm = await Task.detached { await loadVM() }.value
    await MainActor.run { render(vm) } // один hop
}
```

## Диагностика и измерение

### Режимы компилятора
- **Strict Concurrency Checking**: включайте постепенно (Minimal → Targeted → Complete) для поэтапного выявления нарушений `Sendable`/изоляции.
- **Swift 6 Concurrency Mode**: даёт максимально строгие проверки и помогает найти проблемные места до продакшена.

### Sanitizers
- **Thread Sanitizer (TSan)**: ловит data‑race на уровне памяти. Полезен и для кода с акторами, если есть обходные пути или небезопасные участки (`nonisolated(unsafe)`, C‑библиотеки).
- **Undefined Behavior Sanitizer (UBSan)**: для низкоуровневых UB, реже помогает в конкурентности, но полезен при FFI.

### Runtime диагностика акторов
- Запустите со флагами окружения для детекции нарушений изоляции актора:
  - `SWIFT_ACTOR_DATA_RACE_CHECKS=2` — строгая проверка обращений к акторному состоянию из неверного исполнителя (в Debug).

### Instruments
- **Swift Concurrency**: визуализирует задачи, группы, зависания, ожидания `await`, отмену. Ищите длинные ожидания и частые hops.
- **Time Profiler**: измеряет CPU‑горячие точки; выявляйте тяжёлую работу на `@MainActor`.
- **Points of Interest**: добавляйте signpost‑метки для бизнес‑событий и коррелируйте с задачами.

### Логирование и метрики
```swift
import os.signpost

let log = OSLog(subsystem: "app", category: "concurrency")
let sp = OSSignposter(log: log)

func work() async {
    let id = sp.beginInterval("loadVM")
    defer { sp.endInterval("loadVM", id: id) }
    _ = await Task.detached { await loadVM() }.value
}
```

### Измерение времени
```swift
let clock = ContinuousClock()
let t0 = clock.now
// ... async work ...
let dt = clock.now - t0
print("elapsed: \(dt.components.seconds)s")
```

### Диагностика лишних hops
- Подозрения: много кратких `await MainActor.run {}` подряд; частые переключения между кастомным актором и `@MainActor`.
- Приёмы:
  - Сгруппируйте несколько UI‑обновлений в одну критическую секцию `MainActor.run`.
  - Перенесите подготовку данных из `@MainActor` в фоновый исполнитель.
  - Используйте `isolated` параметры функций, чтобы выполнять тело уже в нужной изоляции.


## Атрибуты и аннотации конкурентности

### @_unavailableFromAsync
- Делает API недоступным из `async` контекста (в т.ч. при вызове через `await`). Полезно, чтобы запретить синхронные/blocking вызовы в асинхронном коде (например, API, которое блокирует поток или небезопасно при reentrancy).
```swift
@_unavailableFromAsync
func blockingRead() -> Data { /* ... */ }

func use() async {
    // error: 'blockingRead()' is unavailable from asynchronous contexts
    // let d = blockingRead()
}
```

### @preconcurrency
- Ослабляет строгие проверки конкурентности для объявлений, созданных до появления строгой модели (напр., при импорте старых модулей/SDK). Сигнал компилятору: считать API безопасным «как раньше», не требуя `Sendable` и аннотаций изоляции.
```swift
@preconcurrency import LegacyKit
```

### @unchecked Sendable
- Явно помечает тип как `Sendable`, обходя проверку компилятора. Используйте только если вы гарантируете потокобезопасность вручную (например, внутренние immutable‑инварианты или собственные блокировки).
```swift
final class Box: @unchecked Sendable {
    private var lock = OSAllocatedUnfairLock()
    private var value: Int = 0
    func read() -> Int { lock.withLock { value } }
}
```

### nonisolated(unsafe)
- Разрешает доступ к акторному API без `await` и без изоляции. Опасно: вы берёте на себя ответственность за гонки/безопасность. Применять только для действительно «чистых»/константных путей, которые по факту не трогают состояние.
```swift
actor Store {
    private let version = "1.0"
    nonisolated(unsafe) var buildInfo: String { "v:\(version)" } // опасно, если бы version менялся
}
```

### isolated параметры
- Маркируют параметр функции как изолированный актором вызываемой стороны, позволяя вызывать методы без дополнительных hops.
```swift
func mutate(cart: isolated Cart) { // выполняется в изоляции Cart
    cart.addLocalItem()
}
```

### reasync
- Пробрасывает асинхронность: функция сама может не быть `async`, но принимает `async`‑замыкание и становится «ре‑асинхронной» при вызове с таковым.
```swift
func withLock<T>(body: () reasync throws -> T) rethrows -> T { /* lock/unlock */ }
```

### @_inheritActorContext
- Наследует акторный контекст у метода/замыкания, чтобы избежать лишних hops. Обычно не требуется явно; используется внутри стандартной библиотеки.

### @MainActor/@_MainActor
- `@MainActor` — публичная аннотация; `@_MainActor` — underscored вариант (используется в стандартной библиотеке и иногда в SDK).

### @_unsafeInheritExecutor
- Низкоуровневая аннотация для наследования текущего исполнителя (executor) без обычных проверок безопасности. Может сокращать hops, но опасна — использовать только со знанием гарантий. В обычном приложении практически не нужна.

### @Sendable у замыканий
- Помечает замыкание как безопасное для передачи между исполнителями. Для API, которые могут выполнять замыкания на другом исполнителе/потоке, помечайте параметр как `@Sendable`.
```swift
func perform(_ work: @Sendable @escaping () -> Void) { /* ... */ }
```

### MainActor.assumeIsolated
- Выполнить блок, предполагая, что вы уже на `@MainActor`, без проверки/hop. Используйте только если вы гарантируете нахождение на главном акторе (например, вы внутри метода, помеченного `@MainActor`).
```swift
MainActor.assumeIsolated { /* быстрый доступ к UI‑состоянию без hop */ }
```

### @_spi(Concurrency)
- SPI‑аннотация (System Programming Interface): открывает внутренние символы для дружественных модулей. В контексте конкурентности иногда встречается в стандартной библиотеке для внутренних расширений. В прикладном коде избегайте в пользу публичных API.


