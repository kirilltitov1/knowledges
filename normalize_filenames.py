#!/usr/bin/env python3
"""
Нормализация имён файлов и папок:
- Приводит имена к Unicode NFC (устраняет разницу "й" vs "й" и т.п.)
- Опционально удаляет конфликтные суффиксы " 2"/" 3" (только при явном флаге)
- Безопасно объединяет идентичные файлы (если хэши совпадают)

Запуск:
  python3 normalize_filenames.py --apply        # применить
  python3 normalize_filenames.py --dry-run      # показать план
  python3 normalize_filenames.py --strip-suffix # дополнительно убрать суффиксы " 2"/" 3"
"""
import argparse
import hashlib
import sys
import unicodedata
from pathlib import Path

ROOT = Path("/Users/kirilltitov/Documents/Obsidian Vault")

EXCLUDE_DIR_NAMES = {".git", "backups"}
EXCLUDE_PARTS_CONTAIN = {"Templates"}


def compute_md5(path: Path) -> str:
    m = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            m.update(chunk)
    return m.hexdigest()


def has_combining_marks(s: str) -> bool:
    return any(unicodedata.category(ch) == "Mn" for ch in s)


def normalize_component(name: str, strip_suffix: bool) -> str:
    # Unicode NFC нормализация
    normalized = unicodedata.normalize("NFC", name)
    # Не трогаем расширения/точки, только хвостовые пробел+цифра-сценарии, если явно указано
    if strip_suffix:
        for suffix in (" 2", " 3"):
            if normalized.endswith(suffix):
                normalized = normalized[: -len(suffix)]
                break
    return normalized


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDE_DIR_NAMES:
        return True
    if any(ex in path.parts for ex in EXCLUDE_PARTS_CONTAIN):
        return True
    return False


def plan_normalization(strip_suffix: bool):
    moves = []  # (src, dst)
    for path in sorted(ROOT.rglob("*"), key=lambda p: (p.is_dir(), len(str(p))), reverse=True):
        if path == ROOT:
            continue
        if should_skip(path):
            continue
        # Собираем нормализованный путь по компонентам
        new_parts = []
        for comp in path.relative_to(ROOT).parts:
            new_parts.append(normalize_component(comp, strip_suffix))
        dst = ROOT.joinpath(*new_parts)
        if dst != path:
            moves.append((path, dst))
    return moves


def ensure_parent(dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)


def apply_moves(moves, dry_run: bool):
    # Сначала файлы, потом директории (во избежание конфликтов путей)
    file_moves = [(s, d) for s, d in moves if s.is_file()]
    dir_moves = [(s, d) for s, d in moves if s.is_dir()]

    conflicts = []
    performed = []

    # Файлы
    for src, dst in file_moves:
        if dry_run:
            print(f"FILE: {src} -> {dst}")
            continue
        if dst.exists():
            if dst.is_file():
                # Сравнить содержимое
                try:
                    if compute_md5(src) == compute_md5(dst):
                        # Идентичные: удаляем источник
                        src.unlink()
                        performed.append((src, dst, "deleted-duplicate"))
                        continue
                except Exception as e:
                    conflicts.append((src, dst, f"hash-error: {e}"))
                    continue
                # Разное содержимое: конфликт
                conflicts.append((src, dst, "content-diff"))
                continue
            else:
                conflicts.append((src, dst, "dst-exists-nonfile"))
                continue
        ensure_parent(dst)
        try:
            src.rename(dst)
            performed.append((src, dst, "moved"))
        except Exception as e:
            conflicts.append((src, dst, f"rename-error: {e}"))

    # Директории (переименуем пустые/не конфликтующие)
    for src, dst in dir_moves:
        if dry_run:
            print(f"DIR:  {src} -> {dst}")
            continue
        if dst.exists():
            # Если dst существует и src пустая — удалим src
            try:
                if src.exists() and src.is_dir() and not any(src.iterdir()):
                    src.rmdir()
                    performed.append((src, dst, "removed-empty-dir"))
                else:
                    conflicts.append((src, dst, "dst-exists"))
            except Exception as e:
                conflicts.append((src, dst, f"dir-clean-error: {e}"))
            continue
        ensure_parent(dst)
        try:
            src.rename(dst)
            performed.append((src, dst, "moved-dir"))
        except Exception as e:
            conflicts.append((src, dst, f"rename-error: {e}"))

    return performed, conflicts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Применить изменения (по умолчанию dry-run)")
    parser.add_argument("--dry-run", action="store_true", help="Только показать план (по умолчанию если --apply не указан)")
    parser.add_argument("--strip-suffix", action="store_true", help="Удалять суффиксы ' 2'/' 3' в именах")
    args = parser.parse_args()

    dry_run = not args.apply or args.dry_run

    moves = plan_normalization(strip_suffix=args.strip_suffix)
    if not moves:
        print("✅ Нечего нормализовать")
        return 0

    print(f"🔧 Нашлось к нормализации: {len(moves)} путей")
    performed, conflicts = apply_moves(moves, dry_run=dry_run)

    if dry_run:
        print("\nℹ️  Это dry-run. Добавьте --apply для применения.")
        return 0

    print(f"\n✅ Выполнено: {len(performed)}")
    if conflicts:
        print(f"⚠️ Конфликтов/ошибок: {len(conflicts)}")
        for src, dst, reason in conflicts[:20]:
            print(f"  {src} -> {dst} : {reason}")
        if len(conflicts) > 20:
            print(f"  ... и ещё {len(conflicts)-20}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
