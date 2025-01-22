"""
Configurazioni globali per il sistema di scraping TikTok
"""

# Configurazione principale
# In config.py

CONFIG = {
    'PAGES_TO_ANALYZE': 27,
    'OUTPUT_VIDEOS': 150,
    'COUNTRY_CODE': 'IT',
    'TIME_PERIOD': '7',
    'PAGE_SIZE': 20,
    'DELAY': 0.01,
    'MAX_AUTH_RETRIES': 5,
    'AUTH_RETRY_DELAY': 3,
    'LOCAL_FILENAME': 'scriptok.html',   # Aggiunto per chiarezza
    'REMOTE_FILENAME': 'scriptok.html',  # Aggiunto per FTP
    'VIDEOS_PER_PAGE': 9,
}

# Configurazione browser
BROWSER_CONFIG = {
    'viewport': {'width': 1920, 'height': 1080},
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

# Configurazione API endpoints
API_CONFIG = {
    'trend_list_url': "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/list",
    'base_referer': "https://ads.tiktok.com/business/creativecenter/inspiration/popular/pc/en"
}
