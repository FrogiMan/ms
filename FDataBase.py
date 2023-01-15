import math
import sqlite3
import time


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()


    def getMenu(self):
        sql = '''SELECT * FROM posts '''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print('Ошибка чтения из БД ', )
            return False
        return []

    def addPost(self, name, email, post, message):
        try:
            tm = math.floor(time.time())
            self.__cur.execute('INSERT INTO posts VALUES (NULL, ?,?,?,?,?)', (name, email, post, message, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка добавления статьи в БД ' + str(e))
        return True

    def getPostsAnonce(self):
        try:
            self.__cur.execute(f"SELECT id, name,email,post,message FROM posts ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))

        return []

    def delPost(self, id=0):
        try:
            if id == 0:
                self.__cur.execute('DELETE FROM posts')
        except:
            print('Ошибка удаления меню в БД ' + str())
            return False
        return []

