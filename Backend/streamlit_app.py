import streamlit as st
from streamlit_option_menu import option_menu
import requests
import json

# VAR INIT
if 'user_token' not in st.session_state:
    st.session_state['user_token'] = ''
if 'header' not in st.session_state:
    st.session_state['header'] = {'Content-Type': 'application/json'}
if 'btn_home' not in st.session_state:
    st.session_state['btn_home'] = ''
if 'btn_search' not in st.session_state:
    st.session_state['btn_search'] = ''
if 'btn_change_details' not in st.session_state:
    st.session_state['btn_change_details'] = False
if 'btn_change_success' not in st.session_state:
    st.session_state['btn_change_success'] = ''
if 'btn_change_msg' not in st.session_state:
    st.session_state['btn_change_msg'] = ''
if 'btn_login_regis' not in st.session_state:
    st.session_state['btn_login_regis'] = ''
my_header = st.session_state['header']

st.write(my_header)
st.write(st.session_state['user_token'])
st.write("{}".format(st.session_state['btn_home']))
st.write("{}".format(st.session_state['btn_search']))
st.write("{}".format(st.session_state['btn_change_details']))
st.write("{}".format(st.session_state['btn_change_success']))
st.write("{}".format(st.session_state['btn_change_msg']))
st.write("{}".format(st.session_state['btn_login_regis']))

# HEADER
st.title("Movie Rating API")
choice = option_menu("Navigation", ["Home Page", "Search", "Account"], icons=["house", "search", "person-circle"],menu_icon="cast", orientation="horizontal")
st.markdown("##")

