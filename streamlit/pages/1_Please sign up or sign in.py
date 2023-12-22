import streamlit as st
import requests
from datetime import timedelta
from datetime import datetime

# Replace this with the URL of your FastAPI backend
FASTAPI_URL = "http://fastapi:8095"

# Set session timeout to 15 minutes
SESSION_TIMEOUT = timedelta(minutes=15)

def signup():
    st.title("First time user? Sign Up here")
    first_name = st.text_input("First Name", key="signup_first_name")
    last_name = st.text_input("Last Name", key="signup_last_name")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    if st.button("Sign Up"):
        response = requests.post(f"{FASTAPI_URL}/signup", json={"first_name": first_name, "last_name": last_name, "email": email, "password": password})
        if response.status_code == 200:
            st.success(f"Signed up as {response.json()['first_name']} {response.json()['last_name']}")
        elif response.status_code == 422:
            st.error("Please enter all the fields correctly")
        else:
            st.error(response.json()["detail"])

def login():
    st.title("Already registered? Sign In here")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Sign In"):
        response = requests.post(f"{FASTAPI_URL}/login", data={"username": email, "password": password})
        if response.status_code == 200:
            st.success(f"Welcome : {response.json()['first_name']} {response.json()['last_name']}")
        # Set session state to logged in
            st.session_state.logged_in = True
            st.session_state.last_activity = datetime.now()
        # Store user's first name and last name in session state
            st.session_state.first_name = response.json()['first_name']
            st.session_state.last_name = response.json()['last_name']
        #store email in session state
            st.session_state.email = email
        else:
            try:
                error_detail = response.json()["detail"]
                st.error("invalid credentials")
            except:
                st.error("An error occurred. Please try again.")


def main():
    # Check if user is logged in and session is still valid
    if "logged_in" in st.session_state and "last_activity" in st.session_state:
        time_since_last_activity = datetime.now() - st.session_state.last_activity
        if time_since_last_activity < SESSION_TIMEOUT:
            # Session is still valid, update last activity time
            st.session_state.last_activity = datetime.now()
            # Display welcome message with user's first name and last name
            st.success(f"Welcome : {st.session_state.first_name} {st.session_state.last_name}")

             # Display logout button
            if st.sidebar.button("Logout"):
                del st.session_state.logged_in
                del st.session_state.last_activity
                #rerun the page
                st.experimental_rerun()
        else:
            # Session has timed out, log out user
            del st.session_state.logged_in
            del st.session_state.last_activity

    else:
        # User is not logged in, show login page
        st.sidebar.title("Select an option")
        selected_page = st.sidebar.radio("", ["Sign Up", "Sign In"])

        if selected_page == "Sign Up":
            signup()
        elif selected_page == "Sign In":
            login()

if __name__ == "__main__":
    main()

