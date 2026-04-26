import streamlit as st
from similarity import find_similar_websites

st.set_page_config(
    page_title="Website Suggester",
    layout="centered"
)

st.title("Website Suggester 🔍")
st.write("Enter a website URL to discover similar websites.")

# User URL input
user_url = st.text_input(
    "Enter website URL (e.g., example.com)"
)

# Optional category selection
user_category = st.selectbox(
    "Select category (optional, leave blank to auto-detect)",
    [
        ""
    ] + [
        "Adult",
        "Business/Corporate",
        "Computers and Technology",
        "E-Commerce",
        "Education",
        "Food",
        "Forums",
        "Games",
        "Health and Fitness",
        "Law and Government",
        "News",
        "Photography",
        "Social Networking and Messaging",
        "Sports",
        "Streaming Services",
        "Travel"
    ]
)

# Convert blank to None
user_category = None if user_category == "" else user_category


if st.button("Find Similar Websites"):

    if not user_url.strip():
        st.warning("Please enter a website URL")

    else:
        with st.spinner("Validating and searching..."):
            results = find_similar_websites(
                user_url,
                user_category=user_category
            )

        # If function returned an error message
        if isinstance(results, str):
            st.error(results)

        # If recommendations returned
        else:
            st.success("Top similar websites:")
            st.table(results)