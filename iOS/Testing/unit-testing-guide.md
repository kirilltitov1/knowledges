---
title: Unit Testing в iOS - полное руководство
type: guide
topics: [Testing, Quality Assurance]
subtopic: unit-testing
status: draft
level: intermediate
platforms: [iOS, macOS, watchOS, tvOS]
ios_min: "9.0"
duration: 90m
tags: [unit-testing, xctest, mocking, tdd, test-driven-development, quality-assurance]
---

# 🧪 Unit Testing в iOS - полное руководство

Комплексное руководство по написанию эффективных unit тестов для iOS приложений с использованием XCTest и современными практиками.

## 📋 Содержание
- [Основы XCTest](#основы-xctest)
- [Структура тестов](#структура-тестов)
- [Mocking и Stubbing](#mocking-и-stubbing)
- [Test Driven Development](#test-driven-development)
- [Асинхронное тестирование](#асинхронное-тестирование)
- [Покрытие кода](#покрытие-кода)
- [Лучшие практики](#лучшие-практики)

## Основы XCTest

### Структура тестового класса

```swift
import XCTest

class UserManagerTests: XCTestCase {
    var userManager: UserManager!
    var mockUserService: MockUserService!

    // Выполняется перед каждым тестом
    override func setUp() {
        super.setUp()
        userManager = UserManager()
        mockUserService = MockUserService()
        userManager.userService = mockUserService
    }

    // Выполняется после каждого теста
    override func tearDown() {
        userManager = nil
        mockUserService = nil
        super.tearDown()
    }

    // Пример теста
    func testUserLoginSuccess() {
        // Given (Подготовка)
        let expectedUser = User(id: 1, name: "Test User")
        mockUserService.loginResult = .success(expectedUser)

        // When (Выполнение)
        let expectation = XCTestExpectation(description: "Login completion")
        userManager.login(username: "testuser", password: "password") { result in
            // Then (Проверка)
            switch result {
            case .success(let user):
                XCTAssertEqual(user.id, expectedUser.id)
                XCTAssertEqual(user.name, expectedUser.name)
            case .failure:
                XCTFail("Expected successful login")
            }
            expectation.fulfill()
        }

        wait(for: [expectation], timeout: 1.0)
    }
}
```

### Основные assertion методы

```swift
// Проверка равенства
XCTAssertEqual(user.name, "Test User")
XCTAssertNotEqual(result, expected)

// Проверка истинности
XCTAssertTrue(isValid)
XCTAssertFalse(isLoading)

// Проверка nil/не nil
XCTAssertNil(error)
XCTAssertNotNil(user)

// Проверка неудачи
XCTFail("This should not happen")

// Проверка бросания исключений
XCTAssertThrowsError(try riskyOperation())
XCTAssertNoThrow(try safeOperation())
```

## Структура тестов

### Given-When-Then паттерн

```swift
func testUserRegistration() {
    // Given - Подготовка тестовых данных
    let userData = UserData(name: "John", email: "john@example.com")
    mockUserService.registerResult = .success(User(id: 1, name: "John"))

    // When - Выполнение тестируемого кода
    let expectation = XCTestExpectation(description: "Registration completion")
    userManager.register(userData: userData) { result in
        // Then - Проверка результатов
        switch result {
        case .success(let user):
            XCTAssertEqual(user.name, "John")
            XCTAssertNotNil(user.id)
        case .failure(let error):
            XCTFail("Registration should succeed: \(error)")
        }
        expectation.fulfill()
    }

    wait(for: [expectation], timeout: 1.0)
}
```

### Тестовые данные (Test Data Builders)

```swift
class UserTestData {
    static func validUser() -> User {
        return User(id: 1, name: "Test User", email: "test@example.com")
    }

    static func invalidUser() -> User {
        return User(id: 0, name: "", email: "invalid-email")
    }

    static func userWithLongName() -> User {
        return User(id: 1, name: String(repeating: "A", count: 100), email: "test@example.com")
    }
}

// Использование в тестах
func testUserValidation() {
    let validUser = UserTestData.validUser()
    let invalidUser = UserTestData.invalidUser()

    // Тестирование валидации
    XCTAssertTrue(userValidator.isValid(validUser))
    XCTAssertFalse(userValidator.isValid(invalidUser))
}
```

## Mocking и Stubbing

### Создание Mock объектов

```swift
protocol UserServiceProtocol {
    func fetchUser(id: Int, completion: @escaping (Result<User, Error>) -> Void)
    func saveUser(_ user: User, completion: @escaping (Result<Void, Error>) -> Void)
}

class MockUserService: UserServiceProtocol {
    var fetchUserCallCount = 0
    var saveUserCallCount = 0
    var lastFetchedUserId: Int?
    var lastSavedUser: User?

    var fetchUserResult: Result<User, Error> = .failure(NSError(domain: "TestError", code: 0))
    var saveUserResult: Result<Void, Error> = .success(())

    func fetchUser(id: Int, completion: @escaping (Result<User, Error>) -> Void) {
        fetchUserCallCount += 1
        lastFetchedUserId = id
        completion(fetchUserResult)
    }

    func saveUser(_ user: User, completion: @escaping (Result<Void, Error>) -> Void) {
        saveUserCallCount += 1
        lastSavedUser = user
        completion(saveUserResult)
    }
}
```

### Создание Stub данных

```swift
class TestDataFactory {
    static func createUsers(count: Int) -> [User] {
        return (1...count).map { index in
            User(id: index, name: "User \(index)", email: "user\(index)@example.com")
        }
    }

    static func createError(message: String) -> NSError {
        return NSError(domain: "TestDomain", code: 0, userInfo: [NSLocalizedDescriptionKey: message])
    }
}
```

## Test Driven Development

### Красный-Зеленый-Рефактор цикл

```swift
// 1. Красный: Напишите тест, который падает
func testUserAuthentication() {
    // Given
    let authManager = AuthenticationManager()
    let credentials = Credentials(username: "test", password: "password")

    // When & Then - тест должен падать, так как функциональность не реализована
    XCTAssertTrue(authManager.authenticate(credentials))
}

// 2. Зеленый: Реализуйте минимальный код, чтобы тест прошел
class AuthenticationManager {
    func authenticate(_ credentials: Credentials) -> Bool {
        return credentials.username == "test" && credentials.password == "password"
    }
}

// 3. Рефактор: Улучшите код, сохраняя тесты зелеными
class AuthenticationManager {
    private let validCredentials = ["test": "password"]

    func authenticate(_ credentials: Credentials) -> Bool {
        return validCredentials[credentials.username] == credentials.password
    }
}
```

### TDD для нового функционала

```swift
// Требования: Пользователь должен иметь возможность зарегистрироваться

// Шаг 1: Напишите тест для еще не существующего функционала
func testUserRegistration() {
    let userManager = UserManager()
    let userData = UserRegistrationData(email: "test@example.com", password: "password123")

    let expectation = XCTestExpectation(description: "Registration completion")
    userManager.register(userData: userData) { result in
        switch result {
        case .success(let user):
            XCTAssertEqual(user.email, "test@example.com")
            XCTAssertNotNil(user.id)
        case .failure:
            XCTFail("Registration should succeed")
        }
        expectation.fulfill()
    }

    wait(for: [expectation], timeout: 1.0)
}

// Шаг 2: Реализуйте минимальный код
class UserManager {
    func register(userData: UserRegistrationData, completion: @escaping (Result<User, Error>) -> Void) {
        // Минимальная реализация
        let user = User(id: 1, email: userData.email)
        completion(.success(user))
    }
}

// Шаг 3: Рефактор и добавление валидации
class UserManager {
    private let userService: UserService

    init(userService: UserService = UserService.shared) {
        self.userService = userService
    }

    func register(userData: UserRegistrationData, completion: @escaping (Result<User, Error>) -> Void) {
        // Валидация данных
        guard isValidEmail(userData.email) else {
            completion(.failure(ValidationError.invalidEmail))
            return
        }

        userService.register(userData: userData, completion: completion)
    }
}
```

## Асинхронное тестирование

### Тестирование асинхронных операций

```swift
func testAsyncOperation() {
    // Given
    let asyncService = AsyncService()
    let expectation = XCTestExpectation(description: "Async operation completion")

    // When
    asyncService.performAsyncTask { result in
        // Then
        switch result {
        case .success(let data):
            XCTAssertNotNil(data)
        case .failure(let error):
            XCTFail("Should not fail: \(error)")
        }
        expectation.fulfill()
    }

    // Wait for async operation
    wait(for: [expectation], timeout: 5.0)
}
```

### Тестирование с таймаутами

```swift
func testOperationTimeout() {
    let asyncService = AsyncService()
    let expectation = XCTestExpectation(description: "Operation should timeout")

    asyncService.performSlowTask(timeout: 2.0) { result in
        switch result {
        case .success:
            XCTFail("Should have timed out")
        case .failure(let error):
            if case AsyncError.timeout = error {
                // Expected timeout
            } else {
                XCTFail("Wrong error type")
            }
        }
        expectation.fulfill()
    }

    wait(for: [expectation], timeout: 3.0)
}
```

### Тестирование Combine publishers

```swift
import Combine

func testCombinePublisher() {
    // Given
    let publisher = PassthroughSubject<String, Error>()
    var receivedValues: [String] = []
    var completionReceived = false

    let cancellable = publisher
        .sink(receiveCompletion: { _ in
            completionReceived = true
        }, receiveValue: { value in
            receivedValues.append(value)
        })

    // When
    publisher.send("value1")
    publisher.send("value2")
    publisher.send(completion: .finished)

    // Then
    XCTAssertEqual(receivedValues, ["value1", "value2"])
    XCTAssertTrue(completionReceived)

    cancellable.cancel()
}
```

## Покрытие кода

### Настройка покрытия кода

```bash
# В Build Settings проекта:
GCC_GENERATE_TEST_COVERAGE_FILES = YES
GCC_INSTRUMENT_PROGRAM_FLOW_ARCS = YES

# Для Swift:
SWIFT_COMPILATION_MODE = singlefile  # Для лучшего покрытия
```

### Анализ покрытия

```swift
// Инструмент для анализа покрытия
class CoverageAnalyzer {
    static func generateCoverageReport() {
        // Генерация отчета о покрытии
        // Можно интегрировать с внешними сервисами
    }
}
```

### Целевые показатели покрытия

```swift
// Рекомендуемые уровни покрытия:
// - Model: 90%+
// - ViewModel/Business Logic: 80%+
// - View Controllers: 70%+
// - Utility классы: 95%+
```

## Лучшие практики

### 1. Организация тестов

```swift
class UserManagerTests: XCTestCase {
    // MARK: - Setup

    override func setUp() { /* ... */ }
    override func tearDown() { /* ... */ }

    // MARK: - Login Tests

    func testLoginWithValidCredentials() { /* ... */ }
    func testLoginWithInvalidCredentials() { /* ... */ }
    func testLoginWithNetworkError() { /* ... */ }

    // MARK: - Registration Tests

    func testRegistrationWithValidData() { /* ... */ }
    func testRegistrationWithInvalidEmail() { /* ... */ }

    // MARK: - Helper Methods

    private func createValidUser() -> User { /* ... */ }
    private func createMockUserService() -> MockUserService { /* ... */ }
}
```

### 2. Независимые тесты

```swift
// ❌ Неправильно - тесты зависят друг от друга
func testA() {
    // Настраивает состояние для теста B
}

func testB() {
    // Зависит от состояния, установленного в тесте A
}

// ✅ Правильно - каждый тест независим
func testFeatureA() {
    // Полная настройка для этого теста
}

func testFeatureB() {
    // Полная настройка для этого теста
}
```

### 3. Описательные названия тестов

```swift
// ❌ Неправильно
func test1() { }
func testUser() { }

// ✅ Правильно
func testUserLoginWithValidCredentialsSucceeds() { }
func testUserLoginWithInvalidCredentialsFails() { }
func testUserRegistrationValidatesEmailFormat() { }
```

### 4. Избегайте хрупких тестов

```swift
// ❌ Неправильно - зависит от приватных деталей реализации
func testInternalMethod() {
    let userManager = UserManager()
    // Доступ к приватным методам
}

// ✅ Правильно - тестирует публичное поведение
func testUserCanLoginWithValidCredentials() {
    let userManager = UserManager()
    // Тестирует публичный интерфейс
}
```

## Примеры реальных тестов

### Тестирование ViewModel

```swift
class UserProfileViewModelTests: XCTestCase {
    var viewModel: UserProfileViewModel!
    var mockUserService: MockUserService!
    var mockCoordinator: MockUserProfileCoordinator!

    override func setUp() {
        super.setUp()
        mockUserService = MockUserService()
        mockCoordinator = MockUserProfileCoordinator()
        viewModel = UserProfileViewModel(userService: mockUserService, coordinator: mockCoordinator)
    }

    func testLoadingStateWhenFetchingUser() {
        // Given
        XCTAssertEqual(viewModel.state, .idle)

        // When
        viewModel.loadUser(id: 1)

        // Then
        XCTAssertEqual(viewModel.state, .loading)
    }

    func testShowsUserWhenFetchSucceeds() {
        // Given
        let expectedUser = User(id: 1, name: "Test User")
        mockUserService.fetchUserResult = .success(expectedUser)

        // When
        viewModel.loadUser(id: 1)

        // Then
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            XCTAssertEqual(self.viewModel.state, .loaded(expectedUser))
        }
    }

    func testShowsErrorWhenFetchFails() {
        // Given
        let expectedError = NSError(domain: "TestError", code: 0)
        mockUserService.fetchUserResult = .failure(expectedError)

        // When
        viewModel.loadUser(id: 1)

        // Then
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            XCTAssertEqual(self.viewModel.state, .error(expectedError))
        }
    }
}
```

### Тестирование сетевого слоя

```swift
class NetworkManagerTests: XCTestCase {
    var networkManager: NetworkManager!
    var mockURLSession: MockURLSession!

    override func setUp() {
        super.setUp()
        mockURLSession = MockURLSession()
        networkManager = NetworkManager(session: mockURLSession)
    }

    func testSuccessfulRequest() {
        // Given
        let expectedData = "{\"id\": 1, \"name\": \"Test\"}".data(using: .utf8)!
        let response = HTTPURLResponse(url: URL(string: "https://api.example.com")!,
                                     statusCode: 200,
                                     httpVersion: nil,
                                     headerFields: nil)!

        mockURLSession.dataTaskResult = (expectedData, response)

        // When
        let expectation = XCTestExpectation(description: "Network request")
        networkManager.fetchData(from: "https://api.example.com") { result in
            // Then
            switch result {
            case .success(let data):
                XCTAssertEqual(data, expectedData)
            case .failure:
                XCTFail("Request should succeed")
            }
            expectation.fulfill()
        }

        wait(for: [expectation], timeout: 1.0)
    }

    func testNetworkError() {
        // Given
        let expectedError = NSError(domain: NSURLErrorDomain, code: NSURLErrorNotConnectedToInternet)
        mockURLSession.dataTaskResult = (nil, nil, expectedError)

        // When
        let expectation = XCTestExpectation(description: "Network error")
        networkManager.fetchData(from: "https://api.example.com") { result in
            // Then
            switch result {
            case .success:
                XCTFail("Request should fail")
            case .failure(let error):
                XCTAssertEqual((error as NSError).code, NSURLErrorNotConnectedToInternet)
            }
            expectation.fulfill()
        }

        wait(for: [expectation], timeout: 1.0)
    }
}
```

## Распространенные ошибки в тестировании

### 1. Тесты зависят от внешних факторов

```swift
// ❌ Неправильно - зависит от реального API
func testRealAPI() {
    let apiClient = APIClient()
    apiClient.fetchUsers { users in
        XCTAssertGreaterThan(users.count, 0) // Может падать
    }
}

// ✅ Правильно - контролируемые тесты
func testAPIWithMock() {
    let mockService = MockAPIService()
    mockService.users = [User(id: 1, name: "Test")]
    let apiClient = APIClient(service: mockService)

    apiClient.fetchUsers { users in
        XCTAssertEqual(users.count, 1)
    }
}
```

### 2. Неправильное использование асинхронных тестов

```swift
// ❌ Неправильно - нет ожидания
func testAsyncOperation() {
    asyncService.performTask { result in
        XCTAssertTrue(result.isSuccess) // Может выполниться до завершения
    }
}

// ✅ Правильно - с ожиданием
func testAsyncOperation() {
    let expectation = XCTestExpectation(description: "Async operation")

    asyncService.performTask { result in
        XCTAssertTrue(result.isSuccess)
        expectation.fulfill()
    }

    wait(for: [expectation], timeout: 1.0)
}
```

### 3. Тесты без очистки состояния

```swift
// ❌ Неправильно - состояние сохраняется между тестами
class MyTests: XCTestCase {
    static var sharedData = [String]()

    func test1() {
        MyTests.sharedData.append("test1")
    }

    func test2() {
        XCTAssertEqual(MyTests.sharedData.count, 1) // Может падать из-за test1
    }
}

// ✅ Правильно - изолированные тесты
class MyTests: XCTestCase {
    var testData = [String]()

    func test1() {
        testData.append("test1")
        XCTAssertEqual(testData.count, 1)
    }

    func test2() {
        testData.append("test2")
        XCTAssertEqual(testData.count, 1) // Только данные этого теста
    }
}
```

## Автоматизация тестирования

### 1. Настройка CI/CD для тестов

```yaml
# .github/workflows/tests.yml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          xcodebuild test \
            -workspace MyApp.xcworkspace \
            -scheme MyApp \
            -destination 'platform=iOS Simulator,name=iPhone 15' \
            -enableCodeCoverage YES
```

### 2. Генерация отчетов о покрытии

```bash
# Генерация отчета о покрытии
xcodebuild test \
    -workspace MyApp.xcworkspace \
    -scheme MyApp \
    -destination 'platform=iOS Simulator,name=iPhone 15' \
    -enableCodeCoverage YES \
    -derivedDataPath build

# Конвертация в HTML отчет
xcov --project build --output coverage_report
```

## Заключение

Эффективное unit тестирование — ключевой компонент качественного iOS приложения. Основные принципы:

1. **Пишите тесты перед кодом** (TDD подход)
2. **Делайте тесты независимыми и изолированными**
3. **Используйте описательные названия** для тестов
4. **Mock внешние зависимости** для контролируемости
5. **Тестируйте асинхронный код** правильно
6. **Стремитесь к высокому покрытию** кода тестами
7. **Автоматизируйте запуск тестов** в CI/CD

Помните: "Код без тестов — это код, который не работает."

## Ссылки
- [XCTest Documentation](https://developer.apple.com/documentation/xctest)
- [Test Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
- [Xcode Testing Guide](https://developer.apple.com/library/archive/documentation/DeveloperTools/Conceptual/testing_with_xcode/)
- [WWDC: Testing in Xcode](https://developer.apple.com/videos/play/wwdc2019/413/)
