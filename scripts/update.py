import os, json, re, time
from datetime import datetime, timedelta
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3.8-flash")

SOURCES = {
    "Latest Jobs":  "https://www.sarkariresult.com/latestjob.php",
    "Results":      "https://www.sarkariresult.com/result/",
    "Admit Cards":  "https://www.sarkariresult.com/admitcard/",
    "Answer Keys":  "https://www.sarkariresult.com/answerkey/",
}

def extract(url, category):
    today = datetime.now().strftime("%Y-%m-%d")
    cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    prompt = f"""Visit this URL: {url}
Category: {category}
Today's date is {today}.
ONLY extract entries that were posted on or after {cutoff} (last 30 days).
If an entry has no recent date or is older than {cutoff}, SKIP it.
Extract up to 20 entries as a JSON array.
Each item: {{"title":"exact title","link":"full absolute URL","date":"YYYY-MM-DD"}}
Return ONLY the JSON array. No explanation, no markdown, no backticks."""
    try:
        res = model.generate_content(prompt)
        m = re.search(r"\[.*\]", res.text, re.DOTALL)
        if m:
            return json.loads(m.group())
    except Exception as e:
        print("ai fail", e)
    return []

def is_recent(item):
    d = item.get("date", "").strip()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", d):
        return False
    try:
        item_date = datetime.strptime(d, "%Y-%m-%d")
        return item_date >= datetime.now() - timedelta(days=30)
    except:
        return False

def main():
    all_items = []
    for cat, url in SOURCES.items():
        print("Fetching", cat)
        items = extract(url, cat)
        items = [i for i in items if is_recent(i)]
        print("  kept", len(items), "recent items")
        for it in items:
            it["category"] = cat
        all_items.extend(items)
        time.sleep(20)

    os.makedirs("data", exist_ok=True)
    existing = []
    if os.path.exists("data/updates.json"):
        try:
            existing = json.load(open("data/updates.json"))
        except:
            existing = []

    # Drop old junk from existing file too
    existing = [e for e in existing if is_recent(e)]

    seen = {e.get("title", "").lower() for e in existing}
    new = [i for i in all_items if i.get("title", "").lower() not in seen]
    combined = new + existing
    combined.sort(key=lambda x: x.get("date", ""), reverse=True)

    json.dump(combined, open("data/updates.json", "w"), indent=2)
    print("New:", len(new), "Total:", len(combined))

if __name__ == "__main__":
    main()
