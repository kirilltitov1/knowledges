---
type: "thread"
topics: ["Tooling & Project Setup"]
status: "done"
summary: ""
title: "Build Process"
---

## 🎯 Общий обзор

Процесс сборки iOS приложения проходит через несколько ключевых стадий:

```
Исходный код (Swift/ObjC)
    ↓
Preprocessing (препроцессинг)
    ↓
Compilation (компиляция)
    ↓
Linking (линковка)
    ↓
Asset Compilation (компиляция ресурсов)
    ↓
Code Signing (подписание кода)
    ↓
Packaging (упаковка)
    ↓
.app / .ipa файл
```---

## 1️⃣ Preprocessing (Препроцессинг)

### Что происходит
- Обработка директив препроцессора (`#if`, `#define`, `#import`)
- Раскрытие макросов (в Objective-C)
- Обработка условной компиляции
- Генерация промежуточных файлов

### В Swift
```swift
#if DEBUG
    print("Debug mode")
#elseif RELEASE
    print("Release mode")
#endif
```

### В Objective-C
```objc
#ifdef DEBUG
    NSLog(@"Debug mode");
#endif
```

### Build Settings
- `GCC_PREPROCESSOR_DEFINITIONS` - определения препроцессора
- `SWIFT_ACTIVE_COMPILATION_CONDITIONS` - условия компиляции для Swift

---

## 2️⃣ Compilation (Компиляция)

### 2.1 Swift Compilation

#### Стадии компиляции Swift
1. **Parsing** - парсинг исходного кода в AST (Abstract Syntax Tree)
2. **Semantic Analysis** - проверка типов, разрешение имен
3. **SIL Generation** (Swift Intermediate Language) - генерация промежуточного представления
4. **SIL Optimization** - оптимизация на уровне SIL
5. **LLVM IR Generation** - генерация LLVM промежуточного представления
6. **LLVM Optimization** - оптимизация на уровне LLVM
7. **Code Generation** - генерация машинного кода (ARM64)

#### Ключевые концепции

**Whole Module Optimization (WMO)**
```bash
# Включается в Release конфигурации
SWIFT_COMPILATION_MODE = wholemodule
```
- Компилирует весь модуль как единое целое
- Позволяет проводить более агрессивные оптимизации
- Медленнее при компиляции, но быстрее результирующий код

**Incremental Compilation**
```bash
# Используется в Debug для ускорения
SWIFT_COMPILATION_MODE = incremental
```
- Перекомпилирует только изменённые файлы
- Быстрее при разработке
- Использует dependency graph для отслеживания изменений

#### Артефакты компиляции
- `.swiftmodule` - интерфейс модуля (публичные API)
- `.swiftdoc` - документация
- `.swiftsourceinfo` - информация об исходниках
- `.o` файлы - объектные файлы (машинный код)

### 2.2 Objective-C Compilation

#### Стадии
1. **Preprocessing** - обработка директив
2. **Lexical Analysis** - токенизация
3. **Parsing** - построение AST
4. **Semantic Analysis** - проверка типов
5. **Code Generation** - генерация LLVM IR
6. **Optimization** - оптимизация
7. **Assembly Generation** - генерация ассемблера
8. **Object File Generation** - создание .o файлов

#### Ключевые настройки
```bash
# Уровни оптимизации
GCC_OPTIMIZATION_LEVEL = 0  # Debug: -O0
GCC_OPTIMIZATION_LEVEL = s  # Release: -Os (size)
GCC_OPTIMIZATION_LEVEL = 3  # Aggressive: -O3
```

### 2.3 Build Settings для компиляции

```bash
# Оптимизация
SWIFT_OPTIMIZATION_LEVEL = -Onone  # Debug
SWIFT_OPTIMIZATION_LEVEL = -O      # Release
SWIFT_OPTIMIZATION_LEVEL = -Osize  # Size optimization

# Другие важные настройки
ENABLE_BITCODE = NO  # Bitcode (deprecated для iOS)
DEBUG_INFORMATION_FORMAT = dwarf-with-dsym  # Debug symbols
```

### 2.4 Generics (Дженерики) - Как работает под капотом

#### Что такое Generics в Swift

```swift
// Пример дженерик функции
func swap<T>(_ a: inout T, _ b: inout T) {
    let temp = a
    a = b
    b = temp
}

// Пример дженерик типа
struct Stack<Element> {
    private var items: [Element] = []
    
    mutating func push(_ item: Element) {
        items.append(item)
    }
    
    mutating func pop() -> Element? {
        return items.popLast()
    }
}
```

#### Как работает под капотом

##### 1. Generic Specialization (Специализация)

Компилятор Swift может работать с дженериками двумя способами:

**A. Static Specialization (Статическая специализация)**

```swift
// Исходный код
let numbers = Stack<Int>()
let strings = Stack<String>()

// Компилятор генерирует специализированные версии:
struct Stack_Int {  // Специализированная версия для Int
    private var items: [Int] = []
    func push(_ item: Int) { ... }
}

struct Stack_String {  // Специализированная версия для String
    private var items: [String] = []
    func push(_ item: String) { ... }
}
```

**Преимущества специализации:**
- Нет runtime overhead
- Прямые вызовы функций (без косвенности)
- Лучшая производительность
- Инлайнинг возможен

**Когда происходит:**
- Whole Module Optimization (WMO) включен
- Тип известен на момент компиляции
- В пределах одного модуля

```bash
# Build Settings для максимальной специализации
SWIFT_COMPILATION_MODE = wholemodule
SWIFT_OPTIMIZATION_LEVEL = -O
```

**B. Dynamic Dispatch через Protocol Witness Tables (PWT)**

Когда компилятор не может специализировать (неизвестный тип, библиотека), используется dynamic dispatch:

```swift
// Компилятор генерирует "boxed" версию
struct Stack<Element> {
    // Использует Type Metadata и Protocol Witness Tables
    private var items: [Element] = []  // Element - existential container
    
    func push(_ item: Element) {
        // Вызов через witness table
    }
}
```

**Что происходит под капотом:**

```
Stack<T>
    ↓
Type Metadata для T
    ↓
Protocol Witness Table (если T: Protocol)
    ↓
Value Witness Table (управление памятью: copy, destroy, allocate)
    ↓
Existential Container (если T > 3 слова)
```

##### 2. Type Metadata

Каждый тип в Swift имеет runtime metadata:

```swift
// Под капотом каждый вызов дженерик функции передаёт metadata
func genericFunction<T>(_ value: T) {
    // Скрытый параметр: Type Metadata для T
    print(type(of: value))
}

// Ассемблер (упрощённо):
// x0 = value
// x1 = Type Metadata для T
// call genericFunction
```

**Type Metadata содержит:**
- Size (размер типа)
- Alignment (выравнивание)
- Value Witness Table (операции с памятью)
- Method dispatch table (для классов)

##### 3. Value Witness Table (VWT)

Таблица операций для работы с любым типом:

```c
struct ValueWitnessTable {
    void (*initializeBufferWithCopyOfBuffer)(Buffer *dest, Buffer *src);
    void (*destroy)(T *object);
    void (*copy)(T *dest, T *src);
    size_t (*size)();
    size_t (*stride)();
    unsigned (*flags)();
    // ... и другие
}
```

**Пример использования:**

```swift
func printSize<T>(_ value: T) {
    // Под капотом:
    // 1. Получить Type Metadata для T
    // 2. Прочитать size из VWT
    // 3. Вывести размер
    print(MemoryLayout<T>.size)
}

printSize(42)        // Type Metadata для Int
printSize("hello")   // Type Metadata для String
```

##### 4. Existential Containers

Для хранения значений неизвестного типа:

```swift
// Existential container (3 слова для inline storage)
struct ExistentialContainer {
    var buffer: (Int, Int, Int)  // 24 байта для small values
    var metadata: TypeMetadata    // Указатель на metadata
    var witnessTable: VWT*        // Указатель на witness table
}

// Если тип > 24 байта:
struct LargeExistentialContainer {
    var heapPointer: HeapObject*  // Указатель на кучу
    var metadata: TypeMetadata
    var witnessTable: VWT*
}
```

**Пример:**

```swift
protocol Animal {
    func makeSound()
}

let animal: Animal = Dog()  // Existential container

// Под капотом:
// - Dog instance (если <= 24 байта, в buffer; иначе в heap)
// - Type Metadata для Dog
// - Protocol Witness Table для Dog: Animal
```

---

#### Generics в Static Libraries (.a)

##### Что происходит

**Компиляция:**
```bash
# При сборке статической библиотеки
1. Дженерик код компилируется в .o файлы
2. НО: без специализации для всех возможных типов
3. Генерируется "generic" версия (с metadata и witness tables)
4. .swiftmodule содержит интерфейс (но не реализацию)
```

**Линковка:**
```bash
# При линковке с приложением
1. Весь код из .a встраивается в executable
2. Компилятор приложения МОЖЕТ специализировать дженерики
3. Если WMO включен - возможна cross-module specialization
4. Dead code stripping может удалить неиспользуемые варианты
```

**Пример:**

```swift
// В статической библиотеке MyLib.a
public struct Cache<Value> {
    public func get() -> Value? { ... }
}

// В приложении
import MyLib

let cache = Cache<User>()  // ✅ Может быть специализирован
cache.get()  // Прямой вызов (если WMO включен)
```

##### Преимущества для дженериков

