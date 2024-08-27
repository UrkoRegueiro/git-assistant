from crewai_tools import BaseTool
from typing import Union, Tuple, Dict
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
import json
import os
#############################################################################
#############################################################################

def info_videos(dias=7):
    '''
    Función que devuelve información de los videos de los últimos 7 días

    Input:
        - dias: int --> Número de días

    Output:
        - results: object --> JSON con la información obtenida(titulo, autor, fecha, url, resumen)
    '''

    # Fecha de hace 7 días
    today = datetime(datetime.now().year, datetime.now().month, datetime.now().day, tzinfo=timezone.utc)
    two_days_ago = today - timedelta(days=dias)
    date_format = two_days_ago.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    youtube = build("youtube", "v3", developerKey=os.getenv('YOUTUBE_API_KEY'))
    request = youtube.search().list(part="snippet",
                                    order="date",
                                    type="video",
                                    videoDuration="any",
                                    publishedAfter=date_format,
                                    channelId="UCBLCvUUCiSqBCEc-TqZ9rGw",
                                    maxResults=10
                                    )

    response = request.execute()

    results = {"results": []}
    counter = 0

    for video in response["items"]:
        title = video["snippet"]["title"]
        image_url = video["snippet"]["thumbnails"]["high"]["url"]
        author = video["snippet"]["channelTitle"]
        date = video["snippet"]["publishTime"]
        video_id = video["id"]["videoId"]
        url = f"https://www.youtube.com/watch?v={video_id}&ab_channel=JuanRam%C3%B3nRallo"

        results["results"].append({"id": counter,
                                   "titulo": title,
                                   "url_imagen": image_url,
                                   "autor": author,
                                   "fecha": date,
                                   "url_video": url
                                   })
        counter += 1

    with open('utils/back/information.json', 'w') as file:
        json.dump(results, file)

    return results

class InformationTool(BaseTool):
    name: str = "Herramienta de análisis"
    description: str = ("Esta herramienta se utiliza para obtener información de videos de youtube. NO NECESITA INPUT.")

    def _to_args_and_kwargs(self, tool_input: Union[str, Dict]) -> Tuple[Tuple, Dict]:
        return (), {}

    def _run(self):
        results = info_videos()
        return results
