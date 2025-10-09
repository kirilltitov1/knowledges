---
title: Real-time коммуникации в iOS: WebSocket, SSE, Polling, Push и др.
type: guide
topics: [Networking]
subtopic: Real-time
status: ready
---

## Зачем нужен этот гайд

Этот материал — сжатая, но исчерпывающая шпаргалка для архитектурного собеседования на senior iOS: чем отличаются подходы к real-time коммуникациям (short/long polling, Server-Sent Events, WebSocket, gRPC-streaming, WebRTC, MQTT, APNs), когда и почему их выбирать, какие ограничения есть в iOS (foreground/background), как проектировать надежную и экономную по батарее систему, какие есть подводные камни на проде, и что обычно спрашивают на собеседованиях.

## TL;DR: Как выбирать быстро

- **Нужен двунаправленный real-time (чат, presence, коллаборация) в foreground:** WebSocket.
- **Только поток событий от сервера → клиент (тикер, лента, уведомления в Foreground):** SSE.
- **Редкие обновления, нет жестких SLA по латентности, максимальная совместимость:** (Long) Polling.
- **Стриминг RPC с низкими оверхедами, бинарные payload'ы, строгое API:** gRPC streaming (HTTP/2).
- **Аудио/видео/low-latency P2P, screen-share:** WebRTC (+ TURN/STUN), но инфраструктурно сложнее.
- **IoT/энергосбережение/посредством брокера:** MQTT (требует брокера, отлично для телеметрии).
- **Фоновая доставка событий в iOS (app в background/terminated):** APNs (remote push), для VoIP — PushKit.

Ключевое: в iOS долгоживущие соединения в фоне сильно ограничены. Для фона опирайтесь на APNs/BackgroundTasks, а «живые» сокеты — в Foreground.

## Критерии сравнения

- **Латентность:** насколько быстро событие доезжает до клиента.
- **Сетевые оверхеды:** количество установок соединений, HTTP-заголовков, keep-alive.
- **Двунаправленность:** нужна ли клиент→сервер и сервер→клиент симметрия.
- **Масштабирование серверов:** совместимость с прокси/балансерами/CDN, sticky sessions.
- **Надежность и порядок:** гарантии доставки, повторная доставka, упорядочивание.
- **Совместимость инфраструктуры:** корпоративные прокси, фаерволы, мобильные сети.
- **Поддержка в iOS:** API, жизненный цикл приложений, фоновые ограничения.
- **Энергопотребление:** удержание радиоканала, частые wake-ups, keep-alive.

## Подходы и протоколы

### Short/Long Polling

- **Short polling:** периодические GET-запросы на «есть ли обновления?». Просто, совместимо «везде», но латентность = интервал опроса; HTTP-оверхед высок.
- **Long polling:** клиент делает запрос, сервер держит его открытым до появления события/таймаута. Снижает пустые запросы, но все еще однонаправленно (сервер→клиент), масштабирование требует продуманного timeouts/holding на сервере.
- **Когда выбирать:** редкие обновления, нет жестких требований к латентности, минимальные изменения бэкенда, высокая совместимость.

### Server-Sent Events (SSE)

- Однонаправленный поток событий сервер→клиент поверх HTTP/1.1/HTTP/2. Простой текстовый формат, авто-переподключение.
- Легко проходит через прокси/фаерволы, хорошо подходит для тикеров, уведомлений в Foreground.
- Нет двунаправленности; для uplink используйте обычный HTTP.

### WebSocket (WS/WSS)

- Постоянное двунаправленное соединение поверх TCP (обычно апгрейд с HTTP/1.1). Низкая латентность, гибкость, подходит для чатов, коллаборации, presence.
- Требует продуманной серверной инфраструктуры: sticky sessions, масштабирование по соединениям, ping/pong, backpressure.
- В iOS: `URLSessionWebSocketTask` (Foreground); в Background — ограничения, сокет будет приостановлен.

### gRPC streaming (HTTP/2)

- Бинарные протобафы, эффективная сериализация, multiplexing HTTP/2, стримы client/server/bidirectional.
- Отличен для строгих контрактов, микросервисной архитектуры, низких оверхедов.
- На iOS требует сторонних библиотек и поддержки HTTP/2 на сервере.

### WebRTC

- P2P с минимальной латентностью, поддерживает аудио/видео/датаграммы (SRTP/DTLS/ICE). Для проброса NAT нужны STUN/TURN, часто необходим собственный сигнальный сервер (часто поверх WebSocket).
- Инфраструктурно сложнее, но уникален для мультимедиа и интерактивности.

### MQTT

