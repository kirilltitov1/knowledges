---
type: "quiz"
status: "draft"
summary: ""
title: "Memory Management Quiz"
---

# 🧠 Викторина по управлению памятью в iOS

Тестирование знаний по ARC, retain cycles, memory management и оптимизации памяти в iOS приложениях.

## 📋 Инструкции

- **Время выполнения**: 30 минут
- **Количество вопросов**: 20
- **Пассовый балл**: 80% (16 правильных ответов)
- **Формат**: Множественный выбор + практические задания

## 🎯 Раздел 1: Теоретические вопросы

### Вопрос 1: Что такое ARC?
- [ ] A) Automatic Resource Control
- [x] B) Automatic Reference Counting
- [ ] C) Advanced Runtime Compiler
- [ ] D) Async Resource Controller

### Вопрос 2: Что происходит при создании retain cycle?
- [ ] A) Объекты удаляются из памяти быстрее
- [x] B) Объекты никогда не удаляются из памяти
- [ ] C) Увеличивается производительность приложения
- [ ] D) Уменьшается потребление памяти

### Вопрос 3: Когда нужно использовать weak ссылки?
- [ ] A) Всегда для всех свойств класса
- [ ] B) Только для опциональных свойств
- [x] C) Для делегатов и замыканий, которые могут создать цикл удержания
- [ ] D) Только для констант

### Вопрос 4: Что делает @autoreleasepool?
- [ ] A) Увеличивает скорость выполнения кода
- [ ] B) Создает дополнительную память для объектов
- [x] C) Контролирует время жизни временных объектов
- [ ] D) Оптимизирует работу с базами данных

### Вопрос 5: Чем отличается strong от weak ссылки?
- [ ] A) Strong ссылки медленнее, weak быстрее
- [ ] B) Strong ссылки опциональные, weak нет
- [x] C) Strong ссылки влияют на время жизни объекта, weak нет
- [ ] D) Strong ссылки только для классов, weak для структур

## 🔧 Раздел 2: Практические задания

### Задание 1: Найдите retain cycle

```swift
class ViewController: UIViewController {
    var dataManager: DataManager?

    override func viewDidLoad() {
        super.viewDidLoad()
        dataManager = DataManager()

        // Найдите проблему в этом коде
        dataManager?.completionHandler = { [weak self] in
            self?.updateUI() // Потенциальный цикл удержания
        }
    }

    func updateUI() {
        // Обновление интерфейса
    }
}

class DataManager {
    var completionHandler: (() -> Void)? // strong ссылка
}
```

**Вопрос**: Как исправить retain cycle?
- [x] A) Использовать `[weak self]` в замыкании
- [ ] B) Использовать `[unowned self]` в замыкании
- [ ] C) Сделать `completionHandler` weak свойством
- [ ] D) Удалить замыкание

### Задание 2: Оптимизация памяти

```swift
class ImageProcessor {
    var largeImage: UIImage?

    func processImages(_ urls: [URL]) {
        for url in urls {
            largeImage = UIImage(contentsOfFile: url.path)
            processImage(largeImage!)
            // largeImage остается в памяти после цикла
        }
    }
}
```

**Вопрос**: Как оптимизировать потребление памяти?
- [ ] A) Использовать более быструю обработку
- [x] B) Использовать @autoreleasepool в цикле
- [ ] C) Увеличить размер стека
- [ ] D) Использовать более слабые ссылки

### Задание 3: Правильное использование ссылок

```swift
class NetworkManager {
    var delegate: NetworkManagerDelegate?

    func fetchData() {
        // Загрузка данных
        delegate?.didFinishLoading(data)
    }
}

protocol NetworkManagerDelegate: AnyObject {
    func didFinishLoading(_ data: Data)
}

class ViewController: UIViewController, NetworkManagerDelegate {
    let networkManager = NetworkManager()

    override func viewDidLoad() {
        super.viewDidLoad()
        networkManager.delegate = self // Какая ссылка здесь используется?
    }

    func didFinishLoading(_ data: Data) {
        // Обработка данных
    }
}
```

**Вопрос**: Какая ссылка используется для делегата?
- [x] A) strong (может создать цикл удержания)
- [ ] B) weak (безопасно)
- [ ] C) unowned (может вызвать crash)
- [ ] D) optional (не влияет на память)

## 🧪 Раздел 3: Задачи на исправление кода

### Задача 1: Исправьте retain cycle

**Исходный код:**
```swift
class A {
    var b: B?

    init() {
        b = B()
        b?.a = self // ❌ Создает цикл удержания
    }

    deinit {
        print("A deinitialized")
    }
}

class B {
    var a: A? // strong ссылка

    deinit {
        print("B deinitialized")
    }
}
```

