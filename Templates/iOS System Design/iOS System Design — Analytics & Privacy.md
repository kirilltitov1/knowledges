---
title: iOS System Design — Analytics & Privacy
type: template
topics: [ios, analytics, privacy, consent]
duration: 30-45m
---

# iOS System Design — Analytics & Privacy (шаблон)

## Кейс
Сбор событий, батчинг, оффлайн‑буфер, consent/opt‑in, приватность.

## FR
- [ ] Схема событий; очередь; batch/flush; ретраи
- [ ] Оффлайн буфер; порядковость; дедуп/идемпотентность
- [ ] Consent gate; opt‑in/out; редактируемость

## NFR
- [ ] Минимизация PII; шифрование; размер батча ≤ … KB

## API допущения
- Collector endpoint; auth/token; 2xx/4xx/5xx политика

## Архитектура
- EventQueue → Storage → Flusher → Network
- Backoff/Jitter; sessionization; sampling

## Ошибки/Edge
- Нет сети; 413 payload; schema mismatch; rate limits

## Observability
- Delivery rate; drop reasons; p95 flush

## Тесты
- Моделирование consent; оффлайн/онлайн; большие объёмы

## Talk track
- Политики privacy → очередь/батч → ошибки → метрики → тесты

## Шаблон
- Event schema: …
- Flush triggers: …

