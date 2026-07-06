import os
import sys
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import requests

# Load environment variables from a local .env file if it exists (for local testing)
if os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip() and not line.strip().startswith("#"):
                parts = line.strip().split("=", 1)
                if len(parts) == 2:
                    os.environ[parts[0].strip()] = parts[1].strip()

# Configuration
RSS_URL = "https://news.google.com/rss/search?q=(\"Abacus.AI\"+OR+\"Abacus+AI\"+OR+ChatLLM+OR+\"image+model\"+OR+\"text-to-image\"+OR+\"LLM+advancement\"+OR+GPT+OR+Claude+OR+Llama+OR+Mistral+OR+Midjourney)&hl=en-US&gl=US&ceid=US:en"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Pacific Time Zone (UTC-7) for consistent daily headers
TZ_PACIFIC = timezone(timedelta(hours=-7))
CURRENT_DATE_STR = datetime.now(TZ_PACIFIC).strftime("%A, %B %d, %Y")

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI News Digest - {date}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0b0f19;
            --card-bg: #161b26;
            --border-color: #242b3d;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-purple: #8b5cf6;
            --accent-cyan: #06b6d4;
            --btn-gradient: linear-gradient(135deg, #6366f1, #4f46e5);
            --btn-hover: linear-gradient(135deg, #4f46e5, #4338ca);
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            background-color: var(--bg-color);
            color: var(--text-primary);
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            padding: 1.5rem 1rem;
            display: flex;
            justify-content: center;
            min-height: 100vh;
        }}
        
        .container {{
            width: 100%;
            max-width: 600px;
            display: flex;
            flex-direction: column;
            gap: 2rem;
        }}
        
        header {{
            text-align: center;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }}
        
        .digest-title {{
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.025em;
        }}
        
        .refresh-action-btn {{
            background: transparent;
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            border-radius: 50%;
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .refresh-action-btn:hover {{
            background: var(--card-bg);
            color: var(--accent-cyan);
            border-color: var(--accent-cyan);
        }}
        
        .refresh-action-btn:active {{
            transform: scale(0.95);
        }}
        
        .refresh-icon {{
            width: 20px;
            height: 20px;
            transition: transform 0.3s ease;
        }}
        
        .spinning {{
            animation: spin 1s linear infinite;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .date {{
            font-size: 1rem;
            color: var(--text-secondary);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            text-align: left;
        }}
        
        .status-msg-box {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
            margin-top: 1rem;
            text-align: left;
            font-size: 0.95rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}
        
        .status-msg-box.hidden {{
            display: none !important;
        }}
        
        .progress-bar-container {{
            background: var(--border-color);
            border-radius: 9999px;
            height: 6px;
            width: 100%;
            overflow: hidden;
        }}
        
        .progress-bar {{
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
            height: 100%;
            width: 0%;
            transition: width 0.1s linear;
        }}
        
        section {{
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }}
        
        .section-title {{
            font-size: 1.35rem;
            font-weight: 600;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 0.5rem;
        }}
        
        .headline-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .headline-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
            border-color: rgba(99, 102, 241, 0.4);
        }}
        
        .headline-card h3 {{
            font-size: 1.2rem;
            font-weight: 600;
            line-height: 1.4;
            color: #ffffff;
        }}
        
        .headline-card p {{
            font-size: 1.05rem;
            color: var(--text-secondary);
            font-weight: 300;
        }}
        
        .source-btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 44px;
            padding: 0 1.25rem;
            background: var(--btn-gradient);
            color: #ffffff;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.95rem;
            align-self: flex-start;
            margin-top: 0.5rem;
            transition: background-color 0.2s, transform 0.1s;
        }}
        
        .source-btn:hover {{
            background: var(--btn-hover);
        }}
        
        .source-btn:active {{
            transform: scale(0.98);
        }}
        
        .quick-hits-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}
        
        .quick-hit-item {{
            background-color: var(--card-bg);
            border-left: 3px solid var(--accent-cyan);
            border-radius: 0 8px 8px 0;
            padding: 1rem 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}
        
        .quick-hit-link {{
            color: #ffffff;
            text-decoration: none;
            font-weight: 500;
            font-size: 1.05rem;
            line-height: 1.4;
            min-height: 44px;
            display: flex;
            align-items: center;
        }}
        
        .quick-hit-link:hover {{
            color: var(--accent-cyan);
            text-decoration: underline;
        }}
        
        .takeaway-box {{
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(168, 85, 247, 0.08));
            border-left: 4px solid var(--accent-purple);
            border-radius: 8px;
            padding: 1.5rem;
            border-top: 1px solid rgba(139, 92, 246, 0.1);
            border-right: 1px solid rgba(139, 92, 246, 0.1);
            border-bottom: 1px solid rgba(139, 92, 246, 0.1);
        }}
        
        .takeaway-box h3 {{
            font-size: 1.15rem;
            font-weight: 600;
            color: var(--accent-purple);
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .takeaway-box p {{
            font-size: 1.05rem;
            color: var(--text-primary);
            line-height: 1.6;
        }}
        
        footer {{
            text-align: center;
            padding: 2rem 0;
            font-size: 0.85rem;
            color: var(--text-secondary);
            border-top: 1px solid var(--border-color);
            margin-top: 1rem;
        }}
        
        footer a {{
            color: var(--accent-cyan);
            text-decoration: none;
        }}
        
        footer a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-top">
                <div class="digest-title">AI News Digest</div>
                <button id="refresh-btn" class="refresh-action-btn" title="Trigger Refresh" aria-label="Trigger News Refresh">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="refresh-icon"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
                </button>
            </div>
            <div class="date">{date}</div>
            <div id="status-container" class="status-msg-box hidden">
                <span id="status-text"></span>
                <div class="progress-bar-container"><div id="progress-bar" class="progress-bar"></div></div>
            </div>
        </header>
        
        <section>
            <h2 class="section-title">🔥 Headline Stories</h2>
            {headlines}
        </section>
        
        <section>
            <h2 class="section-title">⚡ Quick Hits</h2>
            <ul class="quick-hits-list">
                {quick_hits}
            </ul>
        </section>
        
        <section>
            <div class="takeaway-box">
                <h3>💡 Why It Matters</h3>
                <p>{why_it_matters}</p>
            </div>
        </section>
        
        <footer>
            Generated automatically via Groq &amp; GitHub Actions.<br>
            Stable bookmark link. Updated daily at 10:00 AM PDT.
        </footer>
    </div>
    <script>
        document.getElementById('refresh-btn').addEventListener('click', async function() {{
            const btn = this;
            const icon = btn.querySelector('.refresh-icon');
            const statusBox = document.getElementById('status-container');
            const statusText = document.getElementById('status-text');
            const progressBar = document.getElementById('progress-bar');
            
            let pat = localStorage.getItem('gh_pat');
            if (!pat) {{
                pat = prompt("To trigger an on-demand news refresh, please enter a GitHub Personal Access Token (PAT) with 'workflow' permissions. It will be saved only in your device's local storage:");
                if (!pat) return;
                localStorage.setItem('gh_pat', pat.trim());
            }}
            
            btn.disabled = true;
            icon.classList.add('spinning');
            statusBox.classList.remove('hidden');
            statusText.innerText = "Triggering refresh on GitHub Actions...";
            progressBar.style.width = "0%";
            
            try {{
                const owner = "Voiddev18";
                const repo = "ai-news";
                const response = await fetch(`https://api.github.com/repos/${{owner}}/${{repo}}/actions/workflows/daily-news.yml/dispatches`, {{
                    method: 'POST',
                    headers: {{
                        'Authorization': `Bearer ${{pat}}`,
                        'Accept': 'application/vnd.github+json',
                        'X-GitHub-Api-Version': '2022-11-28'
                    }},
                    body: JSON.stringify({{ ref: 'main' }})
                }});
                
                if (response.ok || response.status === 204) {{
                    statusText.innerHTML = "🔄 <strong>Refresh triggered!</strong> Scraper is running in the cloud. Updating page in 40 seconds...";
                    
                    let duration = 40;
                    let current = 0;
                    const interval = setInterval(() => {{
                        current += 0.2;
                        const pct = (current / duration) * 100;
                        progressBar.style.width = `${{pct}}%`;
                        
                        if (current >= duration) {{
                            clearInterval(interval);
                            statusText.innerText = "Reloading page...";
                            location.reload();
                        }}
                    }}, 200);
                }} else {{
                    const errText = await response.text();
                    console.error("Github API Error:", errText);
                    if (response.status === 401 || response.status === 403) {{
                        localStorage.removeItem('gh_pat');
                        throw new Error("Invalid GitHub token. It has been cleared. Please click refresh and try again with a valid token.");
                    }} else {{
                        throw new Error(`Failed to trigger workflow: ${{response.status}} ${{response.statusText}}`);
                    }}
                }}
            }} catch (error) {{
                btn.disabled = false;
                icon.classList.remove('spinning');
                statusText.innerHTML = `❌ <strong style="color: #f87171;">Error:</strong> ${{error.message}}`;
                progressBar.style.width = "0%";
            }}
        }});
    </script>
</body>
</html>
"""

def fetch_rss_articles():
    print("Fetching AI news from Google News RSS...")
    req = urllib.request.Request(RSS_URL, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
    except Exception as e:
        print(f"Error fetching RSS: {e}")
        sys.exit(1)
        
    root = ET.fromstring(xml_data)
    items = root.findall('.//item')
    articles = []
    
    for item in items[:25]: # Fetch top 25 recent items
        title = item.find('title').text if item.find('title') is not None else ""
        link = item.find('link').text if item.find('link') is not None else ""
        pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
        
        # Clean title suffix (typically " - Publisher") if present
        clean_title = title
        if " - " in title:
            clean_title = title.rsplit(" - ", 1)[0]
            
        articles.append({
            "title": clean_title,
            "url": link,
            "pubDate": pub_date
        })
        
    print(f"Successfully loaded {len(articles)} articles from RSS.")
    return articles

def generate_news_content(articles):
    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY is not set. Please set the GROQ_API_KEY environment variable.")
        sys.exit(1)
        
    print("Sending articles to Groq API for selection and summarization...")
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    system_prompt = (
        "You are an expert AI news curator specializing in new image generation models (like Midjourney, Stable Diffusion, FLUX, etc.), LLM advancements (like GPT, Claude, Gemini, Llama, Mistral, etc.), and news about Abacus.AI, ChatLLM, or their competitors (such as Scale AI, Databricks, OpenAI, Anthropic, Cohere, Together AI, etc.).\n\n"
        "CRITICAL FILTERING RULE: You must ONLY select news stories that fall into one of these categories:\n"
        "1. New image models and advancements in text-to-image/video generation.\n"
        "2. New large language model (LLM) advancements and model releases.\n"
        "3. News or developments regarding Abacus.AI or ChatLLM.\n"
        "4. News or developments regarding direct competitors of Abacus.AI/ChatLLM (e.g. Scale AI, Databricks, Together AI, OpenAI Enterprise, Anthropic, etc.).\n"
        "Do NOT select or include general AI news, policy, ethics, or unrelated corporate news unless it fits the above categories.\n\n"
        "Constraints:\n"
        "1. Choose 3 to 5 'headline_stories'. For each, write a 2-3 sentence summary. You MUST use the exact URL from the input list.\n"
        "2. Choose 3 to 5 other interesting but minor news points for 'quick_hits'. For each, write a short, one-sentence description and use its exact URL.\n"
        "3. Write a single-paragraph 'why_it_matters' takeaway summarizing the macro trend or key impact of today's news.\n"
        "4. CRITICAL: You must use the exact URLs provided in the input list for the selected stories. Do not modify, truncate, or invent URLs. This is crucial for linking back to sources.\n"
        "5. Respond ONLY with a valid JSON object matching the schema below. Do not include markdown formatting or backticks around the JSON (e.g. do not wrap in ```json ... ```)."
    )
    
    schema_example = {
        "headline_stories": [
            {
                "title": "Clean, descriptive title of story",
                "summary": "2-3 sentences summarizing the news clearly and factually.",
                "url": "Exact URL from input"
            }
        ],
        "quick_hits": [
            {
                "title": "Short descriptive bullet point of other news",
                "url": "Exact URL from input"
            }
        ],
        "why_it_matters": "One 'Why it matters' takeaway explaining the broader implications of today's developments."
    }
    
    user_content = f"JSON schema:\n{json.dumps(schema_example, indent=2)}\n\nArticles:\n{json.dumps(articles, indent=2)}"
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        res_json = response.json()
        raw_content = res_json["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error querying Groq API: {e}")
        # Try fallback model if llama-3.3 fails
        print("Attempting fallback model (llama-3-8b-8192)...")
        payload["model"] = "llama-3-8b-8192"
        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            res_json = response.json()
            raw_content = res_json["choices"][0]["message"]["content"]
        except Exception as fallback_err:
            print(f"Fallback model also failed: {fallback_err}")
            sys.exit(1)
            
    # Parse and clean JSON content
    cleaned_content = raw_content.strip()
    if cleaned_content.startswith("```json"):
        cleaned_content = cleaned_content[7:]
    if cleaned_content.endswith("```"):
        cleaned_content = cleaned_content[:-3]
    cleaned_content = cleaned_content.strip()
    
    try:
        content_data = json.loads(cleaned_content)
        return content_data
    except Exception as e:
        print("Failed to parse JSON response from Groq:")
        print(cleaned_content)
        print(f"Parse error: {e}")
        sys.exit(1)

def build_html(data):
    print("Building HTML output...")
    headlines_html = ""
    for item in data.get("headline_stories", []):
        headlines_html += f"""
        <div class="headline-card">
            <h3>{item.get('title')}</h3>
            <p>{item.get('summary')}</p>
            <a href="{item.get('url')}" target="_blank" rel="noopener noreferrer" class="source-btn">Read Source</a>
        </div>"""
        
    quick_hits_html = ""
    for item in data.get("quick_hits", []):
        quick_hits_html += f"""
        <li class="quick-hit-item">
            <a href="{item.get('url')}" target="_blank" rel="noopener noreferrer" class="quick-hit-link">
                {item.get('title')}
            </a>
        </li>"""
        
    why_it_matters = data.get("why_it_matters", "No takeaway available today.")
    
    html_output = TEMPLATE.format(
        date=CURRENT_DATE_STR,
        headlines=headlines_html,
        quick_hits=quick_hits_html,
        why_it_matters=why_it_matters
    )
    
    output_path = "index.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_output)
    print(f"HTML successfully generated and saved to {output_path}")

def main():
    articles = fetch_rss_articles()
    if not articles:
        print("No articles fetched. Exiting.")
        sys.exit(1)
    summary_data = generate_news_content(articles)
    build_html(summary_data)
    print("Process complete!")

if __name__ == "__main__":
    main()
