# Playbooks

## 📋 Главные playbooks

- [[system-design-interview-framework|System Design Interview Framework]] — структурированный подход к решению задач системного дизайна на интервью
- [[system-design-cheat-sheet|System Design Cheat Sheet]] — краткая шпаргалка-памятка на одну страницу

---

## 🔍 Автоматический список

```dataviewjs
const pages = dv.pages('"iOS/Playbooks"')
    .where(p => p.file.name !== "Playbooks");

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
