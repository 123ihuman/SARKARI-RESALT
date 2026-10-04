import json
from datetime import datetime

def update_html():
    with open('data/updates.json') as f:
        data = json.load(f)
    
    # Sort by date (newest first)
    data.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    # Group by category
    categories = {}
    for item in data:
        cat = item.get('category', 'Latest Jobs')
        categories.setdefault(cat, []).append(item)
    
    # Generate HTML sections
    html = ""
    for cat_name, items in categories.items():
        html += f'<h2>{cat_name}</h2>\n<ul>\n'
        for item in items[:20]:  # Show latest 20 per category
            html += f'  <li><a href="{item["url"]}">{item["title"]}</a> '
            html += f'<span class="date">{item.get("date", "")[:10]}</span></li>\n'
        html += '</ul>\n'
    
    # Inject into your HTML template
    with open('index.html', 'r') as f:
        template = f.read()
    
    # Replace placeholder (add this to your HTML)
    updated = template.replace('<!-- AUTO_UPDATES -->', html)
    
    with open('index.html', 'w') as f:
        f.write(updated)

if __name__ == "__main__":
    update_html()
