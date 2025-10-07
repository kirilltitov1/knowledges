---
title: Практическое руководство по управлению памятью в iOS
type: guide
topics: [Memory Management, ARC, Performance]
subtopic: memory-management
status: draft
level: intermediate
platforms: [iOS, macOS, watchOS, tvOS]
ios_min: "10.0"
duration: 90m
tags: [memory-management, arc, retain-cycles, memory-leaks, performance-optimization, instruments]
---

# Практическое руководство по управлению памятью в iOS

Комплексное руководство по эффективному управлению памятью в iOS приложениях с практическими примерами и инструментами диагностики.

## 📋 Содержание
- [Основы управления памятью](#основы-управления-памятью)
- [Типичные проблемы с памятью](#типичные-проблемы-с-памятью)
- [Инструменты диагностики](#инструменты-диагностики)
- [Оптимизация памяти](#оптимизация-памяти)
- [Best Practices](#best-practices)
- [Примеры кода](#примеры-кода)

## Основы управления памятью

### ARC (Automatic Reference Counting)

**ARC** автоматически управляет памятью, вставляя вызовы `retain`, `release` и `autorelease` во время компиляции.

```swift
class ViewController: UIViewController {
    var dataManager: DataManager? // strong reference

    override func viewDidLoad() {
        super.viewDidLoad()
        dataManager = DataManager() // reference count = 1
        dataManager?.loadData()
    }

    deinit {
        print("ViewController deinitialized")
    }
}

class DataManager {
    var networkService: NetworkService? // strong reference

    init() {
        networkService = NetworkService() // reference count = 1
    }

    deinit {
        print("DataManager deinitialized")
    }
}
```

### Сильные и слабые ссылки

```swift
class ViewController: UIViewController {
    @IBOutlet weak var label: UILabel! // weak reference для outlet
    var dataManager: DataManager? // strong reference

    // Делегат - слабая ссылка для избежания цикла удержания
    weak var delegate: DataManagerDelegate?
}
```

## Типичные проблемы с памятью

### 1. Циклы удержания (Retain Cycles)

#### Проблема
```swift
class A {
    var b: B?
    deinit { print("A deinitialized") }
}

class B {
    var a: A? // strong reference создает цикл
    deinit { print("B deinitialized") }
}

let a = A()
let b = B()
a.b = b
b.a = a

// Ни один объект не будет удален!
```

#### Решение
```swift
class B {
    weak var a: A? // weak reference разрывает цикл
    deinit { print("B deinitialized") }
}
```

### 2. Циклы удержания с замыканиями

#### Проблема
```swift
class ViewController: UIViewController {
    var handler: (() -> Void)?

    override func viewDidLoad() {
        super.viewDidLoad()

        // Цикл удержания: self → handler → self
        handler = { [weak self] in
            self?.updateUI() // strong capture self
        }
    }
}
```

#### Решения
```swift
// Вариант 1: weak self
handler = { [weak self] in
    self?.updateUI()
}

// Вариант 2: unowned self (если уверены, что self не будет nil)
handler = { [unowned self] in
    self.updateUI()
}

// Вариант 3: захват конкретных свойств
handler = { [weak label = self.label] in
    label?.text = "Updated"
}
```

### 3. Большие объекты в памяти

#### Проблема: UIImage в памяти
```swift
class ImageProcessor {
    var largeImage: UIImage? // может храниться в памяти долго

    func processImage() {
        largeImage = UIImage(data: largeData) // большой объект в памяти
        // Обработка изображения
    }
}
```

#### Решение
```swift
class ImageProcessor {
    func processImage() -> UIImage? {
        // Создаем изображение только когда нужно
        guard let largeData = getImageData() else { return nil }

        let image = UIImage(data: largeData)
        defer {
            // Очищаем данные после использования
            largeData = nil
        }

        return image?.processedVersion()
    }
}
```

## Инструменты диагностики

### 1. Memory Graph Debugger

#### Запуск
1. Запустите приложение в Xcode
2. В меню: Debug → Debug Workflow → View Memory Graph Hierarchy
3. Или используйте кнопку в debug area

#### Что искать
- Объекты, которые не должны быть в памяти
- Цепочки сильных ссылок
- Большие объекты данных

### 2. Instruments - Allocations

#### Запуск
1. Product → Profile
2. Выберите "Allocations" или "Leaks"
3. Запустите приложение

#### Ключевые метрики
- **Persistent Bytes**: память, которая не освобождается
- **Transient Bytes**: временная память
- **Total Bytes**: общее потребление памяти

### 3. Xcode Memory Debugger

#### Запуск
1. В debug bar нажмите на кнопку памяти
2. Или: Debug → Debug Workflow → View Debugging → View Memory

#### Полезные команды
```swift
// В консоли LLDB
malloc_history(pid, address)  // История выделения памяти
vmmap(pid)                    // Карта виртуальной памяти
```

## Оптимизация памяти

### 1. Lazy Loading

```swift
class DataManager {
    private var _expensiveData: ExpensiveData?

    var expensiveData: ExpensiveData? {
        if _expensiveData == nil {
            _expensiveData = loadExpensiveData() // Загружаем только когда нужно
        }
        return _expensiveData
    }

    private func loadExpensiveData() -> ExpensiveData {
        // Дорогая операция загрузки
        return ExpensiveData()
    }
}
```

### 2. NSCache для кеширования

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

### 3. @autoreleasepool в циклах

```swift
func processManyImages() {
    let urls = getImageURLs()

    for url in urls {
        @autoreleasepool {
            if let image = UIImage(contentsOfFile: url.path) {
                processImage(image)
            }
        } // Пул сбрасывается, память освобождается
    }
}
```

### 4. Оптимизация коллекций

```swift
// Вместо NSMutableArray используйте Swift коллекции
var items = [Item]() // Более эффективно чем NSMutableArray

// Для больших данных используйте lazy collections
let largeData = (0..<1000000).lazy.map { Item(value: $0) }

// Избегайте копирования больших структур
func process(_ data: [Item]) {
    // Не создавайте копии если не нужно
    data.forEach { processItem($0) }
}
```

## Best Practices

### 1. Управление памятью в View Controllers

```swift
class MyViewController: UIViewController {
    private var dataManager: DataManager?
    private var timer: Timer?

    override func viewDidLoad() {
        super.viewDidLoad()
        dataManager = DataManager()
        setupTimer()
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        timer?.invalidate() // Освобождаем ресурсы
        timer = nil
    }

    deinit {
        print("MyViewController deinitialized")
    }
}
```

### 2. Обработка памяти в многопоточности

```swift
class ThreadSafeManager {
    private let queue = DispatchQueue(label: "com.app.datamanager")
    private var _data: [String: Any] = [:]

    func updateData(_ data: [String: Any]) {
        queue.async { [weak self] in
            self?._data = data
        }
    }

    func getData() -> [String: Any] {
        return queue.sync {
            return _data
        }
    }
}
```

### 3. Обработка больших данных

```swift
class FileProcessor {
    func processLargeFile(at url: URL) {
        guard let handle = FileHandle(forReadingAtPath: url.path) else {
            return
        }

        defer {
            try? handle.close() // Всегда закрываем файл
        }

        // Обрабатываем файл порциями
        while let chunk = try? handle.read(upToCount: 1024) {
            processChunk(chunk)

            // Периодически освобождаем память
            if chunk.count > 10000 {
                @autoreleasepool {
                    // Обработка больших данных
                }
            }
        }
    }
}
```

## Примеры кода

### Пример 1: Singleton с правильным управлением памятью

```swift
class NetworkManager {
    static let shared = NetworkManager()
    private var currentTask: URLSessionTask?

    private init() {
        // Приватный инициализатор для singleton
    }

    func fetchData(completion: @escaping (Data?) -> Void) {
        currentTask?.cancel() // Отменяем предыдущий запрос

        let task = URLSession.shared.dataTask(with: APIEndpoint.data.url) { [weak self] data, response, error in
            // Обработка ответа
            completion(data)
            self?.currentTask = nil // Освобождаем ссылку
        }

        currentTask = task
        task.resume()
    }
}
```

### Пример 2: ViewModel с памятью

```swift
class UserProfileViewModel {
    private let userService: UserService
    private var cancellables = Set<AnyCancellable>()

    @Published private(set) var user: User?
    @Published private(set) var isLoading = false

    init(userService: UserService = UserService.shared) {
        self.userService = userService

        // Подписываемся на изменения
        $user
            .receive(on: DispatchQueue.main)
            .sink { [weak self] user in
                self?.updateUI(with: user)
            }
            .store(in: &cancellables)
    }

    func loadUser(id: String) {
        isLoading = true

        userService.fetchUser(id: id)
            .receive(on: DispatchQueue.main)
            .sink { [weak self] completion in
                self?.isLoading = false
                // Обработка completion
            } receiveValue: { [weak self] user in
                self?.user = user
            }
            .store(in: &cancellables)
    }

    deinit {
        cancellables.removeAll()
    }
}
```

## Распространенные ошибки

### 1. Не освобожденные ресурсы

```swift
// ❌ Неправильно
class FileManager {
    var fileHandle: FileHandle?

    func openFile() {
        fileHandle = FileHandle(forWritingAtPath: path) // Не закрыт
    }
}

// ✅ Правильно
class FileManager {
    func openFile() -> FileHandle? {
        return FileHandle(forWritingAtPath: path)
    }

    func processFile() {
        guard let handle = openFile() else { return }
        defer {
            try? handle.close() // Всегда закрываем
        }
        // Обрабатываем файл
    }
}
```

### 2. Неправильное использование weak/unowned

```swift
// ❌ Неправильно - unowned когда объект может быть nil
class ViewController: UIViewController {
    var handler: (() -> Void)?

    override func viewDidLoad() {
        super.viewDidLoad()

        NetworkManager.shared.fetchData { [unowned self] data in
            self.updateUI() // crash если self уже освобожден
        }
    }
}

// ✅ Правильно - weak для опционального доступа
class ViewController: UIViewController {
    var handler: (() -> Void)?

    override func viewDidLoad() {
        super.viewDidLoad()

        NetworkManager.shared.fetchData { [weak self] data in
            self?.updateUI() // безопасно, если self nil то ничего не делаем
        }
    }
}
```

## Производительность

### Измерение потребления памяти

```swift
class MemoryMonitor {
    func startMonitoring() {
        Timer.scheduledTimer(withTimeInterval: 5.0, repeats: true) { _ in
            let memoryUsage = self.getMemoryUsage()
            print("Memory usage: \(memoryUsage) MB")
        }
    }

    private func getMemoryUsage() -> Float {
        var taskInfo = mach_task_basic_info()
        var count = mach_msg_type_number_t(MemoryLayout<mach_task_basic_info>.size)/4

        let kerr: kern_return_t = withUnsafeMutablePointer(to: &taskInfo) {
            $0.withMemoryRebound(to: integer_t.self, capacity: 1) {
                task_info(mach_task_self_, task_flavor_t(MACH_TASK_BASIC_INFO), $0, &count)
            }
        }

        return kerr == KERN_SUCCESS ? Float(taskInfo.resident_size) / 1024.0 / 1024.0 : 0
    }
}
```

### Мониторинг в Instruments

1. **Allocations**: отслеживание выделения памяти
2. **Leaks**: поиск утечек памяти
3. **VM Tracker**: отслеживание виртуальной памяти
4. **Memory**: общий мониторинг памяти

## Заключение

Эффективное управление памятью - ключевой аспект создания производительных iOS приложений. Основные принципы:

1. **Избегайте циклов удержания** используя weak/unowned ссылки
2. **Освобождайте ресурсы timely** с помощью defer и cleanup кода
3. **Используйте lazy loading** для дорогих ресурсов
4. **Мониторьте память** регулярно с помощью Instruments
5. **Оптимизируйте большие операции** с помощью @autoreleasepool

Помните: "Память - это ресурс, который нужно уважать и эффективно использовать."

## Ссылки
- [WWDC: Understanding Swift Performance](https://developer.apple.com/videos/play/wwdc2016/416/)
- [Memory Management in Swift](https://developer.apple.com/documentation/swift/memory_management)
- [Instruments User Guide](https://developer.apple.com/library/archive/documentation/DeveloperTools/Conceptual/InstrumentsUserGuide/)
