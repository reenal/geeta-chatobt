import streamlit as st
from src.mongo import *
from src.session import *
st.session_state.page = 'Register'
if 'session_id' in st.session_state:
        session_id = st.session_state['session_id']



st.subheader("Create New Account")

name = st.text_input('name')
age = st.number_input('age', min_value=0, max_value=100, step=1)
gender = st.selectbox('gender', ('Male', 'Female'))
email = st.text_input("email")
new_password = st.text_input("Password", type='password')

if st.button("Register"):
    
    registration_status = register_user(email, new_password, name, age, gender)
    if registration_status=='User registered successfully':
        st.session_state['name'] = name.split()[0]
        
        st.success("You have successfully created an account")
        st.experimental_set_query_params(page="pages/login.py")
        st.switch_page('pages\login.py')
    else:
        st.warning(registration_status)