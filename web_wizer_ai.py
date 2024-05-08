import streamlit as st
import textwrap
import google.generativeai as genai
from langchain.tools import DuckDuckGoSearchRun
import requests
from bs4 import BeautifulSoup
import urllib.parse
from dotenv import load_dotenv
import os


load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def to_markdown(text):
    text = text.replace('•', '  *')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

def fetch_related_urls(query, num_results=16):
    urls = []
    search_url = f"https://duckduckgo.com/html/?q={query}&t=h_&ia=web"
    response = requests.get(search_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        search_results = soup.find_all('a', class_='result__a')
        for result in search_results[:num_results]:
            url = result['href']
            # Unquote the URL to decode any encoded characters
            decoded_url = urllib.parse.unquote(url)

            target_url = decoded_url.split('uddg=')[1]
            urls.append(target_url)
    return urls


prompt="""
You are the Ai powered search engine , your name is web-wizer-ai,
your role is summarize the answer get from duckduckgo search results based on user query.

"""

# Define Streamlit app
def main():
    st.title("Web Wizer AI: \n AI-Powered Personalized Search Engine")

    try:
        model = genai.GenerativeModel('gemini-pro')

        with st.form(key='content_form'):
            user_query = st.text_input("Enter your query:", key='user_query')
            submitted = st.form_submit_button("Submit")

            if submitted and user_query:
                response = model.generate_content(user_query)

                if response:
                    st.markdown(to_markdown(response.text))
                else:
                    st.write("Failed to generate content for the query:", user_query)

                related_urls = fetch_related_urls(user_query)

                if related_urls:
                    st.write("Related URLs:")
                    for idx, url in enumerate(related_urls, start=1):
                        st.write(f"{idx}. {url}")
                else:
                    st.write("No related URLs found for query:", user_query)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
