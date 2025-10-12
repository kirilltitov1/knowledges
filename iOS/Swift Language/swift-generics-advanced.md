---
type: "guide"
status: "draft"
level: "advanced"
title: "Swift Generics Advanced"
---

# 🔬 Продвинутые дженерики в Swift - полное руководство

Глубокое погружение в механизм дженериков Swift: от базовых концепций до продвинутых техник, включая протоколы, ограничения типов и оптимизации компиляции.

## 📋 Содержание
- [Основы дженериков](#основы-дженериков)
- [Ограничения типов](#ограничения-типов)
- [Протоколы и дженерики](#протоколы-и-дженерики)
- [Связанные типы (Associated Types)](#связанные-типы-associated-types)
- [Стирание типов (Type Erasure)](#стирание-типов-type-erasure)
- [Специализация и оптимизация](#специализация-и-оптимизация)
- [Распространенные паттерны](#распространенные-паттерны)

## Основы дженериков

### Дженерик функции

```swift
// Базовая дженерик функция
func swapValues<T>(_ a: inout T, _ b: inout T) {
    let temporaryA = a
    a = b
    b = temporaryA
}

// Использование
var x = 10
var y = 20
swapValues(&x, &y) // x = 20, y = 10

var str1 = "Hello"
var str2 = "World"
swapValues(&str1, &str2) // str1 = "World", str2 = "Hello"
```

### Дженерик типы

```swift
// Дженерик структура
struct Stack<Element> {
    private var items = [Element]()

    mutating func push(_ item: Element) {
        items.append(item)
    }

    mutating func pop() -> Element? {
        return items.popLast()
    }

    var isEmpty: Bool {
        return items.isEmpty
    }
}

// Использование
var intStack = Stack<Int>()
intStack.push(1)
intStack.push(2)
let top = intStack.pop() // 2

var stringStack = Stack<String>()
stringStack.push("Swift")
stringStack.push("Generics")
```

## Ограничения типов

### Протоколы как ограничения

```swift
// Функция работает только с типами, реализующими Equatable
func findFirst<T: Equatable>(_ array: [T], _ element: T) -> Int? {
    return array.firstIndex(of: element)
}

// Функция работает только с типами, реализующими Comparable
func minElement<T: Comparable>(_ array: [T]) -> T? {
    return array.min()
}

// Множественные ограничения
func merge<T: Sequence, U: Sequence>(_ first: T, _ second: U) -> [Any]
where T.Element: Equatable, U.Element: Hashable {
    // Реализация
}
```

### Классы как ограничения

```swift
// Ограничение классом UIView
func centerView<T: UIView>(_ view: T) {
    // Можно использовать свойства UIView
    view.center = CGPoint(x: 100, y: 100)
}

// Ограничение любым классом
func printReference<T: AnyObject>(_ object: T) {
    print("Object reference: \(ObjectIdentifier(object))")
}
```

## Протоколы и дженерики

### Протоколы с дженериками

```swift
// Протокол для контейнера
protocol Container {
    associatedtype Item
    var count: Int { get }
    mutating func append(_ item: Item)
    subscript(i: Int) -> Item { get }
}

// Реализация протокола
struct StackContainer<T>: Container {
    typealias Item = T

    private var items = [T]()

    var count: Int {
        return items.count
    }

    mutating func append(_ item: T) {
        items.append(item)
    }

    subscript(i: Int) -> T {
        return items[i]
    }
}
```

### Протоколы с Self требованиями

```swift
// Протокол для копируемых объектов
protocol Copyable {
    func copy() -> Self
}

// Реализация
class Document: Copyable {
    var title: String

    init(title: String) {
        self.title = title
    }

    func copy() -> Self {
        return Self(title: self.title + " (Copy)")
    }
}
```

## Связанные типы (Associated Types)

### Базовые associated types

```swift
protocol Queue {
    associatedtype Element

    mutating func enqueue(_ element: Element)
    mutating func dequeue() -> Element?
    var isEmpty: Bool { get }
    var count: Int { get }
}

struct ArrayQueue<T>: Queue {
    typealias Element = T

    private var elements = [T]()

    mutating func enqueue(_ element: T) {
        elements.append(element)
    }

    mutating func dequeue() -> T? {
        return elements.isEmpty ? nil : elements.removeFirst()
    }

    var isEmpty: Bool {
        return elements.isEmpty
    }

    var count: Int {
        return elements.count
    }
}
```

### Ограничения associated types

```swift
// Протокол с ограничением associated type
protocol Sortable {
    associatedtype Element: Comparable

    func sorted() -> [Element]
    func min() -> Element?
    func max() -> Element?
}

// Реализация
extension Array: Sortable where Element: Comparable {
    typealias Element = Element

    func sorted() -> [Element] {
        return self.sorted()
    }

    func min() -> Element? {
        return self.min()
    }

    func max() -> Element? {
        return self.max()
    }
}
```

## Стирание типов (Type Erasure)

### Проблема гетерогенных коллекций

```swift
// ❌ Не компилируется - разные типы
let shapes: [Shape] = [Circle(), Square()]

// ✅ Правильное решение с протоколом
protocol Shape {
    func draw()
    var area: Double { get }
}

struct Circle: Shape {
    let radius: Double

    func draw() {
        print("Drawing circle with radius \(radius)")
    }

    var area: Double {
        return Double.pi * radius * radius
    }
}

struct Square: Shape {
    let side: Double

    func draw() {
        print("Drawing square with side \(side)")
    }

    var area: Double {
        return side * side
    }
}

// ✅ Теперь работает
let shapes: [Shape] = [Circle(radius: 5), Square(side: 3)]
```

### Кастомное стирание типов

```swift
// Протокол для работы с любыми последовательностями
protocol AnySequenceType {
    func makeIterator() -> AnyIterator<Any>
}

// Стирание типа для конкретной последовательности
struct AnySequence<Element>: AnySequenceType {
    private let _makeIterator: () -> AnyIterator<Element>

    init<S: Sequence>(_ sequence: S) where S.Element == Element {
        _makeIterator = {
            var iterator = sequence.makeIterator()
            return AnyIterator {
                return iterator.next()
            }
        }
    }

    func makeIterator() -> AnyIterator<Element> {
        return _makeIterator()
    }
}

// Использование
let numbers = [1, 2, 3, 4, 5]
let anySequence = AnySequence(numbers)

for number in anySequence {
    print(number) // 1, 2, 3, 4, 5
}
```

## Специализация и оптимизация

### Специализация дженериков

**Как работает специализация:**
```swift
// Исходный дженерик код
struct Container<T> {
    var value: T

    func getValue() -> T {
        return value
    }
}

// После специализации для Int
struct Container_Int {
    var value: Int

    func getValue() -> Int {
        return value
    }
}

// После специализации для String
struct Container_String {
    var value: String

    func getValue() -> String {
        return value
    }
}
```

### Встраивание (Inlining)

```swift
// Функция, подходящая для встраивания
@inlinable
func swapValues<T>(_ a: inout T, _ b: inout T) {
    let temp = a
    a = b
    b = temp
}

// Встраивание позволяет:
// 1. Исключить накладные расходы на вызов функции
// 2. Оптимизировать код в контексте вызова
// 3. Улучшить производительность

// Использование
var x = 10
var y = 20
swapValues(&x, &y)
// Компилятор может встроить тело функции прямо в место вызова
```

### Dead Code Elimination

```swift
// Компилятор удаляет неиспользуемые специализации
func genericFunction<T>(_ value: T) -> T {
    return value
}

// Если используется только с Int
let result = genericFunction(42)

// Компилятор:
// 1. Создает специализацию только для Int
// 2. Удаляет обобщенную версию
// 3. Оптимизирует код специализации
```

## Распространенные паттерны

### 1. Builder Pattern с дженериками

```swift
protocol Builder {
    associatedtype Product

    func build() -> Product
}

struct UserBuilder: Builder {
    typealias Product = User

    private var name: String = ""
    private var age: Int = 0

    mutating func setName(_ name: String) -> Self {
        self.name = name
        return self
    }

    mutating func setAge(_ age: Int) -> Self {
        self.age = age
        return self
    }

    func build() -> User {
        return User(name: name, age: age)
    }
}

// Использование
let user = UserBuilder()
    .setName("John")
    .setAge(25)
    .build()
```

### 2. Strategy Pattern с дженериками

```swift
protocol PaymentStrategy {
    associatedtype PaymentMethod

    func processPayment(_ method: PaymentMethod) -> Bool
}

struct CreditCardPayment: PaymentStrategy {
    typealias PaymentMethod = CreditCard

    func processPayment(_ method: CreditCard) -> Bool {
        // Логика оплаты кредитной картой
        return true
    }
}

struct ApplePayPayment: PaymentStrategy {
    typealias PaymentMethod = ApplePayToken

    func processPayment(_ method: ApplePayToken) -> Bool {
        // Логика оплаты через Apple Pay
        return true
    }
}

// Контекст использования
class PaymentProcessor {
    private let strategy: Any

    init<T: PaymentStrategy>(strategy: T) {
        self.strategy = strategy
    }

    func process<T>(_ method: T.PaymentMethod) -> Bool
    where T: PaymentStrategy, T.PaymentMethod == T {
        // Абстрактная обработка платежа
        return true
    }
}
```

### 3. Repository Pattern с дженериками

```swift
protocol Repository {
    associatedtype Entity: Identifiable

    func get(by id: Entity.ID) async throws -> Entity
    func getAll() async throws -> [Entity]
    func save(_ entity: Entity) async throws
    func delete(_ entity: Entity) async throws
}

class UserRepository: Repository {
    typealias Entity = User

    func get(by id: String) async throws -> User {
        // Реализация получения пользователя
        return User(id: id, name: "User")
    }

    func getAll() async throws -> [User] {
        // Реализация получения всех пользователей
        return [User(id: "1", name: "User1")]
    }

    func save(_ entity: User) async throws {
        // Реализация сохранения пользователя
    }

    func delete(_ entity: User) async throws {
        // Реализация удаления пользователя
    }
}
```

## Продвинутые техники

### 1. Conditional Conformance

```swift
// Условная реализация протокола
extension Array: Equatable where Element: Equatable {
    static func == (lhs: [Element], rhs: [Element]) -> Bool {
        return lhs.elementsEqual(rhs)
    }
}

extension Array: Hashable where Element: Hashable {
    func hash(into hasher: inout Hasher) {
        for element in self {
            hasher.combine(element)
        }
    }
}

// Теперь работает
let array1: [Int] = [1, 2, 3]
let array2: [Int] = [1, 2, 3]
let array3: [String] = ["a", "b", "c"]

print(array1 == array2) // true
print(array1.hashValue) // одинаковый хэш
```

### 2. Generic Subscripts

```swift
struct Matrix<T> {
    private var elements: [[T]]
    let rows: Int
    let columns: Int

    init(rows: Int, columns: Int, defaultValue: T) {
        self.rows = rows
        self.columns = columns
        self.elements = Array(repeating: Array(repeating: defaultValue, count: columns), count: rows)
    }

    subscript(row: Int, column: Int) -> T {
        get {
            precondition(row < rows && column < columns, "Index out of bounds")
            return elements[row][column]
        }
        set {
            precondition(row < rows && column < columns, "Index out of bounds")
            elements[row][column] = newValue
        }
    }

    subscript(row: Int) -> [T] {
        get {
            precondition(row < rows, "Index out of bounds")
            return elements[row]
        }
        set {
            precondition(row < rows && newValue.count == columns, "Invalid row size")
            elements[row] = newValue
        }
    }
}

// Использование
var matrix = Matrix(rows: 3, columns: 3, defaultValue: 0)
matrix[0, 0] = 1
matrix[1, 1] = 2
matrix[2, 2] = 3

print(matrix[0, 0]) // 1
print(matrix[1])    // [0, 2, 0]
```

### 3. Recursive Generic Constraints

```swift
// Рекурсивные ограничения (ограничено в Swift)
protocol RecursiveProtocol {
    associatedtype Element
    // associatedtype Next: RecursiveProtocol where Next.Element == Element
}

// Альтернативное решение через промежуточный протокол
protocol ElementProtocol {
    associatedtype Element
}

protocol RecursiveProtocol: ElementProtocol {
    associatedtype Next: ElementProtocol where Next.Element == Element
}
```

## Производительность дженериков

### Измерение производительности

```swift
func benchmark<T>(_ operation: () -> T, iterations: Int = 1000) -> TimeInterval {
    let startTime = DispatchTime.now()

    for _ in 0..<iterations {
        _ = operation()
    }

    let endTime = DispatchTime.now()
    return Double(endTime.uptimeNanoseconds - startTime.uptimeNanoseconds) / 1_000_000_000
}

// Сравнение производительности
let genericTime = benchmark {
    let container = Container<Int>(value: 42)
    return container.getValue()
}

let concreteTime = benchmark {
    let container = IntContainer(value: 42)
    return container.getValue()
}

print("Generic: \(genericTime), Concrete: \(concreteTime)")
```

### Оптимизация дженериков

```swift
// Использование @inlinable для критичных функций
@inlinable
func optimizedGenericFunction<T: Numeric>(_ value: T) -> T {
    return value * 2
}

// Использование конкретных типов для критичных путей
struct OptimizedStack<Element> {
    @inlinable
    mutating func push(_ element: Element) {
        // Критичная функция помечена для встраивания
        elements.append(element)
    }

    private var elements = [Element]()
}

// Избегание дженериков в критичных путях
func fastPath(_ array: [Int]) -> Int {
    return array.reduce(0, +) // Конкретный тип быстрее дженерика
}
```

## Распространенные ошибки

### 1. Неправильное использование дженериков

```swift
// ❌ Слишком обобщенный код
func process<T>(_ value: T) -> T {
    // Логика зависит от конкретного типа
}

// ✅ Более конкретный подход
func processNumbers(_ numbers: [Int]) -> [Int] {
    return numbers.map { $0 * 2 }
}

func processStrings(_ strings: [String]) -> [String] {
    return strings.map { $0.uppercased() }
}
```

### 2. Игнорирование ограничений типов

```swift
// ❌ Дженерик без ограничений
func find<T>(_ array: [T], _ element: T) -> Int? {
    return array.firstIndex(of: element) // Требует Equatable
}

// ✅ Правильное ограничение
func find<T: Equatable>(_ array: [T], _ element: T) -> Int? {
    return array.firstIndex(of: element)
}
```

### 3. Чрезмерное использование associated types

```swift
// ❌ Слишком много associated types
protocol ComplexProtocol {
    associatedtype Input
    associatedtype Output
    associatedtype Error
    associatedtype Progress

    func process(_ input: Input) -> Result<Output, Error>
    func trackProgress() -> Progress
}

// ✅ Более простая альтернатива
protocol SimpleProcessor<Input, Output, Error> {
    func process(_ input: Input) -> Result<Output, Error>
}
```

## Заключение

Продвинутые дженерики в Swift предоставляют мощные инструменты для создания гибкого и типобезопасного кода. Правильное использование дженериков требует:

1. **Понимания ограничений типов** для создания правильных контрактов
2. **Использования протоколов** для абстракции поведения
3. **Применения associated types** для гибких интерфейсов
4. **Стирания типов** для работы с гетерогенными коллекциями
5. **Оптимизации производительности** через специализацию и встраивание

Помните: "Дженерики - это не только типобезопасность, но и способ мышления о коде."
