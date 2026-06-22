# 🤖 AI News Digest Aggregator

A completely automated, mobile-friendly daily AI News aggregator. This system runs every morning at **10:00 AM PDT** via GitHub Actions, fetches the latest AI stories, compiles a dark-mode responsive page, and publishes it via GitHub Pages.

No login, email, or personal info required—just bookmark the stable GitHub Pages URL on your phone and refresh it daily!

---

## 🛠️ How It Works

1. **Scheduled Trigger**: GitHub Actions runs a daily cron job.
2. **Fetch News**: A Python script queries the Google News RSS feed for the latest "Artificial Intelligence" articles from the past 24 hours.
3. **Analyze & Summarize**: The script calls the Groq API (`llama-3.3-70b-versatile` model) to select the top stories, write summaries, curate quick hits, and create a daily macro takeaway.
4. **Publish**: The script renders the stories into a gorgeous, dark-mode, mobile-optimized `index.html` page and pushes it back to GitHub.
5. **Host**: GitHub Pages serves the page under your stable custom URL.

---

## 🚀 Setup Instructions

Follow these simple steps to configure this project:

### 1. Add your Groq API Key
1. Go to your repository on GitHub.
2. Navigate to **Settings** > **Secrets and variables** > **Actions**.
3. Click **New repository secret**.
4. Set the **Name** to `GROQ_API_KEY`.
5. Set the **Value** to your Groq API key (e.g. `gsk_...`).
6. Click **Add secret**.

### 2. Enable GitHub Pages
1. Go to your repository's **Settings** > **Pages**.
2. Under **Build and deployment** > **Source**, choose **Deploy from a branch**.
3. Under **Branch**, select `main` and `/ (root)`.
4. Click **Save**.

Your stable daily news page will be available at:
`https://<your-username>.github.io/ai-news/` (e.g. `https://Voiddev18.github.io/ai-news/`)

---

## 💻 Local Development

To run or test the script locally on your machine:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Voiddev18/ai-news.git
   cd ai-news
   ```

2. **Create a `.env` file** in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```
   *(Note: `.env` is ignored by git to keep your key secure).*

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the aggregator**:
   ```bash
   python generate_news.py
   ```

5. **View the page**:
   Open the generated `index.html` in any browser or scan it on a mobile simulation view.
