---
type: "thread"
status: "draft"
summary: ""
title: "Autorelease Pool"
---

# Autorelease Pool

## Коротко
**Autorelease pool** — это «яма» для отложенных `release`. Любой Obj‑C объект (и часть Foundation‑объектов, появляющихся при бридже из Swift) может получить сообщение `autorelease`. Вместо немедленного `release` он кладётся в текущий пул. Когда пул сбрасывается (`drain`), всем объектам из него отправляется `release`.

## Почему `deinit` может не сработать сразу после выхода из скоупа
Выход из скоупа убирает только **твои** сильные ссылки, но объект может:

- **Быть autoreleased** — финальный `release` откладывается до сброса пула.
- Иметь **продлённое время жизни временных** (оптимизации компилятора: временные могут жить до конца выражения/функции; есть `withExtendedLifetime`).
- Иметь **скрытые удержания**: промежуточные объекты внутри Foundation/UIKit, кэши и т.п.

Итого: `deinit` вызывается, когда счётчик ссылок упадёт до нуля. Autorelease‑пул просто откладывает уменьшение счётчика.

## Где пулы есть «сами по себе»
- **Главный поток iOS/macOS**: вокруг каждой итерации RunLoop есть неявный autorelease‑pool.
- **NSOperationQueue**: операция обычно выполняется внутри пула.
- **GCD (Dispatch)**: не рассчитывай на пул для каждого блока. Для тяжёлой работы или tight‑loop ставь свой `@autoreleasepool { … }`.
- **Свои потоки (`Thread`/`pthread`)**: создавай пул вручную в теле потока.

## Когда явно ставить `@autoreleasepool`
Особенно в длинных циклах, где создаются/трогаются много Foundation/UIKit объектов (данные, строки, картинки, атрибутированные строки, контексты рисования), а также на фоне:

```swift
let files: [URL] = /* много файлов */
for url in files {
    @autoreleasepool {
        let data = try Data(contentsOf: url)
        if let image = UIImage(data: data) {
            // обработка
        }
        // На выходе из блока пул сбрасывается, пик памяти проседает
    }
}
```

На бэкграунде (GCD):

```swift
DispatchQueue.global(qos: .userInitiated).async {
    @autoreleasepool {
        heavyWork()
    }
}
```

Собственный поток:

```swift
Thread {
    @autoreleasepool {
        runLoopOrWork()
    }
}.start()
```

## Чистый Swift vs Foundation/UIKit
- **Чистые Swift‑классы** управляются ARC без autorelease.
- Как только цепочка касается Foundation/UIKit/CF (бридж в Obj‑C), появляются autoreleased‑объекты. Даже при работе со структурами (`Data`/`String`/`Array`) внутри могут кратко жить Obj‑C контейнеры/буферы.
- Если виден **рост пика памяти** в длинном цикле при работе с Foundation/UIKit — добавь внутренний `@autoreleasepool`.

## Swift Concurrency (Tasks)
- Задачи (`Task`, `Task.detached`) не гарантируют отдельный autorelease‑pool на каждую итерацию вашей логики.
- На `@MainActor` ты обычно под «зонтиком» RunLoop‑пула, но внутри длительных фоновых работ всё равно полезно локально сбрасывать пул.

```swift
Task.detached(priority: .userInitiated) {
    @autoreleasepool {
        await heavyAsyncWork()
    }
}
```

## Core Foundation и бриджинг
- Для CF‑типов действует правило Create/Copy → обязан освободить (`CFRelease`) либо использовать ARC‑бриджинг (`Unmanaged`/`takeRetainedValue`).
- Autorelease‑пул не решает вопросы владения CF‑объектами, он лишь откладывает `release` у Obj‑C.

## Практические заметки
- **Пул — не уборщик утечек.** Retain‑cycle он не исправит.
- **Вложенные пулы** разрешены и полезны для контроля пиков памяти.
- **Гранулярность.** Оборачивай «порцию» работы (итерацию/батч), а не весь метод.
- **Диагностика**: в Instruments (Allocations/Leaks) видно, что без внутреннего пула объекты «висят» до конца итерации RunLoop; с пулом — освобождаются на каждом шаге.

## Что такое drain и как он соотносится со Swift
В Objective‑C у `NSAutoreleasePool` есть метод `-drain`, который:

- В режиме ARC эквивалентен `-release` для самого пула, после чего выполняется освобождение всех объектов, находящихся в пуле.
- В не‑ARC окружениях (`MRC`) `-drain` оптимизирован под сбор на разных платформах; исторически он мог отличаться от прямого `-release`, но практический эффект для нас — «сбросить» все autoreleased объекты.

Во Swift нет явного `drain`. Конструкция `@autoreleasepool { ... }` синтаксически открывает пул при входе и «дренит» его при выходе из блока. Под капотом это обёртка над `objc_autoreleasePoolPush()` и `objc_autoreleasePoolPop()`:

```swift
@inline(__always)
func withAutoreleasePool<T>(_ body: () throws -> T) rethrows -> T {
    let token = objc_autoreleasePoolPush()
    defer { objc_autoreleasePoolPop(token) }
    return try body()
}
```

Практически: «drain случается» при завершении блока `@autoreleasepool`, при завершении итерации RunLoop на главном потоке, а также при завершении жизненного цикла NSOperation, если она исполнялась под пулом.

## TL;DR
`deinit` не обязан случиться ровно на границе скоупа: autorelease и продление жизни временных могут его отложить. `@autoreleasepool {}` даёт **детерминированную точку** сброса отложенных релизов (часто — внутри цикла), чтобы не раздувать пиковую память и вовремя освобождать тяжёлые Foundation/UIKit объекты.

## Связанные темы
- [[arc-mrc|ARC vs MRC]]


