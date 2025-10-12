---
type: "guide"
status: "draft"
level: "advanced"
title: "iOS System Design Interviews"
---

# 🏗️ System Design для собеседований iOS разработчиков

Руководство по подготовке к вопросам системного дизайна на технических собеседованиях iOS разработчиков. Включает типичные сценарии и решения для мобильных приложений.

## 📋 Структура system design интервью

### ⏱️ Временная структура (45-60 минут)
1. **Уточнение требований** (10 минут)
2. **High-level дизайн** (15 минут)
3. **Детальный дизайн компонентов** (15 минут)
4. **Обсуждение ограничений и оптимизаций** (10 минут)
5. **Вопросы интервьюеру** (5 минут)

### 🎯 Основные аспекты оценки
- **Масштабируемость** - как система справляется с ростом нагрузки
- **Надежность** - обработка сбоев и восстановление
- **Производительность** - оптимизация скорости и ресурсов
- **Безопасность** - защита данных и аутентификация
- **Стоимость** - экономическая эффективность решения

## 📱 Типичные сценарии для мобильных приложений

### 1. Социальная сеть (типа Instagram/TikTok)

#### Требования
- Лента постов с пагинацией
- Загрузка изображений/видео
- Лайки, комментарии, репосты
- Push уведомления
- Поиск по контенту

#### High-level архитектура
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   iOS App   │───▶│  API Gateway│───▶│  App Server │
│             │    │             │    │             │
│ - Feed      │    │ - Auth      │    │ - Feed      │
│ - Upload    │    │ - Rate      │    │ - Upload    │
│ - Social    │    │ - Caching   │    │ - Social    │
└─────────────┘    └─────────────┘    └─────────────┘
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   CDN       │    │   Database  │    │   Cache     │
│ - Images    │    │ - Posts     │    │ - Redis     │
│ - Videos    │    │ - Users     │    │ - Hot posts │
│ - Static    │    │ - Comments  │    │ - User data │
└─────────────┘    └─────────────┘    └─────────────┘
```

#### Детальный дизайн ленты

```swift
// iOS клиент - бесконечная прокрутка
class FeedViewController: UIViewController {
    private var posts = [Post]()
    private var isLoading = false
    private var currentPage = 0

    func loadMorePosts() {
        guard !isLoading else { return }

        isLoading = true
        let nextPage = currentPage + 1

        // Предзагрузка изображений для плавной прокрутки
        // Использование NSCache для кеширования
        // Оптимизация размера изображений

        NetworkManager.shared.fetchPosts(page: nextPage) { [weak self] result in
            self?.isLoading = false

            switch result {
            case .success(let newPosts):
                self?.posts.append(contentsOf: newPosts)
                self?.currentPage = nextPage
                self?.tableView.reloadData()
            case .failure(let error):
                self?.showError(error)
            }
        }
    }
}
```

#### Обсуждение ограничений
- **Масштабируемость**: шардирование базы данных, CDN для медиа
- **Производительность**: кеширование популярного контента, предзагрузка
- **Надежность**: fallback для оффлайн режима, retry логика
- **Безопасность**: модерация контента, защита от спама

### 2. Мессенджер (типа WhatsApp/Telegram)

#### Требования
- 1:1 и групповые чаты
- Отправка текста, изображений, файлов
- Online/offline статус
- Push уведомления
- End-to-end шифрование

#### Архитектура в реальном времени
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   iOS App   │◀──▶│WebSocket    │───▶│Message      │
│             │    │Gateway      │    │Broker       │
│ - Chat UI   │    │             │    │             │
│ - File      │    │ - Routing   │    │ - Queue     │
│ - Push      │    │ - Scaling   │    │ - Persistence│
└─────────────┘    └─────────────┘    └─────────────┘
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Push      │    │   Database  │    │   File      │
│ Notification│    │ - Messages  │    │   Storage   │
│ Service     │    │ - Users     │    │ - Images    │
│             │    │ - Groups    │    │ - Documents │
└─────────────┘    └─────────────┘    └─────────────┘
```

#### Детальный дизайн чата

