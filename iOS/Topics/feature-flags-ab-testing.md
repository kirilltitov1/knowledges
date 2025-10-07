---
title: Feature Flags & A/B Testing
type: topic
topics: [feature-flags, ab-testing, remote-config, experimentation]
status: complete
---

# Feature Flags & A/B Testing

Механизмы для управления функциональностью приложения без релиза и проведения экспериментов.

## 📚 Теория

### Что такое Feature Flags?

**Feature Flags (Feature Toggles)** — это техника, позволяющая включать и выключать функциональность приложения динамически, без необходимости выпуска новой версии.

### Зачем нужны?

#### 1. 🚀 **Gradual Rollout (Постепенный выкат)**
Новая функциональность запускается не сразу для всех, а постепенно:
```
Week 1: 5% пользователей
Week 2: 25% пользователей
Week 3: 50% пользователей
Week 4: 100% пользователей
```

**Преимущества:**
- Минимизация рисков при проблемах
- Мониторинг метрик на малой группе
- Возможность быстро откатить изменения

#### 2. 🔧 **Kill Switches (Аварийное отключение)**
Возможность мгновенно отключить проблемную функцию без релиза:
```swift
guard featureFlags.isEnabled(.newPaymentFlow) else {
    // Fallback to old, stable payment flow
    return processOldPayment()
}
```

**Примеры использования:**
- Критический баг обнаружен в production
- Backend API недоступен
- Перегрузка сервера из-за новой функции

#### 3. 🎯 **A/B Testing (Эксперименты)**
Сравнение эффективности разных вариантов функциональности:
```
Variant A (control): 50% пользователей — старый UI
Variant B (treatment): 50% пользователей — новый UI

Метрики:
- Conversion rate
- Time on screen
- User engagement
```

#### 4. 👥 **User Segmentation (Сегментация)**
Разные функции для разных групп пользователей:
- Beta testers видят экспериментальные features
- Premium users имеют доступ к расширенным функциям
- Разные features для разных регионов

#### 5. 🧪 **Canary Releases**
Тестирование на небольшой группе перед полным запуском:
```
1. Deploy new version to app store
2. Enable feature for 1% users (canary group)
3. Monitor metrics for 24 hours
4. If successful → increase to 10% → 50% → 100%
5. If issues → disable flag → investigate
```

#### 6. 📦 **Continuous Deployment**
Код деплоится в production, но feature скрыта за флагом:
```swift
// Новый код уже в production, но отключен
if featureFlags.isEnabled(.newRecommendationEngine) {
    return newRecommendations()
} else {
    return oldRecommendations()
}
```

---

## 💻 Архитектура

### Базовый интерфейс

```swift
// MARK: - Feature Flag Service Protocol

protocol FeatureFlagService {
    /// Проверяет, включена ли функция
    func isEnabled(_ feature: Feature) -> Bool
    
    /// Получает значение конфигурации
    func getValue<T>(_ key: String, defaultValue: T) -> T
    
    /// Обновляет флаги с сервера
    func refresh() async throws
    
    /// Подписка на изменения флагов
    func observe(_ feature: Feature, handler: @escaping (Bool) -> Void)
}

// MARK: - Features Enum

enum Feature: String, CaseIterable {
    // UI Features
    case newCheckoutFlow = "new_checkout_flow"
    case darkModeUI = "dark_mode_ui"
    case experimentalSearch = "experimental_search"
    
    // Business Logic
    case newPaymentProvider = "new_payment_provider"
    case recommendationEngineV2 = "recommendation_engine_v2"
    
    // Performance
    case imagePreloading = "image_preloading"
    case videoAutoplay = "video_autoplay"
    
    // A/B Tests
    case checkoutExperiment = "checkout_experiment_001"
    case onboardingExperiment = "onboarding_experiment_002"
}
```

### Полная реализация

