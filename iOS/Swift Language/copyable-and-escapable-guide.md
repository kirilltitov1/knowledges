## Copyable, ~Copyable, Escapable и ~Escapable в Swift: гайд от junior до senior++

Этот материал объясняет концепции Copyable/~Copyable (некопируемые типы, move-only) и Escapable/~Escapable (эскейпящиеся и неэскейпящиеся замыкания) на практическом уровне — с мотивацией, правилами, примерами, анти-паттернами и советами для собеседований.

### Краткая карта терминов
- **Copyable**: тип можно копировать. Для `struct/enum` — копируются значения; для `class` — копируется ссылка.
- **~Copyable**: тип нельзя копировать (move-only). Им можно владеть, одалживать (borrow), передавать владение (consume/move), но нельзя дублировать.
- **Escapable**: замыкание может «убежать» за рамки текущего вызова (сохраниться/выполниться позже) — аналог `@escaping`.
- **~Escapable**: замыкание гарантированно не утекает — аналог «по умолчанию non-escaping» параметров-замыканий.

Примечание: в сегодняшних стабильных версиях Swift эскейповость выражается через `@escaping`/по умолчанию non-escaping. Термины Escapable/~Escapable используютcя для объяснения typed effects и дженерик-ограничений вокруг (эскейпящихся/неэскейпящихся) функциональных типов.

---

## Зачем всё это: мотивация

- **Безопасность ресурсов**: ~Copyable позволяет выразить уникальное владение ресурсом (файловый дескриптор, сокет, мьютекс) и исключить случайные копии, ведущие к двойному освобождению/закрытию.
- **Производительность**: явная модель владения уменьшает неочевидные копии больших значений, сокращает ARC-качание, облегчает стековые оптимизации и инлайн для ~Escapable замыканий.
- **Читаемость API**: сигнатуры функций (через borrowing/consuming/inout и эскейповость) прямо показывают соглашения владения и времени жизни.

---

## Часть 1. Copyable и ~Copyable (move-only типы)

### Базовые правила
- Большинство обычных типов в Swift — **Copyable**.
- Сделать тип **некопируемым** можно через объявление `: ~Copyable`.
- У ~Copyable-значимых типов (`struct`/`enum`) можно определять `deinit` для освобождения ресурсов.
- Методы и параметры могут указывать модель владения: `borrowing` (заём, чтение), `inout` (эксклюзивный изменяемый заём), `consuming` (поглощение, передача владения).

### Важно: параметры ~Copyable должны явно указывать владение
Для параметров некопируемых типов требуется одна из аннотаций:
- `borrowing T` — только чтение без копии, владение остаётся у вызывающего;
- `inout T` — эксклюзивный изменяемый заём;
- `consuming T` — функция принимает владение и «поглощает» значение.

Иначе получите ошибку уровня компиляции наподобие: `Parameter of noncopyable type 'X' must specify ownership`.

### Минимальный пример: файловый дескриптор
```swift
struct FileDescriptor: ~Copyable {
    private var raw: Int32

    init(_ raw: Int32) { self.raw = raw }

    deinit {
        if raw >= 0 { close(raw) }
    }

    mutating func write(_ bytes: [UInt8]) {
        // Здесь можно писать в raw;
        // важно, что копий FileDescriptor не существует
    }

    consuming func close() {
        if raw >= 0 { close(raw) }
        raw = -1
    }
}

var fd = FileDescriptor(3)
// let fd2 = fd // Ошибка компиляции: копирование запрещено (~Copyable)

func take(_ fd: consuming FileDescriptor) {
    // Получили владение fd; по выходу из области — deinit/или явное close()
}

take(fd) // после этого fd больше нельзя использовать
```

### borrowing, inout, consuming — когда что
- **borrowing**: только чтение, без копий, владение остаётся у вызывающего.
- **inout**: эксклюзивный изменяемый заём; удобно для модификации без копий.
- **consuming**: передаём владение; исходное значение использовать нельзя.

```swift
func printInfo<T>(borrowing value: T) {
    // читаем value без копий
}

func mutate<T>(_ value: inout T) {
    // эксклюзивный доступ, можно менять без копий
}

func useAndLose<T>(consuming value: T) {
    // владеем и «поглощаем» значение, вызывающий теряет доступ
}
```

