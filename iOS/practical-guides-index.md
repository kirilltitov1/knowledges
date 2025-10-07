---
title: Индекс практических руководств
type: index
topics: [iOS, Guides, Practical]
status: draft
---

# 📚 Индекс практических руководств

Специализированный индекс всех практических руководств, руководств по реализации и how-to материалов в базе знаний.

## 🎯 Цель индекса

Этот индекс помогает быстро найти практические руководства и инструкции по реализации различных аспектов iOS разработки.

## 📋 Категории руководств

### 🏗️ Архитектура и паттерны
- [[iOS/Architecture/clean-architecture|Clean Architecture]] - полное руководство по чистой архитектуре
- [[iOS/Architecture/mvvm-model-view-viewmodel|MVVM]] - детальное руководство по MVVM паттерну
- [[iOS/Architecture/coordinator-pattern|Coordinator Pattern]] - навигация без сильной связанности

### 💾 Управление данными
- [[iOS/Memory/memory-management-practical-guide|Управление памятью]] - комплексное руководство по ARC и оптимизации памяти
- [[iOS/Persistence/core-data|Core Data]] - полное руководство по работе с Core Data
- [[iOS/Networking/caching|Кеширование в сетевых запросах]] - стратегии кеширования

### 🔄 Асинхронность и многопоточность
- [[iOS/Concurrency & Multithreading/4-swift-concurrency-modern-approach|Swift Concurrency]] - современный подход к асинхронности
- [[iOS/Concurrency & Multithreading/2-gcd-grand-central-dispatch|GCD]] - Grand Central Dispatch для многопоточности

### 🛜 Сетевые технологии
- [[iOS/Networking/networking-generic-api-client|Generic API Client]] - типобезопасный сетевой клиент
- [[iOS/Networking/urlsession|URLSession]] - полное руководство по сетевым запросам

### 🧪 Тестирование (когда будет заполнен раздел)
- [ ] Unit Testing - XCTest и mocking
- [ ] UI Testing - автоматизированное тестирование интерфейса
- [ ] Integration Testing - тестирование интеграции компонентов

### 🔒 Безопасность (когда будет заполнен раздел)
- [ ] Keychain - безопасное хранение данных
- [ ] Биометрия - Touch ID / Face ID
- [ ] Шифрование - защита данных в покое и в транзите

## 🚀 Быстрый доступ к руководствам

### По уровню сложности
- **Начинающий**: [[iOS/UI/swiftui|SwiftUI Basics]], [[iOS/Architecture/mvc-model-view-controller|MVC Pattern]]
- **Средний**: [[iOS/Concurrency & Multithreading/4-swift-concurrency-modern-approach|Swift Concurrency]], [[iOS/Memory/arc-mrc|ARC vs MRC]]
- **Продвинутый**: [[iOS/Architecture/clean-architecture|Clean Architecture]], [[iOS/Topics/feature-flags-ab-testing|Feature Flags & A/B Testing]]

### По времени изучения
- **Быстрое изучение (15-30 мин)**: [[iOS/UI/uikit|UIKit Basics]], [[iOS/Persistence/userdefaults|UserDefaults]]
- **Среднее изучение (30-60 мин)**: [[iOS/Networking/urlsession|URLSession]], [[iOS/Concurrency & Multithreading/2-gcd-grand-central-dispatch|GCD]]
- **Глубокое изучение (60+ мин)**: [[iOS/Memory/memory-management-practical-guide|Memory Management]], [[iOS/Architecture/clean-architecture|Clean Architecture]]

## 📊 Статистика руководств

