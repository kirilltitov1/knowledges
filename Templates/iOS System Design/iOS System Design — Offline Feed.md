---
title: iOS System Design — Offline Feed
type: template
topics: [ios, system-design, feed, offline, pagination]
duration: 30-45m
---

# iOS System Design — Offline Feed (шаблон)

## Кейс
Спроектировать ленту с пагинацией, кэшированием и оффлайн‑просмотром.

## Scope
- Только iOS‑клиент: UI, кэш, модель данных, синк, ошибки

## FR
- [ ] Пагинация (cursor preferred), pull‑to‑refresh, prefetch
- [ ] Кеширование на диск + память; оффлайн‑просмотр
- [ ] Инкрементальные обновления; invalidation

## NFR (iOS)
- [ ] Time‑to‑first‑feed p95 ≤ … ms; плавный скролл (без jank)
- [ ] Память под изображения; политика очистки

## API контракты (допущения)
- GET /feed?cursor=…&limit=… → items[], nextCursor
- ETags/If‑None‑Match (опц.)

## Архитектура клиента
- Repository → Cache (NSCache+disk) → Network
- ViewModel со стейтом: loading/loaded/partial/error
- Image pipeline: downsampling, приоритеты, отмена задач

## Data Flow
1) Open → read disk cache → show → fetch delta
2) Scroll → prefetch next page → merge

## Ошибки/Edge
- Повтор страницы, дубликаты, сдвиг курсора; нет сети

## Performance/Memory
- Downsampling, reuse identifiers, batch updates

## Observability
- p95 загрузки, cache hit, ошибки

## Тесты
- Snapshot/UI скролл; интеграция кеш/сеть; оффлайн сценарии

## Talk track
- 5/8 мин: FR/NFR/метрики
- 10/15 мин: архитектура, data flow
- 10/15 мин: кеш/изображения/ошибки
- 5/7 мин: тесты, вопросы

## Шаблон
- Модель: Item { … }
- Cache policy: …
- Pagination: cursor size …

