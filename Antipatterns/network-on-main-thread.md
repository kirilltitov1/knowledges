---
type: "antipattern"
status: "draft"
severity: "high"
title: "Network On Main Thread"
---

## Проблема
Сетевые вызовы блокируют главный поток.

## Почему плохо
- Зависает UI, ANR, плохой UX.

## Диагностика
- Main Thread Checker, Time Profiler, ощутимые фризы при запросах.

## Решение
```swift
// ✅ Async/Await
let (data, _) = try await URLSession.shared.data(from: url)

// ✅ GCD
DispatchQueue.global(qos: .userInitiated).async {
  let data = try? Data(contentsOf: url)
  DispatchQueue.main.async { /* update UI */ }
}
```

## Ссылки
- См. тему: [[iOS/Topics/Networking]]
