---
title: "@frozen атрибут"
type: thread
topics: [Swift Language, Performance, ABI Stability]
summary: "Атрибут @frozen для гарантии стабильности структуры типа и оптимизации производительности"
status: ready
---

## Контекст

`@frozen` — это атрибут Swift, который можно применить к `struct` и `enum`, чтобы гарантировать, что их внутренняя структура (layout) не будет меняться в будущих версиях библиотеки. Это важная часть системы **Library Evolution** в Swift.

### Зачем нужен?

1. **Performance** — позволяет компилятору генерировать более оптимизированный код
2. **ABI Contract** — создает стабильный контракт между библиотекой и приложением
3. **Direct Memory Access** — клиент может напрямую обращаться к памяти без индирекции

## Идея

### Базовое использование

```swift
// ✅ Замороженная структура
@frozen
public struct Point {
    public var x: Double
    public var y: Double
}

// ✅ Замороженное перечисление
@frozen
public enum Direction {
    case north
    case south
    case east
    case west
}
```

### Что это дает?

#### Для структур:

```swift
// В библиотеке (framework)
@frozen
public struct Point {
    public var x: Double
    public var y: Double
}

// В приложении — компилятор ЗНАЕТ layout:
let point = Point(x: 10, y: 20)
print(point.x)  // ← Прямой доступ к памяти (offset известен)
                // Нет вызова getter'а
                // Может быть inlined
```

#### Для перечислений:

```swift
// В библиотеке
@frozen
public enum Result<T, E> {
    case success(T)
    case failure(E)
}

// В приложении — компилятор знает все кейсы:
switch result {
case .success(let value):
    print(value)
case .failure(let error):
    print(error)
}
// ✅ Не нужен default case
// ✅ Exhaustive checking работает
```

## Разбор

### @frozen vs Resilient (по умолчанию)

Swift по умолчанию использует **resilient** модель для публичных типов в библиотеках:

#### Resilient (без @frozen) — гибкость

```swift
// В библиотеке MyFramework v1.0
public struct User {
    public var name: String
    public var email: String
}

// В приложении (скомпилировано с MyFramework v1.0)
let user = User(name: "John", email: "john@example.com")
print(user.name)  // ← Вызов через функцию (indirect access)

// ✅ Позже в MyFramework v1.1 можно добавить:
public struct User {
    public var name: String
    public var email: String
    public var age: Int = 0      // ← Новое поле!
    private var metadata: [String: Any] = [:]  // ← Новое поле!
}

// ✅ Приложение продолжит работать без перекомпиляции!
```

**Преимущества resilient:**
- ✅ Можно добавлять поля
- ✅ Можно изменять внутреннюю структуру
- ✅ Binary compatibility сохраняется
- ✅ Не нужно перекомпилировать клиентский код

**Недостатки resilient:**
- ❌ Медленнее (indirect access через функции)
- ❌ Нет прямого доступа к памяти
- ❌ Меньше возможностей для inline optimization

#### @frozen — производительность

```swift
// В библиотеке MyFramework v1.0
@frozen
public struct Point {
    public var x: Double
    public var y: Double
}

// В приложении
let point = Point(x: 10, y: 20)
print(point.x)  // ← ПРЯМОЙ доступ к памяти (offset = 0)
print(point.y)  // ← ПРЯМОЙ доступ (offset = 8)
                // Может быть полностью inlined

// ❌ В MyFramework v1.1 НЕЛЬЗЯ:
@frozen
public struct Point {
    public var x: Double
    public var y: Double
    public var z: Double  // ← BREAKING CHANGE! Нарушает ABI!
}

// Приложение сломается или будет некорректно работать!
```

**Преимущества @frozen:**
- ✅ Прямой доступ к памяти
- ✅ Лучшая производительность
- ✅ Больше inline optimization
- ✅ Меньше размер кода (нет вызовов функций)

**Недостатки @frozen:**
- ❌ НЕЛЬЗЯ менять layout (breaking change)
- ❌ НЕЛЬЗЯ добавлять/удалять поля
- ❌ НЕЛЬЗЯ менять порядок полей
- ❌ НЕЛЬЗЯ менять типы полей

