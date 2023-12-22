import streamlit as st

st.set_page_config(page_title="Stack AI", page_icon="🤖👨‍💻")

st.markdown("""
<style>
    .center {
        display: block;
        margin-left: auto;
        margin-right: auto;
        text-align: center;
    }
    .green {
        color: green;
    }
</style>
""", unsafe_allow_html=True)

# Define custom CSS style
custom_style = """
    <style>
        .center {
            text-align: center;
        }
        .green {
            color: green;
        }
        .feature-box {
            background-color: #f7f7f7;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
        }
    </style>
"""

# Apply the custom style
st.markdown(custom_style, unsafe_allow_html=True)

# Display the content with custom styling
st.markdown("<h1 class='center'>Introducing StackAI 🤖👨‍💻<h1>", unsafe_allow_html=True)

with st.container():
    st.markdown("## Your Ultimate Coding Companion!", unsafe_allow_html=True)
    st.markdown("Wave goodbye to the challenge of hunting down solutions on Stack Overflow. StackAI revolutionizes your coding experience by instantly fetching related answers written by humans, simplifying intricate topics, generating personalized answers tailored to your unique questions and even crafting questions for you to post on Stack Overflow")
    st.markdown("### #UnlockTheCodeGenius", unsafe_allow_html=True)
