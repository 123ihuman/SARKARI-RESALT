import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

def fetch_sarkari_result():
    """Fetch latest from SarkariResult"""
    url = "https://www.sarkariresult.com/latestjob.php"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    jobs = []
    # Extract job listings (adjust selectors as needed)
    for item in soup.select('#post ul li'):
        link = item.find('a')
        if link:
            jobs.append({
                'title': link.text.strip(),
                'url': link.get('href', ''),
                'date': datetime.now().isoformat(),
                'category': 'Latest Jobs'
            })
    return jobs

def categorize_with_ai(items):
    """Use AI to categorize entries automatically"""
    # Integrate with OpenAI/Gemini API here
    # Or use simple keyword matching as fallback
    categories = {
        'result': 'Results',
        'admit': 'Admit Cards', 
        'answer': 'Answer Keys',
        'syllabus': 'Syllabus',
        'job': 'Latest Jobs'
    }
    for item in items:
        title_lower = item['title'].lower()
        for key, cat in categories.items():
            if key in title_lower:
                item['category'] = cat
                break
    return items

def save_data(data):
    """Save to JSON for site generation"""
    with open('data/updates.json', 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    jobs = fetch_sarkari_result()
    categorized = categorize_with_ai(jobs)
    save_data(categorized)
    print(f"Fetched and saved {len(categorized)} items")
