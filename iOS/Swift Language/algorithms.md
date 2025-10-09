---
title: Algorithms & Complexity
type: thread
topics: [Swift Language]
subtopic: algorithms
status: draft
level: intermediate
platforms: [iOS]
ios_min: "10.0"
duration: 90m
tags: [algorithms, complexity, big-o, data-structures, interview]
---

# Algorithms & Complexity

## Контекст
Алгоритмы и структуры данных, оценка сложности, сортировки.

## Big O Notation — Основы

**Big O** описывает верхнюю границу роста времени выполнения или потребления памяти алгоритма при увеличении размера входных данных.

### Основные классы сложности (от лучшей к худшей)

| Нотация | Название | Пример |
|---------|----------|--------|
| O(1) | Константная | Доступ к элементу массива по индексу |
| O(log n) | Логарифмическая | Бинарный поиск |
| O(n) | Линейная | Перебор всех элементов массива |
| O(n log n) | Линейно-логарифмическая | Merge Sort, Quick Sort (средний случай) |
| O(n²) | Квадратичная | Вложенные циклы, Bubble Sort |
| O(n³) | Кубическая | Тройные вложенные циклы |
| O(2ⁿ) | Экспоненциальная | Рекурсивный Fibonacci |
| O(n!) | Факториальная | Перебор всех перестановок |

### Визуальное сравнение роста

```
n = 10:
O(1)      = 1
O(log n)  = 3
O(n)      = 10
O(n log n)= 30
O(n²)     = 100
O(2ⁿ)     = 1024
O(n!)     = 3,628,800

n = 100:
O(1)      = 1
O(log n)  = 7
O(n)      = 100
O(n log n)= 700
O(n²)     = 10,000
O(2ⁿ)     = 1.27 × 10³⁰ (невычислимо)
```

## Сложность операций для Swift коллекций

### Array

| Операция | Средний случай | Худший случай | Примечание |
|----------|---------------|---------------|------------|
| `array[i]` | O(1) | O(1) | Прямой доступ по индексу |
| `array.first` | O(1) | O(1) | Доступ к первому элементу |
| `array.last` | O(1) | O(1) | Доступ к последнему элементу |
| `array.append(_)` | O(1) | O(n) | Амортизированная O(1), может вызвать reallocation |
| `array.insert(_, at: 0)` | O(n) | O(n) | Нужно сдвинуть все элементы |
| `array.remove(at: i)` | O(n) | O(n) | Нужно сдвинуть элементы после удаления |
| `array.contains(_)` | O(n) | O(n) | Линейный поиск |
| `array.sort()` | O(n log n) | O(n log n) | Introsort (hybrid) |

### Set

| Операция | Средний случай | Худший случай | Примечание |
|----------|---------------|---------------|------------|
| `set.insert(_)` | O(1) | O(n) | Хеш-таблица |
| `set.remove(_)` | O(1) | O(n) | Хеш-таблица |
| `set.contains(_)` | O(1) | O(n) | Хеш-таблица |
| `set.union(_)` | O(n+m) | O(n+m) | n и m — размеры множеств |
| `set.intersection(_)` | O(min(n,m)) | O(n×m) | |

### Dictionary

| Операция | Средний случай | Худший случай | Примечание |
|----------|---------------|---------------|------------|
| `dict[key]` | O(1) | O(n) | Хеш-таблица |
| `dict[key] = value` | O(1) | O(n) | Хеш-таблица |
| `dict.removeValue(forKey:)` | O(1) | O(n) | Хеш-таблица |
| `dict.keys` | O(1) | O(1) | Ленивая коллекция |
| `dict.values` | O(1) | O(1) | Ленивая коллекция |

### String

| Операция | Сложность | Примечание |
|----------|-----------|------------|
| `string.count` | O(n) | ⚠️ Не O(1)! Нужно пройти все символы |
| `string[index]` | O(1) | Доступ по String.Index |
| `string.append(_)` | O(m) | m — длина добавляемой строки |
| `string.contains(_)` | O(n×m) | Поиск подстроки |
| `string.split(separator:)` | O(n) | |

## Алгоритмы сортировки

### Сравнительная таблица

