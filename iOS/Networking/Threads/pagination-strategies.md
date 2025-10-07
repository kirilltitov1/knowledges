---
title: Pagination Strategies
type: thread
topics: [Networking]
summary: Сравнение offset/limit, page, cursor (backend-driven)
status: draft
---

## Контекст
Загрузка ленты/новостей/поиска с постраничной подгрузкой.

## Идея
Выбрать стратегию пагинации с учётом серверных ограничений и UX.

## Разбор
- Offset/Limit — просто, но может давать дубли/пропуски при изменении набора данных.
- Page — стабильнее, но сложно пересчитывать при фильтрах.
- Cursor — выдаёт маркер продолжения (последний id/время). Устойчив к изменениям, сервер сложнее.

## Ссылки и примеры
- Пример клиента: [[networking-generic-api-client]]
- Антипаттерн: [[network-on-main-thread]]
