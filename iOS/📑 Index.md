# 📑 Index - Индекс всех заметок

Автоматически сгенерированный индекс всех заметок в базе знаний.

> **⚡ Быстрый доступ:** [[📥 Inbox]] - для быстрой записи новых идей

---

## 📚 По темам (Topics)

```dataviewjs
const pages = dv.pages('"iOS"')
    .where(p => p.topics && !p.file.path.includes("Templates"));

// Собираем все уникальные темы
const allTopics = new Set();
pages.forEach(p => {
    if (Array.isArray(p.topics)) {
        p.topics.forEach(t => allTopics.add(t));
    } else if (p.topics) {
        allTopics.add(p.topics);
    }
});

// Сортируем темы
const sortedTopics = Array.from(allTopics).sort();

// Выводим каждую тему с заметками
for (let topic of sortedTopics) {
    dv.header(3, topic);
    
    const topicPages = pages
        .where(p => {
            if (Array.isArray(p.topics)) {
                return p.topics.includes(topic);
            }
            return p.topics === topic;
        })
        .sort(p => p.file.name);
    
    dv.list(topicPages.map(p => 
        dv.fileLink(p.file.path, false, p.title || p.file.name)
    ));
}
```

---

## 🏷️ По подтемам (Subtopics)

```dataviewjs
const pages = dv.pages('"iOS"')
    .where(p => p.subtopic && !p.file.path.includes("Templates"));

// Группируем по subtopic
const grouped = pages.groupBy(p => p.subtopic);

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

---

## 📝 По типу (Type)

```dataviewjs
const pages = dv.pages('"iOS"')
    .where(p => p.type && !p.file.path.includes("Templates"));

// Группируем по type
const grouped = pages.groupBy(p => p.type);

// Определяем порядок и иконки
const typeOrder = {
    'thread': { order: 1, icon: '📝', name: 'Thread - Основные заметки' },
    'example': { order: 2, icon: '💡', name: 'Example - Примеры кода' },
    'antipattern': { order: 3, icon: '⚠️', name: 'Antipattern - Антипаттерны' },
    'checklist': { order: 4, icon: '✅', name: 'Checklist - Чеклисты' },
    'snippet': { order: 5, icon: '🔧', name: 'Snippet - Сниппеты' },
};

// Сортируем группы
const sortedGroups = grouped.sort(g => typeOrder[g.key]?.order || 99);

// Выводим каждую группу
for (let group of sortedGroups) {
    const typeInfo = typeOrder[group.key] || { icon: '📄', name: group.key };
    dv.header(3, `${typeInfo.icon} ${typeInfo.name}`);
    
    dv.list(group.rows
        .sort(p => p.title || p.file.name)
        .map(p => dv.fileLink(p.file.path, false, p.title || p.file.name))
    );
}
```

---

## 🚦 По статусу (Status)

```dataviewjs
const pages = dv.pages('"iOS"')
    .where(p => p.status && !p.file.path.includes("Templates"));

// Группируем по status
const grouped = pages.groupBy(p => p.status);

// Определяем порядок и иконки
const statusOrder = {
    'draft': { order: 1, icon: '📝', name: 'Draft - Черновик' },
    'in-progress': { order: 2, icon: '🚧', name: 'In Progress - В работе' },
    'review': { order: 3, icon: '👀', name: 'Review - На проверке' },
    'done': { order: 4, icon: '✅', name: 'Done - Готово' },
    'archived': { order: 5, icon: '📦', name: 'Archived - В архиве' },
};

// Сортируем группы
const sortedGroups = grouped.sort(g => statusOrder[g.key]?.order || 99);

// Выводим каждую группу
for (let group of sortedGroups) {
    const statusInfo = statusOrder[group.key] || { icon: '❓', name: group.key };
    dv.header(3, `${statusInfo.icon} ${statusInfo.name} (${group.rows.length})`);
    
    dv.list(group.rows
        .sort(p => p.title || p.file.name)
        .map(p => dv.fileLink(p.file.path, false, p.title || p.file.name))
    );
}
```

---

## 📊 Статистика

```dataviewjs
const pages = dv.pages('"iOS"')
    .where(p => !p.file.path.includes("Templates"));

const stats = {
    total: pages.length,
    byType: {},
    byStatus: {},
    byTopic: {},
    withTitle: pages.where(p => p.title).length,
    withSubtopic: pages.where(p => p.subtopic).length,
};

// Считаем по типам
pages.forEach(p => {
    if (p.type) {
        stats.byType[p.type] = (stats.byType[p.type] || 0) + 1;
    }
    if (p.status) {
        stats.byStatus[p.status] = (stats.byStatus[p.status] || 0) + 1;
    }
    if (p.topics) {
        const topics = Array.isArray(p.topics) ? p.topics : [p.topics];
        topics.forEach(t => {
            stats.byTopic[t] = (stats.byTopic[t] || 0) + 1;
        });
    }
});

dv.header(3, "Общая статистика");
dv.list([
    `**Всего заметок:** ${stats.total}`,
    `**С заголовками:** ${stats.withTitle}`,
    `**С подтемами:** ${stats.withSubtopic}`,
]);

dv.header(4, "По типам:");
dv.list(Object.entries(stats.byType)
    .sort((a, b) => b[1] - a[1])
    .map(([type, count]) => `**${type}**: ${count}`)
);

dv.header(4, "По статусам:");
dv.list(Object.entries(stats.byStatus)
    .sort((a, b) => b[1] - a[1])
    .map(([status, count]) => `**${status}**: ${count}`)
);

dv.header(4, "По темам:");
dv.list(Object.entries(stats.byTopic)
    .sort((a, b) => b[1] - a[1])
    .map(([topic, count]) => `**${topic}**: ${count}`)
);
```

---

## 🔍 Полный список заметок

```dataview
TABLE WITHOUT ID
  link(file.path, default(title, file.name)) AS "Заметка",
  default(type, "-") AS "Тип",
  default(subtopic, "-") AS "Подтема",
  default(status, "-") AS "Статус"
FROM "iOS"
WHERE file.name != "📑 Index" AND !contains(file.path, "Templates")
SORT default(subtopic, "zzz") ASC, default(title, file.name) ASC
```

