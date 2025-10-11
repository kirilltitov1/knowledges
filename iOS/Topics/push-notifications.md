---
title: Push Notifications in iOS — from 0 to Senior++
type: topic
topics: [push-notifications, apns, notifications, background-modes, silent-push]
status: complete
---

# Push Notifications in iOS — от 0 до Senior++

Полный практический гайд: архитектура, реализация, безопасность, продвинутая обработка, отладка, продакшн‑практики и вопросы для собеседований. От базовой теории до сложных кейсов (rich, silent, VoIP, Live Activities, критические уведомления).

## 📚 База

### Что такое APNs
- Apple Push Notification service (APNs) — брокер доставки уведомлений на устройства Apple.
- Доставляет payload → на устройство с активным токеном.
- Транспорт — HTTP/2 (или HTTP/3) с аутентификацией по Auth Key (.p8, JWT) или сертификатам.

### Типы уведомлений
- Local — планируются на устройстве (`UNUserNotificationCenter`).
- Remote — доставляются через APNs.
- Content‑available (silent push) — фоновое обновление без UI.
- Rich (mutable‑content) — медиа/динамический контент через Service Extension.
- Time Sensitive / Critical — повышенный приоритет (требуют entitlement/разрешение Apple для Critical).
- VoIP — для вызовов (современная рекомендация: обычные remote с `apns-push-type: voip` + CallKit).
- Live Activities — обновления активностей на экране блокировки/Dynamic Island.

### Классификация: «кастомные» vs «некастомные»
- Некастомные (стандартные UI): баннер/алерт/звук/бэйдж без расширений. Достаточно payload с `aps.alert`/`sound`/`badge`, категориями и действиями. Простая интеграция, минимальные риски.
- Кастомные (требуют расширений/доп. логики):
  - Rich notifications: `mutable-content: 1` + Notification Service Extension (добавляет медиа/модифицирует текст) и, при необходимости, Notification Content Extension (кастомный UI).
  - Foreground custom UX: в `willPresent` подавляете системный баннер и показываете свой in‑app баннер/ин‑апп сообщение, с трекингом и роутингом.
  - Live Activities: обновление активностей через push (`apns-push-type: liveactivity`) — кастомный UI в рамках ActivityKit.
  - Time Sensitive/Critical: не меняют UI-слой, но меняют приоритет/интеррапшн‑уровень; «critical» требует отдельного entitlement и аппрува Apple.
  - VoIP: особый канал доставки и интеграция с CallKit; UI — ваш (экран звонка) + системные элементы.

### Пользовательские разрешения
- `UNUserNotificationCenter.requestAuthorization(options: [.alert, .badge, .sound, .provisional, .timeSensitive])`
- Проектируйте «why prompt» и «soft ask» перед системным запросом.
- Управляйте категориями/темами, чтобы пользователь мог точечно включать/выключать.

## 🧰 Реализация (клиент)

### Регистрация и токены
```swift
import UserNotifications
import UIKit

final class PushRegistrationService: NSObject, UNUserNotificationCenterDelegate {
    func configureNotifications() {
        let center = UNUserNotificationCenter.current()
        center.delegate = self
        center.requestAuthorization(options: [.alert, .badge, .sound]) { granted, _ in
            guard granted else { return }
            DispatchQueue.main.async { UIApplication.shared.registerForRemoteNotifications() }
        }
    }

    // Device token
    func application(_ application: UIApplication, didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
        let token = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
        // Отправьте токен на ваш бэкенд вместе с userId/session/appVersion/build/locale/timezone
    }

    func application(_ application: UIApplication, didFailToRegisterForRemoteNotificationsWithError error: Error) {
        // Логирование и управляемые повторы
    }

    // Foreground display policy
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                                willPresent notification: UNNotification,
                                withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
        completionHandler([.banner, .sound, .badge]) // Настройте правила per-category
    }

    // Tapping/click actions
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                                didReceive response: UNNotificationResponse,
                                withCompletionHandler completion: @escaping () -> Void) {
        // Извлеките categoryIdentifier, actionIdentifier, userInfo, deeplink
        completion()
    }
}
```

### Категории и действия
```swift
let accept = UNNotificationAction(identifier: "accept", title: "Принять")
let decline = UNNotificationAction(identifier: "decline", title: "Отклонить", options: [.destructive])
let category = UNNotificationCategory(
    identifier: "MEETING_INVITE",
    actions: [accept, decline],
    intentIdentifiers: [],
    options: [.customDismissAction]
)
UNUserNotificationCenter.current().setNotificationCategories([category])
```

