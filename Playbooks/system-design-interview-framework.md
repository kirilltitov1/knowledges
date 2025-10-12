---
type: "playbook"
topics: ["system-design", "interview", "architecture"]
status: "draft"
duration: "45-60m"
title: "System Design Interview Framework"
---

## 🎙 Talk Track (скрипт по минутам)

- **0:00–0:30** — Контекст: «Переформулирую задачу, чтобы убедиться, что мы на одной странице…»
- **0:30–5:00** — Функциональные требования: «Какие use cases must-have для первой версии?»
- **5:00–9:00** — Нефункциональные требования: «Целевые метрики p95/p99 latency, RPS, DAU/MAU, uptime?»
- **9:00–12:00** — Черновые оценки (back-of-the-envelope)
- **12:00–20:00** — High-level архитектура (компоненты и основные потоки)
- **20:00–35:00** — Deep dive по 1–2 критичным компонентам (интерфейсы, данные, state)
- **35:00–45:00** — Данные и консистентность: модели, индексы, кэш, CAP/транзакции/очереди
- **45:00–55:00** — Надёжность и масштабирование: деградация, ретраи/таймауты, алерты, SLI/SLO и error budget
- **55:00–60:00** — Резюме и вопросы интервьюеру

### Готовые фразы
- «Я явно разделю must-have и nice-to-have, чтобы сфокусироваться на ядре.»
- «Зафиксирую целевые метрики: p99 ≤ X ms, RPS ≈ Y, uptime Z.»
- «Сначала опишу простой baseline, затем итеративно усложню под нагрузку.»
- «Тут есть trade-off между консистентностью и доступностью; выберу … потому что …»
- «На уровне клиента предусмотрю graceful degradation при сетевых сбоях.»
---

## 🧩 Шаблон ответа для интервью (скопируй и заполняй)

### 0) Problem Statement (1–2 предложения)
- Что строим и для кого: …

### 1) Functional Requirements
- [ ] Use cases: …
- [ ] Пользовательские роли/платформы: …
- [ ] Out of scope: …

### 2) Non-Functional Requirements (числа!)
- [ ] Latency p95/p99: … ms
- [ ] RPS (read/write): … / …
- [ ] DAU/MAU / peak concurrent: … / … / …
- [ ] Uptime (SLA): …
- [ ] SLI/SLO и бюджет ошибок: …

### 3) Estimations (back-of-the-envelope)
```
QPS_read  = DailyReads  / 86400 ≈ …
QPS_write = DailyWrites / 86400 ≈ …
Storage   = DailyData × Days × Size ≈ …
Bandwidth = QPS × PayloadSize ≈ …
```

### 4) High-Level Design
- Компоненты: Client/iOS, API GW/LB, App Servers, DB, Cache, CDN, MQ…
- Data flows (2–3 ключевых сценария): …

### 5) Data Model (ключевые сущности)
```
User { … }
Content/Post/Message { … }
Relation { … }
```

### 6) Deep Dive по компонентам (выбрать 1–2)
- Networking Layer / Upload Service / Feed Service / Search / Realtime …
- Интерфейсы, схемы данных, consistency, backpressure, failure modes

### 7) Надёжность, Производительность, Масштабирование
- Degradation, retry/timeout, идемпотентность, rate limiting, кэш-стратегии
- Шардирование/реплики, очереди, CDN, индексирование

### 8) Security & Privacy
- Transport/at-rest encryption, authN/Z, PII/consent, безопасное хранение ключей

### 9) Observability
- Метрики, логи, трейсы; алерты на SLO нарушения, error budget policy

### 10) Trade-offs и Next Steps
- Ключевые компромиссы: …
- Вопросы/риски: …

---

## 1️⃣ Этап 1: Уточнение требований (Requirements Gathering)

### 🎯 Цель
Понять, что именно нужно спроектировать, и согласовать scope с интервьюером.

