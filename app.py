import streamlit as st
import requests
import base64

def main():
    st.title("News Summarization & Sentiment Analysis")

    company = st.text_input("Enter company name", value="")

    if st.button("GO", key="company_btn"):
        resp = requests.post("http://127.0.0.1:5000/analyze", json={"company": company})
        if resp.status_code == 200:
            data = resp.json()

            # 1. Display articles
            st.write(f"## Articles for {company}")
            articles = data.get("Articles", [])
            for idx, article in enumerate(articles, start=1):
                st.subheader(f"Article #{idx}")
                st.write(f"**Title:** {article['Title']}")
                st.write(f"**Summary:** {article['Summary']}")
                st.write(f"**Sentiment:** {article['Sentiment']}")
                st.write(f"**Topics:** {', '.join(article['Topics'])}")
                st.write("---")

            # 2. Comparative Sentiment Score
            comparative_score = data.get("Comparative Sentiment Score", {})
            st.write("## Comparative Sentiment Score")
            st.json(comparative_score)

            # 3. Final Sentiment + Audio
            final_analysis = data.get("Final Sentiment Analysis", {})
            st.write("## Final Sentiment Analysis")
            st.write(final_analysis.get("text", "No text found."))

            audio_b64 = final_analysis.get("audio_base64")
            if audio_b64:
                audio_bytes = base64.b64decode(audio_b64)
                st.audio(audio_bytes, format="audio/mp3")
            else:
                st.write("No audio available.")
        else:
            st.error(f"Error from server: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    main()