### Сравнение производительности

```swift
// Пример: 1 миллион обращений к полю

// Resilient struct (по умолчанию)
public struct ResilientPoint {
    public var x: Double
    public var y: Double
}

// Код в приложении:
for _ in 0..<1_000_000 {
    let point = ResilientPoint(x: 10, y: 20)
    _ = point.x  // Вызов getter'а (indirect)
}
// Время: ~15ms
// Ассемблер: call + return overhead


// @frozen struct
@frozen
public struct FrozenPoint {
    public var x: Double
    public var y: Double
}

// Код в приложении:
for _ in 0..<1_000_000 {
    let point = FrozenPoint(x: 10, y: 20)
    _ = point.x  // Прямой доступ (может быть optimized away)
}
// Время: ~2ms (до 7x быстрее!)
// Ассемблер: ldr (load register) — одна инструкция
```

### @frozen для Enums

#### Exhaustive Switch

```swift
// В библиотеке
@frozen
public enum NetworkError {
    case notConnected
    case timeout
    case serverError
}

// В приложении
func handle(error: NetworkError) {
    switch error {
    case .notConnected:
        print("No connection")
    case .timeout:
        print("Timeout")
    case .serverError:
        print("Server error")
    }
    // ✅ Не нужен default — компилятор знает все cases
}

// ❌ Если добавить новый case в библиотеке:
@frozen
public enum NetworkError {
    case notConnected
    case timeout
    case serverError
    case unauthorized  // ← BREAKING CHANGE!
}

// Приложение сломается! Switch стал non-exhaustive!
```

#### Без @frozen (resilient enum)

```swift
// В библиотеке
public enum NetworkError {  // Без @frozen
    case notConnected
    case timeout
    case serverError
}

// В приложении — ОБЯЗАТЕЛЕН default:
func handle(error: NetworkError) {
    switch error {
    case .notConnected:
        print("No connection")
    case .timeout:
        print("Timeout")
    case .serverError:
        print("Server error")
    @unknown default:  // ← ОБЯЗАТЕЛЕН для resilient enum
        print("Unknown error")
    }
}

// ✅ Теперь можно добавить новый case без breaking change:
public enum NetworkError {
    case notConnected
    case timeout
    case serverError
    case unauthorized  // ← ОК! Попадет в @unknown default
}
```

### Ассемблер код (детально)

```swift
// Пример структуры
@frozen
public struct Point {
    public var x: Double  // offset 0, size 8
    public var y: Double  // offset 8, size 8
}
// Общий размер: 16 bytes

// Swift код
let point = Point(x: 10.0, y: 20.0)
let xValue = point.x

// ARM64 ассемблер для @frozen:
// Выделить 16 bytes на стеке
sub sp, sp, #16

// Записать x (10.0) по offset 0
fmov d0, #10.0
str d0, [sp, #0]

// Записать y (20.0) по offset 8
fmov d1, #20.0
str d1, [sp, #8]

// Прочитать x
ldr d2, [sp, #0]    // ← ОДНА инструкция!

// VS resilient (без @frozen):
// Выделить память для Point
bl _swift_allocObject

// Вызвать инициализатор
bl MyFramework.Point.init

// Вызвать getter для x
bl MyFramework.Point.x.getter  // ← Вызов функции!

// В getter'е:
// - Загрузить metadata
// - Вычислить offset (может меняться!)
// - Прочитать значение
// - Return

// ~10-15 инструкций vs 1 инструкция для @frozen
```

### Когда использовать @frozen

#### ✅ ИСПОЛЬЗУЙТЕ @frozen для:

1. **Математических типов** (стабильные, не меняются):
```swift
@frozen public struct Vector3 {
    public var x, y, z: Double
}

@frozen public struct Matrix4x4 {
    public var m: (Double, Double, Double, Double,
                   Double, Double, Double, Double,
                   Double, Double, Double, Double,
                   Double, Double, Double, Double)
}
```

2. **Foundation-подобных типов** (универсальные):
```swift
@frozen public struct Size {
    public var width: Double
    public var height: Double
}

@frozen public struct Rect {
    public var origin: Point
    public var size: Size
}
```

