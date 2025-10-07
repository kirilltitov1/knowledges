---
title: System Design — Social Feed
type: template
topics: [system-design, social, feed, timeline, ranking]
duration: 45-60m
---

# System Design — Social Feed (Шаблон)

> Полезное: [[system-design-interview-framework|Фреймворк]] · [[system-design-cheat-sheet|Шпаргалка]]

---

## 0) Контекст и цели
- Лента: быстрая загрузка, актуальность/персонализация, интерактив
- Контент: посты (текст/фото/видео), лайки, комментарии, репосты
- KPI: time-to-first-feed, engagement, freshness, CTR

---

## 1) Функциональные требования (FR)
- Постинг: создание/редактирование/удаление; медиа-обработка; CDN
- Лента: домашняя, профильная, хэштеги; пагинация, бесконечный скролл
- Взаимодействия: лайки, комментарии, репосты, сохранения
- Подписки/подписчики, блокировки, жалобы, модерация
- Уведомления (push, inbox)
- Поиск/дискавери, рекомендации

---

## 2) Нефункциональные требования (NFR)
- Freshness: новые посты видны за … секунд
- Latency: p95 загрузки ленты ≤ … ms
- Scale: фан-аут/фан-ин, горячие авторы, пики
- Consistency: eventual; дедуп; порядок в пределах ленты/пользователя
- Доступность: 99.9%+; деградация (кеш, старые данные)
- Безопасность/Anti-abuse: rate limits, spam detection

---

## 3) Оценки и расчёты
```
Fanout writes ≈ PostsPerUser × Followers
Feed read QPS ≈ DAU × ViewsPerUser / 86400
Storage: media on CDN; metadata in DB
```

---

## 4) High-Level Design
- Posting Service → Media Processing → CDN
- Social Graph (follow), Feed Service (push/pull/hybrid), Ranking
- Cache (Redis), DB (primary + replicas), Search/Index
- Notifications

### Data Flows
1) Post: user → upload media → process → store → update indexes → fanout
2) Feed read: request → cache/read models → ranking → page/paginate

---

## 5) Data Model (черновик)
```
User { id, … }
Post { id, userId, media[], text, ts, stats }
Follow { followerId, followeeId, ts }
Like { userId, postId, ts }
Comment { id, postId, userId, text, ts }
FeedItem { userId, postId, score, ts }
```

---

## 6) Backend / Интеграции
- Fanout-on-write vs fanout-on-read vs hybrid; hot author handling
- Ranking: chrono / engagement / ML (features, offline/online)
- Кеширование: per-user feed, invalidation; write amplification
- Пагинация: cursor; дедуп между вкладками
- Безопасность: модерация, abuse, теневая блокировка

---

## 7) Эндпоинты (черновик)
```http
# Posting
POST /v1/posts { text, media[] }
GET  /v1/posts/{id}

# Feed
GET /v1/feed/home?cursor={c}&limit={n}
GET /v1/feed/user/{id}?cursor={c}&limit={n}

# Interactions
POST /v1/posts/{id}/like
POST /v1/posts/{id}/comment { text }
```

---

## 8) Mobile (iOS)
- SwiftUI; список с prefetch; image caching; progressive images; video autoplay
- Pagination: cursor; error states; pull-to-refresh; skeletons
- Upload: background, прогресс, ретраи; сжатие медиа; EXIF/privacy
- Feature flags: эксперименты по ранжированию/форматам

---

## 9) SLI/SLO
- Time-to-first-feed p95 ≤ … ms; feed error rate ≤ …%
- Post publish latency ≤ … s; interaction latency p95 ≤ … ms
- Freshness target ≤ … s

---

## 10) Observability
- Метрики: cache hit, p95, 5xx, посты/мин, fanout queue lag
- Логи: события ранжирования (фичи/скор); трассировка запросов

---

## 11) Риски и меры
- Hot keys/Authors → шардирование, rate limit, write coalescing
- Feed staleness → инкрементальные обновления, invalidation, push hints


