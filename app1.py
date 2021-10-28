import streamlit as st
from textblob import TextBlob

def main():
    st.title("Sentiment Analysis Apps")
    menu = ["Home", "User Input", "Scrape Twitter", "Squid Game", "Titans"]

    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.header("Home")

        string = """
        Welcome to **S**entiment **A**nalysis **A**pps. This apps uses a pre-trained **NLP** model to analyze text and extract the overal sentiment based on some key words.
        - Select **User Input** to enter your own sentence to be analyzed.
        - Select **Scrape Twitter** and provide an hastag (e.g. : *#blackpanther*). 10 tweets will be scraped (in real time) from Twitter and each of them will be analyzed.
        - Select **Squid Game** or **Titans** to analyze a database of more than 10000 tweets.
        """

        st.write(string)

    elif choice == "User Input":
        st.header("User Input")

        with st.form(key="myForm", clear_on_submit=True):
            text = st.text_input("Please Enter the text to be analyzed.")
            submit = st.form_submit_button(label="Analyze", )

        col1, col2 = st.columns(2)
        if submit:
            with col1:
                st.success("Result")
                sentiment = TextBlob(text).sentiment
                st.write(sentiment)
                # Emoji
                if sentiment.polarity > 0:
                    st.markdown("Positive: :smiley:")
                elif sentiment.polarity < 0:
                    st.markdown("Negative: :angry:")
                else:
                    st.markdown("Neutral: :neutral_face:")
            with col2:
                st.success("Token")
    
    elif choice == "Scrape Twitter":
        st.header("Scrape Twitter")
    elif choice == "Squid Game":
        st.header("Squid Game")
    else:
        st.header("Titans")

if __name__ == '__main__':
    main()