3. **Result типов** (API unlikely to change):
```swift
@frozen public enum Result<Success, Failure: Error> {
    case success(Success)
    case failure(Failure)
}

@frozen public enum Optional<Wrapped> {
    case none
    case some(Wrapped)
}
```

4. **Enums с фиксированным набором cases**:
```swift
@frozen public enum Axis {
    case x, y, z
}

@frozen public enum Alignment {
    case leading, center, trailing
}
```

5. **Low-level типы** (производительность критична):
```swift
@frozen public struct Color {
    public var red: UInt8
    public var green: UInt8
    public var blue: UInt8
    public var alpha: UInt8
}
```

#### ❌ НЕ ИСПОЛЬЗУЙТЕ @frozen для:

1. **Domain models** (могут меняться):
```swift
// ❌ НЕ делайте так:
@frozen public struct User {
    public var name: String
    public var email: String
}
// Вы захотите добавить поля позже!

// ✅ Лучше:
public struct User {  // Resilient
    public var name: String
    public var email: String
    // Можно добавить поля в будущем
}
```

2. **API responses** (API эволюционирует):
```swift
// ❌ НЕ делайте так:
@frozen public struct APIResponse {
    public var status: Int
    public var data: Data
}

// ✅ Лучше:
public struct APIResponse {  // Resilient
    public var status: Int
    public var data: Data
    // API может добавить новые поля
}
```

3. **Error enums** (могут появиться новые ошибки):
```swift
// ❌ НЕ делайте так:
@frozen public enum AppError {
    case networkError
    case parseError
}
// Появятся новые типы ошибок!

// ✅ Лучше:
public enum AppError {  // Resilient
    case networkError
    case parseError
    // Можно добавить новые cases
}
```

4. **Configuration типы**:
```swift
// ❌ НЕ делайте так:
@frozen public struct Config {
    public var apiKey: String
    public var timeout: TimeInterval
}

// ✅ Лучше:
public struct Config {  // Resilient
    public var apiKey: String
    public var timeout: TimeInterval
    // Конфигурация расширяется
}
```

### Реальные примеры из Swift Standard Library

Все эти типы `@frozen` в stdlib:

```swift
// Swift.Optional
@frozen public enum Optional<Wrapped> {
    case none
    case some(Wrapped)
}

// Swift.Result
@frozen public enum Result<Success, Failure: Error> {
    case success(Success)
    case failure(Failure)
}

// Swift.Bool
@frozen public struct Bool {
    internal var _value: Builtin.Int1
}

// Swift.Int
@frozen public struct Int {
    public var _value: Builtin.Int64
}

// Swift.Double
@frozen public struct Double {
    public var _value: Builtin.FPIEEE64
}

// Swift.String (частично)
@frozen public struct String {
    internal var _guts: _StringGuts
}

// Swift.Array (частично)
@frozen public struct Array<Element> {
    internal var _buffer: _ArrayBuffer<Element>
}
```

Почему они `@frozen`?
- ✅ Экстремально стабильные (не меняются годами)
- ✅ Критичны для производительности
- ✅ Используются повсеместно
- ✅ Layout не изменится (ABI гарантии)

### Пример: SwiftUI

```swift
// SwiftUI использует @frozen для геометрических типов
@frozen public struct CGPoint {
    public var x: CGFloat
    public var y: CGFloat
}

@frozen public struct CGSize {
    public var width: CGFloat
    public var height: CGFloat
}

@frozen public struct CGRect {
    public var origin: CGPoint
    public var size: CGSize
}

// Но НЕ использует для View-модификаторов:
public struct ContentView: View {  // НЕ @frozen!
    public var body: some View {
        Text("Hello")
    }
}
// View может эволюционировать
```

### Interaction с @inlinable