- Легковесный брокерно-ориентированный протокол pub/sub; отличен для IoT/телеметрии/энергосбережения.
- Требует брокера (Mosquitto/EMQX/AWS IoT). На iOS — сторонние SDK.

### APNs (Push)

- Единственный надежный способ доставлять события, когда приложение не в Foreground/запущено: remote push. Для VoIP — PushKit (строже политика).
- Подходит для фона: будит приложение по событию. Не гарантирует низкую латентность секунда-в-секунду, подвержен политике доставки.

## Быстрая матрица выбора

| Сценарий | Рекомендация |
|---|---|
| Чат, presence, коллаборация (Foreground) | WebSocket (WSS), с fallback на SSE/Polling при отказах |
| Тикер цен, лента событий (Foreground, downstream only) | SSE |
| Редкие обновления, минимальные изменения бэкенда | Long Polling |
| Стримовые RPC, бинарные payload'ы | gRPC streaming |
| Голос/видео/whiteboard с низкой задержкой | WebRTC (+ сигнальный WS, STUN/TURN) |
| Фоновая доставка событий, будить приложение | APNs (Push), для VoIP — PushKit |
| IoT, телеметрия, батарея — критично | MQTT |

## Особенности iOS: жизненный цикл и фон

- **Foreground:** можно держать WebSocket/SSE; используйте ping/pong, разумные таймауты, NWPathMonitor для отслеживания сети.
- **Background:** долгоживущие соединения приостанавливаются. Для событий используйте **APNs** (remote push), **BackgroundTasks** для отложенной синхронизации. WebSocket в бэкграунде не надежен.
- **VoIP:** только через **PushKit** (строгие требования к назначению пушей).
- **Background URLSession:** хорош для долгих загрузок, но не для постоянных real-time потоков.

## Архитектурные принципы

1. **Транспортная абстракция:** изолируйте слой «MessagingTransport» от бизнес-логики; поддерживайте стратегии: WebSocket → SSE → Long Polling.
2. **Идемпотентность и порядок:** используйте `messageId`, `sequence`, server acks, дедупликацию.
3. **Надежность:** экспоненциальный backoff с джиттером, детект split-brain на сервере, ping/heartbeat.
4. **Оффлайн и кэш:** локальное хранилище для outbox/inbox, синхронизация после reconnection.
5. **Безопасность:** TLS/WSS, краткоживущие токены, токен-рефреш, certificate pinning при необходимости.
6. **Наблюдаемость:** метрики (latency p50/p95, reconnect rate, delivery lag), логи, трассировки.

## Примерные фрагменты реализации (iOS)

> Ниже — упрощенные фрагменты. Для собеса важно уметь объяснить ключевые решения и риски.

### WebSocket (URLSessionWebSocketTask)

```swift
final class WebSocketClient {
    private let url: URL
    private var task: URLSessionWebSocketTask?
    private let session: URLSession
    private var isActive = false

    init(url: URL, headers: [String: String] = [:]) {
        let config = URLSessionConfiguration.default
        config.httpAdditionalHeaders = headers
        session = URLSession(configuration: config)
        self.url = url
    }

    func connect() {
        guard !isActive else { return }
        isActive = true
        let task = session.webSocketTask(with: url)
        self.task = task
        task.resume()
        listen()
        schedulePing()
    }

    func disconnect() {
        isActive = false
        task?.cancel(with: .goingAway, reason: nil)
    }

    func send(text: String) {
        task?.send(.string(text)) { error in
            // обработать ошибку/ретраи
        }
    }

    private func listen() {
        task?.receive { [weak self] result in
            guard let self else { return }
            switch result {
            case .failure:
                self.reconnectWithBackoff()
            case .success(let message):
                // обработать .string/.data
                if self.isActive { self.listen() }
            }
        }
    }

    private func schedulePing() {
        guard isActive else { return }
        DispatchQueue.global().asyncAfter(deadline: .now() + 20) { [weak self] in
            guard let self, self.isActive else { return }
            self.task?.sendPing { _ in self.schedulePing() }
        }
    }

    private func reconnectWithBackoff() {
        guard isActive else { return }
        // backoff + jitter
        let delay = Double.random(in: 0.5...2.0)
        DispatchQueue.global().asyncAfter(deadline: .now() + delay) { [weak self] in
            self?.connect()
        }
    }
}
```

### SSE (Server-Sent Events)

