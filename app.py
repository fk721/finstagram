#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import hashlib
import os
import time
import base64
import json

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port = 3306,
                       user='root',
                       password='Root1234!',
                       db='finstagram',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

SALT = "cs3083"
IMAGES_DIR = os.path.join(os.getcwd(), "images")

def convertToBinaryData(filename):
    f = open(filename, 'rb')
    binaryData = base64.b64encode(f.read()).decode("utf-8")
    return binaryData

#Define a route to hello function
@app.route('/')
def hello():
    # return render_template('index.html')
    try:
        return home()
    except:
        return login()

#Define route for login
@app.route('/login')
def login():
    return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    username = request.form['username']
    password = (SALT + request.form['password']).encode("utf-8")

    # Get the hashed password
    h = hashlib.new("sha256")
    h.update(password)
    hashedPassword = h.hexdigest()

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM Person WHERE username = %s and password = %s'
    cursor.execute(query, (username, hashedPassword))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if (data):
        #creates a session for the the user
        #session is a built in
        session['username'] = username
        return redirect(url_for('home'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username  = request.form['username']
    password  = (SALT + request.form['password']).encode('utf-8') 
    firstName = request.form['first-name']
    lastName  = request.form['last-name']
    bio       = request.form['bio']
    # Get the hashed password
    h = hashlib.new("sha256")
    h.update(password)
    hashedPassword = h.hexdigest()

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM Person WHERE username = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if (data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO Person VALUES(%s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, hashedPassword, firstName, lastName, bio))
        conn.commit()
        cursor.close()
        return render_template('login.html')


@app.route('/home')
def home():
    try:
        user = session['username']
        cursor = conn.cursor()
        # query = 'SELECT * FROM Photo WHERE photoPoster = %s ORDER BY postingdate DESC'
        # cursor.execute(query, (user))

        query = 'SELECT photoID, postingdate, photoBlob, caption, photoPoster \
                FROM (SELECT * FROM Photo P JOIN Follow F ON (P.photoPoster = F.username_followed) WHERE followstatus = True AND allFollowers = True \
                AND username_follower = %s OR %s IN (SELECT member_username FROM BelongTo WHERE groupName IN (SELECT groupName FROM SharedWith WHERE photoID =  P.photoID))) \
                AS T \
                UNION \
                (SELECT photoID, postingdate, photoBlob, caption, photoPoster \
                FROM Photo \
                WHERE photoPoster = %s) \
                ORDER BY postingdate DESC'
        
        cursor.execute(query, (user, user, user))

        photos = cursor.fetchall()
        cursor.close()
        return render_template('home.html', username=user, photos=photos)
    except:
        return render_template('login.html')

@app.route("/upload", methods=["GET"])
def upload():
    try:
        user = session['username']
        return render_template("upload.html")
    except:
        return render_template('login.html')

@app.route("/uploadImage", methods=["POST"])
def upload_image():
    if 'username' in session:
        if request.files:
            image_file = request.files.get("imageToUpload", "")
            image_name = image_file.filename
            filepath = os.path.join(IMAGES_DIR, image_name)
            image_file.save(filepath)

            blobData = convertToBinaryData(filepath)
            caption = request.form['caption']
            visible = False
            if request.form['options'] == 'allFollowers':
                visible = True
            
            # print(blobData, visible, caption, session['username'])

            cursor = conn.cursor()
            query = "INSERT INTO Photo (postingdate, photoBlob, allFollowers, caption, photoPoster) VALUES (%s, %s, %s,%s, %s)"
            cursor.execute(query, (time.strftime('%Y-%m-%d %H:%M:%S'), blobData, visible, caption, session['username']))
            conn.commit()
            cursor.close()

            message = "Image has been successfully uploaded."
            return render_template("upload.html", message=message)
        else:
            message = "Failed to upload image."
            return render_template("upload.html", message=message)
    else:
        return render_template('login.html')

@app.route("/get_info", methods=["POST"])
def getInfo():
    photoID = request.get_data().decode('utf-8')
    cursor = conn.cursor()

    # Get firstName, lastName of photoPoster, timestamp
    query = 'SELECT firstName, lastName, photoID FROM Photo JOIN Person ON (Photo.photoPoster = Person.username) WHERE photoID = %s'
    cursor.execute(query, (photoID))
    posterStats = cursor.fetchone()

    # Get number of likes
    query = 'SELECT count(*) AS numLikes FROM Likes WHERE photoID = %s'
    cursor.execute(query, (photoID))
    numLikes = cursor.fetchone()['numLikes']

    # Get username, first names, last names of people tagged
    cursor = conn.cursor()
    query = 'SELECT username, firstName, lastName FROM Tagged JOIN Person USING(username) WHERE tagstatus = True AND photoID = %s'
    cursor.execute(query, (photoID))
    taggedUsers = json.dumps(cursor.fetchall())

    # Get username of people who liked the photo and the rating they gave it
    cursor = conn.cursor()
    query = 'SELECT username, rating FROM Likes WHERE photoID = %s'
    cursor.execute(query, (photoID))
    likedUsers = json.dumps(cursor.fetchall())
    cursor.close()

    # print(posterStats, numLikes, taggedUsers, likedUsers)

    print("Tagged Users:",taggedUsers)
    print("Liked Users:",likedUsers)
    return json.dumps({'status':'OK','posterStats':posterStats,'numLikes':numLikes, 'taggedUsers': taggedUsers, 'likedUsers' : likedUsers})
    

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')
        
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    if not os.path.isdir("images"):
        os.mkdir(IMAGES_DIR)
    app.run('127.0.0.1', 5000, debug = True)