### ✅ Функциональные требования (Functional Requirements)

**Вопросы, которые нужно задать:**

#### Основная функциональность
- Какие основные use cases нужно поддержать?
- Какие действия может выполнять пользователь?
- Какие данные система должна обрабатывать и хранить?
- Есть ли специфические бизнес-правила или ограничения?

#### Платформы и устройства
- На каких платформах должна работать система? (iOS, Android, Web, Desktop)
- Нужна ли offline функциональность?
- Какие минимальные версии iOS/Android поддерживать?
- Нужна ли поддержка iPad, Apple Watch, macOS?

#### Пользовательский опыт
- Какие экраны/views необходимы?
- Какие основные user flows?
- Есть ли требования к UX/UI?
- Нужна ли real-time функциональность?

#### Примеры конкретных вопросов для типовых систем:

**Для чата/мессенджера:**
- Поддержка групповых чатов?
- Текст, медиа, голосовые сообщения?
- Typing indicators, read receipts?
- Push notifications?
- История сообщений — полная или ограниченная?

**Для социальной сети:**
- Что такое post? (текст, фото, видео)
- Feed алгоритм — хронологический или кастомный?
- Лайки, комментарии, репосты?
- Подписки, followers?
- Stories, live streaming?

**Для e-commerce:**
- Каталог товаров, поиск, фильтры?
- Корзина, wishlist?
- Оплата — какие методы?
- Доставка — трекинг?
- Отзывы и рейтинги?

### ⚡ Нефункциональные требования (Non-Functional Requirements)

**Вопросы по масштабу:**
- Сколько пользователей ожидается?
  - DAU (Daily Active Users)
  - MAU (Monthly Active Users)
  - Peak concurrent users
- Какой объем данных?
  - Запросов в секунду (QPS/RPS)
  - Размер хранилища
  - Объем трафика

**Вопросы по производительности:**
- Какие требования к latency?
  - Какое время отклика приемлемо?
  - 99th percentile vs median
- Какие требования к throughput?
- Нужна ли оптимизация для медленного соединения?

**Вопросы по доступности и надежности:**
- Какой требуемый uptime? (99.9%, 99.99%)
- Насколько критична потеря данных?
- Consistency vs Availability tradeoffs (CAP theorem)
- Как обрабатывать сбои?

**Вопросы по безопасности:**
- Какие данные считаются sensitive?
- Требования к аутентификации и авторизации?
- Нужно ли end-to-end encryption?
- Compliance требования? (GDPR, HIPAA, etc.)

**Вопросы по масштабируемости:**
- Ожидаемый рост пользователей?
- Geographic distribution пользователей?
- Сезонность нагрузки?

### 📊 Расчет нагрузки (Back-of-the-envelope estimation)

**Пример расчетов:**

```
Дано: Instagram-like система
- 500M DAU
- Каждый пользователь постит 2 фото в день
- Каждый пользователь просматривает 50 фото в день

Расчеты:
Write QPS:
500M × 2 photos / 86400 seconds ≈ 11,600 photos/sec

Read QPS:
500M × 50 photos / 86400 seconds ≈ 290,000 photos/sec

Storage (за 5 лет):
500M × 2 photos × 365 days × 5 years × 2MB/photo ≈ 3.65 PB

Bandwidth:
Write: 11,600 × 2MB ≈ 23 GB/sec
Read: 290,000 × 2MB ≈ 580 GB/sec
```

### 📝 Приоритизация (Must Have / Nice to Have)

Определите вместе с интервьюером:
- **Must Have** — критически важная функциональность
- **Nice to Have** — дополнительная функциональность
- **Out of Scope** — что точно не рассматриваем

---

## 2️⃣ Этап 2: High-Level Design

### 🎯 Цель
Создать общую архитектуру системы на уровне основных компонентов.

### 🏗️ Основные компоненты

