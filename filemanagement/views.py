from django.core.files.storage import FileSystemStorage

# Create your views here.

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from common.exceptions import CustomAPIException, ErrorCodes
from firebaseModels.firestoreModel import Collections, FirestoreModel, Fields
from firebaseModels.storageModel import StorageModel
from utils import *

import uuid

firestoreModel = FirestoreModel()
storageModel = StorageModel()
FILES_USED = ["fragment", "vertex", "vertex_buffer", "colour_buffer", "compute"]


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@api_view(['POST'])
def saveFile(request):
    # Update File is used to know if this is creating a new graphic or updating one
    # The same name is not allowed for two creations by the same user
    vertex = request.POST.get("vertex", "")
    fragment = request.POST.get("fragment", "")
    primitive = request.POST.get("primitive", "")
    vertex_buffer = request.POST.get("vertexBuffer", "")
    colour_buffer = request.POST.get("colourBuffer", "")
    compute = request.POST.get("compute", "")
    tags = request.POST.get("tags", "")

    uid = request.POST.get("uid", "")
    name = request.POST.get("name", "")

    if profanity_check(name):
        raise CustomAPIException('Name contains a swear word', ErrorCodes.PROFANITY_ERROR)

    display_name = request.POST.get("displayName", "")
    vertex_count = request.POST.get("vertexCount", "")
    update_file = request.POST.get("updateFile", "")
    publicStr = request.POST.get("public", "")
    try:
        public = eval(publicStr)
    except:
        public = True

    path = "creations/{0}/{1}/".format(uid, name)
    creation_name = "{0}-{1}".format(uid, name)
    if firestoreModel.newCreation(creation_name, uid, primitive, public, tags) or eval(update_file):
        storageModel.instantiate_new_files(FILES_USED, [fragment, vertex, vertex_buffer, colour_buffer, compute], path)
        firestoreModel.updateVertexCount(creation_name, vertex_count)
        firestoreModel.updatePrimitive(creation_name, primitive)
        firestoreModel.updateTags(creation_name, tags)
        if display_name != "":
            firestoreModel.updateDisplayName(creation_name, display_name)

        try:
            image = request.FILES['image']
            fss = FileSystemStorage()
            file = fss.save(image.name, image)
            file_url = fss.url(file)
            file_url = file_url.replace("/media/", "media/")
            image_path = "{0}{1}".format(path, "image.png")
            image_url = storageModel.uploadFile(image_path, file_url)
            url = storageModel.getURL(image_path, image_url['downloadTokens'])
            firestoreModel.updateDocument(Collections.creations, "{0}-{1}".format(uid, name), {'url': url})
        except:
            raise CustomAPIException("No image provided in the request", ErrorCodes.SAVE_FILE_NO_IMAGE)

        fss.delete(file)
        return Response({}, status=status.HTTP_200_OK)
    raise CustomAPIException('File name already in use', ErrorCodes.FILE_NAME_IN_USER)


