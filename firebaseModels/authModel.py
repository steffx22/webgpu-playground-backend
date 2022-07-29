from firebaseModels.app import fb_init, pb_init
from firebase_admin import auth
from firebase_admin.auth import UserRecord


class AuthModel:
    def __init__(self) -> None:
        self.app = fb_init()

        self.firebase = pb_init()
        self.auth = self.firebase.auth()

    # TODO: fix error messages
    def getUserRecord(self, email: str = None, uid: str = None) -> UserRecord:
        try:
            if email:
                return auth.get_user_by_email(email)
            elif uid:
                return auth.get_user(uid)
        except:
            print("User {0} does not exist".format(uid))
            return None

    def getUserID(self, email: str) -> str:
        userRecord: UserRecord = self.getUserRecord(email=email)
        if userRecord:
            return userRecord.uid

    def getUserEmail(self, uid: str) -> str:
        userRecord: UserRecord = self.getUserRecord(uid=uid)
        if userRecord:
            return userRecord.email

    # TODO: fix error messages
    def newUser(self, email: str, password: str):
        return auth.create_user(email=email, password=password).uid

    # TODO: fix error messages
    def logIn(self, email: str, password: str):
        if self.auth.sign_in_with_email_and_password(email=email, password=password):
            return self.getUserID(email)

    # TODO: fix error messages
    def deleteUser(self, uid: str):
        try:
            auth.delete_user(uid)
        except:
            print("User {0} does not exist".format(uid))

    # TODO: fix error messages
    def listUsers(self):
        userList = auth.list_users()
        while userList:
            for i, user in enumerate(userList.users):
                print('User {0}:\n\tID: {1}\n\tEmail: {2}'.format(i, user.uid, user.email))
            userList = userList.get_next_page()


if __name__ == "__main__":
    authModel = AuthModel()
