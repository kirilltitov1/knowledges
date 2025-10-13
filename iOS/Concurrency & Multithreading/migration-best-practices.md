---
type: "thread"
status: "draft"
summary: ""
title: "Migration Best Practices"
---

# Migration & Best Practices

### GCD → Async/Await

#### Before (GCD)
```swift
func fetchData(completion: @escaping (Result<Data, Error>) -> Void) {
    DispatchQueue.global().async {
        // Fetch data
        DispatchQueue.main.async {
            completion(.success(data))
        }
    }
}
```

#### After (Async/Await)
```swift
func fetchData() async throws -> Data {
    try await URLSession.shared.data(from: url).0
}
```

### Callbacks → Async/Await

#### Before (Callback Hell)
```swift
fetchUser { user in
    fetchPosts(for: user) { posts in
        fetchComments(for: posts) { comments in
            updateUI(with: comments)
        }
    }
}
```

#### After (Async/Await)
```swift
let user = await fetchUser()
let posts = await fetchPosts(for: user)
let comments = await fetchComments(for: posts)
await updateUI(with: comments)
```

### Combine → Async/Await

#### Publisher to Async
```swift
let values = publisher.values
for await value in values {
    print(value)
}
```

### When to Use What

#### Use GCD when:
- Simple background tasks
- Fire-and-forget operations
- Legacy code maintenance
- Need fine-grained control

#### Use Operations when:
- Complex dependencies
- Need cancellation
- Reusable operations
- Priority management

#### Use Async/Await when:
- Modern Swift (iOS 15+)
- Sequential async code
- Better readability
- Structured concurrency needed

#### Use Actors when:
- Shared mutable state
- Data race prevention
- Thread-safe by design

#### Use Combine when:
- Reactive patterns
- Event streams
- SwiftUI integration
- Complex data transformations

#### Use RxSwift when:
- Existing RxSwift codebase
- Cross-platform (RxJava, RxJS)
- Need mature ecosystem

## Подводные камни и рецепты

- Detached tasks вместо `Task {}` → теряете отмену/приоритет. Используйте `Task {}`.
- Двойной `resume` в continuations → только `withChecked*`, защитные флаги.
- Блокировка `@MainActor` тяжёлой работой → вынос на фон + возврат на main для UI.
- Смешение парадигм «ради миграции» → делайте мосты локально, не размазывайте.
- Забытая отмена при переходе экранов → храните `Task` и отменяйте в `deinit`/`onDisappear`.

### Рецепт: миграция GCD group → TaskGroup
```swift
func loadAll(urls: [URL]) async throws -> [Data] {
    try await withThrowingTaskGroup(of: Data.self) { group in
        for url in urls { group.addTask { try await fetch(url) } }
        var result: [Data] = []
        for try await data in group { result.append(data) }
        return result
    }
}
```

### Рецепт: ограничение до N параллельных задач
```swift
func processLimited<T>(_ items: [T], limit: Int) async {
    var index = 0
    while index < items.count {
        let slice = items[index..<min(index+limit, items.count)]
        await withTaskGroup(of: Void.self) { g in
            for item in slice { g.addTask { await process(item) } }
        }
        index += limit
    }
}
```

## Checklist

- UI только на `@MainActor`
- Отмена: храню `Task`, проверяю `Task.isCancelled`
- Конверсия callback → async через `withChecked*Continuation`
- Ограничение параллелизма продумано
- Типы, пересекающие изоляции, помечены `Sendable`
- Логи/метрики для контроля миграции


