---
title: System Design Cheat Sheet
type: playbook
topics: [system-design, interview, quick-reference]
duration: 5m
---

# System Design Cheat Sheet

Краткая шпаргалка для интервью по системному дизайну (quick reference).

> 📖 Полная версия: [[system-design-interview-framework]]

---

## ⏱️ Тайминг (60 мин)

| Этап                | Время     | Что делать                    |
| ------------------- | --------- | ----------------------------- |
| **1. Requirements** | 10-15 мин | Уточнение требований, scope   |
| **2. High-Level**   | 10-15 мин | Общая архитектура, компоненты |
| **3. Deep Dive**    | 15-20 мин | Детали 2-3 компонентов        |
| **4. Edge Cases**   | 10-15 мин | Граничные случаи, оптимизации |
| **5. Questions**    | 5 мин     | Вопросы интервьюеру           |

### Альтернативы (быстрые):
- **45 минут**: 7 → 8 → 15 → 10 → 5
- **30 минут**: 5 → 7 → 12 → 4 → 2

---

## 🎙 Mini Talk Track
- «Переформулирую задачу и уточню must-have.»
- «Зафиксирую метрики: p99, RPS, uptime/SLO.»
- «Нарисую high-level и пройду 2 data flow.»
- «Сделаю deep dive в 1–2 критичных компонента.»
- «Покрою отказоустойчивость, кэш и масштабирование; завершу trade-offs.»

---

## 🧩 Мини-шаблон (копируй и заполняй)
- **Problem**: … (1–2 предложения)
- **FRs**: …
- **NFRs**: p99 … ms, RPS r/w …/…, uptime …, SLO …
- **Estimates**: read/write QPS …/…, storage …, bandwidth …
- **High-Level**: компоненты + 2 потока данных
- **Data Model**: User, Content, Relation …
- **Deep Dive**: компонент A: интерфейсы, данные, failure modes
- **Scale/Reliability**: кэш, шардирование/реплики, retry/timeout, SLI/SLO
- **Security/Privacy**: …
- **Observability**: метрики/логи/алерты
- **Trade-offs**: …; **Q&A**: …

---

## 1️⃣ Requirements Gathering

### ✅ Функциональные требования

**Вопросы:**
- ❓ Какие основные use cases?
- ❓ Какие платформы? (iOS, Android, Web)
- ❓ Нужен ли offline mode?
- ❓ Real-time функциональность?
- ❓ Основные user flows?
- ❓ Какие данные хранить?

### ⚡ Нефункциональные требования

**Scale:**
- 👥 Сколько пользователей? (DAU/MAU)
- 📊 Requests per second? (Read/Write)
- 💾 Объем данных? (Storage)
- 🌍 Geographic distribution?

**Performance:**
- ⚡ Latency requirements? (p99)
- 🚀 Throughput?
- 📶 Медленное соединение?

**Reliability:**
- 🎯 Uptime? (99.9%, 99.99%)
- 💥 Tolerance к потере данных?
- 🔄 CAP: Consistency vs Availability?

**Security:**
- 🔒 Sensitive data?
- 🔐 Auth/Authorization?
- 🛡️ Encryption?

### 📊 Back-of-envelope

```
Формулы:
QPS = Daily Operations / 86400 sec
Storage = Data/day × Days × Size
Bandwidth = QPS × Data Size
```

---

## 2️⃣ High-Level Design

### 🏗️ iOS Client Layers

```
┌──────────────────────┐
│   Presentation       │  ViewControllers/Views
│   (UI)               │  ViewModels
├──────────────────────┤
│   Business Logic     │  Services, Use Cases
│                      │  State Management
├──────────────────────┤
│   Data Layer         │  Repository
│                      │  Cache, Network
└──────────────────────┘
```

### 🔄 Типовая диаграмма

```
Client (iOS)
    ↓
API Gateway / Load Balancer
    ↓
App Servers
    ↓
┌───────┬─────────┬─────────┐
│  DB   │ Cache   │   CDN   │
└───────┴─────────┴─────────┘
```

### 📋 Data Models

Определи ключевые entities:
- User
- Content (Post/Message/etc)
- Relationships
- Metadata

---

