---
title: Realm
type: thread
topics: [Persistence]
subtopic: realm
status: draft
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

### Realm Sync
- MongoDB Realm
- Real-time sync
- Conflict resolution

