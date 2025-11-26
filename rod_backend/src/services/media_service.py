import feedparser
from bs4 import BeautifulSoup
import time
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
import asyncio
import src.services.db_service as db

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=API_KEY)

NRK_RSS_URL = "https://www.nrk.no/toppsaker.rss"

# In-Memory Cache
NEWS_CACHE = {
    "last_updated": 0,
    "data": []
}
CACHE_DURATION = 3600  # 1 hour

async def determine_difficulty(title: str, summary: str) -> str:
    """
    Uses GPT-5-mini to guess the reading level.
    """
    try:
        # PROMPT
        prompt = f"""
        Classify the Norwegian reading level of this news text.
        Title: "{title}"
        Summary: "{summary}"
        
        Levels:
        - A2: Very simple, familiar topics.
        - B1: Clear standard language, work/school topics.
        - B2: Complex concrete/abstract topics.
        - C1: Demanding, implicit meaning.
        
        CRITICAL: Respond with ONLY the two chars (e.g. "B1"). Do not write sentences.
        """
        
        response = await client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "system", "content": "You are a linguistics expert."}, 
                      {"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        print(f"📊 Classified '{title[:20]}...' as: {content}")

        return content.strip() if content else "B1"
    except Exception as e:
        print(f"⚠️ Classifier Failed: {e}")
        return "B1"

def extract_image(entry) -> str:
    if 'media_content' in entry:
        media = sorted(entry.media_content, key=lambda x: int(x.get('width', 0)), reverse=True)
        if media: return str(media[0]['url'])
    if 'summary' in entry:
        soup = BeautifulSoup(str(entry.summary), 'html.parser')
        img = soup.find('img')
        if img and img.get('src'): return str(img['src'])
    return "https://static.nrk.no/nrk-gfx/nrk-logo-white-720.png"

def clean_summary(html_summary: str) -> str:
    if not html_summary: return ""
    soup = BeautifulSoup(html_summary, 'html.parser')
    return soup.get_text().strip()

async def refresh_news_background():
    """
    Fetches RSS. Checks DB. Only classifies and saves NEW items.
    """
    print("🌍 Checking for fresh news...")
    feed = feedparser.parse(NRK_RSS_URL)
    
    new_count = 0
    # Check top 20 items
    for entry in feed.entries[:20]:
        link = str(entry.get('link', ''))
        
        # OPTIMIZATION
        if db.media_exists(link):
            continue

        # If new, process it
        title = str(entry.get('title', 'No Title'))
        raw_summary = str(entry.get('summary', ''))
        text_summary = clean_summary(raw_summary)
        image_url = extract_image(entry)
        
        # AI Classification
        level = await determine_difficulty(title, text_summary)
        
        item = {
            "title": title,
            "summary": text_summary,
            "link": link,
            "image_url": image_url,
            "level": level,
            "source": "NRK"
        }
        
        db.save_media_item(item)
        new_count += 1
    
    if new_count > 0:
        print(f"✅ Added {new_count} new articles to DB.")
    else:
        print("💤 No new news.")

async def get_cached_news():
    """Returns what is in the DB immediately."""
    return db.get_cached_media(limit=20)