✅ **Компилятор видит всё при сборке приложения**
```bash
# Whole Module Optimization может работать
SWIFT_COMPILATION_MODE = wholemodule

# Результат:
- Полная специализация дженериков возможна
- Инлайнинг кода библиотеки
- Dead code stripping работает
- Лучшая производительность
```

✅ **Нет ABI проблем**
```swift
// Можно менять реализацию дженериков без breaking changes
// Код всегда перекомпилируется вместе
```

##### Недостатки

❌ **Больший размер бинарника**
```bash
# Каждая специализация добавляет код
Cache<User>    → Stack_User code
Cache<Post>    → Stack_Post code
Cache<Comment> → Stack_Comment code
```

❌ **Медленная компиляция**
```bash
# Перекомпиляция при изменении библиотеки
# Весь код встроен в executable
```

##### Оптимизация

```bash
# 1. Включить WMO для максимальной специализации
SWIFT_COMPILATION_MODE = wholemodule

# 2. Разрешить cross-module optimization
SWIFT_WHOLE_MODULE_OPTIMIZATION = YES

# 3. Включить LTO
LLVM_LTO = YES
```

**Результат:**
```swift
// Приложение
let cache = Cache<User>()
cache.get()  // → Превращается в прямой вызов, без overhead
```

##### Как именно генерируются специализации?

Это важный вопрос! Давай разберём пошагово что происходит:

**Шаг 1: Сборка статической библиотеки**

```swift
// MyLib/Cache.swift
public struct Cache<Value> {
    private var storage: [Value] = []
    
    public func get() -> Value? {
        return storage.last
    }
    
    public mutating func set(_ value: Value) {
        storage.append(value)
    }
}
```

При компиляции библиотеки:
```bash
# Компилируется в MyLib.a
swiftc -emit-library -static \
       Cache.swift \
       -o MyLib.a \
       -emit-module \
       -module-name MyLib

# Что генерируется:
MyLib.a               # Содержит GENERIC версию Cache<Value>
MyLib.swiftmodule     # Интерфейс модуля
MyLib.swiftdoc        # Документация
```

**Что в MyLib.a?**
```bash
# В .a файле находится:
- Generic версия Cache (работает с Type Metadata)
- Реализация через Value Witness Tables
- Машинный код, но БЕЗ конкретных типов
```

**Шаг 2: Использование в приложении**

```swift
// App/main.swift
import MyLib

struct User {
    let name: String
}

struct Post {
    let title: String
}

let userCache = Cache<User>()      // Использование #1
let postCache = Cache<Post>()      // Использование #2
```

**Шаг 3: Компиляция приложения (БЕЗ WMO)**

```bash
# Компиляция без оптимизации
swiftc main.swift \
       -I . \
       -L . -lMyLib \
       -o MyApp

# Что происходит:
1. Компилятор видит Cache<User> и Cache<Post>
2. НО не может специализировать (модульная граница)
3. Использует generic версию из MyLib.a
4. Всё работает через Type Metadata
```

**Результат:**
```asm
; В MyApp будет:
; - Generic версия Cache (из MyLib.a)
; - Вызовы через metadata:

; userCache.get()
ldr  x8, [x0, #metadata]           ; Загрузить metadata для User
bl   MyLib.Cache.get               ; Вызов generic версии
                                   ; Функция использует metadata
```

**Шаг 4: Компиляция приложения (С WMO)**

```bash
# Компиляция с Whole Module Optimization
swiftc main.swift \
       -I . \
       -L . -lMyLib \
       -o MyApp \
       -whole-module-optimization \
       -O

# Что происходит:
1. Компилятор видит Cache<User> и Cache<Post>
2. Видит .swiftmodule с интерфейсом
3. ГЕНЕРИРУЕТ СПЕЦИАЛИЗИРОВАННЫЕ ВЕРСИИ!
4. Создаёт Cache_User и Cache_Post
5. Заменяет вызовы на прямые
```

**Результат:**
```asm
; В MyApp теперь будет:

; Специализированная версия для User
_MyLib.Cache<User>.get:
    ; ПРЯМАЯ работа с User
    ldr  x0, [x1, #storage_offset]
    ret

; Специализированная версия для Post  
_MyLib.Cache<Post>.get:
    ; ПРЯМАЯ работа с Post
    ldr  x0, [x1, #storage_offset]
    ret

; userCache.get()
bl   _MyLib.Cache<User>.get        ; ПРЯМОЙ вызов!
                                   ; Нет metadata overhead
```

**Проверка специализаций:**

```bash
# Посмотреть символы в бинарнике
nm MyApp | grep Cache

# БЕЗ WMO увидишь:
_$s5MyLib5CacheV3getxyFTj  # Generic версия

# С WMO увидишь:
_$s5MyLib5CacheV3get4UserVyFTj    # Специализация для User
_$s5MyLib5CacheV3get4PostVyFTj    # Специализация для Post
```

**Ключевой момент:**

✅ **Специализации генерируются В ПРИЛОЖЕНИИ, а не в библиотеке!**

```
Static Library (MyLib.a):
    ┌─────────────────────────────┐
    │ Generic Cache<Value>        │  ← Одна версия
    │ (работает с любым типом)    │
    └─────────────────────────────┘
              ↓ линкуется в
    
Application (MyApp):
    ┌─────────────────────────────┐
    │ Cache<User>   ────────────► │  ← Специализация 1
    │ Cache<Post>   ────────────► │  ← Специализация 2
    │ Cache<Comment> ───────────► │  ← Специализация 3
    │                             │
    │ (Компилятор генерирует      │
    │  специализированный код     │
    │  на основе интерфейса)      │
    └─────────────────────────────┘
```

---

##### Системные фреймворки (Foundation, SwiftUI, etc.)

**ВАЖНО:** Foundation, UIKit, SwiftUI - это **НЕ статические библиотеки**!

Это системные динамические фреймворки с Module Stable ABI.

**Что это означает для дженериков:**

```swift
// Foundation дженерики
import Foundation

let array = Array<Int>([1, 2, 3])
let dict = Dictionary<String, Int>()
```

**Как это работает?**

```bash
# Foundation.framework структура:
/System/Library/Frameworks/Foundation.framework/
├── Foundation (dylib)              # Скомпилированный код
└── Modules/
    └── Foundation.swiftmodule/
        └── arm64.swiftinterface    # Интерфейс (НЕ реализация!)
```

**Ключевое отличие:**

1. **Стандартные типы уже специализированы в системе**
   ```swift
   // Array, Dictionary, Set - уже скомпилированы Apple
   // Включают типовые специализации (Int, String, etc.)
   let array = Array<Int>()  // Использует готовую специализацию
   ```

2. **Для кастомных типов - generic версия**
   ```swift
   struct MyType { }
   let array = Array<MyType>()  // Generic версия (медленнее)
   ```

**Проверка:**

```bash
# Посмотреть символы в Foundation
nm /System/Library/Frameworks/Foundation.framework/Foundation | grep Array

# Увидишь много специализаций:
_$sSa5countSivg    # Array.count
_$sSaMa            # Array metadata
# Но НЕ для всех возможных типов!
```

**Почему Foundation быстрый?**

```swift
// Часто используемые типы имеют специализации
let numbers = [1, 2, 3]        // Array<Int> - специализирован
let strings = ["a", "b"]       // Array<String> - специализирован
let dict = ["a": 1]            // Dictionary<String, Int> - специализирован

// Редкие типы используют generic версию
struct Rare { }
let rares = [Rare()]           // Array<Rare> - generic версия
```

**Module Stable ABI:**

```bash
# Что это значит:
1. Foundation скомпилирован Apple
2. Бинарник один для всех приложений
3. НЕ перекомпилируется для каждого приложения
4. ABI гарантирует совместимость

# Преимущества:
- Обновляется с iOS (bug fixes)
- Делится между всеми приложениями
- Меньше размер приложения

# Недостатки:
- Нет full specialization для кастомных типов
- Indirect dispatch для редких типов
```

---

##### Сравнение: Static Library vs System Framework

| Аспект | Static Library (.a) | System Framework |
|--------|---------------------|------------------|
| **Специализация** | ✅ Генерируется в приложении | ⚠️ Только для типовых типов |
| **Производительность** | ✅ Лучшая (full specialization) | ⚠️ Зависит от типа |
| **Размер приложения** | ❌ Больше (код встроен) | ✅ Меньше (делится) |
| **Обновления** | ❌ Требует recompile | ✅ Обновляется с iOS |
| **Компиляция** | ❌ Медленнее | ✅ Быстрее |
| **ABI stability** | ✅ Не важна | ✅ Обязательна |

**Практический пример:**

```swift
// 1. Foundation (system framework)
let array = Array<Int>()      // ✅ Быстро (специализировано Apple)
array.append(1)

struct User { let id: Int }
let users = Array<User>()     // ⚠️ Медленнее (generic версия)
users.append(User(id: 1))

// 2. Ваша статическая библиотека
import MyLib

let cache = Cache<User>()     // ✅ Может быть специализирован в MyApp!
cache.set(user)               // ✅ Direct call (с WMO)
```

**Как проверить что используется:**

```bash
# 1. Посмотреть зависимости
otool -L MyApp
# Увидишь:
# /System/Library/Frameworks/Foundation.framework/Foundation (system)
# MyLib - встроен в executable

# 2. Посмотреть символы
nm MyApp | grep "MyLib\|Foundation"
# MyLib символы - в MyApp
# Foundation символы - undefined (загружаются из системы)

# 3. Размер
size MyApp
# Включает весь код из static libraries
# НЕ включает код из system frameworks
```

