---
title: Шпаргалка по структуре объектов Swift и управлению памятью
type: cheat-sheet
topics: [Memory Management, Swift Runtime, Value vs Reference Types]
subtopic: swift-memory-structure
status: draft
level: intermediate
platforms: [iOS, macOS, watchOS, tvOS]
ios_min: "10.0"
duration: 45m
tags: [swift, memory-structure, value-types, reference-types, arc, copy-on-write]
---

# 🧠 Шпаргалка: Структура объектов Swift и память

## Введение

Эта шпаргалка объясняет, как работает память в Swift, различия между структурами и классами, и как добраться до объектов в RAM. Swift имеет свои особенности по сравнению с Objective-C.

## Основные понятия

### Структуры vs Классы (Value vs Reference Types)

#### Структуры (Struct) - Value Types
- **Копируются при присваивании** (копирование по значению)
- **Размещаются на стеке** (если размер позволяет)
- **Не участвуют в подсчете ссылок ARC**
- **Имеют деинициализатор?** Нет, но могут иметь `deinit`, если будут ~Copyable

```swift
struct Point {
    var x, y: Int

    // Структуры могут иметь методы
    func distance(to other: Point) -> Double {
        return sqrt(Double((x - other.x) * (x - other.x) + (y - other.y) * (y - other.y)))
    }
}

// Использование
var point1 = Point(x: 0, y: 0)
var point2 = point1  // ← Копирование по значению!
point2.x = 5         // Не влияет на point1

print(point1.x) // 0
print(point2.x) // 5
```

#### Классы (Class) - Reference Types
- **Передаются по ссылке** (копируется только указатель)
- **Размещаются в куче** почти всегда, если ЖЦ не выходит компилятор может оптимизировать и положить в стек. 
- **Участвуют в ARC** (подсчет сильных ссылок)
- **Имеют деинициализаторы**

```swift
class Person {
    var name: String

    init(name: String) {
        self.name = name
        print("Person \(name) initialized")
    }

    deinit {
        print("Person \(name) deinitialized")
    }
}

// Использование
var person1 = Person(name: "Alice")  // reference count = 1
var person2 = person1                 // reference count = 2
person2.name = "Bob"                  // влияет на person1 тоже!

print(person1.name) // "Bob"
print(person2.name) // "Bob"
```

## Как работает память в Swift

### Размещение в памяти

#### Структуры (Value Types)
```swift
// Маленькие структуры могут размещаться прямо в указателе или на стеке
struct SmallStruct {
    var value: Int
}

// В зависимости от контекста:
var small = SmallStruct(value: 42)
// Может быть размещено:
// 1. Прямо в переменной (inlined)
// 2. На стеке
// 3. В куче (если нужно)

struct LargeStruct {
    var values: [Int] // большой массив
}
// Всегда размещается в куче из-за размера
```

#### Классы (Reference Types)
```swift
// Всегда размещаются в куче
class MyClass {
    var property: Int
}

let obj = MyClass()  // В куче

// Структура объекта в памяти:
// ┌─────────────────────────────────────────┐
// │           Heap Object Header            │
// ├─────────────────────────────────────────┤
// │           Reference Count               │ ← ARC tracking
// ├─────────────────────────────────────────┤
// │           Property 1                    │
// ├─────────────────────────────────────────┤
// │           Property 2                    │
// ├─────────────────────────────────────────┤
// │           ...                           │
// └─────────────────────────────────────────┘
```

### Внутреннее устройство heap-объекта Swift (metadata/isa, refCounts)

Swift-классы — это heap-объекты с «заголовком» из двух машинных слов: указатель на метаданные типа и битово-упакованные счётчики ссылок.

```c
// Упрощённо (по мотивам open-source Swift runtime):
struct HeapObjectHeader {
    uintptr_t metadata;   // Указатель на метаданные класса
    uintptr_t refCounts;  // Сильные/невладельческие счётчики + флаги
};

struct HeapObject {
    struct HeapObjectHeader header;
    // Далее — поля экземпляра (свойства класса)
};
```

- **metadata**: указатель на «class/type metadata». На платформах Apple совместим с `objc isa` — т.е. `object_getClass(_:)` работает и для Swift-классов. На не-ObjC платформах это указатель на чисто Swift-метаданные.
- **refCounts**: битовое поле для ARC:
  - сильные ссылки (strong) и невладельческие (unowned) счётчики,
  - флаги: «объект деинициализируется», «бессмертный объект» и т.п.,
  - при переполнении/сложных сценариях используется внешнее хранилище.

