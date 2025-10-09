---
title: Protobuf на iOS: SwiftProtobuf и эволюция схем
type: thread
topics: [Networking]
subtopic: Protobuf
status: draft
level: intermediate
platforms: [iOS]
ios_min: "13.0"
duration: 45m
tags: [protobuf, swiftprotobuf, protoc, schema-evolution, oneof, compatibility]
---

## Protobuf на iOS: SwiftProtobuf и эволюция схем

### Что это
Protocol Buffers — бинарный формат сериализации от Google. Компактный, быстрый, со строгими контрактами. Часто используется вместе с gRPC, но может применяться и отдельно.

### Плюсы/минусы
- Плюсы: размер и скорость, четкая схема, обратная совместимость при правильной эволюции.
- Минусы: нужна генерация кода, бинарные полезные нагрузки сложнее инспектировать глазами.

### Инструменты iOS
- Библиотека: `SwiftProtobuf` (через Swift Package Manager).
- Генерация: `protoc` + плагин `protoc-gen-swift`.

Пример схемы:
```proto
syntax = "proto3";
package user.v1;

message User {
  int64 id = 1;
  string name = 2;
  string email = 3;
}
```

Код в Swift:
```swift
import SwiftProtobuf

var user = User.with {
  $0.id = 123
  $0.name = "Alice"
}

let data = try user.serializedData()
let decoded = try User(serializedData: data)
```

### Эволюция схем
- Добавляйте новые поля с новыми номерами; не переиспользуйте теги.
- Для удаляемых полей — используйте `reserved` номера/имена.
- Отдавайте предпочтение optional вместо обязательных полей в мобильных API.
- Для взаимоисключающих вариантов — `oneof`.

### Практика для iOS
- Версионирование эндпоинтов/пакетов (например, `user.v1`).
- Совместимость: клиент должен терпимо относиться к неизвестным полям.
- Смешанные миры: при необходимости используйте JSON‑маппинг Protobuf для логов/диагностики.

См. также: [grpc.md](grpc.md)


