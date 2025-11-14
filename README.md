# 🚀 YouTube Channel Analyzer

 <!-- Optional: Add a GIF or screenshot of your app here -->

A powerful web application built with Streamlit that provides in-depth analysis, strategic insights, and AI-powered recommendations for any YouTube channel. This tool is designed to help content creators understand their performance, discover what works, and plan their next steps for growth.

**[➡️ Live Demo Link Here](https://bestoism-youtubechannelanalyzer.streamlit.app/)** <!-- Replace with your actual Streamlit deployment link -->

---

## ✨ Features

- **Comprehensive Channel Statistics:** Get a complete overview of any channel, including total subscribers, total videos, and total views.
- **Performance Rating:** An objective 1-10 rating system that scores a channel based on key metrics like subscriber count, average views, and engagement rate.
- **In-depth Video Analysis:** Fetches and displays data for all videos on a channel, including view counts, likes, and comments.
- **Content Strategy Insights:** Automatically identifies top-performing videos and popular keywords to provide actionable content suggestions.
- **📈 Interactive Charts:** Visualize content growth over time with an interactive bar chart showing monthly video uploads.
- **🧠 AI-Powered Strategic Analysis (Powered by Google Gemini):**
  - **Channel Essence:** Understand the core identity and value proposition of a channel.
  - **Target Audience Analysis:** Get an AI-generated profile of the ideal audience.
  - **Strategic Content Suggestions:** Receive three concrete, forward-thinking content ideas to drive growth.
- **Modern & Clean UI:** A user-friendly interface organized with tabs for easy navigation.

---

## 🛠️ Tech Stack

This project is built with a modern Python stack:

- **Framework:** [Streamlit](https://streamlit.io/)
- **Data APIs:**
  - [YouTube Data API v3](https://developers.google.com/youtube/v3) for fetching channel and video data.
  - [Google Generative AI (Gemini)](https://ai.google.dev/) for advanced NLP analysis and strategic insights.
- **Data Manipulation:** [Pandas](https://pandas.pydata.org/)
- **Data Visualization:** [Plotly Express](https://plotly.com/python/plotly-express/)
- **Deployment:** [Streamlit Community Cloud](https://streamlit.io/cloud)

---

## 🚀 Getting Started

Follow these instructions to set up and run the project locally on your machine.

### Prerequisites

- Python 3.8+
- Git
- A Google account to get API keys.

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/YoutubeChannelAnalyzer.git
    cd YoutubeChannelAnalyzer
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your API Keys:**
    - You will need API keys from both Google Cloud (for YouTube Data API) and Google AI Studio (for Gemini API).
    - Create a file at `.streamlit/secrets.toml`.
    - Add your keys to this file in the following format:
      ```toml
      YOUTUBE_API_KEY = "your_youtube_api_key_here"
      GEMINI_API_KEY = "your_gemini_api_key_here"
      ```

5.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```
    The application will open in your default web browser at `http://localhost:8501`.

---

## 🚀 Deployment

This application is ready to be deployed on [Streamlit Community Cloud](https://streamlit.io/cloud).

1.  **Push your code to a public GitHub repository.** (You've already done this!)
2.  **Create a `requirements.txt` file:**
    ```bash
    pip freeze > requirements.txt
    ```
3.  **Go to share.streamlit.io** and connect your GitHub account.
4.  **Click "New app"** and select your repository.
5.  **Important:** Go to the "Advanced settings" and paste the contents of your `secrets.toml` file into the "Secrets" section.
6.  **Click "Deploy!"** and wait for your app to go live.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- Thanks to the [Streamlit](https://streamlit.io/) team for creating such an amazing framework for data apps.
- Thanks to [Google](https://google.com) for providing the powerful YouTube and Gemini APIs.
