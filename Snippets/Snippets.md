---
title: Snippets
type: index
topics: [iOS]
subtopic: snippets
status: draft
---

# Snippets

- [Responder Chain (UI)](../iOS/Snippets/responder-chain.md)

```dataviewjs
const pages = dv.pages('"iOS/Snippets"')
    .where(p => p.file.name !== "Snippets");

// Группируем по subtopic
const grouped = pages.groupBy(p => p.subtopic || "Разное");

// Сортируем группы
const sortedGroups = grouped.sort(g => g.key);

// Выводим каждую группу
for (let group of sortedGroups) {
    dv.header(3, group.key);
    dv.list(group.rows
        .sort(p => p.title || p.file.name)
        .map(p => dv.fileLink(p.file.path, false, p.title || p.file.name))
    );
}
```
