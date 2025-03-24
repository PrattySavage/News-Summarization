News Summarization and Analysis

Installation

Prerequisites
•	For this project, Python 3.10.12 was used on Linux.
•	An internet connection is require for News API calls and gTTS.

Steps for the setup
•	Install these dependencies before using the main program, the requirements text file consists of all the package names and their version used.

pip install -r requirements.txt

python3 -m spacy download en_core_web_sm

python3 -m textblob.download_corpora

•	Run Flask
python3 api.py

•	Run Streamlit
streamlit run app.py

•	Visit http://localhost:8501 and enter a company name to fetch and analyze news.


Structure
The project consists of mainly four files
•	utils.py (Consists of all the functions necessary for scraping, summarization, etc.)
•	api.py (Flash backend)
•	app.py (Streamlit frontend)
•	requirements.txt (Consists of all the necessary packages that needs to be installed)


util.py
•	Fetches 10 news articles of company from a new API and scrapes the articles using BeautifulSoup.
•	Summarizes text with the help of sumy library.
•	Extract topics with spacy + YAKE.
•	Sentiment analysis of the summaries of news articles with TextBlob.
•	Generates Hindi speech of the Final Sentiment, an additional step of converting English text to Hindi text is done.

api.py
•	An API endpoint is defined at /analyse that only accepts POST request.
•	This acts as a backend which receives a POST request with a JSON payload, it calls for the functions in the utils file and delivers the final data into a JSON response.
•	The frontend can parse that JSON and use it to display information.

app.py
•	The frontend calls the backends’  /analyse route.
•	The backend returns a JSON response.
•	The frontend decodes that JSON and displays the results via Streamlit widgets.

APIs used
-	POST /analyze
-	Body: `{"company":""}`
-	Response: JSON with articles, comparative sentiment, and an `audio_base64` field for Hindi TTS.

Assumptions
•	Requires a valid NewsAPI.org key or any other API key.
•	Requires an internet connection for NewsAPI and gTTS.

