---
title: Swinject — Dependency Injection для Swift
type: thread
topics:
  - 3rd Party Libraries
subtopic: Dependency Injection
status: draft
---

# Swinject

Swinject — это контейнер внедрения зависимостей (DI) для Swift/iOS/macOS, поддерживающий модульность через `Assembly` и управляемые области жизни (`ObjectScope`).

- Когда использовать: средние и большие проекты, модульная архитектура, требование переиспользуемых конфигураций и удобного мокинга в тестах.
- Когда не использовать: маленькие приложения/прототипы, где достаточно ручного DI (передача зависимостей через инициализаторы без контейнера).

## Установка

### Swift Package Manager (рекомендуется)

- Xcode → File → Add Packages → `https://github.com/Swinject/Swinject`
- Дополнительно по необходимости: `https://github.com/Swinject/SwinjectAutoregistration`, `https://github.com/Swinject/SwinjectStoryboard`

Пример `Package.swift`:

```swift
dependencies: [
    .package(url: "https://github.com/Swinject/Swinject", from: "2.8.0"),
    .package(url: "https://github.com/Swinject/SwinjectAutoregistration", from: "2.8.0"),
]
```

### CocoaPods

```ruby
pod 'Swinject'
pod 'SwinjectAutoregistration' # опционально
pod 'SwinjectStoryboard'       # при использовании UIKit Storyboard
```

## Ключевые понятия

- `Container`/`Resolver` — регистрация и разрешение зависимостей.
- `Assembly` — модуль регистрации (инкапсулирует конфигурацию фичи/подсистемы).
- `Assembler` — агрегатор `Assembly` для сборки общего контейнера.
- `ObjectScope` — область жизни: `.transient`, `.graph`, `.container`, `.weak`.

## Быстрый старт

```swift
import Swinject

protocol AnalyticsService { func track(_ event: String) }
final class FirebaseAnalyticsService: AnalyticsService { func track(_ event: String) { /* ... */ } }

let container = Container()
container.register(AnalyticsService.self) { _ in
    FirebaseAnalyticsService()
}.inObjectScope(.container) // singleton в рамках контейнера

let analytics = container.resolve(AnalyticsService.self)!
analytics.track("App Launched")
```

## Архитектура через Assemblies

```swift
import Swinject

final class NetworkingAssembly: Assembly {
    func assemble(container: Container) {
        container.register(URLSession.self) { _ in URLSession(configuration: .default) }
            .inObjectScope(.container)

        container.register(APIClient.self) { r in
            DefaultAPIClient(session: r.resolve(URLSession.self)!)
        }.inObjectScope(.container)
    }
}

final class FeatureAAssembly: Assembly {
    func assemble(container: Container) {
        container.register(FeatureAViewModel.self) { r in
            FeatureAViewModel(api: r.resolve(APIClient.self)!)
        }.inObjectScope(.graph) // на время графа разрешения (экрана)
    }
}

let assembler = Assembler([
    NetworkingAssembly(),
    FeatureAAssembly(),
])
let resolver = assembler.resolver
```

## UIKit: SwinjectStoryboard (Storyboard-инъекция)

```swift
import Swinject
import SwinjectStoryboard

extension SwinjectStoryboard {
    @objc class func setup() {
        defaultContainer.register(AnalyticsService.self) { _ in FirebaseAnalyticsService() }
            .inObjectScope(.container)

        defaultContainer.storyboardInitCompleted(HomeViewController.self) { r, c in
            c.analytics = r.resolve(AnalyticsService.self)
        }
    }
}
```

## SwiftUI: интеграция через Environment/обертки

Официальной интеграции через `@propertyWrapper` нет, но можно добавить слой:

```swift
import SwiftUI
import Swinject

private struct ResolverKey: EnvironmentKey {
    static let defaultValue: Resolver = Assembler([]).resolver
}

extension EnvironmentValues {
    var resolver: Resolver {
        get { self[ResolverKey.self] }
        set { self[ResolverKey.self] = newValue }
    }
}

@propertyWrapper
struct Inject<Service> {
    @Environment(\.resolver) private var resolver
    var wrappedValue: Service { resolver.resolve(Service.self)! }
}

struct ContentView: View {
    @Inject var analytics: AnalyticsService
    var body: some View { Text("Hello").onAppear { analytics.track("open") } }
}

@main
struct AppMain: App {
    private let assembler = Assembler([NetworkingAssembly(), FeatureAAssembly()])
    var body: some Scene {
        WindowGroup {
            ContentView().environment(\.resolver, assembler.resolver)
        }
    }
}
```

## Боевые кейсы

### 1) Синглтоны инфраструктуры через `.container`

```swift
container.register(APIClient.self) { r in DefaultAPIClient(session: r.resolve(URLSession.self)!) }
    .inObjectScope(.container)
```

Когда: клиенты БД/сети/логгеры. Плюс — единый пул ресурсов; минус — осознайте время жизни для тестов.

### 2) Экземпляры на экран через `.graph`

```swift
container.register(FeatureAViewModel.self) { r in FeatureAViewModel(api: r.resolve(APIClient.self)!) }
    .inObjectScope(.graph)
```

