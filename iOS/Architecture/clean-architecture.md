---
type: "thread"
status: "draft"
summary: ""
title: "Clean Architecture"
---

# Clean Architecture


### Слои
1. **Domain Layer**
   - Entities
   - Use Cases
   - Repository Interfaces
2. **Data Layer**
   - Repository Implementations
   - Data Sources (API, DB)
   - Mappers
3. **Presentation Layer**
   - ViewModels/Presenters
   - Views
   - UI Logic

### Принципы
- Dependency Rule
- Dependency Inversion
- Use Cases
- Domain-driven design

### Преимущества
- Независимость от фреймворков
- Тестируемость
- Масштабируемость
- Переиспользование

### Реализация в iOS
- Protocol-oriented programming
- Dependency Injection
- Repository pattern
- Use Case pattern

