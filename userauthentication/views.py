from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
import firebase_admin
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from common.exceptions import CustomAPIException, ErrorCodes
from firebaseModels.authModel import AuthModel
from firebaseModels.firestoreModel import Fields, FirestoreModel
from utils import *

authModel = AuthModel()
firestoreModel = FirestoreModel("REGISTER_FIRESTORE")


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@api_view(['POST'])
def register(request):
    email = request.POST.get("email", "")
    password = request.POST.get("password", "")
    username = request.POST.get("username", "")
    if profanity_check(username):
        raise CustomAPIException('Name contains a swear word', ErrorCodes.PROFANITY_ERROR)

    if not firestoreModel.checkUsernameIsUnique(username):
        raise CustomAPIException('Username is already taken', ErrorCodes.REGISTER_USERNAME_IN_USE)
    try:
        user = authModel.newUser(email, password)
        firestoreModel.newUser(user, username, email)
        return Response({'uid': user}, status=status.HTTP_200_OK)
    except Exception as err:
        if type(err) == firebase_admin._auth_utils.EmailAlreadyExistsError:
            raise CustomAPIException('Email already in use', ErrorCodes.REGISTER_EMAIL_IN_USE)
        else:
            raise CustomAPIException('Password too short', ErrorCodes.PASSWORD_TOO_SHORT)


@api_view(['POST'])
def login(request):
    username = request.POST.get("username", "")
    password = request.POST.get("password", "")
    if data := firestoreModel.getUserFromUsername(username):
        email = data[Fields.email]
        admin = data.get(Fields.admin, False)
        try:
            if user := authModel.logIn(email, password):
                return Response({
                    'uid': user,
                    'admin': admin
                    }, status=status.HTTP_200_OK)
        except:
            raise CustomAPIException('Password is incorrect', ErrorCodes.LOGIN_INVALID_CREDENTIALS)
    raise CustomAPIException('Username is not recognised', ErrorCodes.LOGIN_INVALID_CREDENTIALS)


@api_view(['POST'])
def addAdmin(request):
    currentUid = request.POST.get("currentUid", "")
    newAdmin = request.POST.get("newAdminUsername", "")
    if currentUid not in firestoreModel.getAdmins():
        raise CustomAPIException("Current user is not an administrator.", ErrorCodes.USER_NOT_ADMIN)
    try:
        newAdminDocumentId = firestoreModel.getUserDocumentID(newAdmin)
    except:
        raise CustomAPIException("Username does not exist.", ErrorCodes.USER_DOES_NOT_EXIST)
    firestoreModel.setAdmin(newAdminDocumentId)
    return Response({}, status.HTTP_200_OK)