#### Client-side (Mobile/iOS)
- **Presentation Layer**
  - View Controllers / SwiftUI Views
  - ViewModels
  - UI Components
- **Business Logic Layer**
  - Services
  - Use Cases / Interactors
  - State Management
- **Data Layer**
  - Repository Pattern
  - Cache / Local Storage
  - Network Layer

#### Backend Components
- **API Gateway / Load Balancer**
- **Application Servers**
- **Databases**
  - Primary DB (SQL/NoSQL)
  - Cache (Redis, Memcached)
  - CDN для статики
- **Message Queue** (если нужен async processing)
- **Notification Service**

### 📐 Диаграмма компонентов

Нарисуйте high-level diagram:
```
┌─────────────┐
│   Client    │
│  (iOS App)  │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ API Gateway │
│ Load Balancer│
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   App       │
│  Servers    │
└──────┬──────┘
       │
   ┌───┴───┐
   ↓       ↓
┌──────┐ ┌────────┐
│ DB   │ │ Cache  │
└──────┘ └────────┘
```

### 🔄 Основные Data Flows

Опишите 2-3 основных сценария:

**Пример: Posting Photo в Instagram**
1. User выбирает фото → UI
2. Upload фото → API Gateway → Upload Service
3. Resize/Process фото → Image Processing Service
4. Сохранение в storage → S3/CDN
5. Metadata в DB → Database
6. Обновление feed'а followers → Feed Service
7. Push notifications → Notification Service

### 🗄️ Data Models

Определите ключевые entities и их relationships:

```
User {
  id: UUID
  username: String
  email: String
  created_at: Date
}

Post {
  id: UUID
  user_id: UUID
  image_url: String
  caption: String
  created_at: Date
  likes_count: Int
}

Relationship {
  follower_id: UUID
  followee_id: UUID
  created_at: Date
}
```

---

## 3️⃣ Этап 3: Детальный дизайн (Deep Dive)

### 🎯 Цель
Углубиться в критичные компоненты системы.

### 📱 iOS Client Architecture

#### Выбор архитектурного паттерна
- **MVC** — простые приложения
- **MVVM** — data binding, реактивность
- **VIPER** — большие команды, модульность
- **TCA (The Composable Architecture)** — SwiftUI, функциональный подход
- **Clean Architecture** — testability, независимость от фреймворков

**Критерии выбора:**
- Размер команды
- Complexity приложения
- Testability требования
- SwiftUI vs UIKit
- Team expertise

#### Networking Layer

**Компоненты:**
```swift
// API Client
protocol APIClient {
    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T
}

// Endpoint
struct Endpoint {
    let path: String
    let method: HTTPMethod
    let headers: [String: String]?
    let body: Encodable?
}

// Response Handler
protocol ResponseHandler {
    func handle<T: Decodable>(data: Data, response: URLResponse) throws -> T
}
```

**Обсудить:**
- Error handling strategy
- Retry logic
- Authentication (OAuth, JWT)
- Request/Response interceptors
- Mock для testing

#### Persistence Layer

**Варианты storage:**
- **UserDefaults** — простые key-value пары, settings
- **Keychain** — sensitive данные (tokens, passwords)
- **CoreData** — complex data models, relationships
- **Realm** — alternative к CoreData
- **SwiftData** — modern CoreData alternative (iOS 17+)
- **File System** — large files (images, videos, documents)
- **SQLite** — custom SQL queries

**Cache Strategy:**
- **Memory Cache** — NSCache для часто используемых данных
- **Disk Cache** — persistent cache
- **Cache Invalidation** — TTL, LRU
- **Image Cache** — SDWebImage, Kingfisher

#### Offline Support

**Стратегии:**
1. **Read-only offline**
   - Cache данные локально
   - Показываем cached data
   - Синхронизация при появлении сети

2. **Full offline with sync**
   - Операции пишутся локально
   - Queue для pending operations
   - Синхронизация при reconnect
   - Conflict resolution

