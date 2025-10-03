---
title: VIPER
type: thread
topics: [Architecture]
subtopic: viper
status: draft
---

# VIPER


### Компоненты
- **V**iew: UI отображение
- **I**nteractor: Бизнес-логика
- **P**resenter: Presentation logic
- **E**ntity: Модели данных
- **R**outer: Навигация

### Реализация
- Protocols для каждого компонента
- Unidirectional data flow
- Module-based architecture
- Wireframe/Router для навигации

### Преимущества
- Максимальная модульность
- Отличная тестируемость
- Четкое разделение ответственности
- Масштабируемость

### Недостатки
- Много boilerplate
- Сложность для простых задач
- Steep learning curve
- Много файлов

### Когда использовать
- Большие enterprise приложения
- Команды разработчиков
- Долгосрочные проекты

