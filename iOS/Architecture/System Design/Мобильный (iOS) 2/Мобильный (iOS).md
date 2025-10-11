# Мобильный (iOS) — содержание раздела

Практики системного дизайна применительно к iOS‑клиенту: архитектура приложения, сетевой слой и надёжность, оффлайн/синхронизация, безопасность, производительность, фичефлаги и аналитика.

## Что сюда класть
- Архитектуру клиента: MVVM/VIPER/TCA; слои Presentation/Domain/Data; DI
- Навигация и интеграции: push, deep/Universal Links, in‑app messaging
- Сетевой слой: ретраи/таймауты, идемпотентность, очереди запросов, приоритеты
- Хранилища: кеш (memory/disk), CoreData/Realm/SwiftData; миграции
- Бэкграунд: загрузки/возобновление, ограничения батареи/сети
- Безопасность: Keychain, device binding, TLS pinning, jailbreak‑сигналы
- Feature flags / Remote config / A/B тесты
- Аналитика: батчинг, consent/opt‑in, приватность

## Быстрый старт
- Универсальный шаблон: [[Templates/System Design]]
- Доменные шаблоны: [[Templates/System Design — Chat & RTC]] · [[Templates/System Design — E-commerce & Booking]] · [[Templates/System Design — Media Streaming]] · [[Templates/System Design — Social Feed]]
- Плейбуки: [[Playbooks/system-design-interview-framework]] · [[Playbooks/system-design-cheat-sheet]]

## Подразделы
- [[iOS/Architecture/System Design/Мобильный (iOS)/Архитектура — push, deep link, in-app messaging/Архитектура — push, deep link, in-app messaging]]
- [[iOS/Architecture/System Design/Мобильный (iOS)/Remote-config, feature-flags и A-B/Remote-config, feature-flags и A-B]]
- [[iOS/Architecture/System Design/Мобильный (iOS)/Бэкграунд-загрузки и возобновление — идемпотентность на сервере/Бэкграунд-загрузки и возобновление — идемпотентность на сервере]]
- [[iOS/Architecture/System Design/Мобильный (iOS)/Клиентские rate limits — экспоненциальный backoff, умные очереди запросов/Клиентские rate limits — экспоненциальный backoff, умные очереди запросов]]
- [[iOS/Architecture/System Design/Мобильный (iOS)/Кэш изображений и сетевой пайплайн — memory, disk, prefetch, приоритеты/Кэш изображений и сетевой пайплайн — memory, disk, prefetch, приоритеты]]
- [[iOS/Architecture/System Design/Мобильный (iOS)/Безопасное хранилище — Keychain, device binding, jailbreak-сигналы/Безопасное хранилище — Keychain, device binding, jailbreak-сигналы]]
- [[iOS/Architecture/System Design/Мобильный (iOS)/Версионирование локальной БД и миграции/Версионирование локальной БД и миграции]]
- [[iOS/Architecture/System Design/Мобильный (iOS)/Батчинг аналитики — приватность, consent, opt-in/Батчинг аналитики — приватность, consent, opt-in]]

## Метрики/SLI (ориентиры)
- App startup time, scroll/jank, p95 сетевых запросов, error rate
- Успешность push/ deeplink переходов, доля оффлайн‑операций, crash‑free users

## Когда использовать
- Любой System Design с фокусом на клиентскую часть и iOS‑ограничения
