---
title: iOS System Design — Realtime Notifications
type: template
topics: [ios, notifications, realtime, sockets]
duration: 30-45m
---

# iOS System Design — Realtime Notifications (шаблон)

## Кейс
Реал‑тайм уведомления в приложении: пуши + in‑app обновления (WebSocket/SSE), единый роутинг и аналитика.

## FR
- [ ] APNs push: categories, actionable, silent (content‑available)
- [ ] In‑app realtime (WS/SSE) для мгновенных апдейтов
- [ ] Единый Router для событий (push/ws) → UI/state updates

## NFR
- [ ] Доставка не гарантирована → компенсировать через фоновый sync
- [ ] Latency цели для in‑app ≤ … ms

## Архитектура (iOS)
- NotificationCenter + Router; WebSocketManager; Background sync
- State store (вью‑модели/редьюсеры); диффы

## Ошибки/Edge
- Дубли/порядок, неизвестные типы событий, версия схемы

## Observability
- Delivered/opened; realtime receive latency; fallback rate

## Тесты
- Sandbox APNs; WS mock; UI маршрутизация

## Talk track
- Комбинация push + realtime; единый контракт событий; деградации

