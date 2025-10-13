---
type: "thread"
status: "draft"
summary: ""
title: "sqlite"
---

# SQLite


## Библиотеки

### SQLite.swift
- Типобезопасные запросы, билдер, удобные миграции.
- Пример:
```swift
import SQLite

let db = try Connection("app.sqlite3")
let users = Table("users")
let id = Expression<Int64>("id")
let name = Expression<String>("name")

try db.run(users.create(ifNotExists: true) { t in
    t.column(id, primaryKey: .autoincrement)
    t.column(name, unique: true)
})

let insert = users.insert(name <- "Alice")
let rowid = try db.run(insert)

for user in try db.prepare(users.filter(id == rowid)) {
    print(user[id], user[name])
}
```

### GRDB.swift
- Высокая производительность, `Record`/`DatabaseQueue`/`DatabasePool`, миграции, FetchableRecord/Queryable.
- Пример миграций:
```swift
import GRDB

let dbQueue = try DatabaseQueue(path: "app.sqlite")

var migrator = DatabaseMigrator()
migrator.registerMigration("v1") { db in
    try db.create(table: "item") { t in
        t.autoIncrementedPrimaryKey("id")
        t.column("title", .text).notNull().indexed()
        t.column("createdAt", .datetime).notNull()
    }
}
try migrator.migrate(dbQueue)
```

### Direct SQL
- FMDB (ObjC) или чистый C API через `sqlite3_*`.
- Prepared statements обязательны.
- Для многопоточности используйте `DatabaseQueue`/`DatabasePool` (GRDB) или свои очереди.

### Schema Design
- Tables
- Indexes
- Relationships
- Constraints

Рекомендации:
- Нормализуйте схему, добавляйте индексы по полям в WHERE/ORDER BY.
- Включайте `WITHOUT ROWID` для широких таблиц без surrogate‑key, если подходит.
- Храните даты в ISO8601/Unix time, не в локализованных строках.

### Queries
- SELECT
- INSERT
- UPDATE
- DELETE
- JOINs

Антипаттерны:
- N+1 в приложении: переносите агрегации в SQL (`JOIN`, `GROUP BY`).
- `SELECT *` в проде: выбирайте только нужные столбцы.

### Transactions
- BEGIN TRANSACTION
- COMMIT
- ROLLBACK

Используйте транзакции для пакетных операций: это многократно ускоряет вставку.
```swift
try dbQueue.write { db in
    try db.inTransaction {
        for payload in payloads { try Item(payload: payload).insert(db) }
        return .commit
    }
}
```

### Best Practices
- Parameterized queries
- Connection pooling
- WAL mode
- Vacuum

Дополнительно:
- Включайте `PRAGMA foreign_keys = ON` для целостности.
- `journal_mode = WAL` уменьшает блокировки на чтение.
- `synchronous = NORMAL` для баланса надёжности/скорости (на dev можно `OFF`).
- Профилируйте через `EXPLAIN QUERY PLAN`.


