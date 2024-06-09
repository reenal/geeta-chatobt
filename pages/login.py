import streamlit as st
from src.mongo import *

st.session_state.page = 'Login'
st.subheader("Login Section")

username = st.text_input("Username")
password = st.text_input("Password", type='password')

if st.button("Login"):
    if login_user(username, password):
        st.success("Logged In as {}".format(username))
        st.switch_page('pages/chat.py')
        
    else:
        st.warning("Incorrect Username/Password")
        