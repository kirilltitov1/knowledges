---
title: Deep Linking
type: thread
topics: [App Lifecycle & Scenes]
subtopic: deep-linking
status: draft
---

# Deep Linking


### URL Schemes
Что это: собственные схемы `myapp://...` для открытия приложения из внешних источников (браузер, другие приложения) и для навигации внутри приложения.

Шаги настройки (с нуля):
- Добавьте схему в `Info.plist` → `CFBundleURLTypes`.

```xml
<key>CFBundleURLTypes</key>
<array>
  <dict>
    <key>CFBundleURLName</key>
    <string>com.example.myapp</string>
    <key>CFBundleURLSchemes</key>
    <array>
      <string>myapp</string>
    </array>
  </dict>
  <!-- при необходимости можно объявить несколько схем -->
  <!-- <dict> ... </dict> -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
  <!-- ... -->
</array>
```

Обработка входящих URL:
- UIKit (iOS 13+ через Scene):

```swift
func scene(_ scene: UIScene, openURLContexts contexts: Set<UIOpenURLContext>) {
    guard let url = contexts.first?.url else { return }
    _ = DeepLinkRouter.shared.handle(url)
}
```

- UIKit (до iOS 13 или как фоллбэк):

```swift
func application(_ app: UIApplication,
                 open url: URL,
                 options: [UIApplication.OpenURLOptionsKey : Any] = [:]) -> Bool {
    DeepLinkRouter.shared.handle(url)
}
```

- SwiftUI:

```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            RootView()
                .onOpenURL { url in
                    _ = DeepLinkRouter.shared.handle(url)
                }
        }
    }
}
```

Роутинг (единая точка входа):
- Используйте единый `DeepLinkRouter` для парсинга `URL` → доменная модель deeplink → навигация.

```swift
enum DeepLink {
    case product(id: String)
    case orders
    case unknown
}

final class DeepLinkRouter {
    static let shared = DeepLinkRouter()

    func handle(_ url: URL) -> Bool {
        guard let link = parse(url) else { return false }
        navigate(to: link)
        return true
    }

    private func parse(_ url: URL) -> DeepLink? {
        guard url.scheme == "myapp" else { return nil }
        let components = URLComponents(url: url, resolvingAgainstBaseURL: false)
        switch url.host {
        case "product":
            let id = components?.queryItems?.first(where: { $0.name == "id" })?.value
            return id.map { .product(id: $0) } ?? .unknown
        case "orders":
            return .orders
        default:
            return .unknown
        }
    }

    private func navigate(to link: DeepLink) {
        switch link {
        case .product(let id):
            // открыть экран товара
            break
        case .orders:
            // открыть список заказов
            break
        case .unknown:
            // показать ошибку/ничего не делать
            break
        }
    }
}
```

Внутренние deeplink-и (из приложения):
- Унифицируйте навигацию: либо всегда вызывайте `DeepLinkRouter.navigate`, либо формируйте URL и используйте `UIApplication.shared.open(_:)` (полезно для тестирования и для единого контракта).

```swift
var components = URLComponents()
components.scheme = "myapp"
components.host = "product"
components.path = "/details"
components.queryItems = [URLQueryItem(name: "id", value: "123")]
if let url = components.url {
    UIApplication.shared.open(url)
}
```

Тестирование:
- Симулятор: 

```bash
xcrun simctl openurl booted "myapp://product/details?id=123"
```

- Из Safari: введите `myapp://...`.

Практические советы:
- Валидируйте входящие URL (схема, хост, параметры) и игнорируйте неизвестные.
- Избегайте логики в парсере; парсер должен только извлекать параметры. Логику — в роутере.
- Для совместимости используйте один роутер и для URL Schemes, и для Universal Links.

### Universal Links
Что это: открытие приложения по HTTPS-ссылкам вида `https://example.com/...`. При установленном приложении — сразу открывается приложение; иначе — сайт.

Требования и настройка (с нуля):
- Associated Domains ( entitlement в проекте): добавьте домены в формате `applinks:example.com`.

```xml
<key>com.apple.developer.associated-domains</key>
<array>
  <string>applinks:example.com</string>
  <!-- при необходимости: applinks:sub.example.com -->
  <!-- для тестовых окружений можно добавить отдельные домены -->
</array>
```

- Файл `apple-app-site-association` (AASA) на домене: `https://example.com/.well-known/apple-app-site-association`
  - Без расширения, `Content-Type: application/json`, доступен по HTTPS.

```json
{
  "applinks": {
    "details": [
      {
        "appIDs": ["ABCDE12345.com.example.myapp"],
        "components": [
          { "/": "/product/*", "comment": "Product pages" },
          { "/": "/orders/*" }
        ]
      }
    ]
  }
}
```

Обработка в приложении:
- UIKit (Scene):

```swift
func scene(_ scene: UIScene, continue userActivity: NSUserActivity) {
    guard userActivity.activityType == NSUserActivityTypeBrowsingWeb,
          let url = userActivity.webpageURL else { return }
    _ = DeepLinkRouter.shared.handle(url)
}
```

- UIKit (AppDelegate):

```swift
func application(_ application: UIApplication,
                 continue userActivity: NSUserActivity,
                 restorationHandler: @escaping ([UIUserActivityRestoring]?) -> Void) -> Bool {
    if userActivity.activityType == NSUserActivityTypeBrowsingWeb,
       let url = userActivity.webpageURL {
        return DeepLinkRouter.shared.handle(url)
    }
    return false
}
```

- SwiftUI:

```swift
.onContinueUserActivity(NSUserActivityTypeBrowsingWeb) { activity in
    if let url = activity.webpageURL {
        _ = DeepLinkRouter.shared.handle(url)
    }
}
```

Рекомендации и нюансы:
- Первая попытка из Safari может показать баннер «Открыть в приложении». После согласия система будет открывать сразу приложение.
- Ссылки должны соответствовать AASA (пути/компоненты), иначе откроется Safari.
- Унифицируйте парсинг: используйте тот же `DeepLinkRouter` — он должен уметь принимать и `https://` URL.
- Тестируйте AASA: проверьте выдачу файла по адресу, корректный `Content-Type`, и домен в списке Associated Domains.
- Отладка: используйте `Console.app` (фильтр по `swcd`/`LinkPresentation`), переустановка приложения и очистка «Доверия» могут повлиять на поведение UL.

### App Clips (iOS 14+)
- App Clip Card
- Invocation URLs
- Size limitations

