import requests 
from bs4 import BeautifulSoup 
from textblob import TextBlob  
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from googletrans import Translator
from gtts import gTTS
import base64
import os
import uuid
import spacy
import yake
import json
import unicodedata

API_KEY = "b2d6e62854c14d5c908885ba470df579"
NEWS_API_URL = "https://newsapi.org/v2/everything"

nlp = spacy.load("en_core_web_sm")  # spaCy's pre-trained model for part-of-speech tagging


# Query a news API for articles
def get_news_articles(company, num_articles=10):
    params = {
        "q": company,
        "apiKey": API_KEY,
        "language": "en",
        "pageSize": num_articles,
        "sortBy": "relevancy"
    }
    response = requests.get(NEWS_API_URL, params=params)
    data = response.json()
    return [article["url"] for article in data.get("articles", [])]

# Summarizes the content of the news article
def summarize_text(text, num_sentences=5):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, num_sentences)
    return '\n'.join([str(sentence) for sentence in summary])


def extract_topics(text, top_n=10):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    
    # Extract named entities
    entities = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT", "EVENT", "GPE"]]
    
    # Extract key phrases using YAKE
    kw_extractor = yake.KeywordExtractor(n=2, top=top_n)
    keywords = [kw[0] for kw in kw_extractor.extract_keywords(text)]
    
    
    topics = list(set(entities + keywords)) # combining the topics exctracted usingg spaCy and YAKE
    topics = [t for t in topics if len(t) > 2]
    return topics[:5]


# Sentiment analysis of the summaries as ether positive, negative or neutral
def analyze_sentiment(text):
    blob = TextBlob(text)
    positive_statements, negative_statements = [], []
    for sentence in blob.sentences:
        sentiment_score = sentence.sentiment.polarity
        if sentiment_score > 0.1:
            positive_statements.append(sentence.raw)
        elif sentiment_score < -0.1:
            negative_statements.append(sentence.raw)
    overall_sentiment = "Positive" if len(positive_statements) > len(negative_statements) else "Negative" if len(negative_statements) > len(positive_statements) else "Neutral"
    return {"sentiment": overall_sentiment, "positive_statements": positive_statements, "negative_statements": negative_statements}


#
def scrape_article(url):
    try:

        #Mimics a common web browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }


        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Extract title and paragraphs
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('title').text.strip() if soup.find('title') else "Title not found"
        paragraphs = soup.find_all('p')
        text_content = ' '.join([p.text for p in paragraphs])


        # Error handling
        if not text_content:
            print(f"No text extracted from {url}.")
            return {"error": "No content found"}


        # Searches for summary tag, if no tag found creates a summary of the text content
        summary_tag = soup.find('meta', attrs={'name': 'description'})
        summary = summary_tag['content'] if summary_tag else summarize_text(text_content)
        
        try:
            topics = extract_topics(text_content)
        except Exception as e:
            print(f"Error extracting topics: {e}")
            topics = []

        try:
            sentiment_analysis = analyze_sentiment(summary)
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            sentiment_analysis = {"sentiment": "Neutral"}

        return {
            "Title": title,
            "Summary": summary,
            "Sentiment": sentiment_analysis["sentiment"],
            "Topics": topics
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {"error": f"Failed to scrape {url}: {e}"}


# Total count of the sentiment across the articles and finds common topics and unique ones
def generate_comparative_analysis(articles):
    sentiment_distribution = {"Positive": 0, "Negative": 0, "Neutral": 0}
    common_topics, unique_topics = set(), {}
    for idx, article in enumerate(articles):
        sentiment_distribution[article['Sentiment']] += 1
        unique_topics[f"Article {idx+1}"] = set(article['Topics'])
        if idx == 0:
            common_topics = set(article['Topics'])
        else:
            common_topics = common_topics.intersection(article['Topics'])

    return {"Sentiment Distribution": sentiment_distribution, "Topic Overlap": {"Common Topics": list(common_topics), "Unique Topics": unique_topics}}



def generate_hindi_tts(text_in_english):
    translator = Translator()
    # Translate English text to Hindi
    translated = translator.translate(text_in_english, dest='hi')
    hindi_text = translated.text  # This is now a proper Hindi string

    # Passing the Hindi text to gTTS
    temp_filename = f"temp_{uuid.uuid4().hex}.mp3"
    audio_base64 = None

    try:
        tts = gTTS(hindi_text, lang='hi')
        tts.save(temp_filename)

        # Convert MP3 file to base64
        with open(temp_filename, "rb") as f:
            audio_data = f.read()
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")
    except Exception as e:
        print("TTS error:", e)
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

    return audio_base64



def generate_final_sentiment(comparative_analysis, company, summaries):
    if not comparative_analysis["Sentiment Distribution"]:
        return "No valid articles found."

    # Generate a summary from all article summaries
    combined_text = " ".join(summaries)
    parser = PlaintextParser.from_string(combined_text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    final_summary_sentences = summarizer(parser.document, 1)  # Summarize into 1 sentence

    # Convert summary sentences into a proper string
    final_summary = " ".join(str(sentence) for sentence in final_summary_sentences)

    # Normalize and Fix Unicode Issues
    final_summary = unicodedata.normalize("NFKC", final_summary)
    final_summary = final_summary.encode("utf-8").decode("utf-8") 

    # Overall sentiment
    main_sentiment = max(comparative_analysis["Sentiment Distribution"], key=comparative_analysis["Sentiment Distribution"].get)

    final_analysis = f"The latest news coverage on {company} is mostly {main_sentiment.lower()}. {final_summary}"
    audio_base64 = generate_hindi_tts(final_analysis)
    return{"text": final_analysis, "audio_base64": audio_base64}



def main(company):
    urls = get_news_articles(company)
    articles = []
    
    for url in urls:
        article = scrape_article(url)
        if 'error' not in article:
            articles.append(article)  # Ensure articles are added

    summaries = [article["Summary"] for article in articles if "Summary" in article]
    comparative_analysis = generate_comparative_analysis(articles)
    final_sentiment = generate_final_sentiment(comparative_analysis, company, summaries)
    
    return {
        "Company": company,
        "Articles": articles,
        "Comparative Sentiment Score": comparative_analysis,
        "Final Sentiment Analysis": final_sentiment
    }


def convert_sets_to_lists(obj):
    """ Recursively convert all sets in the object to lists """
    if isinstance(obj, set):
        return list(obj)  # Convert set to list
    elif isinstance(obj, dict):
        return {k: convert_sets_to_lists(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_sets_to_lists(i) for i in obj]
    else:
        return obj  # Return as-is if it's neither set, dict, nor list




if __name__ == "__main__":
    company_name = input("Enter the company name: ")
    result = main(company_name)
    formatted_result = convert_sets_to_lists(result)
    print(json.dumps(formatted_result, indent=4, ensure_ascii=False))

    