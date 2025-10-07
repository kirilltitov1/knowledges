---
title: Шпаргалка по структуре объектов Objective-C и управлению памятью
type: cheat-sheet
topics: [Memory Management, Objective-C Runtime, Low-Level]
subtopic: objective-c-memory-structure
status: draft
level: advanced
platforms: [iOS, macOS, watchOS, tvOS]
ios_min: "10.0"
duration: 45m
tags: [objective-c, memory-structure, isa-pointer, stack-heap, objc-runtime]
---

# 🧠 Шпаргалка: Структура объектов Objective-C и память

## Введение

Эта шпаргалка объясняет низкоуровневую структуру объектов в Objective-C, как происходит поиск объектов в памяти и как добраться до места объекта в RAM.

## Основные понятия

### Стек vs Куча (Stack vs Heap)

#### Стек (Stack)
- **Быстрая память** для локальных переменных и вызовов функций
- **Автоматическое управление** - память освобождается при выходе из scope
- **Ограниченный размер** (обычно 1-8 MB)
- **Последовательный доступ** (LIFO)

```objc
// Стек содержит:
void function() {
    int localVar = 42;        // ← На стеке
    NSObject *obj = [[NSObject alloc] init]; // ← Указатель на куче
    NSString *str = @"hello"; // ← Указатель на константу
}
```

#### Куча (Heap)
- **Динамическая память** для объектов с произвольным временем жизни
- **Ручное/автоматическое управление** через ARC/MRC
- **Большой размер** (ограничен только памятью устройства)
- **Фрагментация** возможна

```objc
// Куча содержит:
NSObject *obj = [[NSObject alloc] init];  // ← Объект на куче
// obj - это указатель на стеке, указывающий на объект в куче
```

## Структура объекта Objective-C

### Внутренняя структура

```objc
// Объект в памяти выглядит примерно так:
typedef struct objc_object {
    Class isa;  // ← Указатель на класс (первые 8 байт на 64-бит)
} *id;

// Структура класса:
struct objc_class {
    Class isa;           // Указатель на метакласс
    Class super_class;   // Указатель на суперкласс
    const char *name;    // Имя класса
    long version;
    long info;
    long instance_size;  // Размер экземпляра
    struct objc_ivar_list *ivars;  // Список переменных экземпляра
    struct objc_method_list *methodLists;  // Список методов
    struct objc_cache *cache;      // Кеш методов
    struct objc_protocol_list *protocols;  // Протоколы
};
```

### ISA указатель

**ISA** — это указатель на структуру класса объекта, который находится в начале каждого объекта Objective-C.

```objc
// Когда мы создаем объект:
NSObject *obj = [[NSObject alloc] init];

// В памяти это выглядит так:
// ┌─────────────────────────────────────────┐
// │           ISA pointer (8 байт)          │ ← obj->isa указывает сюда
// ├─────────────────────────────────────────┤
// │           ivar 1                        │
// ├─────────────────────────────────────────┤
// │           ivar 2                        │
// ├─────────────────────────────────────────┤
// │           ...                           │
// └─────────────────────────────────────────┘

// obj->isa содержит адрес структуры objc_class для NSObject
```

## Как добраться до объекта в RAM

### Шаг 1: Переменная на стеке
```objc
NSObject *obj = [[NSObject alloc] init];
// obj - это локальная переменная на стеке
// Она содержит адрес объекта в куче (8 байт на 64-бит системе)
```

### Шаг 2: Разыменование указателя
```objc
// Чтобы получить объект, процессор:
// 1. Берет значение obj (адрес в куче)
// 2. Переходит по этому адресу в кучу
// 3. Получает структуру объекта

// В LLDB это можно увидеть так:
po obj              // Показывает объект
p obj               // Показывает адрес объекта
p &obj              // Показывает адрес указателя
p *obj              // Разыменование (сам объект)
```

### Шаг 3: ISA pointer
```objc
// Первый член структуры объекта - isa
// obj->isa содержит адрес структуры objc_class

Class objClass = obj->isa;  // Получаем класс объекта
const char *className = objClass->name;  // Получаем имя класса
```

## Механизм поиска методов (Method Resolution)