```swift
// Управление состоянием чата
class ChatManager {
    private var messages = [Message]()
    private var unreadCount = [String: Int]()
    private let messageQueue = DispatchQueue(label: "com.app.chat")

    func sendMessage(_ message: Message, to chatId: String) {
        // Оптимистическое обновление UI
        messages.append(message)
        delegate?.didReceiveMessage(message, in: chatId)

        // Отправка на сервер
        NetworkManager.shared.sendMessage(message, chatId: chatId) { [weak self] result in
            self?.messageQueue.async {
                switch result {
                case .success(let serverMessage):
                    // Обновить локальную копию если нужно
                    self?.updateMessage(serverMessage)
                case .failure(let error):
                    // Пометить сообщение как не отправленное
                    self?.markMessageAsFailed(message.id)
                }
            }
        }
    }

    func handleIncomingMessage(_ message: Message, chatId: String) {
        messageQueue.async { [weak self] in
            self?.messages.append(message)
            self?.unreadCount[chatId, default: 0] += 1
            self?.delegate?.didReceiveMessage(message, in: chatId)
        }
    }
}
```

#### Обсуждение ограничений
- **Масштабируемость**: шардирование по пользователям, WebSocket clustering
- **Надежность**: оффлайн режим, очередь сообщений, подтверждение доставки
- **Безопасность**: end-to-end шифрование, защита от MITM атак
- **Производительность**: предзагрузка чатов, оптимизация батареи

### 3. E-commerce приложение (типа Amazon/Wildberries)

#### Требования
- Каталог товаров с фильтрами
- Корзина и оформление заказа
- Оплата (карты, Apple Pay)
- Отслеживание доставки
- Отзывы и рейтинги

#### Архитектура e-commerce
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   iOS App   │───▶│  API Gateway│───▶│  Micro-     │
│             │    │             │    │ services    │
│ - Catalog   │    │ - Auth      │    │ - Catalog   │
│ - Cart      │    │ - Rate      │    │ - Cart      │
│ - Payment   │    │ - Caching   │    │ - Payment   │
└─────────────┘    └─────────────┘    └─────────────┘
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   CDN       │    │   Database  │    │   Payment   │
│ - Images    │    │ - Products  │    │   Gateway   │
│ - Assets    │    │ - Orders    │    │ - Stripe    │
│             │    │ - Users     │    │ - Apple Pay │
└─────────────┘    └─────────────┘    └─────────────┘
```

#### Детальный дизайн корзины

```swift
// Управление корзиной с оффлайн поддержкой
class ShoppingCart {
    private var items = [CartItem]()
    private let storage = UserDefaults.standard
    private let queue = DispatchQueue(label: "com.app.cart")

    func addItem(_ item: CartItem) {
        queue.async { [weak self] in
            self?.items.append(item)
            self?.saveToStorage()
            self?.syncWithServer()
        }
    }

    func removeItem(_ itemId: String) {
        queue.async { [weak self] in
            self?.items.removeAll { $0.id == itemId }
            self?.saveToStorage()
            self?.syncWithServer()
        }
    }

    private func saveToStorage() {
        let data = try? JSONEncoder().encode(items)
        storage.set(data, forKey: "cart_items")
    }

    private func syncWithServer() {
        NetworkManager.shared.syncCart(items) { result in
            switch result {
            case .success:
                // Синхронизация успешна
                break
            case .failure:
                // Запланировать повторную синхронизацию
                self.scheduleRetry()
            }
        }
    }

    private func scheduleRetry() {
        // Реализация retry логики с экспоненциальным backoff
    }
}
```

#### Обсуждение ограничений
- **Консистентность**: eventual consistency для корзины, strong consistency для платежей
- **Производительность**: кеширование каталога, предзагрузка популярных товаров
- **Надежность**: оффлайн режим, локальное сохранение корзины
- **Безопасность**: PCI DSS compliance, токенизация карт

### 4. Ride-sharing приложение (типа Uber/Yandex.Taxi)

#### Требования
- Поиск водителей поблизости
- Real-time отслеживание поездки
- Расчет стоимости маршрута
- Push уведомления
- Геолокация в фоне

#### Архитектура ride-sharing
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   iOS App   │◀──▶│WebSocket    │───▶│  Matching   │
│             │    │Gateway      │    │ Service     │
│ - Maps      │    │             │    │             │
│ - Ride      │    │ - Real-time │    │ - Drivers   │
│ - Payment   │    │ - Location  │    │ - Routes    │
└─────────────┘    └─────────────┘    └─────────────┘
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Maps API  │    │   Database  │    │   Payment   │
│ - Google    │    │ - Rides     │    │   Service   │
│ - Yandex    │    │ - Users     │    │ - Stripe    │
│ - Apple     │    │ - Locations │    │ - Apple Pay │
└─────────────┘    └─────────────┘    └─────────────┘
```

#### Детальный дизайн геолокации

