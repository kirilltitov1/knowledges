---
type: "index"
status: "draft"
title: "Concurrency & Multithreading"
---

```dataviewjs
const pages = dv.pages('"iOS/Concurrency & Multithreading"')
    .where(p => p.file.name !== "Concurrency & Multithreading");

// Группируем по subtopic
const grouped = pages.groupBy(p => p.subtopic || "Разное");

// Сортируем группы
const sortedGroups = grouped.sort(g => g.key);

// Выводим каждую группу
for (let group of sortedGroups) {
    dv.header(3, group.key);
    dv.list(group.rows
        .sort(p => p.title || p.file.name)
        .map(p => dv.fileLink(p.file.path, false, p.title || p.file.name))
    );
}
```

## Рекомендуемый маршрут чтения

- [[iOS/Concurrency & Multithreading/basics-concurrency|Основы многопоточности]]
- [[iOS/Concurrency & Multithreading/threads-deep-dive|Threads — Deep Dive]]
- [[iOS/Concurrency & Multithreading/gcd-grand-central-dispatch|GCD — Grand Central Dispatch]]
- [[iOS/Concurrency & Multithreading/operation-queue|Operation Queue]]
- [[iOS/Concurrency & Multithreading/swift-concurrency-modern-approach|Swift Concurrency (Modern)]]
- [[iOS/Concurrency & Multithreading/patterns-and-architectures|Паттерны и архитектуры]]
- [[iOS/Concurrency & Multithreading/comparison-and-when-to-use-what|Сравнение и когда что использовать]]
- [[iOS/Concurrency & Multithreading/interview-questions-concurrency|Вопросы для собеседований]]
- [[iOS/Concurrency & Multithreading/performance-optimization|Производительность и оптимизация]]
- [[iOS/Concurrency & Multithreading/pitfalls-concurrency|Проблемы и рецепты]]
- [[iOS/Concurrency & Multithreading/testing-concurrency|Тестирование]]
- [[iOS/Concurrency & Multithreading/migration-best-practices|Миграция и best practices]]
- [[iOS/Concurrency & Multithreading/best-practices|Best Practices]]
