from flask import jsonify
from codes.dao.follows import FollowsDAO

class FollowsController:
    def build_Follower_dict(self, row):
        result = {}
        result['user_emails'] = row[0]
        result['user_emails'] = row[0]
        result['user_friends_emails'] = row[1]
        result['user_name'] = row[2]
        result['user_lastname'] = row[3]
        result['user_photo_path'] = None
        return result
    def build_follower_attributes(self,user_email, user_friends_emails):
        result = {}
        result['user_email'] = user_email
        result['user_friends_emails'] = user_friends_emails
        return result
    def build_follower_count(self,user_email, count):
        result = {}
        result['user_email'] = user_email
        result['count'] = count
        return result
    def getAllFollowers(self):
        dao = FollowsDAO()
        users_list = dao.getAllFollows()
        result_list = []
        for row in users_list:
            result = self.build_Follower_dict(row)
            result_list.append(result)
        return jsonify(Follows=result_list), 200

    def getMyFollows_route(self, user_email):
        # user_email = args.get("user_email")
        print(user_email)
        dao = FollowsDAO()
        if user_email:
            users_list = dao.getMyFollows(user_email)
        else:
            return jsonify(Error="Malformed query string"), 400
        result_list = []

        if users_list != []:
            for row in users_list:
                result = self.build_Follower_dict(row)
                result_list.append(result)
            return jsonify(Follows=result_list), 200
        else:
            empty_List ={}
            empty_List["user_emails"] = user_email
            empty_List["user_friends_emails"]= "Add your friends!"
            empty_List["user_lastname"]= ""
            empty_List["user_name"]= ""
            empty_List["user_photo_path"]= None
            return jsonify(Follows="Add Friends Here!"), 200


    def getMyFollowers(self, user):
        user_email = user
        dao = FollowsDAO()
        if user_email:
            users_list = dao.getMyFollowers(user_email)
        else:
            return jsonify(Error="Malformed query string"), 400
        result_list = []
        if users_list != []:
            for row in users_list:
                #result = self.build_Follower_dict(row)
                result = row[0]
                result_list.append(result)
            return jsonify(Follows=result_list), 200
        else:
            return jsonify(Follows="Does not have friends"), 200
    # works not used for checking anything right now
    def get_follower_row(self,user_email,user_friends_emails):
        dao = FollowsDAO()
        row = dao.get_follower_row(user_email,user_friends_emails)
        if not row:
            return jsonify(Error="Friendship doesn't exist"), 404
        else:
            empty_list ={}
            return jsonify(Follows=friend), 201

    # Diagnosticado por Manuel como "Poseido por Satanas"
    def addFollower(self, form):
        print("Form: ", form)
        if len(form) != 2:
            return jsonify(Error="Malformed post request"), 400
        else:
            user_email = form['user_email']
            user_friends_emails = form['user_friends_emails']
            if user_email and user_friends_emails:
                dao = FollowsDAO()
                thing = dao.addFollower(user_email, user_friends_emails)
                print("Controller: ", thing)
                #result = self.build_follower_attributes(user_email)
                return jsonify(Follows="Added!"), 201
            else:
                return jsonify(Error="Unexpected attributes in post request"), 400
    # It works!
    def addFollowJson(self,user_email,friend):
        user_email = user_email
        user_friends_emails = friend
        if user_email == user_friends_emails:
            return jsonify(Error="Unexpected attributes in post request"), 405
        if user_email and user_friends_emails:
            dao = FollowsDAO()
            thing = dao.get_follower_row(user_email, user_friends_emails)
            if not thing:
                thing = dao.addFollower(user_email, user_friends_emails)
                print("JsonController: ", thing)
                result = self.build_follower_attributes(user_email, user_friends_emails)
                return jsonify(Follows="Added!"), 201
            else:
                return jsonify(Error="Friendship already exists"), 405
        else:
            return jsonify(Error="Unexpected attributes in post request"), 400

    # it works used for the remove follow
    def removeFollow(self, user_email, friend):
        user_email = user_email
        user_friends_emails = friend
        if user_email and user_friends_emails:
            dao = FollowsDAO()
            nothere = dao.get_follower_row(user_email, user_friends_emails)
            print(nothere)
            if not nothere:
                return jsonify(Error="Friendship doesn't exist"), 405
            else:
                dao.removeFollow(user_email, user_friends_emails)
                return jsonify(DeleteSatus="OK"), 200
        else:
            return jsonify(Error="Unexpected attributes in post request"), 400
    def count_my_friends(self, user_email):
        dao = FollowsDAO()
        number_friends = dao.count_my_friends(user_email)
        result = self.build_follower_count(user_email, number_friends)
        print(number_friends)
        return jsonify(Follows=result), 200
