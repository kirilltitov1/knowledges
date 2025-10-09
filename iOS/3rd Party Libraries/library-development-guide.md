## Разработка iOS‑библиотек

Этот гайд — практический, с «боевыми» примерами кода и инфраструктуры. Он покрывает путь от создания первой библиотеки до промышленного уровня: дизайн публичного API, устойчивость к изменениям (resilience), ABI/Module Stability, упаковка в XCFramework, распространение через SPM/Pods, тестирование, CI/CD, документация DocC, наблюдаемость, безопасность и эксплуатация.

### Содержание
- **Цели и критерии качества библиотеки**
- **Архитектура и API‑дизайн** (public surface, удобство, расширяемость)
- **Resilience/Эволюция API**: `@frozen`, `@inlinable`, `@usableFromInline`, SPI
- **Совместимость**: ABI Stability, Module Stability, SemVer, депрекейты
- **Пакетирование**: SPM (исходники/бинарь), CocoaPods, XCFramework
- **Пример боевой библиотеки `AcmeNetworking` (SPM)**
- **Тестирование**: XCTest, стабы через `URLProtocol`, параллельные тесты
- **Документация**: DocC, примеры, покрытие
- **CI/CD**: сборки, тесты, артефакты, релизы, подпись
- **Наблюдаемость**: os.Logger, метрики, signposts
- **Безопасность и производительность**: keychain, pinning, память, concurrency
- **Чеклист релиза и эксплуатация**

---

## Цели и критерии качества

- **Надёжный публичный API**: минимальный, предсказуемый, документированный.
- **Стабильность**: не ломать потребителей при минорных релизах, чёткий SemVer.
- **Эффективность**: разумная производительность и работа с памятью.
- **Безопасность**: отсутствие PII в логах, безопасные дефолты, криптография без «сюрпризов».
- **Наблюдаемость**: структурные логи, метрики, фичи для диагностики.
- **Опростить поддержку**: удобная сборка/релиз, автогенерация артефактов.

---

## Архитектура и дизайн публичного API

- **Small surface area**: меньше типов/методов — легче эволюция.
- **Композиция > наследование**: протоколы, декораторы, интерцепторы.
- **Расширяемость через протоколы**: `Interceptor`, `RetryPolicy`, «точки расширения».
- **Ясные модели ошибок**: машиночитаемые коды + локализуемые описания.
- **Изоляция потоков**: чётко указанные `@MainActor`/`Sendable` границы.
- **Конфигурация без глобального состояния**: `Configuration` объект, явная передача зависимостей.

---

## Resilience, эволюция и ключевые атрибуты

### Библиотечная эволюция и стабильность

- Включайте «Build Libraries for Distribution» для Swift‑интерфейсов (`.swiftinterface`) и модульной стабильности.
- Без `@frozen` компилятор использует «resilient layout»: можно добавлять поля в типах без ABI‑лома.
- `@inlinable` раскрывает реализацию клиентам на этапе компиляции — меняйте осторожно.
- `@usableFromInline` делает internal символ доступным для inlining в public API.
- SPI (`@_spi`) — для «приватной» API между модулями (не для общедоступных потребителей).

### Пример: что делает `@frozen` и чем грозит добавление поля

`@frozen` фиксирует память и случаи перечисления (для enum) навсегда с точки зрения ABI. Это ускоряет код, но сильно ограничивает будущее развитие.

Плохой сценарий — заморозили тип, потом добавили поле: это ABI‑лом. Клиенты, собранные со старой версией, могут крашиться/получать память не того размера.

```swift
// Версия 1 (в релизе 1.0.0)
@frozen
public struct PublicConfig {
    public let baseURL: URL
    public init(baseURL: URL) { self.baseURL = baseURL }
}

// Версия 2 (попытка в 1.1.0 — так делать нельзя)
@frozen
public struct PublicConfig {
    public let baseURL: URL
    public let timeout: TimeInterval // ДОБАВЛЕНО ПОЛЕ — ABI‑BREAK!
    public init(baseURL: URL, timeout: TimeInterval) {
        self.baseURL = baseURL
        self.timeout = timeout
    }
}
```

