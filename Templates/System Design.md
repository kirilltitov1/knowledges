---
title: System Design Template
type: template
topics: [system-design, interview, architecture]
duration: 45-60m
---

# System Design — Шаблон

> Полезное рядом: [[system-design-interview-framework|Фреймворк]] · [[system-design-cheat-sheet|Шпаргалка]]

---

## 0) Контекст и цели (Goals)
- Бизнес-цели: …
- Пользовательские цели: …
- KPI / North Star Metric: …
- Out of scope: …

---

## 1) Функциональные требования (FR)

### Модули (отметь релевантные)
- [ ] Топливо: карта АЗС, выбор АЗС/колонки, выбор типа топлива, оплата
- [ ] Товары: витрина, карточка товара, корзина, оплата
- [ ] Лояльность: сохранение и синхронизация карт пользователя
- [ ] Инфраструктура: instant apps, диплинки, NFC (сканирование NDEF)
- [ ] Другое: …

### Пользовательские сценарии (user flows)
1. …
2. …

### Платформы и устройства
- iOS: …
- Android: …
- Web/Backend-only: …

---

## 2) Нефункциональные требования (NFR)
- Speed-to-market: как можно быстрее / дедлайны: …
- География: одна страна / локализации: минимум
- Нагрузка: DAU/MAU: …; локальные пики (праздники/часы): …
- Производительность: p95/p99 latency: … ms; throughput: … RPS
- Доступность: uptime (SLA): …; деградация при сбоях: …
- Масштабирование: кэширование/CDN/очереди/реплики: …
- Безопасность/комплаенс: …
- Feature toggles: да/нет; A/B тесты: да/нет
- Команда: …; Дизайн: есть/нет; Backend: есть/нет; Инфра: есть/нет
- Платформы: iOS/Android …

---

## 3) Оценки и расчёты (Back-of-the-envelope)
```
QPS_read  = DailyReads  / 86400 ≈ …
QPS_write = DailyWrites / 86400 ≈ …
Storage   = DailyData × Days × Size ≈ …
Bandwidth = QPS × PayloadSize ≈ …
```

---

## 4) Сроки и план (Timeline)

| Фича/Модуль | Scope (MVP/MLP) | Оценка (чел.-дн) | Риски | Зависимости | Владелец |
| --- | --- | --- | --- | --- | --- |
| Топливо | … | … | … | … | … |
| Товары | … | … | … | … | … |
| Лояльность | … | … | … | … | … |
| Инфраструктура | … | … | … | … | … |

Примечания: timebox, критический путь, буферы.

---

## 5) Тестирование
- Команда/ресурсы: …
- Стратегия: unit, UI, интеграционные, контрактные, E2E
- Пирамида тестирования, фикстуры/тест-данные, окружения
- Автотесты: приоритеты, покрытие критичных сценариев (оплата, авторизация)

---

## 6) Дизайн (UI/UX)
- Источники и статус макетов: …
- Критерии готовности (DOR/DOD): …
- Состояния: loading/empty/error; доступность (accessibility/localization)

---

## 7) Backend / Интеграции
- Идемпотентность: ключ запроса (Idempotency-Key), идемпотентные операции
- Ретраи: политика (maxAttempts, backoff, jitter), конфигурация с сервера
- Пагинация: cursor/offset, page size лимиты
- Кэширование: TTL, cache headers, CDN для статических ресурсов
- Меню товаров: одинаковое; обновление по расписанию: ежедневно в …
- Платёжные ошибки: категории ошибок, компенсации, повторы, уведомления
- Авторизация/аутентификация: OAuth2/JWT/API Key/mTLS; скоупы
- Соглашение об ошибках: коды, структура тела, трассировка (correlation-id)

---

## 8) Эндпоинты (черновая спецификация)

