---
title: Stack Frames в iOS/Swift — практический гайд
type: guide
topics: [Debugging, Low-Level, Memory]
subtopic: stack-frame
status: draft
level: intermediate
platforms: [iOS, macOS]
ios_min: "13.0"
duration: 45m
tags: [stack, frame, call-stack, lldb, async-await, arm64]
---

# Stack Frames в iOS/Swift — как это работает

Гайд о том, когда и как формируются stack frames, как они выглядят на ARM64, как на них влияют оптимизации и async/await, и как всё это дебажить через LLDB.

## Что такое stack frame

Stack frame (кадр стека) — участок стека текущего потока, описывающий один активный вызов функции: сохранённые регистры, локальные переменные, временные значения, метаданные вызова.

## Когда формируется кадр

- На входе в любую функцию/метод/инициализатор/деинициализатор (после пролога).
- При вызове замыкания — создаётся кадр для тела замыкания (захваты — в heap-контейнере closure, не в кадре).
- Рекурсия — один кадр на вызов.
- Ошибки (throw): обычные кадры; при unwind происходит раскрутка и вызов деструкторов.
- Tail call оптимизации — кадр может быть переиспользован, отдельный кадр не формируется.
- Inline — инлайнинг убирает отдельный кадр для инлайновой функции.
- Async/await — между await’ами кадра нет; состояние лежит в heap (async state machine). При resume создаётся новый кадр и восстанавливается состояние.

## ARM64: пролог/эпилог (упрощённо)

```asm
// Пролог
stp x29, x30, [sp, #-16]!   // сохранить frame pointer (x29) и return addr (x30) на стек
mov x29, sp                  // новый frame pointer
sub sp, sp, #localsSize      // выделить место под локальные переменные

// ... тело функции ...

// Эпилог
add sp, sp, #localsSize      // освободить локалы
ldp x29, x30, [sp], #16      // восстановить x29,x30 и убрать запись со стека
ret                          // возврат к вызывающему
```

Примечания:
- В релизе возможен frame pointer omission (FPO) и red zone — структура кадра упрощается, трасы хуже читаемы.
- Swift может класть небольшие временные на регистры (без стека).

## Структура кадра (логически)

- Saved LR/FP (x30/x29)
- Параметры (могут быть в регистрах)
- Локальные переменные, temporaries
- Spill регистров

Фактическая раскладка зависит от оптимизаций компилятора и ABI.

## Влияние Swift-фич

- Value types: чаще размещаются в регистрах/стеке (если маленькие), большие — в куче/через выделения.
- Классы: указатели на heap-объекты в кадре; сами объекты — в куче.
- Closures: контекст (захваты) — в куче; кадр только для тела.
- Error handling: таблицы unwind и вызовы деструкторов при раскрутке.
- Async/await: состояние функции сериализуется в heap-контекст; `await` разрывает непрерывность стека.

## LLDB: как исследовать

### Базовые команды

```bash
bt                      # показать стек вызовов
frame select N          # перейти к кадру N
frame info              # информация о кадре
frame variable          # локальные переменные текущего кадра
register read           # регистры (x29/x30/sp и др.)
thread backtrace all    # стеки всех потоков
```

### Просмотр адресов и памяти

```bash
p &variable             # адрес локальной переменной
memory read -s8 -c8 SP  # чтение памяти вокруг SP
```

### Async/await

```bash
thread backtrace        # стек обрывается на await
settings set target.swift-enable-task-names true  # имена задач
thread info             # ID задачи/актора
```

### Символы и оптимизации

```bash
image lookup -a 0xADDRESS   # найти символ по адресу
settings set target.inline-breakpoint-strategy always  # брейки внутри инлайна
```

## Практика: что смотреть при проблемах

- Странные краши в релизе: отключить FPO (dSYM, настроить компоновку), собрать с символами.
- Утечки и рост памяти: фиксировать call stack аллокаций (Instruments → Allocations), смотреть кто создаёт и не освобождает.
- Recursion/stack overflow: `bt` покажет повторяющиеся кадры; оценить глубину.
- Async баги: понимать, что stack frame между await не сохраняется — искать state machine и точки resume.

## Связанные материалы

- `iOS/Debugging/xcode-debugger-lldb.md` — базовые команды LLDB
- `iOS/Performance & Profiling/instruments-guide.md` — Allocations/Leaks, работа с call stacks
- `iOS/Swift Language/swift-memory-structure-cheat-sheet.md` — память Swift, heap-объекты и ARC

## Чеклист

- Есть ли frame pointer (x29) и корректная цепочка кадров?
- Не «съелся» ли кадр из‑за inlining/tail call?
- Нет ли раскрутки (unwind) по исключению?
- Не разорван ли стек из‑за await?
- Символы/декорации загружены? dSYM на месте?
