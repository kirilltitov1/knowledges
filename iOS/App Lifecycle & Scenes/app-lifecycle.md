---
title: App Lifecycle
type: thread
topics: [App Lifecycle & Scenes]
subtopic: app-lifecycle
status: draft
---

# App Lifecycle


### iOS 12 и ранее (UIApplicationDelegate)

#### Методы жизненного цикла
- `application(_:didFinishLaunchingWithOptions:)`
- `applicationWillEnterForeground(_:)`
- `applicationDidBecomeActive(_:)`
- `applicationWillResignActive(_:)`
- `applicationDidEnterBackground(_:)`
- `applicationWillTerminate(_:)`

#### App States
- Not Running
- Inactive
- Active
- Background
- Suspended

### iOS 13+ (Scene-based)

#### UISceneDelegate
- `scene(_:willConnectTo:options:)`
- `sceneDidBecomeActive(_:)`
- `sceneWillResignActive(_:)`
- `sceneWillEnterForeground(_:)`
- `sceneDidEnterBackground(_:)`
- `sceneDidDisconnect(_:)`

#### UIWindowSceneDelegate
- Window management
- Multiple windows support
- Scene configuration

#### Scene States
- Unattached
- Foreground Inactive
- Foreground Active
- Background
- Suspended

