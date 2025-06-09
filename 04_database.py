import sqlite3
from wat import wat

# Создаем подключение к базе данных (файл my_database.db будет создан)
connection = sqlite3.connect('database_people.db')

cursor = connection.cursor()

# Создаем таблицу Users
# FIXME: telegram_id должно быть уникальным
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    patronymic_name TEXT,
    grade INTEGER NOT NULL,
    class_number INTEGER NOT NULL,
    telegram_id TEXT 
)
''')

a = cursor.execute(
    'INSERT INTO users (first_name, last_name, patronymic_name, grade, class_number, telegram_id) VALUES (?, ?, ?, ?, ?, ?)',
    ('Антон', "Фильченков", None, 10, 4, None),
)

user_id = a.lastrowid
assert user_id

cursor.execute('''
CREATE TABLE IF NOT EXISTS users_settings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    news BOOLEAN NOT NULL,
    message BOOLEAN NOT NULL
)
''')

# wat / a.lastrowid
# wat(a.lastrowid)

b = cursor.execute(
    'INSERT INTO users_settings (user_id, news, message) VALUES (?, ?, ?)',
    (user_id, True, True),
)

print(type(a))
print(a)

# Сохраняем изменения и закрываем соединение
connection.commit()
connection.close()

# #UPDATE users_settings
# 	SET
# 		news = FALSE
# 	WHERE
# 		user_id = (SELECT id FROM users WHERE telegram_id = "250804059");


# SELECT * FROM users_settings WHERE
#    user_id = (SELECT id FROM users WHERE telegram_id = "250804059");

# SELECT * FROM users_settings s
#   INNER JOIN users u ON
#     u.id = s.user_id
#   WHERE telegram_id = "250804059";