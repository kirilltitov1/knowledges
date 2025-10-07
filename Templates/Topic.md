---
title: <% tp.file.title %>
type: topic
topics: [<% tp.file.title %>]
---

# <% tp.file.title %>

## 📚 Теория
Краткий конспект основных идей и понятий.

## 💻 Примеры
```dataview
TABLE file.link AS "Пример", status, ios_min
FROM "iOS/Examples"
WHERE contains(topics, "<% tp.file.title %>")
SORT file.name ASC
```

## ⚠️ Антипаттерны
```dataview
LIST
FROM "iOS/Antipatterns"
WHERE contains(topics, "<% tp.file.title %>")
```

## 🔗 Связанные темы
- 
