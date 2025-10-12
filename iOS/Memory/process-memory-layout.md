---
type: "guide"
status: "draft"
level: "intermediate"
title: "Process Memory Layout"
---

# Разметка памяти процесса в iOS (ARM64)

Краткий справочник по сегментам виртуальной памяти процесса, их назначению и где «живут» сущности Swift.

## Схема (логическая)

Высокие адреса → Kernel Space

┌───────────────────────────────┐
│ Kernel Space                  │
├───────────────────────────────┤
│ Stack (per-thread, ↓ растёт)  │
├───────────────────────────────┤
│ Heap (динамика, ↑ растёт)     │
├───────────────────────────────┤
│ Data Segment                  │
├───────────────────────────────┤
│ Code/Text Segment             │
└───────────────────────────────┘
Низкие адреса

Примечание: рост «вверх/вниз» — концепция; фактически управляет VM.

## Code/Text Segment

- Машинные инструкции (ROX: read+execute, без записи).
- Mach-O: `__TEXT` (`__text`, `__stubs`, `__cstring`, `__const`).
- Может шариться из dyld shared cache.

## Data Segment

- Глобальные/статические переменные:
  - Инициализированные (RW): `__DATA`, `__DATA_DIRTY`.
  - Неинициализированные (BSS, нули при старте).
  - Константные (RO): `__DATA_CONST` или `__TEXT,__const`.
- TLS‑секции для thread‑local данных.

## Heap (Куча)

- Динамические выделения: `malloc/new`, Swift‑объекты (классы), COW‑буферы коллекций, контексты замыканий, структуры задач/акторов, weak‑таблицы и пр.
- Управляется аллокатором (страницы/зоны), возможна фрагментация.
- Страницы обычно RW; свободные могут возвращаться ядру.

## Stack (Стек)

- Отдельно на каждый поток; guard‑страницы для обнаружения overflow.
- Кадры функций: адрес возврата (LR), frame pointer (FP), локальные переменные, spill регистров, параметры.
- При `async/await` стек между await‑точками может отличаться; состояние функции хранится в heap‑continuation.

## Kernel Space

- Память ядра ОС, недоступна из user‑mode.

## Swift‑специфика

- Классы/объекты: в куче, заголовок (metadata/isa, refCounts) + свойства.
- Структуры: чаще в регистрах/на стеке; большие/с COW — с heap‑буферами.
- Константы (строки/литералы): RO‑секции (`__TEXT,__cstring`/`__const`).
- Глобальные `var/static`: `__DATA`/`__DATA_DIRTY`.
- Метаданные типов/таблицы свидетелей: в образе (`__TEXT`/`__DATA_CONST`).
- TLS: хранит указатель на текущую Task; сами Task‑locals — в задаче (heap).

## Диагностика

- LLDB `vmmap <pid>` — карта регионов: `__TEXT`, `__DATA*`, `MALLOC`, `STACK`, `__LINKEDIT`, shared cache.
- Instruments → Allocations/Leaks — кто аллоцирует (heap), call stacks.
- LLDB: `bt`, `frame variable`, `memory read` для анализа стека/памяти.

## Ссылки

- Mach-O Runtime Layout (Apple docs)
- `vmmap` man page
- Swift Runtime internals (swift.org)