```swift
// MARK: - Remote Feature Flag Service

class RemoteFeatureFlagService: FeatureFlagService {
    
    // MARK: - Properties
    
    private var cache: [String: Any] = [:]
    private let apiClient: APIClient
    private let storage: LocalStorage
    private let userId: String
    private var observers: [String: [(Bool) -> Void]] = [:]
    
    // MARK: - Configuration
    
    private let refreshInterval: TimeInterval = 3600 // 1 hour
    private var lastRefreshTime: Date?
    
    // MARK: - Initialization
    
    init(
        apiClient: APIClient,
        storage: LocalStorage,
        userId: String
    ) {
        self.apiClient = apiClient
        self.storage = storage
        self.userId = userId
        
        // Загружаем кешированные флаги
        loadCachedFlags()
        
        // Запускаем фоновое обновление
        startPeriodicRefresh()
    }
    
    // MARK: - FeatureFlagService Implementation
    
    func isEnabled(_ feature: Feature) -> Bool {
        let key = feature.rawValue
        
        // 1. Проверяем in-memory cache
        if let cached = cache[key] as? Bool {
            return cached
        }
        
        // 2. Проверяем persistent storage (offline support)
        if let stored = storage.get(key) as? Bool {
            cache[key] = stored
            return stored
        }
        
        // 3. Default value (feature disabled)
        return false
    }
    
    func getValue<T>(_ key: String, defaultValue: T) -> T {
        if let cached = cache[key] as? T {
            return cached
        }
        
        if let stored = storage.get(key) as? T {
            cache[key] = stored
            return stored
        }
        
        return defaultValue
    }
    
    func refresh() async throws {
        let context = FlagContext(
            userId: userId,
            platform: "ios",
            appVersion: Bundle.main.appVersion,
            osVersion: UIDevice.current.systemVersion,
            deviceModel: UIDevice.current.model,
            locale: Locale.current.identifier
        )
        
        let response = try await apiClient.fetchFeatureFlags(context: context)
        
        // Обновляем cache и storage
        updateFlags(response.flags)
        
        // Сохраняем для offline
        storage.save(response.flags)
        
        lastRefreshTime = Date()
    }
    
    func observe(_ feature: Feature, handler: @escaping (Bool) -> Void) {
        let key = feature.rawValue
        if observers[key] == nil {
            observers[key] = []
        }
        observers[key]?.append(handler)
    }
    
    // MARK: - Private Methods
    
    private func loadCachedFlags() {
        if let stored = storage.getAll() as? [String: Any] {
            cache = stored
        }
    }
    
    private func updateFlags(_ flags: [String: Any]) {
        let oldCache = cache
        cache = flags
        
        // Уведомляем observers об изменениях
        for (key, value) in flags {
            if let newValue = value as? Bool,
               let oldValue = oldCache[key] as? Bool,
               newValue != oldValue {
                observers[key]?.forEach { $0(newValue) }
            }
        }
    }
    
    private func startPeriodicRefresh() {
        Task {
            while true {
                try? await Task.sleep(nanoseconds: UInt64(refreshInterval * 1_000_000_000))
                try? await refresh()
            }
        }
    }
}

// MARK: - Supporting Types

struct FlagContext: Encodable {
    let userId: String
    let platform: String
    let appVersion: String
    let osVersion: String
    let deviceModel: String
    let locale: String
}

struct FlagResponse: Decodable {
    let flags: [String: Bool]
    let configs: [String: AnyCodable]
    let ttl: Int // Time to live в секундах
}
```

### Использование в приложении

#### В UI Layer

