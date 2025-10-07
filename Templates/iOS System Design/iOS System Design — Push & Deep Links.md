---
title: iOS System Design — Push & Deep Links
type: template
topics: [ios, system-design, push, deeplink, notifications]
duration: 30-45m
---

# iOS System Design — Push & Deep Links (шаблон)

## Кейс (часто задаётся)
Спрогнозировать и описать архитектуру пуш‑уведомлений и deep/Universal Links: маршрутизация в нужный экран, восстановление состояния, аналитика и безопасность.

## Границы (scope)
- Клиент iOS: обработка пушей, deeplink/Universal Links, in‑app messaging
- Backend предполагается есть (только договоримся о контрактах)

## Функциональные требования (FR)
- [ ] Получение пушей (APNs), обработка foreground/background/terminated
- [ ] Deeplink/Universal Link маршрутизация (в том числе из пуша)
- [ ] Восстановление контекста (state restoration), cold start сценарии
- [ ] Permission flow + fallback UX
- [ ] In‑app messages (опционально)

## Нефункциональные (NFR, iOS)
- [ ] Надёжность доставки (APNs не гарантирует; дубли/порядок)
- [ ] Latency до открытия нужного экрана ≤ … сек
- [ ] Privacy: минимальный payload, PII в шифре/по токену
- [ ] Версионирование схемы deeplink'ов

## API/Backend допущения
- Registration: POST device token → backend
- Push payload: тип, версия схемы, параметры маршрута, id события
- Deep link schema: app://… и https Universal Links → mapping таблица

## Архитектура клиента
- Router/Coordinator для deeplink; NotificationCenter для сигналов
- AppDelegate/SceneDelegate входные точки; централизованный LinkRouter
- Feature flags: выключать каналы уведомлений/категории

## Data Flow (iOS)
1) Install → permission → deviceToken → backend
2) Push → didReceive → parse → route → track analytics
3) URL → application(_:openURL:) → route → preload data → show

## Ошибки и Edge cases
- Терминальное состояние, expired tokens, дубль пушей, неизвестная версия схемы
- Нет сети при открытии → кеш/плейсхолдер → ретрай

## Observability/Analytics
- Покрыть events: delivered/opened/routed; deep link success rate; latency

## Тестирование
- Unit: парсинг payload/URL; E2E: TestFlight, sandbox APNs; UI: навигация

## Talk track (30/45 мин)
- 5/8 мин: требования и схемы
- 10/15 мин: архитектура, маршрутизация, стейт
- 10/15 мин: ошибки, аналитика, безопасность
- 5/7 мин: тесты, вопросы

## Шаблон заполнения
- FR: …
- NFR: …
- Payload schema: …
- Routing map: …
- Error handling: …
- Metrics: …

