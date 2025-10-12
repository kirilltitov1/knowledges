---
type: "thread"
status: "draft"
summary: ""
title: "websocket"
---

# WebSocket

Полный практический гид по использованию WebSocket в iOS: от протокола и жизненного цикла до устойчивости, безопасности, тестирования и вопросов для собеседований.

### Оглавление
- Что такое WebSocket и когда он нужен
- Протокол в 5 мин: рукопожатие, фреймы, ping/pong, коды закрытия
- API в iOS: URLSessionWebSocketTask
  - Жизненный цикл соединения
  - Отправка и получение сообщений
  - Ping/Pong и закрытие
  - Конфигурация URLSession и делегаты
- Примеры кода
  - Базовое подключение и receive loop
  - Отправка сообщений и обработка backpressure
  - Актор-обёртка WebSocketClient (Swift Concurrency)
  - Heartbeat и таймауты
- Надёжность на мобильных
  - Реконнект с экспоненциальной задержкой и jitter
  - Смена сетей и оффлайн (NWPathMonitor)
  - Background/foreground и ограничения iOS
- Безопасность и авторизация
  - WSS/TLS, ATS, пиннинг сертификата
  - Токены, заголовки, Sec-WebSocket-Protocol
- Форматы сообщений и кейсы
  - Текст/JSON, бинарные (Protobuf, MessagePack)
  - Примеры payload'ов: чат, котировки, presence, GraphQL subscriptions
- Тестирование, отладка и наблюдаемость
- Вопросы для собеседования и чеклист

---

### Что такое WebSocket и когда он нужен
- Двусторонний постоянный канал поверх TCP с минимальными накладными расходами после рукопожатия HTTP(S).
- Предпочтителен, когда нужны низкие задержки и двунаправленность: чат, курсы валют, кооперативное редактирование, live-комменты, игры, телеметрия.
- Альтернативы и сравнение:
  - HTTP polling/long-polling: проще, но выше задержки и нагрузка.
  - Server-Sent Events (SSE): однонаправленно (сервер → клиент), не подходит для двусторонней связи.

### Протокол в 5 мин: рукопожатие, фреймы, ping/pong, коды закрытия
- Рукопожатие: HTTP 1.1 Upgrade до `websocket` с ответом `101 Switching Protocols`. С TLS используется `wss://`.
- Фреймы: текстовые и бинарные, фрагментация поддерживается. Клиентские фреймы обязаны быть маскированы.
- Управляющие фреймы: `ping`, `pong`, `close`.
- Завершение: сторона отправляет `close` с кодом/причиной; другая отвечает `close` и разрывает TCP.
- Типовые коды закрытия: `1000` (normal), `1001` (goingAway), `1006` (abnormal), `1008` (policyViolation), `1011` (internalError).

---

### API в iOS: URLSessionWebSocketTask
- Доступно с iOS 13+. Тип `URLSessionWebSocketTask` (сообщения: `.string(String)` и `.data(Data)`).
- Потокобезопасность: вызывать API из последовательного контекста или обеспечить сериализацию (например, актор/очередь).
- Нет нативных async/await методов — оборачиваем в `AsyncStream`/continuation или используем колбэки.
 - Полезные свойства/делегаты:
   - `maximumMessageSize` — ограничение размера входящего сообщения (по умолчанию 1 МБ).
   - Делегат `URLSessionWebSocketDelegate` с методами `didOpenWithProtocol` и `didCloseWith`.
   - Общие события завершения через `URLSessionTaskDelegate.urlSession(_:task:didCompleteWithError:)`.

#### Жизненный цикл
1) Создание `URLSession` (часто с делегатом и отдельной OperationQueue).
2) `webSocketTask(with:)` → `resume()`.
3) Постоянный receive loop (всегда после обработки сообщения снова вызывать `receive`).
4) Периодический `sendPing` для heartbeat.
5) `cancel(with:reason:)` для корректного закрытия.

#### Отправка и приём
- `send(.string|.data)` с обработкой ошибок и очередью отправки при временной недоступности.
- `receive(completionHandler:)` возвращает `Result<Message, Error>`; важно сразу же вызвать `receive` повторно.

#### Ping/Pong и закрытие
- Клиент может вызывать `sendPing` с callback-ом; измеряем RTT и ставим таймаут.
- Закрытие выполняем кодом `normalClosure` при явном отключении пользователя.

#### Конфигурация URLSession и делегаты
- Собственный `URLSession` с `URLSessionDelegate` для пиннинга/аутентификации и отдельной очередью для изоляции.
- Заголовки/параметры: токен в заголовке `Authorization: Bearer <token>` либо в `Sec-WebSocket-Protocol`.

---

