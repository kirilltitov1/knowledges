---
type: "guide"
topics: ["UI", "Debugging", "Architecture"]
status: "draft"
level: "advanced"
title: "Responder Chain"
---

## 1) Что такое Responder Chain

Responder Chain — это динамическая цепочка объектов, способных обрабатывать события (touches, gestures, editing, hardware events, menu/command actions, First Responder forwarding и т.д.). Объект должен наследоваться от `UIResponder` (UIKit) или задействовать соответствующие адаптеры в SwiftUI. Основные типы: `UIWindow`, `UIView`, `UIViewController`, `UIApplication`.

Ключевая идея: событие отправляется текущему кандидату (обычно First Responder). Если он не обрабатывает, оно поднимается вверх по цепочке к следующему звену, пока не будет обработано или отброшено.
---

## 2) Откуда начинается цепочка

Старты зависят от типа события:
- Touch/gesture: начинается с самой глубокой `UIView`, попавшей под hit-testing (`hitTest(_:with:)` → `point(inside:with:)`), затем вверх по иерархии view → `UIViewController` (если есть) → `UIWindow` → `UIApplication` → `App Delegate` fallback.
- Editing/key commands: с First Responder (`UIResponder.isFirstResponder == true`), затем его `next` по цепочке.
- Menu/command actions (`canPerformAction:withSender:`/`sendAction`): с First Responder, затем подъем вверх.
- Motion/remote control: активное окно/первый responder, далее вверх по цепи.

---

## 3) Формирование next responder

Правило `next`: 
- Для `UIView`: обычно `superview`; если `viewController` владеет этой view, следующим может быть `viewController`.
- Для `UIViewController`: обычно его `view` → затем `parent` VC → затем `UIWindow`.
- Для `UIWindow`: `UIApplication`.
- Для `UIApplication`: объект делегата приложения.

Цепь динамическая: меняется при изменении иерархии, окнах, presented VC, key window, First Responder.

---

## 4) First Responder

- Единственный активный объект, который первым получает ряда событий: клавиатурный ввод, меню/команды, текстовые действия.
- Управление: `becomeFirstResponder()`, `resignFirstResponder()`, `canBecomeFirstResponder`.
- Важен для маршрутизации `UIKeyCommand`, `UIMenu`, `sendAction(_:to:from:for:)` без явного таргета.

Практика: корректно реализуйте `canBecomeFirstResponder`, особенно в кастомных контролах и контейнерах.

---

## 5) Hit Testing и влияние на цепочку

Порядок:
1) Система выполняет hit-testing в активном окне: от корня к листьям.
2) Найденная самая глубокая view становится стартовой для touch/gesture.
3) Если жесты распознаны `UIGestureRecognizer`, они могут перехватить/отменить delivery touches в зависимости от `cancelsTouchesInView`, `delaysTouchesBegan/Ended`, приоритетов и delegate-правил.

Тюнинг hit-testing:
- Переопределение `point(inside:with:)`/`hitTest(_:with:)` для расширения/сужения активной области.
- Следите за `isUserInteractionEnabled`, `alpha < 0.01`, `isHidden` — они исключают view из hit-testing.

---

## 6) sendAction, target=nil и варианты маршрутизации

`UIApplication.shared.sendAction(_ action: Selector, to target: UIResponder?, from sender: Any?, for event: UIEvent?)`

- С `target != nil`: действие вызывается напрямую у таргета (если он реализует селектор). Responder chain не используется.
- С `target == nil`: система ищет обработчик вдоль responder chain, начиная с First Responder. Первый объект, у которого `canPerformAction(_:withSender:) == true` и есть реализация селектора, получит `action`.

Различия сценариев:
- Когда таргет задан: предсказуемость максимальная, гибкость минимальная.
- Когда таргет не задан: гибкость и слабая связность выше; поведение зависит от текущего First Responder/иерархии.

Use-cases target=nil:
- Глобальные действия (Undo/Redo, Copy/Paste, Find, Share) — меняются в зависимости от контекста.
- Команды меню/клавиатуры: `UIKeyCommand`, `UIMenuSystem`.
- Контейнеры, делегирующие действия дочерним контролам без жесткой зависимости.

---

## 7) canPerformAction и динамическая доступность команд

- Система опрашивает цепочку методом `canPerformAction(_:withSender:)` чтобы решить, кому и что показывать/активировать.
- Реализуйте у соответствующих объектов, учитывая контекст (выделение, режим редактирования, состояние модели).
- Для SwiftUI с `commands {}` и `focusedSceneValue`/`@FocusedValue` используется мост к responder chain.

