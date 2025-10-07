---
title: iOS System Design — Image Loading & Caching
type: template
topics: [ios, images, caching, performance]
duration: 30-45m
---

# iOS System Design — Image Loading & Caching (шаблон)

## Кейс
Спроектировать эффективную загрузку изображений: кеширование, приоритеты, отмена, плавный скролл.

## FR
- [ ] Memory + Disk cache (multi‑layer)
- [ ] Prefetching, приоритеты, отмена
- [ ] Progressive/thumbnail → full

## NFR
- [ ] Плавный скролл; p95 decode ≤ … ms
- [ ] Память под кеш ≤ … MB; диск ≤ … MB; политика LRU/TTL

## Архитектура
- ImageLoader → URLSession → Decoder → Cache (NSCache+Disk)
- Downsampling на background; decompress

## Ошибки
- Таймаут, повтор, placeholder, stale cache

## Observability
- Hit ratio, average decode, failures

## Тесты
- Скролл/Reuse; кеш‑хит; падение сети

## Talk track
- Требования → пайплайн → кеш‑стратегии → метрики/тесты

## Шаблон заполнения
- Cache sizes: memory … / disk …
- Downsample rules: …

