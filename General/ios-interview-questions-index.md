---
type: "index"
status: "draft"
title: "iOS Interview Questions Index"
---

# 🎯 Индекс вопросов для собеседований iOS разработчиков

Централизованный индекс всех материалов по подготовке к техническим собеседованиям на позиции iOS разработчика.

## 📋 Структура подготовки

### 🎯 Основные категории вопросов
1. **Технические вопросы** - Swift, iOS SDK, архитектура, алгоритмы
2. **Системный дизайн** - проектирование мобильных систем
3. **Поведенческие вопросы** - soft skills, опыт работы
4. **Алгоритмы и структуры данных** - решение задач
5. **Производительность и оптимизация** - profiling, memory management

## 📚 Технические вопросы

### 1. Вопросы по iOS SDK и фреймворкам
**Файл:** [[ios-sdk-interview-questions|Вопросы по iOS SDK и фреймворкам]]

**Темы:**
- **UIKit** - ViewController lifecycle, Auto Layout, responder chain
- **SwiftUI** - State management, View modifiers, data binding
- **Core Data** - Managed objects, relationships, migrations
- **Foundation** - Collections, strings, threading
- **AVFoundation** - Media playback, camera capture
- **Core Location** - GPS, geocoding, background location
- **MapKit** - Maps, annotations, overlays

### 2. Архитектура и паттерны
**Файл:** [[ios-architecture-interview-questions|Вопросы по архитектуре iOS приложений]]

**Темы:**
- **MVC vs MVVM vs VIPER** - сравнение паттернов
- **Clean Architecture** - принципы независимости от фреймворков
- **Coordinator Pattern** - навигация без связанности
- **Dependency Injection** - внедрение зависимостей
- **Тестируемость архитектуры** - mocking, protocols

### 3. Многопоточность и асинхронность
**Файл:** [[ios-concurrency-interview-questions|Вопросы по многопоточности и асинхронности]]

**Темы:**
- **GCD** - Queues, QoS, DispatchGroup
- **Async/Await** - Structured concurrency, Task groups
- **Actors** - Data isolation, thread safety
- **Thread Safety** - Race conditions, atomic operations
- **Operation Queue** - Dependencies, cancellation

### 4. Производительность и оптимизация
**Файл:** [[ios-performance-interview-questions|Вопросы по производительности и оптимизации]]

**Темы:**
- **Memory Management** - ARC, retain cycles, leaks
- **App Launch** - Cold start optimization, lazy initialization
- **Battery Optimization** - Location, network, background tasks
- **UI Performance** - Frame rate, layout optimization
- **Instruments** - Profiling tools, custom metrics

## 🧠 Алгоритмы и структуры данных

### Алгоритмические вопросы для iOS собеседований
**Файл:** [[ios-interview-algorithms|Алгоритмы и структуры данных для собеседований iOS]]

**Темы:**
- **Массивы и строки** - Two Sum, Maximum Subarray, Valid Parentheses
- **Связанные списки** - Reverse List, Cycle Detection, Merge Lists
- **Деревья и графы** - Tree Traversal, Number of Islands, BFS/DFS
- **Динамическое программирование** - Fibonacci, Climbing Stairs, Coin Change
- **Рекурсия и backtracking** - Permutations, Generate Parentheses

## 🏗️ System Design

### Системный дизайн для мобильных приложений
**Файл:** [[ios-system-design-interviews|System Design для собеседований iOS разработчиков]]

**Сценарии:**
- **Социальная сеть** - Feed, real-time updates, media storage
- **Мессенджер** - Chat, offline mode, E2E encryption
- **E-commerce** - Catalog, cart, payment processing
- **Ride-sharing** - Real-time location, matching algorithm

## 🎭 Поведенческие вопросы

### Soft skills и опыт работы
**Файл:** [[ios-behavioral-interview-questions|Поведенческие вопросы для собеседований iOS разработчиков]]

**Категории:**
- **Работа в команде** - конфликты, коммуникация, code review
- **Решение проблем** - отладка, дедлайны, технические вызовы
- **Лидерство** - инициатива, развитие команды, мотивация
- **Обучение** - изучение технологий, профессиональный рост

## 📊 Статистика вопросов

```dataviewjs
const questions = dv.pages('"General"')
    .where(p => p.file.name.includes("interview") && p.file.name.includes("questions"))
    .sort(p => p.title);

dv.header(2, `Всего материалов: ${questions.length}`);

const categories = {};
questions.forEach(file => {
    const tags = Array.isArray(file.tags) ? file.tags : [];
    tags.forEach(tag => {
        if (tag && tag.includes("interview")) {
            categories[tag] = (categories[tag] || 0) + 1;
        }
    });
});

dv.header(3, "По категориям:");
Object.entries(categories)
    .sort((a, b) => b[1] - a[1])
    .forEach(([category, count]) => {
        dv.paragraph(`**${category}**: ${count} материалов`);
    });
```

## 🚀 Рекомендуемые последовательности изучения

### Для начинающих iOS разработчиков (Junior)
1. **Основы Swift** - опционалы, closures, protocols
2. **iOS SDK** - UIKit, Auto Layout, ViewController lifecycle
3. **Базовая архитектура** - MVC, простые паттерны
4. **Основы многопоточности** - GCD, main queue

