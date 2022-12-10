from flask import jsonify

from config.dbconfig import pg_config
import psycopg2


class FollowsDAO:

    def __init__(self):

        connection_url = "dbname=%s user=%s password=%s port=%s host=%s"% (pg_config['Database'],
                                                                            pg_config['User'],
                                                                            pg_config['Password'],
                                                                            pg_config['Port'],
                                                                            pg_config['Host'])
        print(connection_url)
        self.conn = psycopg2.connect(connection_url)

    # works
    def getMyFollows(self,user_email):
        cursor = self.conn.cursor()
        query = "SELECT f.user_email, User_friends_emails, user_name, user_lastname from Follows as f \
                INNER JOIN users as u on u.user_email = f.user_friends_emails \
                where f.user_email = %s ;"
        cursor.execute(query, (user_email,))
        result = []
        for row in cursor:
            result.append(row)
        return result
    #works
    def getMyFollowers(self, user_email):
        cursor = self.conn.cursor()
        query = "SELECT user_email, User_friends_emails from Follows where User_friends_emails = %s;"
        cursor.execute(query, (user_email,))
        result = []
        for row in cursor:
            result.append(row)
        return result

    def getAllFollows(self):
        cursor = self.conn.cursor()
        query = "SELECT * from Follows"
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result
    def get_follower_row(self, user_email, user_friends_emails):
        cursor = self.conn.cursor()
        query = "SELECT user_email, User_friends_emails from Follows where User_email = %s and User_friends_emails = %s;"
        cursor.execute(query, (user_email, user_friends_emails,))
        result = cursor.fetchone()
        return result
    def addFollower(self, user_email, user_friends_emails):
        cursor = self.conn.cursor()
        query = "insert  into Follows(user_email, user_friends_emails) values (%s, %s);"
        cursor.execute(query, (user_email, user_friends_emails,))
        # result = cursor.fetchall()
        # print(result)
        self.conn.commit()
        return True

    def removeFollow(self, user_email, user_friends_emails):
        cursor = self.conn.cursor()
        query = "delete from Follows where user_email = %s and user_friends_emails = %s;"
        cursor.execute(query, (user_email, user_friends_emails,))
        self.conn.commit()
        return 'Deleted'

    def count_my_friends(self, user_email):
        cursor = self.conn.cursor()
        query = "select count(user_friends_emails) from follows where user_email=%s;"
        cursor.execute(query, (user_email,))
        result = cursor.fetchone()
        return result