#### Side tables и weak-таблица

- **Weak** ссылки не инкрементируют strong count и регистрируются в глобальной слабой таблице. При деинициализации все weak автоматически обнуляются.
- **Unowned** учитываются в refCounts; после деинициализации доступ к ним вызывает краш (trap), поэтому они безопасны при корректной логике времени жизни.
- При больших значениях счётчиков/особых флагах рантайм может использовать «внешнее» хранилище для части состояния (аналог «side table»).

#### Obj-C interop и «isa»

- Классы Swift совместимы с Obj-C рантаймом на iOS/macOS: первый word в заголовке указывает на класс (metadata), совместимый с `isa`.
- Это позволяет:
  - `object_getClass(obj)`, `type(of: obj)` и динамический диспетчинг через Obj-C рантайм,
  - бриджинг ARC между Swift и Obj-C,
  - метод-резолвинг/кеш у Obj-C-классов-предков (`NSObject`).

#### Практика в LLDB: чтение заголовка объекта

```bash
# Получить адрес объекта (без изменения RC)
(lldb) expr -l Swift -- import Foundation
(lldb) expr -l Swift -- let p = Unmanaged.passUnretained(person).toOpaque()
(lldb) expr -l Swift -- p

# Прочитать два первых machine word: metadata и refCounts
(lldb) memory read -s8 -c2 p

# Посмотреть метаданные класса через Obj-C
(lldb) expr -l Swift -- object_getClass(person)
(lldb) expr -l Swift -- type(of: person)
```

#### Важные замечания

- **Строки и коллекции** в Swift — value types с COW: их «данные» часто живут в куче, но заголовок коллекции — это структура (value), не класс.
- **Small/Inline оптимизации**: некоторые значения (например, «малые строки») могут хранить данные прямо внутри структуры, без выделения в куче.
- **RC наблюдения**: `CFGetRetainCount` может быть неточным для Swift-объектов из-за инлайновых счётчиков и оптимизаций; используйте его только для диагностики.

## ARC в Swift (Automatic Reference Counting)

### Как работает ARC

```swift
class Person {
    var passport: Passport?

    deinit {
        print("Person deinitialized")
    }
}

class Passport {
    var owner: Person?  // Strong reference

    deinit {
        print("Passport deinitialized")
    }
}

// Создание объектов
var person = Person()    // RC = 1
var passport = Passport() // RC = 1

person.passport = passport  // person -> passport (RC = 2)
passport.owner = person     // passport -> person (RC = 2)

// RETAIN CYCLE! Никто не будет удален
```

### Разрыв циклов удержания

```swift
// Решение 1: weak ссылки
class Passport {
    weak var owner: Person?  // Не увеличивает RC
}

// Решение 2: unowned ссылки
class Person {
    var passport: Passport?

    deinit {
        print("Person deinitialized")
    }
}

class Passport {
    unowned var owner: Person  // Не опционально, не увеличивает RC

    deinit {
        print("Passport deinitialized")
    }
}
```

## Copy-on-Write (COW) оптимизация

### Как работает COW

```swift
var array1 = [1, 2, 3, 4, 5]  // Исходный массив
var array2 = array1           // Не копируется, shared buffer

print(array1 === array2)      // false (разные объекты)
print(array1.count)           // 5

// При модификации происходит копирование
array2.append(6)              // Копируется только array2

print(array1)  // [1, 2, 3, 4, 5]
print(array2)  // [1, 2, 3, 4, 5, 6]
```

### Реализация COW вручную

```swift
struct MyArray {
    private var _storage: ArrayStorage

    var count: Int {
        return _storage.count
    }

    private class ArrayStorage {
        var values: [Int]
        var refCount = 1

        init(values: [Int]) {
            self.values = values
        }
    }

    // Copy-on-Write логика
    private mutating func ensureUnique() {
        if _storage.refCount > 1 {
            let values = _storage.values
            _storage = ArrayStorage(values: values)
        }
    }

    mutating func append(_ value: Int) {
        ensureUnique()
        _storage.values.append(value)
    }
}
```

## Как добраться до объектов в RAM

### Исследование структур (Value Types)

```swift
struct Point {
    var x, y: Int
}

var point = Point(x: 10, y: 20)

// В LLDB:
(lldb) frame variable point      // Показать переменную
(lldb) frame variable -L point   // Подробная информация
(lldb) p point                   // Напечатать значение
(lldb) p &point                  // Адрес переменной
```

### Исследование классов (Reference Types)

