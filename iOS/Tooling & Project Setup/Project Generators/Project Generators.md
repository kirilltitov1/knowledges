---
type: "thread"
status: "draft"
summary: ""
title: "Project Generators"
---

# Генераторы проектов для iOS — обзор и сравнение

## Сводная таблица

| Инструмент | Подход | Язык конфигурации | Управление зависимостями | Масштабирование монорепо | Порог входа | Основные команды |
|---|---|---|---|---|---|---|
| Tuist | Код → проект | Swift (`Project.swift`) | SPM (+ плагины) | Высокое (workspaces, кеш) | Средний | `tuist init`, `tuist generate`, `tuist install` |
| XcodeGen | YAML → проект | YAML (`project.yml`) | SPM | Среднее | Низкий | `xcodegen` |
| Bazel + rules_xcodeproj | Билд‑граф → проект | Starlark/BUILD | Через правила | Очень высокое | Высокий | `bazel run //:xcodeproj` |
| Buck | Билд‑граф → проект | BUCK | Через правила | Высокое | Высокий | `buck project` |
| CocoaPods Workspace | Workspace → через Pods | Ruby (`Podfile`) | CocoaPods | Низкое/Среднее | Низкий | `pod install` |
| SwiftPM (gen xcodeproj) | Устарело | n/a | SPM | n/a | Низкий | n/a |

## Когда что выбирать
- Tuist: модульность, reuse, генерация как код, хороший DX.
- XcodeGen: минималистичная декларативная конфигурация, быстрая интеграция.
- Bazel/rules_xcodeproj: крупные репозитории, строгие графы, кэш CI.
- Buck: схож с Bazel, но реже встречается в iOS комьюнити.
- CocoaPods workspace: когда нужен Pods‑стек и автогенерация workspace.
- SwiftPM generate-xcodeproj: исторический, сейчас не используется.

## Материалы
- `tuist.md`
- `xcodegen.md`
- `bazel-rules_xcodeproj.md`
- `buck.md`
- `cocoapods-workspace.md`
- `swiftpm-generate-xcodeproj.md`




