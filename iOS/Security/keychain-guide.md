---
type: "guide"
status: "draft"
level: "intermediate"
title: "Keychain Guide"
---

# 🔐 Keychain - безопасное хранение данных

Комплексное руководство по использованию Keychain Services для безопасного хранения конфиденциальных данных в iOS приложениях.

## 📋 Содержание
- [Основы Keychain](#основы-keychain)
- [Типы данных для хранения](#типы-данных-для-хранения)
- [Настройка доступа](#настройка-доступа)
- [Биометрическая аутентификация](#биометрическая-аутентификация)
- [Синхронизация с iCloud](#синхронизация-с-icloud)
- [Примеры кода](#примеры-кода)
- [Безопасность и лучшие практики](#безопасность-и-лучшие-практики)

## Основы Keychain

### Что такое Keychain Services?

**Keychain Services** — это инфраструктура Apple для безопасного хранения небольших объемов конфиденциальной информации, такой как:
- Пароли и токены аутентификации
- Ключи шифрования
- Сертификаты
- Биометрические данные

### Преимущества Keychain

1. **Шифрование** - данные шифруются на устройстве
2. **Защита от несанкционированного доступа**
3. **Синхронизация с iCloud** (опционально)
4. **Интеграция с биометрией**
5. **Автоматическая очистка** при удалении приложения

### Структура Keychain

```swift
// Основные классы для работы с Keychain
import Security

// Классы элементов Keychain
enum KeychainClass {
    case genericPassword    // Общие пароли
    case internetPassword   // Пароли для интернета
    case certificate        // Сертификаты
    case key                // Ключи шифрования
    case identity           // Идентичности (сертификат + ключ)
}
```

## Типы данных для хранения

### 1. Generic Passwords

Для хранения произвольных данных:

```swift
// Сохранение данных
let query: [String: Any] = [
    kSecClass as String: kSecClassGenericPassword,
    kSecAttrAccount as String: "user_token",
    kSecAttrService as String: "com.myapp.auth",
    kSecValueData as String: tokenData
]

let status = SecItemAdd(query as CFDictionary, nil)
```

### 2. Internet Passwords

Для хранения учетных данных веб-сайтов:

```swift
let query: [String: Any] = [
    kSecClass as String: kSecClassInternetPassword,
    kSecAttrServer as String: "api.myapp.com",
    kSecAttrAccount as String: username,
    kSecAttrPort as String: 443,
    kSecAttrProtocol as String: kSecAttrProtocolHTTPS,
    kSecValueData as String: passwordData
]
```

### 3. Certificates

Для хранения сертификатов:

```swift
let query: [String: Any] = [
    kSecClass as String: kSecClassCertificate,
    kSecAttrLabel as String: "My App Certificate",
    kSecValueRef as String: certificateRef
]
```

## Настройка доступа

### Уровни защиты данных

```swift
// Доступные уровни защиты
enum KeychainAccessibility {
    case whenUnlocked              // Доступен когда устройство разблокировано
    case whenUnlockedThisDeviceOnly // Только на этом устройстве
    case whenPasscodeSetThisDeviceOnly // После установки кода-пароля
    case afterFirstUnlock          // После первой разблокировки
    case afterFirstUnlockThisDeviceOnly // После первой разблокировки, только это устройство
    case always                    // Всегда доступен
    case alwaysThisDeviceOnly      // Всегда, только это устройство
    case accessibleWhenPasscodeSetThisDeviceOnly // Когда код-пароль установлен
}
```

### Пример настройки доступа

```swift
let query: [String: Any] = [
    kSecClass as String: kSecClassGenericPassword,
    kSecAttrAccount as String: "sensitive_data",
    kSecAttrService as String: "com.myapp.security",
    kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
    kSecValueData as String: sensitiveData
]
```

## Биометрическая аутентификация

### Local Authentication Framework

```swift
import LocalAuthentication

class BiometricManager {
    private let context = LAContext()

    func authenticateUser(completion: @escaping (Bool, Error?) -> Void) {
        var error: NSError?

        // Проверка доступности биометрии
        if context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) {
            let reason = "Необходимо подтвердить личность для доступа к данным"

            context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics,
                                 localizedReason: reason) { success, error in
                DispatchQueue.main.async {
                    completion(success, error)
                }
            }
        } else {
            completion(false, error)
        }
    }
}
```

### Интеграция с Keychain

```swift
class SecureDataManager {
    private let biometricManager = BiometricManager()

    func saveDataWithBiometricProtection(_ data: Data, key: String) {
        biometricManager.authenticateUser { [weak self] success, error in
            guard success else {
                print("Аутентификация не удалась: \(error?.localizedDescription ?? "")")
                return
            }

            self?.saveToKeychain(data, forKey: key)
        }
    }

    private func saveToKeychain(_ data: Data, forKey key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecAttrService as String: "com.myapp.securedata",
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
            kSecValueData as String: data
        ]

        SecItemDelete(query as CFDictionary) // Удаляем старые данные
        let status = SecItemAdd(query as CFDictionary, nil)

        if status != errSecSuccess {
            print("Ошибка сохранения в Keychain: \(status)")
        }
    }

    func retrieveData(forKey key: String, completion: @escaping (Data?) -> Void) {
        biometricManager.authenticateUser { success, error in
            guard success else {
                completion(nil)
                return
            }

            let data = self.retrieveFromKeychain(forKey: key)
            completion(data)
        }
    }

    private func retrieveFromKeychain(forKey key: String) -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecAttrService as String: "com.myapp.securedata",
            kSecReturnData as String: true
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        if status == errSecSuccess {
            return result as? Data
        }

        return nil
    }
}
```

## Синхронизация с iCloud

### Настройка синхронизации

```swift
// В Capabilities проекта включите Keychain Sharing
// В entitlements добавьте:

<key>keychain-access-groups</key>
<array>
    <string>$(AppIdentifierPrefix)com.myapp.keychain</string>
</array>
```

### Синхронизируемый Keychain

```swift
func saveDataWithiCloudSync(_ data: Data, key: String) {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: key,
        kSecAttrService as String: "com.myapp.icloudsync",
        kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlocked,
        kSecAttrSynchronizable as String: true, // Включаем синхронизацию
        kSecValueData as String: data
    ]

    SecItemDelete(query as CFDictionary)
    let status = SecItemAdd(query as CFDictionary, nil)

    if status != errSecSuccess {
        print("Ошибка сохранения с синхронизацией: \(status)")
    }
}
```

## Примеры кода

### 1. Хранение токенов аутентификации

```swift
class AuthTokenManager {
    private let service = "com.myapp.authtokens"

    func saveToken(_ token: String, forUser userId: String) {
        guard let tokenData = token.data(using: .utf8) else { return }

        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: userId,
            kSecAttrService as String: service,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
            kSecValueData as String: tokenData
        ]

        // Удаляем старый токен если существует
        SecItemDelete(query as CFDictionary)

        let status = SecItemAdd(query as CFDictionary, nil)
        if status != errSecSuccess {
            print("Ошибка сохранения токена: \(status)")
        }
    }

    func getToken(forUser userId: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: userId,
            kSecAttrService as String: service,
            kSecReturnData as String: true
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        if status == errSecSuccess, let data = result as? Data {
            return String(data: data, encoding: .utf8)
        }

        return nil
    }

    func deleteToken(forUser userId: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: userId,
            kSecAttrService as String: service
        ]

        SecItemDelete(query as CFDictionary)
    }
}
```

### 2. Хранение ключей шифрования

```swift
class EncryptionKeyManager {
    private let service = "com.myapp.encryptionkeys"

    func generateAndSaveEncryptionKey() -> Data? {
        var keyData = Data(count: 32)
        let result = keyData.withUnsafeMutableBytes {
            SecRandomCopyBytes(kSecRandomDefault, 32, $0.baseAddress!)
        }

        guard result == errSecSuccess else { return nil }

        let query: [String: Any] = [
            kSecClass as String: kSecClassKey,
            kSecAttrApplicationTag as String: "com.myapp.encryptionkey",
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
            kSecValueData as String: keyData
        ]

        SecItemDelete(query as CFDictionary)
        let status = SecItemAdd(query as CFDictionary, nil)

        return status == errSecSuccess ? keyData : nil
    }

    func getEncryptionKey() -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassKey,
            kSecAttrApplicationTag as String: "com.myapp.encryptionkey",
            kSecReturnData as String: true
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        return status == errSecSuccess ? result as? Data : nil
    }
}
```

### 3. Биометрическая защита для платежей

```swift
class PaymentManager {
    private let secureManager = SecureDataManager()

    func makeSecurePayment(amount: Double, cardData: CardData) {
        // Сначала аутентифицируем пользователя
        secureManager.authenticateWithBiometrics { [weak self] success in
            guard success else {
                self?.handlePaymentError("Аутентификация не удалась")
                return
            }

            // Если аутентификация успешна, сохраняем данные платежа
            let paymentData = PaymentData(amount: amount, card: cardData)
            self?.processPayment(paymentData)
        }
    }

    private func processPayment(_ paymentData: PaymentData) {
        // Обработка платежа с использованием биометрически защищенных данных
        NetworkManager.shared.makePayment(paymentData) { result in
            switch result {
            case .success:
                self.handlePaymentSuccess()
            case .failure(let error):
                self.handlePaymentError(error.localizedDescription)
            }
        }
    }
}
```

## Безопасность и лучшие практики

### 1. Выбор правильного уровня доступа

```swift
// Для данных, которые нужны только когда устройство разблокировано
kSecAttrAccessibleWhenUnlocked

// Для данных, которые нужны только на этом устройстве
kSecAttrAccessibleWhenUnlockedThisDeviceOnly

// Для данных, которые доступны после первой разблокировки
kSecAttrAccessibleAfterFirstUnlock

// Для данных, которые всегда доступны (использовать осторожно!)
kSecAttrAccessibleAlways
```

### 2. Обработка ошибок

```swift
func handleKeychainError(_ status: OSStatus) {
    switch status {
    case errSecSuccess:
        print("Операция выполнена успешно")
    case errSecDuplicateItem:
        print("Элемент уже существует")
    case errSecItemNotFound:
        print("Элемент не найден")
    case errSecAuthFailed:
        print("Ошибка аутентификации")
    case errSecInteractionNotAllowed:
        print("Взаимодействие не разрешено")
    case errSecDecode:
        print("Ошибка декодирования")
    default:
        print("Неизвестная ошибка Keychain: \(status)")
    }
}
```

### 3. Очистка данных при деинсталляции

```swift
class AppLifecycleManager {
    static let shared = AppLifecycleManager()

    func cleanupSensitiveData() {
        // Очистка всех элементов Keychain приложения
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: "com.myapp"
        ]

        SecItemDelete(query as CFDictionary)

        // Очистка ключей шифрования
        let keyQuery: [String: Any] = [
            kSecClass as String: kSecClassKey,
            kSecAttrApplicationTag as String: "com.myapp"
        ]

        SecItemDelete(keyQuery as CFDictionary)
    }
}
```

### 4. Мониторинг доступа к Keychain

```swift
// Включение логирования доступа к Keychain
func enableKeychainLogging() {
    // Добавьте в схему запуска приложения:
    // Environment Variables: OS_ACTIVITY_MODE = disable
    // Или используйте Console.app для мониторинга
}
```

## Распространенные ошибки

### 1. Неправильный уровень доступа

```swift
// ❌ Неправильно - данные всегда доступны
kSecAttrAccessibleAlways

// ✅ Правильно - данные доступны только когда разблокировано
kSecAttrAccessibleWhenUnlockedThisDeviceOnly
```

### 2. Отсутствие обработки ошибок

```swift
// ❌ Неправильно - игнорируем ошибки
SecItemAdd(query as CFDictionary, nil)

// ✅ Правильно - обрабатываем ошибки
let status = SecItemAdd(query as CFDictionary, nil)
if status != errSecSuccess {
    handleKeychainError(status)
}
```

### 3. Небезопасное хранение больших данных

```swift
// ❌ Неправильно - большие данные в Keychain
let largeFileData = try Data(contentsOf: largeFileURL)
saveToKeychain(largeFileData) // Keychain не для больших файлов

// ✅ Правильно - только ключи шифрования
let encryptionKey = generateEncryptionKey()
saveEncryptionKeyToKeychain(encryptionKey)
encryptFile(largeFileURL, withKey: encryptionKey)
```

## Тестирование Keychain

### 1. Мокирование Keychain для тестов

```swift
class MockKeychainManager: KeychainManagerProtocol {
    private var storage = [String: Data]()

    func save(_ data: Data, forKey key: String) {
        storage[key] = data
    }

    func retrieve(forKey key: String) -> Data? {
        return storage[key]
    }

    func delete(forKey key: String) {
        storage.removeValue(forKey: key)
    }
}
```

### 2. Тестирование с реальным Keychain

```swift
class KeychainManagerTests: XCTestCase {
    private var keychainManager: KeychainManager!

    override func setUp() {
        super.setUp()
        keychainManager = KeychainManager()
    }

    func testSaveAndRetrieveData() {
        let testData = "test data".data(using: .utf8)!

        // Сохраняем данные
        keychainManager.save(testData, forKey: "test_key")

        // Получаем данные
        let retrievedData = keychainManager.retrieve(forKey: "test_key")

        // Проверяем
        XCTAssertEqual(testData, retrievedData)
    }

    override func tearDown() {
        super.tearDown()
        // Очищаем тестовые данные
        keychainManager.delete(forKey: "test_key")
    }
}
```

## Заключение

Keychain Services — мощный инструмент для безопасного хранения конфиденциальной информации в iOS приложениях. Основные принципы эффективного использования:

1. **Выбирайте правильный уровень доступа** в зависимости от требований безопасности
2. **Интегрируйте биометрическую аутентификацию** для повышенной защиты
3. **Обрабатывайте ошибки правильно** для надежной работы
4. **Используйте синхронизацию с iCloud** только когда необходимо
5. **Тестируйте тщательно** особенно с биометрией

Помните: "Безопасность — это не то, что можно добавить позже. Это нужно учитывать с самого начала."

## Ссылки
- [Keychain Services Programming Guide](https://developer.apple.com/documentation/security/keychain_services)
- [Local Authentication Framework](https://developer.apple.com/documentation/localauthentication)
- [WWDC: Security on iOS](https://developer.apple.com/videos/play/wwdc2018/702/)
- [WWDC: Protecting your user's privacy](https://developer.apple.com/videos/play/wwdc2020/10676/)
