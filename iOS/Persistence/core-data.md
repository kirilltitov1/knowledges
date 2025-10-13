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

## Optimization Guide (Практика)

### Настройка `NSPersistentContainer`
```swift
import CoreData

enum Persistence {
    static let container: NSPersistentContainer = {
        let container = NSPersistentContainer(name: "AppModel")
        let description = container.persistentStoreDescriptions.first!
        // WAL ускоряет запись и повышает надёжность
        description.setOption(true as NSNumber, forKey: NSPersistentHistoryTrackingKey)
        description.setOption(true as NSNumber, forKey: NSPersistentStoreRemoteChangeNotificationPostOptionKey)
        description.setValue("WAL", forPragmaNamed: "journal_mode")
        description.shouldMigrateStoreAutomatically = true
        description.shouldInferMappingModelAutomatically = true

        container.loadPersistentStores { _, error in
            if let error { fatalError("Persistent store load error: \(error)") }
        }

        let viewContext = container.viewContext
        viewContext.automaticallyMergesChangesFromParent = true
        viewContext.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
        viewContext.name = "viewContext"
        return container
    }()
}
```

### Конкурентность и фоновая работа
- Для тяжёлых операций используйте `performBackgroundTask` или собственные private queue contexts.
- Минимизируйте блокировки UI: никогда не вызывайте долгие `fetch/save` на main queue.

```swift
let container = Persistence.container
container.performBackgroundTask { backgroundContext in
    backgroundContext.mergePolicy = NSMergeByPropertyStoreTrumpMergePolicy
    backgroundContext.name = "bg-import"
    // Импорт/миграции/агрегации
    do {
        // ... работа ...
        try backgroundContext.save()
    } catch {
        backgroundContext.rollback()
    }
}
```

### Faulting, Prefetching, Memory
- Включайте faulting для снижения памяти: по умолчанию Core Data подгружает значения лениво.
- При чтении больших наборов используйте `fetchBatchSize` и `includesPropertyValues = false` для подсчётов.
- Prefetch relationships, когда нужны связанные объекты, чтобы избежать N+1.

```swift
let request: NSFetchRequest<Item> = Item.fetchRequest()
request.sortDescriptors = [NSSortDescriptor(keyPath: \Item.date, ascending: false)]
request.fetchBatchSize = 50
request.returnsObjectsAsFaults = true
request.relationshipKeyPathsForPrefetching = ["author", "comments"]
```

### Индексы, уникальность и дедупликация
- Настройте индексы и Unique Constraints в `.xcdatamodeld` → это ускорит поиск и упростит дедупликацию.
- При импорте используйте запрос по уникальному ключу вместо слепого `insert`.

```swift
func upsert(by id: String, payload: Payload, in context: NSManagedObjectContext) throws -> Item {
    let fetch: NSFetchRequest<Item> = Item.fetchRequest()
    fetch.fetchLimit = 1
    fetch.predicate = NSPredicate(format: "id == %@", id)
    if let existing = try context.fetch(fetch).first {
        existing.title = payload.title
        return existing
    } else {
        let created = Item(context: context)
        created.id = id
        created.title = payload.title
        return created
    }
}
```

### Batch‑операции (массовые апдейты/удаления)
- `NSBatchUpdateRequest` и `NSBatchDeleteRequest` работают на уровне SQL и сильно быстрее итераций по объектам.

```swift
// Batch Update
let update = NSBatchUpdateRequest(entityName: "Item")
update.propertiesToUpdate = ["isArchived": true]
update.predicate = NSPredicate(format: "date < %@", Date() as NSDate)
update.resultType = .updatedObjectIDsResultType
let updateResult = try context.execute(update) as? NSBatchUpdateResult
let updatedIDs = updateResult?.result as? [NSManagedObjectID] ?? []
NSManagedObjectContext.mergeChanges(fromRemoteContextSave: [NSUpdatedObjectsKey: updatedIDs], into: [context])

// Batch Delete
let fr: NSFetchRequest<NSFetchRequestResult> = Item.fetchRequest()
fr.predicate = NSPredicate(format: "isArchived == YES")
let delete = NSBatchDeleteRequest(fetchRequest: fr)
delete.resultType = .resultTypeObjectIDs
if let result = try context.execute(delete) as? NSBatchDeleteResult,
   let ids = result.result as? [NSManagedObjectID] {
    NSManagedObjectContext.mergeChanges(fromRemoteContextSave: [NSDeletedObjectsKey: ids], into: [context])
}
```

