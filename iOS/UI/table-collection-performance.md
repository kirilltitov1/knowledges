---
type: "thread"
status: "draft"
summary: ""
title: "Table Collection Performance"
---

# UITableView/UICollectionView — Оптимизация производительности (Senior++)

## TL;DR чек‑лист
- Оставляйте главный поток свободным: декодирование изображений, измерение текста, форматирование — вне main.
- Минимизируйте иерархию вью и работу в `cellFor…`; используйте кэш размеров и предварительную конфигурацию.
- Применяйте `Diffable Data Source` и `reconfigureItems` вместо массового `reloadData`.
- Включайте prefetching (`UITableViewDataSourcePrefetching`/`UICollectionViewDataSourcePrefetching`) и отмену в `prepareForReuse`.
- Изображения: `UIImage.byPreparingThumbnail(of:)` и `byPreparingForDisplay()`; строгая отмена; `NSCache`.
- Диагностика — Instruments: Time Profiler, Core Animation (FPS/offscreen/blended), Allocations, System Trace/Hitches; в проде — MetricKit.
- Эффекты — избегайте offscreen rendering; `shadowPath`, `isOpaque`, осторожно с блюрами. `shouldRasterize` — крайне точечно.
- Очень большие поверхности — `CATiledLayer`; для обычных списков не нужен.

## 1) База: где теряем кадры
- 16.67 мс/кадр при 60 FPS — бюджет на лейаут, конфиг, рисование, декодирование, аллокации.
- CPU‑узкие места: авто‑лейаут, измерение/форматирование текста, диффы, декодирование изображений.
- GPU‑узкие места: прозрачные слои (blended), offscreen rendering (тени/маски/скругления), эффекты.
- Главная цель — убрать тяжёлую работу из критического пути кадра, сгладить «пилу», снизить аллокации.

## 2) Данные и обновления: Diffable Data Source
- `UICollectionViewDiffableDataSource`/`UITableViewDiffableDataSource` создаёт минимальные диффы, уменьшает инвалидацию и скачки FPS.
- Идентификаторы должны быть стабильными (Hashable). Снимки собирайте в фоне; `apply(snapshot,…)` — на main.
- Точечные обновления:
  - `reconfigureItems([id])` — обновляет конфигурацию без полной перезагрузки ячейки.
  - `reloadItems` — тяжелее: инвалидация лейаута/пересоздание.
- Троттлинг изменений: коалесируйте частые микроправки в один snapshot.

```swift
var snapshot = NSDiffableDataSourceSnapshot<Section, Item>()
// ... наполняем в фоне ...
await MainActor.run {
  dataSource.apply(snapshot, animatingDifferences: true)
}
```

## 3) Лейаут и конфигурация ячеек
- Уплощайте иерархию: меньше сабвью — дешевле измерение и рисование.
- Для коллекций — `CompositionalLayout` + `CellRegistration` + `UIListContentConfiguration` как хороший baseline.
- Self‑sizing:
  - Таблица: `estimatedRowHeight` + кэш высот (ключ: `itemID + widthClass`).
  - Коллекция: избегайте повсеместного `.automaticSize` у `flowLayout`; при необходимости — кэш атрибутов.
- Текст:
  - Кэшируйте `NSAttributedString` и результаты измерений.
  - Для многострочного `UILabel` задавайте `preferredMaxLayoutWidth`.
- Инвалидируйте лейаут только там, где нужно (секция/элемент), не глобально.

## 4) Изображения: декодирование, масштабирование, кэш
- Никогда не декодируйте/ресайзьте на main. Новые API:
  - `UIImage.byPreparingThumbnail(of:)` — дешёвое создание миниатюры с декодированием.
  - `UIImage.byPreparingForDisplay()` — предварительная декомпрессия перед показом.
```swift
Task.detached(priority: .utility) {
  let thumb = await image.byPreparingThumbnail(of: CGSize(width: 200, height: 200))
  let display = await thumb?.byPreparingForDisplay()
  await MainActor.run { cell.imageView.image = display }
}
```
- Свой `NSCache<Key, UIImage>` с политикой инвалидации.
- Отменяйте загрузку/декодирование в `prepareForReuse` (храните `Task`/`Operation` в ячейке и отменяйте).
- Масштабируйте заранее; избегайте повторного ресайза одного и того же `UIImage` в скролле.
- Большие изображения/PDF c zoom — `CATiledLayer`.

## 5) Prefetching и отмена
```swift
final class DS: NSObject, UITableViewDataSourcePrefetching {
  func tableView(_ tv: UITableView, prefetchRowsAt indexPaths: [IndexPath]) { /* start work */ }
  func tableView(_ tv: UITableView, cancelPrefetchingForRowsAt indexPaths: [IndexPath]) { /* cancel */ }
}
```
- Для коллекций — `UICollectionViewDataSourcePrefetching`.
- Держите «окно предзагрузки» разумным, отменяйте невидимое.

