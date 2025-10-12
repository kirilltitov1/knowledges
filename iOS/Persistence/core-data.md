---
type: "thread"
status: "draft"
summary: ""
title: "Core Data"
---

# Core Data


### Architecture
- NSManagedObjectContext
- NSPersistentContainer
- NSManagedObjectModel
- NSPersistentStoreCoordinator

### Data Model
- Entities
- Attributes
- Relationships (one-to-one, one-to-many, many-to-many)
- Inverse relationships
- Delete rules

### Fetching Data
- NSFetchRequest
- Predicates
- Sort descriptors
- Batch size
- Fetch templates

### Saving Data
```swift
let context = persistentContainer.viewContext
context.perform {
    try? context.save()
}
```

### Predicates
- Format strings
- Compound predicates
- Comparison operators
- String operations

### Concurrency
- Main context
- Background context
- Private contexts
- Parent-child contexts

### Performance
- Batch operations
- Faulting
- Prefetching
- Indexing

### Migration
- Lightweight migration
- Manual migration
- Mapping models
- Version hashes

### Best Practices
- Context per thread
- Save on background
- Fetch only needed data
- Use batch operations

