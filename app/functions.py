from langchain_community.document_loaders import YoutubeLoader
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
import os
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