---

##### Best Practices для дженериков

**1. Для библиотек, которые вы контролируете:**

```swift
// Используйте static library для производительности
// Build Settings:
MACH_O_TYPE = staticlib

// Пользователи смогут получить специализации
```

**2. Для системных типов:**

```swift
// Используйте стандартные типы где возможно
let array = Array<Int>()     // ✅ Оптимизировано
let dict = Dictionary<String, User>()  // ✅ String оптимизирован
```

**3. Для performance-critical кода:**

```swift
// Предоставьте @inlinable версии
@inlinable
public func fastOperation<T>(_ value: T) {
    // Код инлайнится, может быть специализирован
}
```

**4. Измеряйте производительность:**

```swift
// Используйте Instruments Time Profiler
// Смотрите на:
// - Количество indirect calls
// - swift_getTypeByMangledName (overhead)
// - Witness table lookups
```

---

##### Incremental vs WMO с библиотеками

**Важный вопрос:** Можно ли использовать Incremental вместо WMO?

**Краткий ответ:** ✅ **Да, можно!** Incremental - это стандартный режим для Debug.

---

**Incremental Compilation Mode**

```bash
# Build Settings
SWIFT_COMPILATION_MODE = incremental

# Что это значит:
- Каждый файл компилируется отдельно
- Перекомпиляция только изменённых файлов
- Быстрее сборка во время разработки
- Но ограниченные оптимизации
```

**Как работает с библиотеками:**

**1. Static Library + Incremental в приложении**

```bash
# Библиотека: MyLib.a (содержит generic код)
# Приложение: SWIFT_COMPILATION_MODE = incremental

Что происходит:
┌────────────────────────────────────────┐
│ Приложение (Incremental)               │
│                                        │
│ main.swift                             │
│   let cache = Cache<User>()            │
│   ↓                                    │
│ Компилируется ОТДЕЛЬНО от других файлов│
│ НЕТ cross-file оптимизаций             │
│ ❌ Специализация ОГРАНИЧЕНА            │
│                                        │
│ user.swift                             │
│   let cache2 = Cache<User>()           │
│   ↓                                    │
│ Компилируется ОТДЕЛЬНО                 │
│ Может создать ДУБЛИРУЮЩУЮ специализацию│
└────────────────────────────────────────┘
```

**Результат:**
```swift
// main.swift скомпилирован
Cache<User>.get()  // ⚠️ Может быть generic или специализирован
                   // Зависит от видимости типа в файле

// user.swift скомпилирован отдельно
Cache<User>.get()  // ⚠️ Может генерировать дубликат специализации
```

**Что теряется:**
- ❌ Меньше специализаций (не видит использование в других файлах)
- ❌ Нет devirtualization
- ❌ Нет cross-file inlining
- ❌ Может быть дублирование кода
- ⚠️ Generic версия используется чаще

**Что остаётся:**
- ✅ Работает корректно (всегда есть generic версия)
- ✅ Быстрая сборка
- ✅ Intra-file оптимизации (внутри файла)

---

**2. Static Library + WMO в приложении**

```bash
# Библиотека: MyLib.a (содержит generic код)
# Приложение: SWIFT_COMPILATION_MODE = wholemodule

Что происходит:
┌────────────────────────────────────────┐
│ Приложение (Whole Module)              │
│                                        │
│ Компилятор видит ВСЕ файлы сразу:      │
│ main.swift: Cache<User>                │
│ user.swift: Cache<User>                │
│ post.swift: Cache<Post>                │
│   ↓                                    │
│ Анализирует все использования          │
│ ✅ Генерирует специализации:           │
│    - Cache<User>  (одна для всех)      │
│    - Cache<Post>                       │
│ ✅ Direct calls везде                  │
│ ✅ Инлайнинг где возможно              │
└────────────────────────────────────────┘
```

**Результат:**
```swift
// Везде в приложении
Cache<User>.get()  // ✅ Direct call к специализации
Cache<Post>.get()  // ✅ Direct call к специализации
```

---

**3. Dynamic Framework (всегда generic!)**

```bash
# Framework: MyFramework.framework
# НЕВАЖНО что в приложении: incremental или WMO

Что происходит:
┌────────────────────────────────────────┐
│ Framework (скомпилирован отдельно)     │
│                                        │
│ Cache<Value> - ТОЛЬКО generic версия   │
│ ❌ Специализации невозможны            │
│ ❌ Закрытая модульная граница          │
└────────────────────────────────────────┘
         ↓ использование
┌────────────────────────────────────────┐
│ Приложение                             │
│ (incremental ИЛИ wholemodule)          │
│                                        │
│ let cache = Cache<User>()              │
│ ❌ НЕ может специализировать           │
│ ❌ Всегда indirect dispatch            │
│                                        │
│ Режим компиляции НЕ ВАЖЕН!             │
└────────────────────────────────────────┘
```

---

**Сравнительная таблица производительности**

| Библиотека | App: Incremental | App: WMO | Разница |
|------------|------------------|----------|---------|
| **Static Library** | ⚠️ Частично специализирован | ✅ Полностью специализирован | **2-3x** |
| **Dynamic Framework** | ❌ Generic (indirect) | ❌ Generic (indirect) | Одинаково медленно |
| **System Framework** | ⚠️ Зависит от типа | ⚠️ Зависит от типа | Одинаково |

---

**Практические примеры**

**Пример 1: Static Library с Incremental**

```swift
// MyLib.a
public struct Cache<Value> {
    public func get() -> Value? { ... }
}

// App (SWIFT_COMPILATION_MODE = incremental)
// File: UserScreen.swift
import MyLib

struct User { let name: String }

func loadUser() {
    let cache = Cache<User>()  // ⚠️ Может быть специализирован в ЭТОМ файле
    cache.get()                // ⚠️ Или generic версия
}

// File: PostScreen.swift
import MyLib

func loadPost() {
    let cache = Cache<User>()  // ⚠️ Может создать ДУБЛИРУЮЩУЮ специализацию
    cache.get()                // ⚠️ Компилятор не знает про UserScreen.swift
}
```

**Что происходит:**
```bash
# Компиляция
swiftc UserScreen.swift -c -o UserScreen.o  # Отдельно
swiftc PostScreen.swift -c -o PostScreen.o  # Отдельно

# Результат:
# - Может быть 2 специализации Cache<User> (дублирование)
# - Или обе используют generic версию (медленнее)
# - Нет гарантий оптимизации
```

**Пример 2: Static Library с WMO**

```swift
// То же самое, но с WMO

// App (SWIFT_COMPILATION_MODE = wholemodule)
// Все файлы компилируются вместе

// Компиляция
swiftc UserScreen.swift PostScreen.swift -whole-module-optimization -o MyApp

# Результат:
# ✅ ОДНА специализация Cache<User> для всех файлов
# ✅ Direct calls везде
# ✅ Инлайнинг где возможно
# ✅ Оптимальная производительность
```

---

**Пример 3: Dynamic Framework (режим не важен)**

```swift
// MyFramework.framework (скомпилирован)
public struct Cache<Value> {
    public func get() -> Value? { ... }
}

// App (ЛЮБОЙ режим: incremental ИЛИ wholemodule)
import MyFramework

let cache = Cache<User>()
cache.get()  // ❌ ВСЕГДА indirect dispatch
             // ❌ Не зависит от режима компиляции приложения
```

---

**Когда использовать Incremental?**

✅ **ИСПОЛЬЗУЙТЕ Incremental когда:**

1. **Разработка / Debug сборка**
   ```bash
   # Debug Configuration
   SWIFT_COMPILATION_MODE = incremental
   SWIFT_OPTIMIZATION_LEVEL = -Onone
   
   # Преимущества:
   - Быстрая инкрементальная сборка
   - Быстрая итерация
   - Debug symbols полные
   ```

2. **Большие проекты (длительная сборка)**
   ```bash
   # Если WMO сборка занимает > 5 минут
   # Incremental может быть в 5-10x быстрее
   ```

3. **CI для feature веток (не release)**
   ```bash
   # Ускорить feedback loop
   # Не критична производительность
   ```

4. **Работа с большим количеством файлов**
   ```bash
   # Изменил 1 файл из 1000
   # Incremental: перекомпилирует 1 файл (~2 сек)
   # WMO: перекомпилирует все (~5 минут)
   ```

---

**Когда использовать WMO?**

✅ **ИСПОЛЬЗУЙТЕ WMO когда:**

1. **Release / Production сборка**
   ```bash
   # Release Configuration
   SWIFT_COMPILATION_MODE = wholemodule
   SWIFT_OPTIMIZATION_LEVEL = -O
   
   # Преимущества:
   - Максимальная производительность
   - Специализация дженериков
   - Devirtualization
   - Меньший размер бинарника
   ```

2. **Библиотеки (особенно с дженериками)**
   ```bash
   # Чтобы пользователи получили специализации
   ```

3. **Performance-critical код**
   ```bash
   # Если производительность критична
   ```

4. **CI для release веток**
   ```bash
   # Production builds
   # App Store uploads
   ```

---

**Гибридный подход (рекомендуется)**

Используйте разные режимы для разных конфигураций:

```bash
# Debug Configuration
SWIFT_COMPILATION_MODE = incremental        # Быстрая сборка
SWIFT_OPTIMIZATION_LEVEL = -Onone          # Без оптимизаций
ENABLE_TESTABILITY = YES                   # Testing enabled

# Release Configuration  
SWIFT_COMPILATION_MODE = wholemodule       # Полная оптимизация
SWIFT_OPTIMIZATION_LEVEL = -O              # Aggressive optimization
ENABLE_TESTABILITY = NO                    # Testing disabled
DEAD_CODE_STRIPPING = YES                  # Strip unused
```

