---
title: Responder Chain — Snippets
type: snippet
topics: [UI]
subtopic: responder-chain
status: draft
level: advanced
platforms: [iOS]
ios_min: "11.0"
tags: [responder-chain, snippets, first-responder, uikit]
---

# Responder Chain — Snippets

## Печать цепочки от произвольного responder
```swift
extension UIResponder {
    func printResponderChain() {
        var node: UIResponder? = self
        var hops = 0
        while let current = node, hops < 128 {
            print("#\(hops): \(type(of: current)) -> \(String(describing: current.next)))")
            node = current.next
            hops += 1
        }
    }
}
```

## Нахождение First Responder в дереве view
```swift
extension UIView {
    func findFirstResponder() -> UIView? {
        if isFirstResponder { return self }
        for subview in subviews {
            if let fr = subview.findFirstResponder() { return fr }
        }
        return nil
    }
}
```

## Отправка действия по цепочке без таргета
```swift
// Вызовет первый responder, который умеет selector
UIApplication.shared.sendAction(#selector(copy(_:)), to: nil, from: self, for: nil)
```

## Кастомное меню с динамической доступностью
```swift
class MyView: UIView {
    override var canBecomeFirstResponder: Bool { true }

    override func canPerformAction(_ action: Selector, withSender sender: Any?) -> Bool {
        switch action {
        case #selector(copy(_:)): return hasSelection
        case #selector(paste(_:)): return UIPasteboard.general.hasStrings
        default: return false
        }
    }

    @objc func copy(_ sender: Any?) { /* ... */ }
    @objc func paste(_ sender: Any?) { /* ... */ }
}
```


