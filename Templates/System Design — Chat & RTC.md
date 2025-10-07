---
title: System Design — Chat & RTC
type: template
topics: [system-design, chat, rtc, messaging, calls]
duration: 45-60m
---

# System Design — Chat & RTC (Шаблон)

> Полезное: [[system-design-interview-framework|Фреймворк]] · [[system-design-cheat-sheet|Шпаргалка]]

---

## 0) Контекст и цели
- Мессенджинг: 1:1, групповые, каналы
- RTC: аудио/видеозвонки, конференции, screen share, запись (опц.)
- UX: presence, typing, read receipts, реакции, пуши
- Безопасность: шифрование, privacy, модерация
- KPI: delivery p95, call setup time, drop rate, DAU/MAU, retention

---

## 1) Функциональные требования (FR)
- Сообщения: текст, медиа (фото/видео/голос), вложения
- Группы/каналы, роли и права
- Presence/online статус, typing indicators
- Read/delivery receipts, message status (sent/delivered/read)
- Редактирование/удаление, пересылка, цитаты, реакции
- История и поиск
- Пуш-уведомления
- RTC: 1:1/групповые звонки, mute/video on/off, переключение камер
- RTC: signaling, join/leave, reconnection, screen sharing, запись (опц.)
- Админ/модерация, блокировки, жалобы

### Платформы
- iOS, Android (возможно Web)

---

## 2) Нефункциональные требования (NFR)
- Latency: messaging p95 ≤ 150–300ms; RTC E2E latency ≤ 200ms
- Jitter/packet loss: устойчивость, FEC/PLC (плеер)
- Масштаб: concurrent connections, peak QPS, fanout
- Delivery semantics: at-least-once, идемпотентность и дедупликация
- Consistency: eventual с упором на UX; порядок сообщений per-conversation
- Доступность: 99.9%+; деградация к push/polling
- Безопасность: TLS, опц. E2EE, управление ключами, DLP/PII
- Observability: метрики, логи, трассировка, QoE (MOS proxy)

---

## 3) Оценки и расчёты
```
Fanout read QPS ≈ MessagesPerUserPerDay × Recipients / 86400
Storage/day ≈ Messages × AvgSize + Attachments
Connection scale ≈ DAU × AvgConcurrentFraction
```

---

## 4) High-Level Design
- Client (iOS/Android) → WebSocket Gateway → Messaging Service → DB/Cache
- Push Service для offline
- Media/Attachment Storage + CDN
- RTC: Signaling Service + STUN/TURN; SFU (или MCU) кластер

### Data Flows
1) Send message → WS GW → Messaging → persist → fanout (queues) → deliver/notify
2) Call setup → signaling (offer/answer/ICE) → SFU media path

---

## 5) Data Model (черновик)
```
User { id, name, avatar, … }
Conversation { id, type, members[], createdAt, … }
Message { id, convId, senderId, ts, kind, content, status, refs }
Attachment { id, url, type, size, checksum }
Presence { userId, state, ts }
CallSession { id, convId, members[], state, startedAt, … }
```

---

## 6) Backend / Интеграции
- WebSocket + fallback (SSE/long-polling); авторизация (JWT/OAuth)
- Идемпотентность send/ack; server-assigned messageId; client tempId
- Ordering per-conversation (sequence/lamport clock)
- Fanout через очередь; retry с backoff/jitter; dead-letter
- STUN/TURN; NAT traversal; QoS приоритеты
- Storage tiering: горячее/холодное; CDN для медиа

---

## 7) Эндпоинты (черновик)
```http
# Auth
POST /v1/auth/token

# Config
GET /v1/config?platform=ios&version={v}

# Conversations
POST /v1/conversations
GET  /v1/conversations/{id}

# Messages (HTTP)
GET  /v1/conversations/{id}/messages?cursor={c}&limit={n}

# WS events
WS  connect: Authorization: Bearer {token}
WS  send_message { tempId, convId, content }
WS  message_ack { messageId }
WS  typing { convId, state }
WS  presence { state }

# RTC signaling
WS  call_offer/answer/ice { sessionId, sdp/candidate }
POST /v1/call/{id}/recording/start
```

---

## 8) Mobile (iOS)
- Min iOS 15, SwiftUI (+UIKit при необходимости), MVVM/TCA, DI
- WebSocket управление жизненным циклом, reconnect, backoff, heartbeat
- Локальная очередь исходящих, идемпотентность, дедуп по tempId/messageId
- Хранение сообщений: CoreData/Realm; пагинация, prefetch, индексирование
- PushKit/UNUserNotificationCenter; CallKit для RTC
- Медиа: background upload/download, прогресс, кэш NSCache+disk
- Security: Keychain, TLS pinning (опц.), безопасные логи

---

## 9) SLI/SLO и бюджет ошибок
- Delivery success p99 ≥ …%; delivery latency p95 ≤ … ms
- Call setup time p95 ≤ … s; drop rate ≤ …%
- WebSocket connect success ≥ …%; reconnect within … s
- Error budget: …; политика деградации (fallback → push)

---

## 10) Observability
- Метрики: отправлено/доставлено/прочитано, задержки ack, подключений WS
- RTC QoE: rebuffer, jitter, bitrate, packet loss
- Логи: структурированные события; трассировка цепочек (correlation-id)

---

## 11) Риски и меры
- Сетевые сбои/потери пакетoв → retry, FEC, offline
- Порядок/дубликаты → sequence, идемпотентность, дедуп, CRDT (опц.)
- Масштаб WS → шардинг по userId, sticky sessions, autoscaling


