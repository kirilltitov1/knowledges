---
type: "guide"
status: "draft"
level: "intermediate"
title: "iOS Interview Algorithms"
---

# 🧮 Алгоритмы и структуры данных для собеседований iOS

Сборник алгоритмических задач и решений, часто встречающихся на технических собеседованиях iOS разработчиков.

## 📋 Содержание
- [Массивы и строки](#массивы-и-строки)
- [Связанные списки](#связанные-списки)
- [Деревья и графы](#деревья-и-графы)
- [Динамическое программирование](#динамическое-программирование)
- [Сортировка и поиск](#сортировка-и-поиск)
- [Рекурсия и backtracking](#рекурсия-и-backtracking)

## Массивы и строки

### 1. Two Sum (Две суммы)

**Задача:** Найти два числа в массиве, сумма которых равна target.

```swift
func twoSum(_ nums: [Int], _ target: Int) -> [Int] {
    var dict = [Int: Int]()

    for (index, num) in nums.enumerated() {
        let complement = target - num

        if let complementIndex = dict[complement] {
            return [complementIndex, index]
        }

        dict[num] = index
    }

    return []
}

// Временная сложность: O(n)
// Пространственная сложность: O(n)
```

### 2. Maximum Subarray (Максимальный подмассив)

**Задача:** Найти непрерывный подмассив с максимальной суммой.

```swift
func maxSubArray(_ nums: [Int]) -> Int {
    var maxSum = nums[0]
    var currentSum = nums[0]

    for i in 1..<nums.count {
        currentSum = max(nums[i], currentSum + nums[i])
        maxSum = max(maxSum, currentSum)
    }

    return maxSum
}

// Алгоритм Кадане
// Временная сложность: O(n)
// Пространственная сложность: O(1)
```

### 3. Merge Sorted Array (Слияние отсортированных массивов)

**Задача:** Слить два отсортированных массива в один.

```swift
func merge(_ nums1: inout [Int], _ m: Int, _ nums2: [Int], _ n: Int) {
    var p1 = m - 1
    var p2 = n - 1
    var p = m + n - 1

    while p1 >= 0 && p2 >= 0 {
        if nums1[p1] > nums2[p2] {
            nums1[p] = nums1[p1]
            p1 -= 1
        } else {
            nums1[p] = nums2[p2]
            p2 -= 1
        }
        p -= 1
    }

    while p2 >= 0 {
        nums1[p] = nums2[p2]
        p2 -= 1
        p -= 1
    }
}
```

### 4. Valid Parentheses (Правильные скобки)

**Задача:** Проверить, правильно ли расставлены скобки в строке.

```swift
func isValid(_ s: String) -> Bool {
    var stack = [Character]()
    let pairs: [Character: Character] = [")": "(", "]": "[", "}": "{"]

    for char in s {
        if let opening = pairs[char] {
            // Закрывающая скобка
            if stack.isEmpty || stack.removeLast() != opening {
                return false
            }
        } else {
            // Открывающая скобка
            stack.append(char)
        }
    }

    return stack.isEmpty
}
```

## Связанные списки

### 1. Reverse Linked List (Разворот связанного списка)

```swift
public class ListNode {
    public var val: Int
    public var next: ListNode?

    public init(_ val: Int) {
        self.val = val
        self.next = nil
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
```

### 2. Merge Two Sorted Lists (Слияние двух отсортированных списков)

```swift
func mergeTwoLists(_ l1: ListNode?, _ l2: ListNode?) -> ListNode? {
    let dummy = ListNode(0)
    var current = dummy
    var list1 = l1
    var list2 = l2

    while list1 != nil && list2 != nil {
        if list1!.val < list2!.val {
            current.next = list1
            list1 = list1?.next
        } else {
            current.next = list2
            list2 = list2?.next
        }
        current = current.next!
    }

    current.next = list1 ?? list2

    return dummy.next
}
```

### 3. Detect Cycle in Linked List (Обнаружение цикла)

```swift
func hasCycle(_ head: ListNode?) -> Bool {
    var slow = head
    var fast = head?.next

    while fast != nil && fast?.next != nil {
        if slow === fast {
            return true
        }
        slow = slow?.next
        fast = fast?.next?.next
    }

    return false
}
```

## Деревья и графы

### 1. Maximum Depth of Binary Tree (Максимальная глубина дерева)

```swift
public class TreeNode {
    public var val: Int
    public var left: TreeNode?
    public var right: TreeNode?

    public init(_ val: Int) {
        self.val = val
        self.left = nil
        self.right = nil
    }
}

func maxDepth(_ root: TreeNode?) -> Int {
    guard let root = root else {
        return 0
    }

    let leftDepth = maxDepth(root.left)
    let rightDepth = maxDepth(root.right)

    return max(leftDepth, rightDepth) + 1
}
```

### 2. Binary Tree Level Order Traversal (Обход дерева по уровням)

```swift
func levelOrder(_ root: TreeNode?) -> [[Int]] {
    guard let root = root else {
        return []
    }

    var result = [[Int]]()
    var queue = [TreeNode]()
    queue.append(root)

    while !queue.isEmpty {
        var level = [Int]()
        let levelSize = queue.count

        for _ in 0..<levelSize {
            let node = queue.removeFirst()
            level.append(node.val)

            if let left = node.left {
                queue.append(left)
            }
            if let right = node.right {
                queue.append(right)
            }
        }

        result.append(level)
    }

    return result
}
```

### 3. Number of Islands (Количество островов)

```swift
func numIslands(_ grid: [[Character]]) -> Int {
    var grid = grid
    let rows = grid.count
    let cols = grid[0].count
    var islands = 0

    func dfs(_ i: Int, _ j: Int) {
        if i < 0 || i >= rows || j < 0 || j >= cols || grid[i][j] == "0" {
            return
        }

        grid[i][j] = "0" // Помечаем как посещенный

        // Обходим соседей
        dfs(i - 1, j)
        dfs(i + 1, j)
        dfs(i, j - 1)
        dfs(i, j + 1)
    }

    for i in 0..<rows {
        for j in 0..<cols {
            if grid[i][j] == "1" {
                islands += 1
                dfs(i, j)
            }
        }
    }

    return islands
}
```

## Динамическое программирование

### 1. Fibonacci Number (Число Фибоначчи)

```swift
// Рекурсивное решение с мемоизацией
func fib(_ n: Int) -> Int {
    var memo = [Int: Int]()

    func fibHelper(_ n: Int) -> Int {
        if n <= 1 {
            return n
        }

        if let cached = memo[n] {
            return cached
        }

        let result = fibHelper(n - 1) + fibHelper(n - 2)
        memo[n] = result
        return result
    }

    return fibHelper(n)
}

// Итеративное решение
func fibIterative(_ n: Int) -> Int {
    if n <= 1 {
        return n
    }

    var a = 0
    var b = 1

    for _ in 2...n {
        let temp = a + b
        a = b
        b = temp
    }

    return b
}
```

### 2. Climbing Stairs (Подъем по лестнице)

**Задача:** Количество способов подняться по лестнице с n ступеньками, если за раз можно подняться на 1 или 2 ступеньки.

```swift
func climbStairs(_ n: Int) -> Int {
    if n <= 2 {
        return n
    }

    var dp = [Int](repeating: 0, count: n + 1)
    dp[1] = 1
    dp[2] = 2

    for i in 3...n {
        dp[i] = dp[i - 1] + dp[i - 2]
    }

    return dp[n]
}
```

### 3. Coin Change (Размен монет)

**Задача:** Минимальное количество монет для размена суммы amount.

```swift
func coinChange(_ coins: [Int], _ amount: Int) -> Int {
    var dp = [Int](repeating: amount + 1, count: amount + 1)
    dp[0] = 0

    for i in 1...amount {
        for coin in coins {
            if coin <= i {
                dp[i] = min(dp[i], dp[i - coin] + 1)
            }
        }
    }

    return dp[amount] > amount ? -1 : dp[amount]
}
```

## Сортировка и поиск

### 1. Binary Search (Бинарный поиск)

```swift
func search(_ nums: [Int], _ target: Int) -> Int {
    var left = 0
    var right = nums.count - 1

    while left <= right {
        let mid = left + (right - left) / 2

        if nums[mid] == target {
            return mid
        } else if nums[mid] < target {
            left = mid + 1
        } else {
            right = mid - 1
        }
    }

    return -1
}
```

### 2. Merge Sort (Сортировка слиянием)

```swift
func mergeSort(_ array: [Int]) -> [Int] {
    guard array.count > 1 else {
        return array
    }

    let middle = array.count / 2
    let left = mergeSort(Array(array[0..<middle]))
    let right = mergeSort(Array(array[middle..<array.count]))

    return merge(left, right)
}

private func merge(_ left: [Int], _ right: [Int]) -> [Int] {
    var result = [Int]()
    var leftIndex = 0
    var rightIndex = 0

    while leftIndex < left.count && rightIndex < right.count {
        if left[leftIndex] < right[rightIndex] {
            result.append(left[leftIndex])
            leftIndex += 1
        } else {
            result.append(right[rightIndex])
            rightIndex += 1
        }
    }

    result.append(contentsOf: left[leftIndex..<left.count])
    result.append(contentsOf: right[rightIndex..<right.count])

    return result
}
```

### 3. Quick Sort (Быстрая сортировка)

```swift
func quickSort(_ array: [Int]) -> [Int] {
    guard array.count > 1 else {
        return array
    }

    let pivot = array[array.count / 2]
    let less = array.filter { $0 < pivot }
    let equal = array.filter { $0 == pivot }
    let greater = array.filter { $0 > pivot }

    return quickSort(less) + equal + quickSort(greater)
}
```

## Рекурсия и backtracking

### 1. Generate Parentheses (Генерация скобок)

```swift
func generateParenthesis(_ n: Int) -> [String] {
    var result = [String]()

    func backtrack(_ current: String, _ open: Int, _ close: Int) {
        if current.count == 2 * n {
            result.append(current)
            return
        }

        if open < n {
            backtrack(current + "(", open + 1, close)
        }

        if close < open {
            backtrack(current + ")", open, close + 1)
        }
    }

    backtrack("", 0, 0)
    return result
}
```

### 2. Letter Combinations of a Phone Number (Комбинации букв телефонного номера)

```swift
func letterCombinations(_ digits: String) -> [String] {
    guard !digits.isEmpty else {
        return []
    }

    let digitToLetters: [Character: String] = [
        "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
        "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"
    ]

    var result = [String]()

    func backtrack(_ combination: String, _ nextIndex: Int) {
        if combination.count == digits.count {
            result.append(combination)
            return
        }

        let digit = digits[digits.index(digits.startIndex, offsetBy: nextIndex)]
        let letters = digitToLetters[digit]!

        for letter in letters {
            backtrack(combination + String(letter), nextIndex + 1)
        }
    }

    backtrack("", 0)
    return result
}
```

### 3. Permutations (Перестановки)

```swift
func permute(_ nums: [Int]) -> [[Int]] {
    var result = [[Int]]()
    var nums = nums
    var current = [Int]()

    func backtrack() {
        if current.count == nums.count {
            result.append(current)
            return
        }

        for i in 0..<nums.count {
            if nums[i] != Int.max { // Проверяем, не использовали ли уже
                let temp = nums[i]
                nums[i] = Int.max
                current.append(temp)

                backtrack()

                current.removeLast()
                nums[i] = temp
            }
        }
    }

    backtrack()
    return result
}
```

## Хэш-таблицы и множества

### 1. Valid Anagram (Правильная анаграмма)

```swift
func isAnagram(_ s: String, _ t: String) -> Bool {
    guard s.count == t.count else {
        return false
    }

    var charCount = [Character: Int]()

    // Подсчет символов в первой строке
    for char in s {
        charCount[char, default: 0] += 1
    }

    // Вычитание символов из второй строки
    for char in t {
        guard let count = charCount[char], count > 0 else {
            return false
        }
        charCount[char] = count - 1
    }

    return true
}
```

### 2. Group Anagrams (Группировка анаграмм)

```swift
func groupAnagrams(_ strs: [String]) -> [[String]] {
    var groups = [String: [String]]()

    for str in strs {
        let sorted = String(str.sorted())
        groups[sorted, default: []].append(str)
    }

    return Array(groups.values)
}
```

## Стеки и очереди

### 1. Valid Parentheses (Правильные скобки) - с использованием стека

```swift
func isValid(_ s: String) -> Bool {
    var stack = [Character]()
    let pairs: [Character: Character] = [")": "(", "]": "[", "}": "{"]

    for char in s {
        if let opening = pairs[char] {
            // Закрывающая скобка - проверяем соответствие
            if stack.isEmpty || stack.removeLast() != opening {
                return false
            }
        } else {
            // Открывающая скобка - добавляем в стек
            stack.append(char)
        }
    }

    return stack.isEmpty
}
```

## Советы по решению алгоритмических задач

### 1. Понимание задачи
- Читайте задачу внимательно
- Определите входные и выходные данные
- Уточните ограничения

### 2. Разработка решения
- Придумайте наивное решение
- Оптимизируйте алгоритм
- Учитывайте edge cases

### 3. Написание кода
- Используйте понятные имена переменных
- Добавляйте комментарии для сложных частей
- Тестируйте на примерах

### 4. Анализ сложности
- Определите временную сложность (Big O)
- Оцените пространственную сложность
- Предложите оптимизации

## Рекомендуемые ресурсы

### Платформы для практики
- [LeetCode](https://leetcode.com/) - огромная база алгоритмических задач
- [HackerRank](https://www.hackerrank.com/) - технические интервью
- [CodeSignal](https://codesignal.com/) - оценка навыков программирования

### Книги
- "Cracking the Coding Interview" by Gayle Laakmann McDowell
- "Introduction to Algorithms" by Cormen, Leiserson, Rivest, Stein
- "Algorithm Design Manual" by Steven Skiena

### Онлайн курсы
- [Algorithm Specialization by Stanford](https://www.coursera.org/specializations/algorithms)
- [Data Structures and Algorithms in Swift](https://www.raywenderlich.com/books/data-structures-algorithms-in-swift/)

## Практика на собеседованиях

### Типичные вопросы по алгоритмам на iOS собеседованиях:
1. **Массивы и строки** - Two Sum, Maximum Subarray, Valid Parentheses
2. **Связанные списки** - Reverse Linked List, Merge Two Lists, Cycle Detection
3. **Деревья** - Maximum Depth, Level Order Traversal, Binary Search Tree validation
4. **Динамическое программирование** - Fibonacci, Climbing Stairs, Coin Change
5. **Графы** - Number of Islands, Course Schedule, Clone Graph

### Советы для успешного прохождения:
1. **Практикуйте регулярно** - решайте минимум 3-5 задач в неделю
2. **Объясняйте ход мыслей** - говорите вслух при решении задач
3. **Тестируйте код** - проверяйте на edge cases
4. **Анализируйте сложность** - объясняйте Big O notation
5. **Предлагайте оптимизации** - показывайте понимание trade-offs

Помните: "Алгоритмы - это не только решение задач, но и способ мышления."