Безопасные альтернативы:
- Не использовать `@frozen` и включить «Library Evolution» (resilient layout) — тогда добавление поля допустимо (source‑совместимость может потребовать дефолтов/перегрузок инициализаторов).
- Заложить «резерв» заранее:

```swift
@frozen
public struct PublicConfig {
    public let baseURL: URL
    // Резерв под будущие флаги/опции (часто — приватный «контейнер»)
    @usableFromInline internal var _reserved: Reserved = .init()

    @frozen
    @usableFromInline struct Reserved { /* пусто, можно расширять */ }

    public init(baseURL: URL) { self.baseURL = baseURL }
}
```

Аналогично с `@frozen enum`: добавление нового кейса — ABI‑лом. Если не замораживать enum, клиенты обязаны иметь `default` обработчик «неизвестных» кейсов.

```swift
// Без @frozen — можно добавить новые кейсы в будущем без ABI‑лома.
public enum ConnectionState { case connected, disconnected }

func handle(_ s: ConnectionState) {
    switch s {
    case .connected: break
    case .disconnected: break
    @unknown default: break // защитим будущие кейсы
    }
}
```

### Когда использовать `@inlinable` и `@usableFromInline`

- Небольшие «горячие» функции, где inlining даёт выигрыш и реализация стабильна.
- Помните: `@inlinable` «запечёт» реализацию в клиент: изменение логики — потенциально source‑совместимо, но может повлиять на поведение уже собранных клиентов.

### Когда `@frozen` безопасен: правила и чеклист

Когда безопасно замораживать типы:
- **Закрытый набор состояний/полей** гарантирован (на годы). Например, внутренние immutable value‑типы алгоритмов, протоколы шифрования с фиксированным набором параметров.
- **Вам нужна предсказуемая ABI‑форма** ради производительности/инлайнинга, и вы контролируете обновления всех клиентов (monorepo/единый релизный поезд).
- **MAJOR‑релиз**: вы готовы сознательно ломать ABI и пересобрать/мигрировать клиентов.

Чего избегать:
- Не ставьте `@frozen` на публичные модели, которые вероятно будут расширяться (конфиги, опции, флаги, error‑типы).
- Не замораживайте `enum`, если возможны новые кейсы; используйте незамороженный `enum` + `@unknown default` на стороне клиентов.

Чеклист перед `@frozen`:
- [ ] Тип точно не будет расширяться полями/кейсамив течение жизненного цикла MINOR/PATCH.
- [ ] Клиенты не зависят от бинарной подмены без пересборки (или у вас MAJOR‑релиз).
- [ ] Включён Library Evolution там, где `@frozen` не нужен, и используются resilient‑типы по умолчанию.
- [ ] Для потенциальных будущих изменений предусмотрен «резерв» (
  внутренние контейнеры/поля, версии протокола на уровне wire‑формата, и т.д.).

---

## Совместимость, SemVer и депрекейты

- **SemVer**: PATCH — багфиксы, MINOR — новые функции без ломов, MAJOR — ломы.
- **Source vs ABI**: SPM из исходников — важнее source‑совместимость; бинарные (XCFramework) — критична ABI‑совместимость.
- **Депрекейты**: помечайте `@available(*, deprecated, message: ...)`, обеспечивайте миграционный путь и сроки удаления.

---

## Пакетирование и распространение

Рекомендуемый путь — **Swift Package Manager**. Дополнительно при необходимости: **CocoaPods** и **XCFramework** для бинарной поставки.

### Минимальный `Package.swift`

```swift
// swift-tools-version: 5.10
import PackageDescription

let package = Package(
    name: "AcmeNetworking",
    platforms: [
        .iOS(.v14), .macOS(.v12)
    ],
    products: [
        .library(name: "AcmeNetworking", targets: ["AcmeNetworking"])
    ],
    targets: [
        .target(
            name: "AcmeNetworking",
            dependencies: [],
            path: "Sources/AcmeNetworking",
            resources: [.process("Resources")] // если нужны ресурсы
        ),
        .testTarget(
            name: "AcmeNetworkingTests",
            dependencies: ["AcmeNetworking"],
            path: "Tests/AcmeNetworkingTests"
        )
    ]
)
```

