import streamlit as st

# Title of the app
st.title("AI Thesis Assistant")

# Input for thesis topic
thesis_topic = st.text_input("Enter your thesis topic:")

# Input for keywords
keywords = st.text_input("Enter keywords related to your thesis:")

# Button to generate suggestion
if st.button("Get Suggestions"):
    # Placeholder for AI-based suggestions
    suggestions = ["Suggestion 1", "Suggestion 2", "Suggestion 3"]
    st.write("Here are some suggestions for your topic and keywords:")
    for suggestion in suggestions:
        st.write(suggestion)