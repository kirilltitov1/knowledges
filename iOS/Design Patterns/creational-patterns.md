---
title: Creational Patterns (Порождающие)
type: thread
topics: [Design Patterns]
subtopic: creational-patterns
status: draft
---

# Creational Patterns (Порождающие)


### Singleton
```swift
class NetworkManager {
    static let shared = NetworkManager()
    private init() {}
}
```
- Единственный экземпляр класса
- Глобальная точка доступа
- Когда использовать и когда избегать

### Factory Method
- Создание объектов через фабричный метод
- Абстракция процесса создания
- Protocol-based factories в Swift

### Abstract Factory
- Создание семейств связанных объектов
- Независимость от конкретных классов

### Builder
- Пошаговое создание сложных объектов
- Fluent interface
- Builder с generics в Swift

### Prototype
- Клонирование объектов
- NSCopying в Objective-C
- Copy-on-write в Swift