## 6) Эффекты, слои и offscreen rendering
- Offscreen триггеры: тени + `masksToBounds`, скругления с масками, сложные блюры/вибранси.
  - Тени: обязательно `layer.shadowPath`.
  - Скругления: по возможности рисуйте фон заранее со скруглениями.
  - Прозрачность: `isOpaque = true`, непрозрачный `backgroundColor`.
- `shouldRasterize` — кеширование снимка слоя в памяти для повторного использования.
  - Подходит только для статичных, дорогих поддеревьев; ставьте `rasterizationScale`.
  - Не подходит для динамичных ячеек списков — контент часто меняется, снимок инвалидируется и ест память.
```swift
layer.shouldRasterize = true
layer.rasterizationScale = UIScreen.main.scale
```

## 7) `CATiledLayer`
- Для гигантских поверхностей (большие изображения, PDF, карты) с zoom — рендер по тайлам.
- Для обычных списков избыточно; используйте миниатюры/кэш.

## 8) Жизненный цикл ячейки
- Минимизируйте работу в `cellFor…` и `prepareForReuse`.
- В `prepareForReuse`: отмена задач, сброс состояния без тяжёлой логики.
- Не дергайте сеть из `cellFor…`; используйте prefetch/репозиторий с кэшем.

## 9) Компос‑лейаут и особенности коллекций
- `CompositionalLayout` даёт прогнозирование атрибутов, `visibleItemsInvalidationHandler` для дешёвых реакций на скролл.
- Горизонтальные карусели (`orthogonalScrollingBehavior`) — следите за вложенным скроллом и числом одновременно видимых ячеек.

## 10) Диагностика и узкие места
- Instruments:
  - Time Profiler — горячие точки (`cellFor…`, форматирование, атрибуты текста, декодирование изображений, JSON→модели).
  - Core Animation — FPS, цветовые оверлеи Blended/Offscreen.
  - Allocations — аллокации, «шум» от Auto Layout/атрибутов.
  - System Trace / Animation Hitches — фиксация hitch‑ей и причин пропусков кадров.
- Xcode Runtime Rendering: Color Blended Layers/Offscreen Rendered, Performance HUD, индикатор `Animation Hitches`.
- MetricKit (прод): `MXAnimationMetrics`, `MXScrollMetrics` — hitch time ratio, средний FPS.
- Своя телеметрия: `os_signpost` вокруг конфигурации ячейки, декодирования, построения snapshot.

## 11) Рецепты безопасных обновлений
- Быстрые изменения внутри ячейки → `reconfigureItems` вместо `reloadItems`.
- Избегайте `reloadData` под скроллом; для массовых изменений — один дифф без анимаций.
- Обновляйте только видимые `indexPath`; невидимое — отложить до prefetch.

## 12) Антипаттерны
- Синхронное I/O/декодирование в `cellFor…`.
- Многократные `reloadData` подряд.
- Глубокие иерархии вью + тяжёлый Auto Layout без кэша.
- Стек блюров; тени без `shadowPath`; `shouldRasterize` на ячейках.
- Отсутствие отмены задач в `prepareForReuse`.

## 13) Мини‑сниппеты

Diffable и точечные апдейты:
```swift
dataSource.apply(snapshot, animatingDifferences: true)
dataSource.reconfigureItems([changedID])
```

Отмена задач в ячейке:
```swift
final class ImageCell: UICollectionViewCell {
  private var task: Task<Void, Never>?
  override func prepareForReuse() {
    super.prepareForReuse()
    task?.cancel()
    imageView.image = nil
  }
  func configure(with image: UIImage) {
    task = Task.detached(priority: .utility) {
      let prepared = await image.byPreparingForDisplay()
      if Task.isCancelled { return }
      await MainActor.run { self.imageView.image = prepared }
    }
  }
}
```

Тени без offscreen:
```swift
let path = UIBezierPath(roundedRect: bounds, cornerRadius: 12).cgPath
layer.shadowPath = path
layer.shadowOpacity = 0.25
```

## 14) Пошаговая диагностика (workflow)
1. Воспроизведите лаг под скроллом → Core Animation (FPS/hitches), Time Profiler.
2. Включите blended/offscreen оверлеи → исправьте `opaque`, тени, слои.
3. Вынесите тяжёлые операции off‑main: изображения, текст, форматирование.
4. Включите prefetch+отмену, добавьте кэши (высоты/атрибуты/картинки).
5. Перейдите на диффы и `reconfigureItems` вместо `reloadData`.
6. Упростите иерархию вью и стабилизируйте лейаут.
7. В проде проверьте MetricKit: hitch ratio и метрики скролла.


