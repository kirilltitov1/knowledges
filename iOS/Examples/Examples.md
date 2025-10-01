---
title: Examples
type: index
---

# Examples

**Что это**: коллекция полноценных и минимальных примеров кода.

**Для чего**: быстро вспомнить подход, показать коллеге/на собеседовании, стартовать от эталона.

**Содержимое**: подпапки по доменам (networking, architecture, concurrency, ui, persistence и т.д.). В крупных кейсах — мини Xcode проекты.

**Как пользоваться**: открывайте нужный пример, читайте `README.md`, запускайте проект или копируйте сниппеты.

```dataview
LIST
FROM "iOS/Examples"
WHERE file.name != "Examples" AND file.name != "README"
SORT file.name ASC
```