### Podspec для CocoaPods (опционально)

```ruby
Pod::Spec.new do |s|
  s.name         = 'AcmeNetworking'
  s.version      = '1.0.0'
  s.summary      = 'Battle-tested HTTP client with interceptors and retries.'
  s.homepage     = 'https://example.com/acme'
  s.license      = { :type => 'MIT' }
  s.author       = { 'Acme' => 'ios@acme.com' }
  s.source       = { :git => 'https://example.com/acme.git', :tag => s.version.to_s }
  s.swift_version = '5.10'
  s.ios.deployment_target = '14.0'
  s.source_files = 'Sources/AcmeNetworking/**/*.swift'
end
```

### Динамические vs статические библиотеки на iOS и доставка на устройство

На iOS приложение поставляется как один `.ipa`, в котором лежат ваши фреймворки (статические или динамические). **Системного «общего пула» пользовательских библиотек нет**: каждая аппка несёт свой набор бинарей.

- **Статические (static) фреймворки/библиотеки**: их код линкуется в основной бинарь приложения/фреймворка. Нет версионирования на устройстве отдельно от приложения — версия всегда та, что собрана в вашем `.ipa`.
- **Динамические (dynamic) фреймворки**: загружаются как отдельные бинарники из бандла приложения. Но всё равно версия поставляется вместе с приложением. Сторонние приложения не смогут «поделиться» вашей библиотекой; кросс‑приложного шэринга версий нет.
- **App Extensions/Frameworks внутри одного app bundle** могут делить один и тот же динамический фреймворк (copy‑on‑write на уровне файловой системы), но это всё в пределах одного установленного приложения.

Последствия для версий:
- Если у вас два разных приложения, одно ждёт v1.2, другое — v1.1, оба включат в свой `.ipa` свою версию фреймворка. На устройстве будут существовать две копии (по одной на приложение) — конфликтов нет.
- Обновление библиотеки для уже установленного приложения происходит только через обновление самого приложения (через App Store/MDM/TestFlight). «Подменить» бинарь библиотеки отдельно от приложения нельзя.

Что меняется из‑за `@frozen` для динамических библиотек:
- Если вы поставляете библиотеку как динамический фреймворк и хотите подменять только её без пересборки клиентов — на iOS это не стандартная модель распространения. Обычно клиенты пересобирают приложения с новой версией вашей библиотеки.
- Тем не менее, если у вас внутренняя инфраструктура и вы реально подменяете бинарь без пересборки, тогда `@frozen` важен: изменение layout замороженных типов или наборов кейсов enum приведёт к ABI‑несовместимости между старым клиентским кодом и новой либой.
- При классической схеме поставки через App Store, где клиент пересобирает своё приложение, `@frozen` рисков почти не несёт — ведь всё компилируется одним тулчейном одновременно. Риски возникают в бинарных SDK/плагинных сценариях без пересборки клиента.

### Как выбрать: статический или динамический фреймворк (решающая схема)

- **Нужен один бинарь на несколько таргетов внутри одного приложения (app + extensions)** → динамический фреймворк упростит шэринг и уменьшит размер за счёт dedup.
- **Максимально быстрый запуск/меньше динамической загрузки** → статический (меньше оверхеда на dyld, иногда меньшие cold‑start задержки).
- **Сложная структура зависимостей, плагинная архитектура** → динамический может помочь изолировать и обновлять части (внутренние кейсы), но помните: для App Store обычно пересборка всего приложения.
- **Контроль размера**: оба варианта можно тюнить. Статика иногда даёт бОльшую оптимизацию dead‑strip, динамика — дедупликацию между таргетами.
- **Требуется binary delivery для сторонних клиентов**: и статический, и динамический могут быть в XCFramework; выбор определяется интеграционной моделью клиента.

