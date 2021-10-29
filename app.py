import twint
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import neattext.functions as nfx
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()
# Useful functions
def get_tweets(search):
    c = twint.Config()
    c.Search = search
    c.Limit = 30
    c.Pandas = True
    c.Lang = 'en'
    c.Hide_output = True
    # c.Count = True
    # Run
    twint.run.Search(c)
    df = twint.output.panda.Tweets_df
    return df

def score_tosentiment(score):
    if score >= 0.05:
        output = "positive"
    elif score <= -0.05:
        output = "negative"
    else:
        output = "neutral"
    return output

def preprocess(s):
    s = nfx.remove_urls(s)
    s = nfx.remove_emojis(s)
    s = nfx.remove_emails(s)
    s = nfx.remove_hashtags(s)
    s = nfx.remove_userhandles(s)
    s = nfx.remove_special_characters(s)
    s = nfx.remove_multiple_spaces(s)
    return s

def get_sentiment(df, N):
    data_list = []
                
    for n in range(N):
        s = df.iloc[n,1]
        data = {}
        s = preprocess(s)
        data['tweet'] = s
        score = analyzer.polarity_scores(s)['compound']
        label = score_tosentiment(score)
        data['compound'] = score
        data['label'] = label
        data_list.append(data)

    tweet_df = pd.DataFrame(data_list)
    return tweet_df

def get_label(s):
    score = analyzer.polarity_scores(s)['compound']
    label = score_tosentiment(score)
    return label

def main():
    st.title("Sentiment Analysis Apps")
    menu = ["Home", "User Input", "Scrape Twitter", "Squid Game"]

    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.header("Home")

        vader = "[VADER](https://github.com/cjhutto/vaderSentiment)"
        github = "[GitHub](https://github.com/mdifils/challenge-sentiment-analysis)"
        string = f"""
        Welcome to **S**entiment **A**nalysis **A**pps. This apps uses a pre-trained **NLP** model ({vader}) to analyze text and extract the overal sentiment based on some key words.
        - Select **User Input** to enter your own sentence to be analyzed.
        - Select **Scrape Twitter** and provide an hastag (e.g. : *#blackpanther*). 10 tweets will be scraped (in real time) from Twitter and each of them will be analyzed.
        - Select **Squid Game** to analyze a database of more than 10000 tweets.


        For more details, please visit my {github}.
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
                st.success("Overall sentiment")
                vs = analyzer.polarity_scores(text)
                score = vs['compound']
                label = score_tosentiment(score)
                st.write(f"""
                Your sentence is: {text}

                Below is the sentiment analysis.
                """)
                # Emoji
                if label == "positive":
                    st.markdown("Positive: :smiley:")
                elif label == "negative":
                    st.markdown("Negative: :angry:")
                else:
                    st.markdown("Neutral: :neutral_face:")
                st.dataframe(pd.DataFrame([vs]))
                st.write("""
                    - The `compound` score is the most useful metric if you want a measure of sentiment for a given sentence. It has a value between -1 (most extreme negative) and +1 (most extreme positive).
                    - The `pos`, `neg` and `neu` are the most useful metrics if you want to analyze the context of a given sentence.
                """)
            with col2:
                st.success("Sentiment by token")
                
                token_score_list = []
                for s in text.split(): 
                    score = analyzer.polarity_scores(s)['compound']
                    label = score_tosentiment(score)
                    token_score_list.append(
                        {
                            "token": s,
                            "compound": score,
                            "sentiment": label
                        }
                    )
                tokens_score_df = pd.DataFrame(token_score_list)
                st.dataframe(tokens_score_df)
    
    elif choice == "Scrape Twitter":
        st.header("Scrape Twitter")

        with st.form(key="tweetForm", clear_on_submit=True):
            hashtag = st.text_input("Please Enter your hashtag to be analyzed.")
            submit = st.form_submit_button(label="Scrape", )
        if submit:
            df = get_tweets(hashtag)
            try:
                df = df[df.language == 'en'][['username','tweet']]
                if len(df) < 10:
                    N = len(df)
                    st.info(f"Only {N} tweets found for this hashtag: {hashtag}")
                else:
                    N = 10
                    st.success(f"Below are the 10 tweets found for this hashtag: {hashtag}")
                
                tweet_df = get_sentiment(df, N)
                values = tweet_df.label.value_counts()
                labels = values.keys()
                fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
                fig.update_layout(title_text='Sentiment Analysis', title_x=0.5)
                st.table(tweet_df)
                st.plotly_chart(fig)
            except:
                st.warning(f"Sorry, no tweets found for this hashtag: {hashtag}")
        
    else:
        st.header("Squid Game")
        df = pd.read_csv("data/squidgame.csv")
        df = df[df['language'] == 'en'][['date','username','tweet','likes_count']]
        df['tweet'] = df['tweet'].apply(preprocess)
        df['label'] = df['tweet'].apply(get_label)
        df1 = df.sort_values(by=['likes_count'], ascending=False)[:10]
        st.info("The 10 most liked tweets")
        st.table(df1)
        s_label = df.label.value_counts()
        fig = go.Figure(data=[go.Pie(labels=s_label.index, values=s_label.values)])
        fig.update_layout(title_text='Sentiment Analysis', title_x=0.5)
        st.plotly_chart(fig)
        s = df['date'].value_counts()
        x = ['/'.join(a.split('-')[::-1]) for a in s.index]
        y = s.values
        fig = go.Figure(data=[
            go.Bar(x=x, 
                   y=y,
                   text=y,
                   textposition='auto',
                   marker=dict(color=y,
                                colorscale='viridis') #viridis,plotly3,sunset,cividis,peach
            )
        ])
        fig.update_layout(
            title_text='Time series', 
            title_x=0.5,
            xaxis_title = 'date',
            yaxis_title = 'Number of Tweets'
        )
        st.plotly_chart(fig)

if __name__ == '__main__':
    main()