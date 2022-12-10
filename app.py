from flask import Flask, request, redirect, url_for
from flask_cors import CORS, cross_origin
from flask import jsonify

from controllers.follows import FollowsController

from controllers.users import UserController
from controllers.emails import EmailController
from controllers.receive import ReceivedController


app = Flask(__name__)
CORS(app)


## CRUD OPERATIONS

@app.route('/MEDALLA-PAMA/received' , methods = ['GET','POST', 'PUT','DELETE'])
def received():
    receive = ReceivedController()
    if request.method == 'GET':
        allReceived = receive.getAllReceived()
        return allReceived

@app.route('/MEDALLA-PAMA/users' , methods = ['GET'])
@app.route('/MEDALLA-PAMA/users/<user_email>' , methods = ['GET','POST', 'PUT','DELETE'])
def users(user_email = None):
    user = UserController()
    if request.method == 'GET':
        allusers = user.getAllUsers()
        return allusers
    elif request.method == 'POST':
        inserted = user.insert(request.json)
        return inserted
    elif request.method == 'PUT':
        upgrated = user.update(user_email, request.json)
        return upgrated
    elif request.method == 'DELETE':
        delete = user.delete_user(user_email)
        return delete
@app.route('/MEDALLA-PAMA/emails' , methods = ['GET','POST', 'PUT','DELETE'])
def emails():
    email = EmailController()
    if request.method == 'GET':
        allEmails = email.getAllEmails()
        return allEmails

@app.route('/MEDALLA-PAMA/<user_email>/inbox/categories' , methods = ['GET'])
def get_categories_user(user_email):
    if request.method == 'GET':
        allReceived = ReceivedController().get_category_user(user_email)
        return allReceived

@app.route('/MEDALLA-PAMA/inbox/search for category:<category>')
def getEmailByCategory(category):
    return ReceivedController().getEmailByCategory(category)

@app.route('/MEDALLA-PAMA/follows_and_followers', methods = ['GET','POST', 'PUT','DELETE'])
def allFriendsInTheUniverse():
    friends = FollowsController()
    if request.method == 'GET':
        return friends.getAllFollowers()