### Примеры кода (секции ниже будут развёрнуты)
#### Базовое подключение и receive loop
```swift
import Foundation

final class WSDelegate: NSObject, URLSessionWebSocketDelegate {
    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didOpenWithProtocol protocol: String?) {
        print("[WS] didOpen, subprotocol=\(protocol ?? "-")")
    }

    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didCloseWith closeCode: URLSessionWebSocketTask.CloseCode, reason: Data?) {
        let reasonText = reason.flatMap { String(data: $0, encoding: .utf8) } ?? "-"
        print("[WS] didClose, code=\(closeCode.rawValue), reason=\(reasonText)")
    }
}

let url = URL(string: "wss://echo.websocket.events")!
let delegate = WSDelegate()
let session = URLSession(configuration: .default, delegate: delegate, delegateQueue: .init())
let task = session.webSocketTask(with: url)
task.resume()

func receiveLoop(_ task: URLSessionWebSocketTask) {
    task.receive { result in
        switch result {
        case .success(let message):
            switch message {
            case .string(let text):
                print("[WS] recv text=", text)
            case .data(let data):
                print("[WS] recv data=", data.count, "bytes")
            @unknown default:
                break
            }
            // Важно снова вызывать receive
            receiveLoop(task)
        case .failure(let error):
            print("[WS] receive error:", error)
        }
    }
}

receiveLoop(task)

task.send(.string("hello")) { error in
    if let error { print("[WS] send error:", error) }
}

task.sendPing { error in
    if let error { print("[WS] ping error:", error) }
}
```

#### Очередь отправки и backpressure
```swift
final class WSSender {
    private let task: URLSessionWebSocketTask
    private var isSending = false
    private var queue: [URLSessionWebSocketTask.Message] = []
    private let maxQueue = 100 // защита от переполнения

    init(task: URLSessionWebSocketTask) {
        self.task = task
    }

    func enqueue(_ message: URLSessionWebSocketTask.Message) {
        if queue.count >= maxQueue { queue.removeFirst() } // политика сброса старых
        queue.append(message)
        pump()
    }

    private func pump() {
        guard !isSending, !queue.isEmpty else { return }
        isSending = true
        let msg = queue.removeFirst()
        task.send(msg) { [weak self] error in
            guard let self else { return }
            self.isSending = false
            if let error { print("[WS] send failed:", error) }
            self.pump()
        }
    }
}
```

#### Актор-обёртка WebSocketClient (с reconnection и heartbeat)
```swift
import Foundation

public enum WebSocketEvent: Sendable {
    case opened(subprotocol: String?)
    case text(String)
    case data(Data)
    case closed(code: URLSessionWebSocketTask.CloseCode, reason: String?)
    case error(Error)
}

public actor WebSocketClient {
    private let url: URL
    private let session: URLSession
    private var task: URLSessionWebSocketTask?
    private var sender: WSSender?
    private var receiveLoopTask: Task<Void, Never>?
    private var heartbeatTask: Task<Void, Never>?
    private var reconnectAttempts = 0
    private let maxBackoff: Double = 30
    private let heartbeatInterval: Double = 20

    public init(url: URL, session: URLSession) {
        self.url = url
        self.session = session
    }

    public func connect() {
        let task = session.webSocketTask(with: url)
        task.maximumMessageSize = 2 * 1024 * 1024 // 2 MB, при необходимости
        task.resume()
        self.task = task
        self.sender = WSSender(task: task)
        startReceiveLoop()
        startHeartbeat()
    }

    public func disconnect() {
        heartbeatTask?.cancel(); heartbeatTask = nil
        receiveLoopTask?.cancel(); receiveLoopTask = nil
        task?.cancel(with: .normalClosure, reason: nil)
        task = nil
        sender = nil
        reconnectAttempts = 0
    }

    public func send(text: String) {
        sender?.enqueue(.string(text))
    }

    public func send(data: Data) {
        sender?.enqueue(.data(data))
    }

    private func startReceiveLoop() {
        guard let task else { return }
        receiveLoopTask = Task { [weakTask = task] in
            guard let task = weakTask else { return }
            while !Task.isCancelled {
                do {
                    let result = try await withCheckedThrowingContinuation { (cont: CheckedContinuation<URLSessionWebSocketTask.Message, Error>) in
                        task.receive { cont.resume(with: $0) }
                    }
                    switch result {
                    case .string(let str):
                        print("[WS] <-", str)
                    case .data(let data):
                        print("[WS] <- data", data.count)
                    @unknown default:
                        break
                    }
                } catch {
                    await scheduleReconnect(after: backoff(for: reconnectAttempts))
                    break
                }
            }
        }
    }

    private func startHeartbeat() {
        guard let task else { return }
        heartbeatTask = Task {
            while !Task.isCancelled {
                try? await Task.sleep(nanoseconds: UInt64(heartbeatInterval * 1_000_000_000))
                await withCheckedContinuation { (cont: CheckedContinuation<Void, Never>) in
                    task.sendPing { error in
                        if let error { print("[WS] ping error:", error) }
                        cont.resume()
                    }
                }
            }
        }
    }

    private func scheduleReconnect(after delay: Double) async {
        reconnectAttempts += 1
        print("[WS] reconnect attempt #\(reconnectAttempts) in \(String(format: "%.2f", delay))s")
        try? await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
        connect()
    }

    private func backoff(for attempt: Int) -> Double {
        let base = min(pow(2.0, Double(attempt)), maxBackoff)
        let jitter = Double.random(in: 0...(base * 0.3))
        return base + jitter
    }
}
```