**Обсудить:**
- Conflict resolution strategy
- Operational transformation
- CRDT (Conflict-free Replicated Data Types)

#### Real-time Communication

**Технологии:**
- **WebSockets** — bidirectional, persistent connection
- **Server-Sent Events (SSE)** — one-way от сервера
- **Long Polling** — fallback для старых устройств
- **Push Notifications** — для background updates

**Для iOS:**
```swift
// WebSocket пример
class WebSocketManager {
    private var webSocket: URLSessionWebSocketTask?
    
    func connect(to url: URL) {
        let session = URLSession(configuration: .default)
        webSocket = session.webSocketTask(with: url)
        webSocket?.resume()
        listen()
    }
    
    func listen() {
        webSocket?.receive { [weak self] result in
            switch result {
            case .success(let message):
                // Handle message
                self?.listen() // Continue listening
            case .failure(let error):
                // Handle error
            }
        }
    }
}
```

#### Concurrency

**GCD (Grand Central Dispatch):**
- DispatchQueue для async операций
- Serial vs Concurrent queues
- QoS (Quality of Service)

**Modern Swift Concurrency:**
- async/await
- Actors для thread-safety
- TaskGroup для parallel tasks
- MainActor для UI updates

**Обсудить:**
- Race conditions prevention
- Deadlocks avoidance
- Memory management with closures
- Cancellation handling

#### Memory Management

**Критичные точки:**
- Retain cycles (weak, unowned)
- Image memory management
- Collection view/table view cell reuse
- Cache memory limits
- Background task memory

**Профилирование:**
- Instruments: Allocations, Leaks
- Memory graph debugger
- Memory warnings handling

### 🖼️ Специфичные компоненты

#### Infinite Scroll / Pagination

**Стратегии:**
```swift
// Cursor-based pagination
struct PaginatedResponse<T: Decodable>: Decodable {
    let items: [T]
    let nextCursor: String?
    let hasMore: Bool
}

// Offset-based pagination
struct OffsetPaginatedResponse<T: Decodable>: Decodable {
    let items: [T]
    let offset: Int
    let limit: Int
    let total: Int
}
```

**Обсудить:**
- Prefetching strategy
- UICollectionView prefetching API
- Loading indicators
- Error handling при загрузке

#### Image Loading & Caching

**Оптимизации:**
- Progressive image loading
- Thumbnail vs full size
- Image format (WebP, HEIF)
- Lazy loading
- Memory/disk cache layers
- Decompression на background thread

#### Feed / Timeline

**Подходы:**
- **Pull model** — загружаем при открытии
- **Push model** — updates через push/websocket
- **Hybrid** — cached + incremental updates

**Ranking алгоритм:**
- Chronological
- Engagement-based
- ML-based personalization

#### Search

**Компоненты:**
- **Local search** — фильтрация кешированных данных
- **Remote search** — API запросы
- **Debouncing** — ограничение частоты запросов
- **Suggestions/Autocomplete**
- **Search history**

**Оптимизации:**
```swift
// Debouncing example
class SearchDebouncer {
    private var workItem: DispatchWorkItem?
    private let delay: TimeInterval
    
    init(delay: TimeInterval = 0.5) {
        self.delay = delay
    }
    
    func debounce(_ action: @escaping () -> Void) {
        workItem?.cancel()
        let newWorkItem = DispatchWorkItem(block: action)
        workItem = newWorkItem
        DispatchQueue.main.asyncAfter(deadline: .now() + delay, execute: newWorkItem)
    }
}
```

#### Video Playback

**Компоненты:**
- AVFoundation / AVPlayer
- HLS streaming
- Preloading
- Background playback
- Picture-in-Picture
- Buffering strategy

**Оптимизации:**
- Adaptive bitrate streaming
- Prefetching next video
- Memory management
- Battery optimization

#### Feature Flags & A/B Testing