**Преимущества:**
- ✅ Быстрая разработка (Incremental в Debug)
- ✅ Оптимальный продукт (WMO в Release)
- ✅ Лучшее из обоих миров

---

**Как проверить что используется?**

```bash
# 1. Посмотреть Build Settings
xcodebuild -showBuildSettings \
    -workspace MyApp.xcworkspace \
    -scheme MyApp \
    -configuration Debug | grep SWIFT_COMPILATION_MODE

# Incremental покажет:
SWIFT_COMPILATION_MODE = singlefile

# WMO покажет:
SWIFT_COMPILATION_MODE = wholemodule

# 2. Посмотреть build log
# Incremental: много параллельных задач компиляции файлов
# WMO: одна задача "Compiling Swift module"

# 3. Время сборки
# Clean build:
#   Incremental: быстрее
#   WMO: медленнее
# Incremental rebuild (1 файл изменён):
#   Incremental: очень быстро
#   WMO: долго (все файлы)
```

---

**Измерение влияния на производительность**

```bash
# 1. Сборка с Incremental
xcodebuild -configuration Debug SWIFT_COMPILATION_MODE=incremental

# 2. Запуск в Instruments Time Profiler
instruments -t "Time Profiler" MyApp.app

# 3. Ищите:
# - Много вызовов swift_getTypeByMangledName (generic overhead)
# - Много indirect calls через witness tables
# - Меньше специализаций

# 4. Сборка с WMO
xcodebuild -configuration Release SWIFT_COMPILATION_MODE=wholemodule

# 5. Сравнить результаты
# - Меньше generic overhead
# - Больше direct calls
# - Лучшая производительность
```

---

**Best Practice: Progressive Compilation**

Для больших проектов используйте progressive подход:

```bash
# Этап 1: Development (быстро)
SWIFT_COMPILATION_MODE = incremental

# Этап 2: Pre-release testing (баланс)
SWIFT_COMPILATION_MODE = incremental
SWIFT_OPTIMIZATION_LEVEL = -O  # Оптимизации включены

# Этап 3: Release candidate (максимум)
SWIFT_COMPILATION_MODE = wholemodule
SWIFT_OPTIMIZATION_LEVEL = -O
LLVM_LTO = YES  # Link-time optimization

# Этап 4: App Store
# Те же настройки что и Этап 3
```

---

**Важные нюансы**

1. **Incremental НЕ ЛОМАЕТ ничего**
   ```swift
   // Код работает одинаково
   // Просто медленнее и больше размер
   ```

2. **WMO может найти больше ошибок**
   ```swift
   // WMO делает более агрессивный анализ
   // Может найти dead code, unused variables
   ```

3. **Библиотеки всегда компилируйте с настройками для production**
   ```bash
   # Даже если приложение в Debug
   # Библиотеки должны быть оптимизированы
   ```

4. **CI/CD стратегия**
   ```bash
   # Pull Request: Incremental (быстрый feedback)
   # Main branch: WMO (production quality)
   # Nightly builds: WMO + все оптимизации
   ```

---

#### Generics в Dynamic Frameworks (.framework)

##### Что происходит

**Компиляция:**
```bash
# При сборке dynamic framework
1. Дженерик код компилируется БЕЗ знания конкретных типов
2. Генерируется ТОЛЬКО generic версия (с metadata/witness tables)
3. Специализация НЕВОЗМОЖНА (closed module boundary)
4. .swiftmodule содержит интерфейс
5. .dylib содержит машинный код
```

**Runtime:**
```bash
# При запуске приложения
1. dyld загружает framework
2. Все вызовы дженериков идут через:
   - Type Metadata
   - Protocol Witness Tables
   - Value Witness Tables
3. Indirect dispatch (медленнее)
4. Нет специализации
```

**Пример:**

```swift
// В dynamic framework MyFramework.framework
public struct Cache<Value> {
    public func get() -> Value? {
        // Компилируется в generic версию
        // Использует Type Metadata для Value
    }
}

// В приложении
import MyFramework

let cache = Cache<User>()  // ❌ НЕ будет специализирован
cache.get()  // Indirect dispatch через witness tables
```

##### Как это работает под капотом

**1. Каждый вызов передаёт metadata:**

```swift
// Исходный код
let cache = Cache<User>()
cache.get()

// Под капотом (упрощённо):
// x0 = cache instance
// x1 = Type Metadata для User  ← ВСЕГДА передаётся!
// call MyFramework.Cache.get(metadata: TypeMetadata)
```

**2. Framework использует metadata:**

```c
// В framework (псевдокод на C)
void* Cache_get(void* cache, TypeMetadata* T) {
    // Получить Value Witness Table из T
    ValueWitnessTable* vwt = T->valueWitnessTable;
    
    // Использовать VWT для операций с Value
    size_t size = vwt->size();
    void* value = malloc(size);
    vwt->copy(value, cache->storage);
    
    return value;
}
```

**3. Protocol Witness Tables для constraints:**

```swift
// В framework
public func process<T: Codable>(_ value: T) {
    // Под капотом:
    // - Type Metadata для T
    // - Protocol Witness Table для T: Codable
    let encoder = JSONEncoder()
    try? encoder.encode(value)  // Вызов через PWT
}

// В приложении
process(user)  // Передаёт PWT для User: Codable
```

##### Производительность

❌ **Runtime overhead:**

```swift
// Static library (специализировано)
cache.get()  
// → прямой вызов: call 0x12345678
// → может быть инлайнен
// → 1-2 инструкции

// Dynamic framework (generic)
cache.get()
// → загрузить metadata: ldr x1, [metadata]
// → загрузить witness table: ldr x2, [x1, #offset]
// → загрузить функцию: ldr x3, [x2, #offset]
// → indirect call: blr x3
// → 10+ инструкций, не может быть инлайнен
```

**Benchmark (примерный):**
```
Static specialized:  1.0x
Dynamic generic:     2-5x медленнее
```

##### Direct vs Indirect Call/Access

Это фундаментальное различие в том, как процессор выполняет код.

**Direct Call (Прямой вызов)**

```swift
// Код Swift
func calculate() -> Int {
    return 42
}

let result = calculate()  // Прямой вызов
```

**Ассемблер (ARM64):**
```asm
; Адрес функции известен на момент компиляции
bl   0x100004abc        ; Branch and Link - прямой переход
; 0x100004abc - это конкретный адрес функции

; CPU выполняет:
; 1. Загрузить адрес 0x100004abc в Program Counter (PC)
; 2. Сохранить адрес возврата в Link Register (LR)
; 3. Начать выполнение
; → 1 инструкция, ~1-2 CPU цикла
```

**Характеристики:**
- ✅ Адрес известен на момент компиляции
- ✅ Процессор может предсказать переход (branch prediction)
- ✅ Может быть инлайнен компилятором
- ✅ Очень быстро: 1-2 CPU цикла
- ✅ Pipeline не ломается

**Indirect Call (Косвенный вызов)**

```swift
// Код Swift (через witness table)
protocol Calculator {
    func calculate() -> Int
}

func process(_ calc: Calculator) {
    let result = calc.calculate()  // Косвенный вызов
}
```

**Ассемблер (ARM64):**
```asm
; Адрес функции НЕ известен на момент компиляции
; Нужно прочитать его из памяти

; Шаг 1: Загрузить указатель на witness table
ldr  x8, [x0, #metadata_offset]     ; x0 = existential container
                                    ; x8 = protocol witness table

; Шаг 2: Загрузить указатель на функцию из witness table
ldr  x9, [x8, #function_offset]     ; x9 = адрес функции calculate

; Шаг 3: Косвенный вызов через регистр
blr  x9                              ; Branch and Link Register
                                    ; Вызвать функцию по адресу в x9

; CPU выполняет:
; 1. Чтение из памяти (ldr) - может быть cache miss
; 2. Ещё одно чтение из памяти (ldr) - ещё один cache miss
; 3. Косвенный переход (blr) - branch predictor не работает хорошо
; → 3+ инструкции, ~10-20 CPU циклов (с учётом cache misses)
```

**Характеристики:**
- ❌ Адрес неизвестен до runtime
- ❌ Требует чтение из памяти (может быть cache miss)
- ❌ Branch predictor работает хуже
- ❌ НЕ может быть инлайнен
- ❌ Медленно: 10-20+ CPU циклов
- ❌ Pipeline может ломаться (branch misprediction)

---

**Direct Access (Прямой доступ к памяти)**

```swift
// @frozen struct - layout известен
@frozen
public struct Point {
    public var x: Double  // offset = 0
    public var y: Double  // offset = 8
}

let point = Point(x: 10, y: 20)
let value = point.x  // Прямой доступ
```

**Ассемблер (ARM64):**
```asm
; point находится по адресу в x0
ldr  d0, [x0]           ; Прямая загрузка из x0 + 0
                        ; d0 = point.x

; CPU выполняет:
; 1. Прочитать из памяти по адресу x0
; → 1 инструкция, ~3-5 CPU циклов (L1 cache hit)
```

**Indirect Access (Косвенный доступ)**

```swift
// Resilient struct - layout скрыт
public struct Cache<Value> {
    private var storage: [Value]
}

let cache = Cache<User>()
let value = cache.storage  // Косвенный доступ через accessor
```

