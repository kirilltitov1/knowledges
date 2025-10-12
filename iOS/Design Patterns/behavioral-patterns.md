---
type: "thread"
status: "draft"
summary: ""
title: "Behavioral Patterns"
---

# Behavioral Patterns (Поведенческие)


### Observer
- Уведомление об изменениях
- NotificationCenter
- KVO (Key-Value Observing)
- Combine Publishers
- Property observers (didSet, willSet)

### Delegate
- Делегирование обязанностей
- Protocol-based delegation
- Weak references для предотвращения retain cycles

### Strategy
- Взаимозаменяемые алгоритмы
- Protocol-based strategies
- Инкапсуляция алгоритмов

### Command
- Инкапсуляция запросов
- Undo/Redo functionality
- Target-Action в UIKit

### Iterator
- Последовательный доступ к элементам
- Sequence и IteratorProtocol
- for-in loops

### State
- Изменение поведения при изменении состояния
- Enum-based state machines
- State pattern в UI

### Template Method
- Определение скелета алгоритма
- Subclass customization
- Protocol extensions с default implementations

### Chain of Responsibility
- Передача запроса по цепочке обработчиков
- Responder chain в UIKit
- Error handling chain

### Memento
- Сохранение и восстановление состояния
- State restoration
- NSCoding, Codable

### Mediator
- Централизованное взаимодействие объектов
- Coordinator pattern
- Уменьшение связности

### Visitor
- Операции над элементами структуры
- Double dispatch
- Type-safe operations

### Interpreter
- Интерпретация языка или выражений
- DSL (Domain Specific Language)
- Expression evaluation

