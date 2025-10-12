---
type: "guide"
status: "draft"
level: "intermediate"
title: "iOS Interview Questions"
---

# 🎯 Вопросы для собеседований по iOS разработке

Комплексный сборник вопросов для подготовки к техническим собеседованиям на позиции iOS разработчика. Вопросы разделены по темам и уровням сложности.

## 📋 Структура собеседования

Типичное техническое собеседование на iOS разработчика включает:

### ⏱️ Временная структура (60-90 минут)
1. **Введение и знакомство** (5-10 мин)
2. **Технические вопросы по iOS** (30-40 мин)
3. **Кодинг задание или архитектурное решение** (15-20 мин)
4. **Вопросы кандидату** (5-10 мин)

### 🎯 Основные темы вопросов
- **Swift Language** - основы языка, современные возможности
- **iOS SDK** - фреймворки и API
- **Архитектура** - паттерны проектирования, организация кода
- **Память и производительность** - управление памятью, оптимизация
- **Асинхронность** - многопоточность, async/await
- **UI/UX** - интерфейс, анимации, адаптивность
- **Тестирование** - стратегии тестирования, инструменты
- **Инструменты разработки** - Xcode, отладка, профилирование

## 🧠 Технические вопросы

### 1. Swift Language

#### Базовый уровень
**Вопрос:** Что такое опционалы в Swift? Приведите примеры использования.
```swift
// Опционалы представляют значения, которые могут быть nil
var name: String? = "John"
var age: Int? = nil

// Безопасная распаковка
if let unwrappedName = name {
    print("Name: \(unwrappedName)")
}

// Force unwrap (использовать осторожно!)
let definiteName = name!

// Optional chaining
let nameLength = name?.count

// Nil coalescing
let displayName = name ?? "Unknown"
```

**Вопрос:** Объясните разницу между классами и структурами в Swift.

**Ответ:**
- **Структуры** (value types): копируются при присваивании, хранятся в стеке
- **Классы** (reference types): передаются по ссылке, хранятся в куче
- Структуры не поддерживают наследование, классы поддерживают

**Вопрос:** Что такое протоколы в Swift? Приведите пример использования.

#### Средний уровень
**Вопрос:** Объясните механизм ARC (Automatic Reference Counting).

**Ответ:** ARC автоматически управляет памятью, вставляя вызовы `retain`, `release` и `autorelease` во время компиляции. Подробнее см. [[iOS/Memory/arc-mrc|ARC vs MRC]].

**Вопрос:** Что такое property wrappers? Приведите пример.

```swift
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
}

var user = User()
user.age = 150  // Автоматически станет 100
```

**Вопрос:** Объясните разницу между `weak` и `unowned` ссылками.

### 2. iOS SDK и фреймворки

#### Базовый уровень
**Вопрос:** Что такое UIViewController lifecycle? Назовите основные методы.

**Ответ:**
1. `init(coder:)` или `init(nibName:bundle:)`
2. `loadView()` - создание корневого view
3. `viewDidLoad()` - настройка после загрузки view
4. `viewWillAppear()` - перед появлением на экране
5. `viewDidAppear()` - после появления на экране
6. `viewWillDisappear()` - перед исчезновением
7. `viewDidDisappear()` - после исчезновения
8. `deinit` - очистка ресурсов

**Вопрос:** Объясните разницу между frame и bounds в UIView.

**Ответ:**
- **frame**: позиция и размер view в координатах superview
- **bounds**: позиция и размер view в собственной системе координат

#### Средний уровень
**Вопрос:** Что такое Auto Layout? Объясните constraint-based layout.

**Ответ:** Auto Layout - система автоматического позиционирования элементов интерфейса на основе ограничений (constraints).

```swift
// Пример создания constraints программно
let constraint = button.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -20)
constraint.isActive = true
```

**Вопрос:** Что такое size classes? Приведите пример использования.

### 3. Архитектура и паттерны

#### Базовый уровень
**Вопрос:** Назовите основные архитектурные паттерны для iOS приложений.

**Ответ:**
1. **MVC** (Model-View-Controller) - классический паттерн
2. **MVVM** (Model-View-ViewModel) - с data binding
3. **VIPER** (View-Interactor-Presenter-Entity-Router) - модульный подход
4. **Clean Architecture** - независимость от фреймворков

**Вопрос:** Что такое делегаты в iOS? Приведите пример использования.

#### Средний уровень
**Вопрос:** Объясните паттерн Coordinator для навигации.

**Ответ:** Coordinator - паттерн для управления навигацией и потоком приложения без жесткой связи между view controllers.

```swift
protocol Coordinator {
    func start()
}

class MainCoordinator: Coordinator {
    private let navigationController: UINavigationController
    private let dependencies: Dependencies

    init(navigationController: UINavigationController, dependencies: Dependencies) {
        self.navigationController = navigationController
        self.dependencies = dependencies
    }

    func start() {
        showMainScreen()
    }

    private func showMainScreen() {
        let viewController = MainViewController()
        viewController.delegate = self
        navigationController.pushViewController(viewController, animated: true)
    }
}
```

