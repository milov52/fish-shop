# FishShopBot

Данный бот выступает в роли магазина, в данном случаи рыбы

## Запуск бота локально
Для запуска бота на вашем сервере необходимо выполнить следующие действия:

1. Cоздать бота в Телеграмм  [см.тут](https://core.telegram.org/bots).
2. Инициализировать с вашим ботом чат.
3. Склонировать себе файлы репозитория выполнив команду **https://github.com/milov52/fish-shop**.
4. Установить необходимы зависимости **pip install -r requirements.txt**.
5. В директории с проектом создать файл **.env** со следующим содержимом:
 ```
    CLIENT_ID=апра3jmMOxhZEXLAY5yhUMZ1MFOFTWQXCFPdIsv
    CLIENT_SECRET=12313
    TELEGRAM_TOKEN=536291вапрвар
    DATABASE_PASSWORD=fghfghjg6c55fJA
    DATABASE_HOST = fghjgfhjfghj
    DATABASE_PORT=13552
    GRANT_TYPE=client_credentials
 ```
   - **CLIENT_ID** токен к CMS (В данном боте используется moltin)
   - **CLIENT_SECRET** секретный ключ для получения кода авторизации к CMS (В данном боте используется moltin)
   - **TELEGRAM_TOKEN** токен к вашему телеграмм боту
   - **DATABASE_HOST** хост к базе данных Redit
   - **DATABASE_PASSWORD** пароль Redis
   - **DATABASE_PORT** port Redis
   - 
6. запустить бота **.\tg_fish_bot.py**
