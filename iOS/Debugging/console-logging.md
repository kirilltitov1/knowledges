---
title: Console Logging
type: thread
topics: [Debugging]
subtopic: console-logging
status: draft
---

# Console Logging


### print vs NSLog vs os_log
```swift
// Swift print
print("Debug message")

// NSLog (Objective-C style)
NSLog("Message: %@", variable)

// os_log (Unified Logging)
os_log("Message", log: .default, type: .debug)
```

### Unified Logging System
- OSLog
- Log levels (debug, info, default, error, fault)
- Subsystems and categories
- Console.app filtering

### Custom Logging
- Logger protocols
- Log levels
- Debug vs Release builds
- Third-party loggers (SwiftyBeaver, CocoaLumberjack)