**Вопрос:** Что такое Dependency Injection? Приведите пример.

### 4. Память и производительность

#### Базовый уровень
**Вопрос:** Что такое retain cycle? Как его избежать?

**Ответ:** Retain cycle - ситуация, когда два или более объекта ссылаются друг на друга сильными ссылками, что препятствует их удалению из памяти.

```swift
// ❌ Retain cycle
class A {
    var b: B?
}

class B {
    var a: A?  // strong ссылка создает цикл
}

// ✅ Исправление
class B {
    weak var a: A?  // weak ссылка разрывает цикл
}
```

**Вопрос:** Что делает @autoreleasepool?

**Ответ:** `@autoreleasepool` создает пул для отложенного освобождения объектов, полезен в циклах для контроля памяти.

#### Средний уровень
**Вопрос:** Объясните разницу между stack и heap памятью.

**Ответ:**
- **Stack**: быстрая память для локальных переменных, автоматически управляется
- **Heap**: динамическая память для объектов классов, управляется ARC

**Вопрос:** Что такое Instruments? Назовите основные инструменты для анализа производительности.

### 5. Асинхронность и многопоточность

#### Базовый уровень
**Вопрос:** Что такое GCD (Grand Central Dispatch)?

**Ответ:** GCD - библиотека для выполнения задач асинхронно и управления очередями в iOS/macOS.

```swift
// Основные типы очередей
DispatchQueue.main.async { /* UI обновления */ }
DispatchQueue.global(qos: .userInitiated).async { /* фоновые задачи */ }

// Кастомные очереди
let customQueue = DispatchQueue(label: "com.myapp.background")
```

**Вопрос:** Что такое Operation Queue?

#### Средний уровень
**Вопрос:** Объясните async/await в Swift.

**Ответ:** Async/await - современный синтаксис для асинхронного программирования в Swift 5.5+.

```swift
func fetchData() async throws -> Data {
    let (data, _) = try await URLSession.shared.data(from: url)
    return data
}

Task {
    do {
        let data = try await fetchData()
        // Обработка данных
    } catch {
        // Обработка ошибки
    }
}
```

**Вопрос:** Что такое actors в Swift?

### 6. UI/UX и интерфейс

#### Базовый уровень
**Вопрос:** Что такое UITableView и как с ним работать?

**Ответ:** UITableView - компонент для отображения списков данных с поддержкой переиспользования ячеек.

```swift
extension ViewController: UITableViewDataSource, UITableViewDelegate {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return items.count
    }

    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "Cell", for: indexPath)
        cell.textLabel?.text = items[indexPath.row]
        return cell
    }
}
```

**Вопрос:** Что такое Auto Layout? Зачем оно нужно?

#### Средний уровень
**Вопрос:** Объясните difference между UIView и CALayer.

**Ответ:**
- **UIView**: управляет контентом, обрабатывает события, участвует в responder chain
- **CALayer**: отвечает за визуальное представление, анимации, геометрию

**Вопрос:** Что такое SwiftUI и чем оно отличается от UIKit?

### 7. Тестирование

#### Базовый уровень
**Вопрос:** Что такое unit тестирование? Приведите пример.

**Ответ:** Unit тестирование - проверка отдельных компонентов кода в изоляции.

```swift
func testUserInitialization() {
    let user = User(name: "John", age: 25)

    XCTAssertEqual(user.name, "John")
    XCTAssertEqual(user.age, 25)
    XCTAssertNotNil(user.id)
}
```

**Вопрос:** Что такое mocking в тестировании?

### 8. Инструменты разработки

#### Базовый уровень
**Вопрос:** Назовите основные инструменты для отладки iOS приложений.

**Ответ:**
1. **Xcode Debugger** - точки останова, инспекция переменных
2. **Instruments** - профилирование производительности и памяти
3. **Console** - логирование и вывод информации
4. **Memory Graph Debugger** - визуализация объектов в памяти

**Вопрос:** Что такое breakpoints и как их использовать?

## 💼 Поведенческие вопросы

### 1. Опыт и проекты

**Вопрос:** Расскажите о вашем последнем проекте. Какие технологии использовали?

**Вопрос:** С какими сложностями сталкивались в разработке? Как их решали?

**Вопрос:** Какой ваш любимый проект и почему?

### 2. Работа в команде

**Вопрос:** Как вы работаете с дизайнерами?

**Вопрос:** Как решаете конфликты в коде при работе в команде?

**Вопрос:** Расскажите о вашем опыте code review.

### 3. Профессиональное развитие

**Вопрос:** Как вы изучаете новые технологии?

**Вопрос:** Какие ресурсы используете для профессионального роста?

**Вопрос:** Как оцениваете качество своего кода?

### 4. Решение проблем

**Вопрос:** Расскажите о самой сложной технической проблеме, которую решали.

**Вопрос:** Как подходите к отладке сложных багов?

**Вопрос:** Как оптимизировали производительность приложения?

## 🧪 Практические задания

### 1. Кодинг задание (типичное)