### Rich notifications (Notification Service Extension)
- Target: Notification Service Extension.
- В `didReceive` скачайте медиа, модифицируйте контент, добавьте вложения.
```swift
final class NotificationService: UNNotificationServiceExtension {
    override func didReceive(_ request: UNNotificationRequest, withContentHandler contentHandler: @escaping (UNNotificationContent) -> Void) {
        let best = (request.content.mutableCopy() as? UNMutableNotificationContent)!
        // Загрузка mediaURL из userInfo, добавление UNNotificationAttachment
        contentHandler(best)
    }
}
```

## 🔕 Silent push (content‑available)

### Назначение
- Фоновая синхронизация, инкрементальные апдейты, invalidation cache, обновление бэйджа.
- Не для гарантированной моментальной доставки. Механизм «opportunistic».

### Требования
- Payload: `{"aps": {"content-available": 1}}` без `alert`/`sound`.
- Capabilities: Background Modes → Remote notifications.
- Заголовки: `apns-push-type: background`, `apns-priority: 5` (экономия энергии), опционально `apns-collapse-id`.

### Ограничения iOS
- Доставка и тайминг не гарантируются; система может объединять/отбрасывать.
- Троттлинг при частых пушах без пользовательской активности.
- На Low Power Mode/выключенном Background App Refresh доставка может не происходить.
- Время исполнения в фоне ограничено (порядка десятков секунд, может быть меньше).
- Нет гарантии запуска, если приложение «глубоко выгружено» системой.

### Обработка на клиенте
```swift
// AppDelegate
func application(_ application: UIApplication,
                 didReceiveRemoteNotification userInfo: [AnyHashable : Any],
                 fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void) {
    // Распарсить userInfo, запустить быструю синхронизацию (короткая работа или URLSession background)
    syncService.performIncrementalSync { result in
        switch result {
        case .success(let hadChanges):
            completionHandler(hadChanges ? .newData : .noData)
        case .failure:
            completionHandler(.failed)
        }
    }
}
```

### Лучшие практики для silent push
- Дедупликация и идемпотентность (используйте `content-id`/`version`/`timestamp`).
- Минимизируйте payload; передавайте ключи для выборочной синхронизации.
- Не злоупотребляйте частотой; экспоненциальный backoff на бэкенде.
- Комбинируйте с `BGAppRefreshTask`/`BGProcessingTask` как fallback.
- Логируйте delivery outcomes (client beacon → backend) для калибровки стратегии.

## 🌐 Бэкенд → APNs

### Чек‑лист интеграции на сервере
- Аккаунт Apple Developer и APNs Auth Key (.p8), `teamId`, `keyId`, `bundleId`.
- Провайдер APNs поверх HTTP/2/3 с JWT‑аутентификацией; кэшируйте `bearer` токен (~20 мин TTL).
- Разделение окружений: `api.sandbox.push.apple.com` для dev/TestFlight (debug), `api.push.apple.com` для prod. Учитывайте, что device token/топик привязаны к окружению.
- Хранилище токенов устройств: mapping `userId → [deviceToken]` + метаданные (locale, tz, appVersion, lastSeen, osVersion, deviceModel), статус подписок/категорий.
- Контракты payload: минимальный `aps` + ваша схема `type/version/payload`, deeplink/route, `dedupeKey`/`eventId`.
- Заголовки: корректный `apns-topic` (bundle id/суффиксы), `apns-push-type`, `apns-priority`, `apns-expiration`, при необходимости `apns-collapse-id`/`apns-id`.
- Политики: ретраи по 5xx с экспоненциальной задержкой, идемпотентность (повтор по `apns-id`), rate limiting/шардинг.
- Очистка токенов: на `410 Unregistered`/`400 BadDeviceToken` — снимайте токен с учётки, логируйте причину.
- Наблюдаемость: корреляция `apns-id` ↔ внутренние события, метрики доставок/открытий, алерты по росту отказов.
- Безопасность: не кладите PII в payload; используйте короткие ключи, шифруйте чувствительные данные по необходимости.

### Аутентификация и окружения
- Рекомендуется Auth Key (.p8, JWT) вместо сертификатов: проще ротация, один ключ на все bundle в Team.
- Endpoint: `api.push.apple.com:443` (prod) и `api.sandbox.push.apple.com:443` (dev).

### Ключевые заголовки
- `apns-topic`: bundle id (для специальных типов бывают суффиксы).
- `apns-push-type`: `alert` | `background` | `voip` | `liveactivity` | `fileprovider` | `complication` | `location` | `mdm`.
- `apns-priority`: 10 (срочно/alert), 5 (фон/экономия).
- `apns-expiration`: unix‑время, до которого актуально.
- `apns-collapse-id`: объединение уведомлений с одинаковым id.
- `apns-id`: UUID запроса для идемпотентности/трассировки.

