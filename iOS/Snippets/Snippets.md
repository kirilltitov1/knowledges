---
title: Snippets
type: index
---

# Snippets

**Что это**: короткие фрагменты кода для повседневных задач.

**Для чего**: быстро вставить проверенный кусок без поиска.

**Содержимое**: однофайловые заметки с кратким описанием.

**Как пользоваться**: копируйте в проект, адаптируйте имена/типы.

```dataview
LIST
FROM "iOS/Snippets"
WHERE file.name != "Snippets" AND file.name != "README"
SORT file.name ASC
```