```http
# Авторизация
POST /v1/auth/token
Headers: Content-Type: application/json
Body: { "grant_type": "…", "code": "…" }

# Конфигурация (ретраи/пагинация)
GET /v1/config?platform=ios&version={v}
Headers: Authorization: Bearer {token}
Response: { "retry": {"max": 3, "backoffMs": 500}, "pagination": {"pageSize": 50} }

# Список АЗС
GET /v1/stations?lat={lat}&lon={lon}&radius={r}
Headers: Authorization: Bearer {token}
Response: { "items": [ … ], "nextCursor": "…" }

# Сессия топлива (старт/авторизация)
POST /v1/fuel/sessions
Headers: Authorization: Bearer {token}, Idempotency-Key: {uuid}
Body: { "stationId": "…", "pump": "…", "fuelType": "…", "amount": … }

# Оплата
POST /v1/payments
Headers: Authorization: Bearer {token}, Idempotency-Key: {uuid}
Body: { "orderId": "…", "method": "card|apple_pay|…" }

# Каталог товаров
GET /v1/catalog?cursor={c}&limit={n}
Headers: Authorization: Bearer {token}
Response: { "items": [ … ], "nextCursor": "…" }

# Корзина
POST /v1/cart/items
Headers: Authorization: Bearer {token}
Body: { "productId": "…", "qty": 1 }

# SMS/OTP
POST /v1/otp/sms
Headers: Authorization: Bearer {token}
Body: { "phone": "+7…" }
```

---

## 9) Mobile (iOS/Android)

### Targets и стек
- iOS: min iOS 15
- UI Toolkit: преимущественно SwiftUI; UIKit для сложных кейсов/интеграции
- Архитектура: MVVM/TCA; слои: Presentation / Domain / Data; DI

### Сеть и надёжность
- Ретраи/таймауты: из /config; политики backoff/jitter; cancelation
- Идемпотентность: ключи на write-запросы; защита от дублей при повторах
- Доступность сети: reachability, оффлайн-кэш (read-only или full sync)
- TLS pinning, валидация сертификата

### Фичефлаги и A/B тесты
- Refresh: on launch + периодически; оффлайн-дефолты; аналитика exposure

### Навигация/интенты
- Диплинки/Universal Links; NFC (CoreNFC) для сканирования меток

### Наблюдаемость (observability)
- Логи (структурированные), метрики (latency, error rate), крэши, трейсинг

---

## 10) Data Model (ключевые сущности)
```
User { id, … }
Station { id, geo, services, … }
FuelSession { id, stationId, pump, fuelType, amount, status, … }
Product { id, title, price, … }
CartItem { productId, qty }
Order { id, amount, status, method, … }
```

---

## 11) High-Level Design
- Компоненты: Client (iOS/Android) → API GW/LB → App Servers → DB/Cache/CDN → MQ (если нужно)
- Data flows (2–3 сценария): …

---

## 12) Estimations (ключевые формулы)
```
QPS, Storage, Bandwidth — см. раздел 3
Оплата: peak TPS ≈ …; latency budget: … ms
```

---

## 13) Надёжность, SLI/SLO и бюджет ошибок
- SLI (успех оплаты, latency, аптайм): …
- SLO (цели по SLI): …; SLA (внешние обязательства): …
- Error budget: …; политика расхода (заморозка релизов/rollout)
- Деградация: graceful fallback, readonly режим, очереди на запись

> См. также: [[iOS/Architecture/System Design/Мини-дизайны/SLA, SLI, SLO — бюджет ошибок/SLA, SLI, SLO — бюджет ошибок]]

---

## 14) Security & Privacy
- Transport/at-rest encryption, секреты, PII/consent, журналирование доступа

---

## 15) Release/Rollout план
- Поэтапный rollout: 5% → 25% → 50% → 100%; canary; kill-switches
- План отката, совместимость версий, миграции

---

## 16) Риски и открытые вопросы
- Риски: …
- Митигирующие меры: …
- Вопросы: …


