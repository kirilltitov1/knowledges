---
title: MVVM (Model-View-ViewModel)
type: thread
topics: [Architecture]
subtopic: mvvm-model-view-viewmodel
status: draft
---

# MVVM (Model-View-ViewModel)


### Концепция
- Model: Данные и бизнес-логика
- View: UI (UIView, UIViewController)
- ViewModel: Presentation logic
- Data binding

### Реализация
- ViewModel как посредник
- Property observers
- Combine/RxSwift для binding
- Testable ViewModels

### Преимущества
- Лучшая тестируемость
- Разделение ответственности
- Reusable ViewModels

### Недостатки
- Больше кода
- Learning curve
- Boilerplate code

### Когда использовать
- Средние и большие проекты
- Когда нужна тестируемость
- С reactive programming

