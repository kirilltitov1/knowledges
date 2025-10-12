---
type: "example"
level: "intermediate"
platforms: "[iOS]"
ios_min: "15.0"
status: "draft"
tags: ["urlsession", "async-await", "endpoint"]
title: "Networking Generic API Client"
---
## Цель
Базовый типобезопасный сетевой клиент c async/await и паттерном Endpoint.

## Код (скелет)
```swift
import Foundation

public enum HTTPMethod: String { case GET, POST, PUT, PATCH, DELETE }

public struct Endpoint<Response: Decodable> {
    public let path: String
    public let method: HTTPMethod
    public var query: [URLQueryItem] = []
    public var headers: [String: String] = [:]
}

public protocol APIClient {
    func request<Response: Decodable>(_ endpoint: Endpoint<Response>) async throws -> Response
}

public final class URLSessionAPIClient: APIClient {
    private let baseURL: URL
    private let session: URLSession

    public init(baseURL: URL, session: URLSession = .shared) {
        self.baseURL = baseURL
        self.session = session
    }

    public func request<Response: Decodable>(_ endpoint: Endpoint<Response>) async throws -> Response {
        var components = URLComponents(url: baseURL.appendingPathComponent(endpoint.path), resolvingAgainstBaseURL: false)!
        components.queryItems = endpoint.query.isEmpty ? nil : endpoint.query
        var request = URLRequest(url: components.url!)
        request.httpMethod = endpoint.method.rawValue
        endpoint.headers.forEach { request.setValue($0.value, forHTTPHeaderField: $0.key) }

        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse, 200..<300 ~= http.statusCode else {
            throw URLError(.badServerResponse)
        }
        return try JSONDecoder().decode(Response.self, from: data)
    }
}
```

## Использование
```swift
struct Article: Decodable { let id: Int; let title: String }
let client = URLSessionAPIClient(baseURL: URL(string: "https://api.example.com")!)
let endpoint = Endpoint<[Article]>(path: "/articles", method: .GET)
let articles = try await client.request(endpoint)
```

## Заметки
- Расширяйте `Endpoint` под body/encoding.
- Добавьте error‑mapping.
- Покройте протоколом для DI и тестов.
