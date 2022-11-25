import streamlit as st
from streamlit_option_menu import option_menu
import requests
import json

user_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY2OTI2OTgyMSwianRpIjoiMTY2Y2RiMjAtNTllNi00NDY1LThmZmItZmNkNzBjYTkwZDk3IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6Im5hYmlsbXV5YXMiLCJuYmYiOjE2NjkyNjk4MjEsImV4cCI6MTY2OTM1NjIyMSwidXNlcl9pZCI6MSwidXNlcl90eXBlIjoiTUVNQkVSIn0.MjgIr3lpZ1jKho-H6CMQ0FybRZ7nspbiWuPRJt_cxv4"

# Header
st.title("Movie Rating API")
choice = option_menu("Navigation", ["Home Page", "Search", "Account"], orientation="horizontal")
st.markdown("##")

if choice == "Home Page":
    my_header = {"Authorization": "JWT {}".format(user_token), 'Content-Type': 'application/json'}
    data = requests.get("http://localhost:5010/get_trend_movie_list/week").json()

    st.header("Trending Right Now")
    st.write("---")
    for i in range(0, 10):
        with st.container():
            col = st.columns(2)
            with col[0]:
                thisdata = data[i]
                st.image("https://www.themoviedb.org/t/p/w220_and_h330_face/{}".format(thisdata["backdrop_path"]))
                st.subheader(thisdata["original_title"])
                st.write("**Movie Rating: :star2: {}**".format(thisdata["vote_average"]))
                st.write("Overview: {}".format(thisdata["overview"]))
                btn1 = st.button("Read More >", key=thisdata["id"])
            if btn1:
                st.markdown("---")
                with st.container():
                    thisdata = data[i]
                    movie_id = thisdata["id"]
                    detail_data = requests.get("http://localhost:5010/get_movie_details/{}".format(movie_id)).json()
                    average_rating = requests.get("http://localhost:5010/get_movie_average_rating/{}".format(movie_id)).json()
                    review_list = requests.get("http://localhost:5010/get_movie_review_list?movie_id_number={}".format(movie_id)).json()

                    st.image("https://www.themoviedb.org/t/p/w220_and_h330_face/{}".format(detail_data["backdrop_path"]))
                    st.subheader(detail_data["original_title"])
                    st.write("**Movie TMDB Rating: :star2: {}**".format(detail_data["vote_average"]))
                    st.write("**Movie Users Rating: :star2: {}**".format(average_rating["Average Rating"]))
                    st.write("Overview: {}".format(detail_data["overview"]))
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
                                st.write(review["comment"])
                            is_reviewed = True
                        if not is_reviewed:
                            st.info("This movie has never been reviewed!")
                    with tabs[1]:
                        if user_token == "":
                            st.error("You must login first!")
                        else:
                            url = "http://localhost:5010/get_user_review_list"
                            account_reviews = requests.get(url, headers=my_header).json()
                            is_reviewed = False
                            for review in account_reviews:
                                if review["movie_id"] == movie_id:
                                    nickname = requests.get("http://localhost:5010/get_user_nickname/{}".format(review["user_id"])).json()[0]["nickname"]
                                    with st.container():
                                        st.write("**A review by {}**".format(nickname))
                                        st.caption("Written by {} on {}".format(nickname, review["created_at"]))
                                        st.write("#")
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
                                            "rating": 1,
                                            "comment": "test"
                                        })
                                        response = requests.post(url, headers=my_header, data=payload).json()
                st.markdown("---")
            with col[1]:
                thisdata = data[i+10]
                st.image("https://www.themoviedb.org/t/p/w220_and_h330_face/{}".format(thisdata["backdrop_path"]))
                st.subheader(thisdata["original_title"])
                st.write("**Movie Rating: :star2: {}**".format(thisdata["vote_average"]))
                st.write("Overview: {}".format(thisdata["overview"]))
                btn2 = st.button("Read More >", key=thisdata["id"])
            if btn2:
                st.markdown("---")
                with st.container():
                    thisdata = data[i+10]
                    movie_id = thisdata["id"]
                    detail_data = requests.get("http://localhost:5010/get_movie_details/{}".format(movie_id)).json()
                    average_rating = requests.get("http://localhost:5010/get_movie_average_rating/{}".format(movie_id)).json()
                    review_list = requests.get("http://localhost:5010/get_movie_review_list?movie_id_number={}".format(movie_id)).json()
                    st.image("https://www.themoviedb.org/t/p/w220_and_h330_face/{}".format(detail_data["backdrop_path"]))
                    st.subheader(detail_data["original_title"])
                    st.write("**Movie TMDB Rating: :star2: {}**".format(detail_data["vote_average"]))
                    st.write("**Movie Users Rating: :star2: {}**".format(average_rating["Average Rating"]))
                    st.write("Overview: {}".format(detail_data["overview"]))
                st.markdown("---")
            st.markdown("##")
    st.write("---")

