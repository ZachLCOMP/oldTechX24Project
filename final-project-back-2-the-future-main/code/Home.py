import streamlit as st
import google.generativeai as genai
from google.cloud import bigquery

st.session_state.status = st.session_state.get('status', 'unverified')

#Setting up bigquery to fetch user credentials
client = bigquery.Client("sds-project-414416")

#Function to get a returning user's credential
def fetch_user(username, password):

    if not (username and password): 
        st.warning('Please Input a Valid Username & Password')

    QUERY = "SELECT username, password FROM `sds-project-414416.back_to_the_future.user_info` WHERE username = \"%s\" AND password = \"%s\"" % (username, password)
    query_job = client.query(QUERY)
    row = query_job.result()

    if row.total_rows == 0: 
        st.warning("Invalid Username and/or Password. Please try again")
        st.session_state.status = 'incorrect_login'
    else:
        st.success("You have successfully logged in")
        st.session_state.status = 'verified'
        st.session_state.username = st.session_state.get('username', username)


#Function to insert a new user's credentials into database
def create_user(username, password): 
    if not (username and password): 
        st.warning('Please Input a Valid Username & Password')

    QUERY = "SELECT * FROM `sds-project-414416.back_to_the_future.user_info` WHERE username = \"%s\"" % (username.strip())
    query_job = client.query(QUERY)
    row = query_job.result()

    if row.total_rows == 0: 
        myquery =  "INSERT INTO `sds-project-414416.back_to_the_future.user_info` (username, password) VALUES (\"%s\", \"%s\")" % (username, password)
        QUERY = (myquery)
        insert_job = client.query(QUERY)
        row = insert_job.result()
        st.success("You have successfully created a new account!")
        st.session_state.status = 'verified'
        st.session_state.username = st.session_state.get('username', username)
    else: 
        st.warning("Username is not available, please try again")
        st.session_state.status = 'incorrect_login'
       

st.set_page_config(page_title="Home Page")

st.title('Welcome to your Digital Bucket List!')
st.write("From career to travel to hobbies, our team wants to use help you achieve your goals. This website uses  GenAI to expand on ideas, provide feedback, and help you start planning for their future. Each web page would be focused on helping users develop their ideas in a different sector of life. The pages will be split up: a travel planner, a career planner, and a hobby tracker.")

st.write('Before you start though, please login')


tab1, tab2 = st.tabs(["Returning User", "New User"])

with tab1: 
    return_username = st.text_input("Username", key='return_user_name')
    return_password = st.text_input("Password", key='return_passwrod')
    submitBtnOld = st.button('Submit', key='return_button')
    if submitBtnOld: 
        fetch_user(return_username, return_password)
with tab2: 
    new_username = st.text_input("Username", key='new_user_name')
    new_password = st.text_input("Password", key='new_password')
    submitBtnNew = st.button('Create Account', key='new_button')
    if submitBtnNew: 
        create_user(new_username, new_password)