```swift
// MARK: - ViewController

class CheckoutViewController: UIViewController {
    
    private let featureFlags: FeatureFlagService
    private let viewModel: CheckoutViewModel
    
    init(featureFlags: FeatureFlagService, viewModel: CheckoutViewModel) {
        self.featureFlags = featureFlags
        self.viewModel = viewModel
        super.init(nibName: nil, bundle: nil)
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        if featureFlags.isEnabled(.newCheckoutFlow) {
            setupNewCheckoutUI()
            analytics.track("checkout_variant", properties: ["version": "new"])
        } else {
            setupOldCheckoutUI()
            analytics.track("checkout_variant", properties: ["version": "old"])
        }
        
        // Подписываемся на изменения (для real-time updates)
        featureFlags.observe(.newCheckoutFlow) { [weak self] isEnabled in
            // Feature flag изменился в runtime
            if isEnabled {
                self?.migrateToNewUI()
            } else {
                self?.revertToOldUI()
            }
        }
    }
    
    private func setupNewCheckoutUI() {
        // Новый UI с улучшенным UX
        let newView = NewCheckoutView()
        view.addSubview(newView)
    }
    
    private func setupOldCheckoutUI() {
        // Старый, проверенный UI
        let oldView = OldCheckoutView()
        view.addSubview(oldView)
    }
}
```

#### В Business Logic Layer

```swift
// MARK: - Payment Service

class PaymentService {
    
    private let featureFlags: FeatureFlagService
    private let oldProvider: PaymentProvider
    private let newProvider: PaymentProvider
    
    func processPayment(_ request: PaymentRequest) async throws -> PaymentResult {
        // Проверяем feature flag
        if featureFlags.isEnabled(.newPaymentProvider) {
            do {
                let result = try await newProvider.process(request)
                
                // Логируем успех с новым провайдером
                analytics.track("payment_success", properties: [
                    "provider": "new",
                    "amount": request.amount
                ])
                
                return result
            } catch {
                // При ошибке падаем обратно на старый провайдер
                logger.error("New payment provider failed, falling back to old", error: error)
                return try await oldProvider.process(request)
            }
        } else {
            // Используем старый, проверенный провайдер
            return try await oldProvider.process(request)
        }
    }
}
```

#### В Network Layer

```swift
// MARK: - API Configuration

class APIConfiguration {
    
    private let featureFlags: FeatureFlagService
    
    var baseURL: String {
        // Можем менять API endpoint через feature flags
        if featureFlags.isEnabled(.useNewAPI) {
            return "https://api-v2.example.com"
        } else {
            return "https://api.example.com"
        }
    }
    
    var timeout: TimeInterval {
        // Можем настраивать таймауты
        return featureFlags.getValue("network_timeout", defaultValue: 30.0)
    }
    
    var maxRetries: Int {
        return featureFlags.getValue("max_retries", defaultValue: 3)
    }
}
```

---

## 🎯 A/B Testing

### Реализация A/B Test Manager

