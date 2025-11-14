# 1. IMPORT LIBRARY YANG DIBUTUHKAN 
# (Bagian ini sama, tidak perlu diubah)
import streamlit as st
import googleapiclient.discovery
import pandas as pd
import plotly.express as px
import re
from datetime import datetime
import google.generativeai as genai

# 2. KONFIGURASI HALAMAN DAN API KEY
# (Bagian ini sama, tidak perlu diubah)
st.set_page_config(page_title="YouTube Channel Analyzer", page_icon="🚀", layout="wide")

try:
    API_KEY = st.secrets["YOUTUBE_API_KEY"]
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)
except Exception as e:
    st.error("Gagal memuat API Key YouTube. Pastikan file .streamlit/secrets.toml sudah benar.")
    st.stop()
    
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("Gagal memuat API Key Gemini. Pastikan sudah ditambahkan di .streamlit/secrets.toml")

# 3. FUNGSI-FUNGSI BANTUAN (LOGIKA UTAMA)
# (Semua fungsi Anda dari get_channel_id_from_url hingga get_nlp_insights tetap sama, tidak perlu diubah)

# ... (Salin semua fungsi Anda dari kode sebelumnya di sini) ...
def get_channel_id_from_url(url):
    """Mengekstrak Channel ID dari berbagai format URL YouTube."""
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/channel\/([a-zA-Z0-9_-]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/c\/([a-zA-Z0-9_-]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/@([a-zA-Z0-9_-]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/user\/([a-zA-Z0-9_-]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            handle = match.group(1)
            if "/channel/" not in url:
                request = youtube.search().list(part="snippet", q=handle, type="channel", maxResults=1)
                response = request.execute()
                if response['items']:
                    return response['items'][0]['id']['channelId']
            else:
                 return handle
    return None

@st.cache_data(ttl=3600)
def get_channel_stats(channel_id):
    """Mengambil statistik utama sebuah channel."""
    request = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    )
    response = request.execute()
    if not response.get("items"):
        return None
    data = response["items"][0]
    stats = {
        "Nama Channel": data["snippet"]["title"],
        "Deskripsi": data["snippet"]["description"],
        "Total Subscriber": int(data["statistics"].get("subscriberCount", 0)),
        "Total Video": int(data["statistics"].get("videoCount", 0)),
        "Total Penonton": int(data["statistics"].get("viewCount", 0)),
        "Tanggal Dibuat": data["snippet"]["publishedAt"]
    }
    return stats

@st.cache_data(ttl=3600)
def get_all_video_details(channel_id):
    """Mengambil detail dari semua video di sebuah channel."""
    all_videos = []
    request = youtube.channels().list(part='contentDetails', id=channel_id)
    response = request.execute()
    playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    next_page_token = None
    while True:
        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        video_ids = [item['contentDetails']['videoId'] for item in response['items']]
        if not video_ids: break

        video_request = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids)
        )
        video_response = video_request.execute()

        for item in video_response["items"]:
            video_data = {
                "Judul": item["snippet"]["title"],
                "Tanggal Upload": item["snippet"]["publishedAt"],
                "Penonton": int(item["statistics"].get("viewCount", 0)),
                "Likes": int(item["statistics"].get("likeCount", 0)),
                "Komentar": int(item["statistics"].get("commentCount", 0)),
                "Video ID": item["id"]
            }
            all_videos.append(video_data)
            
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
            
    return pd.DataFrame(all_videos)

def analyze_content(df):
    """Memberikan insight dan saran berdasarkan data video."""
    if df.empty:
        return "Tidak ada data video untuk dianalisis."
    most_viewed = df.loc[df['Penonton'].idxmax()]
    df['Engagement Rate'] = (df['Likes'] / df['Penonton']).fillna(0)
    best_engagement = df.loc[df['Engagement Rate'].idxmax()]
    top_10_videos = df.nlargest(10, 'Penonton')
    words = ' '.join(top_10_videos['Judul']).lower().split()
    common_words = pd.Series(words).value_counts().head(10).index.tolist()
    stop_words = ['di', 'dan', 'yang', 'ini', 'itu', 'ke', 'cara', 'review', 'part', 'episode', 'dengan', 'untuk', 'the', 'a', 'an']
    keywords = [word for word in common_words if word not in stop_words and len(word) > 3]
    insights = f"""
    ### 💡 Insight & Saran Konten
    **Video Paling Populer:**
    - **Judul:** "{most_viewed['Judul']}"
    - **Penonton:** {most_viewed['Penonton']:,}
    - **Insight:** Konten dengan topik atau format seperti video ini tampaknya sangat disukai audiens Anda. Pertimbangkan untuk membuat video lanjutan atau seri berdasarkan topik ini.
    **Video Engagement Terbaik:**
    - **Judul:** "{best_engagement['Judul']}"
    - **Rasio Like/View:** {best_engagement['Engagement Rate']:.2%} 
    - **Insight:** Video ini berhasil memancing interaksi positif (like) dibandingkan jumlah penontonnya. Pelajari elemen apa dari video ini (narasi, visual, topik, humor?) yang membuatnya sangat menarik bagi audiens.
    **Topik yang Menonjol:**
    - Berdasarkan 10 video teratas, kata kunci yang sering muncul adalah: **{', '.join(keywords)}**.
    - **Saran:**
        1.  **Perdalam Topik:** Buat video yang lebih mendalam tentang **{keywords[0] if keywords else 'topik relevan'}** dan **{keywords[1] if len(keywords)>1 else 'topik lain'}**.
        2.  **Gunakan Format Sukses:** Terapkan elemen yang membuat video engagement terbaik Anda sukses ke topik populer lainnya.
    """
    return insights

def calculate_rating(stats, df):
    """Memberikan rating channel dari 1-10 berdasarkan statistik."""
    score = 0
    reasons = []
    subs = stats.get('Total Subscriber', 0)
    if subs >= 1000000: score += 3; reasons.append(f"🌟 Subscriber > 1 Juta ({subs:,})")
    elif subs >= 100000: score += 2; reasons.append(f"⭐ Subscriber > 100 Ribu ({subs:,})")
    elif subs >= 10000: score += 1; reasons.append(f"👍 Subscriber > 10 Ribu ({subs:,})")
    else: reasons.append(f"🌱 Subscriber {subs:,} (potensi tumbuh)")
    if not df.empty and 'Penonton' in df.columns:
        avg_views = df['Penonton'].mean()
        if avg_views >= 50000: score += 3; reasons.append(f"🚀 Rata-rata View > 50 Ribu ({int(avg_views):,})")
        elif avg_views >= 10000: score += 2; reasons.append(f"👀 Rata-rata View > 10 Ribu ({int(avg_views):,})")
        elif avg_views >= 2000: score += 1; reasons.append(f"💡 Rata-rata View > 2 Ribu ({int(avg_views):,})")
        else: reasons.append(f"🍃 Rata-rata View {int(avg_views):,} (perlu ditingkatkan)")
    else:
        reasons.append("❌ Data video tidak tersedia untuk analisis.")
    if not df.empty and 'Likes' in df.columns and 'Penonton' in df.columns:
        total_likes = df['Likes'].sum()
        total_views = df['Penonton'].sum()
        if total_views > 0:
            engagement_rate = (total_likes / total_views) * 100
            if engagement_rate >= 5: score += 3; reasons.append(f"💖 Engagement > 5% ({engagement_rate:.2f}%)")
            elif engagement_rate >= 2.5: score += 2; reasons.append(f"👍 Engagement > 2.5% ({engagement_rate:.2f}%)")
            elif engagement_rate >= 1: score += 1; reasons.append(f"🤔 Engagement > 1% ({engagement_rate:.2f}%)")
            else: reasons.append(f"📉 Engagement < 1% ({engagement_rate:.2f}%)")
        else: reasons.append("⚠️ Tidak ada penonton untuk menghitung engagement.")
    else:
        reasons.append("❌ Data video tidak tersedia untuk analisis.")
    total_videos = stats.get('Total Video', 0)
    if total_videos >= 500: score += 1; reasons.append(f"🔥 Sangat Aktif ( > 500 video)")
    elif total_videos >= 200: score += 1; reasons.append(f"✅ Cukup Aktif ( > 200 video)")
    elif total_videos < 50: reasons.append(f"⏳ Perlu lebih konsisten ( < 50 video)")
    else: reasons.append(f"✅ Cukup aktif ({total_videos} video)")
    rating = max(1, min(10, round(score)))
    return rating, reasons

@st.cache_data(ttl=86400)
def get_nlp_insights(channel_stats, df):
    """Menggunakan Gemini untuk memberikan analisis mendalam."""
    if df.empty:
        return "Tidak cukup data video untuk dianalisis oleh AI."
    channel_name = channel_stats['Nama Channel']
    channel_description = channel_stats['Deskripsi']
    subscriber_count = channel_stats['Total Subscriber']
    top_5_videos = df.nlargest(5, 'Penonton')
    top_video_titles = "\n- ".join(top_5_videos['Judul'].tolist())
    prompt = f"""
    Anda adalah seorang Ahli Strategi YouTube Profesional.
    Analisis data channel ini:
    - Nama Channel: {channel_name}
    - Subscribers: {subscriber_count:,}
    - Deskripsi: "{channel_description}"
    - 5 Judul Video Terpopuler:
    - {top_video_titles}

    Berikan analisis dalam format berikut:

    **1. Esensi & Identitas Channel:**
    (Jelaskan inti dari channel ini dalam 2-3 kalimat. Apa proposisi nilai uniknya?)

    **2. Analisis Target Audiens:**
    (Jelaskan siapa target audiens ideal channel ini berdasarkan topik video populernya.)

    **3. Tiga Saran Konten Strategis:**
    (Berikan 3 ide konten konkret dan strategis yang baru, bukan mengulang yang sudah ada.)
    - **Ide 1:** [Nama Ide] - [Penjelasan singkat kenapa ide ini bagus]
    - **Ide 2:** [Nama Ide] - [Penjelasan singkat kenapa ide ini bagus]
    - **Ide 3:** [Nama Ide] - [Penjelasan singkat kenapa ide ini bagus]
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Terjadi error saat menghubungi AI Gemini: {e}"


# 4. BAGIAN INTERFACE PENGGUNA (UI) DENGAN STREAMLIT [VERSI BARU]

# --- Injeksi CSS untuk mempercantik tampilan ---
st.markdown("""
<style>
    /* Mengatur container utama agar kontennya di tengah */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Memperbesar dan mempercantik tombol */
    .stButton > button {
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        border-radius: 12px;
        padding: 12px 24px;
        font-size: 18px;
        border: none;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #E03C3C;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transform: scale(1.02);
    }
    /* Mengatur judul utama */
    h1 {
        text-align: center;
        color: #FFFFFF;
    }
    /* Mengatur sub-judul/deskripsi */
    .stMarkdown p {
        text-align: center;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Bagian Landing Page (Input) ---
# Gunakan kolom untuk membuat layout terpusat
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("<h1>🚀 YouTube Channel Analyzer</h1>", unsafe_allow_html=True)
    st.markdown("<p>Dapatkan insight mendalam, rating, dan saran konten strategis<br>untuk mengembangkan channel YouTube Anda.</p>", unsafe_allow_html=True)
    
    st.write("") # Memberi sedikit spasi
    
    url = st.text_input(
        "**Masukkan URL Channel YouTube:**",
        placeholder="Contoh: https://www.youtube.com/@MrBeast",
        label_visibility="collapsed"
    )
    
    st.write("")
    
    # Tombol diletakkan di tengah kolom
    analyze_button = st.button("Analisis Channel Sekarang!")

# --- Bagian Output (Hasil Analisis) ---
if analyze_button:
    if url:
        with st.spinner("Mengambil data dari YouTube... Proses ini mungkin butuh waktu untuk channel besar..."):
            channel_id = get_channel_id_from_url(url)
            
            if channel_id:
                channel_stats = get_channel_stats(channel_id)
                videos_df = get_all_video_details(channel_id)

                if channel_stats and not videos_df.empty:
                    st.success(f"Analisis untuk channel **{channel_stats['Nama Channel']}** berhasil dimuat!")
                    st.markdown("---")

                    # --- Gunakan TABS untuk mengorganisir hasil ---
                    tab1, tab2, tab3, tab4 = st.tabs([
                        "📊 **Ringkasan & Rating**", 
                        "🧠 **Analisis AI**", 
                        "🏆 **Video Populer & Grafik**", 
                        "📋 **Semua Data Video**"
                    ])

                    # TAB 1: Ringkasan & Rating
                    with tab1:
                        st.header("Ringkasan Statistik Channel")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Total Subscriber", f"{channel_stats['Total Subscriber']:,}")
                        c2.metric("Total Video", f"{channel_stats['Total Video']:,}")
                        c3.metric("Total Penonton", f"{channel_stats['Total Penonton']:,}")
                        
                        st.markdown("---")
                        
                        st.header("⭐ Rating Performa Channel")
                        rating, reasons = calculate_rating(channel_stats, videos_df)
                        
                        # Tampilkan rating dalam kolom
                        cr1, cr2 = st.columns([1, 2])
                        with cr1:
                            st.subheader(f"Skor: {rating}/10")
                        with cr2:
                            for reason in reasons:
                                st.markdown(f"- {reason}")
                        
                    # TAB 2: Analisis AI Lanjutan
                    with tab2:
                        st.header("Analisis Strategis dari AI Gemini")
                        st.info("Klik tombol di bawah untuk mendapatkan analisis mendalam tentang identitas channel, target audiens, dan ide konten strategis dari AI.")
                        if st.button("Dapatkan Analisis & Saran Strategis"):
                            with st.spinner("AI sedang berpikir... menganalisis channel Anda..."):
                                nlp_result = get_nlp_insights(channel_stats, videos_df)
                                st.markdown(nlp_result)

                    # TAB 3: Video Populer & Grafik
                    with tab3:
                        st.header("Video Paling Populer")
                        most_viewed_video = videos_df.loc[videos_df['Penonton'].idxmax()]
                        st.subheader(most_viewed_video['Judul'])
                        st.video(f"https://www.youtube.com/watch?v={most_viewed_video['Video ID']}")
                        st.write(f"Ditonton sebanyak **{most_viewed_video['Penonton']:,}** kali.")

                        st.markdown("---")
                        
                        st.header("Grafik Pertumbuhan Konten")
                        videos_df['Tanggal Upload'] = pd.to_datetime(videos_df['Tanggal Upload'])
                        videos_per_month = videos_df.set_index('Tanggal Upload').resample('M').size().reset_index(name='Jumlah Video')
                        fig = px.bar(videos_per_month, x='Tanggal Upload', y='Jumlah Video', title='Jumlah Video yang Di-upload per Bulan')
                        st.plotly_chart(fig, use_container_width=True)

                    # TAB 4: Semua Data Video
                    with tab4:
                        st.header("Tabel Semua Data Video")
                        st.info("Anda bisa mengurutkan data dengan mengklik judul kolom.")
                        st.dataframe(videos_df[['Judul', 'Penonton', 'Likes', 'Komentar', 'Tanggal Upload']])

                else:
                    st.error("Gagal mengambil data. Pastikan channel tersebut memiliki video publik dan URL-nya benar.")
            else:
                st.error("URL tidak valid. Mohon masukkan URL channel YouTube yang benar (contoh: /@MrBeast, /channel/..., /c/...).")
    else:
        st.warning("Mohon masukkan URL channel terlebih dahulu.")