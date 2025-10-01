---
title: Checklists
type: index
---

# Checklists

**Что это**: контрольные списки для релиза, ревью, оптимизации.

**Для чего**: ничего не забыть, стандартизировать качество.

**Содержимое**: чеклисты с пунктами, критериями готовности.

**Как пользоваться**: проходите список перед релизом/мерджем/демо.

```dataview
LIST
FROM "iOS/Checklists"
WHERE file.name != "Checklists" AND file.name != "README"
SORT file.name ASC
```
