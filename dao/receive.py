from config.dbconfig import pg_config
import psycopg2
from flask import jsonify


class ReceivedDAO:

    def __init__(self):
        connection_url = "dbname=%s user=%s password=%s port=%s host=%s" % (pg_config['Database'],
                                                                            pg_config['User'],
                                                                            pg_config['Password'],
                                                                            pg_config['Port'],
                                                                            pg_config['Host'])


        self.conn = psycopg2.connect(connection_url)

    def insert(self, receiver_email, message_id):
        cursor = self.conn.cursor()
        message_id = str(message_id)
        query = "INSERT INTO Receive(receiver_email, message_id) VALUES (%s, %s);"
        cursor.execute(query, (receiver_email, message_id,))
        # message_id = cursor.fetchone()[0]
        self.conn.commit()
        return True

    def category_user(self, receiver_email):
        cursor = self.conn.cursor()
        query = "select category from receive  \
                where receiver_email= %s \
                group by category;"
        cursor.execute(query, (receiver_email,))
        result = []
        for row in cursor:
            result.append(row)
        return result

    def getAllReceived(self):
        cursor = self.conn.cursor()
        query = "SELECT * from Receive;"
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def getEmailByReceiver(self, receiver_email):
        cursor = self.conn.cursor()

        query = "select  e.message_id,e.message_title, e.message_body, e.message_date, \
        e.sender_email, r.receiver_email, r.is_read, \
		is_friend (e.sender_email, r.receiver_email) as sender_is_friend, r.category , e.reply_id \
        from emails as e \
        inner join receive as r on e.message_id = r.message_id \
        where r.receiver_email = %s and reply_id is null and viewable_inbox = true \
        union \
        select e.message_id,e.message_title, e.message_body, e.message_date, \
                e.sender_email, r.receiver_email, r.is_read, \
                is_friend (e.sender_email, r.receiver_email) as sender_is_friend, r.category , e.reply_id \
                from emails as e \
                natural inner join receive as r \
                where message_id in (select max(e.message_id) \
                                        from emails as e \
                                        inner join receive as r on e.message_id = r.message_id \
                                        where r.receiver_email = %s and reply_id is not null and viewable_inbox = true \
                                        group by reply_id)\
        order by message_date desc;"

        cursor.execute(query, (receiver_email,receiver_email))
        result = []
        for row in cursor:
            result.append(row)
        return result

    def searchInboxByUser(self, receiver_email, sender_email):
        cursor = self.conn.cursor()
        query = "select  e.message_id,e.message_title, e.message_body, e.message_date, \
        e.sender_email, r.receiver_email, r.is_read, \
		is_friend (e.sender_email, r.receiver_email) as sender_is_friend, r.category , e.reply_id \
        from emails as e \
        inner join receive as r on e.message_id = r.message_id \
        where r.receiver_email = %s and reply_id is null and viewable_inbox = true \
        and sender_email = %s \
        union \
        select e.message_id,e.message_title, e.message_body, e.message_date, \
                e.sender_email, r.receiver_email, r.is_read, \
                is_friend (e.sender_email, r.receiver_email) as sender_is_friend, r.category , e.reply_id \
                from emails as e \
                natural inner join receive as r \
                where message_id in (select max(e.message_id) \
                                        from emails as e \
                                        inner join receive as r on e.message_id = r.message_id \
                                        where r.receiver_email = %s and reply_id is not null and viewable_inbox = true \
                                        and sender_email = %s \
                                        group by reply_id) \
        order by message_date desc;"
        cursor.execute(query, (receiver_email, sender_email,receiver_email, sender_email))
        result = []
        for row in cursor:
            result.append(row)
        return result

    def readInboxEmail(self, receiver_email, message_id):
        cursor = self.conn.cursor()

        query = "update receive set is_read = true " \
                "where receive.receiver_email = %s and receive.message_id = %s " \
                "returning *"
        cursor.execute(query, (receiver_email, message_id))
        self.conn.commit()
        result = []
        for row in cursor:
            result.append(row)
        return result

    def is_read(self, receiver_email, message_id):
        cursor = self.conn.cursor()
        query = "Select is_read from receive where receiver_email = %s and message_id =%s"
        cursor.execute(query, (receiver_email, message_id))
        try :
            result = cursor.fetchone()[0]
            return result
        except:
            return None


    def update_category(self, user_email, message_id, category):
        cursor = self.conn.cursor()
        query = "UPDATE receive \
                SET category = %s from (select r.* from emails as e \
                                inner join receive as r on r.message_id = e.message_id \
                                where r.receiver_email = %s and (e.message_id = %s or e.reply_id=%s)) as sub \
                WHERE \
                  receive.message_id = sub.message_id;"
        cursor.execute(query, (category, user_email, message_id, message_id))
        self.conn.commit()
        return True

    def getEmailByCategoryFromReceiver(self, receiver_email, category):
        cursor = self.conn.cursor()
        query = "select  e.message_id,e.message_title, e.message_body, e.message_date, \
        e.sender_email, r.receiver_email, r.is_read, \
		is_friend (e.sender_email, r.receiver_email) as sender_is_friend, r.category , e.reply_id \
        from emails as e \
        inner join receive as r on e.message_id = r.message_id \
        where r.receiver_email = %s and reply_id is null and viewable_inbox = true \
        and category = %s \
        union \
        select e.message_id,e.message_title, e.message_body, e.message_date, \
                e.sender_email, r.receiver_email, r.is_read, \
                is_friend (e.sender_email, r.receiver_email) as sender_is_friend, r.category , e.reply_id \
                from emails as e \
                natural inner join receive as r \
                where message_id in (select max(e.message_id) \
                                        from emails as e \
                                        inner join receive as r on e.message_id = r.message_id \
                                        where r.receiver_email = %s and reply_id is not null and viewable_inbox = true \
                                        and category = %s \
                                        group by reply_id) \
        order by message_date desc;"
        cursor.execute(query, (receiver_email, category, receiver_email, category))
        result = []
        for row in cursor:
            result.append(row)
        return result

    def getEmailByCategory(self, category):
        cursor = self.conn.cursor()
        query = "select emails.message_id, emails.message_title, emails.message_body, emails.message_date,  \
                emails.sender_email, receive.receiver_email, receive.is_read,  \
                is_friend (emails.sender_email, receive.receiver_email) as sender_is_friend, receive.category, emails.reply_id  \
                from ((emails inner join users on emails.sender_email = users.user_email)  \
                inner join receive on emails.message_id = receive.message_id)  \
                where (receive.category = %s and receive.viewable_inbox = true);"
        cursor.execute(query, (category,))
        result = []
        for row in cursor:
            result.append(row)
        return result


    def getReceiverEmailByRead(self, receiver_email, is_read):
        cursor = self.conn.cursor()
        if (is_read== 'true' or is_read=='read'):
            query = "select emails.message_id, emails.message_title, emails.message_body, emails.message_date, " \
                    "emails.sender_email, receive.receiver_email, receive.is_read, " \
                    "is_friend (emails.sender_email, receive.receiver_email) as sender_is_friend, receive.category , emails.reply_id " \
                    "from ((emails inner join users on emails.sender_email = users.user_email) " \
                    "inner join receive on emails.message_id = receive.message_id) " \
                    "where receive.receiver_email =%s and is_read = %s and receive.viewable_inbox = true"
            cursor.execute(query, (receiver_email, is_read,))
            result = []
            for row in cursor:
                result.append(row)
            return result
        elif (is_read=='false' or is_read=='unread'):
            query = "select emails.message_id, emails.message_title, emails.message_body, emails.message_date, " \
                    "emails.sender_email, receive.receiver_email, receive.is_read, " \
                    "is_friend (emails.sender_email, receive.receiver_email) as sender_is_friend , receive.category , emails.reply_id " \
                    "from ((emails inner join users on emails.sender_email = users.user_email) " \
                    "inner join receive on emails.message_id = receive.message_id) " \
                    "where receive.receiver_email =%s and is_read = %s and receive.viewable_inbox = true"
            cursor.execute(query, (receiver_email, is_read,))
            result = []
            for row in cursor:
                result.append(row)
            return result

