import firebase_admin
from firebase_admin import firestore, credentials
from firebase_admin import auth
import firebase_admin
from firebase_admin.auth import UserRecord
import pyrebase

configPath = "./firebaseModels/config/webgpu-playground-firebase-adminsdk-5svmd-fd12bb2a88.json"
firebaseConfig = {
    'apiKey': "AIzaSyBZpW6ugiXJV1cN7dVej7z82ENNDS2msr4",
    'authDomain': "webgpu-playground.firebaseapp.com",
    'projectId': "webgpu-playground",
    'storageBucket': "webgpu-playground.appspot.com",
    'messagingSenderId': "111210104264",
    'appId': "1:111210104264:web:ad816eb460d3f1af87ecfd",
    'measurementId': "G-L2H1LHDMFR",
    'databaseURL': 'https://webgpu-playground.firebaseio.com',
    'serviceAccount': configPath
}

def fb_init(name=None):
    cred = credentials.Certificate("./firebaseModels/config/webgpu-playground-firebase-adminsdk-5svmd-fd12bb2a88.json")
    if name:
        return firebase_admin.initialize_app(cred, name=name)
    return  firebase_admin.initialize_app(cred)

def pb_init():
    return pyrebase.initialize_app(firebaseConfig)