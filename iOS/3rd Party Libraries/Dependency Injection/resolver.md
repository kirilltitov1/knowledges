---
type: "thread"
status: "draft"
summary: ""
title: "resolver"
---

# Resolver

Лёгкий DI-контейнер с `@propertyWrapper` интеграцией для SwiftUI/UIKit.

## Установка (SPM)

- Xcode → Add Packages → `https://github.com/hmlongco/Resolver`

## Быстрый старт

```swift
import Resolver

protocol AnalyticsService { func track(_ event: String) }
final class FirebaseAnalytics: AnalyticsService { func track(_ event: String) {} }

extension Resolver: ResolverRegistering {
    public static func registerAllServices() {
        register { FirebaseAnalytics() as AnalyticsService }
            .scope(.application)
    }
}

struct ContentView: View {
    @Injected var analytics: AnalyticsService
    var body: some View { Text("Hello").onAppear { analytics.track("open") } }
}
```

## Особенности

- Регистрация через `Resolver.register { ... }` и области `.application/.shared/.cached/.unique`.
- Property wrappers: `@Injected`, `@LazyInjected`, `@OptionalInjected`.
- Поддержка именованных регистраций и аргументов.

## Кейсы

- SwiftUI-инъекция через property wrappers без доп. оберток.
- Тесты: переопределение регистраций внутри `Resolver.root = .init()` для изоляции.

## Когда выбрать

- Нужна простая интеграция с SwiftUI и минимальный бойлерплейт.