---

## 8) Контроллеры, контейнеры и presented VCs

- При `present(_:animated:)` активным становится окно/presented сцена; цепочка может проходить через presented VC.
- Контейнеры (`UINavigationController`, `UITabBarController`, `UISplitViewController`) часто участвуют в цепи как промежуточные звенья: они могут перехватывать действия (например, навигационные команды) и делегировать вниз/вверх.
- Root VC окна и key window критичны: у кого “фокус” — туда придет событие первым.

---

## 9) UIKit и SwiftUI: мосты

- SwiftUI использует AppKit/UIKit под капотом. Фокус и команды SwiftUI (`.focused(...)`, `@FocusState`, `commands`) транслируются в механизмы responder chain.
- Для интеграции: `UIHostingController` участвует в цепочке как `UIViewController`.
- Кастомные действия в SwiftUI можно провалидировать/обработать через `commands` + `focusedSceneValue`, что концептуально отражает `canPerformAction`/First Responder.

---

## 10) Gesture Recognizers и приоритеты

- Конкуренция жестов влияет на то, кто станет обработчиком: `require(toFail:)`, `shouldRecognizeSimultaneouslyWith`, `shouldBeRequiredToFailBy`, `shouldReceive`.
- При отмене touches жестом (`cancelsTouchesInView = true`), исходные touch-события не дойдут до view по responder chain.
- Последовательность: touches → recognizers (began/changed/ended) → возможная отмена/форвардинг.

---

## 11) Key Commands, Menus, Editing

- `UIKeyCommand`: доставляется First Responder → вверх по цепочке. Регистрация возможна на уровне VC или view.
- `UIMenu`, `UIMenuController`: построение доступности через responder chain; динамическое включение пунктов через `canPerformAction`.
- Editing pipeline: текстовые контролы `UITextField`/`UITextView` становятся First Responder, цепочка обеспечивает Cut/Copy/Paste/Undo/Redo.

---

## 12) Диагностика и дебаг

- Временный override `next` у подозреваемых объектов (`override var next: UIResponder?`) для логирования цепочки.
- Логируйте `isFirstResponder` и путь от First Responder до `UIApplication`.
- Проверяйте hit-testing через `UIView`.draw(debug)/инспекторы, отключайте `userInteractionEnabled` у перекрывающих overlay.
- Для SwiftUI — валидация фокуса через `@FocusState` и проверка `commands`.

---

## 13) Архитектурные практики (Senior)

- Декларируйте намерения действия, а не конкретные получатели: `sendAction` с `target=nil` для контекстных команд; прямые таргеты — для локальных, не контекстных операций.
- Не ломайте цепочку излишними перехватами в контейнерах. Если контейнер обрабатывает действие — убедитесь, что это его зона ответственности.
- Минимизируйте переопределения `hitTest`/`point(inside:)` — это сильные рычаги; документируйте и покрывайте тестами.
- Избегайте утечек First Responder: корректно сбрасывайте фокус при уходе экранов.
- Для доступности: учитывайте, что VoiceOver также влияет на фокус и маршрутизацию.

---

## 14) Частые ловушки

- Невидимые/прозрачные views перекрывают клики и съедают события.
- Несогласованный `canBecomeFirstResponder` мешает key commands и меню.
- Несинхронизированный key window/scene — события попадают “не туда”.
- Жест с `cancelsTouchesInView=true` отменяет взаимодействие дочерних контролов неожиданно.
- Несоответствие `canPerformAction` и фактической реализации селектора приводит к недоступным/пустым пунктам меню.

---

## 15) Мини-FAQ

- Откуда система знает, кому отправить `copy:`? — Сначала First Responder, затем вверх по цепочке, спрашивая `canPerformAction`.
- Чем отличается таргетированная отправка от `target=nil`? — Первая минует цепочку, вторая использует ее для выбора получателя.
- Как посмотреть текущего First Responder? — Нет публичного API для прямого получения; используйте traversal с `sendAction` на кастомный селектор, который помечает себя.

---

## 16) Полезные сниппеты

См. отдельный файл со сниппетами: [Responder Chain — сниппеты](../Snippets/responder-chain.md).

---

## 17) Краткая шпаргалка

- Start точки: Hit-tested view или First Responder (в зависимости от типа события).
- Порядок `next`: `UIView` → `UIViewController` → `UIWindow` → `UIApplication` → App Delegate.
- `target=nil` включает цепочку, `target!=nil` минует ее.
- `canPerformAction` формирует доступность действий.
- Жесты могут перехватывать/отменять touch delivery.
- Следите за key window/scene и First Responder.


