---
type: "thread"
status: "draft"
summary: ""
title: "Background Modes"
---

# Background Modes


### Background Tasks
- Background fetch
- Background processing
- URLSession background tasks

### Background Modes в Info.plist
- Audio, AirPlay, Picture in Picture
- Location updates
- Voice over IP
- External accessory communication
- Bluetooth LE accessories
- Background fetch
- Remote notifications

### BGTaskScheduler (iOS 13+)
- BGAppRefreshTask
- BGProcessingTask
- Task registration
- Task scheduling

### См. также
- `iOS/Topics/push-notifications.md`


## Практика: BGTaskScheduler (iOS 13+)

### Регистрация задач (AppDelegate)

```swift
import BackgroundTasks

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    private let refreshId = "com.example.app.refresh"
    private let processingId = "com.example.app.processing"

    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        BGTaskScheduler.shared.register(forTaskWithIdentifier: refreshId, using: nil) { task in
            self.handleAppRefresh(task: task as! BGAppRefreshTask)
        }

        BGTaskScheduler.shared.register(forTaskWithIdentifier: processingId, using: nil) { task in
            self.handleProcessing(task: task as! BGProcessingTask)
        }

        // Важно: идентификаторы должны быть в Info.plist → BGTaskSchedulerPermittedIdentifiers
        scheduleAppRefresh()
        scheduleProcessing()
        return true
    }

    func applicationDidEnterBackground(_ application: UIApplication) {
        // Рескейджим при уходе в фон, чтобы задача не потерялась
        scheduleAppRefresh()
        scheduleProcessing()
    }
}
```

### Планирование

```swift
func scheduleAppRefresh() {
    let req = BGAppRefreshTaskRequest(identifier: refreshId)
    req.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60) // не гарантия, а пожелание
    do { try BGTaskScheduler.shared.submit(req) } catch { print("BG submit refresh error: \(error)") }
}

func scheduleProcessing() {
    let req = BGProcessingTaskRequest(identifier: processingId)
    req.requiresNetworkConnectivity = true
    req.requiresExternalPower = false
    do { try BGTaskScheduler.shared.submit(req) } catch { print("BG submit processing error: \(error)") }
}
```

### Обработка

```swift
func handleAppRefresh(task: BGAppRefreshTask) {
    // Всегда рескейджим сразу, чтобы задачи повторялись
    scheduleAppRefresh()

    let queue = OperationQueue()
    task.expirationHandler = { queue.cancelAllOperations() }

    let op = SyncOperation() // Ваша короткая синхронизация (должна быстро завершаться)
    op.completionBlock = { task.setTaskCompleted(success: !op.isCancelled) }
    queue.addOperation(op)
}

func handleProcessing(task: BGProcessingTask) {
    scheduleProcessing()

    let queue = OperationQueue()
    queue.maxConcurrentOperationCount = 1
    task.expirationHandler = { queue.cancelAllOperations() }

    let heavyOp = ReindexOperation() // Пример: долгий пересчёт, загрузка/выгрузка
    heavyOp.completionBlock = { task.setTaskCompleted(success: !heavyOp.isCancelled) }
    queue.addOperation(heavyOp)
}
```

> Рекомендации: минимизируйте работу в `AppRefresh`; тяжёлое переносите в `Processing` или `URLSession` background. Делайте работу идемпотентной и прерываемой.


## Практика: Background URLSession

### Конфигурация и запуск задач

```swift
final class BackgroundTransferService: NSObject {
    static let shared = BackgroundTransferService()

    private let identifier = "com.example.app.bg"
    private lazy var session: URLSession = {
        let config = URLSessionConfiguration.background(withIdentifier: identifier)
        config.isDiscretionary = true // система оптимизирует по энергии/сети
        config.sessionSendsLaunchEvents = true
        config.waitsForConnectivity = true
        return URLSession(configuration: config, delegate: self, delegateQueue: nil)
    }()

    func download(_ url: URL) {
        session.downloadTask(with: url).resume()
    }
}

extension BackgroundTransferService: URLSessionDownloadDelegate, URLSessionTaskDelegate {
    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask, didFinishDownloadingTo location: URL) {
        // Переместить файл, обновить состояние
    }

    func urlSession(_ session: URLSession, task: URLSessionTask, didCompleteWithError error: Error?) {
        // Завершение задачи/ошибка
    }

    func urlSessionDidFinishEvents(forBackgroundURLSession session: URLSession) {
        // Сообщить системе, что все события обработаны
        BackgroundURLSessionCoordinator.shared.callCompletionHandlerIfReady(for: session.configuration.identifier)
    }
}
```

### AppDelegate: пробуждение для фоновой сессии