**Ассемблер (ARM64):**
```asm
; Нужно вызвать accessor функцию
; Шаг 1: Получить Type Metadata
ldr  x8, [x0, #metadata_offset]

; Шаг 2: Получить accessor из metadata
ldr  x9, [x8, #accessor_offset]

; Шаг 3: Вызвать accessor
blr  x9                     ; Косвенный вызов

; Шаг 4: Внутри accessor
;   - Вычислить offset для Value с учётом alignment
;   - Прочитать значение
;   - Вернуть результат

; → 10+ инструкций, ~20-30 CPU циклов
```

---

**Сравнительная таблица**

| Операция | Direct | Indirect | Разница |
|----------|--------|----------|---------|
| **Function Call** | `bl 0x1234` | `ldr x9, [table]; blr x9` | **10-20x** медленнее |
| **Field Access** | `ldr d0, [x0]` | `call accessor` | **5-10x** медленнее |
| **Инструкций** | 1-2 | 5-15 | - |
| **CPU циклов** | 1-5 | 10-50+ | - |
| **Инлайнинг** | ✅ Возможен | ❌ Невозможен | - |
| **Branch prediction** | ✅ Работает отлично | ❌ Работает плохо | - |
| **Cache locality** | ✅ Хорошая | ❌ Может быть плохой | - |

---

**Реальный пример: Protocol dispatch**

```swift
// Protocol с методом
protocol Drawable {
    func draw()
}

class Circle: Drawable {
    func draw() {
        print("Drawing circle")
    }
}

class Square: Drawable {
    func draw() {
        print("Drawing square")
    }
}

// Вариант 1: Direct dispatch (generic специализация)
func render1<T: Drawable>(_ shape: T) {
    shape.draw()  // Может быть специализирован → Direct call
}

render1(Circle())  // Компилятор знает тип = Circle
// → Direct call к Circle.draw()

// Вариант 2: Indirect dispatch (через protocol witness table)
func render2(_ shape: Drawable) {
    shape.draw()  // Всегда indirect через PWT
}

render2(Circle())  // Компилятор НЕ знает конкретный тип
// → Indirect call через Protocol Witness Table
```

**Ассемблер для варианта 1 (Direct):**
```asm
; Специализированная версия для Circle
render1_Circle:
    ; Прямой вызов
    bl   Circle.draw
    ret

; 2 инструкции, ~3-5 CPU циклов
```

**Ассемблер для варианта 2 (Indirect):**
```asm
render2:
    ; x0 = existential container
    ; Загрузить witness table
    ldr  x8, [x0, #witness_table_offset]
    
    ; Загрузить адрес draw() из witness table
    ldr  x9, [x8, #draw_offset]
    
    ; Косвенный вызов
    blr  x9
    ret

; 4+ инструкции, ~15-25 CPU циклов
```

---

**Почему indirect медленнее?**

1. **Memory Latency**
   ```
   L1 Cache hit:      ~1-4 cycles
   L2 Cache hit:      ~10-20 cycles
   L3 Cache hit:      ~40-75 cycles
   RAM:               ~100-300 cycles
   
   Indirect требует 2-3 чтения из памяти!
   ```

2. **Branch Misprediction**
   ```
   Правильное предсказание:  0 штрафа
   Неправильное:             ~15-20 cycles (pipeline flush)
   
   Direct call: процессор знает куда прыгать
   Indirect call: адрес загружается из памяти → хуже предсказание
   ```

3. **Нет инлайнинга**
   ```swift
   // Direct - может быть инлайнен
   func fast() { return 42 }
   let x = fast()  // → let x = 42 (0 инструкций)
   
   // Indirect - НЕ может быть инлайнен
   func slow() { return 42 }
   let x = slowViaPointer()  // → call + return (минимум 2 инструкции)
   ```

4. **CPU Pipeline**
   ```
   Direct: процессор может предзагрузить инструкции (prefetch)
   Indirect: процессор не знает куда прыгать → pipeline stall
   ```

---

**Когда неизбежен indirect?**

1. **Виртуальные методы (class)**
   ```swift
   class Base {
       func method() { }  // Indirect через vtable
   }
   ```

2. **Protocol witness tables**
   ```swift
   func process(_ value: Codable) {
       value.encode()  // Indirect через PWT
   }
   ```

3. **Dynamic frameworks с дженериками**
   ```swift
   // Framework
   public func generic<T>(_ value: T) { }
   
   // App
   generic(myValue)  // Indirect call в framework
   ```

4. **Objective-C message dispatch**
   ```objc
   [object method];  // Indirect через objc_msgSend
   ```

---

**Как избежать indirect?**

1. **Whole Module Optimization**
   ```bash
   SWIFT_COMPILATION_MODE = wholemodule
   # Позволяет devirtualize и специализировать
   ```

2. **@inlinable**
   ```swift
   @inlinable
   public func hotPath() {
       // Код инлайнится → direct
   }
   ```

3. **final keyword**
   ```swift
   final class MyClass {
       func method() { }  // Может быть direct (нет override)
   }
   ```

4. **Static dispatch вместо protocol**
   ```swift
   // Вместо
   func process(_ value: Codable) { }
   
   // Используйте
   func process<T: Codable>(_ value: T) { }  // Может специализироваться
   ```

5. **Struct вместо class**
   ```swift
   struct Value {  // Нет vtable
       func method() { }  // Direct call
   }
   ```

---

**Профилирование indirect calls**

```bash
# Instruments → Time Profiler
# Ищите:
# - objc_msgSend (Objective-C overhead)
# - swift_getTypeByMangledName (много = плохо)
# - *_witness_* symbols (protocol dispatch)

# Command line
instruments -t "Time Profiler" MyApp.app

# Анализ с помощью perf (Linux/macOS dtrace)
dtrace -n 'pid$target::*indirect*:entry' -p PID
```

---

##### Module Stability (@frozen)

Для оптимизации можно использовать `@frozen`:

```swift
// В framework
@frozen
public struct Point {
    public var x: Double
    public var y: Double
}

// Позволяет:
// - Прямой доступ к полям (без metadata)
// - Специализацию в некоторых случаях
// - Лучшую производительность
```

**НО: @frozen это ABI contract!**
```swift
// НЕЛЬЗЯ потом:
// - Добавить поля
// - Изменить layout
// - Без breaking change
```

##### Resilience (гибкость)

По умолчанию Swift использует "resilient" модель:

```swift
// В framework (без @frozen)
public struct Cache<Value> {
    private var storage: [Value]  // Layout скрыт
}

// В приложении - доступ только через функции
cache.get()  // Всегда через функцию (нет прямого доступа)

// Преимущество: можно менять реализацию без breaking changes
// Недостаток: медленнее (indirect access)
```

##### XCFramework и Generics

```bash
# XCFramework (binary distribution)
MyFramework.xcframework/
├── ios-arm64/
│   └── MyFramework.framework
│       ├── MyFramework (dylib)
│       └── Modules/
│           └── MyFramework.swiftmodule/
│               └── arm64.swiftmodule  # Только интерфейс!
└── ios-arm64-simulator/

# Проблемы:
- Нет исходников → нет возможности специализировать
- Только generic версия
- Медленнее чем static linking
```

---

#### Решение проблемы производительности

##### 1. @inlinable для критичных функций

```swift
// В dynamic framework
public struct Cache<Value> {
    @inlinable  // Код будет встроен в .swiftmodule
    public func get() -> Value? {
        // Реализация попадёт в .swiftmodule
        return storage.last
    }
    
    // НЕ @inlinable - останется в dylib
    public func complexOperation() { ... }
}

// В приложении
cache.get()  
// ✅ Может быть специализирован и инлайнен!
// Код взят из .swiftmodule, а не из dylib
```

**Важно:**
```swift
// @inlinable это ABI contract!
// Нельзя менять реализацию без breaking change

// ✅ Используйте для:
// - Простых getters/setters
// - Математических операций
// - Критичных по производительности мест

// ❌ НЕ используйте для:
// - Сложной логики, которая может измениться
// - Большого кода (раздует размер приложения)
```

##### 2. Специализированные не-generic версии

```swift
// В framework - generic версия
public struct Cache<Value> {
    public func get() -> Value? { ... }
}

// + Специализированные версии для частых типов
public struct IntCache {
    @inlinable
    public func get() -> Int? { ... }
}

public struct StringCache {
    @inlinable
    public func get() -> String? { ... }
}

// В приложении - используйте специализированные
let cache = IntCache()  // ✅ Быстро
```

##### 3. Type-erased wrappers

```swift
// Для скрытия дженериков в API
public class AnyCache {
    private let _get: () -> Any?
    
    public init<C: CacheProtocol>(_ cache: C) {
        _get = { cache.get() }
    }
    
    public func get() -> Any? {
        return _get()
    }
}

// Убирает дженерики из публичного API
// Упрощает binary compatibility
```

---

#### Практические рекомендации

##### Для Static Libraries (рекомендуется для производительности)

```bash
✅ ИСПОЛЬЗУЙТЕ когда:
- Производительность критична
- Много дженерик кода
- Небольшая библиотека
- Редкие обновления

# Build Settings
MACH_O_TYPE = staticlib
SWIFT_COMPILATION_MODE = wholemodule  # Для WMO в приложении
```

##### Для Dynamic Frameworks (рекомендуется для гибкости)

