---
title: iOS System Design — Photo Library (In-App)
type: template
topics: [ios, photos, library, permissions]
duration: 30-45m
---

# iOS System Design — Photo Library (In-App) (шаблон)

## Кейс
Встроенная медиатека: импорт/просмотр/управление фото/видео внутри приложения.

## FR
- [ ] Доступ к фотоплёнке (limited access), импорт в sandbox
- [ ] Грид/альбомы, фильтры, сортировки
- [ ] Редактирование (опц.), удаление/восстановление

## NFR
- [ ] Производительность грид‑вью; кэш превью; память
- [ ] Privacy: минимум прав; обработка limited/denied

## Архитектура
- Photos.framework; PHCachingImageManager; локальный индекс
- Disk cache для превью; background fetch изменений

## Edge cases
- Permission changes; iCloud assets; большие видео

## Observability
- Время построения грида; cache hit; ошибки разрешений

## Тесты
- Пермишены; большие библиотеки; память/скролл

## Talk track
- Permission model → кэш превью → индекс/поиск → ошибки → тесты