#### Обёртка в AsyncStream (подписка на события)
```swift
struct WebSocketStreams {
    let events: AsyncStream<WebSocketEvent>
}

func makeStreams(task: URLSessionWebSocketTask) -> WebSocketStreams {
    var continuation: AsyncStream<WebSocketEvent>.Continuation!
    let stream = AsyncStream<WebSocketEvent> { cont in
        continuation = cont
    }

    func loop() {
        task.receive { result in
            switch result {
            case .success(let msg):
                switch msg {
                case .string(let s): continuation.yield(.text(s))
                case .data(let d): continuation.yield(.data(d))
                @unknown default: break
                }
                loop()
            case .failure(let err):
                continuation.yield(.error(err))
                continuation.finish()
            }
        }
    }
    loop()

    return .init(events: stream)
}
```

---

### Надёжность на мобильных
- Экспоненциальный бэкофф с jitter, ограничение максимальной задержки.
- Мониторинг сети `NWPathMonitor` для быстрого переподключения при смене сети.
- В бэкграунде iOS не позволяет держать постоянный WS — закрываемся корректно, на передний план переподключаемся.

#### Реконнект стратегия
- Повтор при ошибках сети/`didClose` с кодами ≠ `normalClosure`.
- Бэкофф: `delay = min(2^attempt, max) + jitter(0..30%)`.
- Сброс счетчика при успешном открытии.

```swift
func backoffDelay(attempt: Int, max: Double = 30) -> Double {
    let base = min(pow(2.0, Double(attempt)), max)
    return base + Double.random(in: 0...(base * 0.3))
}
```

#### Реакция на смену сети
```swift
import Network

final class NetworkObserver {
    private let monitor = NWPathMonitor()
    private let queue = DispatchQueue(label: "net.monitor")
    var onAvailable: (() -> Void)?

    func start() {
        monitor.pathUpdateHandler = { [weak self] path in
            if path.status == .satisfied {
                self?.onAvailable?()
            }
        }
        monitor.start(queue: queue)
    }

    func stop() { monitor.cancel() }
}
```

#### Background/Foreground
- При уходе в фон — по возможности закрывайте WS (`normalClosure`).
- При возвращении — быстрый реконнект, повторная авторизация при истёкшем токене.

---

### Безопасность и авторизация
- Использовать `wss://` и включённый ATS. Для самоподписанных — явная конфигурация доверия.
- Пиннинг сертификата/публичного ключа через делегат `URLSessionDelegate`.
- Авторизация через Bearer-токен/куки/подпротокол; своевременно обновлять токен и переподключаться.
 - Ротация токена: при 401/close с policyViolation — получить новый токен, пересоздать `URLRequest`, переподключиться.

#### Заголовки и подпротоколы
```swift
var request = URLRequest(url: URL(string: "wss://api.example.com/ws")!)
request.addValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
request.addValue("graphql-ws", forHTTPHeaderField: "Sec-WebSocket-Protocol")
let task = session.webSocketTask(with: request)
```

#### Пиннинг сертификата (пример)
```swift
final class PinningDelegate: NSObject, URLSessionDelegate {
    func urlSession(_ session: URLSession, didReceive challenge: URLAuthenticationChallenge, completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        guard challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
              let serverTrust = challenge.protectionSpace.serverTrust,
              let serverCert = SecTrustGetCertificateAtIndex(serverTrust, 0),
              let pinnedCertData = try? Data(contentsOf: Bundle.main.url(forResource: "server", withExtension: "cer")!)
        else { return completionHandler(.cancelAuthenticationChallenge, nil) }

        let serverData = SecCertificateCopyData(serverCert) as Data
        if serverData == pinnedCertData {
            completionHandler(.useCredential, URLCredential(trust: serverTrust))
        } else {
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
}
```

