---
type: "thread"
status: "draft"
title: "Паттерны и архитектуры конкурентности"
subtopic: "Паттерны"
---

# Паттерны и архитектуры конкурентности

## Fan-out/Fan-in (агрегация)
- GCD: `DispatchGroup`
- Swift Concurrency: `with(Throwing)TaskGroup`

## Readers-Writer Cache (barrier)
```swift
final class SafeCache {
    private var storage: [String: Data] = [:]
    private let queue = DispatchQueue(label: "cache", attributes: .concurrent)
    func get(_ key: String) -> Data? { var r: Data?; queue.sync { r = storage[key] }; return r }
    func set(_ key: String, _ value: Data) { queue.async(flags: .barrier) { self.storage[key] = value } }
}
```

## Producers-Consumers (ограничение параллелизма)
- Семафор в GCD
- Батчинг задач в TaskGroup

## UI-bound pipelines
- Фоновая работа + `@MainActor` для обновлений

## Orchestration
- Operation dependencies / последовательные `await`

## Чек-лист
- Ограничивайте параллелизм
- Изолируйте общий стейт (акторы/барьеры)
- Обновления UI — только на main