### Дженерики и ограничения на копируемость
- Когда нужна **возможность копировать**:
```swift
func duplicate<T: Copyable>(_ x: T) -> (T, T) { (x, x) }
```
- Когда проектируем **уникальное владение**:
```swift
func operateUniquely<T: ~Copyable>(borrowing x: T) {
    // можно вызывать методы/читать, но нельзя копировать x
}
```

### Анти-паттерны с ~Copyable
- Хранить ~Copyable в контейнерах/структурах, которые предполагают копирование по семантике.
- «Случайно» копировать через присваивание/возврат, когда по смыслу нужен move.
- Забывать пометить завершающие методы как `consuming` (например, `close()`), из-за чего можно «переиспользовать» уже освобождённый ресурс.

### Практическая рекомендация
- Помечайте ресурсо-ориентированные value-типы как `~Copyable` и проектируйте API вокруг `borrowing`/`inout`/`consuming`.
- Для ссылочных типов (`class`) уникальность часто достигают через внутренние уникальные буферы + Copy-on-Write; ~Copyable — про value-типы.

---

## Часть 2. Escapable и ~Escapable (эскейповость замыканий)

### Сегодняшний статус в языке
- Параметры-замыкания в Swift по умолчанию **non-escaping** (то есть **~Escapable** по сути).
- Если замыкание сохраняется/выполняется позже, помечаем параметр `@escaping` (то есть **Escapable**).
- Концепты Escapable/~Escapable полезны для дженериков и объяснения будущих typed effects.

### Когда non-escaping (~Escapable) — это хорошо
- Синхронные обходы (`forEach`), фильтры, `map`, `reduce`, валидации — когда вызываете замыкание «здесь и сейчас» и не храните.
- Компилятор может делать более агрессивные оптимизации (меньше аллокаций, проще анализ владения/aliasing).

```swift
extension Array {
    func myForEach(_ body: (Element) -> Void) { // ~Escapable
        for e in self { body(e) }
    }
}
```

### Когда нужен `@escaping` (Escapable)
- Наблюдатели/подписки: сохраняете обработчик в массиве/слоте и вызываете позже.
- Таймеры, диспетчер очередей, кросс-акторы: выполнение не в рамках текущего стека.

```swift
final class Emitter<Event> {
    private var handlers: [(Event) -> Void] = []

    func observe(_ handler: @escaping (Event) -> Void) {
        handlers.append(handler)
    }

    func emit(_ event: Event) {
        for h in handlers { h(event) }
    }
}
```

### Взаимодействие с конкуренцией: `@Sendable`
- Эскейпящееся замыкание, которое может быть вызвано в другом потоке/акторе, помечайте `@Sendable`.
- Для ~Escapable (non-escaping) это обычно не требуется, потому что оно не утекает.

```swift
func schedule(on queue: DispatchQueue, _ work: @escaping @Sendable () -> Void) {
    queue.async(execute: work)
}
```

### Миграционные приёмы
- Если нужен временный мост non-escaping → escaping, ранее использовали `withoutActuallyEscaping(_:do:)`. С typed effects часть таких кейсов становится не нужна, но в стабильном Swift инструмент всё ещё полезен в редких случаях.

### Анти-паттерны
- Помечать всё `@escaping` «на всякий случай» — лишние аллокации/усложнение владения, риск ретейн-циклов.
- Сильно захватывать `self` в эскейпящееся замыкание без `[weak self]` там, где жизненный цикл может привести к утечке.
- Передавать эскейпящееся замыкание через потоки/акторы без `@Sendable`.

---

## От junior к senior++: что нужно уметь

### Junior
- Понимает отличие копируемого и некопируемого значения; знает, что `~Copyable` запрещает копии.
- Отличает non-escaping и `@escaping` параметры-замыкания; понимает зачем `[weak self]`.

### Middle
- Проектирует ресурсные API с `~Copyable`; правильно расставляет `borrowing`/`inout`/`consuming`.
- Разводит быстрые (~Escapable) и универсальные (Escapable/`@escaping`) пути, понимая их стоимость.

### Senior/Senior++
- Строит абстракции владения, в которых ошибки «двойного освобождения» невозможны по типам.
- Делит горячие пути на non-escaping и escaping ветки; учитывает конкуренцию (`@Sendable`), actor-изоляцию и эффекты.