| Алгоритм | Лучший случай | Средний случай | Худший случай | Память | Стабильность |
|----------|--------------|----------------|---------------|---------|--------------|
| **Bubble Sort** | O(n) | O(n²) | O(n²) | O(1) | Да |
| **Selection Sort** | O(n²) | O(n²) | O(n²) | O(1) | Нет |
| **Insertion Sort** | O(n) | O(n²) | O(n²) | O(1) | Да |
| **Merge Sort** | O(n log n) | O(n log n) | O(n log n) | O(n) | Да |
| **Quick Sort** | O(n log n) | O(n log n) | O(n²) | O(log n) | Нет |
| **Heap Sort** | O(n log n) | O(n log n) | O(n log n) | O(1) | Нет |
| **Tim Sort** | O(n) | O(n log n) | O(n log n) | O(n) | Да |

**Swift использует Introsort** (гибрид Quick Sort, Heap Sort и Insertion Sort) для `sort()` и `sorted()`.

### Когда использовать

- **Insertion Sort** — для почти отсортированных массивов или малых размеров (< 10-20 элементов)
- **Quick Sort** — общий случай, хорошая производительность на практике
- **Merge Sort** — когда нужна стабильная сортировка или работа с linked lists
- **Heap Sort** — когда критична память (in-place) и нужна гарантированная O(n log n)

## Алгоритмы поиска

| Алгоритм | Сложность | Требования | Применение |
|----------|-----------|------------|------------|
| **Linear Search** | O(n) | Нет | Неупорядоченный массив |
| **Binary Search** | O(log n) | Отсортированный массив | `array.binarySearch(_)` |
| **Hash Table** | O(1) средний | Хеш-функция | `Set`, `Dictionary` |
| **DFS** | O(V+E) | Граф | Поиск в глубину |
| **BFS** | O(V+E) | Граф | Поиск в ширину |

## Структуры данных

### Сравнительная таблица операций

| Структура | Доступ | Поиск | Вставка | Удаление | Память |
|-----------|--------|-------|---------|----------|---------|
| **Array** | O(1) | O(n) | O(n) | O(n) | O(n) |
| **Linked List** | O(n) | O(n) | O(1)* | O(1)* | O(n) |
| **Stack** | O(n) | O(n) | O(1) | O(1) | O(n) |
| **Queue** | O(n) | O(n) | O(1) | O(1) | O(n) |
| **Hash Table** | - | O(1) | O(1) | O(1) | O(n) |
| **Binary Tree** | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| **Heap** | O(1) min/max | O(n) | O(log n) | O(log n) | O(n) |

*при наличии указателя на нужную позицию

### Когда использовать

- **Array** — индексный доступ, известный размер, редкие вставки/удаления
- **Set** — уникальные значения, быстрый поиск O(1)
- **Dictionary** — key-value хранение, быстрый доступ по ключу O(1)
- **Linked List** — частые вставки/удаления в начале/середине
- **Stack** — LIFO (Last In First Out), backtracking, undo/redo
- **Queue** — FIFO (First In First Out), BFS, task scheduling
- **Heap** — priority queue, k-largest elements

## Примеры кода в Swift

### Binary Search

```swift
extension Array where Element: Comparable {
    func binarySearch(_ target: Element) -> Int? {
        var left = 0
        var right = count - 1
        
        while left <= right {
            let mid = (left + right) / 2
            
            if self[mid] == target {
                return mid
            } else if self[mid] < target {
                left = mid + 1
            } else {
                right = mid - 1
            }
        }
        
        return nil
    }
}

// Сложность: O(log n)
let numbers = [1, 3, 5, 7, 9, 11, 13]
numbers.binarySearch(7) // 3
```

### Quick Sort

```swift
func quickSort<T: Comparable>(_ array: [T]) -> [T] {
    guard array.count > 1 else { return array }
    
    let pivot = array[array.count / 2]
    let less = array.filter { $0 < pivot }
    let equal = array.filter { $0 == pivot }
    let greater = array.filter { $0 > pivot }
    
    return quickSort(less) + equal + quickSort(greater)
}

// Сложность: O(n log n) средний, O(n²) худший
let unsorted = [3, 7, 8, 5, 2, 1, 9, 5, 4]
quickSort(unsorted) // [1, 2, 3, 4, 5, 5, 7, 8, 9]
```

### Merge Sort

