"""
Script principale che coordina l'esecuzione del programma
"""
import asyncio
import time
import os
from config import CONFIG, BROWSER_CONFIG, API_CONFIG
from scraper import TikTokScraper
from html_template import HTMLGenerator

async def main(pages: int = None, num_videos: int = None):
    """
    Funzione principale che coordina il processo di scraping
    
    Args:
        pages: Numero di pagine da analizzare (opzionale)
        num_videos: Numero di video da includere nell'output (opzionale)
    """
    # Inizializza lo scraper
    scraper = TikTokScraper()
    
    # Usa i valori passati o quelli di default da CONFIG
    pages_to_analyze = min(27, pages if pages is not None else CONFIG['PAGES_TO_ANALYZE'])
    output_videos = num_videos if num_videos is not None else CONFIG['OUTPUT_VIDEOS']
    
    # Mostra configurazione
    print(f"\nConfigurazione attuale:")
    print(f"- Pagine da analizzare: {pages_to_analyze}")
    print(f"- Video nell'output finale: {output_videos}")
    print(f"- Paese: {CONFIG['COUNTRY_CODE']}")
    print(f"- Periodo: ultimi {CONFIG['TIME_PERIOD']} giorni")
    print(f"- File di output locale: {CONFIG['LOCAL_FILENAME']}")
    print(f"- Nome file sul server: {CONFIG['REMOTE_FILENAME']}\n")

    # Ottiene i parametri di autenticazione
    auth_params = await scraper.extract_auth_params()
    if not auth_params:
        print("Errore nell'estrazione dei parametri di autenticazione")
        return
    
    print(f"\nInizio scraping dei video trending...")
    
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
    for page in range(1, pages_to_analyze + 1):
        videos = scraper.fetch_tiktok_page(page, params, headers)
        if videos:
            all_videos.extend(videos)
            print(f"Pagina {page}/{pages_to_analyze} completata")
        time.sleep(CONFIG['DELAY'])

    total_videos = len(all_videos)
    print(f"\nTotale video trovati: {total_videos}")
    
    if all_videos:
        print("\nOrdinamento di tutti i video per timestamp...")
        all_videos_sorted = sorted(all_videos, key=lambda x: int(x['item_id']), reverse=True)
        
        # Verifica che il numero richiesto non sia maggiore del totale disponibile
        output_videos = min(output_videos, total_videos)
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
        
        print(f"Analizzate {pages_to_analyze} pagine, trovati {total_videos} video totali, generato output con i {output_videos} più recenti.")

if __name__ == "__main__":
    asyncio.run(main())