---

## Расширенные примеры

### 1) Уникальный буфер без копий
```swift
struct UniqueBuffer: ~Copyable {
    private var storage: UnsafeMutableRawPointer
    private var capacity: Int

    init(capacity: Int) {
        self.capacity = capacity
        self.storage = .allocate(byteCount: capacity, alignment: 16)
    }

    deinit {
        storage.deallocate()
    }

    mutating func write(bytes: [UInt8]) {
        precondition(bytes.count <= capacity)
        storage.copyMemory(from: bytes, byteCount: bytes.count)
    }

    consuming func consumeBytes() -> [UInt8] {
        // Возвращаем данные и передаём владение наружу (примерно)
        // После вызова использовать self нельзя
        return [UInt8](unsafeUninitializedCapacity: capacity) { buffer, count in
            storage.copyBytes(to: buffer.baseAddress!, count: capacity)
            count = capacity
        }
    }
}
```

### 1.1) «Боевой» пример: транзакция БД и scope-лок на ~Copyable
```swift
// Некопируемый транзакционный контекст с гарантированным завершением
struct DBTransaction: ~Copyable {
    private var handle: OpaquePointer?

    init(beginOn db: OpaquePointer?) {
        handle = db
        // begin transaction
        // sqlite3_exec(db, "BEGIN", nil, nil, nil)
    }

    mutating func execute(_ sql: String) {
        // sqlite3_exec(handle, sql, nil, nil, nil)
    }

    consuming func commit() {
        // sqlite3_exec(handle, "COMMIT", nil, nil, nil)
        handle = nil
    }

    consuming func rollback() {
        // sqlite3_exec(handle, "ROLLBACK", nil, nil, nil)
        handle = nil
    }

    deinit {
        // Если забыли явно завершить — безопасно откатим
        if handle != nil {
            // sqlite3_exec(handle, "ROLLBACK", nil, nil, nil)
        }
    }
}

// Использование
func saveUser(db: OpaquePointer?, user: User) throws {
    var tx = DBTransaction(beginOn: db)
    do {
        tx.execute("INSERT INTO users ...")
        tx.execute("INSERT INTO groups ...")
        // ... другие шаги
        tx.commit() // consuming: после этого tx использовать нельзя
    } catch {
        tx.rollback() // consuming
        throw error
    }
}

// Scope-лок на ~Copyable: гарантированно отпускается один раз
struct MutexLock: ~Copyable {
    private var mtx: pthread_mutex_t

    init(_ mtx: pthread_mutex_t) { self.mtx = mtx; pthread_mutex_lock(&self.mtx) }

    deinit { pthread_mutex_unlock(&mtx) }
}

func withLocked<T>(_ mtx: inout pthread_mutex_t, _ body: () throws -> T) rethrows -> T {
    var lock = MutexLock(mtx)
    // lock не скопировать; по выходу из области — deinit и unlock гарантированно один раз
    return try body()
}
```

Почему это полезно:
- Типовая система запрещает копии «ключей владения» (транзакция/лок), значит невозможно дважды коммитнуть/разлочить.
- `deinit` у value-типа даёт надёжный аварийный путь (rollback/unlock), если контроль потока ушёл по исключению.
- Чёткие сигнатуры с `consuming`/`borrowing`/`inout` делают протоколы владения читаемыми и проверяемыми компилятором.

### 2) Две ветки API для замыканий
```swift
extension Array {
    // Быстрый путь: non-escaping (~Escapable)
    func mapFast<U>(_ transform: (Element) -> U) -> [U] {
        var result: [U] = []
        result.reserveCapacity(count)
        for e in self { result.append(transform(e)) }
        return result
    }

    // Универсальный путь: можно сохранить transform (Escapable / @escaping)
    func mapEscaping<U>(_ transform: @escaping (Element) -> U) -> [U] {
        // Пример условный — тут мы не сохраняем, но сигнатура разрешает
        var result: [U] = []
        result.reserveCapacity(count)
        for e in self { result.append(transform(e)) }
        return result
    }
}
```

