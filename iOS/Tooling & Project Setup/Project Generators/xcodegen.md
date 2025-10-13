---
type: "thread"
status: "draft"
summary: ""
title: "XcodeGen"
---

# XcodeGen — генерация Xcode проектов из YAML

## Зачем
- Хранить конфигурацию проекта декларативно в `project.yml`.
- Простая интеграция в CI, быстрые генерации.

## Установка
```bash
brew install xcodegen
xcodegen --version
```

## Быстрый старт
Создайте `project.yml` в корне и выполните `xcodegen`.

### Пример `project.yml`
```yaml
name: App
options:
  minimumXcodeGenVersion: 2.38.0
targets:
  App:
    type: application
    platform: iOS
    deploymentTarget: "15.0"
    sources:
      - path: Sources
    resources:
      - path: Resources
    settings:
      base:
        PRODUCT_BUNDLE_IDENTIFIER: com.example.app
    dependencies:
      - target: Core
  Core:
    type: framework
    platform: iOS
    sources: [Core]
```

## Зависимости
- Встроенная поддержка SPM через `packages` секцию.
```yaml
packages:
  Alamofire:
    url: https://github.com/Alamofire/Alamofire.git
    from: 5.8.0
targets:
  App:
    dependencies:
      - package: Alamofire
```

## Команды
```bash
xcodegen                            # сгенерировать проект
xcodegen --spec path/to/project.yml # другой путь
```

## Плюсы / Минусы
- Плюсы: простой YAML, быстрый, статичен, легко читаем.
- Минусы: меньше возможностей программирования, чем у Tuist; сложнее переиспользование логики.