# HOME PAGE
if choice == "Home Page":
    st.session_state['btn_login_regis'] = ''
    st.session_state['btn_change_details'] = ''
    st.session_state['btn_search'] = ''
    st.session_state['btn_change_success'] = ''
    st.session_state['btn_change_msg'] = ''
    data = requests.get("http://localhost:5010/get_trend_movie_list/week").json()

    st.header("Trending Right Now")
    st.write("---")
    for i in range(0, 10):
        with st.container():
            col = st.columns(2)

            # LEFT DATA
            with col[0]:
                thisdata = data[i]
                movie_id = thisdata["id"]
                average_rating = requests.get("http://localhost:5010/get_movie_average_rating/{}".format(movie_id)).json()
                st.image("https://www.themoviedb.org/t/p/w220_and_h330_face/{}".format(thisdata["backdrop_path"]))
                st.subheader(thisdata["original_title"])
                st.write("**Movie Rating: :star2: {}**".format(thisdata["vote_average"]))
                st.write("**Movie Users Rating: :star2: {}**".format(average_rating["Average Rating"]))
                st.write("Overview: {}".format(thisdata["overview"]))
                btn1 = st.button("Review List >", key=thisdata["id"])
            if btn1:
                st.session_state['btn_home'] = i
                st.experimental_rerun()
            if st.session_state['btn_home'] == i:
                btn1 = True
            else:
                btn1 = False
            if btn1:
                with st.container():
                    review_list = requests.get("http://localhost:5010/get_movie_review_list?movie_id_number={}".format(movie_id)).json()
                    tabs = st.tabs(["Reviews", "Your Reviews"])
                    with tabs[0]:
                        is_reviewed = False
                        for review in review_list:
                            nickname = requests.get("http://localhost:5010/get_user_nickname/{}".format(review["user_id"])).json()[0]["nickname"]
                            with st.container():
                                st.markdown("---")
                                st.write("**A review by {} with :star2: {}**".format(nickname, review['rating']))
                                if review['created_at'] == review['updated_at']:
                                    st.caption("Written by {} on {}".format(nickname, review["created_at"]))
                                else:
                                    st.caption("Written by {} on {} and edited on {}".format(nickname, review["created_at"], review['updated_at']))
                                st.write("#")
                                st.write(review["comment"])
                                st.markdown("---")
                            is_reviewed = True
                        if not is_reviewed:
                            st.info("This movie has never been reviewed!")
                    with tabs[1]:
                        if st.session_state['user_token'] == '':
                            st.error("You must login first!")
                        else:
                            url = "http://localhost:5010/get_user_review_list"
                            account_reviews = requests.get(url, headers=my_header).json()
                            is_reviewed = False
                            for review in account_reviews:
                                if review["movie_id"] == movie_id:
                                    nickname = requests.get("http://localhost:5010/get_user_nickname/{}".format(review["user_id"])).json()[0]["nickname"]
                                    with st.container():
                                        st.write("**A review by You ({}) with :star2: {}**".format(nickname, review['rating']))
                                        if review['created_at'] == review['updated_at']:
                                            st.caption("Written by You ({}) on {}".format(nickname, review["created_at"]))
                                        else:
                                            st.caption("Written by You ({}) on {} and edited on {}".format(nickname, review["created_at"], review['updated_at']))
                                        st.write("#")
                                        st.write(review["comment"])
                                        st.markdown("---")
                                    with st.form("update_review_form"):
                                        st.subheader("Edit Your Review")
                                        rating_val = st.number_input("Edit your rating", step=1, min_value=0, max_value=10,value=review['rating'])
                                        comment = st.text_area("Edit your comment about the movie", placeholder=review['comment'])
                                        submitted = st.form_submit_button("Submit Review")
                                        st.info("You don't need to fill anything or just ignore this if you don't want to edit.")
                                        if submitted:
                                            url = "http://localhost:5010/update_user_review"
                                            payload = json.dumps({
                                                "review_id": review['review_id'],
                                                "rating": rating_val,
                                                "comment": comment
                                            })
                                            response = requests.put(url, headers=my_header, data=payload).json()
                                            st.success("Your review has been edited!")
                                            st.experimental_rerun()
                                    is_reviewed = True
                            if not is_reviewed:
                                st.info("You never reviewed this movie!")
                                with st.form("review_form"):
                                    st.subheader("Add Your Review")
                                    rating_val = st.number_input("Insert your rating", step=1, min_value=0, max_value=10)
                                    comment = st.text_area("Insert your comment about the movie")
                                    submitted = st.form_submit_button("Submit Review")
                                    if submitted:
                                        url = "http://localhost:5010/insert_review"
                                        payload = json.dumps({
                                            "movie_id": movie_id,
                                            "rating": rating_val,
                                            "comment": comment
                                        })
                                        response = requests.post(url, headers=my_header, data=payload).json()
                                        st.success("Your review has been added!")
                                        st.experimental_rerun()
                st.markdown("---")

            # RIGHT DATA
            with col[1]:
                thisdata = data[i+10]
                movie_id = thisdata["id"]
                average_rating = requests.get("http://localhost:5010/get_movie_average_rating/{}".format(movie_id)).json()
                st.image("https://www.themoviedb.org/t/p/w220_and_h330_face/{}".format(thisdata["backdrop_path"]))
                st.subheader(thisdata["original_title"])
                st.write("**Movie Rating: :star2: {}**".format(thisdata["vote_average"]))
                st.write("**Movie Users Rating: :star2: {}**".format(average_rating["Average Rating"]))
                st.write("Overview: {}".format(thisdata["overview"]))
                btn2 = st.button("Review List >", key=thisdata["id"])
            if btn2:
                st.session_state['btn_home'] = i+10
                st.experimental_rerun()
            if st.session_state['btn_home'] == i+10:
                btn2 = True
            else:
                btn2 = False
            if btn2:
                with st.container():
                    review_list = requests.get("http://localhost:5010/get_movie_review_list?movie_id_number={}".format(movie_id)).json()
                    tabs = st.tabs(["Reviews", "Your Reviews"])
                    with tabs[0]:
                        is_reviewed = False
                        for review in review_list:
                            nickname = requests.get("http://localhost:5010/get_user_nickname/{}".format(review["user_id"])).json()[0]["nickname"]
                            with st.container():
                                st.markdown("---")
                                st.write("**A review by {} with :star2: {}**".format(nickname, review['rating']))
                                if review['created_at'] == review['updated_at']:
                                    st.caption("Written by {} on {}".format(nickname, review["created_at"]))
                                else:
                                    st.caption("Written by {} on {} and edited on {}".format(nickname, review["created_at"], review['updated_at']))
                                st.write("#")
                                st.write(review["comment"])
                                st.markdown("---")
                            is_reviewed = True
                        if not is_reviewed:
                            st.info("This movie has never been reviewed!")
                    with tabs[1]:
                        if st.session_state['user_token'] == '':
                            st.error("You must login first!")
                        else:
                            url = "http://localhost:5010/get_user_review_list"
                            account_reviews = requests.get(url, headers=my_header).json()
                            is_reviewed = False
                            for review in account_reviews:
                                if review["movie_id"] == movie_id:
                                    nickname = requests.get("http://localhost:5010/get_user_nickname/{}".format(review["user_id"])).json()[0]["nickname"]
                                    with st.container():
                                        st.write("**A review by You ({}) with :star2: {}**".format(nickname, review['rating']))
                                        if review['created_at'] == review['updated_at']:
                                            st.caption("Written by You ({}) on {}".format(nickname, review["created_at"]))
                                        else:
                                            st.caption("Written by You ({}) on {} and edited on {}".format(nickname, review["created_at"], review['updated_at']))
                                        st.write("#")
                                        st.write(review["comment"])
                                        st.markdown("---")
                                    with st.form("update_review_form"):
                                        st.subheader("Edit Your Review")
                                        rating_val = st.number_input("Edit your rating", step=1, min_value=0, max_value=10,value=review['rating'])
                                        comment = st.text_area("Edit your comment about the movie", placeholder=review['comment'])
                                        submitted = st.form_submit_button("Edit Your Review")
                                        st.info("You don't need to fill anything or just ignore this if you don't want to edit.")
                                        if submitted:
                                            url = "http://localhost:5010/update_user_review"
                                            payload = json.dumps({
                                                "review_id": review['review_id'],
                                                "rating": rating_val,
                                                "comment": comment
                                            })
                                            response = requests.put(url, headers=my_header, data=payload).json()
                                            st.success("Your review has been edited!")
                                            st.experimental_rerun()
                                    is_reviewed = True
                            if not is_reviewed:
                                st.info("You never reviewed this movie!")
                                with st.form("review_form"):
                                    st.subheader("Add Your Review")
                                    rating_val = st.number_input("Insert your rating", step=1, min_value=0, max_value=10)
                                    comment = st.text_area("Insert your comment about the movie")
                                    submitted = st.form_submit_button("Submit Review")
                                    if submitted:
                                        url = "http://localhost:5010/insert_review"
                                        payload = json.dumps({
                                            "movie_id": movie_id,
                                            "rating": rating_val,
                                            "comment": comment
                                        })
                                        response = requests.post(url, headers=my_header, data=payload).json()
                                        st.success("Your review has been added!")
                                        st.experimental_rerun()
                st.markdown("---")
            st.markdown("##")
    st.write("---")