### 3) Контролируем завершение через consuming
```swift
struct Connection: ~Copyable {
    private var handle: Int32

    init(openTo host: String) { /* ... */ handle = 42 }

    mutating func send(_ data: [UInt8]) { /* ... */ }

    consuming func close() {
        // гарантированное закрытие
    }
}

func withConnection<T>(_ body: (inout Connection) -> T) -> T {
    var conn = Connection(openTo: "example.com")
    defer { conn.close() } // consuming в конце
    return body(&conn)
}
```

---

## Частые вопросы

- «Можно ли сделать `class` некопируемым?» — Ссылочный тип копируется как ссылка. Уникальность реализуют через внутреннее состояние (уникальные буферы, токены владения) или дизайн API; ~Copyable применяется к value-типа́м.
- «Почему не сделать всё ~Copyable?» — Это усложнит использование простых типов и коллекций. Принцип: делать уникальными только сущности с реальным владением ресурсами.
- «Зачем разделять non-escaping и escaping?» — Non-escaping даёт оптимизацию и упрощает анализ владения. Escaping нужен там, где жизненный цикл реально длиннее вызова.

---

## Полезные ссылки

- Swift Evolution — Noncopyable structs and enums (SE-0390):
  [Предложение SE-0390 на swift-evolution](https://github.com/apple/swift-evolution/blob/main/proposals/0390-noncopyable-structs-and-enums.md)

- Swift — Ownership Manifesto (исторический документ о модели владения):
  [Ownership Manifesto на swift](https://github.com/apple/swift/blob/main/docs/OwnershipManifesto.md)

- WWDC: обзорные сессии «What’s new in Swift» и материалы по владению/замыканиям (подборки):
  - [Поиск по «What’s new in Swift» на Apple Developer](https://developer.apple.com/videos/?q=what%27s%20new%20in%20swift)
  - [Поиск по «noncopyable» (владение/ownership)](https://developer.apple.com/videos/?q=noncopyable)
  - [Поиск по «escaping closure»](https://developer.apple.com/videos/?q=escaping%20closure)

### WWDC — прямые ссылки (подборка)
- What’s new in Swift 2024:
  [developer.apple.com/videos/?q=What%27s%20new%20in%20Swift%202024](https://developer.apple.com/videos/?q=What%27s%20new%20in%20Swift%202024)
- What’s new in Swift 2023:
  [developer.apple.com/videos/?q=What%27s%20new%20in%20Swift%202023](https://developer.apple.com/videos/?q=What%27s%20new%20in%20Swift%202023)
- Swift performance (для аспектов non-escaping и замыканий):
  [developer.apple.com/videos/?q=Swift%20performance](https://developer.apple.com/videos/?q=Swift%20performance)

Примечание: конкретные ID сессий зависят от года. Если нужен пинпоинт одной сессии (с ID), напишите год — добавлю прямую ссылку вида `.../videos/play/wwdcYYYY/NNNNN/`.

### Мини‑примеры из WWDC (адаптация)
```swift
// Non-escaping (~Escapable): синхронный обход — быстро и без аллокаций
extension Array {
    func apply(_ body: (Element) -> Void) { // non-escaping
        for e in self { body(e) }
    }
}

// Escaping: подписка/наблюдение — храним обработчик и вызываем позже
final class Notifier<Event> {
    private var handlers: [(Event) -> Void] = []
    func observe(_ handler: @escaping (Event) -> Void) { handlers.append(handler) }
    func emit(_ e: Event) { for h in handlers { h(e) } }
}

// Move-only (~Copyable) ресурсы: транзакция/лок — гарантированная одноразовость
struct Tx: ~Copyable {
    consuming func commit() { /* ... */ }
    consuming func rollback() { /* ... */ }
    deinit { /* аварийный rollback */ }
}
```

Если вам нужна привязка к конкретной сессии WWDC за нужный год — скажите, подберу точный номер и добавлю прямую ссылку.

---

## Итоговые рекомендации
- Для **ресурсов и уникального владения** используйте `~Copyable` + `consuming/borrowing/inout`.
- По умолчанию проектируйте API под **non-escaping** замыкания; поднимайте до `@escaping` только когда это оправдано.
- В конкуренции не забывайте про `@Sendable` для эскейпящихся замыканий, вызываемых в других потоках/акторах.
- В дженериках явно требуйте `T: Copyable` там, где нужны копии; используйте `T: ~Copyable` для уникальных владений.