@api_view(['GET'])
def getFile(request):
    # File path should be in the form: "userId/creationName"
    file_path = request.GET.get("filePath", "")
    firestore_path = file_path.replace("/", "-")
    if not firestoreModel.doesFileExist(firestore_path):
        raise CustomAPIException("File does not exist yet", ErrorCodes.INVALID_FILE_PATH)

    data = storageModel.get_all_files(FILES_USED, file_path)
    doc = firestoreModel.getDocument(Collections.creations, firestore_path).to_dict()

    return Response(
        {**{
            'primitive': doc.get("primitive", "triangle-list"),
            'vertexCount': doc.get("vertexCount", 6),
            'visibility': doc.get("public", True),
            'displayName': doc.get("displayName", "New File"),
            'tags': doc.get("tags", "")
        }, **data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def getAllCreations(request):
    creations = firestoreModel.listCreations()
    tagged_creations = []
    tagged = False
    if (tag := request.GET.get("tag", "").upper()) != "":
        tagged = True
        tagged_creations = firestoreModel.searchTags(tag, creations)
    return Response({'creations': tagged_creations if tagged else creations}, status=status.HTTP_200_OK)


@api_view(['GET'])
def getAllUserCreations(request):
    uid = request.GET.get("uid", "")
    creations = firestoreModel.listCreations(uid=uid)
    tagged_creations = []
    tagged = False
    if (tag := request.GET.get("tag", "").upper()) != "":
        tagged = True
        tagged_creations = firestoreModel.searchTags(tag, creations)
    return Response({'creations': tagged_creations if tagged else creations}, status=status.HTTP_200_OK)


@api_view(['POST'])
def report(request):
    creationName = request.POST.get("creationName", "")
    creatorID = request.POST.get("creatorId", "")
    message = request.POST.get("message", "")
    isSubmission = request.POST.get("isSubmission", False) == 'true'

    creationID = "{0}-{1}".format(creatorID, creationName)

    try:
        # add report
        collection = Collections.submissions if isSubmission else Collections.creations
        cr = firestoreModel.getDocument(collection, creationID).to_dict()
        messages = cr.get(Fields.reportMessages, []) + [message]
        count = cr.get(Fields.reportCount, 0) + 1
        firestoreModel.updateDocument(collection, creationID,
                                      {Fields.reportMessages: messages, Fields.reportCount: count})
    except:
        raise CustomAPIException("Creation {0} doesn't exist.".format(creationID), ErrorCodes.INVALID_FILE_PATH)
    return Response({}, status=status.HTTP_200_OK)


@api_view(['GET'])
def getReported(request):
    creations = list(map(
        lambda doc: doc.to_dict(),
        firestoreModel.getAllDocumentsQueried(Collections.creations, Fields.reportCount, ">", 0)))
    creations.sort(key=lambda cr: cr.get(Fields.reportCount, 0))
    submissions = list(map(
        lambda doc: doc.to_dict(),
        firestoreModel.getAllDocumentsQueried(Collections.submissions, Fields.reportCount, ">", 0)))
    submissions.sort(key=lambda sub: sub.get(Fields.reportCount, 0))
    return Response({"creations": creations, "submissions": submissions}, status=status.HTTP_200_OK)


@api_view(['POST'])
def unreport(request):
    adminUid = request.POST.get("uid", "")
    creationName = request.POST.get("creationName", "")
    creatorID = request.POST.get("creatorId", "")
    isSubmission = request.POST.get("isSubmission", False) == "true"

    creationID = "{0}-{1}".format(creatorID, creationName)

    if adminUid not in firestoreModel.getAdmins():
        raise CustomAPIException("Current user is not an admin.", ErrorCodes.USER_NOT_ADMIN)

    try:
        # clear report related fields
        collection = Collections.submissions if isSubmission else Collections.creations
        firestoreModel.updateDocument(collection, creationID, {Fields.reportCount: 0, Fields.reportMessages: []})
    except:
        raise CustomAPIException("Creation does not exist.", ErrorCodes.INVALID_FILE_PATH)
    return Response({}, status=status.HTTP_200_OK)


@api_view(['POST'])
def updateRating(request):
    creationID = request.POST.get("creationName", "")
    newRating = request.POST.get("newRating", "")
    raterID = request.POST.get("raterID")
    try:
        assert (1 <= int(newRating) <= 5)
    except:
        raise CustomAPIException('Invalid rating: {0}'.format(newRating), ErrorCodes.INVALID_RATING)

    firestoreModel.updateRating(creationID, newRating, raterID)
    return Response({}, status=status.HTTP_200_OK)


@api_view(['POST'])
def updateVisibility(request):
    uid = request.POST.get("uid", "")
    creationName = request.POST.get("creationName", "")
    public = request.POST.get("public", "")
    try:
        creationPath = "{0}-{1}".format(uid, creationName)
        firestoreModel.updateDocument(Collections.creations, creationPath, {"public": eval(public)})
    except:
        raise CustomAPIException('Invalid file path: {0}'.format(creationPath), ErrorCodes.INVALID_FILE_PATH)
    return Response({}, status=status.HTTP_200_OK)


@api_view(['POST'])
def submitCreation(request):
    uid = request.POST.get("uid", "")
    creationID = request.POST.get("creationID", "")
    creation_data = firestoreModel.getDocument(Collections.creations, "{0}-{1}".format(uid, creationID)).to_dict()
    data = storageModel.get_all_files(FILES_USED, "{0}/{1}".format(uid, creationID))

    submission_data = {
        "raters": {},
        **creation_data
    }

    submission_id = str(uuid.uuid4())
    submission_data["creationName"] = f"{uid}-{submission_id}"

    firestoreModel.createNewDocumentWithDocumentID(Collections.submissions, submission_id, submission_data)
    storageModel.instantiate_new_files(list(data.keys()), list(data.values()), "submissions/{0}/".format(submission_id))

    return Response({}, status=status.HTTP_200_OK)


@api_view(['GET'])
def getAllSubmissions(request):
    creations = firestoreModel.listSubmissions()
    tagged_creations = []
    tagged = False
    if (tag := request.GET.get("tag", "").upper()) != "":
        tagged = True
        tagged_creations = firestoreModel.searchTags(tag, creations)
    return Response({'creations': tagged_creations if tagged else creations}, status=status.HTTP_200_OK)


@api_view(['GET'])
def getSubmission(request):
    # File path should be in the form: "userId/creationName"
    creationID = request.GET.get("creationID", "")

    data = storageModel.get_all_files(FILES_USED, "{0}".format(creationID), prefix="submissions")
    doc = firestoreModel.getDocument(Collections.submissions, creationID).to_dict()

    return Response(
        {**{
            'primitive': doc.get("primitive", "triangle-list"),
            'vertexCount': doc.get("vertexCount", 6),
            'visibility': doc.get("public", True),
            'displayName': doc.get("displayName", "New File"),
            'raters': doc.get("raters", {}),
            'ratings': doc.get("rating", {
                1: 0,
                2: 0,
                3: 0,
                4: 0,
                5: 0
            }),
            'averageRating': doc.get("averageRating", 0)
        }, **data}, status=status.HTTP_200_OK)


@api_view(['POST'])
def deleteCreation(request):
    admin = request.POST.get("admin", "")
    uid = request.POST.get("uid", "")
    creationID = request.POST.get("creationID", "")
    isSubmission = request.POST.get("isSubmission", False) == 'true'

    if admin not in firestoreModel.getAdmins():
        raise CustomAPIException("Current user is not an admin.", ErrorCodes.USER_NOT_ADMIN)

    collection = Collections.submissions if isSubmission else Collections.creations
    file = creationID if isSubmission else f"{uid}-{creationID}"
    path = creationID if isSubmission else f"{uid}/{creationID}"

    firestoreModel.deleteDocument(collection, file)
    storageModel.deleteFolder(path, FILES_USED, collection)

    return Response({}, status=status.HTTP_200_OK)


@api_view(['POST'])
def cleanFirebase(request):
    documents = firestoreModel.getAllDocuments(Collections.creations)
    for document in documents:
        doc = document.to_dict()
        if doc.get("displayName", "") == "":
            uid = document.id.split("-")[0]
            creationID = document.id.replace(uid + "-", "")
            firestoreModel.deleteDocument(Collections.creations, document.id)
            storageModel.deleteFolder("{0}/{1}".format(uid, creationID), FILES_USED)
            print("Deleting: {0} by {1}".format(creationID, uid))
            return Response({}, status=status.HTTP_200_OK)

    return Response({}, status=status.HTTP_200_OK)
