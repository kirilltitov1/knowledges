#!/usr/bin/env python3
"""
Полное обслуживание базы знаний - запускает все инструменты
"""
import os
import subprocess
from pathlib import Path
import time

def run_script(script_name, description):
    """Запускает скрипт и показывает прогресс"""
    print(f"\n🚀 {description}")
    print(f"Выполняется: python3 {script_name}")

    try:
        start_time = time.time()
        result = subprocess.run(
            ['python3', script_name],
            capture_output=True,
            text=True,
            timeout=300  # 5 минут таймаут
        )

        end_time = time.time()
        duration = end_time - start_time

        if result.returncode == 0:
            print(f"✅ {description} завершено за {duration:.1f} сек")
            if result.stdout.strip():
                print("📋 Результат:")
                for line in result.stdout.strip().split('\n')[-5:]:  # Последние 5 строк
                    if line.strip():
                        print(f"  {line}")
        else:
            print(f"❌ {description} завершено с ошибкой")
            if result.stderr.strip():
                print(f"Ошибка: {result.stderr.strip()}")

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print(f"⏰ {description} превысило время ожидания")
        return False
    except Exception as e:
        print(f"❌ Ошибка запуска {script_name}: {e}")
        return False

def main():
    """Главная функция - запускает полное обслуживание"""
    print("🎉 Запуск полного обслуживания базы знаний iOS разработки")
    print("=" * 60)

    scripts_dir = Path("/Users/kirilltitov/Documents/Obsidian Vault")
    os.chdir(scripts_dir)

    # Список скриптов для запуска
    maintenance_plan = [
        ("standardize_frontmatter.py", "Стандартизация фронтматтера"),
        ("find_duplicates.py", "Поиск дублированного контента"),
        ("fix_broken_links.py", "Проверка битых ссылок"),
        ("fix_frontmatter_issues.py", "Исправление проблем фронтматтера"),
        ("content_quality_analyzer.py", "Анализ качества контента"),
        ("maintenance_scripts.py", "Комплексная проверка"),
        ("git_integration.py", "Анализ Git интеграции"),
    ]

    results = []

    for script_name, description in maintenance_plan:
        if Path(script_name).exists():
            success = run_script(script_name, description)
            results.append((description, success))
        else:
            print(f"⚠️ Скрипт {script_name} не найден, пропускаем")
            results.append((description, False))

    # Итоговый отчет
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ ОТЧЕТ ПО ОБСЛУЖИВАНИЮ")
    print("=" * 60)

    successful = sum(1 for _, success in results if success)
    total = len(results)

    print(f"\n✅ Успешно выполнено: {successful}/{total}")
    print(f"❌ Не удалось: {total - successful}/{total}")

    print("\n📋 Детальный отчет:")
    for description, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {description}")

    # Рекомендации
    print("\n💡 Рекомендации:")
    if successful == total:
        print("🎉 Все инструменты отработали успешно!")
        print("   База знаний в отличном состоянии.")
    else:
        print("⚠️ Некоторые инструменты завершились с ошибками.")
        print("   Проверьте логи выше для детальной информации.")

    print("\n🚀 Следующие шаги:")
    print("1. Изучите созданные отчеты в корне базы знаний")
    print("2. Исправьте выявленные проблемы вручную")
    print("3. Создайте резервную копию: python3 backup_script.py create")
    print("4. Настройте регулярное обслуживание")

    print(f"\n📅 Время обслуживания: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Директория: {scripts_dir}")

    return 0 if successful == total else 1

if __name__ == "__main__":
    exit(main())
