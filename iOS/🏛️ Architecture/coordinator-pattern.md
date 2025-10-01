---
title: Coordinator Pattern
type: thread
topics: [Architecture]
subtopic: coordinator-pattern
status: draft
---

# Coordinator Pattern


### Концепция
- Централизованная навигация
- Отделение навигации от ViewController
- Flow coordination

### Реализация
```swift
protocol Coordinator {
    var childCoordinators: [Coordinator] { get set }
    var navigationController: UINavigationController { get set }
    func start()
}
```

### Типы координаторов
- App Coordinator
- Tab Bar Coordinator
- Flow Coordinators
- Child Coordinators

### Преимущества
- Reusable flows
- Deep linking упрощается
- A/B testing flows
- Testable navigation

### Недостатки
- Additional complexity
- Memory management
- Coordinator lifecycle

