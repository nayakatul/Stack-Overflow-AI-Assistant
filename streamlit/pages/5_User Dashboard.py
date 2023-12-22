import streamlit as st

from datetime import timedelta
from datetime import datetime
import pandas as pd
import webbrowser

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
        
        # Display welcome message with user's first name and last name
        st.title(f"{st.session_state.first_name} {st.session_state.last_name}'s Dashboard")

        # search history
        st.markdown("<h1 style='text-align: center; color:red'>Search History</h1>", unsafe_allow_html=True)

        # Retrieve the stored search history from session state
        search_history = getattr(st.session_state, "search_history", [])

        if not search_history:
            st.markdown("<h4>No history available</h4>", unsafe_allow_html=True)
        else:
            # Create a data frame from the search history
            df = pd.DataFrame(search_history)

            # Rename the columns
            df.columns = ["Question", "Most Similar Topic"]

            # Function to render the "Most Similar Topic" column as clickable links
            def render_link(row):
                return f'<a href="{row}" target="_blank">{row}</a>'

            # Apply the function to the "Most Similar Topic" column
            df["Most Similar Topic"] = df["Most Similar Topic"].apply(render_link)

            # Display the modified table with clickable links
            st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

    else:
        # Session has timed out, log out user and display login page
        del st.session_state.logged_in
        del st.session_state.last_activity
        
        # Display message asking user to log in
        st.warning("Please Sign In first")
        
else:
    # User is not logged in, display message asking user to log in and display login page
    st.warning("Please Sign In first")