**Зачем нужны:**
- 🎯 **A/B тестирование** — сравнение вариантов функциональности
- 🚀 **Gradual rollout** — постепенный выкат новых features
- 🔧 **Kill switches** — быстрое отключение проблемных features
- 🎭 **Feature toggles** — включение/выключение функций без релиза
- 👥 **User segmentation** — разные features для разных групп
- 🧪 **Canary releases** — тестирование на малой группе пользователей

**Архитектура:**

```swift
// Feature Flag Service
protocol FeatureFlagService {
    func isEnabled(_ feature: Feature) -> Bool
    func getValue<T>(_ key: String, default: T) -> T
    func refresh() async
}

enum Feature: String {
    case newCheckoutFlow = "new_checkout_flow"
    case darkModeUI = "dark_mode_ui"
    case premiumFeatures = "premium_features"
    case experimentalSearch = "experimental_search"
}

// Implementation
class RemoteFeatureFlagService: FeatureFlagService {
    private var cache: [String: Any] = [:]
    private let apiClient: APIClient
    private let storage: LocalStorage // для offline
    
    func isEnabled(_ feature: Feature) -> Bool {
        // 1. Проверяем cache
        if let cached = cache[feature.rawValue] as? Bool {
            return cached
        }
        
        // 2. Проверяем local storage (offline)
        if let stored = storage.get(feature.rawValue) as? Bool {
            cache[feature.rawValue] = stored
            return stored
        }
        
        // 3. Default value
        return false
    }
    
    func refresh() async {
        do {
            let flags = try await apiClient.fetchFeatureFlags()
            cache = flags
            storage.save(flags) // сохраняем для offline
        } catch {
            // Continue with cached/stored values
        }
    }
}
```

**Использование в коде:**

```swift
// В UI
class CheckoutViewController: UIViewController {
    let featureFlags: FeatureFlagService
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        if featureFlags.isEnabled(.newCheckoutFlow) {
            setupNewCheckoutUI()
        } else {
            setupOldCheckoutUI()
        }
    }
}

// В business logic
class PaymentService {
    let featureFlags: FeatureFlagService
    
    func processPayment() async throws {
        if featureFlags.isEnabled(.newPaymentProvider) {
            return try await processWithNewProvider()
        } else {
            return try await processWithOldProvider()
        }
    }
}
```

**A/B Testing:**

```swift
// A/B Test Manager
class ABTestManager {
    enum Variant: String {
        case control = "A"
        case treatment = "B"
    }
    
    struct Experiment {
        let id: String
        let name: String
        let variants: [Variant: Double] // % distribution
    }
    
    private let userId: String
    private var assignments: [String: Variant] = [:]
    
    func getVariant(for experiment: Experiment) -> Variant {
        // Проверяем, есть ли уже assignment
        if let assigned = assignments[experiment.id] {
            return assigned
        }
        
        // Deterministic assignment на основе userId
        let hash = "\(userId)-\(experiment.id)".hashValue
        let normalized = abs(Double(hash) / Double(Int.max))
        
        var cumulative = 0.0
        for (variant, percentage) in experiment.variants.sorted(by: { $0.key.rawValue < $1.key.rawValue }) {
            cumulative += percentage
            if normalized <= cumulative {
                assignments[experiment.id] = variant
                return variant
            }
        }
        
        return .control
    }
}

// Использование
let experiment = Experiment(
    id: "checkout_flow_test",
    name: "New Checkout Flow",
    variants: [.control: 0.5, .treatment: 0.5] // 50/50 split
)

let variant = abTestManager.getVariant(for: experiment)
switch variant {
case .control:
    // Show old checkout flow
    analytics.track("experiment_view", properties: ["variant": "A"])
case .treatment:
    // Show new checkout flow
    analytics.track("experiment_view", properties: ["variant": "B"])
}
```

**Стратегии rollout:**