### 1. Кеш методов (Method Cache)
```objc
// Сначала проверяется кеш методов класса
struct objc_cache *cache = objClass->cache;

// Кеш содержит быстрые соответствия:
// selector -> implementation
```

### 2. Поиск в списках методов
```objc
// Если не найдено в кеше, ищется в methodLists класса
struct objc_method_list *methods = objClass->methodLists;

// Поиск по селектору (SEL)
SEL selector = @selector(description);
Method method = method_getInstanceMethod(objClass, selector);
```

### 3. Поиск в суперклассах
```objc
// Если не найдено в текущем классе, поиск в суперклассах
Class superClass = objClass->super_class;
if (superClass) {
    // Рекурсивный поиск в суперклассе
    method = method_getInstanceMethod(superClass, selector);
}
```

## Практические примеры в LLDB

### Исследование структуры объекта
```bash
# В LLDB при отладке:
(lldb) po obj                    # Показать объект
(lldb) p obj                     # Показать адрес объекта
(lldb) p &obj                    # Показать адрес указателя
(lldb) p obj->isa                # Показать ISA pointer
(lldb) p obj->isa->name          # Показать имя класса
(lldb) p obj->isa->ivars         # Показать ivars класса
```

### Исследование памяти
```bash
# Карта памяти процесса
(lldb) vmmap
# История выделения памяти
(lldb) malloc_history $pid 0xADDRESS
# Инспекция памяти по адресу
(lldb) x/gx 0xADDRESS
```

## Важные моменты

### 1. Tagged Pointers
```objc
// Маленькие объекты (NSNumber, NSDate) могут храниться прямо в указателе
NSNumber *smallNumber = @42;
// smallNumber - это не указатель на кучу, а сам объект в указателе
```

### 2. Слабые ссылки (__weak)
```objc
// Слабые ссылки хранятся в специальных хэш-таблицах
__weak NSObject *weakRef = obj;
// weakRef регистрируется в side table для автоматической очистки
```

### 3. Автоматическое освобождение
```objc
// Авторелизованные объекты добавляются в пул
@autoreleasepool {
    NSString *str = [NSString stringWithFormat:@"Hello %@", name];
    // str добавляется в autorelease pool
} // Пул очищается здесь
```

## Вопросы для самопроверки

1. **Что лежит на стеке?** Локальные переменные, указатели на объекты, параметры функций
2. **Что лежит в куче?** Сама структура объекта (данные экземпляра)
3. **Что такое ISA?** Указатель на структуру класса в начале каждого объекта
4. **Как найти класс объекта?** Через `obj->isa`
5. **Как найти адрес объекта?** Через значение указателя `NSObject *obj`
6. **Где хранится ISA?** В первых 8 байтах структуры объекта
7. **Как работает поиск методов?** Кеш → списки методов класса → суперклассы

## Полезные команды LLDB

```bash
# Структура объекта
(lldb) p *(objc_object *)obj
# Класс объекта
(lldb) p obj->isa
# Имя класса
(lldb) p obj->isa->name
# Размер объекта
(lldb) p obj->isa->instance_size
# Методы класса
(lldb) p obj->isa->methodLists
```

## Заключение

Понимание структуры памяти в Objective-C критически важно для:
- **Отладки** сложных проблем с памятью
- **Оптимизации** производительности
- **Понимания** работы ARC и MRC
- **Анализа** crash-дампов

Помните: каждый указатель на объекте — это адрес в куче, где первые байты содержат ISA, указывающий на класс с метаданными.

## 📅 Система обновления знаний

### Последнее обновление
- **Дата**: 2024-01-15
- **Версия**: iOS 17.2, Xcode 15.2
- **Источники**:
  - [Objective-C Runtime Programming Guide](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/ObjCRuntimeGuide/)
  - [LLDB Debuggger Tutorial](https://lldb.llvm.org/use/tutorial.html)
  - [WWDC: Understanding Runtime](https://developer.apple.com/videos/play/wwdc2014/416/)

### План следующего обновления
- Добавить примеры с Swift объектами
- Обновить для новых фич Objective-C runtime
- Добавить больше примеров LLDB команд
