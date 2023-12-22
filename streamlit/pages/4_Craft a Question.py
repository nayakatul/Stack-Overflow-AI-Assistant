import streamlit as st

from datetime import timedelta
from datetime import datetime
import requests
import pandas as pd

# Check if user is logged in and session is still valid
if "logged_in" in st.session_state and "last_activity" in st.session_state:
    time_since_last_activity = datetime.now() - st.session_state.last_activity
    if time_since_last_activity < timedelta(minutes=15):
        # Session is still valid, update last activity time
        st.session_state.last_activity = datetime.now()

        # Display logout button
        if st.sidebar.button("Logout"):
            del st.session_state.logged_in
            del st.session_state.last_activity
            #rerun the page
            st.experimental_rerun()

        st.markdown("""
        <style>
            .center {
                display: block;
                margin-left: auto;
                margin-right: auto;
                text-align: center;
            }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("<h1 class='center'>Still didn't get a solution to your problem?</h21>", unsafe_allow_html=True)
        st.markdown("<h3>StackAI will craft a question for you to post on StackOverflow with all the required fields, so it can be answered by a human</h3>", unsafe_allow_html=True)

        #if user question and user tag is in session state, proceed to display the question
        if "user_question" in st.session_state and "user_tag" in st.session_state:
            st.markdown("<h2 class='center';>Your question :</h2>", unsafe_allow_html=True)
            st.markdown(f"<h2 class='center'; style=color:red;>{st.session_state.user_question}</h2>", unsafe_allow_html=True)
            with st.spinner("Crafting..."):
                # Add a result button
                if st.button("Let StackAI craft a question for you"):
                    # Make a POST request to the FastAPI endpoint for user's question
                    fastapi_url = "http://fastapi:8095/generate_stackoverflow_question"
                    try:
                        user_question_data = {
                            "question_title": st.session_state.user_question,
                            "question_body": st.session_state.user_tag,
                            "temperature": 0.2  # Set the desired temperature here
                        }
                        response = requests.post(fastapi_url, json=user_question_data)
                        response.raise_for_status()  # Raise an exception for non-200 status codes
                        if response.status_code == 200:
                            if "answer" not in st.session_state:
                                st.session_state.answer = []
                            answer = response.json()["answer"]
                            st.markdown(f"{answer}", unsafe_allow_html=True)

                        else:
                            st.error("Failed to gcraft a question. Please try again.")
                    except requests.exceptions.RequestException as e:
                        st.error(f"An error occurred while making the request: {e}")

        else:
            st.markdown("<h2 class='center'; style=color:red;>Go back and enter your question first</h2>", unsafe_allow_html=True)

    
    else:
        # Session has timed out, log out user and display login page
        del st.session_state.logged_in
        del st.session_state.last_activity
        
        # Display message asking user to log in
        st.warning("Please Sign In first")
            
else:
    # User is not logged in, display message asking user to log in and display login page
    st.warning("Please Sign In first")                
