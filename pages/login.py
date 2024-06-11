import streamlit as st
from src.mongo import *

st.session_state.page = 'Login'
st.subheader("Login Section")

username = st.text_input("Username", key='username')
password = st.text_input("Password", type='password')


if st.button("Login"):
    user = login_user(username, password)
    if user:
        st.session_state['first_name'] = user['name'].split()[0]
        st.success("Logged In as {}".format(username))
        st.experimental_set_query_params(page="pages/chat")
        st.switch_page('pages/chat.py')
        
    else:
        st.warning("Incorrect Username/Password")
        