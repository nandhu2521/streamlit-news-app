import streamlit as st
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from urllib.request import urlopen, HTTPError, URLError
from newspaper import Article
from bs4 import BeautifulSoup as soup

# nltk punkt, vader_lexicon for nlp, sentiment analysis
try:
    nltk.data.find("punkt")
    nltk.data.find("vader_lexicon")
except Exception as e:
    print(e)
    nltk.download("punkt")
    nltk.download("vader_lexicon")

# Page config
st.set_page_config(page_title="streamlit News App", page_icon=":newspaper:", layout="wide")

# Custom styling
custom_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
}
</style>
"""
st.markdown(custom_style, unsafe_allow_html=True)

# Fetch news
def fetch_news(flag=1, topic=""):
    if flag == 2:
        src_url = f"https://news.google.com/rss/rss/headlines/section/topic/{topic.upper()}"  # fetch using category
    elif flag == 3:
        src_url = f"https://news.google.com/rss/search?q={topic.upper()}"  # fetch using a search term
    else:
        src_url = "https://news.google.com/rss"  # top news, default
    try:
        response = urlopen(src_url)
        html = response.read()
        response.close()
        soup_page = soup(html, "xml")
        news_list = soup_page.find_all("item")
        return news_list
    except (URLError, HTTPError) as e:
        st.error(f"Error fetching news, {e}")
        return []


# Load news
def load_news(news_list, news_no=5):
    forecast = {'pos':0,'neg':0,'comp':0,}
    for index, news in enumerate(news_list[:news_no]):
        news_data = Article(news.link.text)
        try:
            news_data.download()
            news_data.parse()
            news_data.nlp()
            sia = SentimentIntensityAnalyzer()
            ps = sia.polarity_scores(news_data.text)
        except Exception as e:
            st.error(f"Error parsing news content, {e}")
        st.header(f'''{index+1}. {news.title.text}''')
        st.image(f'''{news_data.top_image}''')
        st.caption(f'''{news.title.text}''')
        st.subheader(f'''{news_data.summary}''')
        st.markdown(
            f"""
        [Read more at {news.source.text}]({news.link.text})
        """
        )
        forecast['pos'] += float(ps['pos'])
        forecast['neg'] += float(ps['neg'])
        forecast['comp'] += float(ps['compound'])
        st.write(f"{news.pubDate.text}")
        st.markdown(
            f""" 
        <span style="color:green; padding-right: 10px">{ps['pos']}% Positive</span> 
        <span style="color:blue; padding-right: 10px;">{ps['neu']}% Neutral</span>
        <span style="color:red; padding-right: 10px;">{ps['neg']}% Negative</span>
        <span style="padding-right: 10px;"> Overall Sentiment is {
            '<span style="color:green; padding-right: 10px">Positive</span>' if ps['compound'] > 0 else
            '<span style="color:red; padding-right: 10px">Negative</span>' 
            }
        </span>
        """,
            unsafe_allow_html=True,
        )
    st.sidebar.markdown(
            f""" 
        <h3 style="color: black; margin-bottom: -12px, margin-top: -6px">Overall news analysis for today</h3>
        <p style="color:green; margin-bottom: -2px">{round(forecast['pos'], 2)}% Positive</p> 
        <p style="color:blue; margin-bottom: -2px">{round(forecast['neg'], 2)}% Neutral</p>
        <p style="color:red; margin-bottom: -2px">{round(forecast['comp'], 2)}% Negative</p>
        <p style="margin-bottom: -2px;"> Overall Sentiment today is {
            '<span style="color:green; margin-bottom: -2px"> Positive</span>' if round(ps['compound'], 2) > 0 else
            '<span style="color:red; margin-bottom: -2px"> Negative</span>' 
            }
        </p>
        """,
            unsafe_allow_html=True,
    )

# Driver
def run():
    st.title("streamlit News App :newspaper:")
    st.sidebar.title("streamlit News App :newspaper:")
    st.sidebar.write("A streamlit app that scrapes Google News RSS feed for news, summarizes it and displays as per choice - by top trending, a specific category or just type in a search term. Also has a bit of NLP magic working behind the scenes - to summarize long articles into a crisp little news byte.")
    category = [
    "Select an option",
    "Top trending news 🔥",
    "Browse categories 🗞️",
    "Search a topic 🔍",
    ]
    category_selected = st.sidebar.selectbox("Select an option", category)

    if category_selected == category[0]:
        st.sidebar.warning("Please select an option from the dropdown")

    elif category_selected == category[1]:
        st.sidebar.subheader("Here's what's trending")
        news_no = st.sidebar.slider(
            "Number of news items to show", min_value=10, max_value=1000, step=10
        )
        news_list = fetch_news()
        load_news(news_list, news_no)

    elif category_selected == category[2]:
        topics = [
            "Choose a topic",
            "World",
            "Nation",
            "Business",
            "Technology",
            "Entertainment",
            "Sports",
            "Science",
            "Health",
        ]
        st.sidebar.subheader("Choose a category")
        topic_selected = st.sidebar.selectbox("Choose a category", topics)
        
        if topic_selected == topics[0]:
            st.sidebar.warning("Please choose a category")
        else:
            news_no = news_no = st.sidebar.slider(
                "Number of news items to show", min_value=10, max_value=1000, step=10
            )
            news_list = fetch_news(2, topic_selected)
            
            if news_list:
                st.subheader(f"Here's news from {topic_selected}")
                load_news(news_list, news_no)
            else:
                st.error(f"Sorry, we couldn't find any news for {topic_selected}")

    elif category_selected == category[3]:
        user_topic = st.sidebar.text_input("Enter a search term")
        news_no = st.sidebar.slider(
            "Number of news items to show", min_value=10, max_value=1000, step=100
        )
        if st.sidebar.button("Search") and user_topic != "":
            user_topic_cleaned = user_topic.replace(" ", "")
            news_list = fetch_news(3, topic=user_topic_cleaned)
            if news_list:
                st.subheader(f"Here's some news on {user_topic.title()}")
                load_news(news_list, news_no)
            else:
                st.error(f"Sorry, we couldn't find any news for {user_topic}")
        else:
            st.warning("Please provide a topic to search with minimum 3 characters")

if __name__ == "__main__":
    run()
