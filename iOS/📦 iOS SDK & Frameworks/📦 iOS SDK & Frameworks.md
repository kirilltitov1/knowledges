# 📦 iOS SDK & Frameworks

```dataviewjs
const pages = dv.pages('"iOS/📦 iOS SDK & Frameworks"')
    .where(p => p.file.name !== "📦 iOS SDK & Frameworks");

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

