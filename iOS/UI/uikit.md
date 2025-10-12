---
type: "thread"
status: "draft"
summary: ""
title: "uikit"
---

# UIKit

### View Controllers
- UIViewController lifecycle
  - `init(coder:)` или `init(nibName:bundle:)` 
  - `loadView()`
  - `viewDidLoad()`
  - `viewWillAppear(_:)`
  - `viewDidAppear(_:)`
  - `viewWillDisappear(_:)`
  - `viewDidDisappear(_:)`
  - Вспомогательные методы
    `viewWillLayoutSubviews():` Вызывается перед тем, как layoutSubviews() будет вызван на view.
    `viewDidLayoutSubviews():` Вызывается после того, как subviews были перестроены. Используется для выполнения любых дополнительных настроек после размещения subviews.
- Navigation
  - UINavigationController
  - Push/Pop
  - Custom transitions
- Presentation
  - Modal presentation styles
  - Presentation controllers
  - Custom presentations

### Auto Layout & Constraints
- NSLayoutConstraint
- Visual Format Language
- Layout Anchors
- Constraint priorities
- Content Hugging & Compression Resistance
- Intrinsic content size
- Safe Area
- Layout Margins
- Stack Views (UIStackView)

### UITableView
- Data source & Delegate
- Cell reuse
- Custom cells
- Section headers/footers
- Editing mode
- Swipe actions
- Diffable Data Source (iOS 13+)

### UICollectionView
- Flow Layout
- Custom layouts
- Compositional Layout (iOS 13+)
- Diffable Data Source
- Cell registration
- Supplementary views
- Decoration views

### Custom Views
- Subclassing UIView
- `draw(_:)` method
- `layoutSubviews()`
- `intrinsicContentSize`
- `sizeThatFits(_:)`
- Hit testing

### Gestures
- UITapGestureRecognizer
- UISwipeGestureRecognizer
- UIPanGestureRecognizer
- UIPinchGestureRecognizer
- UIRotationGestureRecognizer
- UILongPressGestureRecognizer
- Custom gesture recognizers

### Controls
- UIButton
- UITextField
- UITextView
- UISwitch
- UISlider
- UISegmentedControl
- UIDatePicker
- UIPickerView

### Responder Chain
- [Responder Chain — гайд](responder-chain.md)
- [Responder Chain — сниппеты](../Snippets/responder-chain.md)

## Вопросы собеседований
- Какие есть методы, которые участвуют в процессе layout view?
- Вопрос про view с примером.
- В каком методе жизненного цикла UIViewController’а раньше всего будут известный размеры view?