**Задание:** Реализуйте простой кэш для изображений с использованием NSCache.

```swift
class ImageCache {
    private let cache = NSCache<NSString, UIImage>()

    func image(for url: URL) -> UIImage? {
        let key = url.absoluteString as NSString

        if let cachedImage = cache.object(forKey: key) {
            return cachedImage
        }

        guard let image = UIImage(contentsOfFile: url.path) else {
            return nil
        }

        cache.setObject(image, forKey: key)
        return image
    }
}
```

**Вопросы для обсуждения:**
- Как обработать ошибки загрузки?
- Как ограничить размер кэша?
- Как сделать кэш потокобезопасным?

### 2. Архитектурное задание

**Задание:** Спроектируйте архитектуру для приложения с новостной лентой.

**Ожидаемые компоненты:**
- Модели данных (Article, User, Comment)
- Сервисы (NetworkService, DataService)
- ViewModels для экранов
- Координатор для навигации
- Протоколы для тестируемости

### 3. Алгоритмическое задание

**Задание:** Реализуйте функцию поиска подстроки в строке (алгоритм КМП или простой поиск).

```swift
func findSubstring(_ text: String, _ pattern: String) -> [Int] {
    var result: [Int] = []
    let textArray = Array(text)
    let patternArray = Array(pattern)

    for i in 0..<(textArray.count - patternArray.count + 1) {
        var found = true
        for j in 0..<patternArray.count {
            if textArray[i + j] != patternArray[j] {
                found = false
                break
            }
        }
        if found {
            result.append(i)
        }
    }

    return result
}
```

## 📊 Оценка уровня кандидата

### Junior (0-2 года опыта)
- Знает основы Swift и iOS SDK
- Понимает базовые концепции (MVC, delegates)
- Может написать простой код под руководством
- Знает базовые инструменты разработки

### Middle (2-5 лет опыта)
- Глубоко знает Swift и iOS SDK
- Работал с различными архитектурными паттернами
- Может самостоятельно решать сложные задачи
- Знает инструменты профилирования и отладки

### Senior (5+ лет опыта)
- Эксперт в Swift и iOS разработке
- Может проектировать сложные архитектуры
- Знает принципы производительности и оптимизации
- Может руководить командой разработки

## 🎯 Подготовка к собеседованию

### 1. Техническая подготовка
1. **Изучите основы Swift** - опционалы, closures, protocols, generics
2. **Практикуйте алгоритмы** - массивы, строки, деревья, рекурсия
3. **Готовьтесь к кодингу** - пишите код на доске или в онлайн-редакторе
4. **Изучайте архитектуру** - MVC, MVVM, VIPER, Clean Architecture

### 2. Практическая подготовка
1. **Создайте портфолио проектов** - GitHub с качественным кодом
2. **Практикуйте объяснение кода** - умение объяснить свои решения
3. **Изучайте вопросы собеседований** - LeetCode, HackerRank
4. **Готовьтесь к поведенческим вопросам** - STAR метод

### 3. День собеседования
1. **Будьте уверены в себе** - покажите энтузиазм и интерес
2. **Задавайте вопросы** - покажите интерес к компании и проекту
3. **Объясняйте ход мыслей** - говорите вслух при решении задач
4. **Будьте честны** - если не знаете ответ, скажите об этом

## 📚 Рекомендуемые ресурсы

### Книги
- "Effective Objective-C 2.0" by Matt Galloway
- "iOS Programming: The Big Nerd Ranch Guide"
- "Advanced Swift" by Chris Eidhof

### Онлайн ресурсы
- [Ray Wenderlich](https://www.raywenderlich.com/) - туториалы по iOS
- [Hacking with Swift](https://www.hackingwithswift.com/) - Swift туториалы
- [Swift.org](https://swift.org/) - официальная документация
- [Apple Developer Documentation](https://developer.apple.com/documentation/)

### Практика
- [LeetCode](https://leetcode.com/) - алгоритмические задачи
- [HackerRank](https://www.hackerrank.com/) - технические интервью
- [CodeSignal](https://codesignal.com/) - оценка навыков программирования

## ✅ Чеклист подготовки

- [ ] Изучить основы Swift (опционалы, closures, protocols)
- [ ] Практиковать алгоритмы и структуры данных
- [ ] Готовиться к кодингу на доске
- [ ] Изучить архитектурные паттерны
- [ ] Практиковать объяснение технических решений
- [ ] Готовить вопросы для интервьюера
- [ ] Создавать портфолио проектов
- [ ] Изучать инструменты разработки
- [ ] Практиковать поведенческие вопросы

## 🔄 Последнее обновление

- **Дата**: 2024-01-15
- **Источники**:
  - [Ray Wenderlich iOS Interview Questions](https://www.raywenderlich.com/594-interview-questions-for-ios-engineers)
  - [iOS Dev Interview Questions](https://github.com/ole/whats-new-in-swift-4)
  - [Technical Interview Handbook](https://techinterviewhandbook.org/)

**Совет:** Регулярно обновляйте знания, следите за новыми версиями iOS и Swift, изучайте современные практики разработки.
