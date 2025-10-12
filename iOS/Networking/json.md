---
type: "thread"
status: "draft"
summary: ""
title: "json"
---

## JSON на iOS: `Codable` и практики

### Почему JSON
Текстовый, человекочитаемый формат, повсеместная поддержка, отличный баланс простоты и возможностей. Дефолт для REST и GraphQL‑ответов.

### Инструменты iOS
- `Codable` (`Decodable`/`Encodable`), `JSONDecoder`/`JSONEncoder`.
- `URLSession` для HTTP.

### Рецепты
- Имена полей: `decoder.keyDecodingStrategy = .convertFromSnakeCase` если сервер snake_case.
- Даты/время: настройте `dateDecodingStrategy` (ISO8601/форматер/миллисекунды epoch).
- Числа как строки: кастомные `init(from:)`/`encode(to:)` либо обертки (`LosslessStringConvertible`).
- Необязательные поля: делайте их `Optional`, задавайте безопасные дефолты.
- Частичный парсинг: выделяйте подмодели, не пытайтесь «глотать» `Any`; избегайте `JSONSerialization` без нужды.
- Ошибки: типизированные модели ошибок сервера; не теряйте контекст (trace‑id, код, сообщение).
- Производительность: избегайте лишних копий `Data`, крупные ответы — разбирать по кускам/стримить на сервере, на клиенте — пагинация.

### Кэш и идемпотентность
- Используйте ETag/Last‑Modified, `URLCache`, валидируйте кэш-стратегии.
- Для POST/модификаторов — идемпотентные ключи, ретраи только для безопасных методов.

### Безопасность и наблюдаемость
- Логируйте безопасно: не пишите PII/секреты, маскируйте токены.
- Включайте метаданные запросов: latency, код ответа, размер, сетевой тип.

Пример декодера с базовыми стратегиями:
```swift
let decoder = JSONDecoder()
decoder.keyDecodingStrategy = .convertFromSnakeCase
decoder.dateDecodingStrategy = .iso8601
let model = try decoder.decode(User.self, from: data)
```

См. также: [rest-api.md](rest-api.md), [graphql.md](graphql.md)


