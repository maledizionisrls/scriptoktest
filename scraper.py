"""
Gestione dello scraping dei video TikTok
"""
from typing import List, Dict, Optional
import pyktok as pyk
import json
import time
import requests
from playwright.async_api import async_playwright
import asyncio
from config import CONFIG, BROWSER_CONFIG, API_CONFIG

class TikTokScraper:
    def __init__(self):
        self.config = CONFIG
        self.browser_config = BROWSER_CONFIG
        self.api_config = API_CONFIG

    async def extract_auth_params(self) -> Optional[Dict[str, str]]:
        """Estrae i parametri di autenticazione necessari"""
        for attempt in range(self.config['MAX_AUTH_RETRIES']):
            target_params = None
            request_event = asyncio.Event()
            
            async with async_playwright() as p:
                print(f"Tentativo {attempt + 1} di {self.config['MAX_AUTH_RETRIES']} per l'estrazione dei parametri di autenticazione...")
                browser = None
                try:
                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context(
                        viewport=self.browser_config['viewport'],
                        user_agent=self.browser_config['user_agent']
                    )
                    
                    page = await context.new_page()
                    
                    async def handle_request(request):
                        if "creative_radar_api/v1/popular_trend/list" in request.url:
                            headers = request.headers
                            nonlocal target_params
                            target_params = {
                                'timestamp': headers.get('timestamp'),
                                'user-sign': headers.get('user-sign'),
                                'web-id': headers.get('anonymous-user-id', '')
                            }
                            request_event.set()

                    page.on("request", handle_request)

                    try:
                        navigation_task = asyncio.create_task(
                            page.goto(self.api_config['base_referer'])
                        )
                        await asyncio.wait_for(request_event.wait(), timeout=7)
                        await navigation_task
                        
                        if target_params:
                            print("Parametri di autenticazione estratti con successo!")
                            return target_params
                            
                    except Exception as e:
                        print(f"Errore durante la navigazione nel tentativo {attempt + 1}: {e}")
                    
                finally:
                    if browser:
                        await browser.close()
            
            if attempt < self.config['MAX_AUTH_RETRIES'] - 1:
                print(f"Attendo {self.config['AUTH_RETRY_DELAY']} secondi prima del prossimo tentativo...")
                await asyncio.sleep(self.config['AUTH_RETRY_DELAY'])
        
        print("Impossibile ottenere i parametri di autenticazione dopo tutti i tentativi")
        return None

    def fetch_tiktok_page(self, page: int, params: Dict, headers: Dict) -> List[Dict]:
        """Recupera una singola pagina di video"""
        params = params.copy()
        params['page'] = str(page)

        try:
            response = requests.get(
                self.api_config['trend_list_url'],
                headers=headers,
                params=params,
                timeout=7
            )
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and isinstance(data['data'], dict):
                    videos = data['data'].get('videos', [])
                    print(f"Pagina {page} caricata")
                    return videos
                return []
        except Exception as e:
            print(f"Errore pagina {page}: {str(e)}")
            return []

    def extract_video_data(self, url: str) -> Optional[Dict]:
        """Estrae i dati di un singolo video"""
        try:
            tt_json = pyk.alt_get_tiktok_json(url)
            
            if tt_json is None:
                return {
                    'titolo': 'Video non disponibile',
                    'creator': 'N/A',
                    'url': url,
                    'views': 'N/A',
                    'categorie': 'N/A',
                    'keywords': 'N/A'
                }
            
            if isinstance(tt_json, str):
                try:
                    tt_json = json.loads(tt_json)
                except json.JSONDecodeError:
                    return None

            default_scope = tt_json.get('__DEFAULT_SCOPE__', {})
            webapp_detail = default_scope.get('webapp.video-detail', {})
            item_info = webapp_detail.get('itemInfo', {}).get('itemStruct', {})
            
            stats = item_info.get('stats', {})
            views = stats.get('playCount', 'N/A') if isinstance(stats, dict) else 'N/A'
            views_formatted = self.format_number(views) if views != 'N/A' else 'N/A'
            
            div_labels = item_info.get('diversificationLabels', [])
            sug_words = item_info.get('suggestedWords', [])
            
            return {
                'titolo': item_info.get('desc', 'N/A'),
                'creator': item_info.get('author', {}).get('nickname', 'N/A'),
                'url': url,
                'views': views_formatted,
                'categorie': ', '.join(div_labels) if div_labels else 'N/A',
                'keywords': ', '.join(sug_words) if sug_words else 'N/A'
            }
            
        except Exception as e:
            print(f"Errore nell'estrazione dei dati per {url}: {str(e)}")
            return None

    @staticmethod
    def format_number(num):
        """Formatta i numeri con i separatori delle migliaia"""
        try:
            return "{:,}".format(int(num)).replace(",", ".")
        except:
            return str(num)

