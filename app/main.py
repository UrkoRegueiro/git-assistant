from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate

import os
from dotenv import load_dotenv
load_dotenv()

# Cargo API_KEY
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Defino API
app = FastAPI()
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],  # Permite todas las orígenes. Puedes especificar una lista de dominios permitidos.    allow_credentials=True,
                   allow_methods=["*"],  # Permite todos los métodos (GET, POST, PUT, etc.)
                   allow_headers=["*"],  # Permite todos los headers
                   )

class Message(BaseModel):
    message: str


# Defino el llm:
model = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)

# Creamos una cadena con un prompt template y nuestro modelo:
template = """Eres un asistente útil y amable que ayuda a los usuarios con sus preguntas.

{history}
Human: {human_input}
Assistant:"""

prompt = PromptTemplate(input_variables=["history", "human_input"], template=template)


assistant_chain = LLMChain(llm=model,
                           prompt=prompt,
                           verbose=False,
                           memory=ConversationBufferWindowMemory(k=4),
                          )

@app.post("/send-message")
async def send_message(request: Message):
    user_message = request.message

    ai_message = assistant_chain.predict(human_input= user_message)

    return {"response": ai_message}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)