```swift
// MARK: - A/B Test Manager

class ABTestManager {
    
    // MARK: - Types
    
    enum Variant: String {
        case control = "A"
        case treatment = "B"
        case treatmentB = "C"
    }
    
    struct Experiment {
        let id: String
        let name: String
        let variants: [Variant: Double] // Процентное распределение
        
        init(id: String, name: String, variants: [Variant: Double] = [.control: 0.5, .treatment: 0.5]) {
            self.id = id
            self.name = name
            
            // Нормализуем проценты до 1.0
            let total = variants.values.reduce(0, +)
            self.variants = variants.mapValues { $0 / total }
        }
    }
    
    // MARK: - Properties
    
    private let userId: String
    private let storage: LocalStorage
    private let analytics: Analytics
    private var assignments: [String: Variant]
    
    // MARK: - Initialization
    
    init(userId: String, storage: LocalStorage, analytics: Analytics) {
        self.userId = userId
        self.storage = storage
        self.analytics = analytics
        
        // Загружаем сохраненные assignments
        self.assignments = storage.get("ab_test_assignments") ?? [:]
    }
    
    // MARK: - Public Methods
    
    func getVariant(for experiment: Experiment) -> Variant {
        // 1. Проверяем, есть ли уже assignment
        if let assigned = assignments[experiment.id] {
            return assigned
        }
        
        // 2. Deterministic assignment на основе userId
        // Это гарантирует, что пользователь всегда попадет в одну и ту же группу
        let seed = "\(userId)-\(experiment.id)"
        let hash = abs(seed.hashValue)
        let normalized = Double(hash % 10000) / 10000.0
        
        // 3. Распределяем по вариантам
        var cumulative = 0.0
        let sortedVariants = experiment.variants.sorted { $0.key.rawValue < $1.key.rawValue }
        
        for (variant, percentage) in sortedVariants {
            cumulative += percentage
            if normalized <= cumulative {
                // Сохраняем assignment
                assignments[experiment.id] = variant
                saveAssignments()
                
                // Логируем в аналитику
                analytics.track("experiment_assigned", properties: [
                    "experiment_id": experiment.id,
                    "experiment_name": experiment.name,
                    "variant": variant.rawValue
                ])
                
                return variant
            }
        }
        
        // Fallback (не должно произойти при правильной конфигурации)
        return .control
    }
    
    func trackExperimentView(_ experiment: Experiment, variant: Variant) {
        analytics.track("experiment_view", properties: [
            "experiment_id": experiment.id,
            "variant": variant.rawValue
        ])
    }
    
    func trackExperimentConversion(_ experiment: Experiment, variant: Variant, value: Double? = nil) {
        var properties: [String: Any] = [
            "experiment_id": experiment.id,
            "variant": variant.rawValue
        ]
        
        if let value = value {
            properties["value"] = value
        }
        
        analytics.track("experiment_conversion", properties: properties)
    }
    
    // MARK: - Private Methods
    
    private func saveAssignments() {
        storage.save(assignments, forKey: "ab_test_assignments")
    }
}
```

### Примеры использования A/B Testing

#### Пример 1: A/B тест нового checkout flow

```swift
// MARK: - Checkout A/B Test

let checkoutExperiment = ABTestManager.Experiment(
    id: "checkout_flow_v2",
    name: "New Checkout Flow Test",
    variants: [
        .control: 0.5,    // 50% - старый flow
        .treatment: 0.5   // 50% - новый flow
    ]
)

class CheckoutCoordinator {
    
    private let abTestManager: ABTestManager
    
    func startCheckout() {
        let variant = abTestManager.getVariant(for: checkoutExperiment)
        
        // Логируем показ эксперимента
        abTestManager.trackExperimentView(checkoutExperiment, variant: variant)
        
        switch variant {
        case .control:
            // Старый checkout flow
            let oldVC = OldCheckoutViewController()
            navigationController.push(oldVC)
            
        case .treatment:
            // Новый checkout flow
            let newVC = NewCheckoutViewController()
            navigationController.push(newVC)
            
        default:
            break
        }
    }
    
    func trackPurchaseCompleted(amount: Double) {
        let variant = abTestManager.getVariant(for: checkoutExperiment)
        
        // Логируем конверсию
        abTestManager.trackExperimentConversion(
            checkoutExperiment,
            variant: variant,
            value: amount
        )
        
        // Дополнительная аналитика
        analytics.track("purchase_completed", properties: [
            "amount": amount,
            "checkout_variant": variant.rawValue
        ])
    }
}
```

#### Пример 2: Multi-variant тест (A/B/C)

```swift
// MARK: - Onboarding Multi-Variant Test

let onboardingExperiment = ABTestManager.Experiment(
    id: "onboarding_screens_v3",
    name: "Onboarding Screens Test",
    variants: [
        .control: 0.33,      // 33% - 5 экранов
        .treatment: 0.33,    // 33% - 3 экрана
        .treatmentB: 0.34    // 34% - 1 экран
    ]
)

class OnboardingViewController: UIViewController {
    
    private let abTestManager: ABTestManager
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        let variant = abTestManager.getVariant(for: onboardingExperiment)
        abTestManager.trackExperimentView(onboardingExperiment, variant: variant)
        
        switch variant {
        case .control:
            setupFiveScreenOnboarding()
        case .treatment:
            setupThreeScreenOnboarding()
        case .treatmentB:
            setupOneScreenOnboarding()
        }
    }
    
    func onOnboardingCompleted() {
        let variant = abTestManager.getVariant(for: onboardingExperiment)
        abTestManager.trackExperimentConversion(onboardingExperiment, variant: variant)
    }
}
```

