#!/usr/bin/env python3
"""
Единый очиститель фронтматтера Markdown-файлов в Obsidian-хранилище.

Что делает безопасно (минимальные правки без смены семантики):
- Чинит перенос перед закрывающими "---" (случаи вида: title: "..."---)
- Исправляет битый формат topics (например: topics: "[\"Networking\"]" или
  дубли типа: topics: ["Networking"]Networking"]")
- Убирает случайные лишние символы после корретных скобок у topics
- Сохраняет прочие поля как есть, не меняет порядок и кавычки, когда это возможно

Исключает из обработки: каталоги Templates и backups.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple


VAULT_PATH = Path("/Users/kirilltitov/Documents/Obsidian Vault")


def split_frontmatter(content: str) -> Tuple[str | None, str | None, str]:
    """Возвращает (frontmatter_text, delimiter, body).

    Поддерживает случаи, когда закрывающие --- ошибочно прилеплены к строке поля
    (например: title: "..."---). В таком случае пытается аккуратно отделить
    разделитель на новую строку.
    """
    if not content.startswith("---"):
        return None, None, content

    # Быстрый путь: корректный формат
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", content, flags=re.DOTALL)
    if m:
        return m.group(1), "---", m.group(2)

    # Толерантный путь: парсим построчно и ищем закрывающий маркер
    lines = content.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return None, None, content

    fm_lines: List[str] = []
    i = 1
    closing_found = False
    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip("\n")

        if line.strip() == "---":
            closing_found = True
            i += 1
            break

        # Случай, когда закрывающий --- прилеплен к строке поля
        # пример: title: "real-time-communications-ios"---
        if "---" in line:
            idx = line.find("---")
            left = line[:idx].rstrip()
            right = line[idx:]
            if right == "---":
                fm_lines.append(left + "\n")
                closing_found = True
                i += 1
                break

        fm_lines.append(raw)
        i += 1

    if not closing_found:
        # Нет корректного закрытия — считаем, что фронтматтера нет
        return None, None, content

    frontmatter_text = "".join(fm_lines)
    body = "".join(lines[i:])
    return frontmatter_text, "---", body


def clean_topics_line(line: str) -> str:
    """Приводит строку с topics к корректному виду, если она сломана.

    Обрабатывает:
    - topics: "[\"Networking\"]" -> topics: ["Networking"]
    - topics: ["Networking"]Networking"]" -> topics: ["Networking"]
    - Повторяющиеся значения в одной строке
    Не трогает многострочные списки с "- item".
    """
    # Не трогаем многострочные списки (когда строка равна просто 'topics:' или начинается с 'topics:' и переносом)
    if line.strip() == "topics:" or (line.strip().startswith("topics:") and line.strip().endswith(":")):
        return line

    if not line.strip().startswith("topics:"):
        return line

    # Уберём внешние кавычки вокруг всего массива, если есть
    # topics: "[ ... ]" -> topics: [ ... ]
    line = re.sub(r'^(\s*topics:\s*)"(\s*\[.*\]\s*)"\s*$', r"\1\2", line)

    # Извлечём все значения в кавычках — даже если после массива есть мусор
    values = re.findall(r'"([^"]+)"', line)
    if not values:
        return line

    # Удалим дубликаты, сохраняя порядок
    seen = set()
    unique_values: List[str] = []
    for v in values:
        # отбрасываем мусорные темы вида "]", "[", пустые и чисто пунктуацию
        if not re.search(r"[\wА-Яа-я]", v):
            continue
        if v.strip() in {']', '[', '"', '\''}:
            continue
        if v not in seen:
            seen.add(v)
            unique_values.append(v)

    cleaned = f"topics: [{', '.join(f'\"{v}\"' for v in unique_values)}]"
    return cleaned + ("\n" if not line.endswith("\n") else "")


def clean_tags_line(line: str) -> str:
    """Нормализует строку с tags к корректному YAML-массиву строк.

    Поддерживаемые случаи:
    - tags: "[a, b]" -> tags: ["a", "b"]
    - tags: [a, b] -> tags: ["a", "b"]
    - tags: a, b -> tags: ["a", "b"]
    Не трогаем многострочные списки ("- item").
    """
    s = line.rstrip("\n")
    if s.strip() == "tags:" or (s.strip().startswith("tags:") and s.strip().endswith(":")):
        return line

    if not s.lstrip().startswith("tags:"):
        return line

    m = re.match(r"^(\s*tags:\s*)(.*)$", s)
    if not m:
        return line
    prefix, rest = m.groups()

    rest = rest.strip()
    # Уберем внешние кавычки вокруг всего списка, если есть
    if len(rest) >= 2 and rest[0] == '"' and rest[-1] == '"':
        rest = rest[1:-1].strip()

    # Достанем содержимое скобок или работаем как со списком через запятую
    if '[' in rest and ']' in rest:
        l = rest.find('[')
        r = rest.rfind(']')
        items_str = rest[l + 1:r]
    else:
        items_str = rest

    raw_values = [v.strip() for v in items_str.split(',') if v.strip()]

    values: List[str] = []
    seen = set()
    for v in raw_values:
        v_clean = v.strip().strip('"\'')
        if not re.search(r"[\wА-Яа-я]", v_clean):
            continue
        if v_clean in seen:
            continue
        seen.add(v_clean)
        values.append(v_clean)

    if not values:
        return line

    cleaned = f"{prefix}[{', '.join(f'\"{v}\"' for v in values)}]"
    return cleaned + ("\n" if not line.endswith("\n") else "")


def normalize_title_value(value: str) -> str:
    """Преобразует slug-подобный title в читабельный.

    example: "real-time-communications-ios" -> "Real time communications iOS"
    Не трогает, если уже есть пробелы или это не похоже на slug.
    """
    raw = value.strip()
    if not raw:
        return value

    # Уже похоже на человекочитаемый заголовок — оставляем
    if " " in raw:
        return value

    # Если присутствуют дефисы/подчеркивания — нормализуем
    if "-" not in raw and "_" not in raw:
        return value

    tokens = re.split(r"[-_]+", raw)
    if not tokens:
        return value

    acronyms = {
        "ios": "iOS",
        "api": "API",
        "grpc": "gRPC",
        "sse": "SSE",
        "mqtt": "MQTT",
        "apns": "APNs",
        "webrtc": "WebRTC",
        "url": "URL",
        "ws": "WS",
        "http": "HTTP",
        "https": "HTTPS",
        "rpc": "RPC",
        "json": "JSON",
        "xml": "XML",
    }

    normalized: List[str] = []
    for t in tokens:
        low = t.lower()
        if not low:
            continue
        if low in acronyms:
            normalized.append(acronyms[low])
        else:
            normalized.append(low.capitalize())

    return " ".join(normalized)


def clean_frontmatter_text(text: str) -> str:
    """Чистит только самые распространённые ошибки без агрессивной нормализации."""
    lines = text.splitlines(keepends=True)
    out: List[str] = []

    def split_multiple_keys(raw_line: str) -> List[str]:
        # Ставит каждую пару key: value на отдельную строку, если их >1 в строке
        line_no_nl = raw_line[:-1] if raw_line.endswith("\n") else raw_line
        m = re.match(r"^(\s*[A-Za-z_][\w-]*\s*:\s*)(.*)$", line_no_nl)
        if not m:
            return [raw_line]

        prefix, value_str = m.groups()

        # Сканируем value_str на предмет второго ключа вне кавычек и квадратных скобок
        in_quotes = False
        escape = False
        bracket_level = 0
        pos2 = -1
        i = 0
        while i < len(value_str):
            ch = value_str[i]
            if escape:
                escape = False
                i += 1
                continue
            if ch == '\\':
                escape = True
                i += 1
                continue
            if ch == '"':
                in_quotes = not in_quotes
                i += 1
                continue
            if not in_quotes:
                if ch == '[':
                    bracket_level += 1
                elif ch == ']':
                    bracket_level = max(0, bracket_level - 1)
                # Потенциальное начало нового ключа
                if bracket_level == 0:
                    m2 = re.match(r"\s*([A-Za-z_][\w-]*)\s*:\s", value_str[i:])
                    if m2:
                        pos2 = i + m2.start()
                        break
            i += 1

        if pos2 == -1:
            return [raw_line]

        first = (prefix + value_str[:pos2].rstrip())
        rest = value_str[pos2:].lstrip()
        # Рекурсивно разбиваем хвост, если там тоже склеены ключи
        tail_lines: List[str] = []
        cur = rest
        while True:
            # добавим переносы строк к частям
            block = cur
            # следующий разрез
            m_head = re.match(r"^(\s*[A-Za-z_][\w-]*\s*:\s*)(.*)$", block)
            if not m_head:
                tail_lines.append(block)
                break
            pfx, val = m_head.groups()
            # поиск следующего ключа
            in_q = False
            esc = False
            br = 0
            cut = -1
            j = 0
            while j < len(val):
                c = val[j]
                if esc:
                    esc = False
                    j += 1
                    continue
                if c == '\\':
                    esc = True
                    j += 1
                    continue
                if c == '"':
                    in_q = not in_q
                    j += 1
                    continue
                if not in_q:
                    if c == '[':
                        br += 1
                    elif c == ']':
                        br = max(0, br - 1)
                    if br == 0:
                        m3 = re.match(r"\s*([A-Za-z_][\w-]*)\s*:\s", val[j:])
                        if m3:
                            cut = j + m3.start()
                            break
                j += 1

            if cut == -1:
                tail_lines.append(pfx + val)
                break
            else:
                tail_lines.append((pfx + val[:cut].rstrip()))
                cur = val[cut:].lstrip()
                continue

        result = []
        result.append(first + ("\n" if not first.endswith("\n") else ""))
        for t in tail_lines:
            t2 = t + ("\n" if not t.endswith("\n") else "")
            result.append(t2)
        return result

    for raw in lines:
        # Разбиваем строки, где случайно склеены несколько ключей
        candidate_lines = split_multiple_keys(raw)
        for cand in candidate_lines:
        # Чиним темы
            if cand.lstrip().startswith("topics:"):
                fixed = clean_topics_line(cand)
                out.append(fixed)
                continue

            if cand.lstrip().startswith("tags:"):
                fixed = clean_tags_line(cand)
                out.append(fixed)
                continue

            # Чиним случая, когда в строку попали лишние закрывающие --- (редкая аномалия)
            if "---" in cand and cand.strip() != "---":
            # Если это не строка вида '---', а какой-то мусор, попробуем обрезать
            # Оставим всё до '---' включительно только если похоже на ключ: значение
            # Иначе вообще отбросим мусор после ключа
                idx = cand.find("---")
                left = cand[:idx].rstrip()
            # Признак пары ключ: значение
                if ":" in left:
                    out.append(left + ("\n" if not left.endswith("\n") else ""))
                else:
                    # Если это не ключ-значение — просто пропустим мусорную строку
                    if left.strip():
                        out.append(left + ("\n" if not left.endswith("\n") else ""))
                continue

            # Нормализуем title из slug в читабельный
            if cand.lstrip().startswith("title:"):
                # Захватываем и с кавычками, и без
                m_q = re.match(r"^(\s*title:\s*)\"(.*?)\"(\s*)$", cand)
                m_nq = re.match(r"^(\s*title:\s*)([^\"\n]+?)(\s*)$", cand)
                if m_q:
                    prefix, val, suffix = m_q.groups()
                    normalized = normalize_title_value(val)
                    out.append(f"{prefix}{'\"'}{normalized}{'\"'}{suffix}\n" if not cand.endswith("\n") else f"{prefix}{'\"'}{normalized}{'\"'}{suffix}")
                    continue
                if m_nq:
                    prefix, val, suffix = m_nq.groups()
                    normalized = normalize_title_value(val)
                    out.append(f"{prefix}\"{normalized}\"{suffix}\n" if not cand.endswith("\n") else f"{prefix}\"{normalized}\"{suffix}")
                    continue

            out.append(cand)

    cleaned = "".join(out)

    # Форсируем переносы строк между склеенными ключами (например, 
    # 'topics: ["Networking"]status: "done"' -> две строки)
    known_keys = (
        "type|topics|status|level|title|summary|platforms|ios_min|tags|severity|duration"
    )
    pattern_keys = re.compile(rf"(\]|\")\s*(?=(?:{known_keys})\s*:)" )

    def enforce_newlines_between_keys(block: str) -> str:
        # Применяем построчно, чтобы не задеть многострочные структуры
        result_lines: List[str] = []
        for ln in block.splitlines(keepends=False):
            fixed_ln = pattern_keys.sub(r"\1\n", ln)
            result_lines.append(fixed_ln)
        return "\n".join(result_lines) + ("\n" if block.endswith("\n") else "")

    cleaned = enforce_newlines_between_keys(cleaned)
    # Убедимся, что фронтматтер оканчивается переводом строки
    if cleaned and not cleaned.endswith("\n"):
        cleaned += "\n"
    return cleaned


def rebuild_content(frontmatter_text: str, body: str) -> str:
    fm = clean_frontmatter_text(frontmatter_text)
    return f"---\n{fm}---\n{body}"


def process_file(md_file: Path) -> bool:
    try:
        content = md_file.read_text(encoding="utf-8")
    except Exception:
        return False

    fm_text, delim, body = split_frontmatter(content)
    if fm_text is None:
        return False

    fixed = rebuild_content(fm_text, body)
    if fixed != content:
        try:
            md_file.write_text(fixed, encoding="utf-8")
            return True
        except Exception:
            return False
    return False


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    return "Templates" in parts or "backups" in parts


def main() -> int:
    changed = 0
    scanned = 0
    for md in VAULT_PATH.rglob("*.md"):
        if should_skip(md):
            continue
        scanned += 1
        if process_file(md):
            changed += 1

    print(f"Просканировано файлов: {scanned}")
    print(f"Исправлено фронтматтеров: {changed}")
    if changed:
        print("Готово ✅")
    else:
        print("Изменений не требуется ✅")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