1. **Percentage-based rollout**
   ```swift
   // 10% пользователей видят новую feature
   if featureFlags.getRolloutPercentage(.newFeature) > userHash % 100 {
       showNewFeature()
   }
   ```

2. **User-based targeting**
   ```swift
   // Только для beta testers
   if user.isBetaTester && featureFlags.isEnabled(.experimentalFeature) {
       showExperimentalFeature()
   }
   ```

3. **Gradual rollout**
   ```
   Week 1: 5% users
   Week 2: 20% users
   Week 3: 50% users
   Week 4: 100% users
   ```

4. **Kill switch**
   ```swift
   // Быстрое отключение проблемной feature
   guard featureFlags.isEnabled(.newAlgorithm) else {
       return fallbackToOldAlgorithm()
   }
   ```

**Backend API для feature flags:**

```
GET /api/v1/feature-flags?userId=123&platform=ios&version=1.2.0

Response:
{
  "flags": {
    "new_checkout_flow": true,
    "dark_mode_ui": false,
    "premium_features": true
  },
  "experiments": {
    "checkout_test": {
      "variant": "B",
      "experimentId": "exp_001"
    }
  },
  "rollouts": {
    "new_algorithm": {
      "enabled": true,
      "percentage": 25
    }
  },
  "ttl": 3600  // cache время в секундах
}
```

**Обсудить:**
- **Targeting rules:**
  - User attributes (country, language, plan)
  - Device attributes (iOS version, device model)
  - App version
  - Custom rules
  
- **Refresh strategy:**
  - On app launch
  - Periodic refresh (every N minutes)
  - Real-time via WebSocket
  - Push notification triggered
  
- **Offline behavior:**
  - Cached flags from last sync
  - Default values для новых flags
  - Local storage (UserDefaults/CoreData)
  
- **Performance:**
  - In-memory cache для быстрого доступа
  - Batch fetching всех flags
  - Минимальная latency для checks
  
- **Analytics integration:**
  - Track feature exposure
  - Track variant assignments
  - Measure conversion metrics
  - Statistical significance
  
- **Best practices:**
  - Feature flags should be temporary (remove after full rollout)
  - Clear naming convention
  - Documentation для каждого flag
  - Monitoring активных flags
  - Cleanup старых flags

**Popular tools:**
- **LaunchDarkly** — enterprise solution
- **Firebase Remote Config** — free, simple
- **Optimizely** — A/B testing focused
- **Split.io** — feature flagging
- **ConfigCat** — developer-friendly
- **Custom solution** — полный контроль

**Trade-offs:**

| Подход | Плюсы | Минусы |
|--------|-------|--------|
| **Remote Config** | Flexible, instant updates, no app release | Network dependency, complexity |
| **Hardcoded** | Simple, no dependencies | Requires app release to change |
| **Hybrid** | Best of both, offline support | More complex architecture |

### 🔐 Security

**Обсудить:**
- **Network Security**
  - TLS/SSL pinning
  - Certificate validation
  - API key management
  
- **Data Security**
  - Encryption at rest (Keychain, encrypted DB)
  - Encryption in transit (HTTPS)
  - Biometric authentication
  
- **Code Security**
  - Obfuscation
  - Jailbreak detection
  - Reverse engineering protection

### 📊 Analytics & Monitoring

**Что логировать:**
- User interactions
- API calls (success/failure)
- Performance metrics
- Crashes
- Business metrics

**Tools:**
- Firebase Analytics
- Crashlytics
- Custom logging solution

---

## 4️⃣ Этап 4: Edge Cases и Оптимизации

### 🎯 Цель
Показать, что вы думаете о граничных случаях и знаете, как оптимизировать систему.

### ⚠️ Edge Cases

#### Network
- ❌ No internet connection
- 🐌 Slow/unreliable connection
- 📶 Switching between WiFi and cellular
- ⏱️ Request timeout
- 🔄 Retry after failure

