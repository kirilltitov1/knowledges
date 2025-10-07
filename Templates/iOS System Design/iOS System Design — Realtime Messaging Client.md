---
title: iOS System Design — Realtime Messaging Client
type: template
topics: [ios, messaging, websocket, realtime]
duration: 45-60m
---

# iOS System Design — Realtime Messaging Client (шаблон)

## Кейс
Клиент мессенджера: сообщения, доставки, оффлайн, WebSocket, пуши.

## FR
- [ ] Сообщения: текст/медиа, статусы (sent/delivered/read)
- [ ] WS соединение: reconnect, heartbeat, backoff
- [ ] Оффлайн очередь исходящих, дедуп по tempId/messageId
- [ ] Пуши для offline

## NFR
- [ ] Delivery latency p95 ≤ … ms; connect success ≥ …%

## Архитектура
- WS Manager; Outbox queue; Repository; Local DB

## Протокол (пример)
- send_message { tempId, convId, content }
- message_ack { messageId, tempId }

## Edge cases
- Дубликаты, порядок, конфликт правок, большие вложения

## Observability
- Sent/delivered/read, reconnects, queue backlog

## Тесты
- WS mock; offline/online; массовые сообщения

## Talk track
- Контракт событий → outbox/идемпотентность → reconnect → метрики → тесты

