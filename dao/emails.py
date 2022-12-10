from psycopg.errors import UniqueViolation
from config.dbconfig import pg_config
import psycopg2

class EmailsDAO:

    def __init__(self):
        connection_url = "dbname=%s user=%s password=%s port=%s host=%s" % (pg_config['Database'],
                                                                            pg_config['User'],
                                                                            pg_config['Password'],
                                                                            pg_config['Port'],
                                                                            pg_config['Host'])

        self.conn = psycopg2.connect(connection_url)

    def getAllEmails(self):
        cursor = self.conn.cursor()
        query = "SELECT * from Emails;"
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_my_outbox_Emails(self, user_email):
        print (user_email)
        cursor = self.conn.cursor()
        query = "select  e.message_id,e.message_title, e.message_body, e.message_date,e.sender_email, \
        				String_AGG(r.receiver_email,  ';') as receiver_email, \
        				e.reply_id, (us.user_name || ' ' || us.user_lastname) as sender_fullname, \
        				STRING_AGG(ur.user_name || ' ' || ur.user_lastname, ';') as receiver_fullname \
                        from emails as e \
                        left join receive as r on e.message_id = r.message_id \
                        left join users as us on e.sender_email = us.user_email \
        				left join users as ur on r.receiver_email = ur.user_email \
        				where e.sender_email = %s and e.reply_id is null and e.viewable_outbox = true \
        				group by e.message_id,e.message_title, e.message_body, e.message_date,e.sender_email, e.reply_id, \
        				sender_fullname \
                        union \
                        select max(e.message_id), max(e.message_title), max(e.message_body), max(e.message_date), \
        				max(e.sender_email), max(r.receiver_email), e.reply_id , max(us.user_name || ' ' || us.user_lastname) as sender_fullname, \
        				max(ur.user_name || ' ' || ur.user_lastname) as receiver_fullname \
                        from emails as e \
                        inner join receive as r on e.message_id = r.message_id \
                        inner join users as us on e.sender_email = us.user_email \
        				inner join users as ur on r.receiver_email = ur.user_email \
                        where e.sender_email = %s and e.reply_id is not null and e.viewable_outbox = true \
                        group by reply_id \
                        order by message_date desc;"
        cursor.execute(query, (user_email,user_email))
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_father(self, message_id):
        cursor = self.conn.cursor()
        query = "select reply_id from emails where message_id = %s;"
        cursor.execute(query, (message_id,))
        try:
            result = cursor.fetchone()[0]
            return result
        except:
            return None

    def get_message_info(self, message_id, user_email):
        cursor = self.conn.cursor()
        query = "select e.message_title, e.sender_email , r.receiver_email, e.message_body, r.is_read from emails as e  \
                 LEFT JOIN  receive as r on e.message_id = r.message_id \
                where e.message_id = %s and (e.sender_email=%s or r.receiver_email = %s);"
        cursor.execute(query, (message_id,user_email, user_email))
        try:
            result = cursor.fetchone()
            return result
        except:
            return None


    def is_premium(self, user_email):
        cursor = self.conn.cursor()
        query = "Select is_premium from users where user_email = %s;"
        cursor.execute(query, (user_email,))
        result = cursor.fetchone()[0]
        return result

    def insert(self, message_title, message_body, sender_email, reply_id=None):
        cursor = self.conn.cursor()
        if not reply_id:
            query = "INSERT INTO emails(message_title, message_body ,sender_email) \
                    VALUES (%s, %s,%s) returning message_id;"
            cursor.execute(query, (message_title, message_body ,sender_email,))
        else:
            query = "INSERT INTO emails(message_title, message_body, reply_id ,sender_email) \
                                    VALUES (%s, %s, %s,%s) returning message_id;"
            cursor.execute(query, (message_title, message_body, reply_id ,sender_email,))
        message_id = cursor.fetchone()[0]
        self.conn.commit()
        return message_id

    def get_message_and_responses_from_outbox(self, message_id, sender_email):
        cursor = self.conn.cursor()
        query = "select e.message_title, e.message_body, e.message_date, e.sender_email,us.user_name  ||' ' ||us.user_lastname as sender_fullname, \
                string_Agg(r.receiver_email,';') as receiver_email, \
                STRING_AGG(ur.user_name || ' ' || ur.user_lastname,';') as receiver_fullname, e.message_id \
                from emails as e \
                INNER JOIN  receive as r on e.message_id = r.message_id \
                INNER JOIN users as us on e.sender_email = us.user_email \
                INNER JOIN users as ur on r.receiver_email = ur.user_email \
                where (e.message_id = %s or e.reply_id = %s) and (e.sender_email = %s and viewable_outbox=true) \
                group by e.message_id,e.reply_id ,e.message_title, e.message_body, e.message_date, e.sender_email,us.user_name, \
                us.user_lastname, e.message_id \
				union \
                select e.message_title, e.message_body, e.message_date, e.sender_email,us.user_name  ||' ' ||us.user_lastname as sender_fullname, \
                string_Agg(r.receiver_email,';') as receiver_email, \
                STRING_AGG(ur.user_name || ' ' || ur.user_lastname,';') as receiver_fullname, e.message_id \
                from emails as e \
                INNER JOIN  receive as r on e.message_id = r.message_id \
                INNER JOIN users as us on e.sender_email = us.user_email \
                INNER JOIN users as ur on r.receiver_email = ur.user_email \
                where (e.message_id = %s or e.reply_id = %s) and (r.receiver_email = %s and viewable_inbox=true) \
                group by e.message_id,e.reply_id ,e.message_title, e.message_body, e.message_date, e.sender_email,us.user_name, \
                us.user_lastname, e.message_id \
                order by message_date asc;"
        reply_id = message_id
        cursor.execute(query, (message_id, reply_id, sender_email, message_id, reply_id, sender_email))
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_message_and_responses_from_inbox(self, message_id, receiver_email):
        cursor = self.conn.cursor()
        query = "select e.message_title, e.message_body, e.message_date, e.sender_email,us.user_name  ||' ' ||us.user_lastname as sender_fullname, \
                        string_Agg(r.receiver_email,';') as receiver_email, \
                        STRING_AGG(ur.user_name || ' ' || ur.user_lastname,';') as receiver_fullname, e.message_id, r.category \
                        from emails as e \
                        INNER JOIN  receive as r on e.message_id = r.message_id \
                        INNER JOIN users as us on e.sender_email = us.user_email \
                        INNER JOIN users as ur on r.receiver_email = ur.user_email \
                        where (e.message_id = %s or e.reply_id = %s) and (e.sender_email = %s and viewable_outbox=true) \
                        group by e.message_id,e.reply_id ,e.message_title, e.message_body, e.message_date, e.sender_email,us.user_name, \
                        us.user_lastname, e.message_id, r.category \
        				union \
                        select e.message_title, e.message_body, e.message_date, e.sender_email,us.user_name  ||' ' ||us.user_lastname as sender_fullname, \
                        string_Agg(r.receiver_email,';') as receiver_email, \
                        STRING_AGG(ur.user_name || ' ' || ur.user_lastname,';') as receiver_fullname, e.message_id, r.category \
                        from emails as e \
                        INNER JOIN  receive as r on e.message_id = r.message_id \
                        INNER JOIN users as us on e.sender_email = us.user_email \
                        INNER JOIN users as ur on r.receiver_email = ur.user_email \
                        where (e.message_id = %s or e.reply_id = %s) and (r.receiver_email = %s and viewable_inbox=true) \
                        group by e.message_id,e.reply_id ,e.message_title, e.message_body, e.message_date, e.sender_email,us.user_name, \
                        us.user_lastname, e.message_id, r.category \
                        order by message_date asc;"
        reply_id = message_id
        cursor.execute(query, (message_id, reply_id, receiver_email, message_id, reply_id, receiver_email))
        result = []
        for row in cursor:
            result.append(row)
        return result
    def update_message(self, message_id, message_body):
        cursor = self.conn.cursor()

        print(message_id, message_body)
        query = "update emails set message_body=%s\
                                    where message_id = %s"
        cursor.execute(query, (message_body, str(message_id)))
        self.conn.commit()
        return True

    def update_title(self, message_id, message_title):
        cursor = self.conn.cursor()

        query = "update emails set message_title= %s \
                                    where message_id = %s or reply_id = %s;"
        cursor.execute(query, (message_title, str(message_id),str(message_id)))
        self.conn.commit()
        return True

    def delete_message_in_inbox(self, message_id):
        cursor = self.conn.cursor()
        query = "UPDATE receive SET viewable_inbox = false where message_id = %s;"
        cursor.execute(query, (message_id,))
        self.conn.commit()
        print("Se borro")
        return True
    def delete_message_in_outbox(self,message_id ):
        cursor = self.conn.cursor()
        query = "UPDATE emails SET viewable_outbox = false where message_id = %s;"
        cursor.execute(query, (message_id,))
        self.conn.commit()
        print("Se borro")
        return True
    def delete_in_outbox(self, message_id, sender_email):
        cursor = self.conn.cursor()
        query = "UPDATE emails \
                SET viewable_outbox = false from (select e.* from emails as e \
                left join receive as r on r.message_id = e.message_id \
                where e.sender_email = %s and (e.message_id = %s or e.reply_id=%s)) as sub \
                WHERE emails.message_id = sub.message_id;"
        cursor.execute(query, (sender_email, message_id, message_id))
        self.conn.commit()
        return True

    def delete_in_inbox(self, message_id, receiver_email):
        cursor = self.conn.cursor()
        query = "UPDATE receive \
                SET viewable_inbox = false from (select e.* from emails as e \
                left join receive as r on r.message_id = e.message_id \
                where r.receiver_email = %s and (e.message_id = %s or e.reply_id=%s)) as sub \
                WHERE receive.message_id = sub.message_id;"
        cursor.execute(query, (receiver_email, message_id, message_id))
        self.conn.commit()
        return True

    def delete_premium(self, message_id):
        cursor = self.conn.cursor()
        query = "begin transaction; \
                update emails set viewable_outbox = false \
                where message_id = %s; \
                update receive set viewable_inbox = false \
                where message_id = %s; \
                commit;"
        cursor.execute(query, (message_id, message_id))
        self.conn.commit()
        return True



