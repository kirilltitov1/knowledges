# Чат и RTC — содержание раздела

Этот раздел посвящён дизайну мессенджинга и real‑time коммуникаций: текст/медиа‑сообщения, presence/typing, push/WebSocket, а также аудио/видеозвонки (WebRTC), сигналинг, STUN/TURN, SFU/MCU и запись.

## Что сюда класть
- Архитектуры WS/SSE/long‑poll и fallback‑стратегии
- Отправка/доставка/подтверждения: tempId → messageId, ack, порядок в диалоге
- Идемпотентность, ретраи с backoff/jitter, дедупликация
- Offline/online поведение, пуш‑уведомления, CallKit (iOS)
- Мультимедиа: загрузка/кеш, прогресс, CDN
- WebRTC: сигналинг (offer/answer/ICE), TURN, реконнект, QoS
- Безопасность: TLS, опц. E2EE (управление ключами), DLP/privacy

## Быстрый старт
- Шаблон: [[Templates/System Design — Chat & RTC]]
- Примеры:
  - [[iOS/Architecture/System Design/Чат и RTC/Zoom и WebRTC — видеоконференции, TURN и STUN, запись, масштабирование SFU и MCU/Zoom и WebRTC — видеоконференции, TURN и STUN, запись, масштабирование SFU и MCU]]
  - [[iOS/Architecture/System Design/Чат и RTC/WhatsApp и Signal — E2E чат, доставки, медиасообщения, presence/WhatsApp и Signal — E2E чат, доставки, медиасообщения, presence]]

## Метрики/SLI (ориентиры)
- Delivery latency p95; delivery success
- WebSocket connect success; reconnect time
- RTC: call setup time; drop rate; jitter/packet loss

## Когда использовать
- Любые real‑time сценарии: мессенджер, лайв‑поддержка, звонки/конференции
