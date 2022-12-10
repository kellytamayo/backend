from flask import jsonify
from dao.emails import EmailsDAO
from dao.receive import ReceivedDAO
from dao.users import UsersDAO
from controllers.receive import ReceivedController

class EmailController:

    def buld_emails_dict (self,row):
        result = {}
        result['message_id'] = row[0]
        result['message_title'] = row[1]
        result['message_body'] = row[2]
        result['message_date'] = row[3]
        result['sender_email'] = row[4]
        result['reply_id'] = row[5]
        result['viewable_outbox'] = row[6]
        return result

    def build_email_dict(self, row):
        result = {}
        result['reply_id'] = row[0]
        result['message_id'] = row[1]
        result['sender_email'] = row[2]
        result['receiver_email'] = row[3]
        result['message_title'] = row[4]
        result['message_date'] = row[5]
        result['message_body'] = row[6]
        return result

    def build_outbox_dict(self, row):
        result = {}
        result['message_id'] = row[0]
        result['message_title'] = row[1]
        result['message_body'] = row[2]
        result['message_date'] = row[3]
        result['sender_email'] = row[4]
        result['receiver_email'] = row[5]
        result['reply_id'] = row[6]
        result['sender_fullname'] = row[7]
        result['receiver_fullname'] = row[8]
        return result

    def build_message_inbox_dict(self, row):
        result = {}
        result['message_title'] = row[0]
        result['message_body'] = row[1]
        result['message_date'] = row[2]
        result['sender_email'] = row[3]
        result['sender_fullname'] = row[4]
        result['receiver_email'] = row[5]
        result['receiver_f'] = row[6]
        result['message_id'] = row[7]
        result['category'] = row[8]
        return result
    def build_message_outbox_dict(self, row):
        result = {}
        result['message_title'] = row[0]
        result['message_body'] = row[1]
        result['message_date'] = row[2]
        result['sender_email'] = row[3]
        result['sender_fullname'] = row[4]
        result['receiver_email'] = row[5]
        result['receiver_f'] = row[6]
        result['message_id'] = row[7]
        return result

    def build_top_dict(self, row):
        result = {}
        result['user_email'] = row[0]
        result['message_count'] = row[1]
        return result

    def build_replies_dict(self, row):
        result = {}
        result['message_id'] = row[0]
        result['message_title'] = row[1]
        result['message_body'] = row[2]
        result['message_date'] = row[3]
        result['number_of_replies'] = row[4]
        return result


    def getAllEmails(self):
        dao = EmailsDAO()
        emails_list = dao.getAllEmails()
        result_list = []
        for row in emails_list:
            result = self.buld_emails_dict(row)
            result_list.append(result)
        return jsonify(Emails = result_list) , 201

    def get_my_outbox_Emails(self, user_email):
        dao = EmailsDAO()
        emails_list = dao.get_my_outbox_Emails(user_email)
        result_list = []
        if not emails_list:
            return jsonify(Error="You haven't sent emails"), 404
        else:
            for row in emails_list:
                result = self.build_outbox_dict(row)
                result_list.append(result)
            return jsonify(Emails = result_list), 200

    def search_outbox_emails_by_user(self, user_id, user_id_searched):
        dao = EmailsDAO()
        emails_list = dao.get_outbox_emails_per_user(user_id, user_id_searched)
        result_list = []
        for row in emails_list:
            result = self.build_email_dict(row)
            result_list.append(result)
        return jsonify(Emails=result_list) , 200

    def read_message(self, user_email, message_id):
        emails_list_outbox = None
        emails_list_inbox = None
        dao = EmailsDAO()
        receive = ReceivedController()
        reply_id = dao.get_father(message_id)
        if not reply_id:
            reply_id = message_id
        msg_info = dao.get_message_info(message_id, user_email)
        if msg_info:
            message_title = msg_info[0]
            sender = msg_info[1]
            if user_email == sender:
                emails_list_outbox = dao.get_message_and_responses_from_outbox (reply_id, user_email)
            else:
                is_read = msg_info [4]#receive.is_read(user_email, message_id)
                print(is_read)
                emails_list_inbox = dao.get_message_and_responses_from_inbox(reply_id, user_email)
                if is_read == None:
                    return jsonify(Error="AllMessage not found"), 404
                if not is_read:
                    receive.read_Email(user_email, message_id)
                    new_body = " was read by " + user_email
                    new_title = "[MESSAGE READ] " + message_title
                    receiver_email = sender
                    self.send_message_from_support(new_title, new_body, receiver_email)

            if emails_list_outbox != [] and emails_list_outbox !=None:
                result_list = []
                print(emails_list_outbox)
                for row in emails_list_outbox:
                    result = self.build_message_outbox_dict(row)
                    result_list.append(result)
                return jsonify(Emails=result_list), 200
            elif emails_list_inbox != [] and emails_list_inbox !=None:
                result_list = []
                print(emails_list_inbox)
                for row in emails_list_inbox:
                    result = self.build_message_inbox_dict(row)
                    result_list.append(result)
                return jsonify(Emails=result_list), 200
            else:
                return jsonify(Error="AllMessage not found"), 404
        else:
            return jsonify(Error="AllMessage not found"), 404

    def send_message_from_support (self, message_title, message_body, receiver_email):
        sender_email = "support@upr.edu"
        if receiver_email != sender_email:
            dao_send = EmailsDAO()
            dao_receive = ReceivedDAO()
            message_id = dao_send.insert(message_title, message_body, sender_email)
            dao_receive.insert(receiver_email, message_id)

    def send_message(self, user_email, json):
        print (json)
        if json and len(json) == 3:
            dao_send = EmailsDAO()
            dao_receive = ReceivedDAO()
            dao_user = UsersDAO()
            message_title = json['message_title']
            message_body = json ['message_body']
            sender_email = user_email
            receiver_email = json['receiver_email']
            print (message_title, message_body,receiver_email, sender_email)
            if message_title == "":
                message_title = "NOT SUBJECT"
            if message_title and message_body and sender_email and receiver_email:
                print(message_title, message_body, receiver_email, sender_email)
                receiver_not_exits = []
                print(receiver_email)
                if len(receiver_email)>1:
                    for user in receiver_email:
                        if not dao_user.get_user(user):
                            receiver_not_exits.append(user)
                    if receiver_not_exits:
                        return jsonify(Emails= str(receiver_not_exits) + " These Users do not exist, please correct the information to send the message " ), 404
                    else:
                        message_id = dao_send.insert(message_title, message_body, sender_email)
                        for user in receiver_email:
                            dao_receive.insert(user, message_id)
                        return jsonify(Emails="Message was Sent successfully for all"), 201

                else:
                    user = receiver_email[0]
                    if dao_user.get_user(user):
                        message_id = dao_send.insert(message_title, message_body, sender_email)
                        dao_receive.insert(user, message_id)
                        return jsonify(Emails="Message was Sent successfully "), 201
                    else:
                        return jsonify(Emails="User Not Exists"), 404
            else:
                return jsonify(Error="Malformed query string"), 204
        else:
            return jsonify(Error="Malformed query string"), 204

    def response_message(self, user_email, message_id, json):
        print(json, len(json))
        if json and len(json) == 1:
            dao_send = EmailsDAO()
            dao_receive = ReceivedDAO()
            reply_id = dao_send.get_father(message_id)
            print(reply_id)
            if not reply_id:
                reply_id = message_id
            result = dao_send.get_message_info(message_id, user_email)
            if result:
                message_title = result[0]
                sender = result[1]
                receiver = result[2]
                if user_email == sender:
                    sender_email = sender
                    receiver_email = receiver
                elif user_email == receiver:
                    sender_email = receiver
                    receiver_email = sender
                else:
                    return jsonify(Error="Email not found"), 404
                message_body = json['message_body']
                print("sender:" + sender_email + "receiver: " + receiver_email)
                print (message_title , message_body , sender_email , receiver_email, reply_id)
                if message_title and message_body and sender_email and receiver_email and reply_id:
                    message_id = dao_send.insert(message_title, message_body, sender_email, reply_id)
                    dao_receive.insert(receiver_email, message_id)
                    return jsonify(Emails="AllMessage was responded successfully"), 201
                else:
                    return jsonify(Error="Malformed query string"), 404
            else:
                return jsonify(Error="Email not found"), 404
        else:
            return jsonify(Error="Malformed query string"), 404

    def get_message_info(self, message_id, user_email):
        dao = EmailsDAO()
        result = dao.get_message_info(message_id, user_email)
        message_title = result[0]
        sender_email = result[1]
        receiver_email = result[2]
        message_body_old = result[3]
        return sender_email, receiver_email

    def edit_email(self, user_email, message_id, json):
        dao = EmailsDAO()
        is_premium = dao.is_premium(user_email)
        print(is_premium)
        if is_premium:
            result = dao.get_message_info(message_id, user_email)
            print(result)
            sender_email = result[1]
            print(sender_email)
            if sender_email == user_email:
                if json and len(json) == 2 :
                    message_title_new = json['message_title']
                    message_body_new = json['message_body']
                    if message_title_new == "" and message_body_new != "":
                        dao.update_message(message_id, message_body_new)
                        return jsonify(Emails="AllMessage updated successfully"), 201
                    elif message_title_new != "" and message_body_new == "":
                        dao.update_title(message_id, message_title_new)
                        return jsonify(Emails="AllMessage updated successfully"), 201
                    else:
                        return jsonify(Error="No changes made"), 404
                else:
                    return jsonify(Error="Malformed query string"), 404
            else:
                return jsonify(Error="AllMessage not Found"), 404
        else:
            return jsonify(Error="User is not Premium")

    def delete_message(self, message_id, user_email):
        dao = EmailsDAO()
        result = dao.get_message_info(message_id, user_email)
        sender = result[1]
        receiver = result[2]
        if user_email == sender:
            print("delete es sender" + message_id + user_email)
            dao.delete_message_in_outbox(message_id)
            return jsonify(Result="AllMessage was deleted successfully from Outbox."), 200
        elif user_email == receiver:
            print("delete es receiver" + message_id + user_email)
            dao.delete_message_in_inbox(message_id)
            return jsonify(Result="AllMessage was deleted successfully from Inbox."), 200
        else:
            return jsonify(Error="AllMessage not found"), 400

    def delete_in_outbox(self, message_id, sender_email):
        try:
            dao = EmailsDAO()
            present = dao.get_message_info(message_id, sender_email)
            sender = present[1]
            if sender == sender_email:
                result = dao.delete_in_outbox(message_id, sender_email)
                print (result)
                return jsonify(Result="AllMessage was deleted successfully from Outbox."), 200
            else:
                return jsonify(Error="wrong person")
        except:
            return jsonify(Error="Wrong parameters."), 404

    def delete_in_inbox(self, message_id, receiver_email):
        dao = EmailsDAO()
        try:
            present = dao.get_message_info(message_id, receiver_email)
            receiver = present[2]
            print(receiver_email, receiver)
            if receiver == receiver_email:
                dao.delete_in_inbox(message_id, receiver_email)
                return jsonify(result="AllMessage was deleted successfully from inbox."), 200
            else:
                return jsonify(error="does not exist in inbox.,"), 404
        except:
            return jsonify(error="Wrong parameters."), 404

    def delete_premium(self, user_email, message_id):
        dao = EmailsDAO()
        try:
            msg_info = dao.get_message_info(message_id, user_email)
            is_premium = dao.is_premium(user_email)
            sender = msg_info[1]
            if is_premium:
                if sender == user_email:
                    result = dao.delete_premium(message_id)
                    return jsonify(Emails="AllMessage was deleted successfully of all users."), 200
                else:
                    return jsonify(Error="does not exist in outbox,"), 404
            else:
                return jsonify(Error="User is not Premium,") ,403
        except:
            return jsonify(Error="does not exist in outbox,"), 404


### STATITICS

    def top_ten_outbox(self):
        dao = EmailsDAO()
        user_list = dao.top_ten_outbox()
        result_list = []
        for row in user_list:
            result = self.build_top_dict(row)
            result_list.append(result)
        return jsonify(Email=result_list)

    def top_ten_inbox(self):
        dao = EmailsDAO()
        user_list = dao.top_ten_inbox()
        result_list = []
        for row in user_list:
            result = self.build_top_dict(row)
            result_list.append(result)
        return jsonify(Email=result_list)

    def email_with_most_replies_user(self,sender_email):
        if sender_email:
            dao = EmailsDAO()
            row = dao.email_with_most_replies_user(sender_email)

            if not row:
                return jsonify(Error="User has not sent emails or User does not exist!"), 404
            else:
                result = self.build_replies_dict(row)
                return jsonify(Email=result)
    def email_with_most_replies(self):
            dao = EmailsDAO()
            most_replies = dao.email_with_most_replies()
            if not most_replies:
                return jsonify(Error="No emails in database"), 404
            else:
                result = self.build_replies_dict(most_replies)
                return jsonify(Email=result)