# SEARCH PAGE
if choice == "Search":
    st.session_state['btn_login_regis'] = ''
    st.session_state['btn_home'] = ''
    st.session_state['btn_change_details'] = ''
    st.session_state['btn_change_msg'] = ''
    st.session_state['btn_change_success'] = ''

    st.header("Search Your Movie")
    st.write("---")
    query = st.text_input("Movie Name:")
    st.write("##")
    if query:
        count = 0
        data_list = requests.get("http://localhost:5010/search_movie/{}".format(query)).json()

        for data in data_list:
            with st.container():
                movie_id = data["id"]
                review_list = requests.get("http://localhost:5010/get_movie_review_list?movie_id_number={}".format(movie_id)).json()
                average_rating = requests.get("http://localhost:5010/get_movie_average_rating/{}".format(movie_id)).json()
                st.write("---")
                st.image("https://www.themoviedb.org/t/p/w220_and_h330_face/{}".format(data["backdrop_path"]))
                st.subheader(data["original_title"])
                st.write("**Movie TMDB Rating: :star2: {}**".format(data["vote_average"]))
                st.write("**Movie Users Rating: :star2: {}**".format(average_rating["Average Rating"]))
                st.write("Overview: {}".format(data["overview"]))
                btn = st.button("Open Reviews >", key=data["id"])
                if btn:
                    st.session_state['btn_search'] = count
                if st.session_state['btn_search'] == count:
                    btn = True
                else:
                    btn = False
                if btn:
                    with st.container():
                        tabs = st.tabs(["Reviews", "Your Reviews"])
                        with tabs[0]:
                            is_reviewed = False
                            for review in review_list:
                                nickname = requests.get("http://localhost:5010/get_user_nickname/{}".format(review["user_id"])).json()[0]["nickname"]
                                with st.container():
                                    st.markdown("---")
                                    st.write("**A review by {}**".format(nickname))
                                    st.caption("Written by {} on {}".format(nickname, review["created_at"]))
                                    st.write("#")
                                    st.write("**Review Movie Rating: :star2: {}**".format(review["rating"]))
                                    st.write(review["comment"])
                                    st.markdown("---")
                                is_reviewed = True
                            if not is_reviewed:
                                st.info("This movie has never been reviewed!")
                        with tabs[1]:
                            if st.session_state['user_token'] == '':
                                st.error("You must login first!")
                            else:
                                url = "http://localhost:5010/get_user_review_list"
                                account_reviews = requests.get(url, headers=my_header).json()
                                is_reviewed = False
                                for review in account_reviews:
                                    if review["movie_id"] == movie_id:
                                        nickname = requests.get("http://localhost:5010/get_user_nickname/{}".format(review["user_id"])).json()[0]["nickname"]
                                        with st.container():
                                            st.write("**A review by You ({})**".format(nickname))
                                            st.caption("Written by You ({}) on {}".format(nickname, review["created_at"]))
                                            st.write("#")
                                            st.write("**Review Movie Rating: :star2: {}**".format(review["rating"]))
                                            st.write(review["comment"])
                                        is_reviewed = True
                                if not is_reviewed:
                                    st.info("You never reviewed this movie!")
                                    with st.form("review_form"):
                                        st.subheader("Add Your Review")
                                        rating_val = st.number_input("Insert your rating", step=1, min_value=0, max_value=10)
                                        comment = st.text_area("Insert your comment about the movie")
                                        submitted = st.form_submit_button("Submit Review")
                                        if submitted:
                                            url = "http://localhost:5010/insert_review"
                                            payload = json.dumps({
                                                "movie_id": movie_id,
                                                "rating": rating_val,
                                                "comment": comment
                                            })
                                            response = requests.post(url, headers=my_header, data=payload).json()
                                            st.success("Your review has been added!")
                                            st.experimental_rerun()
            count += 1

