---
type: "thread"
status: "draft"
summary: ""
title: "realm"
---

# Realm


### Basics
- Realm database
- Real-time updates
- Object-oriented

### Models
```swift
class Person: Object {
    @Persisted var name: String
    @Persisted var age: Int
}
```

### CRUD Operations
- Create: `realm.add(object)`
- Read: `realm.objects(Person.self)`
- Update: Write transaction
- Delete: `realm.delete(object)`

### Queries
- Filtering
- Sorting
- Linking objects
- Computed properties

### Relationships
- To-one
- To-many
- Inverse relationships

### Notifications
- Collection notifications
- Object notifications
- Realm notifications

### Threading
- Thread-confined objects
- ThreadSafeReference
- Async operations

### Migration
- Schema versioning
- Migration blocks
- Automatic migration

```swift
let config = Realm.Configuration(schemaVersion: 2) { migration, oldVersion in
    if oldVersion < 2 {
        // Переименование/инициализация новых полей
        migration.enumerateObjects(ofType: Person.className()) { _, newObject in
            if newObject?["age"] == nil { newObject?["age"] = 0 }
        }
    }
}
Realm.Configuration.defaultConfiguration = config
let realm = try Realm()
```

### Realm Sync
- MongoDB Realm
- Real-time sync
- Conflict resolution

## Практика и производительность
- Группируйте изменения в одну write‑транзакцию.
- Используйте `ThreadSafeReference` для передачи объектов между потоками.
- Избегайте частых уведомлений UI: батчируйте изменения с `beginWrite`/`commitWrite`.
- Индексируйте часто фильтруемые поля (`@Persisted(indexed: true)`).

## Сравнение с Core Data (когда что выбирать)
- Realm: быстрый старт, простые модели, live‑обновления/нотификации, кроссплатформенность, встроенный Sync.
- Core Data: tight интеграция с iOS, NSFetchedResultsController/SwiftUI, тонкая настройка, нативный стек, больше контроля.
- SQLite/GRDB: максимальная гибкость/производительность/контроль запросов, но больше кода и ответственности.


