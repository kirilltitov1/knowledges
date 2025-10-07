---
title: Custom Notification Center
type: example
topics: [Design Patterns, Architecture]
subtopic: Паттерны проектирования
level: intermediate
platforms: [iOS, macOS]
ios_min: "13.0"
status: complete
tags: [observer-pattern, type-safe, notifications, event-bus]
---

## Цель
Типобезопасный notification center для замены стандартного `NotificationCenter`. Позволяет избежать строковых констант и опциональных значений, предоставляя compile-time проверку типов.

## Код

```swift
import Foundation

// Ему следуют все классы, которые могут получать события от нотификейшн центра.
protocol Observer: AnyObject {
    func observe(
		    event: String, 
		    object: Any?, 
		    notificationCenter: CustomNotificationCenter
		)
}

// Является интерфейсом для CustomNotificationCenter
protocol Observable {
    func add(_ observer: Observer, forEvent event: String)
    func remove(_ observer: Observer, forEvent event: String)
    func post(event: String, object: Any?)
    func hasObserver(_ observer: Observer, forEvent event: String) -> Bool
}

final class WeakObserver: Hashable {

	weak var observer: Observer?

	init(_ observer: Observer) {
		self.observer = observer
	}

	func hash(into hasher: inout Hasher) {
		guard let observer = observer else { return }
		hasher.combine(ObjectIdentifier(observer))
	}

	static func == (lhs: WeakObserver, rhs: WeakObserver) -> Bool {
		guard let lObserver = lhs.observer,
				let rObserver = rhs.observer else { return false }
		return ObjectIdentifier(lObserver) == ObjectIdentifier(rObserver)
	}
}
final class CustomNotificationCenter: Observable {
    
    static let shared = CustomNotificationCenter()
    
    private var observers = [String: Set<WeakObserver>]()
    private let queue = DispatchQueue(
		    label: "CustomNotificationCenter", 
		    attributes: .concurrent
		)
    
    private init() {}

    func add(_ observer: Observer, forEvent event: String) {
        queue.async(flags: .barrier) { [weak self] in
            guard let self else { return }
            let weakObserver = WeakObserver(observer)
            self.observers[event, default: []].insert(weakObserver)
        }
    }

    func remove(_ observer: Observer, forEvent event: String) {
        queue.async(flags: .barrier) { [weak self] in
            guard let self else { return }
            let weakObserver = WeakObserver(observer)
            self.observers[event]?.remove(weakObserver)
        }
    }
    
    func post(event: String, object: Any?) {
        queue.sync {
            observers[event]?.forEach {
                $0.observer?.observe(event: event, object: object, notificationCenter: self)
            }
        }
    }
    
    func hasObserver(_ observer: Observer, forEvent event: String) -> Bool {
        queue.sync {
            let weakObserver = WeakObserver(observer)
            return observers[event]?.contains(weakObserver) ?? false
        }
    }
}
```

## Использование

### Определение уведомлений

```swift
// Определяем типы уведомлений
enum Notifications {
    
    struct UserLoggedIn: NotificationDescriptor {
        static let name = "user.logged.in"
        typealias Payload = User
    }
    
    struct CartUpdated: NotificationDescriptor {
        static let name = "cart.updated"
        typealias Payload = CartInfo
    }
    
    struct NetworkError: NotificationDescriptor {
        static let name = "network.error"
        typealias Payload = Error
    }
}

struct User {
    let id: String
    let name: String
}

struct CartInfo {
    let itemCount: Int
    let totalPrice: Decimal
}
```

### Подписка и отправка

```swift
// Подписка на уведомление
class ProfileViewController: UIViewController {
    private var tokens: [ObservationToken] = []
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        let token = TypedNotificationCenter.shared.addObserver(
            Notifications.UserLoggedIn.self
        ) { [weak self] user in
            self?.updateProfile(with: user)
        }
        
        tokens.append(token)
    }
    
    private func updateProfile(with user: User) {
        // Обновляем UI с данными пользователя
        print("User logged in: \(user.name)")
    }
}

// Отправка уведомления
class AuthService {
    func login(email: String, password: String) async throws {
        // ... логика авторизации
        let user = User(id: "123", name: "John Doe")
        
        // Отправляем типобезопасное уведомление
        TypedNotificationCenter.shared.post(
            Notifications.UserLoggedIn.self,
            payload: user
        )
    }
}
```