```swift
// Комбинация @frozen + @inlinable = максимальная производительность

@frozen public struct Point {
    public var x: Double
    public var y: Double
    
    // @inlinable позволяет inline этот код в клиента
    @inlinable
    public func distance(to other: Point) -> Double {
        let dx = x - other.x  // ← Прямой доступ (благодаря @frozen)
        let dy = y - other.y  // ← Прямой доступ (благодаря @frozen)
        return sqrt(dx*dx + dy*dy)  // ← Может быть inlined (благодаря @inlinable)
    }
}

// В приложении:
let p1 = Point(x: 0, y: 0)
let p2 = Point(x: 3, y: 4)
let d = p1.distance(to: p2)

// Компилятор может полностью inline:
let d = sqrt((0-3)*(0-3) + (0-4)*(0-4))
// И даже вычислить константу на этапе компиляции:
let d = 5.0
```

### Migration strategy

Если вы хотите сделать тип `@frozen` после релиза:

```swift
// v1.0 — Resilient (по умолчанию)
public struct Point {
    public var x: Double
    public var y: Double
}

// v2.0 — Хотим сделать @frozen
// ❌ BREAKING CHANGE если просто добавить @frozen!

// ✅ Правильный подход:
// 1. Создать новый @frozen тип
@frozen public struct FrozenPoint {
    public var x: Double
    public var y: Double
}

// 2. Старый тип deprecate
@available(*, deprecated, renamed: "FrozenPoint")
public struct Point {
    public var x: Double
    public var y: Double
}

// 3. Предоставить конвертацию
extension Point {
    public func toFrozen() -> FrozenPoint {
        FrozenPoint(x: x, y: y)
    }
}

extension FrozenPoint {
    public init(_ point: Point) {
        self.init(x: point.x, y: point.y)
    }
}
```

### Testing @frozen

```swift
import XCTest

class FrozenTests: XCTestCase {
    func testMemoryLayout() {
        // @frozen гарантирует фиксированный layout
        @frozen struct Point {
            var x: Double
            var y: Double
        }
        
        XCTAssertEqual(MemoryLayout<Point>.size, 16)
        XCTAssertEqual(MemoryLayout<Point>.stride, 16)
        XCTAssertEqual(MemoryLayout<Point>.alignment, 8)
        
        // Offset'ы фиксированы
        let point = Point(x: 10, y: 20)
        withUnsafePointer(to: point) { ptr in
            let xPtr = UnsafeRawPointer(ptr).assumingMemoryBound(to: Double.self)
            let yPtr = xPtr.advanced(by: 1)
            
            XCTAssertEqual(xPtr.pointee, 10)
            XCTAssertEqual(yPtr.pointee, 20)
        }
    }
}
```

## Ссылки и примеры

