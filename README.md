# 🥶 Bing Chilling - Microsoft Rewards Automator

A stealthy, asynchronous desktop application built in Python to fully automate Microsoft Bing Rewards daily tasks. 

Powered by **CustomTkinter** for a responsive, modern UI and **Camoufox** (via Playwright) for advanced anti-detect browser automation.

## ✨ Features
* **Multi-Account Manager:** Create, rename, delete, and seamlessly switch between multiple Microsoft profiles.
* **Local Secure Storage:** Emails, passwords, and browser cookies are stored locally in isolated profile folders.
* **Auto-Installer:** Automatically detects and downloads the required Camoufox stealth browser binaries in the background.
* **Smart Login:** Uses saved browser cookies to bypass login screens if a session is already active.
* **Humanized Searches:** Integrates with [SerpApi](https://serpapi.com/) to fetch real-time Google trends for organic-looking search queries.
* **Async & Threaded UI:** The GUI remains 100% responsive while the browser executes complex automation tasks in the background.

## 🛠️ Included Automation Tasks
1. **Daily Quests:** Automatically completes the 3 daily punch-card clicks.
2. **Daily Searches:** Cycles through required PC searches.
3. **Search Trends:** Performs sequential searches using real-world trending keywords.
4. **▶ Run All:** Sequentially fires off all tasks for true one-click automation.

---

## 🚀 Getting Started (For Standard Users)

If you just want to run the app without installing Python, use the pre-compiled release.

### 1. Download the Release
1. Go to the [Releases](../../releases) tab on the right side of this GitHub page.
2. Download the latest `.zip` file (e.g., `BingRewardsBot_v1.0.zip`).
3. Extract the **entire folder** to your desktop or desired location. *(Do not extract just the `.exe` file!)*

### 2. Set Up Your API Key
This bot uses SerpApi to fetch real trending words so your searches don't look like a bot repeating the same dictionary words.
1. Create a free account at [SerpApi.com](https://serpapi.com/) to get an API key.
2. Open the extracted bot folder.
3. Rename the `.env.example` file to `.env`.
4. Open `.env` in Notepad and paste your API key:
   ```
   SERPAPI_KEY=your_api_key_here
   ```
### **3. Run the Bot**

Double-click BingRewardsBot.exe to launch the dashboard. Create your first profile, enter your credentials, and click "Start Browser & Login"!

(Note: On the very first run, the app will ask to download the ~300MB Camoufox stealth browser engine. Allow it to finish downloading before starting tasks).


💻 Building from Source (For Developers)

If you want to read the code or run the bot directly through Python:
Prerequisites

    Python 3.10+

    Git

Installation

1.Clone the repository:
  ```
  git clone [https://github.com/yourusername/Bing-Rewards-Automator.git](https://github.com/yourusername/Bing-Rewards-Automator.git)
  cd Bing-Rewards-Automator
  ```
# 2. Create and activate a virtual environment (Recommended):
**Create the environment**
    python -m venv .venv
**Windows:**
```.venv\Scripts\activate```
**Mac/Linux:**
```source .venv/bin/activate```
# 3. Install dependencies and fetch browser binaries:
**Install required Python packages**
```pip install -r requirements.txt```

**Download the custom stealth browser**
```camoufox fetch```
# 4. Set up your environment variables:
Create a .env file in the root directory and add your SerpApi key.
```# File: .env```
```SERPAPI_KEY=your_api_key_here```
# 5. Launch the application:
```python main.py```
⚠️ Disclaimer & Warning

Use this software at your own risk. Automating Microsoft Rewards violates Microsoft's Terms of Service. While this bot uses an advanced anti-detect browser (Camoufox) and natural search terms to minimize risk, there is always a chance of account suspension or bans.

Pro-Tip: Do NOT route this bot's traffic through the Tor network or cheap VPNs. Microsoft heavily flags datacenter/Tor exit node IPs. For the highest safety, run this on your standard home network or a mobile hotspot.
📄 License

This project is open-source and available under the [MIT License](https://opensource.org/license/mit).
