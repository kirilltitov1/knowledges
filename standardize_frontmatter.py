#!/usr/bin/env python3
import os
import re
from pathlib import Path

def parse_simple_yaml(text):
    """Простой парсер YAML для базовых структур"""
    result = {}
    for line in text.split('\n'):
        line = line.strip()
        if ': ' in line:
            key, value = line.split(': ', 1)
            key = key.strip()
            value = value.strip().strip('"\'')
            result[key] = value
    return result

def generate_simple_yaml(data):
    """Простой генератор YAML"""
    lines = []
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}: [{', '.join(f'\"{v}\"' for v in value)}]")
        else:
            lines.append(f"{key}: \"{value}\"")
    return '\n'.join(lines)

def standardize_frontmatter():
    """Стандартизирует фронтматтер во всех .md файлах"""

    # Шаблоны фронтматтера для разных типов контента
    templates = {
        'thread': {
            'type': 'thread',
            'topics': [],
            'status': 'draft',
            'summary': ''
        },
        'example': {
            'type': 'example',
            'topics': [],
            'level': 'intermediate',
            'platforms': ['iOS'],
            'ios_min': '15.0',
            'status': 'draft',
            'tags': []
        },
        'topic': {
            'type': 'topic',
            'topics': [],
            'status': 'draft'
        },
        'guide': {
            'type': 'guide',
            'topics': [],
            'status': 'draft',
            'level': 'intermediate'
        },
        'index': {
            'type': 'index',
            'topics': [],
            'status': 'draft'
        },
        'antipattern': {
            'type': 'antipattern',
            'topics': [],
            'status': 'draft',
            'severity': 'medium'
        },
        'playbook': {
            'type': 'playbook',
            'topics': [],
            'status': 'draft',
            'duration': '30m'
        }
    }

    # Пройтись по всем .md файлам
    obsidian_root = Path("/Users/kirilltitov/Documents/Obsidian Vault")

    for md_file in obsidian_root.rglob("*.md"):
        # Пропустить шаблоны и файлы в Templates
        if "Templates" in md_file.parts or md_file.name.startswith("Thread.md"):
            continue

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Проверить, есть ли фронтматтер
            if not content.startswith('---'):
                print(f"Пропускаем {md_file} - нет фронтматтера")
                continue

            # Извлечь фронтматтер
            frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
            if not frontmatter_match:
                print(f"Пропускаем {md_file} - неправильный формат фронтматтера")
                continue

            frontmatter_text = frontmatter_match.group(1)
            body = content[frontmatter_match.end():]

            # Парсить фронтматтер
            try:
                frontmatter = parse_simple_yaml(frontmatter_text)
                if not frontmatter:
                    frontmatter = {}
            except:
                print(f"Ошибка парсинга фронтматтера в {md_file}")
                continue

            # Определить тип контента по пути файла или существующему типу
            file_type = frontmatter.get('type', 'thread')

            # Если тип не распознан, попробовать определить по пути
            if file_type not in templates:
                for folder in md_file.parts:
                    if folder in ['Examples', 'Примеры']:
                        file_type = 'example'
                        break
                    elif folder in ['Antipatterns', 'Антипаттерны']:
                        file_type = 'antipattern'
                        break
                    elif folder in ['Playbooks', 'Плейбуки']:
                        file_type = 'playbook'
                        break
                else:
                    file_type = 'thread'  # По умолчанию

            # Стандартизировать фронтматтер
            template = templates.get(file_type, templates['thread']).copy()

            # Сохранить существующие значения, если они есть
            for key in template:
                if key in frontmatter:
                    template[key] = frontmatter[key]

            # Специальная обработка для топиков
            if not template.get('topics'):
                # Попытаться извлечь топики из пути файла
                path_topics = []
                for part in md_file.parts:
                    if part not in ['iOS', 'General', 'Templates', 'Examples', 'Antipatterns', 'Playbooks']:
                        # Очистить от специальных символов и номеров
                        clean_part = re.sub(r'[0-9()«»""'']', '', part).strip()
                        if clean_part and len(clean_part) > 2:
                            path_topics.append(clean_part)

                if path_topics:
                    template['topics'] = path_topics[:3]  # Максимум 3 топика

            # Добавить title если отсутствует
            if not template.get('title'):
                template['title'] = md_file.stem

            # Создать новый фронтматтер
            new_frontmatter = generate_simple_yaml(template)

            # Обновить файл
            new_content = f"---\n{new_frontmatter}\n---\n{body}"

            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"Обновлен фронтматтер в {md_file}")

        except Exception as e:
            print(f"Ошибка обработки {md_file}: {e}")

if __name__ == "__main__":
    standardize_frontmatter()