Практический совет: по умолчанию используйте статические библиотеки SPM, переключайтесь на динамическую сборку только при явной потребности (шэринг кода между extension/host, специфические загрузочные требования).

### Матрица совместимости `@frozen` vs resilient по сценариям

| Сценарий | Поставка | Требуется бинарная совместимость | `@frozen struct/enum` безопасен при добавлении поля/кейса? |
|---|---|---|---|
| SPM, исходники, клиент пересобирается | Исходники | Нет | Да (клиент пересобирается; но enum с `@frozen` всё равно не расширить без MAJOR) |
| XCFramework, клиент НЕ пересобирается | Бинарь | Да | Нет — добавление поля/кейса ломает ABI |
| Внутренний плагин, подмена только библиотеки | Бинарь | Да | Нет — риск краша/коррупции |
| App Store, клиент пересобирается с новой либой | Исходники/бинарь | Нет | Да (всё собирается вместе одним компилятором) |
| Resilient тип (без `@frozen`) | Любая | Да | Да — layout позволяет добавление полей, для enum используйте `@unknown default` |

Коротко: `@frozen` требует синхронного обновления клиента. Resilient‑типы дают свободу эволюции без ABI‑лома.

### Сборка XCFramework (бинарная поставка)

```bash
# Архивы для симулятора и девайса, затем сборка XCFramework
xcodebuild archive \
  -scheme AcmeNetworking \
  -destination "generic/platform=iOS Simulator" \
  -archivePath build/AcmeNetworking-sim \
  SKIP_INSTALL=NO BUILD_LIBRARY_FOR_DISTRIBUTION=YES

xcodebuild archive \
  -scheme AcmeNetworking \
  -destination "generic/platform=iOS" \
  -archivePath build/AcmeNetworking-ios \
  SKIP_INSTALL=NO BUILD_LIBRARY_FOR_DISTRIBUTION=YES

xcodebuild -create-xcframework \
  -framework build/AcmeNetworking-sim.xcarchive/Products/Library/Frameworks/AcmeNetworking.framework \
  -framework build/AcmeNetworking-ios.xcarchive/Products/Library/Frameworks/AcmeNetworking.framework \
  -output build/AcmeNetworking.xcframework
```

---

## Боевая библиотека: `AcmeNetworking` (SPM)

Ниже — минималистичная, но расширяемая архитектура: запросы, интерцепторы, политика ретраев, наблюдаемость. Современная конкуррентность (`async/await`).

