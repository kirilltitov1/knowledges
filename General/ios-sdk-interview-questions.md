---
title: Вопросы по iOS SDK и фреймворкам для собеседований
type: guide
topics: [iOS SDK, Frameworks, Interview Preparation]
subtopic: ios-sdk-questions
status: draft
level: intermediate
platforms: [iOS, macOS, watchOS, tvOS]
ios_min: "10.0"
duration: 90m
tags: [ios-sdk, frameworks, uikit, core-data, networking, graphics, interview-questions]
---

# 📱 Вопросы по iOS SDK и фреймворкам для собеседований

Комплексный сборник вопросов по основным фреймворкам iOS SDK, часто встречающихся на технических собеседованиях разработчиков.

## 📋 Структура вопросов по фреймворкам

### 🎯 Основные категории
- **UI Frameworks** - UIKit, SwiftUI, Core Graphics
- **Data Management** - Core Data, Foundation, File System
- **Networking** - URLSession, Network, Bonjour
- **Media** - AVFoundation, Photos, Camera
- **Location & Maps** - Core Location, MapKit
- **Graphics & Animation** - Core Animation, Metal, SceneKit
- **Security** - Keychain, Local Authentication, CryptoKit

## 🖼️ UI Frameworks

### UIKit

#### Базовые концепции
**Вопрос:** Объясните иерархию UIViewController.

**Ответ:**
```
UIResponder (базовый класс)
├── UIViewController
    ├── UINavigationController
    ├── UITabBarController
    ├── UISplitViewController
    └── UITableViewController
```

**Вопрос:** Что такое responder chain?

**Ответ:** Responder chain - механизм маршрутизации событий (touch, keyboard) от дочерних view к родительским, пока не найдется обработчик.

**Вопрос:** Объясните разницу между frame и bounds.

**Ответ:**
- **frame**: позиция и размер view в координатах superview
- **bounds**: позиция и размер view в собственной системе координат

#### Auto Layout и Constraints
**Вопрос:** Что такое intrinsic content size?

**Ответ:** Intrinsic content size - размер, который view "хочет" иметь для правильного отображения контента (например, UILabel с текстом).

**Вопрос:** Объясните constraint priorities.

**Ответ:**
- **Required (1000)**: обязательные constraints
- **High (750)**: важные, но могут быть нарушены
- **Low (250)**: могут быть легко нарушены

#### View Lifecycle
**Вопрос:** Назовите основные методы жизненного цикла UIViewController.

**Ответ:**
```swift
// Инициализация
init(coder:) или init(nibName:bundle:)

// Загрузка view
loadView()
viewDidLoad()

// Появление на экране
viewWillAppear()
viewDidAppear()

// Исчезновение с экрана
viewWillDisappear()
viewDidDisappear()

// Освобождение памяти
deinit
```

**Вопрос:** Когда вызывается viewWillLayoutSubviews()?

**Ответ:** Перед каждым пересчетом layout'а view и subviews.

### SwiftUI

#### Базовые концепции
**Вопрос:** Что такое @State и @Binding?

**Ответ:**
- **@State**: источник истины для простых значений в view
- **@Binding**: ссылка на @State из другого view для двусторонней синхронизации

**Вопрос:** Объясните разницу между @ObservedObject и @StateObject.

**Ответ:**
- **@StateObject**: создает и владеет ObservableObject
- **@ObservedObject**: наблюдает за существующим ObservableObject

#### Layout System
**Вопрос:** Что такое VStack, HStack, ZStack?

**Ответ:** Контейнеры для вертикального, горизонтального и наложенного размещения контента.

**Вопрос:** Объясните модификаторы в SwiftUI.

**Ответ:** Модификаторы - методы, возвращающие модифицированную копию view для цепочки вызовов.

## 💾 Data Management

### Core Data

#### Базовые концепции
**Вопрос:** Что такое NSManagedObjectContext?

**Ответ:** NSManagedObjectContext - "scratchpad" для работы с managed объектами. Изменения в контексте не сохраняются автоматически в persistent store.

**Вопрос:** Объясните разницу между main context и background context.

**Ответ:**
- **Main context**: работает в главном потоке, используется для UI
- **Background context**: работает в фоновом потоке, используется для тяжелых операций

#### Модели данных
**Вопрос:** Что такое entity в Core Data?

**Ответ:** Entity - описание типа данных, аналогичное таблице в базе данных. Содержит attributes и relationships.

**Вопрос:** Объясните relationships в Core Data.

**Ответ:**
- **To-One**: один объект связан с другим
- **To-Many**: один объект связан с множеством других
- **Inverse relationships**: двусторонние связи

#### Запросы и фильтрация
**Вопрос:** Что такое NSFetchRequest?

**Ответ:** NSFetchRequest - запрос для получения данных из Core Data с возможностью фильтрации, сортировки и пагинации.

**Вопрос:** Объясните NSPredicate.

**Ответ:** NSPredicate - механизм фильтрации данных в Core Data с использованием форматных строк или блоков.

```swift
// Пример NSPredicate
let predicate = NSPredicate(format: "age > %@ AND name CONTAINS %@", argumentArray: [18, "John"])
fetchRequest.predicate = predicate
```

