---
type: "thread"
status: "draft"
summary: ""
title: "CocoaPods Workspace"
---

# CocoaPods — генерация Xcode workspace через Podfile

## Идея
- `pod install` формирует `.xcworkspace` и интегрирует Pods‑таргеты в проект.

## Быстрый старт
```ruby
platform :ios, '15.0'
use_frameworks!

target 'App' do
  pod 'Alamofire', '~> 5.8'
end
```

```bash
pod install
open App.xcworkspace
```

## Плюсы / Минусы
- Плюсы: зрелый менеджер зависимостей, автогенерация workspace.
- Минусы: внешний менеджер, медленнее чем SPM, добавляет прослойку к сборке.