Когда: `ViewModel`, координирующие объекты, завязанные на жизненный цикл экрана.

### 3) Аргументы при разрешении (Detail экраны)

```swift
container.register(UserDetailViewModel.self) { (r: Resolver, userId: String) in
    UserDetailViewModel(userId: userId, api: r.resolve(APIClient.self)!)
}

let vm = container.resolve(UserDetailViewModel.self, argument: "42")
```

### 4) Авто-регистрация (уменьшение бойлерплейта)

```swift
import SwinjectAutoregistration

container.autoregister(AnalyticsService.self, initializer: FirebaseAnalyticsService.init)
    .inObjectScope(.container)
```

Когда: много простых биндингов интерфейс→имплементация. Пакет: `SwinjectAutoregistration`.

### 5) Круговые зависимости (разрываем через `initCompleted`)

```swift
final class A { weak var b: B? }
final class B { weak var a: A? }

container.register(A.self) { _ in A() }
    .initCompleted { r, a in a.b = r.resolve(B.self) }
    .inObjectScope(.container)

container.register(B.self) { _ in B() }
    .initCompleted { r, b in b.a = r.resolve(A.self) }
    .inObjectScope(.container)
```

Важно: используйте `weak` для разрыва retain cycle и избегайте таких связей в дизайне.

### 6) Потоки: безопасное разрешение

- Регистрируйте зависимости на старте приложения, до доступа из потоков.
- Для многопоточной резолюции используйте обертку:

```swift
let syncResolver = container.synchronize() // SynchronizedResolver
let service = syncResolver.resolve(AnalyticsService.self)
```

### 7) Тестирование и переопределение зависимостей

```swift
final class StubAnalytics: AnalyticsService { func track(_ event: String) {} }

let testAssembler = Assembler([
    NetworkingAssembly(),
    FeatureAAssembly(),
])

// Переопределение в тестах
testAssembler.apply(assemblies: [
    BasicAssembly { container in
        container.register(AnalyticsService.self) { _ in StubAnalytics() }
            .inObjectScope(.container)
    }
])
```

Или создавайте отдельный контейнер в каждом тесте для изоляции.

### 8) Модульность и фичи

- Каждая фича публикует свой `Assembly`.
- Корневой `Assembler` агрегирует фичи, а в рантайме можно подключать/отключать сборки.

## Шаблон BaseAssembly (утилита)

```swift
final class BasicAssembly: Assembly {
    private let configure: (Container) -> Void
    init(configure: @escaping (Container) -> Void) { self.configure = configure }
    func assemble(container: Container) { configure(container) }
}
```

## Антипаттерны

- Глобальный доступ к контейнеру из любого места (Service Locator). Предпочитайте конструкторную инъекцию.
- Регистрация во время резолюции/на лету. Всю регистрацию — при старте.
- Глубокая резолюция в доменном коде. Инжектируйте зависимости в верхних слоях (композиционный корень).

## Рецепты интеграции

- UIKit без Storyboard: фабрики координаторов/контроллеров через `Assembly`.
- SwiftUI Previews: создавайте lightweight-assembler с стабами.
- App Extensions/Widgets: отдельный контейнер/assembler на каждый таргет.

## Сравнение с альтернативами

Критерии: безопасность (compile-time), производительность, эргономика, области жизни, интеграции, зрелость.

| Библиотека | Тип | Безопасность | Перфоманс | Области жизни | SwiftUI | Storyboard | Autoreg | Порог входа |
|---|---|---|---|---|---|---|---|---|
| Swinject | Рантайм-контейнер | Рантайм-проверки | Высокая | Да (.container/.graph/.transient/.weak) | Через обертки | Да (SwinjectStoryboard) | Да (отдельный пакет) | Средний |
| Resolver | Рантайм-контейнер | Рантайм-проверки | Высокая | Да | Да (property wrappers) | Нет | Нет | Низкий |
| Needle | Codegen (Uber) | Компайл-тайм | Очень высокая | Да | Опционально | Нет | Нет | Выше среднего |
| Cleanse | Codegen/модульная конфигурация | Компайл-тайм | Очень высокая | Да | Опционально | Нет | Нет | Высокий |
| Factory | Рантайм-контейнер | Рантайм-проверки | Высокая | Да | Да (property wrappers) | Нет | Нет | Низкий |
| Manual DI | Без контейнера | Компайл-тайм (явные конструкторы) | Очень высокая | Ручное | Да | Да | — | Низкий/Средний |

Примечания:
- Swinject выделяется поддержкой Storyboard и богатыми областями жизни, хорош для модульности.
- Needle/Cleanse дают compile-time гарантий больше, но требуют генерации кода и более строгой структуры.
- Resolver/Factory удобны в SwiftUI за счет property wrappers.

## Когда выбрать Swinject

- Нужна модульность и единая точка конфигурации через `Assembly`/`Assembler`.
- Нужна Storyboard-инъекция в UIKit.
- Требуются разные области жизни и аргументы при создании объектов.

## Ссылки внутри хранилища

- См. раздел «Популярные библиотеки» → [[Популярные библиотеки]].
- См. архитектурную заметку «Dependency Injection» → [[dependency-injection]].