```swift
final class SSEClient: NSObject, URLSessionDataDelegate {
    private let url: URL
    private lazy var session = URLSession(configuration: .default, delegate: self, delegateQueue: nil)
    private var task: URLSessionDataTask?

    init(url: URL) { self.url = url }

    func start() {
        var request = URLRequest(url: url)
        request.setValue("text/event-stream", forHTTPHeaderField: "Accept")
        task = session.dataTask(with: request)
        task?.resume()
    }

    func urlSession(_ session: URLSession, dataTask: URLSessionDataTask, didReceive data: Data) {
        // парсинг SSE-строк: event:, data:, id:
    }

    func stop() { task?.cancel() }
}
```

### Long Polling (эскиз)

```swift
final class LongPollingClient {
    private let url: URL
    private let session = URLSession(configuration: .default)
    private var eTag: String?

    init(url: URL) { self.url = url }

    func poll() {
        var req = URLRequest(url: url)
        if let eTag { req.setValue(eTag, forHTTPHeaderField: "If-None-Match") }
        session.dataTask(with: req) { [weak self] data, resp, _ in
            guard let self else { return }
            defer { self.scheduleNext() }
            if let http = resp as? HTTPURLResponse, let tag = http.allHeaderFields["ETag"] as? String {
                self.eTag = tag
            }
            // обработать data
        }.resume()
    }

    private func scheduleNext() {
        DispatchQueue.global().asyncAfter(deadline: .now() + 2) { [weak self] in self?.poll() }
    }
}
```

### Отслеживание сети

```swift
import Network

final class NetworkMonitor {
    private let monitor = NWPathMonitor()

    func start() {
        monitor.pathUpdateHandler = { path in
            // Wi-Fi/Cellular, expensive, constrained
        }
        monitor.start(queue: DispatchQueue.global(qos: .background))
    }
}
```

## Серверные аспекты и масштабирование

- **Sticky sessions:** для WS/SSE/long-poll удобно закреплять сессию за нодой (или использовать распределенный state/presence-слой).
- **Backpressure:** ограничивайте скорость отправки, буферы, используйте ack/flow control.
- **Fan-out/fan-in:** брокеры (Kafka/NATS), топики, фильтрация на BFF/edge.
- **Прокси и балансеры:** убедитесь в корректной поддержке WebSocket/SSE (upgrade, timeouts, idle, keep-alive, HTTP/2).

## Надежность доставки и порядок

- **Гарантии:** минимум «at-least-once» с идемпотентностью по `messageId`.
- **Порядок:** sequence/offset, дедупликация, reordering на клиенте.
- **Повторы:** экспоненциальный backoff с джиттером; различайте временные/перманентные ошибки.

## Энергопотребление и производительность

- Избегайте частых wake-ups; держите соединение с разумными ping-интервалами.
- Сжимайте полезную нагрузку, используйте бинарные форматы (Protobuf) при больших объемах.
- Коалесируйте мелкие сообщения, применяйте batching, где приемлемо.

## Безопасность

- WSS/TLS, минимальные наборы шифров, HSTS на веб-частях.
- Краткоживущие токены, обновление/ротATION, защита от re-use.
- Certificate pinning — где это оправдано (финтех/медицина), с планом ротации.

## Тестирование и наблюдаемость

- Эмуляция сетевых условий (потери, задержки, 2G/3G/LTE/5G).
- Мониторинг: p50/p95 latency, reconnects/min, delivery lag, server queue depth.
- Трассировки: корреляция событий клиент↔сервер (trace-id).

## Типичные вопросы на собеседовании

1. Отличия long polling/SSE/WebSocket: латентность, оверхед, двунаправленность, совместимость.
2. Что будете использовать для чата/тикера/VoIP/фоновых событий и почему?
3. Как спроектировать reconnection, backoff, idempotency, порядок сообщений?
4. Как работать в iOS с фоном, какие ограничения и обходные пути?
5. Как масштабировать WS-сервер: sticky sessions, presence-слой, брокеры, fan-out.
6. Как обеспечить безопасность (TLS, токены, pinning) и наблюдаемость?

## Чек-лист выбора

- Требуется ли двунаправленность и низкая латентность? → WebSocket/gRPC.
- Только downstream? → SSE.
- Нет жестких требований/хотим простоты? → Long Polling.
- Фоновая доставка? → APNs.
- Медиа/минимальная задержка? → WebRTC.
- IoT/энергия? → MQTT.

## Дополнительно

- HTTP/2 упрощает SSE и gRPC; HTTP/3/QUIC может улучшать латентность, но зависит от стека.
- В проде используйте единообразный формат событий (envelope) с полем версии, id, типом события.

—

Если нужно, можно расширить разделы под ваш кейс (чат, коллаб, трекинг локации) и добавить схемы/диаграммы.