### Примеры payload
```json
{
  "aps": {
    "alert": { "title": "Привет", "body": "У тебя новое сообщение" },
    "badge": 5,
    "sound": "default",
    "thread-id": "chat-123",
    "target-content-id": "message"
  },
  "deeplink": "myapp://chat/123"
}
```

```json
{
  "aps": { "content-available": 1 },
  "delta": { "messagesSince": 10231 }
}
```

### Примеры отправки (curl)
```bash
# JWT должен формироваться на сервере из .p8 (teamId, keyId, bundleId)
curl -v \
  --http2 \
  --header "authorization: bearer $APNS_JWT" \
  --header "apns-topic: com.example.app" \
  --header "apns-push-type: alert" \
  --header "apns-priority: 10" \
  --data '{"aps":{"alert":{"title":"Hi","body":"Test"}}}' \
  https://api.sandbox.push.apple.com/3/device/$DEVICE_TOKEN

# Silent push
curl -v \
  --http2 \
  --header "authorization: bearer $APNS_JWT" \
  --header "apns-topic: com.example.app" \
  --header "apns-push-type: background" \
  --header "apns-priority: 5" \
  --data '{"aps":{"content-available":1},"delta":{"messagesSince":10231}}' \
  https://api.push.apple.com/3/device/$DEVICE_TOKEN
```

### Retry/Idempotency/Очистка токенов
- Храните mapping `userId → deviceTokens` с метаданными (локаль, timezone, appVersion, lastSeen).
- Идемпотентные пуши: используйте `apns-id` и собственные `dedupeKey`.
- Ретраи по 5xx, обработка 4xx: `BadDeviceToken`, `Unregistered` → чистите токен.
- Сегментация и rate limiting по пользователям/пуллам устройств.

## 🔒 Безопасность и приватность
- Не кладите PII в payload; предпочитайте server fetch по `content-id`.
- Токены устройств — чувствительные данные. Ограничьте доступ, включите ротации, исключите их из логов.
- Для E2E‑сценариев продумайте управление ключами и деградацию UX при недоступности.

## 🧪 Тестирование и отладка
- Симуляция на симуляторе: `xcrun simctl push <UDID> <bundleId> payload.json` (для remote типов).
- На устройстве: используйте Proxyman/Charles для сетевых вызовов после silent push, `os_log`/`Logger` для таймстемпов.
- Проверьте `Background Modes → Remote notifications` и включенный Background App Refresh.
- Логи APNs провайдера: коррелируйте `apns-id` и внутренние ids.

## 📲 UX/Продукт
- Показывайте «why prompt» до системного диалога.
- Экран настроек внутри приложения: категории, превью, рекомендации.
- Deep links и восстановление контекста после тапа; защищайте маршруты авторизацией.

## 🧩 Интеграция с фичами iOS
- Notification Content Extension — кастомные UI для rich.
- ActivityKit/Live Activities — `apns-push-type: liveactivity`, `relevance-score`, `stale-date`.
- Interruption Levels: `passive`, `active`, `time-sensitive`, `critical` (последний — только с entitlement и одобрением Apple).

## 🧯 Траблшутинг (чек‑лист)
- Токен получен и отправлен на бэкенд? Окружение (sandbox/prod) совпадает?
- `apns-topic` и `apns-push-type` корректны? Для silent push — `background`, `apns-priority: 5`.
- Включены `Background Modes` и `Background App Refresh`?
- Нет ли спама silent push без ценности → система троттлит?
- Расширения (Service/Content) подписаны верно и имеют доступ к сети, если нужно?
- На устройстве не включён Low Power Mode при ожидании мгновенной доставки?

## ❓Вопросы для собеседований (Junior → Senior++)
- Жизненный цикл уведомления от провайдера до UI и обработка в приложении.
- Разница между local, remote, silent, rich, time‑sensitive, critical, VoIP, Live Activities.
- Поведение `UNUserNotificationCenterDelegate` в foreground/background.
- Архитектура хранения device tokens и их инвалидирование/привязка к пользователю.
- Idempotency/дедупликация на клиенте и сервере.
- Политика iOS по троттлингу silent push и корректные обходные стратегии.
- Безопасная обработка deeplink и навигация после тапа.
- Ограничения времени у Notification Service Extension.
- Тестирование и симуляция доставки на симуляторе/устройстве.
- Заголовки APNs: `apns-push-type`, `apns-topic`, `apns-priority`, `apns-expiration`, `apns-collapse-id` — когда и что ставить.
- Почему silent push может не прийти и что предпринять.
- Проектирование retry/backoff pipeline на сервере и очистка токенов.

## 🔗 См. также
- `iOS/App Lifecycle & Scenes/push-notifications.md`
- `iOS/App Lifecycle & Scenes/background-modes.md`