#### STATISTICS

    def getTopSenderEmail(self, receiver_email):
        cursor = self.conn.cursor()
        query = "select emails.sender_email, count(emails.sender_email) " \
                "from emails inner join receive  " \
                "on emails.message_id = receive.message_id " \
                "where receive.receiver_email= %s and viewable_outbox = true and sender_email != 'support@upr.edu'" \
                "GROUP BY emails.sender_email " \
                "HAVING COUNT(emails.sender_email) >= 1 " \
                "order by count desc " \
                "limit 5;"

        cursor.execute(query, (receiver_email,))
        result = []
        for row in cursor:
            result.append(row)
        return result
    def getTopReceiversEmail(self, sender_email):
        cursor = self.conn.cursor()
        query = "select receive.receiver_email, count(receive.receiver_email) " \
                "from emails inner join receive " \
                "on emails.message_id = receive.message_id " \
                "where emails.sender_email= %s and viewable_inbox = true " \
                "GROUP BY receive.receiver_email " \
                "HAVING COUNT(receive.receiver_email) >= 1 " \
                "order by count desc " \
                "limit 5;"
        cursor.execute(query, (sender_email,))
        result = []
        for row in cursor:
            result.append(row)
        return result
    def getEmailsWithMostRecepients(self):
        cursor = self.conn.cursor()
        query = "SELECT emails.message_id, emails.message_title, emails.message_body, emails.message_date, " \
                "COUNT(emails.message_id) " \
                "from emails inner join receive " \
                "on emails.message_id = receive.message_id " \
                "where emails.sender_email != 'support@upr.edu' and viewable_outbox = true " \
                "GROUP BY emails.message_id, emails.message_title, emails.message_body, emails.message_date " \
                "HAVING COUNT(emails.message_id) >= 1 " \
                "order by count desc " \
                "limit 1;"
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def getEmailsWithMostRecepientsByUser(self, sender_email):
        cursor = self.conn.cursor()
        query = "SELECT emails.message_id, emails.message_title, emails.message_body, emails.message_date, " \
                "COUNT(emails.message_id) " \
                "from emails inner join receive " \
                "on emails.message_id = receive.message_id " \
                "where emails.sender_email=%s and viewable_outbox = true " \
                "GROUP BY emails.message_id, emails.message_title, emails.message_body, emails.message_date " \
                "HAVING COUNT(emails.message_id) >= 1 " \
                "order by count desc " \
                "limit 1;"
        cursor.execute(query, (sender_email,))
        result = []
        for row in cursor:
            result.append(row)
        return result