```swift
import Foundation
import OSLog

public enum HTTPMethod: String { case GET, POST, PUT, PATCH, DELETE }

public struct Request<T: Decodable>: Sendable {
    public let path: String
    public let method: HTTPMethod
    public var headers: [String: String]
    public var query: [String: String]
    public var body: Data?

    public init(
        path: String,
        method: HTTPMethod = .GET,
        headers: [String: String] = [:],
        query: [String: String] = [:],
        body: Data? = nil
    ) {
        self.path = path
        self.method = method
        self.headers = headers
        self.query = query
        self.body = body
    }
}

public struct HTTPResponse<T: Decodable>: Sendable {
    public let value: T
    public let statusCode: Int
    public let headers: [AnyHashable: Any]
}

public protocol RequestInterceptor: Sendable {
    func adapt(_ request: URLRequest) async throws -> URLRequest
    func validate(response: URLResponse?, data: Data?) throws
}

public extension RequestInterceptor {
    func adapt(_ request: URLRequest) async throws -> URLRequest { request }
    func validate(response: URLResponse?, data: Data?) throws { /* no-op */ }
}

public protocol RetryPolicy: Sendable {
    func nextDelay(after attempt: Int, for error: Error?, response: HTTPURLResponse?) -> TimeInterval?
}

public struct ExponentialBackoffPolicy: RetryPolicy {
    public let maxRetries: Int
    public let baseDelay: TimeInterval
    public init(maxRetries: Int = 3, baseDelay: TimeInterval = 0.2) {
        self.maxRetries = maxRetries
        self.baseDelay = baseDelay
    }
    public func nextDelay(after attempt: Int, for error: Error?, response: HTTPURLResponse?) -> TimeInterval? {
        guard attempt < maxRetries else { return nil }
        // Ретраим 5xx и сетевые ошибки
        if let code = response?.statusCode, (500...599).contains(code) { return pow(2.0, Double(attempt)) * baseDelay }
        if error != nil { return pow(2.0, Double(attempt)) * baseDelay }
        return nil
    }
}

public struct HTTPClientConfiguration: Sendable {
    public var baseURL: URL
    public var session: URLSession
    public var decoder: JSONDecoder
    public var interceptors: [RequestInterceptor]
    public var retryPolicy: RetryPolicy

    public init(
        baseURL: URL,
        session: URLSession = .shared,
        decoder: JSONDecoder = JSONDecoder(),
        interceptors: [RequestInterceptor] = [],
        retryPolicy: RetryPolicy = ExponentialBackoffPolicy()
    ) {
        self.baseURL = baseURL
        self.session = session
        self.decoder = decoder
        self.interceptors = interceptors
        self.retryPolicy = retryPolicy
    }
}

public final class HTTPClient: @unchecked Sendable { // URLSession не полностью Sendable
    private let configuration: HTTPClientConfiguration
    private let logger = Logger(subsystem: "com.acme.networking", category: "http")

    public init(configuration: HTTPClientConfiguration) {
        self.configuration = configuration
    }

    public func send<T: Decodable>(_ request: Request<T>) async throws -> HTTPResponse<T> {
        var url = configuration.baseURL
        url.append(path: request.path)
        if !request.query.isEmpty {
            var comps = URLComponents(url: url, resolvingAgainstBaseURL: false)!
            comps.queryItems = request.query.map { URLQueryItem(name: $0.key, value: $0.value) }
            url = comps.url!
        }

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = request.method.rawValue
        urlRequest.httpBody = request.body
        for (k, v) in request.headers { urlRequest.setValue(v, forHTTPHeaderField: k) }

        // Adapt через цепочку интерцепторов
        for interceptor in configuration.interceptors {
            urlRequest = try await interceptor.adapt(urlRequest)
        }

        var attempt = 0
        while true {
            do {
                logger.log("➡️ Sending \(urlRequest.httpMethod ?? "") \(url.absoluteString, privacy: .public)")
                let (data, response) = try await configuration.session.data(for: urlRequest)
                guard let http = response as? HTTPURLResponse else { throw URLError(.badServerResponse) }

                for interceptor in configuration.interceptors { try interceptor.validate(response: response, data: data) }

                if (200..<300).contains(http.statusCode) {
                    let value = try configuration.decoder.decode(T.self, from: data)
                    return HTTPResponse(value: value, statusCode: http.statusCode, headers: http.allHeaderFields)
                } else {
                    throw HTTPError.statusCode(http.statusCode, data: data)
                }
            } catch {
                let http = (error as? HTTPError)?.httpResponse
                if let delay = configuration.retryPolicy.nextDelay(after: attempt, for: error, response: http) {
                    attempt += 1
                    logger.warning("Retry \(attempt) after error: \(String(describing: error), privacy: .public)")
                    try await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
                    continue
                }
                throw error
            }
        }
    }
}

public enum HTTPError: Error, CustomNSError {
    case statusCode(Int, data: Data?)

    public static var errorDomain: String { "com.acme.networking" }
    public var errorCode: Int {
        switch self { case .statusCode(let code, _): return code }
    }
    public var errorUserInfo: [String : Any] { [:] }

    var httpResponse: HTTPURLResponse? {
        switch self { case .statusCode(let code, _):
            return HTTPURLResponse(url: URL(string: "about:blank")!, statusCode: code, httpVersion: nil, headerFields: nil)
        }
    }
}
```

Расширяйте цепочку интерцепторов для аутентификации, ETag/If‑None‑Match, логирования тела (только в дев‑сборках), трейсинга.

### Тестирование через `URLProtocol` стабы

