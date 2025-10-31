# 🚀 Отправка Payment Bot на GitHub

## ✅ Репозиторий готов!

Все файлы закоммичены и готовы к отправке на GitHub.

---

## 📋 БЫСТРЫЕ ШАГИ

### 1. Создайте репозиторий на GitHub

1. Откройте: https://github.com/new
2. **Repository name:** `PaymentBot` (или другое имя)
3. **Description:** `Telegram Bot для отслеживания TRC20 платежей и Payment API`
4. Выберите **Public** или **Private**
5. **НЕ** ставьте галочки на:
   - ❌ Add a README file
   - ❌ Add .gitignore
   - ❌ Choose a license
6. Нажмите **"Create repository"**

---

### 2. Подключите и отправьте код

**После создания репозитория GitHub покажет инструкции. Выполните:**

```bash
cd /Users/roma/Desktop/платежка

# Добавьте remote (замените URL на ваш!)
git remote add origin https://github.com/UnifrormMantis/PaymentBot.git

# Или если используете SSH:
# git remote add origin git@github.com:UnifrormMantis/PaymentBot.git

# Отправьте код на GitHub
git branch -M main
git push -u origin main
```

---

### 3. Если попросит авторизацию

**GitHub требует Personal Access Token вместо пароля:**

1. Создайте токен:
   - GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
   - Нажмите **"Generate new token (classic)"**
   - **Note:** `PaymentBot Push`
   - Выберите scope: ✅ **repo** (все галочки в repo)
   - Нажмите **"Generate token"**
   - **Скопируйте токен** (показывается только раз!)

2. При `git push` используйте:
   - **Username:** ваш GitHub username
   - **Password:** вставьте скопированный токен (не пароль!)

---

## ✅ ПРОВЕРКА

После успешного push:

1. Откройте ваш репозиторий на GitHub
2. Проверьте что все файлы на месте
3. README.md должен отображаться

---

## 🔄 ОБНОВЛЕНИЕ КОДА

Когда сделаете изменения:

```bash
cd /Users/roma/Desktop/платежка

# Добавить изменения
git add .

# Закоммитить
git commit -m "Описание изменений"

# Отправить на GitHub
git push
```

---

## 📦 ЧТО УЖЕ В РЕПОЗИТОРИИ

✅ Все файлы Payment Bot  
✅ Payment API (`simple_payment_api.py`)  
✅ Главный бот (`main.py`, `private_bot.py`)  
✅ База данных (`database.py`)  
✅ Трекер транзакций (`tron_tracker.py`)  
✅ Скрипты запуска/остановки  
✅ Документация  
✅ `.gitignore` (логи, БД, venv исключены)  

---

## 🎯 ГОТОВО!

После push ваш Payment Bot будет на GitHub и готов к:
- ✅ Клонированию на VPS
- ✅ Работе в команде
- ✅ Резервному копированию
- ✅ Версионированию

---

**Если возникнут проблемы - напишите, помогу!** 🚀

