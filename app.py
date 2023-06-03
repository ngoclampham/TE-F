from flask import Flask, render_template, request
import sqlite3
import requests


app = Flask(__name__)


def validate_user(email, password):
    print("validating user...")
    user = {}

    conn = sqlite3.connect('./static/data/activity_tracker.db')
    curs = conn.cursor()
    #get all columns if there is a match
    result  = curs.execute("SELECT name, email, phone FROM users WHERE email=(?) AND password= (?)", [email, password])
  
    for row in result:
       user = {'name': row[0],  'email': row[1], 'phone': row[2]}
         
    conn.close()
    return user

def store_sugg(name, street_add, street_name, city):
    conn = sqlite3.connect('./static/data/activity_monitor.db')
    curs = conn.cursor()
    curs.execute("INSERT INTO underground_spots (name, street_add, street_name, city) VALUES((?),(?),(?),(?))",
        (name, street_add, street_name, city))
    conn.commit()
    conn.close()

def store_user(name, email, phone, pw):
    conn = sqlite3.connect('./static/data/activity_tracker.db')
    curs = conn.cursor()
    curs.execute("INSERT INTO users (name, email, phone, password) VALUES((?),(?),(?),(?))",
        (name, email, phone, pw))
    
    conn.commit()
    conn.close()


def get_all_users():
    conn = sqlite3.connect('./static/data/activity_tracker.db')
    curs = conn.cursor()
    all_users = [] # will store them in a list
    rows = curs.execute("SELECT rowid, * from users")
    for row in rows:
        user = {'rowid': row[0],
                'name' : row[1], 
                'email': row[2],
                'phone': row[3],
                }
        all_users.append(user)

    conn.close()

    return all_users


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/home')
def home():
    response = requests.get("https://animechan.vercel.app/api/random")
    json_data = response.json()
    return render_template('home.html', data=json_data)

@app.route('/login_user' , methods=['POST', 'GET'])
def login_user():
    response = requests.get("https://animechan.vercel.app/api/random")
    json_data = response.json()

    email = request.form['email']
    password = request.form['password']

    data = {}
    user = validate_user(email, password)
    
    if user:
        data = {
            "anime": json_data["anime"],
            "quote": json_data["quote"],
            "character" : json_data["character"]
        }

        #load home if there is a user, along with data.
        return render_template('home.html', data=data)
         

    else: 
        error_msg = "Login failed"

        data = {
            "error_msg": error_msg
        }
        #no user redirects back to the main login page, with error msg.
        return render_template('index.html', data=data)

@app.route('/post_sugg' , methods=['POST', 'GET'])
def post_sugg():
    name= request.form.get('name')
    street_add= request.form.get('street_add')
    street_name= request.form.get('street_name')
    city= request.form.get('city')
    
    store_sugg(name, street_add, street_name, city)

    suggs = get_all_users()
    # print(users)

    #get the last user entered
    new_sugg = suggs.pop()

    return render_template('contribute.html', sugg=new_sugg)


@app.route('/another')
def another():
    conn = sqlite3.connect('./static/data/activity_monitor.db')
    curs = conn.cursor()
    curs.execute('SELECT * FROM underground_spots')
    data = curs.fetchall()

    # all_spots = []
    # rows = curs.execute("SELECT * from underground_spots")
    # for row in rows:
    #     spot = {'name': row[0],
    #             'street_add' : row[1], 
    #             'street_name': row[2],
    #             'city': row[3],
    #             'zip': row[4]
    #             }
    #     all_spots.append(spot)
    # conn.close()
    
    return render_template('another.html', data=data)


@app.route('/post_user' , methods=['POST'])
def post_user():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    pw = request.form['password']
    
    store_user(name, email, phone, pw)

    users = get_all_users()
    # print(users)

    #get the last user entered
    new_user = users.pop()


    return render_template('index.html', user=new_user)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='4000')