## 3️⃣ Deep Dive Чеклист

### 📱 iOS Architecture

**Выбор паттерна:**
- [ ] MVC / MVVM / VIPER / TCA / Clean
- [ ] Почему именно этот?
- [ ] Trade-offs?

### 🌐 Networking

**Компоненты:**
- [ ] API Client / Endpoint
- [ ] Error handling
- [ ] Retry logic
- [ ] Authentication (OAuth, JWT)
- [ ] Request/Response interceptors
- [ ] Mocking для tests

**Код-пример:**
```swift
protocol APIClient {
    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T
}
```

### 💾 Persistence

**Storage options:**

| Тип                 | Использование     |
| ------------------- | ----------------- |
| UserDefaults        | Settings, flags   |
| Keychain            | Tokens, passwords |
| CoreData/SwiftData  | Complex models    |
| FileSystem          | Images, videos    |
| Cache (Memory/Disk) | Temporary data    |

**Cache strategy:**
- [ ] Memory cache (NSCache)
- [ ] Disk cache
- [ ] Invalidation (TTL, LRU)
- [ ] Image cache (Kingfisher/SDWebImage)

### 📡 Offline Support

**Стратегии:**
1. **Read-only**: Cache + sync on reconnect
2. **Full offline**: Local writes + sync queue + conflict resolution

**Обсудить:**
- [ ] Conflict resolution
- [ ] Operational transformation / CRDT

### 🔄 Real-time

**Технологии:**
- WebSockets (bidirectional)
- SSE (Server-Sent Events)
- Long Polling
- Push Notifications

### ⚡ Concurrency

**Swift Concurrency:**
```swift
// Modern approach
async/await
Actors (thread-safety)
TaskGroup (parallel)
@MainActor (UI updates)
```

**GCD:**
```swift
DispatchQueue.main.async { }
DispatchQueue.global(qos: .background).async { }
```

---

## 4️⃣ Edge Cases

### ⚠️ Network
- [ ] No connection
- [ ] Slow/unreliable connection
- [ ] WiFi ↔ Cellular switch
- [ ] Timeout / Retry
- [ ] Request cancellation

### 📦 Data
- [ ] Empty states
- [ ] Large datasets
- [ ] Deleted content
- [ ] Invalid server data
- [ ] Permission denied

### 👤 User Input
- [ ] Too long / empty
- [ ] Special characters
- [ ] Validation
- [ ] Localization

### 📱 App State
- [ ] Background/foreground
- [ ] App termination
- [ ] Low memory warning
- [ ] Low power mode
- [ ] Interruptions (calls)

### 🔄 Concurrency
- [ ] Race conditions
- [ ] Deadlocks
- [ ] Multiple simultaneous requests

---

## 🚀 Optimizations

### 🌐 Network
- ✅ Caching (HTTP, response, CDN)
- ✅ Compression (GZIP, images)
- ✅ Batching (batch requests)
- ✅ Prefetching (predictive)
- ✅ GraphQL (minimize requests)

### 🎨 UI/Rendering
- ✅ Cell reuse
- ✅ Height caching
- ✅ Async image loading
- ✅ Prefetching API
- ✅ Auto Layout optimization
- ✅ Layer rasterization
- ✅ Image downsampling

### 💾 Memory
- ✅ Memory warnings handling
- ✅ Cache limits
- ✅ Autoreleasepool в loops
- ✅ Lazy loading
- ✅ Image memory management

### 🔋 Battery
- ✅ Location: significant changes only
- ✅ Network: batch, schedule
- ✅ Background: BGTaskScheduler
- ✅ Animations: optimize

### 🗄️ Database
- ✅ Indexing
- ✅ Batch operations
- ✅ Background context (CoreData)
- ✅ Pagination
- ✅ Query optimization

---

## 📋 Quick Checklist

### Перед дизайном
- [ ] Задал вопросы
- [ ] Functional requirements
- [ ] Non-functional requirements
- [ ] Estimations
- [ ] Согласовал scope

### High-Level
- [ ] Diagram компонентов
- [ ] Data flows (2-3 сценария)
- [ ] Data models
- [ ] Архитектурный выбор