### SATATITICS
    def top_ten_outbox(self):
        cursor = self.conn.cursor()
        query = "select sender_email, count(message_id) from emails " \
                "where viewable_outbox = true and sender_email != 'support@upr.edu' " \
                "group by sender_email" \
                " order by count(message_id) desc limit 10;"
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def top_ten_inbox(self):
        cursor = self.conn.cursor()
        query = "select receiver_email, count(message_id) from receive \
                where viewable_inbox = true and receiver_email != 'support@upr.edu'\
                 group by receiver_email  \
                order by count(message_id) desc limit 10;"
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result
    def email_with_most_replies_user(self,sender_email):
        cursor = self.conn.cursor()
        query = "SELECT e.message_id, e.message_title, e.message_body,\
				e.message_date, sub.number_of_replies \
                FROM emails as e, ( \
                    select e.reply_id, count(e.message_id) as number_of_replies \
                    from emails as e \
                    inner join receive as r on r.message_id = e.message_id \
                    where ((e.sender_email = %s and viewable_outbox = true) \
					or (r.receiver_email = %s and viewable_inbox = true)) \
					and reply_id is not null \
                    group by e.reply_id \
                    order by number_of_replies desc, reply_id desc \
					limit 1) as sub \
                WHERE e.message_id = sub.reply_id;"
        cursor.execute(query, (sender_email,sender_email))
        result = cursor.fetchone()
        return result
    def email_with_most_replies(self):
        cursor = self.conn.cursor()
        query = "SELECT e.message_id, e.message_title, e.message_body, e.message_date, sub.number_of_replies \
                    FROM emails as e, ( \
                        select e.reply_id, count(e.message_id) as number_of_replies \
                        from emails as e \
                        left join receive as r on r.message_id = e.message_id \
                        where e.reply_id is not null and  viewable_outbox = true \
                        group by e.reply_id \
                        order by number_of_replies desc, reply_id desc \
                        limit 1) as sub \
                    WHERE e.message_id = sub.reply_id;"
        cursor.execute(query)
        result = cursor.fetchone()
        return result