```swift
import XCTest
@testable import AcmeNetworking

final class URLProtocolStub: URLProtocol {
    static var handler: ((URLRequest) throws -> (HTTPURLResponse, Data))?
    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
    override func startLoading() {
        guard let handler = URLProtocolStub.handler else { fatalError("Handler not set") }
        do {
            let (resp, data) = try handler(request)
            client?.urlProtocol(self, didReceive: resp, cacheStoragePolicy: .notAllowed)
            client?.urlProtocol(self, didLoad: data)
            client?.urlProtocolDidFinishLoading(self)
        } catch {
            client?.urlProtocol(self, didFailWithError: error)
        }
    }
    override func stopLoading() { }
}

final class HTTPClientTests: XCTestCase {
    func test_success_decoding() async throws {
        let config = URLSessionConfiguration.ephemeral
        config.protocolClasses = [URLProtocolStub.self]
        let session = URLSession(configuration: config)
        let baseURL = URL(string: "https://example.com")!
        let client = HTTPClient(configuration: .init(baseURL: baseURL, session: session))

        struct User: Codable, Equatable { let id: Int; let name: String }

        URLProtocolStub.handler = { req in
            let data = try JSONEncoder().encode(User(id: 1, name: "Alice"))
            let resp = HTTPURLResponse(url: req.url!, statusCode: 200, httpVersion: nil, headerFields: nil)!
            return (resp, data)
        }

        let response: HTTPResponse<User> = try await client.send(.init(path: "/user/1"))
        XCTAssertEqual(response.value, User(id: 1, name: "Alice"))
    }
}
```

---

## Документация: DocC

- Добавьте DocC каталог: `Sources/AcmeNetworking/AcmeNetworking.docc/` с символами и туториалами.
- Настройте сборку документации в CI и публикацию (GitHub Pages/вики/артефакт релиза).

---

## Наблюдаемость

- Используйте `os.Logger` для структурных логов, уровни: debug/info/error.
- Для трассировки долгих операций — signposts (`OSSignpostID`, `os_signpost`).
- Не логируйте PII/секреты; в dev можно включать расширенный логгер через флаг конфигурации.

---

## Безопасность и производительность

- **Сетевые настройки**: разумные таймауты, поддержка отмены (`Task.cancel()`).
- **TLS pinning** (опционально) через `URLSessionDelegate`.
- **Keychain** для чувствительных токенов; избегайте глобальных синглтонов.
- **Память**: избегайте крупных копий данных, используйте `Data` слайсы/стриминг при необходимости.
- **Concurrency**: помечайте типы `Sendable`, используйте `@MainActor` для UI‑обратных вызовов.

---

## CI/CD: сборка, тесты, релизы

Пример GitHub Actions (SPM + DocC + релизные артефакты):

```yaml
name: ci
on:
  push:
    tags: [ 'v*.*.*' ]
    branches: [ main ]
jobs:
  build-and-test:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4
      - uses: maxim-lobanov/setup-xcode@v1
        with: { xcode-version: '16.0' }
      - name: Test (SPM)
        run: swift test --parallel
      - name: Build DocC
        run: swift package generate-documentation --target AcmeNetworking --output-path docs
      - name: Upload Docs
        uses: actions/upload-artifact@v4
        with: { name: docs, path: docs }

  release:
    if: startsWith(github.ref, 'refs/tags/')
    needs: build-and-test
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4
      - uses: maxim-lobanov/setup-xcode@v1
        with: { xcode-version: '16.0' }
      - name: Build XCFramework
        run: |
          xcodebuild archive -scheme AcmeNetworking -destination "generic/platform=iOS Simulator" -archivePath build/sim SKIP_INSTALL=NO BUILD_LIBRARY_FOR_DISTRIBUTION=YES
          xcodebuild archive -scheme AcmeNetworking -destination "generic/platform=iOS" -archivePath build/ios SKIP_INSTALL=NO BUILD_LIBRARY_FOR_DISTRIBUTION=YES
          xcodebuild -create-xcframework -framework build/sim.xcarchive/Products/Library/Frameworks/AcmeNetworking.framework -framework build/ios.xcarchive/Products/Library/Frameworks/AcmeNetworking.framework -output build/AcmeNetworking.xcframework
      - name: Release
        uses: softprops/action-gh-release@v2
        with:
          files: build/AcmeNetworking.xcframework
```

