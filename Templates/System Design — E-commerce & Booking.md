---
title: System Design — E-commerce & Booking
type: template
topics: [system-design, ecommerce, booking, checkout, payments]
duration: 45-60m
---

# System Design — E-commerce & Booking (Шаблон)

> Полезное: [[system-design-interview-framework|Фреймворк]] · [[system-design-cheat-sheet|Шпаргалка]]

---

## 0) Контекст и цели
- Каталог/поиск, карточка товара, корзина, оформление заказа
- Инвентарь/доступность, ценообразование, промо, доставка/слоты, трекинг
- Бронирование/резервы: удержание, подтверждение/оплата, отмена/возврат
- KPI: checkout success, latency, конверсия, AOV, возвраты

---

## 1) Функциональные требования (FR)
- Каталог: категории, фильтры, сортировки, рекомендации
- Поиск: подсказки, опечатки, синонимы
- Карточка: варианты, отзывы/рейтинги, похожие товары
- Корзина: добавление/удаление/кол-во, купоны
- Checkout: адрес/доставка/оплата (Apple Pay), валидация
- Заказы: создание, статус, отмена/возврат
- Бронирование: проверка доступности, hold, оплата, подтверждение
- Акции/промо/динамические цены

### Платформы
- iOS/Android; веб (опц.)

---

## 2) Нефункциональные требования (NFR)
- Скорость: p95/p99 на карточке/поиске/checkout
- Доступность: 99.9%+; деградация (read-only каталог, кеш)
- Консистентность: избегать oversell, стратегия резервирования
- Идемпотентность: все write (orders/payments), защита от дублей
- Масштаб: пики (праздники), очереди на оплату/обработку
- Безопасность: PCI DSS, токенизация, 3DS, защита PII
- Feature flags/A-B тесты

---

## 3) Оценки и расчёты
```
Search QPS ≈ MAU × AvgSearchesPerUser / 86400
Checkout TPS_peak ≈ PeakUsers × ConvRate × StepsPerSec
Inventory hold TTL and capacity sizing
```

---

## 4) High-Level Design
- Client → API GW → Catalog/Search → Pricing → Inventory → Cart → Checkout → Orders
- Payments Gateway (токенизация, 3DS), Notifications, Recommendation
- Cache/CDN для каталога, индекс поиска (ES/Opensearch)
- Очереди для асинхронной обработки (заказы, уведомления)

### Data Flows
1) Checkout: cart → price/discount → address/delivery → pay → order create
2) Booking: availability → hold (reserve) → pay → confirm → release on timeout

---

## 5) Data Model (черновик)
```
Product { id, sku, title, attrs, price, media, rating }
Stock { sku, location, qty }
Cart { id, userId, items[], total }
Order { id, userId, items[], amount, status, paymentId }
Reservation { id, sku, qty, expiresAt, status }
Promotion { id, rule, value, period }
```

---

## 6) Backend / Интеграции
- Идемпотентность: Idempotency-Key на orders/payments
- Ретраи: конфигурация (max/backoff/jitter) с сервера
- Inventory: read-through cache, event sourcing (опц.), резервы TTL
- Пагинация: cursor для каталогов/истории заказов
- Поиск: индексация, консистентность, reindex strategy
- Оплата: webhooks, подписки событий, безопасная обработка ошибок

---

## 7) Эндпоинты (черновик)
```http
# Catalog/Search
GET /v1/catalog?cursor={c}&limit={n}&filters=…
GET /v1/products/{id}
GET /v1/search?q=…&page=…

# Cart
POST /v1/cart/items { productId, qty }
DELETE /v1/cart/items/{id}

# Availability/Booking
GET  /v1/availability?sku={sku}&qty={n}
POST /v1/reservations { sku, qty, ttl }

# Checkout/Orders
POST /v1/checkout { cartId, address, method }
POST /v1/orders { cartId, paymentToken }

# Payments
POST /v1/payments { orderId, method, token }
POST /v1/payments/webhook
```

---

## 8) Mobile (iOS)
- Min iOS 15; SwiftUI; MVVM/TCA; DI; Feature flags/A-B
- Catalog: кеш, prefetch, offline read; изображения: downsampling, кэш
- Checkout: Apple Pay, валидация форм; idempotency на сабмите
- Error UX: понятные статусы, повтор отправки, локальные очереди

---

## 9) SLI/SLO
- p95 checkout ≤ … ms; success rate ≥ …%
- Inventory accuracy ≥ …%; oversell ≤ … ppm
- Поиск p95 ≤ … ms; CTR/конверсия метрики

---

## 10) Observability
- Метрики: latency, errors, payment failures, oversell, reindex time
- Логи: структурированные; трассировка заказа end-to-end (correlation-id)

---

## 11) Риски и меры
- Пики нагрузки → масштабирование, кеш, очереди
- Отказ платёжного провайдера → fallback, ретраи, ручная обработка
- Инвентарь рассинхрон → резервы, TTL, события, reconciliation