def save_video_data(videos_data, output_filename):
    """Salva i dati dei video in un file JSON"""
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(videos_data, f, ensure_ascii=False, indent=4)

async def run():
    try:
        # Inizializza lo scraper
        scraper = TikTokScraper()
        
        # Ottiene i parametri di autenticazione
        auth_params = await scraper.extract_auth_params()
        if not auth_params:
            print("Errore nell'estrazione dei parametri di autenticazione")
            return
        
        # Prepara i parametri per le richieste
        params = {
            "period": CONFIG['TIME_PERIOD'],
            "limit": str(CONFIG['PAGE_SIZE']),
            "order_by": "vv",
            "country_code": CONFIG['COUNTRY_CODE']
        }
        
        headers = {
            "timestamp": auth_params['timestamp'],
            "user-sign": auth_params['user-sign'],
            "anonymous-user-id": auth_params['web-id'],
            "Accept": "application/json",
            "User-Agent": BROWSER_CONFIG['user_agent'],
            "Referer": API_CONFIG['base_referer']
        }

        # Recupera tutti i video
        all_videos = []
        for page in range(1, CONFIG['PAGES_TO_ANALYZE'] + 1):
            videos = scraper.fetch_tiktok_page(page, params, headers)
            if videos:
                all_videos.extend(videos)
                print(f"Pagina {page}/{CONFIG['PAGES_TO_ANALYZE']} completata")
            time.sleep(CONFIG['DELAY'])

        total_videos = len(all_videos)
        print(f"\nTotale video trovati: {total_videos}")
        
        if all_videos:
            print("\nOrdinamento di tutti i video per timestamp...")
            all_videos_sorted = sorted(all_videos, key=lambda x: int(x['item_id']), reverse=True)
            
            # Verifica che il numero richiesto non sia maggiore del totale disponibile
            output_videos = min(CONFIG['OUTPUT_VIDEOS'], total_videos)
            top_videos = all_videos_sorted[:output_videos]
            
            print(f"\nInizio analisi dettagliata dei {output_videos} video più recenti tra i {total_videos} video trovati...\n")
            
            videos_data = []
            for idx, video in enumerate(top_videos, 1):
                url = video['item_url']
                print(f"\nAnalisi video {idx}/{output_videos}: {url}")
                
                video_data = scraper.extract_video_data(url)
                if video_data:
                    videos_data.append(video_data)
                    print(f"Video {idx} analizzato con successo")
                else:
                    print(f"Non è stato possibile analizzare questo video")
                
                time.sleep(CONFIG['DELAY'])

            # Salva i dati dei video in un file JSON
            video_data_file = 'video_data.json'
            save_video_data(videos_data, video_data_file)

            # Assicurati che la directory esista
            output_dir = os.path.dirname(CONFIG['LOCAL_FILENAME'])
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Genera il file HTML con il nome specificato in LOCAL_FILENAME
            HTMLGenerator.generate_html_file(videos_data, CONFIG['LOCAL_FILENAME'])
            
            if os.path.exists(CONFIG['LOCAL_FILENAME']):
                print(f"\nFile HTML generato con successo: {CONFIG['LOCAL_FILENAME']}")
                print(f"Dimensione file: {os.path.getsize(CONFIG['LOCAL_FILENAME'])} bytes")
            else:
                print(f"\nERRORE: Il file {CONFIG['LOCAL_FILENAME']} non è stato creato!")

            # Upload FTP
            upload_to_ftp(CONFIG['LOCAL_FILENAME'])
            
            print(f"Analizzate {CONFIG['PAGES_TO_ANALYZE']} pagine, trovati {total_videos} video totali, generato output con i {output_videos} più recenti.")

    except Exception as e:
        print(f"Errore durante l'esecuzione: {e}")
        import traceback
        print("\nStack trace completo:")
        print(traceback.format_exc())
        raise

if __name__ == "__main__":
    asyncio.run(run())
