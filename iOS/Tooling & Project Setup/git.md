---
title: Git - Система контроля версий
type: thread
topics: [Tooling, Version Control]
subtopic: Git
status: draft
---

# Git - Система контроля версий

## Основы

### Базовые команды
```bash
git init                    # Инициализация репозитория
git clone <url>            # Клонирование репозитория
git status                 # Статус изменений
git add <file>             # Добавить файл в stage
git add .                  # Добавить все изменения
git commit -m "message"    # Создать коммит
git push                   # Отправить изменения
git pull                   # Получить изменения
```

### Конфигурация
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --list          # Показать конфигурацию
```

## Работа с ветками

### Создание и переключение
```bash
git branch                 # Список веток
git branch <name>          # Создать ветку
git checkout <name>        # Переключиться на ветку
git checkout -b <name>     # Создать и переключиться
git switch <name>          # Новый способ переключения (Git 2.23+)
git switch -c <name>       # Создать и переключиться (новый способ)
```

### Слияние веток
```bash
git merge <branch>         # Слить ветку в текущую
git merge --no-ff <branch> # Слияние без fast-forward
git rebase <branch>        # Rebase текущей ветки на другую
```

### Удаление веток
```bash
git branch -d <name>       # Удалить локальную ветку
git branch -D <name>       # Принудительное удаление
git push origin --delete <name>  # Удалить удаленную ветку
```

## Работа с изменениями

### Просмотр истории
```bash
git log                    # История коммитов
git log --oneline          # Короткий формат
git log --graph            # С графом веток
git log --all --decorate --oneline --graph  # Полный граф
git show <commit>          # Показать изменения коммита
git diff                   # Изменения в рабочей директории
git diff --staged          # Изменения в stage
```

### Отмена изменений
```bash
git restore <file>         # Отменить изменения в файле (Git 2.23+)
git restore --staged <file> # Убрать из stage
git checkout -- <file>     # Отменить изменения (старый способ)
git reset HEAD <file>      # Убрать из stage (старый способ)
git reset --soft HEAD~1    # Отменить последний коммит (изменения остаются в stage)
git reset --hard HEAD~1    # Отменить последний коммит (изменения удаляются)
git revert <commit>        # Создать коммит, отменяющий изменения
```

### Stash - временное сохранение
```bash
git stash                  # Сохранить изменения
git stash save "message"   # Сохранить с сообщением
git stash list             # Список сохраненных изменений
git stash pop              # Применить и удалить последний stash
git stash apply            # Применить без удаления
git stash drop             # Удалить последний stash
git stash clear            # Удалить все stash
```

## Работа с удаленными репозиториями

### Удаленные репозитории
```bash
git remote                 # Список удаленных репозиториев
git remote -v              # С URL
git remote add <name> <url> # Добавить удаленный репозиторий
git remote remove <name>   # Удалить удаленный репозиторий
git fetch                  # Получить изменения без слияния
git pull                   # Получить и слить изменения
git push origin <branch>   # Отправить ветку
git push -u origin <branch> # Отправить и установить upstream
```

### Теги
```bash
git tag                    # Список тегов
git tag <name>             # Создать легковесный тег
git tag -a <name> -m "msg" # Создать аннотированный тег
git push origin <tag>      # Отправить тег
git push --tags            # Отправить все теги
git tag -d <name>          # Удалить локальный тег
```

## Специфика iOS-разработки

### .gitignore для iOS
```gitignore
# Xcode
*.xcodeproj/*
!*.xcodeproj/project.pbxproj
!*.xcodeproj/xcshareddata/
*.xcworkspace/*
!*.xcworkspace/contents.xcworkspacedata
*.xcuserstate
xcuserdata/

# CocoaPods
Pods/
*.podspec

# Carthage
Carthage/Build/

# Swift Package Manager
.swiftpm/
.build/
Packages/

# Fastlane
fastlane/report.xml
fastlane/Preview.html
fastlane/screenshots
fastlane/test_output

# Code coverage
*.gcov
*.gcda
*.gcno

# DerivedData
DerivedData/

# Build files
build/
*.ipa
*.dSYM.zip
*.dSYM
```

### Работа с большими файлами (Git LFS)
```bash
# Установка Git LFS
brew install git-lfs
git lfs install

# Отслеживание файлов
git lfs track "*.framework"
git lfs track "*.a"
git add .gitattributes
```

## Best Practices для iOS

### Коммиты
- ✅ Пишите понятные commit messages
- ✅ Используйте conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`
- ✅ Один коммит = одна логическая единица изменений
- ❌ Не коммитьте закомментированный код
- ❌ Не коммитьте приватные ключи и секреты

### Ветки
- `main/master` - стабильная ветка
- `develop` - ветка разработки
- `feature/название` - новый функционал
- `bugfix/название` - исправление багов
- `hotfix/название` - срочные исправления
- `release/версия` - подготовка релиза

### Git Flow
```bash
# Начало работы над фичей
git checkout develop
git pull
git checkout -b feature/new-feature

# Завершение фичи
git checkout develop
git merge --no-ff feature/new-feature
git push origin develop
git branch -d feature/new-feature
```

## Полезные алиасы

```bash
# Добавить в ~/.gitconfig
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = log --graph --all --decorate --oneline
    amend = commit --amend --no-edit
```

## Решение проблем

### Конфликты слияния
```bash
# Просмотр конфликтов
git status

# После разрешения конфликтов
git add .
git commit

# Отмена слияния
git merge --abort
```

### Изменение истории
```bash
# Изменить последний коммит
git commit --amend

# Интерактивный rebase
git rebase -i HEAD~3

# Squash коммитов
# В интерактивном режиме: pick -> squash
```

### Восстановление
```bash
# Найти потерянные коммиты
git reflog

# Восстановить коммит
git checkout <commit>
git checkout -b recovery-branch
```

## Вопросы на собеседовании

### 1. Что такое Git и чем он отличается от GitHub?
**Ответ:** 
- **Git** - это распределенная система контроля версий, инструмент для отслеживания изменений в коде
- **GitHub** - это веб-платформа для хостинга Git-репозиториев с дополнительными возможностями (pull requests, issues, CI/CD)
- Аналоги GitHub: GitLab, Bitbucket

### 2. Что такое stash и когда его использовать?
**Ответ:**
Git stash - временное хранилище для незакоммиченных изменений.

**Когда использовать:**
- Нужно срочно переключиться на другую ветку, но текущие изменения не готовы для коммита
- Хотите протестировать что-то на чистой ветке
- Нужно сделать pull, но есть локальные изменения

```bash
git stash              # Сохранить изменения
git stash pop          # Вернуть изменения
git stash list         # Посмотреть список stash
```

**Особенность:** stash работает как стек (LIFO - Last In, First Out)

### 3. В чем разница между merge и rebase?

**Merge:**
- Создает новый merge commit
- Сохраняет всю историю изменений
- История становится нелинейной (с ветвлениями)
- Безопаснее для публичных веток

```bash
git checkout main
git merge feature
# Создается merge commit
```

**Rebase:**
- Переписывает историю коммитов
- Создает линейную историю
- Коммиты из feature ветки "переносятся" на вершину main
- Нельзя использовать для публичных веток (изменяет SHA коммитов)

```bash
git checkout feature
git rebase main
# Коммиты feature перемещаются на вершину main
```

**Правило:** 
- Используйте `merge` для публичных веток
- Используйте `rebase` для локальных веток перед merge
- "Golden Rule": никогда не делайте rebase публичных веток

### 4. Что такое fast-forward merge?

**Ответ:**
Fast-forward - это специальный тип слияния, когда целевая ветка не имеет новых коммитов после создания feature ветки.

```bash
# main: A -> B -> C
# feature:        C -> D -> E

git checkout main
git merge feature
# Результат: main просто "перемещается" к E
# main: A -> B -> C -> D -> E (без merge commit)
```

**Отключение fast-forward:**
```bash
git merge --no-ff feature  # Всегда создает merge commit
```

### 5. Чем отличается git pull от git fetch?

**git fetch:**
- Загружает изменения с удаленного репозитория
- НЕ сливает изменения с локальной веткой
- Безопасно - можно посмотреть изменения перед слиянием

```bash
git fetch origin
git log origin/main  # Посмотреть изменения
git merge origin/main # Слить когда готовы
```

**git pull:**
- Выполняет `git fetch` + `git merge` одной командой
- Автоматически сливает изменения
- Может привести к конфликтам

```bash
git pull  # = git fetch + git merge
git pull --rebase  # = git fetch + git rebase
```

### 6. Что такое cherry-pick и когда его использовать?

**Ответ:**
Cherry-pick позволяет применить конкретный коммит из одной ветки в другую.

```bash
git checkout main
git cherry-pick abc123  # Применить коммит abc123 из другой ветки
```

**Когда использовать:**
- Нужен только один конкретный фикс из feature ветки
- Случайно закоммитили в неправильную ветку
- Хотите перенести hotfix в несколько веток

**Проблемы:**
- Создает дубликаты коммитов (разные SHA)
- Может вызвать конфликты в будущем

### 7. Что делать при merge конфликте?

**Ответ:**
```bash
# 1. Посмотреть конфликтующие файлы
git status

# 2. Открыть файл с конфликтом
# Увидите маркеры:
<<<<<<< HEAD
ваш код
=======
чужой код
>>>>>>> branch-name

# 3. Разрешить конфликт вручную (выбрать нужный вариант)

# 4. Добавить разрешенный файл
git add <file>

# 5. Завершить merge
git commit

# Или отменить merge
git merge --abort
```

**Инструменты для разрешения:**
- Xcode: Editor → Resolve Conflicts
- VS Code: встроенный merge editor
- SourceTree: визуальное разрешение конфликтов

### 8. Чем отличается git reset от git revert?

**git reset:**
- Удаляет коммиты из истории
- Опасно для публичных веток
- Три режима: `--soft`, `--mixed`, `--hard`

```bash
git reset --soft HEAD~1   # Отменить коммит, изменения в stage
git reset --mixed HEAD~1  # Отменить коммит и stage (по умолчанию)
git reset --hard HEAD~1   # Отменить всё (опасно!)
```

**git revert:**
- Создает новый коммит, отменяющий изменения
- Безопасно для публичных веток
- Сохраняет историю

```bash
git revert abc123  # Создает новый коммит, отменяющий abc123
```

**Правило:** для публичных веток используйте `revert`, для локальных - можно `reset`

### 9. Что такое HEAD, origin, master/main?

**HEAD:**
- Указатель на текущий коммит/ветку
- `HEAD~1` - предыдущий коммит
- `HEAD~2` - два коммита назад
- Detached HEAD - когда HEAD указывает на коммит, а не на ветку

**origin:**
- Стандартное имя для удаленного репозитория
- Создается автоматически при `git clone`
- Можно иметь несколько удаленных репозиториев

**master/main:**
- Имя основной ветки (по умолчанию)
- GitHub переименовал `master` в `main` в 2020

```bash
HEAD -> текущая позиция
origin/main -> ветка main на удаленном сервере
main -> локальная ветка main
```

### 10. Что такое .gitignore и как он работает?

**Ответ:**
`.gitignore` - файл с паттернами файлов, которые Git должен игнорировать.

```gitignore
# Игнорировать все .DS_Store
.DS_Store

# Игнорировать папку
build/

# Игнорировать все .log файлы
*.log

# НЕ игнорировать specific.log
!specific.log

# Игнорировать все .txt в корне
/*.txt

# Игнорировать в любой вложенности
**/*.tmp
```

**Важно:**
- `.gitignore` работает только для untracked файлов
- Если файл уже в репозитории, нужно сначала удалить его из индекса:

```bash
git rm --cached <file>     # Удалить из Git, но оставить локально
git commit -m "Remove tracked file"
```

### 11. Как отменить git push?

**Ответ:**
Зависит от ситуации:

**Если еще никто не забрал изменения:**
```bash
git reset --hard HEAD~1    # Отменить локально
git push --force origin main  # Принудительно запушить (опасно!)
```

**Если другие уже забрали изменения (правильный способ):**
```bash
git revert HEAD           # Создать коммит отмены
git push origin main      # Запушить отмену
```

**⚠️ Важно:** `git push --force` опасен для командной работы!

### 12. Что такое Git Flow?

**Ответ:**
Git Flow - популярная модель ветвления для Git.

**Основные ветки:**
- `main/master` - стабильный продакшн код
- `develop` - ветка разработки

**Вспомогательные ветки:**
- `feature/*` - новый функционал
- `release/*` - подготовка релиза
- `hotfix/*` - срочные исправления в продакшне

**Процесс:**
```bash
# Новая фича
git checkout develop
git checkout -b feature/login
# ... разработка ...
git checkout develop
git merge --no-ff feature/login

# Релиз
git checkout -b release/1.0.0 develop
# ... финальные правки ...
git checkout main
git merge --no-ff release/1.0.0
git tag -a 1.0.0

# Hotfix
git checkout -b hotfix/critical-bug main
# ... исправление ...
git checkout main
git merge --no-ff hotfix/critical-bug
git checkout develop
git merge --no-ff hotfix/critical-bug
```

### 13. Как найти коммит, который сломал функционал?

**Ответ:** Используйте `git bisect` - бинарный поиск проблемного коммита.

```bash
# Начать bisect
git bisect start
git bisect bad              # Текущий коммит сломан
git bisect good abc123      # Коммит abc123 был рабочим

# Git автоматически переключается на средний коммит
# Тестируете и говорите:
git bisect good   # если работает
git bisect bad    # если сломано

# Git продолжает поиск
# В конце показывает проблемный коммит

# Завершить bisect
git bisect reset
```

**Автоматический bisect:**
```bash
git bisect start HEAD abc123
git bisect run ./test.sh  # Автоматически тестирует каждый коммит
```

### 14. Как объединить несколько коммитов в один (squash)?

**Ответ:**
Используйте интерактивный rebase:

```bash
# Объединить последние 3 коммита
git rebase -i HEAD~3

# В редакторе:
pick abc123 First commit
squash def456 Second commit   # Изменить pick на squash
squash ghi789 Third commit    # Изменить pick на squash

# Откроется редактор для объединенного commit message
```

**Альтернатива при merge:**
```bash
git checkout main
git merge --squash feature  # Объединит все коммиты из feature
git commit -m "Add new feature"
```

### 15. Что делать, если случайно закоммитили секретный ключ?

**Ответ:**
**⚠️ Важно:** Простое удаление файла НЕ помогает - он остается в истории!

**Решение:**
```bash
# 1. Немедленно деактивируйте ключ/пароль на сервисе!

# 2. Удалите файл из всей истории
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/secret.key" \
  --prune-empty --tag-name-filter cat -- --all

# Или используйте BFG Repo-Cleaner (быстрее)
brew install bfg
bfg --delete-files secret.key
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 3. Принудительно запушьте
git push --force --all

# 4. Сообщите команде, что нужно перезаклонировать репозиторий
```

**Профилактика:**
- Используйте `.gitignore`
- Храните секреты в `.env` файлах (добавлены в `.gitignore`)
- Используйте git hooks для проверки секретов

### 16. Какая разница между клонированием и форком репозитория?

**Клонирование (git clone):**
- Создает локальную копию репозитория
- Связан с оригинальным репозиторием как `origin`
- Нужен доступ для push

**Форк (GitHub/GitLab fork):**
- Создает копию репозитория на вашем аккаунте GitHub
- Независимый репозиторий
- Используется для контрибуций в open source
- Workflow: fork → clone → branch → commit → push → pull request

```bash
# После форка
git clone https://github.com/YOUR_USERNAME/repo.git
cd repo
git remote add upstream https://github.com/ORIGINAL_OWNER/repo.git

# Синхронизация с оригинальным репозиторием
git fetch upstream
git checkout main
git merge upstream/main
```

## Ссылки

- [Pro Git Book](https://git-scm.com/book/ru/v2)
- [GitHub Git Cheat Sheet](https://training.github.com/downloads/github-git-cheat-sheet/)
- [Atlassian Git Tutorials](https://www.atlassian.com/git/tutorials)
- [Oh Shit, Git!?!](https://ohshitgit.com/ru) - решение частых проблем
- [Learn Git Branching](https://learngitbranching.js.org/?locale=ru_RU) - интерактивное обучение

## См. также

- [[iOS/CI & CD/CI & CD]] - автоматизация с помощью Git hooks
- [[iOS/App Store & Distribution/App Store & Distribution]] - версионирование и релизы
- [[interview-preparation]] - подготовка к собеседованиям