```swift
func mergeSort<T: Comparable>(_ array: [T]) -> [T] {
    guard array.count > 1 else { return array }
    
    let mid = array.count / 2
    let left = mergeSort(Array(array[..<mid]))
    let right = mergeSort(Array(array[mid...]))
    
    return merge(left, right)
}

func merge<T: Comparable>(_ left: [T], _ right: [T]) -> [T] {
    var result: [T] = []
    var i = 0, j = 0
    
    while i < left.count && j < right.count {
        if left[i] < right[j] {
            result.append(left[i])
            i += 1
        } else {
            result.append(right[j])
            j += 1
        }
    }
    
    result.append(contentsOf: left[i...])
    result.append(contentsOf: right[j...])
    
    return result
}

// Сложность: O(n log n) всегда
```

## Часто задаваемые задачи на собеседованиях

### 1. Two Sum (найти пару чисел с заданной суммой)

```swift
func twoSum(_ nums: [Int], _ target: Int) -> [Int]? {
    var dict: [Int: Int] = [:]
    
    for (i, num) in nums.enumerated() {
        let complement = target - num
        if let index = dict[complement] {
            return [index, i]
        }
        dict[num] = i
    }
    
    return nil
}

// Сложность: O(n) время, O(n) память
twoSum([2, 7, 11, 15], 9) // [0, 1]
```

### 2. Reverse Linked List

```swift
class ListNode {
    var val: Int
    var next: ListNode?
    init(_ val: Int) {
        self.val = val
    }
}

func reverseList(_ head: ListNode?) -> ListNode? {
    var prev: ListNode? = nil
    var current = head
    
    while current != nil {
        let next = current?.next
        current?.next = prev
        prev = current
        current = next
    }
    
    return prev
}

// Сложность: O(n) время, O(1) память
```

### 3. Validate Parentheses

```swift
func isValid(_ s: String) -> Bool {
    var stack: [Character] = []
    let pairs: [Character: Character] = [")": "(", "}": "{", "]": "["]
    
    for char in s {
        if pairs.values.contains(char) {
            stack.append(char)
        } else if let last = stack.last, pairs[char] == last {
            stack.removeLast()
        } else {
            return false
        }
    }
    
    return stack.isEmpty
}

// Сложность: O(n) время, O(n) память
isValid("()[]{}") // true
isValid("([)]") // false
```

## Советы для собеседований

### 1. Анализ сложности
- Всегда указывайте временную и пространственную сложность
- Объясняйте, почему именно такая сложность
- Упоминайте лучший, средний и худший случаи

### 2. Оптимизация
- Начните с brute-force решения O(n²) или O(n³)
- Затем оптимизируйте до O(n log n) или O(n)
- Используйте хеш-таблицы для O(1) lookup
- Рассмотрите two-pointer технику

### 3. Типичные паттерны
- **Sliding Window** — подмассивы, подстроки
- **Two Pointers** — отсортированные массивы, палиндромы
- **Hash Map** — подсчет, группировка
- **Stack** — вложенность, backtracking
- **Queue** — level-order traversal
- **Binary Search** — отсортированные данные

### 4. Trade-offs
- Время vs память
- Простота vs производительность
- Стабильность vs скорость (для сортировки)

## Полезные ресурсы

- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)
- [LeetCode](https://leetcode.com/) — практика алгоритмов
- [Swift Algorithm Club](https://github.com/raywenderlich/swift-algorithm-club)

## Вопросы собеседований

### Теория
- Какие есть виды сортировок массива?
- Объясните разницу между O(n) и O(n²)
- Что такое амортизированная сложность?
- Почему `string.count` в Swift имеет сложность O(n)?
- Какая сложность у `array.append(_)` и почему?

### Практика
- Найти k-й наибольший элемент в массиве
- Проверить, является ли строка палиндромом
- Развернуть связанный список
- Найти цикл в связанном списке
- Реализовать LRU Cache

### Дополнительные
- Какое максимальное значение для 32 битного int? (2³¹ - 1 = 2,147,483,647)
- На C/C++ что-нибудь писал?

## См. также
- [[iOS/Swift Language/Swift Language]] — Язык Swift
- [[iOS/Swift Language/best-practices]] — Лучшие практики
- [[functional-programming]] — Функциональное программирование


