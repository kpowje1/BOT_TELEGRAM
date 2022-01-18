# Telegram_BOT
Save picture and voice message and get public link

Для сохранения данных используется PostgreSQL на сервере. 
# nano /etc/postgresql/14/main/pg_hba.conf 
Для успешного подключения к БД используется конфигурация через имя пользователя БД и пароль. Поэтому необходимо отредактировать файл pg_hba.conf.
Найти его можно по пути /etc/postgresql/14/main/pg_hba.conf, где 14 - версия ПО.
Запись, которую необходимо добавить под записью с юзером postgres: local all db_user_name password