```swift
// Оптимизированная геолокация
class LocationManager {
    private let manager = CLLocationManager()
    private var backgroundTask: UIBackgroundTaskIdentifier = .invalid

    func startTracking() {
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyBestForNavigation
        manager.distanceFilter = 10 // Обновлять каждые 10 метров

        // Запрос разрешения
        manager.requestWhenInUseAuthorization()

        // Фоновое отслеживание для активных поездок
        if isActiveRide {
            startBackgroundTracking()
        }
    }

    private func startBackgroundTracking() {
        backgroundTask = UIApplication.shared.beginBackgroundTask { [weak self] in
            self?.endBackgroundTask()
        }

        manager.allowsBackgroundLocationUpdates = true
        manager.startUpdatingLocation()
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.last else { return }

        // Оптимизация: отправляем координаты только если изменились значительно
        if shouldSendLocationUpdate(location) {
            NetworkManager.shared.sendLocation(location) { result in
                // Обработка ответа
            }
        }
    }

    private func shouldSendLocationUpdate(_ newLocation: CLLocation) -> Bool {
        guard let lastLocation = lastSentLocation else {
            return true
        }

        let distance = newLocation.distance(from: lastLocation)
        return distance > 50 // Отправлять только если переместились > 50 метров
    }
}
```

#### Обсуждение ограничений
- **Масштабируемость**: гео-шардирование, оптимизация запросов по локации
- **Производительность**: предзагрузка карты, оптимизация батареи
- **Надежность**: оффлайн карты, fallback режимы
- **Безопасность**: верификация поездок, защита от мошенничества

## 🔧 Технические аспекты

### 1. Кеширование

#### Стратегии кеширования для мобильных приложений
```swift
// HTTP кеширование
let cache = URLCache(memoryCapacity: 50 * 1024 * 1024, diskCapacity: 100 * 1024 * 1024)
URLCache.shared = cache

// Кастомное кеширование
class ImageCache {
    private let cache = NSCache<NSString, UIImage>()

    func image(for url: URL) -> UIImage? {
        let key = url.absoluteString as NSString

        if let cachedImage = cache.object(forKey: key) {
            return cachedImage
        }

        // Загрузка изображения
        guard let image = loadImage(from: url) else { return nil }

        cache.setObject(image, forKey: key)
        return image
    }
}
```

### 2. Синхронизация данных

#### Offline-first подход
```swift
class DataSynchronizer {
    private var pendingOperations = [Operation]()

    func saveItem(_ item: Item) {
        // Оптимистическое обновление UI
        updateUI(with: item)

        // Сохранение локально
        localStorage.save(item)

        // Добавление в очередь синхронизации
        let syncOperation = SyncOperation(item: item)
        pendingOperations.append(syncOperation)

        // Синхронизация с сервером
        syncWithServer()
    }

    private func syncWithServer() {
        NetworkManager.shared.sync(pendingOperations) { [weak self] result in
            switch result {
            case .success:
                self?.pendingOperations.removeAll()
            case .failure:
                // Повторная синхронизация с экспоненциальным backoff
                self?.scheduleRetry()
            }
        }
    }
}
```

### 3. Обработка ошибок

#### Комплексная стратегия обработки ошибок
```swift
enum NetworkError: Error {
    case noInternet
    case timeout
    case serverError(statusCode: Int)
    case parsingError
    case rateLimited

    var shouldRetry: Bool {
        switch self {
        case .noInternet, .timeout:
            return true
        case .serverError(let code) where code >= 500:
            return true
        default:
            return false
        }
    }

    var retryDelay: TimeInterval {
        switch self {
        case .timeout:
            return 2.0
        case .serverError(let code) where code == 503:
            return 5.0
        default:
            return 1.0
        }
    }
}

class RetryManager {
    private var retryCount = 0
    private let maxRetries = 3

    func executeWithRetry<T>(
        operation: @escaping () async throws -> T,
        onRetry: ((Error, Int) -> Void)? = nil
    ) async throws -> T {
        do {
            return try await operation()
        } catch let error as NetworkError {
            if error.shouldRetry && retryCount < maxRetries {
                retryCount += 1
                onRetry?(error, retryCount)

                try await Task.sleep(nanoseconds: UInt64(error.retryDelay * 1_000_000_000))

                return try await executeWithRetry(
                    operation: operation,
                    onRetry: onRetry
                )
            } else {
                throw error
            }
        }
    }
}
```

## 📊 Метрики и мониторинг

### Ключевые метрики для мобильных приложений