### Foundation

#### Коллекции
**Вопрос:** Объясните разницу между Array и NSArray.

**Ответ:**
- **Array**: value type, immutable semantics, современный Swift
- **NSArray**: reference type, mutable, Objective-C compatible

**Вопрос:** Что такое copy-on-write для Swift коллекций?

**Ответ:** Copy-on-write - оптимизация, при которой копирование происходит только при модификации shared экземпляра.

#### Строки и данные
**Вопрос:** Что такое NSString и как он взаимодействует с Swift String?

**Ответ:** NSString - Objective-C класс для строк. Swift String автоматически bridge'ается с NSString при необходимости.

**Вопрос:** Объясните NSData и Data в Swift.

**Ответ:**
- **NSData**: Objective-C класс для бинарных данных
- **Data**: Swift struct для бинарных данных с value semantics

## 🛜 Networking

### URLSession

#### Базовые концепции
**Вопрос:** Что такое URLSession и как его использовать?

**Ответ:** URLSession - основной API для сетевых запросов в iOS.

```swift
let session = URLSession.shared
let task = session.dataTask(with: url) { data, response, error in
    // Обработка ответа
}
task.resume()
```

**Вопрос:** Объясните разницу между data task, download task и upload task.

**Ответ:**
- **Data task**: для получения данных в память
- **Download task**: для скачивания файлов на диск
- **Upload task**: для отправки данных на сервер

#### Конфигурация
**Вопрос:** Что такое URLSessionConfiguration?

**Ответ:** URLSessionConfiguration определяет поведение сессии (кеширование, таймауты, аутентификация).

```swift
let config = URLSessionConfiguration.default
config.timeoutIntervalForRequest = 30
config.requestCachePolicy = .reloadIgnoringLocalCacheData

let session = URLSession(configuration: config)
```

### Network Framework

#### Современный подход
**Вопрос:** Что такое Network framework (NWConnection)?

**Ответ:** Network framework - современный низкоуровневый API для сетевого взаимодействия, альтернатива URLSession для кастомных протоколов.

**Вопрос:** Объясните WebSocket в контексте iOS.

**Ответ:** WebSocket - протокол для двусторонней связи между клиентом и сервером.

```swift
let connection = NWConnection(host: "ws://echo.websocket.org", port: 80, using: .ws)
connection.start(queue: .main)
```

## 🎬 Media Frameworks

### AVFoundation

#### Аудио и видео
**Вопрос:** Что такое AVPlayer и как его использовать?

**Ответ:** AVPlayer - класс для воспроизведения аудио и видео контента.

```swift
let player = AVPlayer(url: videoURL)
let playerLayer = AVPlayerLayer(player: player)
view.layer.addSublayer(playerLayer)

player.play()
```

**Вопрос:** Объясните разницу между AVAudioPlayer и AVPlayer для аудио.

**Ответ:**
- **AVAudioPlayer**: простой плеер для локальных аудиофайлов
- **AVPlayer**: более гибкий плеер для стриминга и сложных сценариев

#### Захват медиа
**Вопрос:** Что такое AVCaptureSession?

**Ответ:** AVCaptureSession - центральный класс для захвата фото/видео с камеры или микрофона.

```swift
let session = AVCaptureSession()
session.sessionPreset = .high

// Добавление устройств ввода
let camera = AVCaptureDevice.default(for: .video)
let input = try AVCaptureDeviceInput(device: camera)
session.addInput(input)

// Добавление вывода
let output = AVCaptureMovieFileOutput()
session.addOutput(output)
```

### Photos Framework

#### Работа с галереей
**Вопрос:** Что такое PHAsset и как получить доступ к фото?

**Ответ:** PHAsset представляет фото или видео в галерее устройства.

```swift
// Запрос доступа к галерее
PHPhotoLibrary.requestAuthorization { status in
    if status == .authorized {
        // Доступ разрешен
        let assets = PHAsset.fetchAssets(with: .image, options: nil)
    }
}
```

**Вопрос:** Объясните PHImageManager.

**Ответ:** PHImageManager отвечает за загрузку изображений из PHAsset с различными размерами и опциями.

## 📍 Location & Maps

### Core Location

#### Геолокация
**Вопрос:** Что такое CLLocationManager?

**Ответ:** CLLocationManager - основной класс для получения геолокационных данных.

```swift
class LocationManager: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyBest
    }

    func requestLocation() {
        manager.requestWhenInUseAuthorization()
        manager.startUpdatingLocation()
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.last else { return }
        print("Location: \(location.coordinate)")
    }
}
```

**Вопрос:** Объясните разницу между значимыми изменениями локации и постоянным мониторингом.

**Ответ:**
- **Значимые изменения**: обновления только при значительном перемещении, экономит батарею
- **Постоянный мониторинг**: непрерывные обновления, высокое потребление энергии

### MapKit

#### Карты
**Вопрос:** Что такое MKMapView и как добавить аннотации?

**Ответ:** MKMapView - компонент для отображения карт с поддержкой аннотаций и оверлеев.

