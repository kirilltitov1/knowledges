## gRPC для iOS

### Что это
gRPC — это RPC‑фреймворк поверх HTTP/2 с бинарной сериализацией Protobuf. Поддерживает unary вызовы и стриминг (server‑streaming, client‑streaming, bidi).

### Когда использовать
- Требуется высокая производительность и компактность полезной нагрузки.
- Нужны двунаправленные стримы (реaltime‑события, телеметрия, долгоживущие соединения).
- Есть единая контрактная схема и строго типизированная модель домена.

### Плюсы
- HTTP/2 (мультиплексирование, header‑compression, приоритеты).
- Protobuf (скорость/размер, четкие контракты).
- Генерация типобезопасных клиентов.

### Минусы
- Порог входа: генерация кода/инструменты, настройка TLS/ALPN, DevOps.
- Дебаг труднее, чем у REST/JSON.

### Инструменты для iOS
- Клиент: `grpc-swift` (на основе SwiftNIO).
- Сериализация: `SwiftProtobuf`.
- Установка: Swift Package Manager (предпочтительно). Для генерации кода нужны плагины `protoc-gen-swift` и `protoc-gen-grpc-swift`.

Пример генерации (локально):
```bash
protoc \
  --swift_out=./Generated \
  --grpc-swift_out=./Generated \
  --proto_path=./Protos \
  Protos/my_service.proto
```

### Пример клиента на iOS (упрощенно)
```swift
import GRPC
import NIO

let eventLoopGroup = MultiThreadedEventLoopGroup(numberOfThreads: 1)
defer { try? eventLoopGroup.syncShutdownGracefully() }

let channel = ClientConnection
  .usingTLSBackedByNIOSSL(on: eventLoopGroup)
  .connect(host: "api.example.com", port: 443)
defer { try? channel.close().wait() }

let client = My_Service_V1_MyServiceAsyncClient(channel: channel)

// Unary вызов с таймаутом
let options = CallOptions(timeLimit: .timeout(.seconds(5)))
let request = My_Service_V1_GetItemRequest.with { $0.id = "42" }
let response = try await client.getItem(request, callOptions: options)
```

### Практические рекомендации
- Таймауты и ретраи: задавайте явные `CallOptions.timeLimit`, реализуйте backoff.
- TLS/ALPN: используйте TLS 1.2+, проверяйте ALPN на бэкенде. При пиннинге — отдельная валидация.
- Размер сообщений: ограничивайте `maxReceiveMessageLength`/`maxSendMessageLength`.
- Ошибки: маппируйте gRPC‑статусы на доменные ошибки UI. Логируйте `metadata` для диагностики.
- Фоновый режим: долгие стримы требуют внимательного управления жизненным циклом и политики reconnect.
- Совместимость схем: добавляйте поля как optional, избегайте ломающих изменений.

См. также: [protobuf.md](protobuf.md), [rest-vs-grpc-vs-graphql.md](rest-vs-grpc-vs-graphql.md)


