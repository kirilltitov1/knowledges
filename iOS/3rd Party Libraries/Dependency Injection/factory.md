---
title: Factory — Лёгкий DI для Swift
type: thread
topics:
  - 3rd Party Libraries
subtopic: Dependency Injection
status: draft
---

# Factory

Минималистичный DI с `@Injected`/фабриками, ориентирован на SwiftUI.

## Быстрый старт

```swift
import Factory

protocol AnalyticsService { func track(_ event: String) }
final class FirebaseAnalytics: AnalyticsService { func track(_ event: String) {} }

extension Container {
    var analytics: Factory<AnalyticsService> { self { FirebaseAnalytics() }.singleton }
}

struct ContentView: View {
    @Injected(\.analytics) var analytics: AnalyticsService
    var body: some View { Text("Hi").onAppear { analytics.track("open") } }
}
```

## Когда выбрать

- Нужен простой DI без тяжелых контейнеров, упор на SwiftUI и читаемость.




