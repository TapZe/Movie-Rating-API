import streamlit as st
from streamlit_option_menu import option_menu
import requests

# Header
st.title("Movie Rating API")
choice = option_menu("Navigation", ["Home Page", "Search", "Account"], orientation="horizontal")
st.markdown("##")

if choice == "Home Page":
    data = requests.get("http://localhost:5010/get_trend_movie_list/week").json()
    btnlist = []

    st.header("Trending Right Now")
    st.write("---")
    for i in range(0, 10):
        with st.container():
            col = st.columns(2)
            with col[0]:
                thisdata = data[i]
                st.image("https://www.themoviedb.org/t/p/w220_and_h330_face/{}".format(thisdata["backdrop_path"]))
                st.subheader(thisdata["original_title"])
                st.write("Movie Rating: {}".format(thisdata["vote_average"]))
                st.write("Overview: {}".format(thisdata["overview"]))
                btnlist.append(st.button("Read More >", key=thisdata["id"]))
            with col[1]:
                thisdata = data[i+10]
                st.image("https://www.themoviedb.org/t/p/w220_and_h330_face/{}".format(thisdata["backdrop_path"]))
                st.subheader(thisdata["original_title"])
                st.write("Movie Rating: {}".format(thisdata["vote_average"]))
                st.write("Overview: {}".format(thisdata["overview"]))
                btnlist.append(st.button("Read More >", key=thisdata["id"]))
            st.markdown("##")
    st.write("---")
    
    for i in range (0,20):
        if btnlist[i]:
            st.markdown("##")
            with st.container():
                thisdata = data[i]
                movie_id = thisdata["id"]
                detail_data = requests.get("http://localhost:5010/get_movie_details/{}".format(movie_id)).json()
                average_rating = requests.get("http://localhost:5010/get_movie_average_rating/{}".format(movie_id)).json()
                review_list = requests.get("http://localhost:5010/get_movie_review_list?movie_id_number={}".format(movie_id)).json()
                st.image("https://www.themoviedb.org/t/p/w220_and_h330_face/{}".format(detail_data["backdrop_path"]))
                st.subheader(detail_data["original_title"])
                st.write("Movie TMDB Rating: {}".format(detail_data["vote_average"]))
                st.write("Movie Users Rating: {}".format(average_rating["Average Rating"]))
                st.write("Overview: {}".format(detail_data["overview"]))

    