### Deep Dive
- [ ] 2-3 критичных компонента
- [ ] Networking layer
- [ ] Persistence strategy
- [ ] Caching strategy
- [ ] Concurrency
- [ ] Offline scenarios
- [ ] Feature flags / A/B testing (если применимо)

### Edge Cases
- [ ] Error handling
- [ ] Network issues
- [ ] Empty/loading states
- [ ] Data validation
- [ ] App lifecycle

### Optimizations
- [ ] Performance
- [ ] Memory
- [ ] Battery
- [ ] Scalability (модульность, feature flags)
- [ ] Monitoring

---

## 💡 Quick Tips

### ✅ DO
1. ❓ Задавай вопросы
2. 💬 Думай вслух
3. 🎯 Начинай с простого
4. 🔧 Будь конкретным (названия технологий)
5. ⚖️ Обсуждай trade-offs
6. 🔄 Адаптируйся к feedback

### ❌ DON'T
1. 🤐 Не молчи
2. 💻 Не прыгай сразу в код
3. 🤔 Не делай assumptions без проверки
4. 🚫 Не игнорируй ограничения
5. ⏰ Не зацикливайся на одной части
6. 🗣️ Не спорь с интервьюером

---

## 🎯 Типовые системы для практики

### 🟢 Beginner
- URL Shortener
- Pastebin
- Timer/Stopwatch App

### 🟡 Intermediate
- Instagram Feed
- Twitter Timeline
- Chat/Messenger
- News Feed
- E-commerce Catalog
- Food Delivery App

### 🔴 Advanced
- YouTube (video streaming)
- Spotify (music streaming)
- Google Maps
- Uber (ride sharing)
- Airbnb (booking)

---

## 📱 iOS-Specific Components

### Infinite Scroll
```swift
// Cursor-based pagination
struct PaginatedResponse<T> {
    let items: [T]
    let nextCursor: String?
    let hasMore: Bool
}
```

### Search с Debouncing
```swift
class Debouncer {
    private var workItem: DispatchWorkItem?
    private let delay: TimeInterval = 0.5
    
    func debounce(_ action: @escaping () -> Void) {
        workItem?.cancel()
        let item = DispatchWorkItem(block: action)
        workItem = item
        DispatchQueue.main.asyncAfter(deadline: .now() + delay, execute: item)
    }
}
```

### Image Loading
- Progressive loading
- Thumbnail vs full size
- Lazy loading
- Multi-layer cache
- Background decompression

### Video Playback
- AVFoundation/AVPlayer
- HLS streaming
- Preloading
- Background playback
- PiP
- Adaptive bitrate

### Feature Flags & A/B Testing

**Зачем:**
- 🎯 A/B testing
- 🚀 Gradual rollout (5% → 25% → 50% → 100%)
- 🔧 Kill switches (быстрое отключение)
- 👥 User segmentation

**Quick implementation:**
```swift
protocol FeatureFlagService {
    func isEnabled(_ feature: Feature) -> Bool
}

// Использование
if featureFlags.isEnabled(.newCheckoutFlow) {
    showNewFlow()
} else {
    showOldFlow()
}
```

**Стратегии:**
- **Percentage-based** — 10% users видят feature
- **User-targeting** — beta testers, premium users
- **Device-targeting** — iOS 17+, iPhone 15+
- **Geo-targeting** — определенные страны

**Tools:**
- Firebase Remote Config
- LaunchDarkly
- Optimizely
- Custom solution

**Обсудить:**
- Offline behavior (cached flags)
- Refresh strategy (on launch, periodic)
- Analytics integration (track exposure)
- Default values

---

## 🔐 Security Quick List

- [ ] TLS/SSL pinning
- [ ] Certificate validation
- [ ] Encryption at rest (Keychain)
- [ ] Encryption in transit (HTTPS)
- [ ] Biometric auth
- [ ] Jailbreak detection
- [ ] Code obfuscation

---

## 📊 Monitoring

**Что логировать:**
- User interactions
- API calls (success/failure)
- Performance metrics
- Crashes
- Business metrics

**Tools:** Firebase, Crashlytics, Custom

---

**🔗 Связано:** [[system-design-interview-framework|Полная версия]]


