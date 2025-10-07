---
title: iOS System Design — Client Caching & State
type: template
topics: [ios, caching, state, offline]
duration: 30-45m
---

# iOS System Design — Client Caching & State (шаблон)

## Кейс
Клиентское состояние и кеш: что держим в памяти/на диске, как инвалидируем, как работаем оффлайн.

## FR
- [ ] In‑memory cache (NSCache) + Disk cache
- [ ] State store (view model/reducer); hydration на старте
- [ ] Invalidation: TTL/LRU/ETag; manual refresh

## NFR
- [ ] Память ≤ … MB; диск ≤ … MB; recovery после crash

## Архитектура
- Repository слой; CachePolicy; Persistence (CoreData/SQLite)

## Edge cases
- Stale data; concurrent updates; eviction storms

## Observability
- Hit ratio; eviction stats; stale reads

## Тесты
- Инструментальные для eviction; восстановление после падения

## Talk track
- Какие данные/где/как долго; стратегии инвалидации; метрики

