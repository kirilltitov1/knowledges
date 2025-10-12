---
type: "guide"
status: "draft"
level: "intermediate"
title: "Instruments Guide"
---

# 🔍 Instruments - профилирование производительности iOS

Комплексное руководство по использованию Instruments для анализа производительности, памяти и других аспектов iOS приложений.

## 📋 Содержание
- [Запуск Instruments](#запуск-instruments)
- [Основные инструменты](#основные-инструменты)
- [Анализ памяти](#анализ-памяти)
- [Профилирование CPU](#профилирование-cpu)
- [Анализ энергопотребления](#анализ-энергопотребления)
- [Сетевой анализ](#сетевой-анализ)
- [Автоматизация профилирования](#автоматизация-профилирования)

## Запуск Instruments

### Способы запуска

#### 1. Через Xcode
```bash
# В меню Xcode: Product → Profile
# Или комбинация клавиш: Cmd + I
```

#### 2. Через Spotlight
```bash
# Найдите "Instruments" в Spotlight
# Или запустите из /Applications/Xcode.app/Contents/Applications/Instruments.app
```

#### 3. Через командную строку
```bash
# Запуск конкретного инструмента
instruments -t "Allocations" MyApp.app

# Запуск с кастомным шаблоном
instruments -t "My Custom Template" MyApp.app

# Запуск на устройстве
instruments -t "Time Profiler" -D "iPhone" MyApp.app
```

## Основные инструменты

### 1. Time Profiler

#### Назначение
Анализ производительности CPU, поиск узких мест в коде.

#### Запуск
```bash
instruments -t "Time Profiler" MyApp.app
```

#### Что анализировать
- **Hot spots** - функции, потребляющие больше всего CPU времени
- **Call trees** - цепочки вызовов функций
- **Thread activity** - активность потоков
- **Sample analysis** - детальный анализ семплов

#### Интерпретация результатов
```swift
// Красные области - горячие точки
// Зеленые области - эффективный код
// Желтые области - умеренное потребление

// Ищите:
// - Долгие операции в главном потоке
// - Чрезмерное использование CPU в фоне
// - Неэффективные алгоритмы
```

### 2. Allocations

#### Назначение
Анализ выделения и освобождения памяти.

#### Запуск
```bash
instruments -t "Allocations" MyApp.app
```

#### Ключевые метрики
- **Persistent Bytes** - память, которая не освобождается
- **Transient Bytes** - временная память
- **Total Bytes** - общее потребление памяти
- **# Persistent** - количество неосвобожденных объектов

#### Анализ утечек памяти
```bash
// В инструменте:
// 1. Найдите объекты с большим количеством persistent bytes
// 2. Проверьте call stack для понимания причины
// 3. Ищите циклы удержания в Memory Graph
```

### 3. Leaks

#### Назначение
Автоматическое обнаружение утечек памяти.

#### Запуск
```bash
instruments -t "Leaks" MyApp.app
```

#### Как работает
- Автоматически обнаруживает объекты, которые не могут быть освобождены
- Показывает цепочку владения объектом
- Указывает на точное место утечки

### 4. Memory Graph Debugger

#### Назначение
Визуализация графа объектов в памяти.

#### Запуск в Xcode
```bash
// В debug area: View → Debug Area → Activate Console
// Или кнопка "Show Memory Graph" в debug bar
```

#### Анализ графа
```swift
// Что искать:
// - Объекты, которые не должны быть в памяти
// - Циклы сильных ссылок
// - Большие цепочки владения
// - Объекты с множественными владельцами
```

## Анализ памяти

### 1. Поиск утечек памяти

#### Шаги анализа
1. Запустите приложение в Instruments с шаблоном "Leaks"
2. Взаимодействуйте с приложением для создания объектов
3. Дождитесь автоматического обнаружения утечек
4. Проанализируйте call stack утечки

#### Пример утечки
```swift
class ViewController: UIViewController {
    var timer: Timer? // ❌ Не освобождается

    override func viewDidLoad() {
        super.viewDidLoad()
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { _ in
            // Делаем что-то каждую секунду
        }
    }

    // ❌ Отсутствует очистка таймера
}

// ✅ Правильное решение
class ViewController: UIViewController {
    var timer: Timer?

    override func viewDidLoad() {
        super.viewDidLoad()
        startTimer()
    }

    func startTimer() {
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            self?.timerFired()
        }
    }

    func timerFired() {
        // Обработка таймера
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        timer?.invalidate() // ✅ Освобождаем таймер
        timer = nil
    }
}
```

### 2. Анализ потребления памяти

#### Мониторинг памяти в реальном времени
```swift
class MemoryMonitor {
    private var timer: Timer?

    func startMonitoring() {
        timer = Timer.scheduledTimer(withTimeInterval: 5.0, repeats: true) { _ in
            self.logMemoryUsage()
        }
    }

    func stopMonitoring() {
        timer?.invalidate()
        timer = nil
    }

    private func logMemoryUsage() {
        let memoryUsage = getMemoryUsage()
        print("Memory usage: \(memoryUsage) MB")
    }

    private func getMemoryUsage() -> Double {
        var taskInfo = mach_task_basic_info()
        var count = mach_msg_type_number_t(MemoryLayout<mach_task_basic_info>.size)/4

        let kerr: kern_return_t = withUnsafeMutablePointer(to: &taskInfo) {
            $0.withMemoryRebound(to: integer_t.self, capacity: 1) {
                task_info(mach_task_self_, task_flavor_t(MACH_TASK_BASIC_INFO), $0, &count)
            }
        }

        return kerr == KERN_SUCCESS ? Double(taskInfo.resident_size) / 1024.0 / 1024.0 : 0
    }
}
```

### 3. Анализ роста памяти

#### Шаги анализа
1. Запустите Allocations инструмент
2. Мониторьте график памяти во времени
3. Ищите линейный рост (признак утечки)
4. Анализируйте аллокации по типам объектов

## Профилирование CPU

### 1. Time Profiler анализ

#### Запуск и настройка
```bash
instruments -t "Time Profiler" \
    -D "iPhone 15" \
    -e CPU_PROFILER_SAMPLING_INTERVAL 1ms \
    MyApp.app
```

#### Анализ результатов
- **Self Weight** - время, проведенное в функции
- **Total Weight** - время в функции + подфункциях
- **Symbol Name** - имя функции/метода

#### Поиск проблем
```swift
// Ищите функции с высоким Self Weight
// Особенно в главном потоке

// Признаки проблем:
// - Высокое потребление CPU в UI потоке
// - Долгие операции синхронизации
// - Неэффективные алгоритмы
```

### 2. System Trace

#### Назначение
Детальный анализ системных вызовов и активности потоков.

#### Запуск
```bash
instruments -t "System Trace" MyApp.app
```

#### Что анализировать
- **Thread states** - состояния потоков (running, blocked, waiting)
- **System calls** - системные вызовы
- **CPU usage by thread** - потребление CPU по потокам
- **I/O activity** - активность ввода-вывода

### 3. Оптимизация CPU использования

#### Пример оптимизации
```swift
// ❌ Неэффективный код
func processLargeArray() {
    let array = Array(0..<100000)

    for i in 0..<array.count {
        for j in 0..<array.count {
            if array[i] + array[j] == target {
                return (i, j)
            }
        }
    }
    return nil
}

// ✅ Оптимизированный код
func processLargeArrayOptimized() {
    let array = Array(0..<100000)
    var valueToIndex = [Int: Int]()

    // O(n) вместо O(n²)
    for (index, value) in array.enumerated() {
        let complement = target - value
        if let complementIndex = valueToIndex[complement] {
            return (complementIndex, index)
        }
        valueToIndex[value] = index
    }
    return nil
}
```

## Анализ энергопотребления

### 1. Energy Impact

#### Назначение
Анализ энергопотребления приложения.

#### Запуск
```bash
instruments -t "Energy Log" MyApp.app
```

#### Метрики энергопотребления
- **CPU Usage** - потребление процессора
- **Network Activity** - сетевая активность
- **Location Services** - сервисы геолокации
- **Display Brightness** - яркость экрана
- **Background App Refresh** - обновление в фоне

### 2. Power Consumption Analysis

#### Что мониторить
```bash
// Высокое энергопотребление указывает на:
// - Чрезмерное использование CPU
// - Частые сетевые запросы
// - Постоянное использование геолокации
// - Высокая яркость экрана
// - Частое обновление в фоне
```

#### Оптимизация энергопотребления
```swift
class PowerOptimizedManager {
    private var backgroundTask: UIBackgroundTaskIdentifier = .invalid
    private let locationManager = CLLocationManager()

    func startOptimizedLocationUpdates() {
        // Используем значимые изменения вместо постоянного мониторинга
        locationManager.startMonitoringSignificantLocationChanges()

        // Ограничиваем обновления в фоне
        backgroundTask = UIApplication.shared.beginBackgroundTask { [weak self] in
            self?.endBackgroundTask()
        }
    }

    func endBackgroundTask() {
        if backgroundTask != .invalid {
            UIApplication.shared.endBackgroundTask(backgroundTask)
            backgroundTask = .invalid
        }
    }

    func optimizeNetworkRequests() {
        // Пакетируем сетевые запросы
        // Используем фоновые сессии
        // Ограничиваем частоту запросов
    }
}
```

## Сетевой анализ

### 1. Network инструмент

#### Назначение
Анализ сетевой активности приложения.

#### Запуск
```bash
instruments -t "Network" MyApp.app
```

#### Метрики для анализа
- **Request/Response time** - время запросов и ответов
- **Data throughput** - пропускная способность
- **Connection establishment** - время установления соединений
- **TLS handshake** - рукопожатие SSL

### 2. HTTP Traffic

#### Анализ трафика
```bash
// Что анализировать:
// - Размер запросов и ответов
// - Время выполнения запросов
// - Количество параллельных соединений
// - Эффективность кеширования
```

#### Оптимизация сети
```swift
class NetworkOptimizer {
    private let session: URLSession

    init() {
        let configuration = URLSessionConfiguration.default
        configuration.httpMaximumConnectionsPerHost = 6 // Ограничиваем соединения
        configuration.timeoutIntervalForRequest = 30.0
        configuration.requestCachePolicy = .returnCacheDataElseLoad

        session = URLSession(configuration: configuration)
    }

    func optimizedRequest() {
        // Пакетируем запросы
        // Используем HTTP/2 multiplexing
        // Настраиваем таймауты
    }
}
```

## Автоматизация профилирования

### 1. Кастомные инструменты

#### Создание кастомного шаблона Instruments
```bash
# Создание шаблона
instruments -t "Custom Template" -saveAs "MyApp Performance.tracetemplate"

# Шаблон включает:
// - Time Profiler
// - Allocations
// - Network
// - Energy Log
```

### 2. Автоматизированные тесты производительности

```swift
class PerformanceTests: XCTestCase {
    func testAppLaunchPerformance() {
        let app = XCUIApplication()

        measure {
            app.launch()
        }
    }

    func testDataLoadingPerformance() {
        let app = XCUIApplication()

        app.launch()

        measure {
            app.buttons["Load Data"].tap()
            // Ждем завершения загрузки
            XCTAssertTrue(app.staticTexts["Data Loaded"].waitForExistence(timeout: 5.0))
        }
    }
}
```

### 3. CI/CD интеграция

```yaml
# .github/workflows/performance.yml
name: Performance Tests

on: [push, pull_request]

jobs:
  performance:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run performance tests
        run: |
          xcodebuild test \
            -workspace MyApp.xcworkspace \
            -scheme MyApp \
            -configuration Release \
            -destination 'platform=iOS Simulator,name=iPhone 15' \
            -enablePerformanceTests YES
```

## Заключение

Instruments — мощный инструмент для анализа производительности iOS приложений. Эффективное использование помогает:

1. **Находить узкие места** в производительности
2. **Обнаруживать утечки памяти** автоматически
3. **Оптимизировать энергопотребление**
4. **Анализировать сетевую активность**
5. **Автоматизировать мониторинг** в CI/CD

Помните: "Измеряй дважды, оптимизируй один раз."

## Ссылки
- [Instruments User Guide](https://developer.apple.com/library/archive/documentation/DeveloperTools/Conceptual/InstrumentsUserGuide/)
- [WWDC: Instruments](https://developer.apple.com/videos/play/wwdc2018/410/)
- [Performance Best Practices](https://developer.apple.com/documentation/xcode/improving-your-app-s-performance)
- [Memory Management Guide](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/MemoryMgmt/Articles/MemoryMgmt.html)