**Исправленный код:**
```swift
class A {
    var b: B?

    init() {
        b = B()
        b?.a = self
    }

    deinit {
        print("A deinitialized")
    }
}

class B {
    weak var a: A? // ✅ weak ссылка разрывает цикл

    deinit {
        print("B deinitialized")
    }
}
```

### Задача 2: Оптимизируйте память в цикле

**Исходный код:**
```swift
func processManyItems(_ items: [Item]) {
    for item in items {
        let data = loadData(for: item) // Создает много временных объектов
        processData(data)
    }
    // Временные объекты остаются в памяти до конца метода
}
```

**Оптимизированный код:**
```swift
func processManyItems(_ items: [Item]) {
    for item in items {
        @autoreleasepool { // ✅ Контролирует время жизни объектов
            let data = loadData(for: item)
            processData(data)
        } // Пул сбрасывается, память освобождается
    }
}
```

## 📊 Раздел 4: Вопросы по инструментам диагностики

### Вопрос 6: Какой инструмент лучше всего подходит для поиска retain cycles?
- [ ] A) Time Profiler
- [x] B) Memory Graph Debugger
- [ ] C) System Trace
- [ ] D) Network

### Вопрос 7: Что показывает Instruments - Allocations?
- [ ] A) Только утечки памяти
- [x] B) Выделение и освобождение памяти
- [ ] C) Только производительность CPU
- [ ] D) Только сетевые запросы

### Вопрос 8: Как запустить Memory Graph Debugger?
- [ ] A) Product → Profile → Memory
- [ ] B) Debug → Attach to Process
- [x] C) Debug → Debug Workflow → View Memory Graph Hierarchy
- [ ] D) Window → Devices and Simulators

## 🎯 Раздел 5: Продвинутые вопросы

### Вопрос 9: Что такое Protocol Witness Table?
- [ ] A) Таблица для хранения объектов
- [ ] B) Таблица для управления памятью
- [x] C) Таблица методов для реализации протокола
- [ ] D) Таблица для сетевых соединений

### Вопрос 10: Когда нужно использовать unowned вместо weak?
- [ ] A) Всегда, когда возможно
- [ ] B) Никогда, weak всегда лучше
- [x] C) Когда объект точно не будет nil во время доступа
- [ ] D) Только для опциональных свойств

## 📝 Практическое задание: Анализ кода

Проанализируйте следующий код и найдите все проблемы с памятью:

```swift
class ViewController: UIViewController {
    var timer: Timer?
    var dataService: DataService?

    override func viewDidLoad() {
        super.viewDidLoad()
        setupTimer()
        dataService = DataService()
    }

    func setupTimer() {
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            self?.dataService?.fetchData { data in
                self?.updateUI(with: data) // Множественные сильные ссылки
            }
        }
    }

    func updateUI(with data: Data) {
        // Обновление интерфейса
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        timer?.invalidate()
        // timer не обнуляется
    }
}
```

**Вопросы:**
1. Сколько потенциальных проблем с памятью вы нашли?
2. Как исправить каждую проблему?

## 🏆 Оценка результатов

### Отлично (18-20 правильных ответов)
- Глубокое понимание ARC и управления памятью
- Умение применять знания на практике
- Знание инструментов диагностики

### Хорошо (15-17 правильных ответов)
- Хорошее понимание основных концепций
- Нужно попрактиковаться в применении знаний

### Удовлетворительно (12-14 правильных ответов)
- Базовое понимание, но есть пробелы
- Нужно изучить практические аспекты

### Нужно улучшить (менее 12 правильных ответов)
- Требуется дополнительное изучение темы
- Рекомендуется изучить теоретические основы

## 📚 Рекомендации для изучения

### Если результат ниже ожидаемого:
1. Изучите [[iOS/Memory/arc-mrc|ARC vs MRC]] - теоретические основы
2. Попрактикуйтесь с [[iOS/Memory/memory-management-practical-guide|практическим руководством]]
3. Поэкспериментируйте с Memory Graph Debugger в Xcode

### Для углубления знаний:
1. Изучите [[iOS/Concurrency & Multithreading/4-swift-concurrency-modern-approach|Swift Concurrency]]
2. Освойте [[iOS/Tooling & Project Setup/xcode-integration-guide|инструменты разработки]]
3. Изучите [[iOS/Debugging/memory-debugging|отладку памяти]]

## 🔄 Повторное прохождение

Рекомендуется проходить викторину каждые 3 месяца для закрепления знаний и отслеживания прогресса.

**Последнее обновление:** 2024-01-15
**Версия:** 1.0
**Источники:** Официальная документация Apple, WWDC сессии