---

## 🚀 Стратегии Rollout

### 1. Percentage-based Rollout

```swift
class PercentageRollout {
    
    private let userId: String
    
    func shouldShowFeature(_ feature: Feature, percentage: Int) -> Bool {
        // percentage: 0-100
        let hash = abs("\(userId)-\(feature.rawValue)".hashValue)
        return (hash % 100) < percentage
    }
}

// Использование
let rollout = PercentageRollout(userId: currentUser.id)

// 25% пользователей видят новую feature
if rollout.shouldShowFeature(.newRecommendations, percentage: 25) {
    showNewRecommendations()
} else {
    showOldRecommendations()
}
```

### 2. User Attribute Targeting

```swift
class TargetedRollout {
    
    private let user: User
    private let featureFlags: FeatureFlagService
    
    func shouldShowFeature(_ feature: Feature) -> Bool {
        guard featureFlags.isEnabled(feature) else {
            return false
        }
        
        // Проверяем targeting rules
        switch feature {
        case .betaFeatures:
            return user.isBetaTester
            
        case .premiumFeatures:
            return user.hasPremiumSubscription
            
        case .regionSpecificFeature:
            return ["US", "UK", "CA"].contains(user.countryCode)
            
        case .iosNewFeature:
            return user.iosVersion >= 17.0
            
        default:
            return true
        }
    }
}
```

### 3. Gradual Rollout Schedule

```swift
struct RolloutSchedule {
    let startDate: Date
    let stages: [(days: Int, percentage: Int)]
    
    static let standard = RolloutSchedule(
        startDate: Date(),
        stages: [
            (days: 0, percentage: 5),    // Day 1: 5%
            (days: 2, percentage: 10),   // Day 3: 10%
            (days: 4, percentage: 25),   // Day 5: 25%
            (days: 7, percentage: 50),   // Day 8: 50%
            (days: 10, percentage: 100)  // Day 11: 100%
        ]
    )
    
    func currentPercentage() -> Int {
        let daysSinceStart = Calendar.current.dateComponents(
            [.day],
            from: startDate,
            to: Date()
        ).day ?? 0
        
        // Находим текущий stage
        for stage in stages.reversed() {
            if daysSinceStart >= stage.days {
                return stage.percentage
            }
        }
        
        return 0
    }
}
```

---

## 🔧 Backend API

### API Endpoint

```
GET /api/v1/feature-flags
Headers:
  Authorization: Bearer <token>
  X-User-ID: <userId>
  X-Platform: ios
  X-App-Version: 2.1.0
  X-OS-Version: 17.2
  X-Device-Model: iPhone15,3
  X-Locale: en_US

Response 200 OK:
{
  "flags": {
    "new_checkout_flow": true,
    "dark_mode_ui": false,
    "premium_features": true,
    "experimental_search": false
  },
  "configs": {
    "network_timeout": 30.0,
    "max_retries": 3,
    "cache_ttl": 3600,
    "image_quality": 0.8
  },
  "experiments": {
    "checkout_experiment_001": {
      "variant": "B",
      "experimentId": "exp_checkout_001",
      "experimentName": "New Checkout Flow"
    },
    "onboarding_experiment_002": {
      "variant": "A",
      "experimentId": "exp_onboarding_002",
      "experimentName": "Simplified Onboarding"
    }
  },
  "rollouts": {
    "new_recommendation_engine": {
      "enabled": true,
      "percentage": 25,
      "targetingRules": {
        "countries": ["US", "UK", "CA"],
        "minAppVersion": "2.0.0",
        "userAttributes": {
          "isPremium": true
        }
      }
    }
  },
  "ttl": 3600,
  "refreshAfter": "2024-01-15T12:00:00Z"
}
```

