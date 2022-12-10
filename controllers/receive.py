from flask import jsonify
from dao.emails import EmailsDAO
from dao.receive import ReceivedDAO


class ReceivedController:

    def build_received_dict(self, row):
        result = {}
        result['receiver_email'] = row[0]
        result['message_id'] = row[1]
        result['category'] = row[2]
        result['is_read'] = row[3]
        result['viewable_inbox'] = row[4]
        return result
    def build_message_dict(self, row):
        result = {}
        result['message_id'] = row[0]
        result['message_title'] = row[1]
        result['message_body'] = row[2]
        result['message_date'] = row[3]
        result['sender_email'] = row[4]
        result['receiver_email'] = row[5]
        result['is_read'] = row[6]
        result['sender_is_friend'] = row[7]
        result['category'] = row[8]
        result['reply_id'] = row[9]
        return result
    def build_inbox_dict(self, row):
        result = {}
        result['message_id'] = row[0]
        result['sender_email'] = row[1]
        result['message_title'] = row[2]
        result['message_date'] = row[3]
        result['is_read'] = row[4]
        result['sender_is_friend'] = row[5]

        return result

    def build_statistic_dict(self, row):
        result = {}
        result['users_email'] = row[0]
        result['message_count'] = row[1]

        return result
    def build_RecipientStat_dict(self, row):
        result = {}
        result['message_id'] = row[0]
        result['message_title'] = row[1]
        result['message_body'] = row[2]
        result['message_date'] = row[3]
        result['number_recipients'] = row[4]
        return result

    def build_category(self, row):
        result = {}

        result['value'] = row[0]
        result['text'] = row[0]
        return result

    def get_category_user(self, user_email):
        dao = ReceivedDAO()
        category_list = dao.category_user(user_email)
        result_list = []
        print(category_list)
        if category_list:
            for row in category_list:
                result = self.build_category(row)
                result_list.append(result)
            return jsonify(Category=result_list), 200
        else:
            return jsonify(Category="not categories"), 404

    def getAllReceived(self):
        dao = ReceivedDAO()
        emails_list = dao.getAllReceived()
        result_list = []
        for row in emails_list:
            result = self.build_received_dict(row)
            result_list.append(result)
        return jsonify(Receive = result_list), 200

    def getEmailByReceiver(self, receiver_email):
        dao = ReceivedDAO()
        receiver_list = dao.getEmailByReceiver(receiver_email)
        result_list=[]
        if not receiver_list:
            return jsonify(Error="No email by such receiver"), 404
        else:
            for row in receiver_list:
                result = self.build_message_dict(row)
                result_list.append(result)
        return jsonify(Receive=result_list), 200

    def getReceivedByRead(self, is_read):
        dao = ReceivedDAO()
        read_list = dao.getReceivedByRead(is_read)
        result_list = []
        if not read_list:
            return jsonify(Error="Method not allowed, readStatus accepts true, false, read or unread"), 405
        else:
            for row in read_list:
                result = self.build_message_dict(row)
                result_list.append(result)
            return jsonify(Receive = result_list), 200

    def searchInboxByUser(self, receiver_email, sender_email):
        dao = ReceivedDAO()
        receiver_list = dao.searchInboxByUser(receiver_email, sender_email)
        result_list=[]
        if not receiver_list:
            return jsonify(Error="No email by such receiver"), 404
        else:
            for row in receiver_list:
                result = self.build_message_dict(row)
                result_list.append(result)
        return jsonify(Receive=result_list) , 200

    def searchInboxBycategory(self, user_email, category):
        dao = ReceivedDAO()
        receiver_list = dao.searchInboxBycategory(user_email, category)
        result_list=[]
        if not receiver_list:
            return jsonify(Error="No email by such emails by category " + category), 404
        else:
            for row in receiver_list:
                result = self.build_message_dict(row)
                result_list.append(result)
        return jsonify(Receive=result_list) , 200

    def read_Email(self, receiver_email, message_id):
        dao = ReceivedDAO()
        receiver_list = dao.readInboxEmail(receiver_email, message_id)
        if not receiver_list:
            return None
        else:
            return receiver_list
    def is_read(self, receiver_email, message_id):
        return ReceivedDAO().is_read(receiver_email, message_id)

    def update_category(self, user_email, message_id, category):
        dao = ReceivedDAO()
        dao_email = EmailsDAO()
        result = dao_email.get_message_info(message_id, user_email)
        if result == None:
            return jsonify(Error="AllMessage not found"), 404
        reply_id = dao_email.get_father(message_id)
        print(reply_id)
        if not reply_id:
            reply_id = message_id
        sender_email = result[1]
        receiver_email = result[2]
        if sender_email:
            result = dao.update_category(user_email, reply_id,category)
            if result:
                return jsonify(Receive="Changes to category were made "), 201
        else:
            return jsonify(Error="AllMessage not found"), 400

    def getEmailByCategoryFromReceiver(self, receiver_email, category):
        dao = ReceivedDAO()
        print(category)
        emails_list = dao.getEmailByCategoryFromReceiver(receiver_email, category)
        result_list = []
        if not emails_list:
            return jsonify(Error="Category not found"), 404
        else:
            for row in emails_list:
                result = self.build_message_dict(row)
                result_list.append(result)
            return jsonify(Receive=result_list) , 200

    def getEmailByCategory(self, category):
        dao = ReceivedDAO()
        emails_list = dao.getEmailByCategory(category)
        result_list = []
        if not emails_list:
            return jsonify(Error="Category not found"), 404
        else:
            for row in emails_list:
                result = self.build_message_dict(row)
                result_list.append(result)
            return jsonify(Receive=result_list) , 200

    def getReceiverEmailByRead(self, receiver_email, is_read):
        dao = ReceivedDAO()
        read_list = dao.getReceiverEmailByRead(receiver_email, is_read)
        result_list = []
        if not read_list:
            return jsonify(Error="Method not allowed, readStatus accepts true, false"), 405
        else:
            for row in read_list:
                result = self.build_message_dict(row)
                result_list.append(result)
            return jsonify(Receive = result_list)

##### STATITICS
    def getTopSenderEmail(self, receiver_email):
        dao = ReceivedDAO()
        emails_list = dao.getTopSenderEmail(receiver_email)
        result_list = []
        if not emails_list:
            return jsonify(Error="Category not found"), 404
        else:
            for row in emails_list:
                result = self.build_statistic_dict(row)
                result_list.append(result)
            return jsonify(TopFiveSenders=result_list)

    def getTopReceiversEmail(self, sender_email):
        dao = ReceivedDAO()
        emails_list = dao.getTopReceiversEmail(sender_email)
        result_list = []
        if not emails_list:
            return jsonify(Error="No receivers"), 404
        else:
            for row in emails_list:
                result = self.build_statistic_dict(row)
                result_list.append(result)
            return jsonify(TopFiveReceivers=result_list)

    def getEmailsWithMostRecepients(self):
        dao = ReceivedDAO()
        emails_list = dao.getEmailsWithMostRecepients()
        if emails_list:
            for row in emails_list:
                result = self.build_RecipientStat_dict(row)
            return jsonify(Receive = result), 200
        else:
            return jsonify(Receive='not recipients'), 404

    def getEmailsWithMostRecepientsByUser(self, sender_email):
        dao = ReceivedDAO()
        emails_list = dao.getEmailsWithMostRecepientsByUser(sender_email)

        if not emails_list:
            return jsonify(Error="No emails in database"), 404
        for row in emails_list:
            result = self.build_RecipientStat_dict(row)
        return jsonify(Receive = result)