```swift
final class BackgroundURLSessionCoordinator {
    static let shared = BackgroundURLSessionCoordinator()
    private var handlers: [String: () -> Void] = [:]

    func storeCompletionHandler(_ handler: @escaping () -> Void, for identifier: String) {
        handlers[identifier] = handler
    }

    func callCompletionHandlerIfReady(for identifier: String?) {
        guard let id = identifier, let handler = handlers[id] else { return }
        handlers[id] = nil
        handler()
    }
}

// AppDelegate
func application(_ application: UIApplication,
                 handleEventsForBackgroundURLSession identifier: String,
                 completionHandler: @escaping () -> Void) {
    BackgroundURLSessionCoordinator.shared.storeCompletionHandler(completionHandler, for: identifier)
    // Важно: воссоздайте сессию с тем же identifier, чтобы делегаты продолжили приходить
    _ = BackgroundTransferService.shared
}
```

> Важно: держите strong‑reference на сервис/делегат, иначе делегатские вызовы потеряются.


## Практика: Silent Push (content-available)

Требования: включить Background Modes → Remote notifications, настроить APNs и отправлять `apns-push-type: background`, `apns-priority: 5`. См. `iOS/Topics/push-notifications.md`.

```swift
// AppDelegate
func application(_ application: UIApplication,
                 didReceiveRemoteNotification userInfo: [AnyHashable : Any],
                 fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void) {
    // Быстрый инкрементальный синк (≤ десятков секунд)
    Task {
        do {
            let hadChanges = try await SyncService.shared.performIncrementalSync()
            completionHandler(hadChanges ? .newData : .noData)
        } catch {
            completionHandler(.failed)
        }
    }
}
```

> Для тяжёлого — ставьте задачи в `URLSession` background и сразу вызывайте `completionHandler`.


## Практика: Короткое завершение при уходе в фон

```swift
var bgId: UIBackgroundTaskIdentifier = .invalid

func sceneDidEnterBackground(_ scene: UIScene) {
    bgId = UIApplication.shared.beginBackgroundTask(withName: "flush") {
        UIApplication.shared.endBackgroundTask(bgId)
        bgId = .invalid
    }

    // Сохранить состояние/сбросить буферы/завершить транзакции (быстро)

    UIApplication.shared.endBackgroundTask(bgId)
    bgId = .invalid
}
```

> Этот механизм даёт несколько секунд на “дописать и закрыть”. Не используйте для долгих задач.


## SwiftUI: интеграция через scenePhase

```swift
@Environment(\.scenePhase) var scenePhase

var body: some View {
    ContentView()
        .onChange(of: scenePhase) { phase in
            switch phase {
            case .background:
                scheduleAppRefresh()
            case .inactive:
                break
            case .active:
                break
            @unknown default:
                break
            }
        }
}
```


## Чеклист: проект “с нуля”

- [ ] Включить только нужные Background Modes: **Remote notifications**, по необходимости **Background fetch**, **Location**, **Audio/PiP** и др.
- [ ] Добавить в Info.plist `BGTaskSchedulerPermittedIdentifiers` со всеми идентификаторами задач.
- [ ] Зарегистрировать BG‑задачи при старте; всегда рескейджить в обработчиках и при уходе в фон.
- [ ] Разделить “короткое сейчас” (refresh) и “тяжёлое в фоне” (processing/URLSession background).
- [ ] `URLSessionConfiguration.background` для длинных сетевых операций; держать живой делегат; обрабатывать `handleEventsForBackgroundURLSession`.
- [ ] Настроить silent push на бэкенде (payload/headers) и включить Remote notifications.
- [ ] Сделать синхронизацию идемпотентной и прерываемой; добавить дедупликацию.
- [ ] Учесть Low Power Mode/Background App Refresh/сеть/зарядку при планировании.
- [ ] Логгирование (oslog), метрики, алерты на фейлы фоновых задач.


## Траблшутинг

- **BGTask не запускается**: проверь `BGTaskSchedulerPermittedIdentifiers`, bundle id, идентификаторы совпадают, задача рескейджится в обработчике.
- **Silent push не приходит**: проверь capability, токен/окружение, заголовки APNs (`apns-push-type: background`, приоритет 5), нет ли троттлинга на бэке.
- **URLSession фоновые делегаты не приходят**: убедись в strong‑reference на делегат, реализован `handleEventsForBackgroundURLSession`, совпадает identifier.
- **Работа прерывается**: используй `expirationHandler`, делайте операции атомарными и короткими, сохраняйте прогресс.
- **Потребление энергии**: `isDiscretionary`, бэтчинг, уменьшение частоты задач, backoff.


## Вопросы на собеседовании

- Разница между Active/Inactive/Background/Suspended и что можно делать в каждом.
- Когда выбирать `BGAppRefreshTask` vs `BGProcessingTask` vs `URLSession` background vs silent push.
- Как устроен цикл жизни background URLSession и роль `handleEventsForBackgroundURLSession`.
- Ограничения и политика iOS по времени/энергии и троттлингу silent push.
- Идемпотентность, дедупликация и стратегии ретраев.

