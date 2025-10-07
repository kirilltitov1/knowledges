---
title: iOS System Design — Background Transfers
type: template
topics: [ios, background, uploads, downloads]
duration: 30-45m
---

# iOS System Design — Background Transfers (шаблон)

## Кейс
Фоновые загрузки/выгрузки (background URLSession / BGTaskScheduler), возобновление, идемпотентность.

## FR
- [ ] Background uploads/downloads; прогресс; возобновление
- [ ] Очередь задач; приоритеты; ограничения сети/батареи
- [ ] Идемпотентность на write; retry/backoff

## NFR
- [ ] Надёжность после kill/reboot; лимиты iOS

## API допущения
- Idempotency-Key на POST/PUT; range requests на download

## Архитектура
- TransferManager (background URLSession)
- Disk staging area; checksum; resume data
- Task persistence (CoreData/SQLite)

## Ошибки/Edge
- Token refresh; сеть изменилась; quota; конфликт на сервере

## Observability
- Успешность задач, среднее время, причины отказов

## Тесты
- Симуляция kill/restore; деградации сети; большие файлы

## Talk track
- Лимиты платформы → контракт → очередь и storage → ошибки → тесты

## Шаблон
- Queue policy: …
- Retry: max … backoff …

