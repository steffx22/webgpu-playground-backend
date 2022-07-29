# WebGPU Playground

## Getting started
### Setup python environment
Create a python virtual environment in the root directory
#### Mac
```
python3 -m venv env
source env/bin/activate
```

#### Windows PS
```
python3 -m venv env
.\env\Scripts\Activate.ps1
```

### Install development dependencies
```
pip3 install -r requirements.txt
```

## Run the server:
```
python manage.py runserver localhost:8000
```

## URLs to Use Server
### User Authentication
#### Logging In
To log in, a POST request is needed with the url extension:
```
userauthentication/login/
```
In the body of the POST these details are needed:
```
username: user's username
password: user's password
```
Returns:
```
uid: the user's unique id, used for creating files
admin: whether or not the user is an admin
```

#### Sign up
To register a new user, a POST request is needed with the url extension:
```
userauthentication/register/
```
In the body of the POST these details are needed:
```
email: user's email
password: user's password
username: user's username
```
Returns:
```
uid: the user's unique id, used for creating files
ERROR 100: email already taken
ERROR 101: username already taken
ERROR 150: password is too short
ERROR 700: profanity in username
```

### File Management
#### Saving data
To save the code written by a user, use a POST request with this url:
```
filemanagement/saveFile/
```
In the body of the POST these details are needed:
```
vertex: the raw string containing the vertex code
fragment: the raw string containing the fragment code
primitive: the primitive of the file
vertexBuffer: the raw string of the vertex buffer
colourBuffer: the raw string of the colour buffer
compute: the raw data of the compute file
uid: user's unique id
name: name of the creation
displayName: name that is displayed and picked by the user
updateFile: whether this is updating a creation or making a new one
public: whether this file will be publicly available or private
image: a png file of the creation 
tags: a space separated string of associated tags
```
Returns:
```
No return
```

#### Downloading a file
To download existing data, use a GET request with this url:
```
filemanagement/getFile/
```
Parameters:
```
filePath: path of the file which takes the form of "{creatorId}/{creationName}
```
Returns:
```
vertex: the raw string containing the vertex code
fragment: the raw string containing the fragment code
primitive: the primitive of the file
visibility: visibility of the file
vertexBuffer: raw data of the vertex buffer
colourBuffer: raw data of the colour buffer
compute: the raw data of the compute file
displayName: the user chosen name of the creation
vertexCount: the vertex count
tags: the creation's tags
```

#### Getting a list of all creations
To download existing data, use a GET request with this url:
```
filemanagement/getAllCreations/
```
Parameters:
```
tag: optional parameter used for searching through tags, creation name and username
```
Returns:
```
creations: a list of all creations containing {
    creationName: name of the creation
    uid: id of the creator
    creationDate: the date and time of the creation
    rating: dictionary containing the number of stars given (1-5)
    averageRating: average rating for the creation
    username: username of the person who created it
    primitive: the primitive of the creation
    url: the url of the snapshot of the creation
    tags: the associated tags
    displayName: the user chosen name of the creation
}
```

#### Getting a list of all a user's creations
To download existing data, use a GET request with this url:
```
filemanagement/getAllUserCreations/
```
Parameters:
```
uid: id of the user who's creations your getting
tag: optional parameter used for searching through tags, creation name and username
```
Returns:
```
creations: a list of all creations containing {
    creationName: name of the creation
    uid: id of the creator
    creationDate: the date and time of the creation
    rating: dictionary containing the number of stars given (1-5)
    averageRating: average rating for the creation
    username: username of the person who created it
    primitive: the primitive of the creation
    url: the url of the snapshot of the creation
    tags: the associated tags
    displayName: the user chosen name of the creation
}
```

#### Giving/Changing a Rating
To give a creation a rating, use a POST request with this url:
```
filemanagement/updateRating/
```
Parameters:
```
creationName: name of the creation being rated
newRating: the new rating being given
raterID: the id of the person rating
```
Returns:
```
No return
```

#### Updating a Creation's Visibility
To change a creation's visibility to the public, use a POST request with this url:
```
filemanagement/updateVisibility/
```
Parameters:
```
uid: the uid of the creator
creationName: name of the creation being rated
public: whether or not the creation is publicly available
```
Returns:
```
No return
```

#### Submitting a Creation for Ratings
To give a creation a rating, it must first be submitted using a POST request with this url:
```
filemanagement/submitCreation/
```
Parameters:
```
uid: uid of user who is submitting their creation
creationID = the id of the creation being submitted
```
Returns:
```
No return
```

#### Fetching all Submissions
To download all the submitted creations, use a GET request with this url:
```
filemanagement/getAllSubmissions/
```
Parameters:
```
tag: optional parameter used for searching through tags, creation name and username
```
Returns:
```
creations: a list of all submissions containing {
    creationName: name of the creation
    uid: id of the creator
    creationDate: the date and time of the creation
    rating: dictionary containing the number of stars given (1-5)
    averageRating: average rating for the creation
    username: username of the person who created it
    primitive: the primitive of the creation
    url: the url of the snapshot of the creation
    tags: the associated tags
    displayName: the user chosen name of the creation
}
```

#### Downloading a Submission
To download a specific submission, use a GET request with this url:
```
filemanagement/getSubmission/
```
Parameters:
```
creationID: the id of the creation in question
```
Returns:
```
vertex: the raw string containing the vertex code
fragment: the raw string containing the fragment code
primitive: the primitive of the file
visibility: visibility of the file
vertexBuffer: raw data of the vertex buffer
colourBuffer: raw data of the colour buffer
compute: the raw data of the compute file
displayName: the user chosen name of the creation
vertexCount: the vertex count
raters: all the people who have rated and their ratings
ratings: the scores given by the raters
averageRating: the average rating
```

#### Deleting a Creation
To delete a specific submission, use a POST request with this url:
```
filemanagement/deleteCreation/
```
Parameters:
```
uid: uid of the creation's creator
creationID: the id of the creation in question
```
Returns:
```
No return
```

#### Add an Admin
To add an admin from an admin account use this POST url:
```
userauthentication/addAdmin/
```
Parameters:
```
currentUid: uid of the current admin
newAdminUsername: username of the admin to be created
```
Returns:
```
No return
```

#### Report a Creation
To report a specific submission, use a POST request with this url:
```
filemanagement/report/
```
Parameters:
```
creationName: name of the creation
creatorId: the id of the creator who made the creation
message: message of the report
isSubmission: boolean if it was a submission or not
```
Returns:
```
No return
```

#### Unreport a Creation
To unreport a specific submission, use a POST request with this url:
```
filemanagement/unreport/
```
Parameters:
```
uid: the uid of the admin unreporting
creationName: name of the creation
creatorId: the id of the creator who made the creation
isSubmission: boolean if it was a submission or not
```
Returns:
```
No return
```

#### Get All Reported Creations
To get all reported submissions, use a GET request with this url:
```
filemanagement/gerReported/
```
Parameters:
```
No Parameters
```
Returns:
The return is a nested dictionary of:
```
creations: all reported creations
submissions: all reported submissions
```
Which both have the structure:
```
vertex: the raw string containing the vertex code
fragment: the raw string containing the fragment code
primitive: the primitive of the file
visibility: visibility of the file
vertexBuffer: raw data of the vertex buffer
colourBuffer: raw data of the colour buffer
compute: the raw data of the compute file
displayName: the user chosen name of the creation
vertexCount: the vertex count
raters: all the people who have rated and their ratings
ratings: the scores given by the raters
averageRating: the average rating
reportCount: number of reports given to the creation
```