```dataviewjs
const guides = dv.pages('"iOS"')
    .where(p => p.type === "guide" || p.file.name.includes("practical") || p.file.name.includes("how-to"))
    .sort(p => p.title);

dv.header(2, `Всего руководств: ${guides.length}`);

const byTopic = {};
guides.forEach(guide => {
    const topics = Array.isArray(guide.topics) ? guide.topics : [guide.topics];
    topics.forEach(topic => {
        if (topic) {
            byTopic[topic] = (byTopic[topic] || 0) + 1;
        }
    });
});

dv.header(3, "По темам:");
Object.entries(byTopic)
    .sort((a, b) => b[1] - a[1])
    .forEach(([topic, count]) => {
        dv.paragraph(`**${topic}**: ${count} руководств`);
    });
```

## 🔍 Поиск руководств

### По технологиям
- **SwiftUI**: [[iOS/UI/swiftui|SwiftUI Basics]]
- **Combine**: [[iOS/Concurrency & Multithreading/5-reactive-programming|Reactive Programming]]
- **Core Data**: [[iOS/Persistence/core-data|Core Data Guide]]
- **URLSession**: [[iOS/Networking/urlsession|URLSession Guide]]

### По задачам
- **Начать проект**: [[iOS/Tooling & Project Setup/build-process|Build Process]]
- **Управление состоянием**: [[iOS/Architecture/mvvm-model-view-viewmodel|MVVM Pattern]]
- **Оптимизация производительности**: [[iOS/Performance & Profiling|Performance Profiling]]
- **Подготовка к публикации**: [[iOS/App Store & Distribution/app-store-connect|App Store Connect]]

## 🎓 Рекомендуемые последовательности изучения

### Для начинающих iOS разработчиков
1. [[iOS/UI/swiftui|SwiftUI Basics]] (основы интерфейса)
2. [[iOS/Architecture/mvc-model-view-controller|MVC Pattern]] (базовая архитектура)
3. [[iOS/Persistence/userdefaults|UserDefaults]] (простое хранение данных)
4. [[iOS/Networking/urlsession|URLSession]] (сетевые запросы)

### Для разработчиков среднего уровня
1. [[iOS/Architecture/mvvm-model-view-viewmodel|MVVM Pattern]] (современная архитектура)
2. [[iOS/Concurrency & Multithreading/4-swift-concurrency-modern-approach|Swift Concurrency]] (асинхронность)
3. [[iOS/Memory/arc-mrc|ARC vs MRC]] (управление памятью)
4. [[iOS/Persistence/core-data|Core Data]] (сложное хранение данных)

### Для Senior разработчиков
1. [[iOS/Architecture/clean-architecture|Clean Architecture]] (продвинутая архитектура)
2. [[iOS/Topics/feature-flags-ab-testing|Feature Flags & A/B Testing]] (эксперименты)
3. [[iOS/Memory/memory-management-practical-guide|Memory Management]] (оптимизация памяти)
4. [[iOS/Networking/api-client-architecture|API Client Architecture]] (сетевой слой)

## 📝 Создание нового руководства

При создании нового практического руководства следуйте шаблону:

```markdown
---
title: Название руководства
type: guide
topics: [основная-тема, под-тема]
subtopic: конкретная-подтема
status: draft
level: beginner | intermediate | advanced
platforms: [iOS, macOS, watchOS, tvOS]
ios_min: "15.0"
duration: 45m
tags: [ключевые-слова]
---

# Название руководства

## Цель руководства
Краткое описание того, что читатель узнает из этого руководства.

## Предварительные требования
Что нужно знать перед изучением этой темы.

## Шаги реализации
1. Шаг 1
2. Шаг 2
3. Шаг 3

## Примеры кода
Детальные примеры с объяснениями.

## Распространенные ошибки
Что делать НЕ нужно и почему.

## Лучшие практики
Рекомендации по эффективному использованию.

## Дополнительные ресурсы
Ссылки на документацию, статьи, видео.
```

## 🔄 Обновление индекса

Индекс обновляется автоматически с помощью Dataview. Для добавления нового руководства:

1. Создайте файл с типом `guide` в метаданных
2. Укажите правильные topics и subtopic
3. Индекс автоматически включит новое руководство

Последнее обновление индекса: 2024-01-15
