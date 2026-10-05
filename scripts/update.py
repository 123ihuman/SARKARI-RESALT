import os, json, re, time
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
    prompt = f"""Visit this URL: {url}
Category: {category}
Extract the top 20 latest entries as a JSON array.
Each item must be: {{"title":"exact title","link":"full absolute URL","date":"YYYY-MM-DD or empty"}}
Return ONLY the JSON array. No explanation, no markdown."""
    try:
        res = model.generate_content(prompt)
        m = re.search(r"\[.*\]", res.text, re.DOTALL)
        if m:
            return json.loads(m.group())
    except Exception as e:
        print("ai fail", e)
    return []

def main():
    all_items = []
    for cat, url in SOURCES.items():
    print("Fetching", cat)
    items = extract(url, cat)
    print("  got", len(items), "items")
    for it in items:
        it["category"] = cat
    all_items.extend(items)
    time.sleep(20)   # wait 20s to avoid free-tier rate limit

    os.makedirs("data", exist_ok=True)
    existing = []
    if os.path.exists("data/updates.json"):
        try:
            existing = json.load(open("data/updates.json"))
        except: existing = []

    seen = {e.get("title","").lower() for e in existing}
    new = [i for i in all_items if i.get("title","").lower() not in seen]
    combined = new + existing
    combined.sort(key=lambda x: x.get("date",""), reverse=True)

    json.dump(combined, open("data/updates.json","w"), indent=2)
    print("New:", len(new), "Total:", len(combined))

if __name__ == "__main__":
    main()
