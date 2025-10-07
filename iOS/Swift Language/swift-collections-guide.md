---
title: Коллекции в Swift - детальное руководство
type: guide
topics: [Swift Language, Data Structures, Collections]
subtopic: swift-collections
status: draft
level: intermediate
platforms: [iOS, macOS, watchOS, tvOS]
ios_min: "10.0"
duration: 90m
tags: [swift-collections, array, dictionary, set, performance, algorithms, data-structures]
---

# 📚 Коллекции в Swift - детальное руководство

Комплексное руководство по коллекциям Swift с практическими примерами, анализом производительности и рекомендациями по использованию.

## 📋 Содержание
- [Массивы (Array)](#массивы-array)
- [Словари (Dictionary)](#словари-dictionary)
- [Множества (Set)](#множества-set)
- [Протоколы коллекций](#протоколы-коллекций)
- [Производительность и оптимизации](#производительность-и-оптимизации)
- [Распространенные паттерны](#распространенные-паттерны)

## Массивы (Array)

### Основные операции

```swift
// Создание массивов
let emptyArray: [Int] = []
let numbers = [1, 2, 3, 4, 5]
var mutableArray = [String]()

// Добавление элементов
mutableArray.append("Hello")
mutableArray += ["World"]

// Вставка по индексу
mutableArray.insert("Swift", at: 0)

// Доступ к элементам
let first = numbers[0]  // 1
let last = numbers.last // Optional(5)

// Проверка наличия
numbers.contains(3) // true
numbers.isEmpty     // false
```

### Сложность операций

| Операция | Сложность | Описание |
|----------|-----------|----------|
| Доступ по индексу | O(1) | Прямой доступ |
| Вставка в конец | O(1) | Амортизированная |
| Вставка в начало | O(n) | Сдвиг всех элементов |
| Вставка в середину | O(n) | Сдвиг части элементов |
| Поиск элемента | O(n) | Линейный поиск |

### Примеры использования

```swift
// Фильтрация
let evenNumbers = numbers.filter { $0 % 2 == 0 }

// Маппинг
let doubled = numbers.map { $0 * 2 }

// Редукция
let sum = numbers.reduce(0, +)

// Сортировка
let sorted = numbers.sorted()
let sortedDesc = numbers.sorted(by: >)

// Первый элемент удовлетворяющий условию
let firstEven = numbers.first { $0 % 2 == 0 }

// Разделение массива
let (even, odd) = numbers.partitioned { $0 % 2 == 0 }
```

## Словари (Dictionary)

### Основные операции

```swift
// Создание словарей
let emptyDict: [String: Int] = [:]
let ages = ["Alice": 25, "Bob": 30, "Charlie": 35]
var mutableDict = [Int: String]()

// Добавление/обновление
mutableDict[1] = "One"
mutableDict.updateValue("Two", forKey: 2)

// Получение значений
let aliceAge = ages["Alice"] // Optional(25)
let defaultAge = ages["Unknown", default: 0] // 0

// Проверка наличия ключа
ages.keys.contains("Alice") // true
ages.values.contains(25)    // true

// Удаление
mutableDict.removeValue(forKey: 1)
let removedValue = mutableDict.removeValue(forKey: 2)
```

### Сложность операций

| Операция | Сложность | Описание |
|----------|-----------|----------|
| Доступ по ключу | O(1) среднее | Хэш-функция |
| Вставка | O(1) среднее | Хэш-функция |
| Удаление | O(1) среднее | Хэш-функция |
| Поиск ключа | O(1) среднее | Хэш-функция |

### Примеры использования

```swift
// Группировка по условию
let grouped = Dictionary(grouping: numbers) { $0 % 2 == 0 ? "even" : "odd" }

// Маппинг ключей и значений
let stringDict = ages.mapKeys { "\($0)" }
let doubledDict = ages.mapValues { $0 * 2 }

// Фильтрация
let adultsOnly = ages.filter { $0.value >= 18 }

// Редукция
let totalAge = ages.values.reduce(0, +)

// Проверка всех/любого условия
ages.values.allSatisfy { $0 > 0 } // true
ages.values.contains { $0 > 40 }  // false
```

## Множества (Set)

### Основные операции

```swift
// Создание множеств
let emptySet: Set<Int> = []
let numbersSet: Set = [1, 2, 3, 3, 4] // [1, 2, 3, 4]
var mutableSet = Set<String>()

// Добавление элементов
mutableSet.insert("Apple")
mutableSet.insert("Banana")

// Проверка наличия
numbersSet.contains(3) // true

// Операции с множествами
let setA: Set = [1, 2, 3, 4]
let setB: Set = [3, 4, 5, 6]

let union = setA.union(setB)        // [1, 2, 3, 4, 5, 6]
let intersection = setA.intersection(setB) // [3, 4]
let difference = setA.subtracting(setB)    // [1, 2]
let symmetricDifference = setA.symmetricDifference(setB) // [1, 2, 5, 6]

// Проверка подмножества
setA.isSubset(of: setA.union(setB)) // true
setA.isSuperset(of: setA.intersection(setB)) // true
```

### Сложность операций

| Операция | Сложность | Описание |
|----------|-----------|----------|
| Вставка | O(1) среднее | Хэш-функция |
| Удаление | O(1) среднее | Хэш-функция |
| Поиск | O(1) среднее | Хэш-функция |
| Операции множеств | O(n) | Линейный обход |

## Протоколы коллекций

### Иерархия протоколов

```swift
// Базовые протоколы
protocol Sequence {
    associatedtype Iterator: IteratorProtocol
    func makeIterator() -> Iterator
}

protocol IteratorProtocol {
    associatedtype Element
    mutating func next() -> Element?
}

// Протоколы коллекций
protocol Collection: Sequence {
    associatedtype Index: Comparable
    var startIndex: Index { get }
    var endIndex: Index { get }
    func index(after i: Index) -> Index
    subscript(position: Index) -> Element { get }
}

protocol BidirectionalCollection: Collection {
    func index(before i: Index) -> Index
}

protocol RandomAccessCollection: BidirectionalCollection {
    // Все операции индексации O(1)
}

// Изменяемые протоколы
protocol MutableCollection: Collection {
    subscript(position: Index) -> Element { get set }
}

protocol RangeReplaceableCollection: Collection {
    mutating func replaceSubrange<C: Collection>(_ subrange: Range<Index>, with newElements: C)
}
```

### Протоколы для конкретных типов

```swift
// Array специфические протоколы
extension Array: RandomAccessCollection, MutableCollection, RangeReplaceableCollection {}

// Dictionary специфические протоколы
extension Dictionary: Collection {
    typealias Element = (key: Key, value: Value)
    typealias Index = Dictionary<Key, Value>.Index
}

// Set специфические протоколы
extension Set: Collection {
    typealias Element = Set<Element>.Element
    typealias Index = Set<Element>.Index
}
```

## Производительность и оптимизации

### Copy-on-Write (COW)

**Что такое Copy-on-Write?**
```swift
// До COW - копирование всего массива при каждом присваивании
var array1 = [1, 2, 3, 4, 5]  // Создание массива
var array2 = array1           // Копирование всего массива (O(n))

// С COW - копирование только при модификации
var array3 = [1, 2, 3, 4, 5]  // Создание массива
var array4 = array3           // Общий underlying storage
array4.append(6)              // Копирование только при модификации
```

**Как реализовать COW:**
```swift
class Reference<T> {
    var value: T
    init(_ value: T) {
        self.value = value
    }
}

struct CopyOnWriteArray<Element> {
    private var reference: Reference<[Element]>

    init(_ elements: [Element] = []) {
        reference = Reference(elements)
    }

    private mutating func ensureUnique() {
        if !isKnownUniquelyReferenced(&reference) {
            reference = Reference(reference.value)
        }
    }

    mutating func append(_ element: Element) {
        ensureUnique()
        reference.value.append(element)
    }

    var count: Int {
        return reference.value.count
    }

    subscript(index: Int) -> Element {
        get {
            return reference.value[index]
        }
        set {
            ensureUnique()
            reference.value[index] = newValue
        }
    }
}
```

### Оптимизация операций

```swift
// Предварительное выделение памяти
var optimizedArray = [Int]()
optimizedArray.reserveCapacity(1000) // Предвыделение памяти

// Эффективное создание больших массивов
let largeArray = (0..<100000).map { $0 * 2 } // Лучше чем цикл

// Оптимизация поиска
let largeSet = Set(0..<100000) // O(1) поиск vs O(n) в массиве
let isPresent = largeSet.contains(50000) // O(1) среднее

// Эффективная фильтрация
let filtered = largeArray.lazy.filter { $0 % 2 == 0 }.prefix(10)
```

## Распространенные паттерны

### 1. Аккумулятор с reduce

```swift
// Подсчет статистики
struct Statistics {
    let sum: Int
    let count: Int
    let average: Double
}

let stats = numbers.reduce(into: Statistics(sum: 0, count: 0, average: 0)) { result, number in
    result.sum += number
    result.count += 1
    result.average = Double(result.sum) / Double(result.count)
}

// Группировка с словарем
let groupedByParity = numbers.reduce(into: [String: [Int]]()) { result, number in
    let key = number % 2 == 0 ? "even" : "odd"
    result[key, default: []].append(number)
}
```

### 2. Маппинг с индексами

```swift
// Нумерация элементов
let numbered = numbers.enumerated().map { "\($0.offset + 1): \($0.element)" }

// Преобразование с позиционным контекстом
let windows = (0..<numbers.count).map { index in
    Array(numbers[max(0, index-1)...min(numbers.count-1, index+1)])
}
```

### 3. Фильтрация с состоянием

```swift
// Удаление дубликатов с сохранением порядка
var seen = Set<Int>()
let uniqueOrdered = numbers.filter { seen.insert($0).inserted }

// Поиск первого элемента удовлетворяющего сложному условию
let firstValid = numbers.first { number in
    return number > 10 && number % 2 == 0 && isPrime(number)
}
```

## Практические примеры

### 1. LRU Cache с Dictionary

```swift
class LRUCache<Key: Hashable, Value> {
    private var cache = [Key: Value]()
    private var order = [Key]()
    private let capacity: Int

    init(capacity: Int) {
        self.capacity = capacity
    }

    func get(_ key: Key) -> Value? {
        guard let value = cache[key] else { return nil }

        // Перемещаем ключ в конец (самый свежий)
        order.removeAll { $0 == key }
        order.append(key)

        return value
    }

    func put(_ key: Key, _ value: Value) {
        if cache[key] != nil {
            // Обновляем существующий
            order.removeAll { $0 == key }
        } else if cache.count >= capacity {
            // Удаляем самый старый
            let oldestKey = order.removeFirst()
            cache.removeValue(forKey: oldestKey)
        }

        cache[key] = value
        order.append(key)
    }
}
```

### 2. Группировка данных

```swift
// Группировка пользователей по возрасту
let users = [
    User(name: "Alice", age: 25),
    User(name: "Bob", age: 30),
    User(name: "Charlie", age: 25)
]

let groupedByAge = Dictionary(grouping: users) { $0.age }

// Результат: [25: [Alice, Charlie], 30: [Bob]]

// Более сложная группировка
let groupedByAgeRange = users.reduce(into: [String: [User]]()) { result, user in
    let range = user.age < 30 ? "young" : "old"
    result[range, default: []].append(user)
}
```

### 3. Поиск и фильтрация

```swift
// Поиск всех комбинаций
func findCombinations(_ candidates: [Int], _ target: Int) -> [[Int]] {
    var result = [[Int]]()

    func backtrack(_ combination: [Int], _ start: Int, _ currentSum: Int) {
        if currentSum == target {
            result.append(combination)
            return
        }

        for i in start..<candidates.count {
            if currentSum + candidates[i] > target {
                break // Оптимизация - нет смысла продолжать
            }

            backtrack(combination + [candidates[i]], i, currentSum + candidates[i])
        }
    }

    backtrack([], 0, 0)
    return result
}
```

## Рекомендации по выбору коллекций

### Когда использовать Array
- ✅ Последовательный доступ к элементам
- ✅ Много операций вставки/удаления в конец
- ✅ Нужно сохранять порядок элементов
- ✅ Часто используется с индексами

### Когда использовать Dictionary
- ✅ Частый поиск по ключу
- ✅ Нужно ассоциировать ключи со значениями
- ✅ Размер коллекции относительно небольшой
- ✅ Ключи - hashable типы

### Когда использовать Set
- ✅ Нужно проверять принадлежность элементов
- ✅ Важна уникальность элементов
- ✅ Порядок не важен
- ✅ Математические операции с множествами

## Распространенные ошибки

### 1. Неэффективный поиск в массиве

```swift
// ❌ O(n) поиск
let users = getAllUsers()
let user = users.first { $0.id == userId }

// ✅ O(1) поиск с предварительной индексацией
let userIndex = users.reduce(into: [Int: User]()) { $0[$1.id] = $1 }
let user = userIndex[userId]
```

### 2. Изменение массива во время итерации

```swift
// ❌ Непредсказуемое поведение
for (index, item) in array.enumerated() {
    if shouldRemove(item) {
        array.remove(at: index) // Меняет индексы!
    }
}

// ✅ Правильное решение
var indicesToRemove = [Int]()
for (index, item) in array.enumerated() {
    if shouldRemove(item) {
        indicesToRemove.append(index)
    }
}

for index in indicesToRemove.reversed() {
    array.remove(at: index)
}
```

### 3. Игнорирование Copy-on-Write

```swift
// ❌ Создание ненужных копий
func process(_ array: [Int]) -> [Int] {
    var result = array  // Копирование всего массива
    for i in 0..<result.count {
        result[i] *= 2  // Копирование при первой модификации
    }
    return result
}

// ✅ Эффективное использование
func process(_ array: [Int]) -> [Int] {
    return array.map { $0 * 2 } // Ленивое преобразование
}
```

## Заключение

Коллекции Swift предоставляют мощные инструменты для работы с данными. Правильный выбор коллекции и понимание их характеристик производительности критически важны для создания эффективных приложений.

**Ключевые принципы:**
1. **Выбирайте коллекцию по операции** - Array для последовательного доступа, Dictionary для поиска по ключу, Set для уникальности
2. **Используйте lazy операции** для больших коллекций
3. **Понимайте Copy-on-Write** для оптимизации производительности
4. **Предварительно выделяйте память** для известного размера
5. **Используйте протоколы** для обобщенного кода

Помните: "Выбор правильной коллекции - половина решения задачи."
