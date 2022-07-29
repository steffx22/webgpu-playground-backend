from firebaseModels.app import pb_init
import pyrebase
import os


class StorageModel:
    def __init__(self) -> None:
        self.firebase = pb_init()
        self.storage = self.firebase.storage()

    def instantiate_new_files(self, files: list[str], data: list[str], path: str):
        for (file_name, data) in zip(files, data):
            self.makeTextFileAndSave(path + file_name, data)

    def makeTextFileAndSave(self, pathToSaveTo: str, rawData: str):
        tmpFileName: str = (pathToSaveTo + ".txt").replace("/", "-")
        with open(tmpFileName, "w") as file:
            file.write(rawData)
            file.close()
        self.uploadFile(pathToSaveTo + ".txt", tmpFileName)
        os.remove(tmpFileName)

    def instantiate_default_files(self, files: list[str], path: str):
        for file in files:
            self.save_file(path + file, "defaults\\{0}.txt".format(file))

    def get_all_files(self, files: list[str], path: str, prefix="creations"):
        d = {}
        for file in files:
            d[file] = self.getTextFileData(prefix + "/{0}/{1}.txt".format(path, file))
        return d

    def save_file(self, pathToSaveTo: str, path: str):
        self.uploadFile(pathToSaveTo + ".txt", path)

    def uploadFile(self, storagePath, localPath):
        return self.storage.child(storagePath).put(localPath, token="test")

    def downloadFile(self, storagePath, localPath):
        self.storage.child(storagePath).download(storagePath, localPath)

    def getURL(self, path, token):
        return self.storage.child(path).get_url(token)

    def getTextFileData(self, storagePath):
        tmpFileName: str = storagePath.replace("/", "-")
        try:
            self.downloadFile(storagePath, tmpFileName)
            with open(tmpFileName, "r") as file:
                data = file.read()
                file.close()

            os.remove(tmpFileName)

            return data
        except:
            return ""

    def deleteFile(self, path):
        try:
            self.storage.delete(path, None)
        except:
            pass

    def deleteFolder(self, path, files, collection):
        for file in files:
            self.deleteFile(f"{collection}/{path}/{file}.txt")
        self.deleteFile(f"{collection}/{path}/image.png")


if __name__ == "__main__":
    storageModel = StorageModel()