```bash
✅ ИСПОЛЬЗУЙТЕ когда:
- Код делится между app и extensions
- Большая библиотека (уменьшает compile time)
- Частые обновления
- Нужна ABI stability

# Оптимизация производительности:
1. Используйте @inlinable для hot paths
2. Используйте @frozen для stable types
3. Предоставьте специализированные версии
4. Профилируйте и оптимизируйте bottlenecks
```

##### Hybrid подход (лучшее из обоих миров)

```swift
// Framework содержит:
// 1. Protocols (в public API)
public protocol CacheProtocol {
    associatedtype Value
    func get() -> Value?
}

// 2. Generic реализация (internal)
struct GenericCache<Value>: CacheProtocol {
    func get() -> Value? { ... }
}

// 3. Фабрика в приложении (может специализировать)
public func makeCache<V>() -> some CacheProtocol<Value = V> {
    GenericCache<V>()  // Специализация в приложении
}
```

---

#### Debugging и Analysis

##### Проверка специализации

```bash
# 1. Посмотреть сгенерированные символы
nm MyApp | grep -i "generic\|specialized"

# 2. Дизассемблировать
otool -tV MyApp | less

# 3. Проверить размер binary
size MyApp

# 4. Анализ производительности
# Instruments → Time Profiler
# Смотреть на:
# - swift_getTypeByMangledName (много = плохо)
# - swift_allocObject (много = много boxing)
```

##### Build log analysis

```bash
# Включить verbose output
xcodebuild -verbose OTHER_SWIFT_FLAGS="-driver-print-jobs"

# Найти:
# - Generic specialization logs
# - Inlining decisions
# - Module compilation info
```

---

#### Вопросы для собеседования (Senior+)

##### Про дженерики

1. **Объясните разницу между generic specialization и dynamic dispatch для дженериков**
   - Specialization: компилируется под конкретный тип (быстро)
   - Dynamic: через metadata/witness tables (гибко, но медленнее)

2. **Что такое Protocol Witness Table?**
   - Таблица функций для реализации protocol methods
   - Аналог vtable в C++

3. **Что такое Value Witness Table?**
   - Таблица операций для управления памятью (copy, destroy, etc.)
   - Для любого типа

4. **Почему дженерики в dynamic framework медленнее чем в static library?**
   - Нет возможности специализировать
   - Indirect dispatch через metadata
   - Нет inline optimization

5. **Как @inlinable влияет на производительность дженериков в framework?**
   - Код попадает в .swiftmodule
   - Может быть специализирован в приложении
   - Но это ABI contract

6. **Что такое Existential Container?**
   - Структура для хранения значений protocol типа
   - 3 слова для inline storage + metadata

7. **Как Whole Module Optimization влияет на дженерики?**
   - Позволяет специализировать across files
   - Cross-module optimization возможна
   - Лучшая производительность

8. **В чём разница между @frozen и resilient типами?**
   - @frozen: layout известен (быстро, но нельзя менять)
   - Resilient: layout скрыт (гибко, но медленнее)

---

## 3️⃣ Linking (Линковка)

### Что такое линковка
Процесс объединения объектных файлов (.o) и библиотек в единый исполняемый файл.

### Типы линковки

#### Static Linking (Статическая)
```bash
# Static library (.a)
- Код встраивается в исполняемый файл
- Увеличивает размер приложения
- Быстрее запуск приложения
- Нет runtime зависимостей
```

**Пример подключения**:
```ruby
# Podfile
pod 'Alamofire', :git => 'https://github.com/Alamofire/Alamofire.git'
# по умолчанию подключается статически
```

#### Dynamic Linking (Динамическая)
```bash
# Dynamic framework (.framework)
- Код загружается во время выполнения
- Уменьшает размер приложения
- Медленнее запуск (dyld loading)
- Можно переиспользовать между app extensions
```

**Пример**:
```ruby
# Podfile
use_frameworks!  # Использовать динамические фреймворки
pod 'Alamofire'
```

### Dynamic Linker (dyld)

#### Что делает dyld при запуске приложения
1. **Load dylibs** - загрузка динамических библиотек
2. **Rebase** - корректировка указателей из-за ASLR
3. **Bind** - привязка символов
4. **Initialize** - запуск инициализаторов (+load, __attribute__((constructor)))
5. **Main** - передача управления main()

#### Оптимизация dyld
```bash
# dyld optimization
DYLD_LIBRARY_PATH
DYLD_FRAMEWORK_PATH

# Используйте dyld shared cache
# iOS кэширует системные фреймворки
```

### Link-Time Optimization (LTO)

```bash
# Включение LTO
LLVM_LTO = YES  # Whole-module LTO

# Виды LTO
- Full LTO: максимальная оптимизация, медленная сборка
- Thin LTO: компромисс между скоростью и оптимизацией
```

### Linker Flags

```bash
# Общие флаги
OTHER_LDFLAGS = -ObjC  # Загрузить все Objective-C классы
OTHER_LDFLAGS = -all_load  # Загрузить всё из статических библиотек
OTHER_LDFLAGS = -force_load <library>  # Загрузить конкретную библиотеку

# Framework search paths
FRAMEWORK_SEARCH_PATHS = $(inherited) $(PROJECT_DIR)/Frameworks
```

### Dead Code Stripping

```bash
# Удаление неиспользуемого кода
DEAD_CODE_STRIPPING = YES

# Работает только с:
- Static linking
- Правильной visibility (public/internal)
```

---

## 4️⃣ Asset Compilation (Компиляция ресурсов)

### Asset Catalog

#### Что компилируется
- `Assets.xcassets` → `Assets.car` (compiled asset catalog)
- Оптимизация изображений
- Генерация app icons всех размеров
- Компиляция color assets

#### Формат .car
```bash
# Бинарный формат, содержит:
- Оптимизированные PNG/JPEG
- @1x, @2x, @3x варианты
- Dark mode variants
- Device-specific assets
```

### Storyboards и XIBs

```bash
# Компиляция
Main.storyboard → Main.storyboardc (compiled)
LaunchScreen.xib → LaunchScreen.nib

# Процесс:
1. XML parsing
2. Validation
3. Binary serialization
4. Optimization
```

### Localizable Resources

```bash
# Локализация
Localizable.strings → компилируются в .lproj папки
- Encoding conversion
- String validation
- Binary plist format
```

### Info.plist Processing

```bash
# Обработка Info.plist
- Variable substitution: $(PRODUCT_NAME)
- Merging with entitlements
- Validation
- Binary plist conversion
```

---

## 5️⃣ Code Signing (Подписание кода)

### Зачем нужна подпись
- Гарантирует, что код не был изменён
- Идентифицирует разработчика
- Необходима для установки на устройство/App Store

### Компоненты Code Signing

#### 1. Certificates (Сертификаты)
```bash
# Типы сертификатов
- Development: для разработки и тестирования
- Distribution: для App Store и Ad Hoc
- Enterprise: для корпоративного распространения
```

**Как работает**:
```
Private Key (на вашем Mac)
    ↓
CSR (Certificate Signing Request)
    ↓
Apple (подписывает)
    ↓
Certificate (.cer)
```

#### 2. Provisioning Profiles

```bash
# Содержит:
- App ID (com.company.appname)
- Device UUIDs (для development/ad hoc)
- Entitlements
- Certificate(s)
- Expiration date
```

**Типы профилей**:
- **Development**: для разработки (до 100 устройств)
- **Ad Hoc**: для тестирования вне App Store (до 100 устройств)
- **App Store**: для публикации в App Store
- **Enterprise**: для внутреннего распространения

#### 3. Entitlements

```xml
<!-- Example.entitlements -->
<plist version="1.0">
<dict>
    <key>aps-environment</key>
    <string>production</string>
    
    <key>com.apple.developer.applesignin</key>
    <array>
        <string>Default</string>
    </array>
    
    <key>keychain-access-groups</key>
    <array>
        <string>$(AppIdentifierPrefix)com.company.app</string>
    </array>
</dict>
</plist>
```

### Процесс подписания

```bash
# Команда codesign
codesign --force \
         --sign "iPhone Distribution: Company Name" \
         --entitlements MyApp.entitlements \
         --timestamp \
         MyApp.app

# Проверка подписи
codesign --verify --verbose=4 MyApp.app
codesign --display --verbose=4 MyApp.app

# Проверка provisioning profile
security cms -D -i embedded.mobileprovision
```

### Code Signature

```bash
# Что подписывается
MyApp.app/
├── MyApp (executable)           ← подписан
├── Frameworks/
│   └── MyFramework.framework    ← подписан отдельно
├── PlugIns/
│   └── Widget.appex              ← подписан отдельно
├── _CodeSignature/
│   └── CodeResources            ← манифест всех ресурсов
└── embedded.mobileprovision     ← профиль подписи
```

### Automatic Code Signing

```bash
# Xcode 8+ automatic signing
CODE_SIGN_STYLE = Automatic
DEVELOPMENT_TEAM = XXXXXXXXXX

# Manual signing
CODE_SIGN_STYLE = Manual
CODE_SIGN_IDENTITY = "iPhone Distribution"
PROVISIONING_PROFILE_SPECIFIER = "AppStore Profile"
```

### Проблемы и решения

**Проблема**: "No signing certificate found"
```bash
# Решение:
1. Проверить Keychain Access
2. Убедиться, что есть private key
3. Переустановить сертификат
```

**Проблема**: "Code signing entitlements are not compatible"
```bash
# Решение:
1. Синхронизировать entitlements с provisioning profile
2. Проверить App ID capabilities
3. Обновить профиль
```

---

## 6️⃣ Packaging (Упаковка)

