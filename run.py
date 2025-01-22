import asyncio
import os
from ftplib import FTP
from main import main
from config import CONFIG

# Configurazione FTP
FTP_CONFIG = {
    'host': 'notizia.info',
    'user': 'scriptok@notizia.info',
    'password': 'scriptok2025##',
    'path': '/public_html',
    'remote_filename': CONFIG['LOCAL_FILENAME'],  # Usa lo stesso nome del file locale
}

def upload_to_ftp(local_file):
    """
    Carica un file nella directory specificata del server FTP
    """
    print(f"\nInizio processo di upload FTP per {local_file}")
    print(f"Dimensione locale del file: {os.path.getsize(local_file)} bytes")
    
    try:
        with FTP(FTP_CONFIG['host']) as ftp:
            # Mostra informazioni di debug FTP
            ftp.set_debuglevel(2)
            
            # Login
            print("\nTentativo di login...")
            ftp.login(user=FTP_CONFIG['user'], passwd=FTP_CONFIG['password'])
            print("Login effettuato con successo")
            
            # Cambia directory
            print(f"\nCambio directory in {FTP_CONFIG['path']}...")
            ftp.cwd(FTP_CONFIG['path'])
            print("Directory cambiata con successo")
            
            # Lista i file prima dell'upload
            print("\nFile presenti sul server prima dell'upload:")
            files_before = ftp.nlst()
            for f in files_before:
                print(f"- {f}")
            
            # Carica il file
            print(f"\nInizio caricamento di {local_file}...")
            with open(local_file, 'rb') as f:
                # Usa STOR con il nome del file remoto
                upload_result = ftp.storbinary(f'STOR {FTP_CONFIG["remote_filename"]}', f)
                print(f"Risultato upload: {upload_result}")
            
            # Verifica il caricamento
            print("\nVerifica del caricamento...")
            files_after = ftp.nlst()
            if FTP_CONFIG['remote_filename'] in files_after:
                remote_size = ftp.size(FTP_CONFIG['remote_filename'])
                print(f"File trovato sul server! Dimensione: {remote_size} bytes")
                if remote_size == os.path.getsize(local_file):
                    print("Le dimensioni corrispondono - Upload completato con successo!")
                else:
                    print("ATTENZIONE: Le dimensioni non corrispondono!")
            else:
                raise Exception("File non trovato sul server dopo l'upload")
                
    except Exception as e:
        print(f"\nErrore durante l'upload FTP: {str(e)}")
        raise

async def run():
    try:
        # Esegui lo script principale
        print("Avvio dello script principale...")
        await main()
        
        # Verifica il file locale
        local_file = CONFIG['LOCAL_FILENAME']
        if not os.path.exists(local_file):
            raise FileNotFoundError(f"File {local_file} non trovato!")
        
        # Upload FTP
        upload_to_ftp(local_file)
        
    except Exception as e:
        print(f"Errore durante l'esecuzione: {e}")
        import traceback
        print("\nStack trace completo:")
        print(traceback.format_exc())
        raise

if __name__ == "__main__":
    asyncio.run(run())
