---
title: iOS System Design — Pagination (Generic Lists)
type: template
topics: [ios, pagination, lists, offline]
duration: 30-45m
---

# iOS System Design — Pagination (Generic Lists) (шаблон)

## Кейс
Любой список с пагинацией и базовым кешированием.

## FR
- [ ] Cursor‑based pagination; pull‑to‑refresh; prefetch
- [ ] Local cache; offline read; invalidation

## NFR
- [ ] Smooth scroll; p95 page fetch ≤ … ms

## Архитектура
- Repository (network+cache); ViewModel state machine
- Error handling: partial, retry with backoff

## Data Flow
1) Initial → cache → page 1
2) Scroll → prefetch → merge

## Тесты/Метрики
- UI scroll tests; cache hit; p95 fetch; error rate

## Talk track
- Cursor vs offset; merge‑политики; offline; метрики