#### Data
- 📭 Empty states (no data)
- 📚 Large datasets
- 🗑️ Deleted/removed content
- 🔒 Permission denied
- 🚫 Invalid data from server

#### User Input
- 📏 Too long input
- 🈳 Empty input
- 💥 Special characters
- 📝 Input validation
- 🔤 Localization issues

#### State Management
- 🔄 Background/foreground transitions
- 💀 App termination
- 📱 Low memory warning
- 🔋 Low power mode
- 📞 Phone calls / interruptions

#### Concurrency
- 🏃‍♂️ Race conditions
- 🔒 Deadlocks
- 🔄 Multiple simultaneous requests
- ❌ Request cancellation

### 🚀 Performance Optimizations

#### Network
- **Caching**
  - HTTP cache
  - Response caching
  - CDN usage
  
- **Compression**
  - GZIP/Brotli
  - Image compression
  
- **Batching**
  - Batch API requests
  - GraphQL для минимизации requests
  
- **Prefetching**
  - Predictive loading
  - Preload next page

#### UI/Rendering
- **Collection View / Table View**
  - Cell reuse
  - Height caching
  - Async image loading
  - Prefetching API
  
- **Layout**
  - Auto Layout optimization
  - Layer rasterization
  - shouldRasterize
  
- **Image**
  - Downsampling
  - Appropriate image size
  - Format optimization (WebP, HEIF)

#### Memory
- **Memory warnings handling**
- **Cache limits**
- **Image memory management**
- **Autoreleasepool для loops**
- **Lazy loading**

#### Battery
- **Location updates** — significant changes only
- **Network calls** — batch, schedule
- **Background processing** — BGTaskScheduler
- **Animations** — optimize/reduce

#### Database
- **Indexing**
- **Batch operations**
- **Background context для CoreData**
- **Pagination**
- **Query optimization**

### 📈 Scalability

#### Client-side
- **Code modularization**
  - Feature modules
  - Swift Package Manager
  - Framework targets
  
- **Dependency injection**
  - Testability
  - Flexibility
  
- **Feature flags**
  - A/B testing
  - Gradual rollout
  - Kill switches

#### Infrastructure (если спрашивают про backend)
- **Horizontal scaling** — добавление серверов
- **Vertical scaling** — увеличение мощности
- **Database sharding**
- **Read replicas**
- **Caching layers** (Redis, Memcached)
- **CDN** для статики
- **Microservices** — разделение на сервисы
- **Message queues** — async processing

### 🔍 Monitoring & Observability

- **Metrics**
  - Response times
  - Error rates
  - Crash rates
  - User engagement
  
- **Logging**
  - Structured logging
  - Log levels
  - Centralized logging
  
- **Alerting**
  - Threshold-based alerts
  - Anomaly detection
  
- **Performance monitoring**
  - APM tools
  - Custom metrics
  - User experience metrics

---

## 5️⃣ Чеклист для интервью

### ✅ Перед началом дизайна

- [ ] Задал уточняющие вопросы
- [ ] Определил функциональные требования
- [ ] Определил нефункциональные требования
- [ ] Сделал back-of-the-envelope estimation
- [ ] Согласовал scope (must have / nice to have)
- [ ] Определил платформы и устройства

### ✅ High-Level Design

- [ ] Нарисовал диаграмму компонентов
- [ ] Описал основные data flows
- [ ] Определил data models
- [ ] Выбрал архитектурный подход
- [ ] Обсудил client-server взаимодействие

### ✅ Детальный дизайн

- [ ] Детально проработал 2-3 критичных компонента
- [ ] Обсудил networking layer
- [ ] Обсудил persistence strategy
- [ ] Обсудил caching strategy
- [ ] Обсудил concurrency approach
- [ ] Учел offline scenarios

### ✅ Edge Cases

- [ ] Обсудил error handling
- [ ] Учел network issues
- [ ] Учел empty/loading states
- [ ] Обсудил data validation
- [ ] Учел app lifecycle events

