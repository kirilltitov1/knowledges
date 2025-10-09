---
title: 6. Migration & Best Practices
type: thread
topics: [Concurrency & Multithreading]
subtopic: 6. Migration & Best Practices
status: draft
level: intermediate
platforms: [iOS]
ios_min: "13.0"
duration: 45m
tags: [migration, async-await, callbacks, combine, operations, actors]
---

# 6. Migration & Best Practices


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