```swift
class Person {
    var name: String
    init(name: String) { self.name = name }
}

let person = Person(name: "Alice")

// В LLDB:
(lldb) po person                 // Показать объект
(lldb) p person                  // Адрес объекта в куче
(lldb) p &person                 // Адрес указателя на стеке
(lldb) p person.name             // Доступ к свойству
```

### Исследование памяти объектов

```swift
// Структура объекта класса в памяти
class MyClass {
    let id: Int
    var name: String

    init(id: Int, name: String) {
        self.id = id
        self.name = name
    }
}

// В LLDB можно исследовать:
// Heap object header + свойства
(lldb) p *(MyClass *)person      // Разыменовать объект
```

## Важные особенности Swift

### 1. Implicitly Shared (COW) коллекции

```swift
// Array, Dictionary, Set используют COW
var array1 = [1, 2, 3]
var array2 = array1      // Не копируется

array2.append(4)         // Копируется только array2
```

### 2. Value Types в функциях

```swift
func modifyStruct(_ point: Point) {
    var point = point    // Локальная копия
    point.x = 100        // Не влияет на оригинал
}

func modifyClass(_ person: Person) {
    person.name = "Bob"  // Изменяет оригинал
}
```

### 3. @escaping замыкания

```swift
class NetworkManager {
    var handlers: [() -> Void] = []

    func fetchData(completion: @escaping () -> Void) {
        handlers.append(completion)  // Захватывается strongly
        // Без @escaping замыкание не может пережить функцию
    }
}

// Решение для циклов удержания
func fetchData(completion: @escaping () -> Void) {
    handlers.append { [weak self] in
        completion()  // слабая ссылка на self
    } }
```

## Практические примеры LLDB

### Исследование структур

```bash
(lldb) frame variable point
(lldb) p sizeof(Point)           # Размер структуры
(lldb) p &point                  # Адрес на стеке
(lldb) p point.x                 # Доступ к полю
```

### Исследование классов

```bash
(lldb) po person                 # Показать объект
(lldb) p person                  # Адрес в куче
(lldb) p person.name             # Свойство
(lldb) p *(MyClass *)person      # Разыменовать объект
```

### Исследование ARC

```swift
// Создать объекты и посмотреть reference count
(lldb) p person                 # Адрес объекта
(lldb) expr CFGetRetainCount(person)  # Получить RC (unsafe_unretained)
```

## Вопросы для самопроверки

1. **Чем отличаются структуры от классов?** Структуры - value types (копирование), классы - reference types (ссылки)
2. **Где размещаются структуры?** На стеке или в указателе (если маленькие)
3. **Где размещаются классы?** Всегда в куче
4. **Что такое ARC?** Automatic Reference Counting - автоматический подсчет сильных ссылок
5. **Как избежать циклов удержания?** Использовать weak/unowned ссылки
6. **Что такое Copy-on-Write?** Оптимизация, когда копирование происходит только при модификации
7. **Как исследовать память в LLDB?** Через `po`, `p`, `frame variable`

## Полезные команды LLDB для Swift

```bash
# Исследование переменных
(lldb) frame variable -L variableName
(lldb) p variableName
(lldb) p &variableName
(lldb) p sizeof(TypeName)

# Исследование объектов
(lldb) po object
(lldb) p *(ClassName *)object
(lldb) p object.property

# Исследование памяти
(lldb) x/gx 0xADDRESS
(lldb) malloc_history $pid 0xADDRESS
```

## Заключение

Понимание работы памяти в Swift критически важно для:

- **Выбора между структурами и классами** (value vs reference semantics)
- **Оптимизации производительности** (Copy-on-Write, размещение в памяти)
- **Избегания утечек памяти** (правильное использование weak/unowned)
- **Отладки проблем с памятью** (понимание размещения объектов)

**Ключевой принцип Swift:** "Value types для иммутабельности, reference types для разделяемого состояния"

## 📅 Система обновления знаний

### Последнее обновление
- **Дата**: 2024-01-15
- **Версия**: Swift 5.9, iOS 17.2, Xcode 15.2
- **Источники**:
  - [The Swift Programming Language - Memory Safety](https://docs.swift.org/swift-book/LanguageGuide/MemorySafety.html)
  - [WWDC: Understanding Swift Performance](https://developer.apple.com/videos/play/wwdc2016/416/)
  - [Swift Blog: Value and Reference Types](https://swift.org/blog/value-and-reference-types/)

### План следующего обновления
- Добавить примеры с async/await и памятью
- Обновить для новых фич Swift 6
- Добавить больше примеров Copy-on-Write реализаций
