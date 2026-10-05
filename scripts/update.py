import os, json, re, requests
from bs4 import BeautifulSoup
from datetime import datetime
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

SOURCES = {
    "Latest Jobs":  "https://www.sarkariresult.com/latestjob.php",
    "Results":      "https://www.sarkariresult.com/result/",
    "Admit Cards":  "https://www.sarkariresult.com/admitcard/",
    "Answer Keys":  "https://www.sarkariresult.com/answerkey/",
}

def fetch(url):
    try:
        r = requests.get(f"https://r.jina.ai/{url}", timeout=60)
        print("Fetched", url, "len:", len(r.text))
        return r.text
    except Exception as e:
        print("fetch fail", url, e)
        return ""

def extract(html, category):
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)[:6000]
    prompt = f"""Extract job listings from this {category} page text.
Return ONLY a JSON array. Each item: {{"title":"...","link":"...","date":"YYYY-MM-DD or empty"}}.
Max 30 items. No explanation.

TEXT:
{text}"""
    try:
        res = model.generate_content(prompt)
        m = re.search(r"\[.*\]", res.text, re.DOTALL)
        return json.loads(m.group()) if m else []
    except Exception as e:
        print("ai fail", e)
        return []

def main():
    all_items = []
    for cat, url in SOURCES.items():
        print("Fetching", cat)
        html = fetch(url)
        items = extract(html, cat)
        for it in items:
            it["category"] = cat
        all_items.extend(items)

    os.makedirs("data", exist_ok=True)
    existing = []
    if os.path.exists("data/updates.json"):
        existing = json.load(open("data/updates.json"))

    seen = {e.get("title","").lower() for e in existing}
    new = [i for i in all_items if i.get("title","").lower() not in seen]
    combined = new + existing
    combined.sort(key=lambda x: x.get("date",""), reverse=True)

    json.dump(combined, open("data/updates.json","w"), indent=2)
    print("New:", len(new), "Total:", len(combined))

if __name__ == "__main__":
    main()
