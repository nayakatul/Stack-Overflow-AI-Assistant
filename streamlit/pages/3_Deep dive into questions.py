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

        st.markdown("<h1 class='center'>Deep dive into questions</h1>", unsafe_allow_html=True)

        # Check if the result is stored in session state
        if "filtered_similar_topics" in st.session_state and "filtered_similarity_scores" in st.session_state:
            # Get the result from session state
            filtered_similar_topics = st.session_state.filtered_similar_topics
            filtered_similarity_scores = st.session_state.filtered_similarity_scores
            
            # Get the df2 DataFrame from session state
            df2 = st.session_state.df2

            # Check if any similar topics were found
            if len(filtered_similar_topics) > 0:
                # Display the result
                options = [f"{i+1}. {filtered_similar_topics[i]['question_title']} (similarity score: {filtered_similarity_scores[i]:.2f})" for i in range(len(filtered_similar_topics))]
                st.markdown("<h3> Select a question :</h3>", unsafe_allow_html=True)
                selected_option = st.selectbox("",options)

                # Get the index of the selected topic
                selected_index = options.index(selected_option)
            
                # Get the details of the selected topic
                selected_topic = filtered_similar_topics[selected_index]
                question_id, question_title, question_body, accepted_answer = selected_topic['question_id'], selected_topic['question_title'], selected_topic['question_body'], selected_topic['accepted_answer']
                
                if (accepted_answer)=="N/A":
                    st.markdown("<h3 style='color:red'>No accepted answer</h3>", unsafe_allow_html=True)
                else:
                    # Render the HTML content of the accepted answer
                    st.markdown(f"<h3 style='color:green'>Accepted answer:</h3> {accepted_answer}", unsafe_allow_html=True)

                    accepted_answer_creation_date = selected_topic['accepted_answer_creation_date']
                    accepted_answer_view_count = selected_topic['accepted_answer_view_count']
                    accepted_answer_score = selected_topic['accepted_answer_score']
                    owner_reputation = selected_topic['owner_reputation']
                    owner_badge = selected_topic['owner_badge']

                    # Set the color of the accepted answer view count based on its value
                    if accepted_answer_view_count > 1000:
                        view_count_color = "green"
                    elif accepted_answer_view_count >= 500:
                        view_count_color = "orange"
                    else:
                        view_count_color = "red"

                    # Set the color of the accepted answer score based on its value
                    if accepted_answer_score > 5:
                        score_color = "green"
                    elif accepted_answer_score >= 1:
                        score_color = "orange"
                    else:
                        score_color = "red"

                    # Set the color of the owner reputation based on its value
                    if owner_reputation > 1000:
                        reputation_color = "green"
                    elif owner_reputation >= 500:
                        reputation_color = "orange"
                    else:
                        reputation_color = "red"

                    # Create an HTML table to display the details of the accepted answer
                    table_html = f"""
                        <table>
                            <tr>
                                <th>Accepted answer creation date</th>
                                <td>{accepted_answer_creation_date}</td>
                            </tr>
                            <tr>
                                <th>Accepted answer view count</th>
                                <td style="color: {view_count_color};">{accepted_answer_view_count}</td>
                            </tr>
                            <tr>
                                <th>Accepted answer score</th>
                                <td style="color: {score_color};">{accepted_answer_score}</td>
                            </tr>
                            <tr>
                                <th>Owner reputation</th>
                                <td style="color: {reputation_color};">{owner_reputation}</td>
                            </tr>
                            <tr>
                                <th>Owner badge</th>
                                <td>{owner_badge}</td>
                            </tr>
                        </table>
                    """
                    st.write(table_html, unsafe_allow_html=True)

                post_comments = df2[df2['post_id'] == question_id]

                st.markdown(f"<h3>Question body:{question_body}</h3>", unsafe_allow_html=True)

                comments_text = ""
                if not post_comments.empty:
                    st.markdown("<h3>Comments:</h3>", unsafe_allow_html=True)
                    for index, row in post_comments.iterrows():
                        st.write(f"\t- {row['text']}")
                        comments_text += f"\n- {row['text']}"
                        comment_creation_date = row['creation_date']
                        comment_score = row['score']

                        # Set the color of the comment score based on its value
                        if comment_score > 5:
                            score_color = "green"
                        elif comment_score >= 1:
                            score_color = "orange"
                        else:
                            score_color = "red"

                        # Create an HTML table to display the details of the comment
                        table_html = f"""
                            <table>
                                <tr>
                                    <th>Comment creation date</th>
                                    <td>{comment_creation_date}</td>
                                </tr>
                                <tr>
                                    <th>Comment score</th>
                                    <td style="color: {score_color};">{comment_score}</td>
                                </tr>
                                
                            </table>
                        """
                        st.write(table_html, unsafe_allow_html=True)


                
                #store accepted answer, comments, question_body, question_title in session state
                st.session_state.accepted_answer = accepted_answer
                st.session_state.comments_text = comments_text
                st.session_state.question_body = question_body
                st.session_state.question_title = question_title

                if (st.session_state.accepted_answer)=="N/A":
                    # Add a "Generate StackAI Answer" button
                    st.markdown("<h2 style='color:blue'>No accepted answer? Do not worry!</h2>", unsafe_allow_html=True)
                    fastapi_url = "http://fastapi:8095/generate_answer"

                    # Create the data JSON payload
                    data = {
                        "question_title": str(st.session_state.question_title),
                        "question_body": str(st.session_state.question_body),
                        "temperature": 0.2  # Set the desired temperature here
                    }

                    if st.button("Let StackAI generate an answer"):
                        with st.spinner("Generating an answer..."):
                            # Make a POST request to the FastAPI endpoint
                            try:
                                response = requests.post(fastapi_url, json=data)
                                response.raise_for_status()  # Raise an exception for non-200 status codes
                                if response.status_code == 200:
                                    answer = response.json()["answer"]
                                    st.markdown(f"{answer}", unsafe_allow_html=True)
                                else:
                                    st.error("Failed to generate the answer. Please try again.")
                            except requests.exceptions.RequestException as e:
                                st.error(f"An error occurred while making the request: {e}")

                else:
                    FASTAPI_URL = "http://fastapi:8095/summarize"

                    # Get the index of the selected topic
                    selected_index = options.index(selected_option)
                    # Get the details of the selected topic
                    selected_topic = filtered_similar_topics[selected_index]
                    question_id, question_title, question_body, accepted_answer = selected_topic['question_id'], selected_topic['question_title'], selected_topic['question_body'], selected_topic['accepted_answer']

                    # Get the details of the selected topic
                    data = f"{accepted_answer}"

                    # Create a request body with the user input parameters
                    request_body = {
                        "data": data,
                    }
                    # Add a "Summarize the Accepted Answer" button
                    st.markdown("<h2 style='color:blue'>Too long to read?</h2>", unsafe_allow_html=True)

                    if st.button("Let StackAI summarize the accepted answer"):
                        with st.spinner("Summarizing..."):
                            response = requests.post(FASTAPI_URL, json=request_body)

                        # Check the response status code
                        if response.status_code == 200:
                            # Get the response body as a JSON object
                            response_body = response.json()
                            # Get the summary from the response body
                            summary = response_body["summary"]
                            # Display the summary
                            st.markdown(f"<h3>Summary of the accepted answer:</h3>", unsafe_allow_html=True)
                            st.markdown(f"{summary}", unsafe_allow_html=True)
                        else:
                            # Display an error message if something went wrong
                            st.error(f"Something went wrong. Status code: {response.status_code}")

            else:
                # Display a message if no similar topics were found
                st.warning("No related topics found in StackOverflow. Please try again with a different question.")    

        else:
            # Display a message if no similar topics were found
            st.warning("Please ask a question first!")
    else:
        # Session has timed out, log out user and display login page
        del st.session_state.logged_in
        del st.session_state.last_activity
        
        # Display message asking user to log in
        st.warning("Please Sign In first")
        
else:
    # User is not logged in, display message asking user to log in and display login page
    st.warning("Please Sign In first")
