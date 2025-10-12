---
type: "thread"
topics:
  - Swift Language
  - Performance
  - ABI StabilitySwift Language", "Performance", "ABI Stability"]"
status: "done"
summary: "Атрибут @frozen для гарантии стабильности структуры типа и оптимизации производительности"
title: "Frozen Attribute"
---

## Заключение

**Ключевые takeaways:**

1. `@frozen` = жесткий ABI contract + прямой доступ к памяти + производительность
2. Используйте для стабильных типов (Point, Color, Result)
3. НЕ используйте для эволюционирующих типов (User, APIResponse)
4. В Swift stdlib большинство базовых типов `@frozen`
5. @frozen + @inlinable = максимальная оптимизация
6. Изменение @frozen типа = breaking change = нужна major версия

**Правило большого пальца:**
> Если сомневаетесь — НЕ используйте @frozen. Resilient по умолчанию безопаснее. @frozen только для типов, в стабильности которых вы на 100% уверены.