Примечание: пиннинг требует ротации сертификата и сопровождения. Рассмотрите пиннинг по публичному ключу.

---

### Форматы сообщений и кейсы
- Текст/JSON сообщения, бинарные (Protobuf/MessagePack) для компактности.
- Кейсы: чат, котировки, presence, коллаборация, график/маркет-лента, telemetry.
 - Дедупликация/идемпотентность: используйте `messageId`/`sequence` и ack'и, чтобы восстанавливаться после реконнектов.

#### Разбор кейсов
- Чат:
  - Подписка на комнату, система ack/идемпотентность, отправка `typing` событий, presence.
  - Стоит хранить локальную очередь исходящих сообщений до подтверждения.
- Котировки/маркеты:
  - Высокая частота обновлений — следить за backpressure и batch-обновления UI.
  - Использовать бинарный формат для экономии трафика.
- Коллаборация/курсор-шеринг:
  - Секвенирование событий и конфликт-резолюция (CRDT/OT) — зафиксировать порядок на сервере.
- Телеметрия/игры:
  - Частые пинги и аггрегация событий перед отправкой (throttle/debounce).

#### Примеры payload'ов
Чат (JSON):
```json
{ "type": "message", "roomId": "abc", "text": "Привет", "ts": 1734001112 }
```

Котировки (JSON stream):
```json
{ "type": "tick", "symbol": "AAPL", "bid": 224.12, "ask": 224.16, "ts": 1734001112 }
```

Presence:
```json
{ "type": "presence", "userId": "u1", "status": "online" }
```

GraphQL Subscriptions (graphql-ws):
```json
{ "type": "connection_init", "payload": { "authToken": "..." } }
```

---

### Тестирование, отладка и наблюдаемость
- Инструменты: локальный echo-сервер, `wscat`, Charles/Proxyman с TLS, логирование.
- Метрики: количество реконнектов, средний RTT по ping, размер очереди отправки, доля ошибок.

#### Быстрая проверка с echo-сервером
```bash
wscat -c wss://echo.websocket.events
```

#### Логирование и метрики
- Логируйте открытия/закрытия, коды закрытия, RTT ping, ошибки `send/receive`.
- Экспортируйте в аналитику: `reconnect_attempts`, `queue_depth`, `bytes_in/out`.

#### Интеграционные тесты
- Поднимите локальный WS (например, `websocketd`, Node `ws`), прогоните сценарии: открытие, приём/отправка, закрытие, реконнект.
- Фуззинг входящих: длинные сообщения, бинарные, неожиданные типы.
- Тесты на таймаут heartbeat.

#### Траблшутинг
- Проверьте ATS/сертификаты при проблемах с `wss://`.
- Смотрите коды закрытия: `1006` часто о сетевых разрывах/NAT.
- На медленных сетях уменьшайте частоту ping и размер сообщений.

---

### Вопросы для собеседования и чеклист
- Разница WebSocket vs SSE vs long-polling.
- Как построить receive loop и зачем он нужен.
- Реконнект-стратегии и ограничения iOS в фоне.
- Как реализовать heartbeat и что делать при таймауте.
- Как делать пиннинг и авторизацию для `wss://`.

#### Примерные ответы (кратко)
- `receive loop`: нужен, чтобы непрерывно слушать входящие; после каждого `receive` снова вызывать `receive`.
- Реконнект: экспоненциальный бэкофф + jitter, сброс при успехе; учитываем смену сети.
- Heartbeat: периодический `sendPing`; при таймауте считаем соединение мёртвым и реконнектимся.
- Фон: постоянный WS недопустим; корректно закрываем, при возврате — переподключаемся.
- Пиннинг: сверка сертификата/ключа в делегате; авторизация через заголовки или подпротокол.

#### Чеклист перед продом
- Устойчивый receive loop и обработка ошибок
- Реконнект с бэкоффом и реакция на смену сети
- Heartbeat с таймаутом и метриками
- Ограничение размера сообщений и backpressure для отправки
- WSS, ATS, пиннинг (при необходимости), безопасное хранение токена
- Наблюдаемость: логи и ключевые метрики

#### Дополнительные вопросы для мидла/сеньора
- Как реализовать идемпотентность при повторной доставке после реконнекта?
- Что выбрать: JSON vs бинарный формат? Как измерить экономию?
- Как проектировать протокол поверх WS: версии, ошибки, ack/накопление, компрессия?
- Как работать с GraphQL Subscriptions и перезапусками операций при реконнекте?
- Как измерять и улучшать P50/P95 latency канала?

---

### Полезные ссылки
- RFC 6455 (WebSocket Protocol)
- Apple Docs: `URLSessionWebSocketTask`
- GraphQL over WebSocket (graphql-ws)