### .app Bundle Structure

```bash
MyApp.app/
├── MyApp                        # Executable (Mach-O binary)
├── Info.plist                   # App metadata
├── embedded.mobileprovision     # Provisioning profile
├── PkgInfo                      # Legacy file
├── Assets.car                   # Compiled assets
├── Base.lproj/                  # Storyboards
│   ├── Main.storyboardc
│   └── LaunchScreen.storyboardc
├── en.lproj/                    # Localization
│   └── Localizable.strings
├── Frameworks/                  # Embedded frameworks
│   └── MyFramework.framework
├── PlugIns/                     # App extensions
│   └── Widget.appex
├── _CodeSignature/              # Signature data
│   └── CodeResources
└── [Other resources]
```

### .ipa Creation

#### Что такое .ipa
```bash
# .ipa = iOS App Store Package
# По сути это ZIP-архив с определённой структурой
```

#### Структура .ipa

```bash
MyApp.ipa (ZIP archive)
└── Payload/
    └── MyApp.app/
        └── [все файлы приложения]
```

#### Создание .ipa вручную

```bash
# 1. Создать структуру
mkdir Payload
cp -r MyApp.app Payload/

# 2. Заархивировать
zip -r MyApp.ipa Payload/

# 3. Проверить
unzip -l MyApp.ipa
```

#### Создание через Xcode

```bash
# Archive для распространения
xcodebuild archive \
    -workspace MyApp.xcworkspace \
    -scheme MyApp \
    -configuration Release \
    -archivePath MyApp.xcarchive

# Export .ipa
xcodebuild -exportArchive \
    -archivePath MyApp.xcarchive \
    -exportPath output/ \
    -exportOptionsPlist ExportOptions.plist
```

### Export Options

```xml
<!-- ExportOptions.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store</string>  <!-- app-store, ad-hoc, enterprise, development -->
    
    <key>teamID</key>
    <string>XXXXXXXXXX</string>
    
    <key>uploadSymbols</key>
    <true/>
    
    <key>uploadBitcode</key>
    <false/>
    
    <key>compileBitcode</key>
    <false/>
    
    <key>signingStyle</key>
    <string>automatic</string>
    
    <key>provisioningProfiles</key>
    <dict>
        <key>com.company.myapp</key>
        <string>AppStore Profile Name</string>
    </dict>
</dict>
</plist>
```

---

## 7️⃣ Build Configurations

### Debug vs Release

#### Debug Configuration
```bash
# Оптимизация
SWIFT_OPTIMIZATION_LEVEL = -Onone
GCC_OPTIMIZATION_LEVEL = 0

# Debug symbols
DEBUG_INFORMATION_FORMAT = dwarf
ENABLE_TESTABILITY = YES

# Preprocessor
GCC_PREPROCESSOR_DEFINITIONS = DEBUG=1
SWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG

# Другое
ENABLE_NS_ASSERTIONS = YES  # NSAssert работает
VALIDATE_PRODUCT = NO
```

#### Release Configuration
```bash
# Оптимизация
SWIFT_OPTIMIZATION_LEVEL = -O
GCC_OPTIMIZATION_LEVEL = s  # Optimize for size
SWIFT_COMPILATION_MODE = wholemodule

# Debug symbols
DEBUG_INFORMATION_FORMAT = dwarf-with-dsym
ENABLE_TESTABILITY = NO

# Code stripping
DEAD_CODE_STRIPPING = YES
STRIP_INSTALLED_PRODUCT = YES
COPY_PHASE_STRIP = YES

# Другое
ENABLE_NS_ASSERTIONS = NO
VALIDATE_PRODUCT = YES
```

### Custom Configurations

```bash
# Создание кастомных конфигураций
- Staging
- Production
- QA

# Использование
#if STAGING
    let apiURL = "https://staging.api.com"
#elseif PRODUCTION
    let apiURL = "https://api.com"
#endif
```

---

## 8️⃣ Build System

### xcodebuild

#### Основные команды

```bash
# Сборка
xcodebuild build \
    -workspace MyApp.xcworkspace \
    -scheme MyApp \
    -configuration Debug \
    -sdk iphoneos \
    -destination 'generic/platform=iOS'

# Очистка
xcodebuild clean \
    -workspace MyApp.xcworkspace \
    -scheme MyApp

# Архивирование
xcodebuild archive \
    -workspace MyApp.xcworkspace \
    -scheme MyApp \
    -configuration Release \
    -archivePath build/MyApp.xcarchive

# Тестирование
xcodebuild test \
    -workspace MyApp.xcworkspace \
    -scheme MyApp \
    -destination 'platform=iOS Simulator,name=iPhone 15'

# Список schemes
xcodebuild -list -workspace MyApp.xcworkspace

# Список destinations
xcodebuild -showdestinations \
    -workspace MyApp.xcworkspace \
    -scheme MyApp
```

### New Build System (Xcode 10+)

#### Преимущества
- Быстрее параллельная сборка
- Лучшее определение зависимостей
- Более точное инкрементальное пересобирание
- Improved build system diagnostics

#### Build Settings
```bash
# Включить новую систему сборки
# Project Settings > Build System
# "New Build System (Default)"
```

### Derived Data

```bash
# Расположение
~/Library/Developer/Xcode/DerivedData/

# Структура
DerivedData/
└── MyApp-<hash>/
    ├── Build/
    │   ├── Intermediates.noindex/  # Промежуточные файлы
    │   └── Products/               # Итоговые продукты
    ├── Index/                      # Index для code completion
    ├── Logs/                       # Build logs
    └── ModuleCache.noindex/        # Кэш модулей

# Очистка
rm -rf ~/Library/Developer/Xcode/DerivedData/
# или через Xcode: Product > Clean Build Folder (Cmd+Shift+K)
```

---

## 9️⃣ Optimization Techniques

### Build Time Optimization

#### 1. Использование Precompiled Headers (PCH)
```objc
// ProjectName-Prefix.pch
#ifdef __OBJC__
    #import <UIKit/UIKit.h>
    #import <Foundation/Foundation.h>
#endif
```

#### 2. Параллельная сборка
```bash
# Build settings
PARALLEL_BUILD_ENABLED = YES

# Command line
xcodebuild -jobs 8  # Использовать 8 параллельных задач
```

#### 3. Модульность
```swift
// Разбивайте проект на модули/фреймворки
// Быстрее инкрементальная сборка
MyApp
├── CoreModule.framework
├── UIModule.framework
└── NetworkModule.framework
```

#### 4. Оптимизация Swift Compilation

```bash
# Debug: Incremental, каждый файл отдельно
SWIFT_COMPILATION_MODE = incremental

# Отключить WHOLE_OPTIMIZATION в Debug
SWIFT_WHOLE_MODULE_OPTIMIZATION = NO

# Измерять время компиляции
OTHER_SWIFT_FLAGS = -Xfrontend -warn-long-function-bodies=100
OTHER_SWIFT_FLAGS = -Xfrontend -warn-long-expression-type-checking=100
```

#### 5. Dependency Management
```bash
# Используйте binary frameworks где возможно
# Вместо компиляции из исходников
pod 'Firebase/Analytics', :binary => true
```

### Runtime Optimization

#### 1. App Launch Time
```bash
# Минимизируйте dyld loading
- Уменьшите количество динамических фреймворков
- Используйте static linking где возможно
- Отложите инициализацию тяжёлых библиотек
```

#### 2. Binary Size
```bash
# Оптимизация размера
DEPLOYMENT_POSTPROCESSING = YES
STRIP_INSTALLED_PRODUCT = YES
STRIP_SWIFT_SYMBOLS = YES

# App Thinning
ENABLE_BITCODE = NO  # Deprecated для iOS
ASSETCATALOG_COMPILER_OPTIMIZATION = space

# Удаление неиспользуемых ресурсов
# Используйте инструменты типа FengNiao
```

---

## 🔟 Advanced Topics

### Bitcode (Deprecated)

```bash
# Что такое Bitcode
- Промежуточное представление (LLVM IR)
- Позволяет Apple перекомпилировать для новых процессоров
- Deprecated с Xcode 14

ENABLE_BITCODE = NO  # По умолчанию теперь NO
```

### dSYM Files

```bash
# Debug Symbol Files
- Необходимы для символикации crash reports
- Генерируются при Release сборке

# Build Settings
DEBUG_INFORMATION_FORMAT = dwarf-with-dsym

# Расположение
build/MyApp.app.dSYM

# Upload в Crashlytics/Firebase
./upload-symbols -gsp GoogleService-Info.plist -p ios build/MyApp.app.dSYM
```

### Build Scripts (Run Script Phases)

```bash
# Примеры использования

# 1. SwiftLint
if which swiftlint >/dev/null; then
  swiftlint
else
  echo "warning: SwiftLint not installed"
fi

# 2. Копирование Firebase config
cp "${SRCROOT}/Config/${CONFIGURATION}/GoogleService-Info.plist" "${BUILT_PRODUCTS_DIR}/${PRODUCT_NAME}.app/"

# 3. Версионирование
buildNumber=$(/usr/libexec/PlistBuddy -c "Print CFBundleVersion" "${INFOPLIST_FILE}")
buildNumber=$(($buildNumber + 1))
/usr/libexec/PlistBuddy -c "Set :CFBundleVersion $buildNumber" "${INFOPLIST_FILE}"
```

### Build Phases Order