if choice == "Account":
    st.session_state['btn_home'] = ''
    st.session_state['btn_search'] = ''
    
    st.header("Account Details")
    response = requests.get("http://localhost:5010/user_data", headers=my_header)
    if response.status_code != 200:
        st.info("You are logged out!")
        login = st.button("Login")
        st.write("or")
        register = st.button("Register")

        if login:
            st.session_state['btn_login_regis'] = 'Login'
        if register:
            st.session_state['btn_login_regis'] = 'Register'

        # LOGIN FORM
        if st.session_state['btn_login_regis'] == 'Login':
            st.markdown("---")
            with st.form("Login Form"):
                username = st.text_input(
                    label="Username"
                )
                password = st.text_input(
                    label="Password"
                )
                clicked = st.form_submit_button("Login", type="primary")

                if clicked:
                    url = "http://localhost:5010/login_user"
                    data_json = {}
                    if username != "":
                        data_json.update({"username": username})
                    if password != "":
                        data_json.update({"password": password})
                    payload = json.dumps(data_json)
                    response = requests.post(url, headers=my_header, data=payload)
                    data_json = response.json()

                    if response.status_code == 200:
                        st.session_state['user_token'] = data_json['access_token']
                        st.session_state['header'] = {'Content-Type': 'application/json', "Authorization": "JWT {}".format(data_json['access_token'])}
                    else:
                        st.error(data_json['Status'])
                    
                    st.session_state['btn_login_regis'] = ''
                    st.experimental_rerun()
        
        # REGISTER FORM
        if st.session_state['btn_login_regis'] == 'Register':
            st.markdown("---")
            with st.form("Register Form"):
                email = st.text_input(
                    label="Email"
                )
                nickname = st.text_input(
                    label="Nickname"
                )
                username = st.text_input(
                    label="Username"
                )
                password = st.text_input(
                    label="Password"
                )
                clicked = st.form_submit_button("Register", type="primary")

                if clicked:
                    url = "http://localhost:5010/register_user"
                    data_json = {}
                    if email != "":
                        data_json.update({"email": email})
                    if nickname != "":
                        data_json.update({"nickname": nickname})
                    if username != "":
                        data_json.update({"username": username})
                    if password != "":
                        data_json.update({"password": password})
                    payload = json.dumps(data_json)
                    response = requests.post(url, headers=my_header, data=payload)
                    data_json = response.json()

                    if response.status_code == 200:
                        st.success(data_json['Status'])
                    else:
                        st.error(data_json['Status'])
                    
                    st.session_state['btn_login_regis'] = ''
                    st.experimental_rerun()
    else:
        response = response.json()[0]
        st.write("##")
        st.text_input(
            label="Email",
            disabled=True,
            placeholder=response["email"]
        )
        st.text_input(
            label="Nickname",
            disabled=True,
            placeholder=response["nickname"]
        )
        st.text_input(
            label="Username",
            disabled=True,
            placeholder=response["username"]
        )
        st.text_input(
            label="Password",
            disabled=True,
            placeholder="********"
        )
        change = st.button("Change Account Details")
        sign_out = st.button("Sign Out", type="primary")

        if sign_out:
            st.session_state["user_token"] = ''
            st.session_state['header'] = {'Content-Type': 'application/json'}
            st.experimental_rerun()

        placeholder = st.empty()
        if st.session_state['btn_change_success'] == True:
            placeholder.success("Update Success!")
        elif st.session_state['btn_change_success'] == False:
            placeholder.error(st.session_state['btn_change_msg'])

        if change:
            st.session_state['btn_change_details'] = True

        if st.session_state['btn_change_details']:
            st.markdown("---")
            cancel = st.button("Cancel", type="primary")

            if cancel:
                st.session_state['btn_change_details'] = False
                st.experimental_rerun()

            st.markdown("##")
            with st.form("Change Details"):
                nickname = st.text_input(
                    label="Nickname"
                )
                username = st.text_input(
                    label="username"
                )
                password = st.text_input(
                    label="Password"
                )
                clicked = st.form_submit_button("Update Details")
                st.info("The one that is filled is the one that will be edited.")

                if clicked:
                    url = "http://localhost:5010/update_user_data"
                    data_json = {}
                    if nickname != "":
                        data_json.update({"nickname": nickname})
                    if username != "":
                        data_json.update({"username": username})
                    if password != "":
                        data_json.update({"password": password})
                    payload = json.dumps(data_json)
                    response = requests.put(url, headers=my_header, data=payload)
                    data_json = response.json()

                    if response.status_code == 200 and data_json["Check"] == 1:
                        st.session_state['btn_change_success'] = True
                    else:
                        st.session_state['btn_change_success'] = False
                        st.session_state['btn_change_msg'] = data_json['Status']
                    
                    st.session_state['btn_change_details'] = False
                    st.experimental_rerun()
            st.markdown("---")
        
        st.markdown("##")
        st.header("Your Reviews")
        st.write('---')
        url = "http://localhost:5010/get_user_review_list_v2"
        account_reviews = requests.get(url, headers=my_header).json()
        has_reviewed = False
        for review in account_reviews:
            nickname = requests.get("http://localhost:5010/get_user_nickname/{}".format(review["user_id"])).json()[0]["nickname"]
            with st.container():
                st.write("**A review by You ({}) for movie \"{}\"**".format(nickname, review["original_title"]))
                st.caption("Written by You ({}) on {}".format(nickname, review["created_at"]))
                st.write("#")
                st.write(review["comment"])
                st.write('---')
            has_reviewed = True
        if not has_reviewed:
            st.info("You never reviewed any movie!")
        