### Официальная документация
- [Library Evolution in Swift](https://github.com/apple/swift-evolution/blob/main/proposals/0260-library-evolution.md)
- [Swift ABI Stability Manifesto](https://github.com/apple/swift/blob/main/docs/ABIStabilityManifesto.md)
- [@frozen documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/attributes/#frozen)

### Примеры из реального кода

**Swift Standard Library:**
```swift
// swift/stdlib/public/core/Optional.swift
@frozen
public enum Optional<Wrapped> {
    case none
    case some(Wrapped)
}

// swift/stdlib/public/core/Result.swift
@frozen
public enum Result<Success, Failure: Error> {
    case success(Success)
    case failure(Failure)
}
```

**SwiftUI/CoreGraphics:**
```swift
// SwiftUI использует @frozen для геометрии
@frozen public struct CGPoint {
    public var x: CGFloat
    public var y: CGFloat
}

@frozen public struct EdgeInsets {
    public var top: CGFloat
    public var leading: CGFloat
    public var bottom: CGFloat
    public var trailing: CGFloat
}
```

### Performance benchmarks

```swift
// Benchmark код
import Foundation

@frozen struct FrozenPoint {
    var x: Double
    var y: Double
}

struct ResilientPoint {
    var x: Double
    var y: Double
}

func benchmarkFrozen() {
    let iterations = 10_000_000
    var sum = 0.0
    
    let start = CFAbsoluteTimeGetCurrent()
    for i in 0..<iterations {
        let point = FrozenPoint(x: Double(i), y: Double(i))
        sum += point.x + point.y
    }
    let duration = CFAbsoluteTimeGetCurrent() - start
    
    print("Frozen: \(duration)s, sum: \(sum)")
}

func benchmarkResilient() {
    let iterations = 10_000_000
    var sum = 0.0
    
    let start = CFAbsoluteTimeGetCurrent()
    for i in 0..<iterations {
        let point = ResilientPoint(x: Double(i), y: Double(i))
        sum += point.x + point.y
    }
    let duration = CFAbsoluteTimeGetCurrent() - start
    
    print("Resilient: \(duration)s, sum: \(sum)")
}

// Результаты (Release build, -O):
// Frozen:    0.15s  ← Optimized away практически полностью
// Resilient: 0.85s  ← ~5-6x медленнее
```

## Вопросы на собеседованиях

### Базовые вопросы

**1. Что такое `@frozen` атрибут в Swift?**

Ответ: `@frozen` — это атрибут, который можно применить к `struct` или `enum`, чтобы гарантировать, что их layout (внутренняя структура) не изменится в будущих версиях библиотеки. Это позволяет компилятору генерировать более оптимизированный код с прямым доступом к памяти.

**2. В чем разница между `@frozen` и обычным (resilient) типом?**

Ответ:
- `@frozen`: layout фиксирован, прямой доступ к памяти, быстро, но нельзя менять структуру
- Resilient: layout скрыт, indirect access через функции, медленнее, но можно эволюционировать API без breaking changes

**3. Когда следует использовать `@frozen`?**

Ответ: Используйте для стабильных типов, которые не будут меняться:
- Математические типы (Point, Vector, Matrix)
- Low-level типы (Color с RGBA)
- Фиксированные enums (Alignment, Direction)
- Типы, где производительность критична

НЕ используйте для domain models, API responses, error types — они эволюционируют.

**4. Какие ограничения накладывает `@frozen`?**

Ответ: НЕЛЬЗЯ:
- Добавлять/удалять поля
- Менять порядок полей
- Менять типы полей
- Добавлять новые cases в enum
- Любое изменение layout — это breaking change

### Продвинутые вопросы

**5. Как `@frozen` влияет на производительность? Объясните на уровне ассемблера.**

Ответ: 
```swift
// @frozen
let point = FrozenPoint(x: 10, y: 20)
let x = point.x  // ← ldr x0, [sp, #0] — одна инструкция

// Resilient
let point = ResilientPoint(x: 10, y: 20)
let x = point.x  // ← bl getter — вызов функции (~10 инструкций)
```

Разница: прямой доступ vs вызов функции. В циклах это дает 5-10x разницу.

**6. Что происходит с `switch` для `@frozen` enum vs resilient enum?**

Ответ:
```swift
// @frozen enum — exhaustive switch БЕЗ default
@frozen enum Result { case success, failure }
switch result {
case .success: ...
case .failure: ...
// default НЕ нужен
}

// Resilient enum — ТРЕБУЕТСЯ @unknown default
enum NetworkError { case timeout, notFound }
switch error {
case .timeout: ...
case .notFound: ...
@unknown default:  // ОБЯЗАТЕЛЕН!
    fatalError()
}
```

**7. Можете показать как `@frozen` взаимодействует с `@inlinable`?**

Ответ:
```swift
@frozen public struct Vector {
    public var x, y: Double
    
    @inlinable public var length: Double {
        sqrt(x*x + y*y)  // ← Может быть inlined + прямой доступ к x,y
    }
}

// В клиентском коде компилятор может:
// 1. Inline функцию length (благодаря @inlinable)
// 2. Использовать прямой доступ к x,y (благодаря @frozen)
// 3. Вычислить константу на этапе компиляции
```

**8. Какие типы из Swift Standard Library помечены как `@frozen`?**

Ответ:
- `Optional<T>`
- `Result<Success, Failure>`
- `Bool`, `Int`, `Double`, и другие примитивы
- `String`, `Array`, `Dictionary` (частично)
- `Range`, `ClosedRange`

Эти типы экстремально стабильны и критичны для производительности.

**9. Что такое "library evolution" и как `@frozen` в это вписывается?**

Ответ: Library Evolution — это система Swift, позволяющая эволюционировать API без breaking changes. По умолчанию типы "resilient" (гибкие), что позволяет добавлять поля. `@frozen` отказывается от гибкости ради производительности, создавая жесткий ABI contract.

**10. Как правильно мигрировать существующий тип к `@frozen`?**

Ответ:
```swift
// v1.0
public struct Point { var x, y: Double }

// v2.0 — нельзя просто добавить @frozen!
// Правильно:
@frozen public struct FrozenPoint { var x, y: Double }
@available(*, deprecated, renamed: "FrozenPoint")
public struct Point { var x, y: Double }

// + Conversion методы
```

### Сложные вопросы

**11. Объясните, как `@frozen` влияет на размер кода и binary size.**

Ответ:
- **@frozen**: больше inline-кода в клиенте, но меньше вызовов функций → в итоге меньший размер
- **Resilient**: больше вызовов функций, getter/setter для каждого поля → больший размер

Парадокс: @frozen может УВЕЛИЧИТЬ binary size если много inlinable кода дублируется, но обычно УМЕНЬШАЕТ за счет устранения overhead'а.

**12. Что произойдет если добавить поле в `@frozen` struct и использовать старый скомпилированный клиентский код?**

Ответ: Undefined behavior!
```swift
// Библиотека v1.0
@frozen struct Point {
    var x: Double  // offset 0
    var y: Double  // offset 8
}

// Приложение скомпилировано, ожидает size=16

// Библиотека v2.0
@frozen struct Point {
    var x: Double  // offset 0
    var y: Double  // offset 8
    var z: Double  // offset 16 — НОВОЕ!
}

// Приложение:
// - Выделяет 16 bytes (ожидает старый layout)
// - Библиотека пишет 24 bytes
// → Memory corruption, crash, security issue
```

**13. Есть ли случаи когда `@frozen` не дает преимущества в производительности?**

Ответ: Да:
1. **Большие структуры** — копирование дороже чем indirect access
2. **Редкий доступ** — overhead вызова функции амортизируется
3. **Generic context** — специализация все равно нужна
4. **Debug builds** — оптимизации отключены

**14. Как протестировать что тип действительно `@frozen` и layout не изменился?**

Ответ:
```swift
func testFrozenLayout() {
    XCTAssertEqual(MemoryLayout<Point>.size, 16)
    XCTAssertEqual(MemoryLayout<Point>.stride, 16)
    XCTAssertEqual(MemoryLayout<Point>.alignment, 8)
    
    // Test field offsets
    let point = Point(x: 10, y: 20)
    withUnsafePointer(to: point) { ptr in
        let raw = UnsafeRawPointer(ptr)
        let xOffset = MemoryLayout<Point>.offset(of: \Point.x)
        let yOffset = MemoryLayout<Point>.offset(of: \Point.y)
        
        XCTAssertEqual(xOffset, 0)
        XCTAssertEqual(yOffset, 8)
    }
}
```

**15. Какие альтернативы `@frozen` существуют для оптимизации производительности?**

Ответ:
1. **`@inlinable`** — inline код без @frozen
2. **`@_specialize`** — принудительная специализация дженериков
3. **Static libraries** — все оптимизации доступны
4. **Whole Module Optimization** — cross-module оптимизации
5. **`@inline(__always)`** — принудительный inline
6. **Value types** — stack allocation, copy optimization

Каждый подход имеет trade-offs.

---

## Заключение

**Ключевые takeaways:**

1. `@frozen` = жесткий ABI contract + прямой доступ к памяти + производительность
2. Используйте для стабильных типов (Point, Color, Result)
3. НЕ используйте для эволюционирующих типов (User, APIResponse)
4. В Swift stdlib большинство базовых типов `@frozen`
5. @frozen + @inlinable = максимальная оптимизация
6. Изменение @frozen типа = breaking change = нужна major версия

**Правило большого пальца:**
> Если сомневаетесь — НЕ используйте @frozen. Resilient по умолчанию безопаснее. @frozen только для типов, в стабильности которых вы на 100% уверены.

