import requests
import shutil

from pathlib import Path

def get_http_request_with_streaming(url: str, headers:dict, params:dict, output_pad:Path):
    """
    Gemaakt met AI.

    Generieke DWH-ingestie met de 'requests' bibliotheek.
    Volledig veilig voor bestanden tot 100GB+ dankzij stream=True.
    """

    output_pad_folder=output_pad.parent
    if not output_pad_folder.exists() or not output_pad_folder.is_dir():
        output_pad_folder.mkdir(parents=True, exist_ok=True)

    # stream=True zorgt ervoor dat alleen de HTTP-headers direct worden ingeladen
    # De feitelijke body (data) blijft op de server wachten tot we gaan lezen
    with requests.get(url, headers=headers, params=params, stream=True) as response:
        # Belangrijk voordeel van requests: super makkelijke status check
        response.raise_for_status() 
        response.raw.decode_content = True
        
        # Gebruik de 'raw' socket-stream van requests i.c.m. shutil
        with open(output_pad, 'wb') as lokaal_bestand:
            shutil.copyfileobj(response.raw, lokaal_bestand)
            
    