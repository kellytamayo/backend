from flask import jsonify, redirect, url_for
from dao.users import UsersDAO

class UserController:

    def build_user_dict(self, row):
        result =  {}
        result['user_email'] = row[0]
        result['user_password'] = row[1]
        result['is_premium'] = row[2]
        result['user_name'] = row[3]
        result['user_lastname'] = row[4]
        return result

    def build_user(self, row):
        result =  {}
        result['user_email'] = row[0]
        result['user_name'] = row[1]
        result['user_lastname'] = row[2]
        return result

    def getAllUsers(self):
        dao = UsersDAO()
        users_list = dao.getAllUsers()
        result_list = []
        for row in users_list:
            result = self.build_user_dict(row)
            result_list.append(result)
        return jsonify(Users=result_list), 201

    def insert(self, json):
        try:
            if json and len(json) == 5:
                user_email = json['user_email']
                user_password = json['user_password']
                print(json['is_premium'])
                is_premium =  json['is_premium']
                user_name =  json['user_name']
                user_lastname = json['user_lastname']
                if user_email and user_password and user_name and user_lastname and is_premium !=None:
                    print(user_email, user_password, user_name, user_lastname, is_premium)
                    dao = UsersDAO()
                    inserted = dao.insert(user_email, user_password, is_premium, user_name, user_lastname)
                    print('inserto', inserted)
                    if inserted:
                        result = {}
                        result['user_email'] = user_email
                        result['user_password'] = user_password
                        result['is_premium'] = is_premium
                        result['user_name'] = user_name
                        result['user_lastname'] = user_lastname
                        return jsonify(Users = "User " + user_email +" singup correctly" ), 201
                    else:
                        return jsonify(Error="User can't register, use other account"), 403

                else:
                    return jsonify(Error="no complete"), 404
            else:
                return jsonify(Error = "no complete"), 404
        except:
            return jsonify(Error="no complete"), 400

    def valid_login(self, form):
        try:
            if form and len(form) == 2:
                user_email = form['user_email']
                user_password = form['user_password']
                dao = UsersDAO()
                db_password = dao.get_user_password(user_email)

                if db_password:
                    if db_password == user_password:
                        return jsonify(Users="ha entrado correctamente!!"), 201
                    else:
                        return jsonify(Error="contrasena incorreca, intente nuevamente"), 404
                else:
                    return jsonify(Error = "no ha ingresado la contraseña"), 404
            else:
                return jsonify(Error = "no ha ingresado toda la informacion"), 404
        except:
            return jsonify(Error="no ha ingresado toda la informacion"), 404

    def get_user(self, user_email):
        dao = UsersDAO()
        user = dao.get_user(user_email)
        if user:
            result = self.build_user(user)
            return jsonify(Users= result), 201
        else:
            return jsonify(Error = "User no exist"), 404

    def update(self, user_email,json):
        print(len(json))

        if json and len(json) == 4:
            user_password = json['user_password']
            is_premium =  json['is_premium']
            user_name =  json['user_name']
            user_lastname = json['user_lastname']
            if user_email:
                dao = UsersDAO()
                user = dao.update_user(user_email, user_password, is_premium, user_name, user_lastname)
                if user:
                    result = self.build_user_dict(user)
                    return jsonify(Users = result), 201
                else:
                    return jsonify(Error="el usuario ya existe, use otro email para registrar"), 404
            else:
                return jsonify(Error="Los valores no estan completos 2"), 404
        else:
            return jsonify(Error = "Los valores no estan completos"), 404

    def delete_user(self, user_email):
        dao = UsersDAO()
        deleted = dao.delete_user(user_email)
        if deleted:
            return jsonify(Users= "User was deleted properly"), 201
        else:
            return jsonify(Error = "User cannot delete"), 404