### Targeting Rules на Backend

```json
{
  "feature": "premium_video_quality",
  "enabled": true,
  "targetingRules": {
    "all": [
      {
        "attribute": "subscription",
        "operator": "equals",
        "value": "premium"
      },
      {
        "attribute": "appVersion",
        "operator": "greaterThanOrEqual",
        "value": "2.1.0"
      }
    ],
    "any": [
      {
        "attribute": "country",
        "operator": "in",
        "value": ["US", "UK", "CA", "AU"]
      },
      {
        "attribute": "isBetaTester",
        "operator": "equals",
        "value": true
      }
    ]
  },
  "rolloutPercentage": 50
}
```

---

## 📊 Мониторинг и Analytics

### Метрики для отслеживания

```swift
class FeatureFlagAnalytics {
    
    private let analytics: Analytics
    
    // Exposure tracking
    func trackFeatureExposure(_ feature: Feature, isEnabled: Bool) {
        analytics.track("feature_flag_exposure", properties: [
            "feature": feature.rawValue,
            "enabled": isEnabled,
            "timestamp": Date().iso8601String
        ])
    }
    
    // Experiment metrics
    func trackExperimentMetrics(_ experiment: ABTestManager.Experiment, variant: ABTestManager.Variant) {
        analytics.track("experiment_metrics", properties: [
            "experiment_id": experiment.id,
            "variant": variant.rawValue,
            "session_duration": sessionDuration,
            "screens_viewed": screensViewed,
            "actions_completed": actionsCompleted
        ])
    }
    
    // Conversion tracking
    func trackConversion(
        event: String,
        experiment: ABTestManager.Experiment,
        variant: ABTestManager.Variant,
        value: Double? = nil
    ) {
        var properties: [String: Any] = [
            "event": event,
            "experiment_id": experiment.id,
            "variant": variant.rawValue
        ]
        
        if let value = value {
            properties["value"] = value
        }
        
        analytics.track("conversion", properties: properties)
    }
    
    // Error tracking
    func trackFeatureFlagError(_ error: Error, feature: Feature) {
        analytics.track("feature_flag_error", properties: [
            "feature": feature.rawValue,
            "error": error.localizedDescription,
            "timestamp": Date().iso8601String
        ])
    }
}
```

### Dashboard метрики

Что отслеживать для A/B тестов:
- **Sample size** — количество пользователей в каждой группе
- **Conversion rate** — процент пользователей, совершивших целевое действие
- **Statistical significance** — достаточно ли данных для выводов (обычно p-value < 0.05)
- **Confidence interval** — диапазон, в котором находится истинное значение
- **Time to conversion** — сколько времени занимает конверсия
- **Secondary metrics** — дополнительные метрики (retention, engagement, revenue)

---

## ⚖️ Best Practices

### ✅ DO

1. **Именование флагов**
   ```swift
   // ✅ Good: описательное, понятное
   .newCheckoutFlow
   .darkModeEnabled
   .premiumFeaturesAccess
   
   // ❌ Bad: непонятное, generic
   .feature1
   .flag_x
   .temp
   ```

2. **Default values**
   ```swift
   // ✅ Always provide safe defaults
   func isEnabled(_ feature: Feature) -> Bool {
       return cache[feature.rawValue] ?? false // Safe default
   }
   ```

3. **Offline support**
   ```swift
   // ✅ Cache flags locally
   storage.save(flags)
   
   // Load cached on startup
   loadCachedFlags()
   ```

4. **Lifecycle management**
   ```swift
   // ✅ Temporary flags with expiration
   struct FeatureFlag {
       let key: String
       let enabled: Bool
       let expiresAt: Date?
       let reason: String // "rollout", "experiment", "killswitch"
   }
   
   // Remove expired flags
   func cleanupExpiredFlags() {
       flags = flags.filter { flag in
           guard let expiresAt = flag.expiresAt else { return true }
           return expiresAt > Date()
       }
   }
   ```