# REQUIREMENTS
@app.route('/MEDALLA-PAMA/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = UserController()
        result = user.valid_login(request.json)
        return result

@app.route('/MEDALLA-PAMA/logout')
def logout():
    return "logout of the account"

@app.route('/MEDALLA-PAMA/signup', methods = ['GET', 'POST'])
def signup():
    user = UserController()
    if request.method == 'POST':
        inserted = user.insert(request.json)
        return inserted

@app.route('/MEDALLA-PAMA/<my_email>/search_user: <user_email>', methods = ['GET'])
def search_user(my_email, user_email):
    user = UserController()
    if request.method == 'GET':
        user_info = user.get_user(user_email)
        return user_info

@app.route('/MEDALLA-PAMA/<user_email>/inbox', methods = ['GET'])
@app.route('/MEDALLA-PAMA/<user_email>/inbox/read status: <is_read>', methods = ['GET'])
@app.route('/MEDALLA-PAMA/<user_email>/inbox/search for: <sender_email>', methods = ['GET'])
@app.route('/MEDALLA-PAMA/<user_email>/inbox/search for category:', methods = ['GET'])
@app.route('/MEDALLA-PAMA/<user_email>/inbox/<message_id>', methods = ['PUT'])
def view_inbox(user_email, sender_email=None, is_read=None, message_id=None):
    if request.method == 'GET':
        if sender_email:
            return ReceivedController().searchInboxByUser(user_email, sender_email)
        elif is_read:
            return ReceivedController().getReceiverEmailByRead(user_email, is_read)
        else:
            return ReceivedController().getEmailByReceiver(user_email)
    elif request.method == 'POST':
        emails = EmailController()
        response = emails.send_message(user_email, request.json)
        return response
    elif request.method == 'PUT':
        return EmailController().delete_in_inbox(message_id, user_email)


@app.route('/MEDALLA-PAMA/<user_email>/outbox/<message_id>/deleteall', methods = ['DELETE'])
def delete_as_premium (user_email, message_id):
    if request.method == 'DELETE':
        return EmailController().delete_premium(user_email, message_id)

@app.route('/MEDALLA-PAMA/<receiver_email>/inbox/search for category:<category>')
@app.route('/MEDALLA-PAMA/<receiver_email>/inbox/search for category: <category>')
def getEmailByCategoryFromReceiver(receiver_email, category):
    return ReceivedController().getEmailByCategoryFromReceiver(receiver_email, category)

@app.route('/MEDALLA-PAMA/<user_email>/inbox/<message_id>/category:<category>', methods=['PUT'])
@app.route('/MEDALLA-PAMA/<user_email>/inbox/<message_id>/category: <category>', methods=['PUT'])
def update_category(user_email, message_id, category):
    if request.method == 'PUT':
        return ReceivedController().update_category(user_email, message_id, category)

@app.route('/MEDALLA-PAMA/<user_email>/outbox', methods = ['GET','POST', 'PUT','DELETE'])
@app.route('/MEDALLA-PAMA/<user_email>/outbox/<message_id>', methods = ['GET','POST', 'PUT','DELETE'])
def view_outbox (user_email, message_id=None):
    if request.method == 'GET':
        emails = EmailController()
        all_message = emails.get_my_outbox_Emails(user_email)
        return all_message
    elif request.method == 'POST':
        emails = EmailController()
        response = emails.send_message(user_email, request.json)
        return response
    elif request.method == 'PUT':
        return EmailController().edit_email(user_email, message_id, request.json)

    elif request.method == 'DELETE':
        return EmailController().delete_in_outbox(message_id, user_email)


@app.route('/MEDALLA-PAMA/<user_email>/view/<message_id>', methods = ['GET','POST', 'PUT', 'DELETE'])
@app.route('/MEDALLA-PAMA/<user_email>/view/<message_id>', methods = ['GET','POST', 'PUT','DELETE'])
def view_message_and_replies(user_email, message_id):
    if request.method == 'GET':
        emails = EmailController()
        all_message = emails.read_message(user_email, message_id)
        return all_message
    elif request.method == 'POST':
        print("esta aqui")
        emails = EmailController()
        response = emails.response_message(user_email, message_id, request.json)
        return response
    elif request.method == 'PUT':
        return EmailController().edit_email(user_email, message_id, request.json)
    elif request.method == 'DELETE':
        return EmailController().delete_message(message_id, user_email)

@app.route('/MEDALLA-PAMA/<user_email>/inbox/view/<message_id>', methods = ['DELETE'])
def delete_message_from_inbox(user_email, message_id):
    if request.method == 'DELETE':
        return EmailController().delete_message(message_id, user_email)
@app.route('/MEDALLA-PAMA/<user_email>/outbox/view/<message_id>', methods = ['DELETE'])
def delete_message_from_outbox(user_email, message_id):
    if request.method == 'DELETE':
        return EmailController().delete_message(message_id, user_email)

@app.route('/MEDALLA-PAMA/<user_email>/myfollowers/', methods = ['GET'])
def my_followers(user_email):
    if request.method == 'GET':
        # ALL MY FOLLOWERS
        return FollowsController().getMyFollowers(user_email)
        pass

@app.route('/MEDALLA-PAMA/<user_email>/myfollows', methods = ['GET'])
@app.route('/MEDALLA-PAMA/<user_email>/myfollows/<friend>', methods = ['GET','POST','DELETE'])
def friendship(user_email, friend=None):
    if request.method == 'GET':
        # ALL MY FRIENDS
        return FollowsController().getMyFollows_route(user_email)
    elif request.method == 'POST':
        # ADD A FRIEND
        return FollowsController().addFollowJson(user_email, friend)
    elif request.method == 'DELETE':
        # DELETE A FRIEND
        return FollowsController().removeFollow(user_email, friend)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route('/MEDALLA-PAMA/<user_email>/myfollows/count', methods = ['GET'])
def count_friends(user_email):
    if request.method == 'GET':
        # ALL MY FRIENDS
        return FollowsController().count_my_friends(user_email)

### USER STATITICS
@app.route('/MEDALLA-PAMA/<sender_email>/statistics/most recepients')
def getEmailsWithMostRecepientsByUser(sender_email):
    return ReceivedController().getEmailsWithMostRecepientsByUser(sender_email)
@app.route('/MEDALLA-PAMA/<sender_email>/statistics/email with most replies')
def getEmailWithMostReplies_user(sender_email):
    return EmailController().email_with_most_replies_user(sender_email)

@app.route('/MEDALLA-PAMA/<receiver_email>/statistics/top 5 senders')
def getTopfiveSenderEmail(receiver_email):
    return ReceivedController().getTopSenderEmail(receiver_email)

@app.route('/MEDALLA-PAMA/<sender_email>/statistics/top 5 receivers')
def getTopfiveReceiversEmail(sender_email):
    return ReceivedController().getTopReceiversEmail(sender_email)



### GLOBAL STATITICS
@app.route('/MEDALLA-PAMA/statistics/most recepients')
def getEmailsWithMostRecepients():
    return ReceivedController().getEmailsWithMostRecepients()
@app.route('/MEDALLA-PAMA/statistics/email with most replies')
def getEmailWithMostReplies():
    return EmailController().email_with_most_replies()
@app.route('/MEDALLA-PAMA/statistics/top 10 inbox')
def getToptenMoreEmailsInbox():
    return EmailController().top_ten_inbox()
@app.route('/MEDALLA-PAMA/statistics/top 10 outbox')
def getToptenMoreEmailsOutbox():
    return EmailController().top_ten_outbox()


if __name__ == '__main__':
    app.run(debug=True, port=8000)