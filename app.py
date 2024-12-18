import os
from dotenv import load_dotenv
import streamlit as st
from googleapiclient.discovery import build
from groq import Groq

load_dotenv()

# Load API keys
groqcloud_apikey = os.getenv('GROQCLOUD_API_KEY')
youtube_api_key = os.getenv('YOUTUBE_API_KEY')

# Set environment variables for Groq Cloud API
os.environ['GROQ_API_KEY'] = groqcloud_apikey

def init_groq_client():
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        # Test client initialization
        _ = client.chat.completions.create(
            messages=[{"role": "system", "content": "hello"}],
            model="llama3-8b-8192",
        )
        return client
    except Exception as e:
        if 'invalid_api_key' in str(e):
            st.error("Invalid Groq API Key! Please verify your API key and try again.")
        else:
            st.error(f"Failed to initialize Groq client: {e}")
        st.stop()

def init_youtube_client():
    try:
        youtube_client = build('youtube', 'v3', developerKey=youtube_api_key)
        # Test the YouTube API with a simple request
        request = youtube_client.channels().list(
            part='snippet',
            id='UC_x5XG1OV2P6uZZ5FSM9Ttw'  # Replace with a valid YouTube channel ID
        )
        response = request.execute()
        return youtube_client
    except Exception as e:
        if 'keyInvalid' in str(e):
            st.error("Invalid YouTube API Key! Please verify your API key and try again.")
        else:
            st.error(f"Failed to initialize YouTube client: {e}")
        st.stop()

client = init_groq_client()
youtube = init_youtube_client()

st.set_page_config(
    page_title="IPL AI & YouTube Insights",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

def fetch_youtube_videos(query):
    try:
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=5
        ).execute()
        return search_response.get("items", [])
    except Exception as e:
        st.error(f"Error fetching YouTube videos: {e}")
        return []

def get_chatbot_response(user_message, chat_history):
    try:
        messages = chat_history + [{"role": "user", "content": user_message}]
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error getting response from IPL AI: {e}")
        return "Sorry, I am having trouble understanding you right now."

def main():
    st.title('🏏 IPL AI & YouTube Insights')
    st.write("Explore IPL insights and related YouTube videos.")

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    with st.form(key='chat_form'):
        user_input = st.text_input('You: ', placeholder="Ask about IPL or cricket topics...")
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        chatbot_response = get_chatbot_response(user_input, st.session_state['chat_history'])
        st.session_state['chat_history'].append({"role": "user", "content": user_input})
        st.session_state['chat_history'].append({"role": "assistant", "content": chatbot_response})
        
        st.markdown(f"**You:** {user_input}")
        st.markdown(f"**IPL AI:** {chatbot_response}")

        st.markdown("### Related YouTube Videos")
        videos = fetch_youtube_videos(user_input)
        for video in videos:
            video_title = video['snippet']['title']
            video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
            st.markdown(f"- [{video_title}]({video_url})")

if __name__ == "__main__":
    main()
