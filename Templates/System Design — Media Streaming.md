---
title: System Design — Media Streaming
type: template
topics: [system-design, streaming, vod, live, cdn, drm]
duration: 45-60m
---

# System Design — Media Streaming (Шаблон)

> Полезное: [[system-design-interview-framework|Фреймворк]] · [[system-design-cheat-sheet|Шпаргалка]]

---

## 0) Контекст и цели
- VOD (видео по запросу) и/или Live
- Быстрый старт воспроизведения, низкая буферизация, стабильное качество
- KPI: startup time, rebuffer ratio, watch time, error rate

---

## 1) Функциональные требования (FR)
- Контент: каталог, плейлисты, поиск, рекомендации
- Плеер: HLS/DASH, ABR (адаптивный битрейт), субтитры, аудиодорожки
- DRM: FairPlay (iOS), Widevine/PlayReady (другие платформы)
- Live: задержка, DVR окно, чат (опц.)
- Аккаунт/покупки/подписки (опц.)

---

## 2) Нефункциональные требования (NFR)
- Startup time ≤ 2s (VOD), ≤ 3s (Live)
- Rebuffer ratio ≤ …%; p95 stall events ≤ …
- Масштаб: пиковые одновременные просмотры, региональное распределение
- Косты: CDN offload, транскодинг, хранение
- Надёжность: origin failover, CDN multi-provider
- Безопасность: DRM, токены доступа, signed URLs

---

## 3) Оценки и расчёты
```
CDN egress ≈ Concurrency × AvgBitrate
Storage ≈ Assets × Renditions × Duration × Bitrate
Transcoding CPU-hours ≈ Inputs × Renditions × Complexity
```

---

## 4) High-Level Design
- Ingest → Storage (origin) → Transcoding pipeline → Packager → CDN(s)
- Metadata Service, License/DRM Server, Analytics, Recommendations
- Edge auth: signed cookies/URLs

### Data Flows
1) VOD: upload → transcode (renditions) → package (HLS) → CDN → playback
2) Live: ingest (RTMP/SRT) → transcode/pack → CDN → playback

---

## 5) Data Model (черновик)
```
Asset { id, title, meta, duration }
Rendition { id, bitrate, resolution, codec }
Playlist { id, assetId, type: HLS/DASH, url }
License { id, drm, policy }
Session { id, userId, assetId, startedAt, metrics }
```

---

## 6) Backend / Интеграции
- Транскодинг: очереди, worker'ы, приоритеты, retry, idempotency
- Пакетирование: HLS (variant playlists), LL-HLS (опц.)
- CDN: multiple providers, геораспределение, кеш-правила
- DRM/лицензирование: KMS, ключи, policy, offline (опц.)
- Signed URLs/cookies, токены доступа, rate limiting

---

## 7) Эндпоинты (черновик)
```http
# Catalog
GET /v1/assets?cursor={c}&limit={n}
GET /v1/assets/{id}

# Playback
GET /v1/playback/{assetId}/manifest.m3u8
GET /v1/license?assetId={id}&drm=fairplay

# Analytics
POST /v1/analytics/playback { sessionId, event, ts, data }
```

---

## 8) Mobile (iOS)
- AVPlayer, HLS; FairPlay DRM; PiP, background playback
- Предзагрузка/кеширование мини-сегментов; ABR настройки
- UI: прогресс/буферизация; ошибки/повторы; ограничение по сети/батарее

---

## 9) SLI/SLO
- Startup time p95 ≤ … s; rebuffer ratio ≤ …%
- Fatal error rate ≤ …%; DRM license success ≥ …%
- CDN hit ratio ≥ …%

---

## 10) Observability
- Плеерные события: startup, first frame, stalls, bitrate switches
- Сервер: транскодинг тайминги, очередь задач, CDN egress, origin errors

---

## 11) Риски и меры
- Пики (релизы/премьеры) → multi-CDN, pre-warm, ABR tuning
- DRM сбои → fallback, кэш лицензий (осторожно), алерты
- Косты → оптимизация rendition ladder, storage lifecycle