---

## Чеклист релиза

- [ ] Обновлены CHANGELOG и README, DocC с примерами
- [ ] Тесты зелёные, покрытие в норме; интеграционные тесты прошли
- [ ] Нет публичных API‑ломов для MINOR/PATCH релизов
- [ ] Версия SemVer и тег соответствуют изменениям
- [ ] Артефакты (XCFramework/Docs) опубликованы
- [ ] Включены флаги: Build Libraries for Distribution = YES (где нужно)

---

## Быстрый старт: использование `AcmeNetworking`

```swift
import AcmeNetworking

let client = HTTPClient(configuration: .init(baseURL: URL(string: "https://api.example.com")!))

struct Profile: Decodable { let id: Int; let name: String }

Task {
    do {
        let response: HTTPResponse<Profile> = try await client.send(.init(path: "/me"))
        print("Hello, \(response.value.name)")
    } catch {
        print("Request failed: \(error)")
    }
}
```

---

## Итоги и рекомендации Principal‑уровня

- Проектируйте **устойчивые** публичные API: минимум surface, чёткая эволюция.
- Управляйте совместимостью: **SemVer + Library Evolution**, избегайте `@frozen`, если не уверены.
- Поставляйте через **SPM** (исходники) и при необходимости — **XCFramework**.
- Вкладывайтесь в **наблюдаемость, безопасность и документацию** — это ускоряет поддержку и масштабирование.

---

## Глоссарий аббревиатур

- **ABI (Application Binary Interface)**: бинарный контракт между скомпилированными модулями. Совместимость ABI означает, что новый бинарь может подменить старый без пересборки клиентов.
- **Module Stability**: стабильность формата Swift‑интерфейсов (`.swiftinterface`), позволяющая компилировать клиенты против разных версий компилятора/SDK при неизменном публичном API.
- **SemVer (Semantic Versioning)**: схема версионирования `MAJOR.MINOR.PATCH` — MAJOR для ломающих изменений, MINOR для новых фич без ломов, PATCH для багфиксов.
- **SPM (Swift Package Manager)**: менеджер пакетов Swift, поставляет исходники/бинарные таргеты, интегрируется в Xcode.
- **XCFramework**: контейнер для универсальной поставки фреймворка (arm64/симулятор/разные платформы) как бинарного артефакта.
- **DocC**: система документации для Swift/Apple, генерирует сайты документации из аннотаций и туториалов.
- **Resilience**: способность публичного API эволюционировать без ABI‑ломов (resilient layout и правила совместимости).
- **SPI (System/Swift Private Interface)**: механизм маркировки символов для ограниченного доступа между модулями (не для публичных клиентов).
- **PII (Personally Identifiable Information)**: персональные данные, которые нельзя логировать/хранить без оснований.

---

## Пример использования `@_spi` для межмодульной интеграции

`@_spi` позволяет пометить API как «полуприватный»: он не виден обычным клиентам, но доступен другим модулям, которые импортируют ваш пакет с тем же SPI‑тегом. Это удобно для внутренних слоёв/плагинов без публикации символов всему миру.

```swift
// В пакете: Sources/Core/InternalSPI.swift
@_spi(Internal) public struct InternalDiagnostics {
    public static func mark(_ message: String) { /* ... */ }
}
```

В модуле‑потребителе (который вы контролируете):

```swift
@_spi(Internal) import Core

func debugStuff() {
    InternalDiagnostics.mark("DBG")
}
```

Важно:
- SPI — инструмент для внутренних контрактов. Не используйте его для публичных клиентов.
- Совместимость SPI между версиями также нужно поддерживать (SemVer внутри вашей организации), иначе внутренние модули сломаются.