### Использование с Combine

```swift
import Combine

class CartViewModel: ObservableObject {
    @Published var itemCount = 0
    @Published var totalPrice: Decimal = 0
    
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        CombineNotificationCenter.shared
            .publisher(for: Notifications.CartUpdated.self)
            .sink { [weak self] cartInfo in
                self?.itemCount = cartInfo.itemCount
                self?.totalPrice = cartInfo.totalPrice
            }
            .store(in: &cancellables)
    }
}

// Отправка
class CartService {
    func addItem(_ item: Product) {
        // ... добавление товара
        let cartInfo = CartInfo(itemCount: 5, totalPrice: 99.99)
        
        CombineNotificationCenter.shared.post(
            Notifications.CartUpdated.self,
            payload: cartInfo
        )
    }
}
```

### Управление подписками

```swift
class MyViewController: UIViewController {
    private var observationToken: ObservationToken?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Сохраняем токен
        observationToken = TypedNotificationCenter.shared.addObserver(
            Notifications.UserLoggedIn.self
        ) { user in
            print("User: \(user.name)")
        }
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        
        // Вручную отменяем подписку
        observationToken?.cancel()
    }
    
    // Или просто позволяем токену очиститься при deinit
    deinit {
        // observationToken автоматически вызовет cancel()
    }
}
```

## Преимущества

1. **Типобезопасность** — компилятор проверяет типы payload во время компиляции
2. **Автодополнение** — IDE подсказывает доступные уведомления и их payload
3. **Нет строковых констант** — невозможно опечататься в имени уведомления
4. **Автоматическая отписка** — через `ObservationToken` и deinit
5. **Поддержка Combine** — интеграция с реактивным программированием
6. **Тестируемость** — легко мокировать для unit-тестов

## Недостатки

1. Больше boilerplate кода при создании новых уведомлений
2. Нет прямой интеграции с system notifications (UIKeyboardWillShow и т.д.)
3. Требует создания отдельных типов для каждого уведомления

## Альтернативы

- **NotificationCenter** — стандартное решение от Apple
- **Combine** — для реактивного программирования
- **Делегаты** — для 1-to-1 коммуникации
- **Closures/Callbacks** — для простых случаев
- **RxSwift** — сторонняя библиотека для реактивного программирования

## Заметки

- Используйте этот подход когда нужна глобальная система событий с compile-time проверками
- Для локальной коммуникации между 2 объектами лучше использовать делегаты
- При работе с Combine рассмотрите использование `CombineNotificationCenter`
- Не забывайте управлять жизненным циклом токенов во избежание retain cycles
- Для system notifications создайте обертки в виде `NotificationDescriptor`

## Расширения

### Добавление приоритетов

```swift
public enum NotificationPriority {
    case low, normal, high
}

// Расширьте TypedNotificationCenter для поддержки приоритетов
extension TypedNotificationCenter {
    public func post<N: NotificationDescriptor>(
        _ descriptor: N.Type,
        payload: N.Payload,
        priority: NotificationPriority = .normal
    ) {
        let queue: DispatchQueue
        switch priority {
        case .low:
            queue = .global(qos: .utility)
        case .normal:
            queue = .global(qos: .default)
        case .high:
            queue = .global(qos: .userInitiated)
        }
        
        queue.async {
            self.center.post(
                name: Notification.Name(N.name),
                object: payload
            )
        }
    }
}
```

### Дебаг-логирование

```swift
extension TypedNotificationCenter {
    public func enableDebugLogging() {
        // Добавьте логирование всех уведомлений
        center.addObserver(
            forName: nil,
            object: nil,
            queue: nil
        ) { notification in
            print("📢 Notification posted: \(notification.name.rawValue)")
        }
    }
}
```

## См. также

- [[behavioral-patterns]] — Observer Pattern
- [[iOS/Design Patterns/Design Patterns]] — Паттерны проектирования
- [[networking-generic-api-client]] — Типобезопасный API клиент

