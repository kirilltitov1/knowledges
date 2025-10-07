# System Design — что хранится в этом разделе

Этот раздел — точка входа для материалов по системному дизайну в контексте мобильных (iOS) и связанных backend‑интеграций. Здесь лежат фреймворки, доменные под‑разделы (чат, e‑commerce, медиа, соцсети), мини‑дизайны и конспекты.

## Зачем
- Быстро подготовиться к интервью по System Design
- Иметь повторяемую структуру рассуждений (FR/NFR → оценки → HLD → deep dive → SLI/SLO → trade‑offs)
- Хранить доменные заготовки и мини‑кейсы для отработки

## Как пользоваться
1. Открой [[Templates/System Design|универсальный шаблон]] или соответствующий доменный шаблон из `Templates/`.
2. Заполни блоки: цели → FR/NFR → оценки (QPS, storage, bandwidth) → HLD (диаграмма/потоки) → deep dive по 1–2 компонентам → SLI/SLO/бюджет ошибок → риски.
3. При необходимости открой соседние разделы: мини‑дизайны, доменные заметки, плейбуки.

## Быстрые ссылки
- Фреймворк: [[Playbooks/system-design-interview-framework]] · Шпаргалка: [[Playbooks/system-design-cheat-sheet]]
- Шаблоны: 
  - [[Templates/System Design|Универсальный]]
  - [[Templates/System Design — Chat & RTC]]
  - [[Templates/System Design — E-commerce & Booking]]
  - [[Templates/System Design — Media Streaming]]
  - [[Templates/System Design — Social Feed]]
- Под‑разделы:
  - [[iOS/Architecture/System Design/Чат и RTC/Чат и RTC]]
  - [[iOS/Architecture/System Design/E-commerce и бронирование/E-commerce и бронирование]]
  - [[iOS/Architecture/System Design/Файлы и медиа/Файлы и медиа]]
  - [[iOS/Architecture/System Design/Соцсети и контент/Соцсети и контент]]
  - [[iOS/Architecture/System Design/Мини-дизайны/Мини-дизайны]]

## Что сюда складывать
- Обзорные материалы, чеклисты, ссылки на доменные разделы
- Универсальные приёмы: ретраи/идемпотентность, кеш, пагинация, безопасность
- Методички по оценкам нагрузки и мониторингу