### Тонкие настройки `NSFetchRequest`
- `includesPendingChanges = false` для отчётных запросов по сохранённому состоянию.
- `includesSubentities = false`, если дочерние сущности не нужны.
- `propertiesToFetch` + `resultType = .dictionaryResultType` для агрегаций без материализации объектов.

```swift
let r = NSFetchRequest<NSDictionary>(entityName: "Item")
r.resultType = .dictionaryResultType
r.propertiesToFetch = ["category", NSExpressionDescription.max("dateMax", keyPath: "date")]
r.propertiesToGroupBy = ["category"]
```

```swift
extension NSExpressionDescription {
    static func max(_ name: String, keyPath: String) -> NSExpressionDescription {
        let d = NSExpressionDescription()
        d.name = name
        d.expression = NSExpression(forFunction: "max:", arguments: [NSExpression(forKeyPath: keyPath)])
        d.expressionResultType = .dateAttributeType
        return d
    }
}
```

### Миграции и версии модели
- Включите light‑weight migration (`shouldMigrateStoreAutomatically`, `shouldInferMappingModelAutomatically`).
- Для сложных случаев используйте Mapping Model и этапную миграцию.
- Следите за `versionHashModifier` при изменениях, чтобы избежать неожиданных несовместимостей.

### Persistent History Tracking
- Включение `NSPersistentHistoryTrackingKey` позволяет отслеживать изменения между контекстами/процессами (полезно для виджетов, эксентов).
- Обрабатывайте `NSPersistentStoreRemoteChange` нотификации для слияния изменений во viewContext.

### SwiftUI
- Для таблиц/списков используйте `@FetchRequest` c батчингом и сортировками.
- Для сложных экранов, требующих точного контроля, оборачивайте `NSFetchedResultsController` во вью‑модель.

### Диагностика и профилирование
- Instruments → Core Data/Time Profiler для горячих точек.
- Включайте SQL‑логирование переменной окружения `-com.apple.CoreData.SQLDebug 1` на dev.

## Цели оптимизации и метрики (что и зачем)

- Время отклика UI: список/деталь должны отображаться < 100–200 мс с кэшем, холодный запуск < 2–3 с.
- Память: избегать роста до сотен МБ при прокрутке/импорте (faulting, batch fetch, reset).
- Диск/IO: минимизировать количество и размер записей (batch insert/update/delete, WAL).
- Конкурентность: отсутствие блокировок main thread при сохранениях/импорте.
- Надёжность данных: корректные миграции и политика конфликта (merge policies/уникальность).

Главное правило: оптимизируем под конкретные пользовательские сценарии и измеряем до/после.

## Когда какую технику применять (почему и когда)

- Экран списка (таблица/коллекция):
  - Используйте `NSFetchedResultsController` (UIKit) или `@FetchRequest` (SwiftUI) для дифф‑обновлений и экономии памяти. Почему: фреймворк оптимально управляет faulting и диффами.
  - Задайте `fetchBatchSize` и сорт/предикат. Когда: большие списки (> сотен записей) или бесконечная лента.

- Экран детали:
  - Грузите только нужный объект по `objectID` и требуемые связи с `relationshipKeyPathsForPrefetching`. Почему: меньше запросов/N+1. Когда: сложные графы связей.

- Импорт/синхронизация больших объёмов:
  - Фоновый `performBackgroundTask`, `NSBatchInsertRequest`/`NSBatchUpdateRequest`/`NSBatchDeleteRequest`. Почему: операции на уровне SQL кратно быстрее и не материализуют объекты. Когда: > тысяч строк.

- Частые пересохранения и конфликты:
  - `mergePolicy = NSMergeByPropertyObjectTrump` (UI) и `NSMergeByPropertyStoreTrump` (импорт). Почему: предсказуемое разрешение конфликтов по полям. Когда: параллельные изменения.

- Многомодульные приложения/виджеты/экстеншены:
  - Включите Persistent History + `automaticallyMergesChangesFromParent`. Почему: корректная синхронизация изменений между процессами. Когда: есть App Extensions/Widgets.

