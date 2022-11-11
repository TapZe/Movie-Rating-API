from flask import Flask, request, jsonify, make_response
import pymysql, requests

# Membuat server flask
app = Flask(__name__)

mydb = pymysql.connect(
	host="localhost",
	user="root",
	passwd="",
	database="db_movie_rating"
)

@app.route('/')
@app.route('/index')
def index():
	return "<h1>Data Movie Backend API</h1>"

@app.route('/get_trend_movie_list/<time>', methods=['GET'])
def get_trend_movie_list(time):
	try:
		url = ""
		payload={}
		headers = {}
		app_key = "aef829310f8af509d6ebabe33b18f3e9"

		if time == "day":
			url = "https://api.themoviedb.org/3/trending/movie/day?api_key={}".format(app_key)
		elif time == "week":
			url = "https://api.themoviedb.org/3/trending/movie/week?api_key={}".format(app_key)

		response = requests.request("GET", url, headers=headers, data=payload)

		if int(response.status_code) != 200:
			raise Exception("Status Code tidak 200")

		response_json = response.json()

		return make_response(jsonify(response_json), 200)
	
	except Exception as e:
		response_json = {
			"status" : "Gagal mendapatkan list movie",
			"description" : str(e)
		}
		return make_response(jsonify(response_json), 200)

@app.route('/get_popular_movie_list/<page>', methods=['GET'])
def get_popular_movie_list(page):
	try:
		app_key = "aef829310f8af509d6ebabe33b18f3e9"
		url = "https://api.themoviedb.org/3/movie/popular?api_key={}".format(app_key)
		payload= {}
		headers = {}
		
		if page:
			url += "&page={}".format(page)

		response = requests.request("GET", url, headers=headers, data=payload)

		if int(response.status_code) != 200:
			raise Exception("Status Code tidak 200")

		response_json = response.json()

		return make_response(jsonify(response_json), 200)
	
	except Exception as e:
		response_json = {
			"status" : "Gagal mendapatkan list movie",
			"description" : str(e)
		}
		return make_response(jsonify(response_json), 200)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5010, debug=True)