5. **Documentation**
   ```swift
   enum Feature: String {
       /// New checkout flow with improved UX
       /// Owner: @payments-team
       /// Jira: CHECKOUT-123
       /// Expected removal: Q2 2024
       case newCheckoutFlow = "new_checkout_flow"
   }
   ```

### ❌ DON'T

1. **Не оставляйте флаги навсегда**
   ```swift
   // ❌ Bad: flag живет годами
   if featureFlags.isEnabled(.experimentFrom2020) {
       // Старый код, который должен быть удален
   }
   
   // ✅ Good: после full rollout удаляем флаг и мертвый код
   showNewFeature() // Просто используем новую версию
   ```

2. **Не делайте слишком granular флаги**
   ```swift
   // ❌ Bad: слишком мелкие флаги
   .showLoginButton
   .loginButtonBlue
   .loginButtonText
   
   // ✅ Good: логические группы
   .newLoginFlow // Включает все связанные изменения
   ```

3. **Не делайте сложную вложенную логику**
   ```swift
   // ❌ Bad: сложная логика
   if featureFlags.isEnabled(.featureA) {
       if featureFlags.isEnabled(.featureB) {
           if !featureFlags.isEnabled(.featureC) {
               // Очень сложно понять
           }
       }
   }
   
   // ✅ Good: простая, линейная логика
   guard featureFlags.isEnabled(.newFeature) else {
       return showOldVersion()
   }
   return showNewVersion()
   ```

4. **Не забывайте про testing**
   ```swift
   // ✅ Mock для testing
   class MockFeatureFlagService: FeatureFlagService {
       var flags: [Feature: Bool] = [:]
       
       func isEnabled(_ feature: Feature) -> Bool {
           return flags[feature] ?? false
       }
   }
   
   // В тестах
   func testNewCheckoutFlow() {
       let mockFlags = MockFeatureFlagService()
       mockFlags.flags[.newCheckoutFlow] = true
       
       let viewModel = CheckoutViewModel(featureFlags: mockFlags)
       // Test new flow
   }
   ```

---

## 🔗 Популярные инструменты

### Firebase Remote Config
- **Плюсы:** Бесплатно, простая интеграция, real-time updates
- **Минусы:** Ограниченные возможности targeting, нет встроенного A/B testing dashboard
- **Best for:** Малые и средние приложения, быстрый старт

### LaunchDarkly
- **Плюсы:** Enterprise-level features, отличный UI, powerful targeting
- **Минусы:** Дорого, может быть overkill для малых проектов
- **Best for:** Большие команды, enterprise приложения

### Optimizely
- **Плюсы:** Фокус на A/B testing, статистический анализ, experimentation platform
- **Минусы:** Дорого, сложная настройка
- **Best for:** Product teams с фокусом на эксперименты

### Split.io
- **Плюсы:** Feature flagging + experimentation, хороший баланс цена/качество
- **Минусы:** Меньше известен чем LaunchDarkly
- **Best for:** Mid-size to large teams

### Custom Solution
- **Плюсы:** Полный контроль, нет внешних зависимостей, нет recurring costs
- **Минусы:** Нужно разрабатывать и поддерживать самим
- **Best for:** Специфические требования, security-critical apps

---

## 💻 Примеры

```dataview
TABLE file.link AS "Пример", status
FROM "Examples"
WHERE contains(topics, "feature-flags") OR contains(topics, "ab-testing")
SORT file.name ASC
```

## ⚠️ Антипаттерны

```dataview
LIST
FROM "Antipatterns"
WHERE contains(topics, "feature-flags") OR contains(topics, "ab-testing")
```

## 🔗 Связанные темы

- [[Architecture]] — архитектурные подходы
- [[dependency-injection]] — DI для feature flags
- [[testing]] — тестирование с feature flags
- [[analytics]] — аналитика и метрики
- [[remote-config]] — remote configuration