```swift
class MapViewController: UIViewController, MKMapViewDelegate {
    private let mapView = MKMapView()

    override func viewDidLoad() {
        super.viewDidLoad()
        setupMap()
        addAnnotations()
    }

    private func setupMap() {
        mapView.delegate = self
        mapView.showsUserLocation = true
        view.addSubview(mapView)
    }

    private func addAnnotations() {
        let annotation = MKPointAnnotation()
        annotation.coordinate = CLLocationCoordinate2D(latitude: 55.7558, longitude: 37.6176)
        annotation.title = "Москва"
        mapView.addAnnotation(annotation)
    }
}
```

## 🎨 Graphics & Animation

### Core Graphics

#### Рисование
**Вопрос:** Что такое CGContext и как создать кастомный рисунок?

**Ответ:** CGContext - контекст для рисования 2D графики.

```swift
override func draw(_ rect: CGRect) {
    guard let context = UIGraphicsGetCurrentContext() else { return }

    // Рисование прямоугольника
    context.setFillColor(UIColor.red.cgColor)
    context.fill(CGRect(x: 50, y: 50, width: 100, height: 100))

    // Рисование линии
    context.setStrokeColor(UIColor.blue.cgColor)
    context.setLineWidth(2)
    context.move(to: CGPoint(x: 0, y: 0))
    context.addLine(to: CGPoint(x: 200, y: 200))
    context.strokePath()
}
```

### Core Animation

#### Анимации
**Вопрос:** Что такое CALayer и как создать базовую анимацию?

**Ответ:** CALayer - низкоуровневый класс для визуального представления контента с поддержкой анимаций.

```swift
// Создание анимации
let animation = CABasicAnimation(keyPath: "opacity")
animation.fromValue = 1.0
animation.toValue = 0.0
animation.duration = 1.0

// Применение анимации
layer.add(animation, forKey: "fadeOut")
```

**Вопрос:** Объясните implicit vs explicit анимации.

**Ответ:**
- **Implicit**: автоматические анимации при изменении свойств
- **Explicit**: явные анимации с контролем над параметрами

## 🔒 Security

### Keychain Services

#### Хранение данных
**Вопрос:** Что такое Keychain и зачем он нужен?

**Ответ:** Keychain - безопасное хранилище для конфиденциальной информации (пароли, токены, ключи шифрования).

**Вопрос:** Объясните уровни защиты данных в Keychain.

**Ответ:**
- **WhenUnlocked**: доступен когда устройство разблокировано
- **AfterFirstUnlock**: доступен после первой разблокировки
- **Always**: всегда доступен (наименее безопасный)

### Local Authentication

#### Биометрия
**Вопрос:** Что такое LAContext и как реализовать биометрическую аутентификацию?

**Ответ:** LAContext управляет биометрической аутентификацией.

```swift
import LocalAuthentication

class BiometricAuth {
    private let context = LAContext()

    func authenticate(completion: @escaping (Bool, Error?) -> Void) {
        let reason = "Аутентификация для доступа к данным"

        context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics,
                             localizedReason: reason) { success, error in
            DispatchQueue.main.async {
                completion(success, error)
            }
        }
    }
}
```

## 📊 Дополнительные вопросы по фреймворкам

### Производительность
**Вопрос:** Как оптимизировать производительность UITableView?

**Ответ:**
1. **Переиспользование ячеек**: dequeueReusableCell
2. **Предзагрузка контента**: prefetching API
3. **Оптимизация высоты**: height caching
4. **Асинхронная загрузка изображений**

### Память
**Вопрос:** Как избежать retain cycles в блоках/замыканиях?

**Ответ:**
1. **Использовать weak self**: `[weak self] in`
2. **Использовать unowned**: когда объект точно существует
3. **Захватывать конкретные свойства**: `[weak label = self.label]`

### Многопоточность
**Вопрос:** Объясните thread safety в Core Data.

**Ответ:**
- **Main context**: только в главном потоке
- **Background context**: для тяжелых операций
- **Parent-child contexts**: для сложных сценариев синхронизации

## 🎯 Подготовка к вопросам по SDK

### 1. Теоретическая подготовка
- Изучите документацию по ключевым фреймворкам
- Практикуйте написание кода для основных сценариев
- Изучите различия между iOS версиями

### 2. Практическая подготовка
- Создайте тестовые проекты для каждого фреймворка
- Практикуйте отладку типичных проблем
- Изучите performance implications

### 3. Глубокое понимание
- Знайте не только "как", но и "зачем"
- Понимайте архитектуру фреймворков
- Умейте объяснять trade-offs решений

## 📚 Рекомендуемые ресурсы

### Официальная документация
- [iOS Developer Library](https://developer.apple.com/library/ios/navigation/)
- [UIKit Framework Reference](https://developer.apple.com/documentation/uikit)
- [Foundation Framework Reference](https://developer.apple.com/documentation/foundation)

### Книги
- "iOS Programming: The Big Nerd Ranch Guide"
- "Core Data by Tutorials" by Ray Wenderlich
- "AVFoundation Programming Guide"

Помните: "Глубокое понимание фреймворков отличает хорошего разработчика от отличного."
