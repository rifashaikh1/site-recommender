import streamlit as st
from similarity import find_similar_websites


st.set_page_config(
    page_title="Website Suggester",
    layout="centered"
)

st.title("Website Suggester 🔍")


# -------------------
# Input URL
# -------------------
user_url = st.text_input(
    "Enter website URL"
)


# -------------------
# Optional category
# -------------------
user_category = st.selectbox(
    "Select category (optional)",
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

user_category = (
    None if user_category == ""
    else user_category
)


# -------------------
# Search button
# -------------------
if st.button("Find Similar Websites"):

    if not user_url:
        st.warning("Enter website URL")

    else:

        with st.spinner("Searching..."):
            results = find_similar_websites(
                user_url,
                user_category=user_category
            )

        # Handle invalid/parked/gibberish cases
        if "Message" in results.columns:
            st.warning(
                results["Message"].iloc[0]
            )

        # Normal recommendations
        else:
            st.success(
                "Top similar websites:"
            )
            st.table(
                results.reset_index(
                    drop=True
                )
            )