### ✅ Оптимизации

- [ ] Обсудил performance optimizations
- [ ] Обсудил memory management
- [ ] Обсудил battery efficiency
- [ ] Обсудил scalability
- [ ] Упомянул monitoring

### ✅ Общее

- [ ] Объяснял решения и trade-offs
- [ ] Слушал feedback интервьюера
- [ ] Адаптировал дизайн по ходу
- [ ] Использовал правильную терминологию
- [ ] Остался в рамках времени

---

## 💡 Общие советы

### ✅ DO (Делать)

1. **Задавайте вопросы**
   - Лучше задать "глупый" вопрос, чем делать неправильные assumptions
   - Интервьюер ожидает вопросов

2. **Думайте вслух**
   - Объясняйте свой thought process
   - Проговаривайте trade-offs
   - "Я думаю об этом так... потому что..."

3. **Начинайте с простого**
   - Сначала simple solution
   - Потом оптимизируйте и усложняйте
   - Итеративный подход

4. **Будьте конкретными**
   - Используйте реальные технологии и инструменты
   - Приводите примеры кода (где уместно)
   - Называйте конкретные цифры

5. **Обсуждайте trade-offs**
   - Каждое решение имеет плюсы и минусы
   - Объясняйте, почему выбрали именно это решение
   - "X лучше для Y, но Z может быть проблемой"

6. **Адаптируйтесь**
   - Слушайте hints от интервьюера
   - Будьте готовы изменить подход
   - Реагируйте на feedback

### ❌ DON'T (Не делать)

1. **Не молчите**
   - Silence is bad
   - Интервьюер не знает, что вы думаете

2. **Не прыгайте сразу в код**
   - Сначала high-level дизайн
   - Потом детали

3. **Не делайте assumptions без уточнения**
   - Всегда проверяйте с интервьюером
   - "Я предполагаю X, это правильно?"

4. **Не игнорируйте ограничения**
   - Учитывайте scale, performance, etc.
   - Реалистичные решения

5. **Не зацикливайтесь на одной части**
   - Покрывайте всю систему
   - Time management важен

6. **Не спорьте с интервьюером**
   - Прислушивайтесь к feedback
   - Collaborative approach

---

## 📚 Типовые системы для практики

### Beginner Level
1. **URL Shortener** (bit.ly)
2. **Pastebin**
3. **Instagram Stories**
4. **Timer / Stopwatch App**

### Intermediate Level
5. **Instagram Feed**
6. **Twitter Timeline**
7. **Messenger / Chat App**
8. **News Feed (Reddit-like)**
9. **E-commerce App (Product Catalog + Cart)**
10. **Food Delivery App (Uber Eats-like)**

### Advanced Level
11. **YouTube / Video Streaming**
12. **Spotify / Music Streaming**
13. **Google Maps / Navigation**
14. **Uber / Ride Sharing**
15. **Airbnb / Booking System**
16. **Notification System**
17. **Rate Limiter**
18. **Distributed Cache**

---

## 🔗 Связанные темы

- [[Architecture]] — архитектурные паттерны iOS
- [[Networking]] — networking best practices
- [[Persistence]] — data persistence стратегии
- [[Concurrency & Multithreading]] — многопоточность
- [[Performance & Profiling]] — оптимизация производительности
- [[Security]] — безопасность приложений

---

## 📖 Дополнительные ресурсы

### Книги
- "System Design Interview" by Alex Xu (Vol 1 & 2)
- "Designing Data-Intensive Applications" by Martin Kleppmann
- "Building Microservices" by Sam Newman

### Online
- System Design Primer (GitHub)
- Grokking the System Design Interview
- ByteByteGo (YouTube)
- Engineering blogs: Netflix, Uber, Twitter, Facebook

### iOS Specific
- WWDC videos on architecture
- iOS app architecture books
- objc.io articles


