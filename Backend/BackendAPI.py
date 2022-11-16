from flask import Flask, request, jsonify, make_response, render_template
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, JWTManager
from flask_cors import CORS
import pymysql
import datetime
import hashlib
import requests

# Membuat server flask dan API KEY TMDB
app = Flask(__name__)
CORS(app)
app_key = "aef829310f8af509d6ebabe33b18f3e9"

# Flask JWT Extended Configuration
app.config['SECRET_KEY'] 					= "INI_SECRET_KEY"
app.config['JWT_HEADER_TYPE']				= "JWT"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] 		= datetime.timedelta(days=1) #1 hari token JWT expired
jwt = JWTManager(app)

mydb = pymysql.connect(
	host="localhost",
	user="root",
	passwd="",
	database="db_movie_rating"
)

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

### EXTERNAL API ###
@app.route('/get_trend_movie_list/<time>', methods=['GET'])
def get_trend_movie_list(time):
	try:
		url = ""
		payload={}
		headers = {}

		if time == "day":
			url = "https://api.themoviedb.org/3/trending/movie/day?api_key={}".format(app_key)
		elif time == "week":
			url = "https://api.themoviedb.org/3/trending/movie/week?api_key={}".format(app_key)

		response = requests.request("GET", url, headers=headers, data=payload)

		if int(response.status_code) != 200:
			raise Exception("Status Code is not 200")

		response_json = response.json()
		movie_data = response_json["results"]

		return make_response(jsonify(movie_data), 200)
	
	except Exception as e:
		response_json = {
			"Status" : "Failed to get trending movie list",
			"Description" : str(e)
		}
		return make_response(jsonify(response_json), 200)

@app.route('/get_popular_movie_list/<page>', methods=['GET'])
def get_popular_movie_list(page):
	try:
		url = "https://api.themoviedb.org/3/movie/popular?api_key={}".format(app_key)
		payload= {}
		headers = {}
		
		if page:
			url += "&page={}".format(page)

		response = requests.request("GET", url, headers=headers, data=payload)

		if int(response.status_code) != 200:
			raise Exception("Status Code is not 200")

		response_json = response.json()
		movie_data = response_json["results"]

		return make_response(jsonify(movie_data), 200)
	
	except Exception as e:
		response_json = {
			"Status" : "Failed to get popular movie list",
			"Description" : str(e)
		}
		return make_response(jsonify(response_json), 200)


### USER API ###
@app.route('/register_user', methods=['POST'])
def register_user():
	hasil = {"Status": "Register failed"}

	try:
		data = request.json
		email = data["email"]
		nickname = data["nickname"]
		username = data["username"]
		password = data["password"]

		if len(password) < 8:
			hasil = {"Status": "Your password needs to be atleast 8 character!"}
			return jsonify(hasil)

		username = username.lower()
		password_enc = hashlib.md5(password.encode('utf-8')).hexdigest()

		# Cek apakah username ada didalam database
		query = " SELECT username FROM user_list WHERE username = %s "
		values = (username, )

		mycursor = mydb.cursor()
		mycursor.execute(query, values)
		data_user = mycursor.fetchall()

		if len(data_user) > 0:
			hasil = {"Status": "The username that you enter already exsisted!"}
			return jsonify(hasil)

		# Register data baru
		query = "INSERT INTO user_list (email, nickname, username, password, user_type) VALUES(%s,%s,%s,%s,%s)"
		values = (email, nickname, username, password_enc, "MEMBER",)
		mycursor = mydb.cursor()
		mycursor.execute(query, values)
		mydb.commit()
		hasil = {"Status": "Register successful"}

	except Exception as e:
		print("Error: " + str(e))

	return jsonify(hasil)

@app.route("/login_user", methods=["POST"])
def login():
	access_token = ""

	try:
		data = request.json

		username = data["username"]
		password = data["password"]

		username = username.lower()
		password_enc = hashlib.md5(password.encode('utf-8')).hexdigest()

		# Cek kredensial didalam database
		query = " SELECT user_id, password, user_type FROM user_list WHERE username = %s "
		values = (username, )

		mycursor = mydb.cursor()
		mycursor.execute(query, values)
		data_user = mycursor.fetchall()

		if len(data_user) == 0:
			hasil = {"Status": "The username that you enter does not exsist!"}
			return jsonify(hasil)

		data_user	= data_user[0]

		user_id 	= data_user[0]
		db_password = data_user[1]
		user_type	= data_user[2]

		if password_enc != db_password:
			hasil = {"Status": "The password you enter is wrong!"}
			return jsonify(hasil)

		jwt_payload = {
			"user_id" : user_id,
			"user_type" : user_type
		}

		access_token = create_access_token(username, additional_claims=jwt_payload)

	except Exception as e:
		print("Error: " + str(e))

	return jsonify(access_token=access_token)

@app.route("/user_data", methods=["GET"])
@jwt_required()
def user_data():
	user_id = str(get_jwt()["user_id"])
	query = "SELECT * FROM user_list WHERE user_id = %s"
	values = (user_id,)

	mycursor = mydb.cursor()
	mycursor.execute(query, values)
	row_headers = [x[0] for x in mycursor.description]
	data = mycursor.fetchall()
	json_data = []
	for result in data:
		json_data.append(dict(zip(row_headers, result)))
	return make_response(jsonify(json_data),200)


### RATING API ###
@app.route('/insert_review', methods=['POST'])
@jwt_required()
def insert_review():
	hasil = {"status": "gagal insert data siswa"}

	user_id = str(get_jwt()["user_id"])

	try:
		data = request.json
		create_time = datetime.datetime.now()
		update_time = create_time

		query = "INSERT INTO rating_list(user_id, rating, comment, created_at, updated_at) VALUES(%s,%s,%s,%s,%s)"
		values = (user_id, data["rating"], data["comment"], create_time, update_time, )
		mycursor = mydb.cursor()
		mycursor.execute(query, values)
		mydb.commit()
		hasil = {"Status": "Review inserted successfuly!"}

	except Exception as e:
		print("Error: " + str(e))
		hasil = {
			"Status": "Insert failed!",
			"Error" : str(e)
		}

	return jsonify(hasil)


### MAIN ###
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5010, debug=True)
