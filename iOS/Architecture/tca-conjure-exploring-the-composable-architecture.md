---
type: "article"
status: "draft"
summary: ""
title: "Tca Conjure Exploring The Composable Architecture"
---

# Exploring the Composable Architecture (Conjure, 2023)

Статья даёт краткое введение в The Composable Architecture (TCA) от Point‑Free и показывает, как применять её в SwiftUI/Combine‑проектах с акцентом на композицию, тестируемость и управление сайд‑эффектами.

### Тезисы
- **Назначение**: единообразная архитектура с односторонним потоком данных и явными зависимостями.
- **Фокус**: композиция фич, тестируемость редьюсеров/эффектов, эргономика работы со стейтом.
- **Сайд‑эффекты**: управляются через эффекты и зависимости; легко изолировать и покрывать тестами.

### Компоненты TCA
- **State** — данные фичи (истина хранится в одном месте).
- **Action** — все возможные события/намерения.
- **Reducer** — чистая функция, изменяющая состояние по экшену.
- **Store** — принимает экшены, прогоняет редьюсер, хранит состояние.
- **Effect** — операции вне «локального» контекста (асинхронщина, I/O и т. п.).
- **Environment/Dependencies** — (в TCA 1.x) окружение; в современных версиях — внедрение через `@Dependency`.

### Поток данных (упрощённо)
1. View отправляет `Action` в `Store`.
2. `Store` вызывает `Reducer`, который мутирует `State` и может вернуть `Effect`.
3. Эффект диспатчит новые `Action` по завершении.
4. Обновлённый `State` пробрасывается в View → UI реагирует.

### Интеграция со SwiftUI
- `WithViewStore` упрощает подписку на состояние и отправку экшенов без `ObservedObject`‑обёрток.
- Биндинги можно строить прямо из `Store` по отдельным полям состояния.

### Зависимости
- В примере используются зависимости через `@Dependency` с предварительной регистрацией (см. `TCA+Dependencies.swift` в демо).
- Это упрощает подмену зависимостей в тестах.

### Демо (из статьи)
- Фича `BusStopFeature` (реализует `ReducerProtocol`): `State`, `Action`, `reducer` в одном модуле.
- Тап по остановке → `selectStop` → редьюсер выставляет `selectedStop` и возвращает эффект → `setSheet` выставляет `isSheetPresented` → View презентует шит (биндинг от стора).

### Когда использовать
- Проекты со сложным состоянием, требующие предсказуемости, масштабируемости и тестируемости.
- Командам, которым важна композиция фич и прозрачные сайд‑эффекты.

### Плюсы
- Прозрачный односторонний поток данных, удобная отладка.
- Сильная тестируемость редьюсеров/эффектов.
- Чёткая композиция фич и изоляция состояния.

### Минусы
- Порог входа; может казаться подробной/многословной для простых экранов.
- Возможные оверхеды по производительности без аккуратной структуры.

### Установка (SPM)
В Xcode: File → Add Packages → добавить репозиторий `https://github.com/pointfreeco/swift-composable-architecture`.

### Ссылки
- Статья: [Exploring the Composable Architecture Framework — Conjure (2023)](https://insight.conjure.co.uk/the-composable-architecture-2eae60963248)
- Репозиторий TCA: [pointfreeco/swift-composable-architecture](https://github.com/pointfreeco/swift-composable-architecture)
- Демо из статьи: [conjure/demo-ios-tca](https://github.com/conjure/demo-ios-tca)
- Коллекция материалов: [Point‑Free — Composable Architecture](https://www.pointfree.co/collections/composable-architecture)
- Видео: [Swift & Tips](https://youtu.be/SfFDj6qT-xg), [Zach Eriksen](https://youtu.be/MmzMHNO9cno)

### Связанные заметки
- [[redux-tca-the-composable-architecture]]


