from typing import Dict, List
from firebaseModels.app import fb_init
from firebase_admin import firestore
from datetime import datetime


# Documentation: https://firebase.google.com/docs/firestore


class Collections():
    users = "users"
    creations = "creations"
    submissions = "submissions"


class Documents():
    pass


class Fields():
    creationName = "creationName"
    displayName = "displayName"
    creationDate = "creationDate"
    creatorId = "creatorId"
    rating = "rating"
    averageRating = "averageRating"
    uid = "uid"
    username = "username"
    email = "email"
    primitive = "primitive"
    public = "public"
    vertexCount = "vertexCount"
    url = "url"
    tags = "tags"
    raters = "raters"
    reportMessages = "reportMessages"
    reportCount = "reportCount"
    admin = "admin"


class FirestoreModel:
    def __init__(self, name="FIRESTORE_APP") -> None:
        self.app = fb_init(name=name)
        self.db: firestore.firestore.Client = firestore.client(self.app)

    def createNewDocument(self, collection: str, data: Dict[str, any]):
        self.db.collection(collection).add(data)

    def createNewDocumentWithDocumentID(self, collection: str, documentId: str, data: Dict[str, any]):
        self.db.collection(collection).document(documentId).set(data)

    def getCollection(self, collection: str) -> firestore.firestore.CollectionReference:
        return self.db.collection(collection)

    def getField(self, collection: str, documentId: str, field: str):
        return self.getDocument(collection, documentId).to_dict().get(field, None)

    def getDocument(self, collection: str, documentId: str) -> firestore.firestore.DocumentSnapshot:
        return self.db.collection(collection).document(documentId).get()

    def getAllDocuments(self, collection: str) -> List[firestore.firestore.DocumentSnapshot]:
        return self.db.collection(collection).stream()

    def getAllDocumentsOrdered(self, collection: str, orderBy: str, descending: bool) -> List[
        firestore.firestore.DocumentSnapshot]:
        direction = firestore.Query.DESCENDING if descending else firestore.Query.ASCENDING
        return self.db.collection(collection).order_by(orderBy, direction=direction).stream()

    def getAllDocumentsQueried(self, collection: str, field: str, comparator: str, value: any) -> List[
        firestore.firestore.DocumentSnapshot]:
        return self.db.collection(collection).where(field, comparator, value).stream()

    def updateDocument(self, collection: str, document: str, data: Dict[str, any]):
        # To update a dictionary value use the format: {dictionaryName.fieldName: value}
        self.db.collection(collection).document(document).update(data)

    def addElementToArray(self, collection: str, document: str, fieldName: str, value: any):
        self.db.collection(collection).document(document).update({fieldName: firestore.ArrayUnion([value])})

    def removeElementFromArray(self, collection: str, document: str, fieldName: str, value: any):
        self.db.collection(collection).document(document).update({fieldName: firestore.ArrayRemove([value])})

    def removeElementFromDictionary(self, collection: str, document: str, fieldName: str, value: str):
        self.db.collection(collection).document(document).update({f'{fieldName}.{value}': firestore.DELETE_FIELD})

    def incrementValue(self, collection: str, document: str, fieldName: str, value: float):
        # To decrement, use a negative value
        self.db.collection(collection).document(document).update({fieldName: firestore.Increment(value)})

    def deleteDocument(self, collection: str, document: str):
        self.db.collection(collection).document(document).delete()

    def deleteField(self, collection: str, document: str, fieldName: str):
        self.db.collection(collection).document(document).update({fieldName: firestore.DELETE_FIELD})

    def newCreation(self, creationName: str, creatorId: str, primitive: str, public: bool, tags: str = "") -> bool:
        docs = self.getAllDocumentsQueried(Collections.users, Fields.uid, "==", creatorId)
        for doc in docs:
            username = doc.to_dict()[Fields.username]
            if not self.getDocument(Collections.creations, creationName).exists:
                data = {
                    Fields.primitive: primitive,
                    Fields.vertexCount: 6,
                    Fields.displayName: "New File",
                    Fields.public: public,
                    Fields.creationName: creationName,
                    Fields.creationDate: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    Fields.creatorId: creatorId,
                    Fields.username: username,
                    Fields.rating: {
                        "1": 0,
                        "2": 0,
                        "3": 0,
                        "4": 0,
                        "5": 0
                    },
                    Fields.averageRating: 0,
                    Fields.tags: tags
                }
                self.createNewDocumentWithDocumentID(Collections.creations, creationName, data)
                return True
            return False
        return False

    def doesFileExist(self, creationName: str):
        return self.getDocument(Collections.creations, creationName).exists

    def updatePrimitive(self, creationName: str, primitive: str):
        self.updateDocument(Collections.creations, creationName, {Fields.primitive: primitive})

    def updateVertexCount(self, creationName: str, vertexCount: int):
        self.updateDocument(Collections.creations, creationName, {Fields.vertexCount: vertexCount})

    def updateDisplayName(self, creationName: str, displayName: str):
        self.updateDocument(Collections.creations, creationName, {Fields.displayName: displayName})

    def updateTags(self, creationName: str, tags: str):
        self.updateDocument(Collections.creations, creationName, {Fields.tags: tags})

    def checkUsernameIsUnique(self, username):
        docs = self.getAllDocumentsQueried(Collections.users, Fields.username, "==", username)
        for _ in docs:
            return False
        return True

    def newUser(self, uid, username, email):
        self.createNewDocument(
            Collections.users,
            {
                Fields.uid: uid,
                Fields.username: username,
                Fields.email: email
            }
        )

    def extractFiles(self, fileStream, user, submission=False):
        fileStructs = []
        for f in fileStream:
            f_dict = f.to_dict()
            if (f_dict.get(Fields.public, True) and user is None) or (f_dict[Fields.creatorId] == user):
                fileStructs.append({
                    Fields.uid: f_dict[Fields.creationName].split("-")[0],
                    Fields.creationName: "-".join(f_dict[Fields.creationName].split("-")[1:]),
                    Fields.creationDate: f_dict[Fields.creationDate],
                    Fields.rating: f_dict[Fields.rating],
                    Fields.averageRating: f_dict.get(Fields.averageRating, 0),
                    Fields.username: f_dict.get(Fields.username, ""),
                    Fields.primitive: f_dict.get(Fields.primitive, "point-list"),
                    Fields.url: f_dict.get(Fields.url, ""),
                    Fields.displayName: f_dict.get(Fields.displayName,
                                                   "-".join(f_dict[Fields.creationName].split("-")[1:])),
                    Fields.tags: f_dict.get(Fields.tags, "")
                })
        return fileStructs

    def listCreations(self, uid=None):
        files: List[firestore.firestore.DocumentSnapshot] = self.getAllDocumentsOrdered(Collections.creations,
                                                                                        Fields.averageRating, True)
        return self.extractFiles(files, uid)

    def listSubmissions(self, uid=None):
        files: List[firestore.firestore.DocumentSnapshot] = self.getAllDocumentsOrdered(Collections.submissions,
                                                                                        Fields.averageRating, True)
        return self.extractFiles(files, uid)

    def getEmailFromUsername(self, username):
        docs = self.getAllDocumentsQueried(Collections.users, Fields.username, "==", username)
        for doc in docs:
            return doc.to_dict()[Fields.email]

    def getUserFromUsername(self, username):
        docs = self.getAllDocumentsQueried(Collections.users, Fields.username, "==", username)
        for doc in docs:
            return doc.to_dict()

    def updateRating(self, creation, new, raterID):
        doc = self.db.collection(Collections.submissions).document(creation).get().to_dict()
        ratings = doc['rating']
        raters = doc['raters']
        if raters.get(raterID, 0) == new:
            return

        if raters.get(raterID, 0) != 0:
            self.incrementValue(Collections.submissions, creation, 'rating.{0}'.format(raters[raterID]), -1)
        self.incrementValue(Collections.submissions, creation, 'rating.{0}'.format(new), 1)
        doc = self.db.collection(Collections.submissions).document(creation).get().to_dict()
        ratings = doc[Fields.rating]
        raters = doc[Fields.raters]
        raters[raterID] = new

        total_rating = sum([int(i) * r for i, r in ratings.items()])
        average = round(total_rating / sum(ratings.values()), 3)
        self.updateDocument(Collections.submissions, creation, {
            Fields.averageRating: average,
            Fields.raters: raters
        })

    def searchTags(self, tag, creations):
        tagged_creations = []
        tags = tag.split(" ")
        for c in creations:
            for t in tags:
                if t in c["displayName"].upper() or t in c["username"].upper() or t in c["tags"].upper():
                    tagged_creations.append(c)
        return tagged_creations

    def getUserDocumentID(self, username: str):
        return list(self.getAllDocumentsQueried(Collections.users, Fields.username, "==", username))[0].id

    def getAdmins(self):
        return map(lambda u: u[Fields.uid],
                   filter(lambda u: u.get(Fields.admin),
                          map(lambda doc: doc.to_dict(),
                              self.getAllDocuments(Collections.users))))

    def setAdmin(self, documentId: str):
        self.updateDocument(Collections.users, documentId, {Fields.admin: True})


if __name__ == "__main__":
    firestoreModel = FirestoreModel()