```swift
// Метрики производительности
struct PerformanceMetrics {
    let appLaunchTime: TimeInterval     // Время запуска приложения
    let networkLatency: TimeInterval     // Задержка сети
    let memoryUsage: Double             // Использование памяти
    let batteryImpact: Double           // Влияние на батарею
    let crashRate: Double               // Частота сбоев
}

// Метрики пользовательского опыта
struct UXMetrics {
    let timeToFirstInteraction: TimeInterval  // Время до первого взаимодействия
    let scrollPerformance: Double             // Производительность прокрутки
    let animationFrameRate: Double            // FPS анимаций
    let userRetention: Double                 // Удержание пользователей
}
```

### Мониторинг в реальном времени

```swift
class MetricsCollector {
    private let queue = DispatchQueue(label: "com.app.metrics")

    func collectPerformanceMetrics() {
        queue.async {
            let metrics = PerformanceMetrics(
                appLaunchTime: self.measureAppLaunchTime(),
                networkLatency: self.measureNetworkLatency(),
                memoryUsage: self.getMemoryUsage(),
                batteryImpact: self.measureBatteryImpact(),
                crashRate: self.calculateCrashRate()
            )

            self.sendMetricsToAnalytics(metrics)
        }
    }

    private func sendMetricsToAnalytics(_ metrics: PerformanceMetrics) {
        // Отправка метрик в аналитическую систему
        Analytics.shared.track("performance_metrics", properties: [
            "launch_time": metrics.appLaunchTime,
            "network_latency": metrics.networkLatency,
            "memory_usage": metrics.memoryUsage,
            "battery_impact": metrics.batteryImpact,
            "crash_rate": metrics.crashRate
        ])
    }
}
```

## 🔒 Безопасность

### Аутентификация и авторизация

```swift
class AuthManager {
    private let keychain = KeychainManager()

    func authenticate(username: String, password: String) async throws -> AuthToken {
        // Валидация входных данных
        guard isValidCredentials(username, password) else {
            throw AuthError.invalidCredentials
        }

        // Аутентификация на сервере
        let token = try await NetworkManager.shared.authenticate(username: username, password: password)

        // Сохранение токена в Keychain
        try keychain.saveToken(token, forUser: username)

        return token
    }

    func logout() {
        keychain.clearTokens()
        UserDefaults.standard.removeObject(forKey: "current_user")
    }
}
```

### Шифрование данных

```swift
class EncryptionManager {
    private let keychain = KeychainManager()

    func encrypt(_ data: Data) throws -> Data {
        guard let encryptionKey = keychain.getEncryptionKey() else {
            throw EncryptionError.noKey
        }

        return try AES256.encrypt(data, key: encryptionKey)
    }

    func decrypt(_ encryptedData: Data) throws -> Data {
        guard let encryptionKey = keychain.getEncryptionKey() else {
            throw EncryptionError.noKey
        }

        return try AES256.decrypt(encryptedData, key: encryptionKey)
    }
}
```

## 🚀 Подготовка к system design интервью

### 1. Техническая подготовка
- Изучите типичные сценарии (social, e-commerce, messaging, ride-sharing)
- Практикуйте проектирование архитектуры на бумаге
- Изучите современные мобильные технологии (WebSocket, GraphQL, gRPC)
- Понимайте принципы масштабируемости и производительности

### 2. Практическая подготовка
- Создавайте диаграммы архитектуры для разных сценариев
- Практикуйте объяснение технических решений
- Изучайте реальные кейсы из индустрии
- Готовьтесь отвечать на вопросы о trade-offs

### 3. День интервью
- Задавайте уточняющие вопросы
- Объясняйте ход мыслей вслух
- Предлагайте несколько вариантов решений
- Обсуждайте ограничения и компромиссы

## 📚 Рекомендуемые ресурсы

### Книги
- "System Design Interview" by Alex Xu
- "Designing Data-Intensive Applications" by Martin Kleppmann
- "Mobile Architecture" patterns and practices

### Онлайн ресурсы
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Grokking the System Design Interview](https://www.educative.io/courses/grokking-the-system-design-interview)
- [ByteByteGo](https://bytebytego.com/) - визуальные объяснения системного дизайна

### Практика
- [SystemDesignInterview.com](https://systemdesigninterview.com/)
- [Expedia System Design](https://github.com/ExpediaGroup/system-design)
- [Mobile System Design questions](https://github.com/ashishps1/awesome-system-design-resources)

Помните: "Хороший system design - это баланс между идеальным решением и практическими ограничениями."
