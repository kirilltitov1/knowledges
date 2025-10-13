---
type: "thread"
status: "draft"
title: "Потоки (Threads) — детальный разбор"
subtopic: "Threads"
---

# Потоки (Threads) — детальный разбор

## Когда использовать Threads напрямую
- Низкоуровневые интеграции, требующие собственного потока/RunLoop
- Специализированные задачи с явным управлением жизненным циклом

## Основы
- Main thread: UI/SwiftUI/UIKit — только на главном потоке
- QoS/приоритеты: соотносите с UX
- RunLoop: нужен для таймеров/портов/источников событий

## Пример: поток с RunLoop
```swift
let worker = Thread {
    let runLoop = RunLoop.current
    let timer = Timer(timeInterval: 1.0, repeats: true) { _ in
        print("tick on \(Thread.current)")
    }
    runLoop.add(timer, forMode: .default)
    runLoop.run()
}
worker.qualityOfService = .userInitiated
worker.start()
```

## Подводные камни
- Deadlock при взаимных sync-вызовах между потоками
- Thread explosion — создавайте ограниченно, предпочитайте GCD
- Отсутствие кооперативной отмены — внедряйте флаг cancel
- Отсутствие RunLoop — таймеры не работают

## Чек-лист
- Никогда не трогайте UI вне main
- Используйте QoS осознанно
- Освобождайте ресурсы при завершении


