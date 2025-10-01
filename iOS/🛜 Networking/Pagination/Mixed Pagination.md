---
title: Mixed Pagination (Hybrid)
type: thread
topics:
  - Networking
summary: Гибридная пагинация (page на UI, cursor под капотом)
status: draft
subtopic: Pagination
---

## Контекст
Нужно UX как со страницами, но стабильность курсора.

## Идея
Интерфейс оперирует страницами, но хранится курсор, отображаются relative pages.

## Плюсы
- UX ожидаемый
- Стабильная загрузка

## Минусы
- Реализация сложнее
- Надо тщательно логировать и тестировать
