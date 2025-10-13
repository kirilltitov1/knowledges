---
type: "thread"
status: "draft"
summary: ""
title: "Tuist"
---

# Tuist — генерация Xcode проектов как код

## Зачем
- **Консистентность**: проект описывается в `Project.swift`, повторяемость между командами/окружениями.
- **Скорость онбординга**: `tuist generate` создаёт проект с нужными настройками и зависимостями.
- **Модульность**: удобная декомпозиция на `Targets`/`Projects`/`Workspace`.

## Установка
```bash
bash <(curl -Ls https://install.tuist.io)
tuist version
```

Альтернатива через `Mint`:
```bash
mint install tuist/tuist
```

## Быстрый старт
```bash
tuist init --platform ios --template swiftui
tuist generate
```

Создаст `Project.swift` и структуру исходников. Откройте сгенерированный `.xcodeproj`.

## Ключевые сущности
- `Project.swift` — описание таргетов, схем, зависимостей.
- `Workspace.swift` — объединение нескольких проектов.
- `Tuist/` — плагины, манифесты, конфигурации.

## Пример `Project.swift`
```swift
import ProjectDescription

let project = Project(
    name: "App",
    targets: [
        .target(
            name: "App",
            destinations: [.iPhone, .iPad],
            product: .app,
            bundleId: "com.example.app",
            infoPlist: .extendingDefault(with: [
                "UILaunchStoryboardName": "LaunchScreen"
            ]),
            sources: ["Sources/**"],
            resources: ["Resources/**"],
            dependencies: [
                .target(name: "Core"),
                .external(name: "Alamofire")
            ]
        ),
        .target(
            name: "Core",
            destinations: [.iPhone, .iPad],
            product: .framework,
            bundleId: "com.example.core",
            sources: ["Core/**"],
            resources: []
        )
    ]
)
```

## Управление зависимостями
- `Tuist/Dependencies.swift` позволяет подключить SPM.

```swift
import ProjectDescription

let dependencies = Dependencies(swiftPackageManager: .init(
    baseSettings: .settings(),
    projects: [
        .remote(url: "https://github.com/Alamofire/Alamofire.git", requirement: .upToNextMajor(from: "5.8.0"))
    ]
))
```

Команды:
```bash
tuist install
tuist generate
```

## Workspaces и модули
- Вынесите фичи/ядро в отдельные проекты и объедините через `Workspace.swift`.

```swift
import ProjectDescription

let workspace = Workspace(name: "AppWorkspace", projects: [
  ".", "Modules/Core", "Modules/FeatureA"
])
```

## CI интеграция
- Кеширование билдов и зависимостей (`tuist cache warm`).
- Генерация для конкретной схемы/конфигурации.

```bash
tuist cache warm --dependencies-only
tuist generate --project-only
```

## Лучшие практики
- Храните манифесты в репозитории, генерацию проекта делайте детерминированной.
- Версионируйте Tuist с помощью `tuist local` для стабильности.
- Разносите общие настройки в плагины/хелперы (директория `Tuist/ProjectDescriptionHelpers`).

## Траблшутинг
- Если Xcode проект «плывёт» — пересоберите (`tuist clean && tuist generate`).
- Конфликты зависимостей — проверяйте `Tuist/Dependencies.lock` и перегенерируйте `tuist install`.




