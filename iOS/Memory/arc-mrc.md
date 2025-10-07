---
title: ARC vs MRC
type: thread
topics: [Memory Management, ARC]
subtopic: ARC & MRC
status: draft
level: intermediate
platforms: [iOS, macOS, watchOS, tvOS]
ios_min: "10.0"
duration: 30m
tags: [memory-management, automatic-reference-counting, manual-reference-counting, retain-cycles]
---

# ARC vs MRC

## Теоретические основы

### Что такое ARC (Automatic Reference Counting)?
**ARC** — это механизм автоматического управления памятью в Swift и Objective-C, где компилятор автоматически вставляет вызовы `retain`, `release` и `autorelease` для управления жизненным циклом объектов.

### Что такое MRC (Manual Reference Counting)?
**MRC** — ручное управление памятью в Objective-C, где разработчик самостоятельно вызывает `retain`, `release` и `autorelease` для управления памятью объектов.

## Как работает ARC

### Принципы работы
1. **Сильные ссылки (strong references)**: Объекты с сильными ссылками не удаляются из памяти
2. **Слабые ссылки (weak references)**: Не влияют на время жизни объекта
3. **Ненадежные ссылки (unowned references)**: Аналогичны слабым, но не опциональные

### Механизм подсчета ссылок
```swift
class Person {
    var name: String
    var passport: Passport? // strong reference

    init(name: String) {
        self.name = name
        print("Person \(name) initialized")
    }

    deinit {
        print("Person \(name) deinitialized")
    }
}

class Passport {
    var number: String
    var owner: Person? // strong reference

    init(number: String) {
        self.number = number
        print("Passport \(number) initialized")
    }

    deinit {
        print("Passport \(number) deinitialized")
    }
}

// Использование
var person: Person? = Person(name: "John")
var passport: Passport? = Passport(number: "12345")

person?.passport = passport
passport?.owner = person

// Reference count: person = 1, passport = 1
// Когда мы обнуляем ссылки:
person = nil    // person reference count = 0 → deinit
passport = nil  // passport reference count = 0 → deinit
```

### Проблемы с памятью

#### Retain Cycles (Циклы удержания)
```swift
class A {
    var b: B?
    deinit { print("A deinitialized") }
}

class B {
    var a: A?
    deinit { print("B deinitialized") }
}

// Создаем цикл удержания
let a = A()
let b = B()
a.b = b
b.a = a

// Ни один объект не будет удален из памяти!
// Решение: использовать weak или unowned
class B {
    weak var a: A?  // слабая ссылка
    deinit { print("B deinitialized") }
}
```

## Objective-C и MRC

### Основные правила MRC
```objc
// Создание объекта
NSObject *obj = [[NSObject alloc] init];  // reference count = 1

// Увеличение счетчика ссылок
[obj retain];  // reference count = 2

// Уменьшение счетчика ссылок
[obj release];  // reference count = 1

// Автоматическое освобождение
[obj autorelease];  // будет вызван release позже
```

### Правила владения (Ownership Rules)
1. **Alloc/Init/New/Copy/MutableCopy** → владелец объекта
2. **Другие методы** → autorelease объект

```objc
// Правило 1: alloc/init создает владельца
NSString *str1 = [[NSString alloc] initWithString:@"Hello"];
// Нужно вызвать [str1 release] или [str1 autorelease]

// Правило 2: методы без alloc возвращают autorelease объекты
NSString *str2 = [NSString stringWithString:@"World"];
// Автоматически autorelease, не нужно вручную управлять памятью
```

## Autorelease Pool

### Что такое Autorelease Pool?
**Autorelease Pool** — механизм отложенного освобождения памяти в Objective-C. Объекты, помеченные как `autorelease`, добавляются в пул и освобождаются только при сбросе пула.

### Когда использовать
```swift
// В цикле с большим количеством временных объектов
for i in 0..<10000 {
    @autoreleasepool {
        let data = try? Data(contentsOf: url)  // может создать много временных объектов
        // Обработка данных
    }  // Пул сбрасывается, память освобождается
}
```

### В Swift
```swift
@autoreleasepool {
    // Код, создающий много временных Foundation объектов
    let array = NSArray(array: [1, 2, 3])
    let string = NSString(string: "Hello")
}
```

## Практические рекомендации

### В Swift (ARC)
1. **Используйте weak для делегатов и замыканий**
2. **Используйте unowned только если уверены, что объект не будет nil**
3. **Избегайте циклов удержания** между объектами
4. **Используйте @autoreleasepool в циклах** с Foundation объектами

### В Objective-C (MRC)
1. **Следуйте правилам владения**
2. **Используйте @autoreleasepool в циклах**
3. **Будьте осторожны с многопоточностью**
4. **Тестируйте на утечки памяти**

## Инструменты диагностики

### Memory Graph Debugger
- Визуализация графа объектов в памяти
- Поиск циклов удержания
- Анализ цепочек владения

### Instruments - Allocations
- Мониторинг выделения памяти
- Поиск утечек (Leaks)
- Анализ роста памяти

### Xcode Memory Debugger
- Просмотр объектов в памяти
- Поиск сильных циклов
- Анализ retain/release операций

## Вопросы собеседований

### Теоретические вопросы
- В чем концепция ARC и MRC и что это такое?
- В какой момент ARC помогает нам с управлением памятью и что он делает?
- Что такое strong ссылка?
- Что такое retain cycle и как его избежать?
- Слышал ли что-то про Autorelease pool?
- Если понимание что такое MRC, как работает?

### Практические вопросы
- Покажите пример retain cycle и как его исправить
- Когда нужно использовать weak/unowned ссылки?
- Как работает @autoreleasepool в Swift?
- Чем отличается strong от weak ссылки?

## Связанные темы
- [[autorelease-pool|Autorelease Pool]]
- [[memory-debugging|Отладка памяти]]
- [[retain-cycles|Циклы удержания]]

## 📅 Система обновления знаний

### Последнее обновление
- **Дата**: 2024-01-15
- **Версия**: iOS 17.2, Swift 5.9, Xcode 15.2
- **Источники**:
  - [WWDC 2023: Improve app performance with SwiftUI](https://developer.apple.com/videos/play/wwdc2023/10169/)
  - [The Swift Programming Language](https://docs.swift.org/swift-book/LanguageGuide/MemorySafety.html)
  - [Automatic Reference Counting](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/MemoryMgmt/Articles/MemoryMgmt.html)

### Что изменилось
- Добавлены примеры с современным Swift синтаксисом (iOS 17+)
- Обновлены рекомендации по использованию weak/unowned ссылок
- Добавлены практические примеры retain cycles
- Улучшены объяснения Objective-C MRC

### План следующего обновления
- Добавить примеры с async/await и памятью
- Обновить для iOS 18+ features
- Добавить больше примеров инструментов диагностики