- Проблемы с памятью при длинных сессиях импорта/обработки:
  - Периодически вызывайте `context.reset()`, сохраняйте `NSManagedObjectID` вместо живых объектов. Почему: освобождает граф из памяти. Когда: батчевые операции.

- Миграции схемы:
  - Lightweight (infer) по возможности; сложные изменения — Mapping Model и этапная миграция. Почему: минимальный даунтайм/риски. Когда: breaking‑изменения в моделях.

## Симптомы → причины → решения

| Симптом | Вероятная причина | Что делать |
|---|---|---|
| Скролл лагает при списке | Тяжёлый fetch на main, N+1 по связям | `fetchBatchSize`, prefetch relationships, FRC, перенести тяжелые вычисления в фон |
| рост памяти при импорте | Материализация тысяч объектов | `NSBatchInsertRequest`, периодический `reset()`, работать с `objectID` |
| Долгое сохранение | Много изменённых объектов на main | Сохранять в фоне, группировать изменения, упростить объектный граф |
| Таймауты/холодный старт | Миграция на старте, тяжёлые запросы | Предмиграция, ленивые загрузки, экраны‑скелетоны |
| Конфликты данных | Параллельные сохранения | Настроить `mergePolicy`, уникальные ограничения, идемпотентные upsert |
| Блокировки UI | Запуск batch операций на main | Все batch/импорт — в фоне; main только чтение/презентация |

## Рецепты (готовые паттерны)

### NSBatchInsertRequest (iOS 13+)
```swift
// Быстрый импорт без материализации NSManagedObject
let insert = NSBatchInsertRequest(entity: Item.entity()) { (managed: NSManagedObject) -> Bool in
    guard let item = managed as? Item else { return false }
    // заполнить поля из внешнего буфера
    // item.id = ...; item.title = ...
    return true // false — завершить досрочно
}
insert.resultType = .objectIDs
let result = try backgroundContext.execute(insert) as? NSBatchInsertResult
if let ids = result?.result as? [NSManagedObjectID] {
    NSManagedObjectContext.mergeChanges(fromRemoteContextSave: [NSInsertedObjectsKey: ids], into: [viewContext])
}
```

### Управление памятью при больших обработках
```swift
for (index, payload) in payloads.enumerated() {
    let obj = Item(context: backgroundContext)
    // заполняем obj
    if index % 500 == 0 { // батч сохраняем
        try backgroundContext.save()
        backgroundContext.reset() // освобождаем объекты
    }
}
```

### Быстрые отчёты/агрегации без объектов
```swift
let r = NSFetchRequest<NSDictionary>(entityName: "Item")
r.resultType = .dictionaryResultType
r.propertiesToFetch = ["category", NSExpressionDescription.max("latest", keyPath: "date")]
r.propertiesToGroupBy = ["category"]
let rows = try context.fetch(r)
```

## Store‑уровень: настройки SQLite (когда трогать)

- `journal_mode = WAL` — включайте почти всегда: быстрее запись, меньше блокировок чтения.
- `synchronous = NORMAL` — баланс надёжности/скорости; `FULL` — реже, `OFF` — только на dev.
- Менять через `NSPersistentStoreDescription.setValue(_:forPragmaNamed:)`. Почему: контроль производительности/надёжности в зависимости от продукта/окружения.

Пример:
```swift
description.setValue("WAL", forPragmaNamed: "journal_mode")
description.setValue("NORMAL", forPragmaNamed: "synchronous")
```

## Миграции: порядок действий

1) Включить lightweight migration по умолчанию. Почему: покрывает частые изменения без ручных моделей.
2) При сложных изменениях подготовить Mapping Model и прогнать тестовую миграцию на сэмпле. Когда: переименование/разделение сущностей.
3) На проде показывать экран «обновления данных», логировать длительность, иметь фолбэк.
4) Избегать миграций на первый экран UI: мигрируйте до инициализации основного стека.

## Расширенная диагностика

- SQLDebug уровни: `-com.apple.CoreData.SQLDebug 3` — показывает запросы/время/параметры.
- Instruments: Core Data Fetches, Allocations (утечки/рост), Time Profiler (горячие точки).
- Метрики: время fetch/save, размер файла SQLite, кол-во строк/индексов, latency экрана.
- Логируйте ключевые операции (batch, миграции, синхронизация) и их длительность в аналитике.