```bash
Правильный порядок Build Phases:

1. Target Dependencies
2. [Run Script] - перед компиляцией (генерация кода)
3. Compile Sources
4. [Run Script] - после компиляции (SwiftLint)
5. Link Binary With Libraries
6. Copy Bundle Resources
7. [Run Script] - после копирования (обработка ресурсов)
8. Embed Frameworks
9. [Run Script] - финальные действия (Firebase, dSYM upload)
```

### Conditional Compilation

```swift
// По платформе
#if os(iOS)
    import UIKit
#elseif os(macOS)
    import AppKit
#endif

// По архитектуре
#if arch(arm64)
    // ARM64 specific
#elseif arch(x86_64)
    // Simulator
#endif

// По Swift версии
#if swift(>=5.5)
    // Async/await available
#endif

// Кастомные флаги
#if DEBUG
    print("Debug build")
#endif
```

---

## 📊 Build Analysis

### Build Time Analysis

```bash
# Xcode Build Timeline
# Product > Perform Action > Build With Timing Summary

# Показывает:
- Время компиляции каждого файла
- Параллельность сборки
- Bottlenecks

# Command line
xcodebuild -workspace MyApp.xcworkspace \
           -scheme MyApp \
           -showBuildTimingSummary
```

### Compilation Time per File

```bash
# Добавить в Other Swift Flags
-Xfrontend -debug-time-function-bodies
-Xfrontend -debug-time-compilation

# Анализ результатов
grep "time to" build_log.txt | sort -n
```

---

## 🐛 Common Issues & Troubleshooting

### 1. Module Not Found

```bash
Ошибка: "No such module 'ModuleName'"

Решения:
1. Clean Build Folder (Cmd+Shift+K)
2. Удалить DerivedData
3. Проверить Framework Search Paths
4. Rebuild dependencies (pod install)
5. Проверить target membership файла
```

### 2. Signing Errors

```bash
Ошибка: "Code signing is required"

Решения:
1. Проверить сертификаты в Keychain
2. Обновить provisioning profiles
3. Проверить Bundle ID match
4. Включить Automatic Signing
5. Проверить entitlements
```

### 3. Linker Errors

```bash
Ошибка: "Undefined symbols for architecture"

Решения:
1. Проверить target membership
2. Добавить -ObjC в OTHER_LDFLAGS
3. Проверить правильность импорта библиотек
4. Проверить architecture в Build Settings
```

### 4. Asset Catalog Errors

```bash
Ошибка: "Failed to find or create execution context"

Решения:
1. Перезапустить Xcode
2. Удалить DerivedData
3. Проверить структуру Assets.xcassets
4. Проверить формат изображений
```

### 5. Provisioning Profile Issues

```bash
Ошибка: "Provisioning profile doesn't support capability"

Решения:
1. Обновить capabilities в App ID
2. Скачать новый профиль
3. Синхронизировать entitlements
4. Проверить expiration date
```

---

## 🔧 Best Practices

### 1. Build Configuration Management

```bash
✅ DO:
- Используйте разные конфигурации для разных окружений
- Храните конфиги в .xcconfig файлах
- Используйте environment variables

❌ DON'T:
- Хардкодить API keys в коде
- Использовать одну конфигурацию для всего
```

### 2. Dependency Management

```bash
✅ DO:
- Закрепляйте версии зависимостей
- Используйте Lockfile (Podfile.lock, Package.resolved)
- Регулярно обновляйте зависимости

❌ DON'T:
- Использовать 'latest' без контроля
- Коммитить Pods/ в git (спорно)
```

### 3. Build Scripts

```bash
✅ DO:
- Документируйте все кастомные скрипты
- Делайте скрипты идемпотентными
- Проверяйте exit codes

❌ DON'T:
- Делать сложную логику в Run Script phases
- Игнорировать ошибки скриптов
```

### 4. Code Signing

```bash
✅ DO:
- Используйте Automatic Signing для разработки
- Храните сертификаты в Keychain
- Используйте Fastlane Match для команды

❌ DON'T:
- Шарить private keys
- Использовать wildcard profiles в production
```

### 5. Build Optimization

```bash
✅ DO:
- Используйте модульную архитектуру
- Измеряйте время сборки
- Оптимизируйте медленные файлы

❌ DON'T:
- Игнорировать warnings
- Держать неиспользуемые зависимости
```

---

## 📝 Вопросы для собеседования Senior

### Процесс сборки

1. **Опишите полный процесс сборки iOS приложения от исходного кода до .ipa файла**
   - Preprocessing, Compilation, Linking, Asset Compilation, Code Signing, Packaging

2. **Что происходит при компиляции Swift кода?**
   - Parsing → AST → SIL → LLVM IR → Machine Code

3. **В чём разница между Whole Module Optimization и Incremental Compilation?**
   - WMO: весь модуль сразу, больше оптимизаций, медленнее
   - Incremental: по файлам, быстрее для debug

4. **Что такое Link-Time Optimization?**
   - Оптимизация на стадии линковки между модулями
   - Full vs Thin LTO

### Линковка

5. **В чём разница между static и dynamic linking?**
   - Static: встраивается в binary, больше размер, быстрее запуск
   - Dynamic: загружается runtime, меньше размер, медленнее запуск

6. **Как работает dynamic linker (dyld)?**
   - Load → Rebase → Bind → Initialize → Main

7. **Что такое dead code stripping?**
   - Удаление неиспользуемого кода при линковке

### Code Signing

8. **Объясните процесс code signing в iOS**
   - Certificate + Provisioning Profile + Entitlements
   - Private/Public key cryptography

9. **Какие типы provisioning profiles существуют?**
   - Development, Ad Hoc, App Store, Enterprise

10. **Что содержится в provisioning profile?**
    - App ID, Device IDs, Entitlements, Certificate, Expiration

### Оптимизация

11. **Как оптимизировать время сборки?**
    - Модульность, параллелизация, precompiled headers
    - Измерение времени компиляции
    - Оптимизация медленных файлов

12. **Как оптимизировать размер приложения?**
    - Strip symbols, App Thinning, Asset compression
    - Dead code stripping, удаление неиспользуемых ресурсов

13. **Как уменьшить время запуска приложения?**
    - Уменьшить количество динамических фреймворков
    - Static linking, отложенная инициализация

### Advanced

14. **Что такое dSYM файлы и зачем они нужны?**
    - Debug symbols для символикации crash reports

15. **Как работает Build System в Xcode?**
    - Dependency graph, parallel tasks, incremental builds

16. **Объясните разницу между Debug и Release конфигурациями**
    - Оптимизации, debug symbols, assertions, stripping

17. **Что такое .xcarchive и что в нём содержится?**
    - Bundle содержит .app, dSYMs, Info.plist, metadata

18. **Как работает App Thinning?**
    - Slicing (device-specific), Bitcode (deprecated), On-demand resources

---

## 🔗 Связанные темы

- [[git]] - Version Control
- [[CI & CD]] - Автоматизация сборки
- [[app-store-connect]] - Распространение
- [[certificates-provisioning]] - Code Signing

---

## 📚 Полезные ресурсы

### Официальная документация
- [Xcode Build System Guide](https://developer.apple.com/documentation/xcode)
- [Code Signing Guide](https://developer.apple.com/support/code-signing/)
- [App Distribution Guide](https://developer.apple.com/distribute/)

### Инструменты
- `xcodebuild` - Command-line build tool
- `codesign` - Code signing tool
- `xcrun` - Run Xcode tools
- `xcode-select` - Manage Xcode versions
- `altool` - Upload to App Store
- `security` - Keychain management

### Build Time Analysis
- [BuildTimeAnalyzer](https://github.com/RobertGummesson/BuildTimeAnalyzer-for-Xcode)
- Xcode Build Timeline (Product → Perform Action)

### Fastlane
```ruby
# Автоматизация всего процесса
lane :release do
  increment_build_number
  build_app(scheme: "MyApp")
  upload_to_app_store
end
```

---

## 💡 Tips & Tricks

### Ускорение сборки

```bash
# 1. Использовать .xcconfig файлы
SWIFT_COMPILATION_MODE = singlefile  # для Debug
SWIFT_COMPILATION_MODE = wholemodule # для Release

# 2. Кэширование CocoaPods
$ pod install --deployment

# 3. Использовать cached builds в CI
# Кэшировать DerivedData, Carthage/Build, .build/

# 4. Измерять время
defaults write com.apple.dt.Xcode ShowBuildOperationDuration -bool YES
```

### Debugging Build Issues

```bash
# Verbose xcodebuild output
xcodebuild -verbose

# Show environment
xcodebuild -showBuildSettings

# Build log location
~/Library/Developer/Xcode/DerivedData/*/Logs/Build/

# Analyze build log
xcbeautify  # Pretty build output
```

### Scripting

```bash
# Автоматический build number
agvtool next-version -all

# Автоматическая версия из git
git describe --tags --always
```

---

## ✅ Чеклист для Senior

- [ ] Понимаю все стадии сборки от исходников до .ipa
- [ ] Могу объяснить разницу между static и dynamic linking
- [ ] Знаю как работает code signing и provisioning
- [ ] Могу оптимизировать build time и app size
- [ ] Понимаю как работает dyld при запуске
- [ ] Знаю как дебажить проблемы со сборкой
- [ ] Могу настроить CI/CD pipeline
- [ ] Понимаю Build Settings и их влияние
- [ ] Знаю best practices для разных конфигураций
- [ ] Могу объяснить New Build System в Xcode

---

**Дата создания:** 2025-10-05  
**Статус:** Complete ✅  
**Уровень:** Senior iOS Developer

