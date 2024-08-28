from langchain_community.document_loaders import YoutubeLoader
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
import os
from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup

from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from typing import Type

load_dotenv()

#############################################################################
#############################################################################
def get_news(number: str) -> dict:
    """
    Obtiene la información de una noticia específica del boletin semanal.

    Args:
        number (str): El índice de la noticia a recuperar.

    Returns:
        dict: Un diccionario con el título, autor, fecha y URL de la noticia.
    """
    int_num = int(number) - 1
    newsletter_url = "https://urkoregueiro.github.io/web-assistant/"
    response = requests.get(newsletter_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    news = soup.find("ul", class_="news-list").find_all("li", class_="news-item")

    titulo = news[int_num].find("h3", class_="news-title").get_text()
    autor = news[int_num].find("span", class_="author").get_text()
    fecha = news[int_num].find("span", class_="date").get_text()
    URL = news[int_num].find("span", class_="source").find("a")["href"]

    information = {"titulo": titulo,
                   "autor": autor,
                   "fecha": fecha,
                   "URL": URL
                   }

    return information


#############################################################################
#############################################################################



llm_summary = ChatOpenAI(temperature=0, model="gpt-4o-mini", openai_api_key=os.getenv('OPENAI_API_KEY'))

prompt_template = """Write an article in SPANISH for a newspaper summarizing the following:
    {text}
    SUMMARY:"""
prompt = PromptTemplate.from_template(prompt_template)

refine_template = (
    "Your job is to produce a final newspaper article in SPANISH\n"
    "We have provided an existing summary of a text in spanish up to a certain point: {existing_answer}\n"
    "We have the opportunity to refine the existing summary"
    "(only if needed) with some more context below.\n"
    "------------\n"
    "{text}\n"
    "------------\n"
    "Given the new context, refine the original summary"
    "If the context isn't useful, return the original summary."
)
refine_prompt = PromptTemplate.from_template(refine_template)

# Chain
chain = load_summarize_chain(llm=llm_summary,
                             chain_type="refine",
                             question_prompt=prompt,
                             refine_prompt=refine_prompt,
                             return_intermediate_steps=False,
                             input_key="input_documents",
                             output_key="output_text",
                             )

def summarizer(url: str):
    '''
    Función utilizada para la transcripción de videos y su resumen.

    Inputs:
        - url: str -> La url del video.

    Output:
        - resumen: str -> El resumen del video.
    '''

    # Cargo y transcribo:
    loader = YoutubeLoader.from_youtube_url(url, add_video_info=True, language=["es"])
    transcript = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=3500, chunk_overlap=500)
    chunks = text_splitter.split_documents(transcript)

    summary = chain.invoke({"input_documents": chunks}, return_only_outputs=True)["output_text"]

    return summary

#############################################################################
#############################################################################

class SearchInput(BaseModel):
    number: str = Field(...,
                        description="Número de la noticia en formato str. Solo el número.")

class GetInformationTool(BaseTool):
    name = "search_information"
    description = "Utilizada para obtener la información sobre una noticia específica del boletin semanal. El input SOLO puede ser un numero."
    args_schema: Type[BaseModel] = SearchInput

    def _run(self, number: str) -> str:
        information = get_news(number)

        return information

#############################################################################
#############################################################################

class UrlInput(BaseModel):
    url: str = Field(...,
                     description="La url de la noticia. Solo la URL.")

class SummarizeTool(BaseTool):
    name = "resumidor"
    description = "Utilizada para resumir una noticia específica del boletin semanal. El input SOLO puede ser una URL."
    args_schema: Type[BaseModel] = UrlInput

    def _run(self, url: str) -> str:
        resumen = summarizer(url)

        return resumen