from config.dbconfig import pg_config
from psycopg2.errors import UniqueViolation
import psycopg2

class UsersDAO:
    def __init__(self):

        connection_url = "dbname=%s user=%s password=%s port=%s host=%s"% (pg_config['Database'],
                                                                            pg_config['User'],
                                                                            pg_config['Password'],
                                                                            pg_config['Port'],
                                                                            pg_config['Host'])
        self.conn = psycopg2.connect(connection_url)

    def getAllUsers(self):
        cursor = self.conn.cursor()
        query = "SELECT user_email, user_password, is_premium, user_name, user_lastname FROM Users;"
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def insert(self, user_email,user_password, is_premium, user_name, user_lastname):
        cursor = self.conn.cursor()
        try:
            query = "INSERT INTO users(user_email, user_password, is_premium, user_name, user_lastname) VALUES (lower(%s), %s, %s, %s, %s);"
            cursor.execute(query, (user_email,user_password, is_premium, user_name, user_lastname,))
            self.conn.commit()
            return True
        except UniqueViolation as e:
            return False

    def get_user_password(self, user_email):
        cursor = self.conn.cursor()
        try:
            query = "Select user_password from users where user_email=%s;"
            cursor.execute(query, (user_email,))
            result = cursor.fetchone()[0]
            return result
        except UniqueViolation as e:
            return None

    def get_user(self, user_email):
        cursor = self.conn.cursor()
        query = "select lower(user_email), user_name, user_lastname from users where user_email = lower(%s);"
        cursor.execute(query, (user_email,))
        try:
            result = cursor.fetchone()
            return result
        except Exception as e:
            print(e)
            return False

    def update_user(self, user_email, user_password = None, is_premium = None, user_name= None, user_lastname= None):
        cursor = self.conn.cursor()
        try:
            if user_password:
                query = "UPDATE users set user_password = %s where user_email = lower(%s) RETURNING *;"
                cursor.execute(query, (user_password, user_email))
            if is_premium:
                query = "UPDATE users set is_premium = %s where user_email = lower(%s) RETURNING *;"
                cursor.execute(query, (is_premium, user_email))
            if user_name:
                query = "UPDATE users set user_name = %s where user_email = lower(%s) RETURNING *;"
                cursor.execute(query, (user_name, user_email))
            if user_lastname:
                query = "UPDATE users set user_lastname = %s where user_email = lower(%s) RETURNING *;"
                cursor.execute(query, (user_lastname, user_email))

            result = cursor.fetchone()
            self.conn.commit()
            return result
        except UniqueViolation as e:
            return False

    def delete_user(self, user_email):
        cursor = self.conn.cursor()
        query = "delete from users where user_email = lower(%s);"
        try:
            cursor.execute(query, (user_email,))
            self.conn.commit()
            return True
        except Exception as e:
            print(e)
            return False