### Для разработчиков среднего уровня (Middle)
1. **Архитектура приложений** - MVVM, Coordinator, DI
2. **Производительность** - memory management, Instruments
3. **Современные практики** - async/await, Combine, SwiftUI
4. **Алгоритмы** - базовые структуры данных, простые алгоритмы

### Для Senior разработчиков
1. **Системный дизайн** - проектирование масштабируемых систем
2. **Продвинутые алгоритмы** - сложные структуры данных, оптимизации
3. **Архитектура** - Clean Architecture, DDD, microservices
4. **Лидерство** - командная работа, архитектурные решения

## 🎯 Стратегии подготовки

### 1. Техническая подготовка
- **Практикуйте кодинг** на LeetCode/HackerRank (минимум 3 задачи в неделю)
- **Изучайте фреймворки глубоко** - не только API, но и принципы работы
- **Создавайте pet projects** для демонстрации навыков
- **Изучайте современные технологии** - SwiftUI, Combine, async/await

### 2. Практическая подготовка
- **Решайте задачи на доске** - практикуйте объяснение решений вслух
- **Анализируйте чужой код** - читайте open source проекты
- **Создавайте портфолио** - GitHub с качественными проектами
- **Изучайте инструменты** - Instruments, Xcode debugging

### 3. День собеседования
- **Будьте уверены** - показывайте энтузиазм и интерес
- **Объясняйте ход мыслей** - говорите вслух при решении задач
- **Задавайте вопросы** - покажите интерес к компании и проекту
- **Будьте честны** - если не знаете ответ, скажите об этом

## 📈 Метрики успеха

### Количественные показатели
- **Решенные задачи**: минимум 100 алгоритмических задач
- **Проекты в портфолио**: 3-5 качественных проекта
- **Чтение кода**: анализ 10+ open source проектов
- **Технические статьи**: 20+ прочитанных статей

### Качественные показатели
- **Глубина понимания** - объяснение не только "как", но и "зачем"
- **Практическое применение** - реальные проекты с использованием изученного
- **Коммуникация** - умение объяснять сложные концепции простыми словами

## 🔗 Связанные материалы

### Теоретические основы
- [[iOS/Memory/arc-mrc|ARC vs MRC]] - управление памятью
- [[iOS/Architecture/clean-architecture|Clean Architecture]] - принципы архитектуры
- [[iOS/Concurrency & Multithreading/4-swift-concurrency-modern-approach|Swift Concurrency]] - современная асинхронность

### Практические руководства
- [[iOS/Memory/memory-management-practical-guide|Практическое управление памятью]]
- [[iOS/Tooling & Project Setup/xcode-integration-guide|Интеграция с Xcode]]
- [[iOS/Testing/unit-testing-guide|Unit Testing руководство]]

### Упражнения и викторины
- [[iOS/Exercises/memory-management-quiz|Викторина по управлению памятью]]
- [[iOS/practical-guides-index|Индекс практических руководств]]

## 📚 Внешние ресурсы

### Платформы для практики
- **LeetCode** - алгоритмические задачи с фокусом на iOS
- **HackerRank** - технические интервью и алгоритмы
- **CodeSignal** - оценка навыков программирования
- **SystemDesignInterview.com** - вопросы системного дизайна

### Книги
- "Cracking the Coding Interview" by Gayle Laakmann McDowell
- "iOS Programming: The Big Nerd Ranch Guide"
- "Effective Objective-C 2.0" by Matt Galloway

### Онлайн курсы
- [Stanford CS193p - iOS Development](https://cs193p.sites.stanford.edu/)
- [Ray Wenderlich iOS Courses](https://www.raywenderlich.com/ios)
- [Hacking with Swift](https://www.hackingwithswift.com/)

## ✅ Финальная проверка готовности

### Перед собеседованием убедитесь:

**Технические навыки:**
- [ ] Знаю основы Swift (опционалы, closures, protocols, generics)
- [ ] Понимаю iOS SDK (UIKit, Foundation, Core Data)
- [ ] Знаю архитектурные паттерны (MVC, MVVM, VIPER)
- [ ] Понимаю многопоточность (GCD, async/await, actors)
- [ ] Знаю инструменты разработки (Xcode, Instruments)

**Практические навыки:**
- [ ] Могу решить алгоритмические задачи среднего уровня
- [ ] Могу спроектировать простую систему
- [ ] Могу объяснить технические решения
- [ ] Имею портфолио проектов

**Soft skills:**
- [ ] Могу рассказать о своем опыте структурировано
- [ ] Могу объяснить сложные концепции простыми словами
- [ ] Задаю релевантные вопросы интервьюеру
- [ ] Показываю энтузиазм и интерес

## 🎯 Заключение

Подготовка к техническим собеседованиям iOS разработчика требует системного подхода и регулярной практики. Используйте эту базу знаний как основу для изучения и регулярно обновляйте свои знания новыми технологиями и практиками.

**Помните:** "Лучшая подготовка - это не зазубривание ответов, а глубокое понимание технологий и умение применять знания на практике."

Последнее обновление: 2024-01-15
