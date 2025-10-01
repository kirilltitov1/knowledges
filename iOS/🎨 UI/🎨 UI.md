
```dataview
TABLE WITHOUT ID link(file.path, default(title, file.name)) AS "Заметка", default(subtopic, "misc") AS "Тема", type, status
FROM "iOS"
WHERE contains(topics, "UI") AND (type = "thread" OR type = "example" OR type = "antipattern")
FLATTEN default(subtopic, "misc") AS subtopic
SORT subtopic ASC, default(title, file.name) ASC
```
