---
title: Cursor-based Pagination
type: thread
topics:
  - Networking
summary: Курсорная пагинация (backend-driven, маркер продолжения)
status: draft
subtopic: Pagination
---

## Контекст
Стабильная подгрузка ленты при изменяющихся данных.

## Идея
Сервер возвращает marker/next_cursor; клиент шлёт его в следующем запросе.

## Плюсы
- Нет дублей/пропусков при вставках/удалениях
- Хорошо ложится на сортировку по времени/id

## Минусы
- Сложнее на бэке (хранить маркеры)
- Нельзя перескочить на произвольную страницу

## Примеры
- [[iOS/Examples/networking-generic-api-client]]
