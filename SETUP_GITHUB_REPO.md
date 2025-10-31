# 🚀 Настройка GitHub репозитория для Payment Bot

## ✅ Git репозиторий уже создан локально!

Теперь нужно создать репозиторий на GitHub и подключить его.

---

## ШАГ 1: Создайте репозиторий на GitHub

1. Откройте https://github.com/new
2. Название репозитория: `PaymentBot` (или любое другое)
3. Сделайте его **Public** или **Private** (на ваше усмотрение)
4. **НЕ** добавляйте README, .gitignore или лицензию (у нас уже есть файлы)
5. Нажмите **"Create repository"**

---

## ШАГ 2: Подключите локальный репозиторий к GitHub

После создания репозитория GitHub покажет инструкции. Выполните на вашем компьютере:

```bash
cd /Users/roma/Desktop/платежка

# Добавьте remote (замените URL на ваш репозиторий)
git remote add origin https://github.com/ВАШ_ЮЗЕРНЕЙМ/НАЗВАНИЕ_РЕПО.git

# Или если используете SSH:
# git remote add origin git@github.com:ВАШ_ЮЗЕРНЕЙМ/НАЗВАНИЕ_РЕПО.git

# Отправьте код на GitHub
git branch -M main
git push -u origin main
```

---

## Пример:

Если ваш GitHub username: `UnifrormMantis`, а репозиторий называется `PaymentBot`:

```bash
cd /Users/roma/Desktop/платежка
git remote add origin https://github.com/UnifrormMantis/PaymentBot.git
git branch -M main
git push -u origin main
```

---

## Если возникнут проблемы с аутентификацией:

GitHub больше не поддерживает пароли для push. Нужно использовать:

### Вариант 1: Personal Access Token (PAT)
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token
3. Выберите scope: `repo`
4. Используйте токен вместо пароля при `git push`

### Вариант 2: SSH ключ
```bash
# Проверьте есть ли SSH ключ
ls -la ~/.ssh/id_rsa.pub

# Если нет - создайте
ssh-keygen -t ed25519 -C "your_email@example.com"

# Добавьте в GitHub:
# GitHub → Settings → SSH and GPG keys → New SSH key
# Скопируйте содержимое: cat ~/.ssh/id_ed25519.pub
```

---

## ✅ Готово!

После успешного push ваш код будет на GitHub и вы сможете:
- Клонировать на VPS
- Работать в команде
- Делать бэкапы

---

## Полезные команды Git:

```bash
# Проверить статус
git status

# Добавить изменения
git add .

# Закоммитить
git commit -m "Описание изменений"

# Отправить на GitHub
git push

# Получить обновления
git pull
```

