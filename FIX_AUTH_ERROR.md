# 🔧 Исправление ошибки аутентификации (403)

## ❌ ОШИБКА:
```
remote: Permission denied to UnifrormMantis/PaymentBot.git
fatal: unable to access: The requested URL returned error: 403
```

---

## ✅ РЕШЕНИЕ 1: Проверьте токен

### Проблемы с токеном:

1. **Токен скопирован не полностью**
   - Убедитесь что скопировали весь токен (обычно ~40 символов)
   - Начинается с `ghp_`

2. **Не выбран scope "repo"**
   - Токен должен иметь права на репозиторий
   - При создании токена обязательно выберите ✅ **repo**

3. **Токен истек**
   - Если выбрали срок действия - проверьте что не истек
   - Создайте новый токен

---

## ✅ РЕШЕНИЕ 2: Очистите кэш Git

Git может кэшировать старый пароль. Очистите:

```bash
# Очистка кэша учетных данных
git credential-cache exit

# Или для macOS:
git credential-osxkeychain erase
host=github.com
protocol=https

# Нажмите Enter дважды
```

Затем попробуйте снова:
```bash
git push -u origin main
```

---

## ✅ РЕШЕНИЕ 3: Используйте SSH (РЕКОМЕНДУЕТСЯ)

SSH не требует ввода пароля каждый раз и работает надежнее.

### Настройка SSH:

```bash
# 1. Проверьте есть ли SSH ключ
ls -la ~/.ssh/id_ed25519.pub

# 2. Если нет - создайте новый
ssh-keygen -t ed25519 -C "your_email@example.com"
# На все вопросы нажмите Enter (используйте значения по умолчанию)

# 3. Скопируйте публичный ключ
cat ~/.ssh/id_ed25519.pub
# Скопируйте весь вывод (начинается с ssh-ed25519)

# 4. Добавьте в GitHub:
#    GitHub → Settings → SSH and GPG keys → New SSH key
#    Title: PaymentBot
#    Key: вставьте скопированный ключ
#    Add SSH key

# 5. Измените URL репозитория на SSH
cd /Users/roma/Desktop/платежка
git remote set-url origin git@github.com:UnifrormMantis/PaymentBot.git

# 6. Проверьте подключение
ssh -T git@github.com
# Должно показать: Hi UnifrormMantis! You've successfully authenticated...

# 7. Отправьте код
git push -u origin main
```

---

## ✅ РЕШЕНИЕ 4: Используйте токен в URL

Можно добавить токен прямо в URL (менее безопасно, но работает):

```bash
cd /Users/roma/Desktop/платежка

# Получите токен (скопируйте его)
# Затем выполните (замените YOUR_TOKEN на ваш токен):
git remote set-url origin https://YOUR_TOKEN@github.com/UnifrormMantis/PaymentBot.git

# Отправьте
git push -u origin main
```

⚠️ **Небезопасно!** Токен будет виден в истории команд. После push удалите токен из URL.

---

## ✅ РЕШЕНИЕ 5: Создайте новый токен

Если старый не работает, создайте новый:

1. **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. **Generate new token (classic)**
3. **Note:** `PaymentBot Push 2`
4. **Expiration:** `No expiration` или `90 days`
5. **Select scopes:** ✅ **repo** (обязательно!)
   - ✅ repo:status
   - ✅ repo_deployment
   - ✅ public_repo
   - ✅ repo:invite
   - ✅ security_events
6. **Generate token**
7. **Скопируйте новый токен**

Затем попробуйте снова:
```bash
git push -u origin main
```

---

## 🔍 ПРОВЕРКА ТОКЕНА

Убедитесь что токен:
- ✅ Начинается с `ghp_`
- ✅ Длина ~40-50 символов
- ✅ Скопирован полностью (без пробелов в начале/конце)
- ✅ Имеет scope "repo"
- ✅ Не истек

---

## 📝 ПОШАГОВЫЙ ПЛАН

### Попробуйте в этом порядке:

1. **Очистите кэш Git** (Решение 2)
2. **Создайте новый токен** (Решение 5)
3. **Попробуйте push снова**

Если не работает - используйте **SSH** (Решение 3) - это самый надежный способ.

---

## 🚀 БЫСТРОЕ РЕШЕНИЕ (SSH)

```bash
# Создать SSH ключ
ssh-keygen -t ed25519 -C "your_email@example.com"
# Enter на всех вопросах

# Скопировать ключ
cat ~/.ssh/id_ed25519.pub

# Добавить в GitHub (Settings → SSH and GPG keys → New SSH key)

# Изменить URL на SSH
cd /Users/roma/Desktop/платежка
git remote set-url origin git@github.com:UnifrormMantis/PaymentBot.git

# Отправить
git push -u origin main
```

---

**Попробуйте сначала Решение 2 (очистка кэша) и Решение 5 (новый токен). Если не поможет - используйте SSH!**

