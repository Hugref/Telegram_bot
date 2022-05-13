import sqlite3


class SQLighter1:
    def __init__(self, database_file):
        "Подключаемся к БД и сохраняем курсор соединения"
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def add_bar(self, bar_title, bar_description, bar_metro, bar_url, bar_users):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO bars (bar_title, bar_description, bar_metro, bar_url, bar_users) VALUES (?, ?, ?, ?, ?)",
                (bar_title, bar_description, bar_metro, bar_url, bar_users))

    def get_bar_from_title(self, bar_title):
        with self.connection:
            return self.cursor.execute("SELECT * from bars WHERE bar_title = ?", (bar_title,)).fetchall()

    def get_bar_from_metro(self, bar_metro):
        with self.connection:
            return self.cursor.execute("SELECT * from bars WHERE bar_metro = ?", (bar_metro,)).fetchall()

    def get_bars_users(self, bar_id):
        with self.connection:
            return self.cursor.execute("SELECT bar_users from bars WHERE bar_id = ?", (bar_id,)).fetchall()

    def into_bar(self, bar_id, bar_users):
        with self.connection:
            return self.cursor.execute("UPDATE bars SET bar_users = bar_users || ? WHERE bar_id = ?",
                                       (bar_users, bar_id)), self.connection.commit()

    def update_bar(self, bar_id):
        with self.connection:
            return self.cursor.execute("UPDATE bars SET bar_users = '' WHERE bar_id = ?",
                                       (bar_id,)), self.connection.commit()

    def get_bar_id(self, bar_title):
        with self.connection:
            return self.cursor.execute("SELECT bar_id from bars WHERE bar_title=?", (bar_title,)).fetchall()

    def get_reg_in_bar(self, bar_id, username):
        with self.connection:
            return str(self.cursor.execute("SELECT bar_users from bars WHERE bar_id=?", (bar_id,)).fetchall()[0]).find(
                username)

    def clear_user_in_bar(self, bar_id, username):
        with self.connection:
            s = self.cursor.execute("SELECT bar_users from bars WHERE bar_id = ?", (bar_id,)).fetchall()[0]
            s = list(s)
            s = s[0]
            s = str(s.split(' '))[1:-3]
            s = s.replace("'" + str(username) + "'," + " ", "")
            s = s.replace("'", "")
            s = s.replace(",", "")
            return s

    def clear_all_bars(self):
        with self.connection:
            return self.cursor.execute("UPDATE bars SET bar_users = '' "), self.connection.commit()

    def update_bar_no_user(self, bar_id, s):
        with self.connection:
            return self.cursor.execute("UPDATE bars SET bar_users = ? WHERE bar_id = ?",
                                       (s, bar_id,)), self.connection.commit()

    def who_is_in_bar(self, bar_id):
        with self.connection:
            s = str(self.cursor.execute("SELECT bar_users from bars WHERE bar_id = ?", (bar_id,)).fetchall())
            return s[3:-4]

    def bar_title_from_bar_id(self, bar_id):
        with self.connection:
            return self.cursor.execute("SELECT * from bars WHERE bar_id = ?", (bar_id,)).fetchall()

    def close(self):
        "Закрываем соединение с бд"
        self.connection.close()
