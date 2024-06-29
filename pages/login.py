import streamlit as st
from src.mongo import *
from src.session import *
from src.google_analytics import *

st.session_state.page = 'Login'
st.subheader("Login Section")
inject_google_analytics()
# inject_ga() # antoher method to check GA working or not
    

username = st.text_input("Username", key='username')
password = st.text_input("Password", type='password')


if st.button("Login"):
    user = login_user(username, password)
    if user:
        st.session_state['first_name'] = user['name'].split()[0]
        st.success("Logged In as {}".format(username))
        # st.experimental_set_query_params(page="pages/chat")
        session_id = create_user_session(username, datetime.now())
        st.session_state['session_id'] = session_id

        if 'session_id' in st.session_state:
            session_id = st.session_state['session_id']
            st.switch_page('pages/Chat.py')
        
    else:
        st.warning("Incorrect Username/Password")
        