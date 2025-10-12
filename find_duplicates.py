#!/usr/bin/env python3
"""
Поиск дублированного контента в базе знаний
"""
import os
import hashlib
from pathlib import Path
from collections import defaultdict

def find_duplicate_content():
    """Находит файлы с идентичным содержимым"""
    print("🔍 Поиск дублированного контента...")

    obsidian_root = Path("/Users/kirilltitov/Documents/Obsidian Vault")
    file_hashes = defaultdict(list)

    # Проходим по всем .md файлам
    for md_file in obsidian_root.rglob("*.md"):
        if "Templates" in md_file.parts or "backups" in md_file.parts:
            continue

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Создаем хэш от содержимого файла
            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            file_hashes[content_hash].append(md_file)

        except Exception as e:
            print(f"Ошибка обработки {md_file}: {e}")

    # Находим дубликаты
    duplicates = []
    for hash_value, files in file_hashes.items():
        if len(files) > 1:
            duplicates.append((hash_value, files))

    if duplicates:
        print(f"\n❌ Найдено {len(duplicates)} групп дублированного контента:")
        for hash_value, files in duplicates:
            print(f"\nХэш: {hash_value}")
            for file_path in files:
                print(f"  {file_path}")
    else:
        print("✅ Дублированного контента не найдено")

    return duplicates

def find_similar_files():
    """Находит файлы с похожими названиями"""
    print("🔍 Поиск файлов с похожими названиями...")

    obsidian_root = Path("/Users/kirilltitov/Documents/Obsidian Vault")
    file_names = defaultdict(list)

    # Собираем все имена файлов
    for md_file in obsidian_root.rglob("*.md"):
        if "Templates" in md_file.parts or "backups" in md_file.parts:
            continue

        file_names[md_file.name].append(md_file)

    # Находим похожие имена
    similar = []
    for name, files in file_names.items():
        if len(files) > 1:
            similar.append((name, files))

    if similar:
        print(f"\n❌ Найдено {len(similar)} групп файлов с похожими названиями:")
        for name, files in similar:
            print(f"\nФайл: {name}")
            for file_path in files:
                print(f"  {file_path}")
    else:
        print("✅ Файлов с похожими названиями не найдено")

    return similar

def find_empty_files():
    """Находит пустые файлы"""
    print("🔍 Поиск пустых файлов...")

    obsidian_root = Path("/Users/kirilltitov/Documents/Obsidian Vault")
    empty_files = []

    for md_file in obsidian_root.rglob("*.md"):
        if "Templates" in md_file.parts or "backups" in md_file.parts:
            continue

        try:
            if md_file.stat().st_size == 0:
                empty_files.append(md_file)
        except:
            pass

    if empty_files:
        print(f"\n❌ Найдено {len(empty_files)} пустых файлов:")
        for file_path in empty_files:
            print(f"  {file_path}")
    else:
        print("✅ Пустых файлов не найдено")

    return empty_files

def main():
    """Главная функция"""
    print("🚀 Анализ базы знаний на наличие дубликатов...")

    duplicates = find_duplicate_content()
    similar = find_similar_files()
    empty = find_empty_files()

    print("\n📋 Итоговый отчет:")
    print(f"Дублированного контента: {len(duplicates)} групп")
    print(f"Похожих названий: {len(similar)} групп")
    print(f"Пустых файлов: {len(empty)}")

    if duplicates or similar or empty:
        print("\n⚠️  Найдены дубликаты, требующие внимания")
        return 1
    else:
        print("\n✅ Дубликатов не найдено")
        return 0

if __name__ == "__main__":
    exit(main())
