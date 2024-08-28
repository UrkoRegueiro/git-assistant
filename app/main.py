from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI

from functions import GetInformationTool, SummarizeTool

import os
from dotenv import load_dotenv
load_dotenv()

#############################################################################################
class EnhancedInMemoryChatMessageHistory(InMemoryChatMessageHistory):
    """Enhanced version of InMemoryChatMessageHistory with message limit."""

    max_messages: int = 2

    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the store and enforce message limit.

        Args:
            message: The message to add.
        """
        super().add_message(message)
        self.messages = self.messages[-self.max_messages:]

class Message(BaseModel):
    message: str
#############################################################################################


# Cargo API_KEY
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Defino API
app = FastAPI()
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_methods=["*"], # (GET, POST, PUT, ...)
                   allow_headers=["*"],
                   )



llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=OPENAI_API_KEY)

memory = EnhancedInMemoryChatMessageHistory(session_id="test-session")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Eres un asistente de un boletin de noticias semanales."
                   "Ayudarás a los lectores en lo que necesiten. "
                   "Eres un experto en presentar resumenes claros."
                   "Cuando tengas que realizar un resumen devolveras este para que se pueda visualizar en un archivo HTML. Devuelve SOLO el contenido HTML, sin comillas triples como '```', '```html' o cualquier otro texto."
                   "El resto de respuestas que no sean un resumen NO seran en formato HTML."),

        ("placeholder", "{chat_history}"),

        ("human", "{input}"),

        ("placeholder", "{agent_scratchpad}"),
    ]
)

tools = [GetInformationTool(), SummarizeTool()]

agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools)

agent_with_chat_history = RunnableWithMessageHistory(agent_executor,
                                                     lambda session_id: memory,
                                                     input_messages_key="input",
                                                     history_messages_key="chat_history",
                                                    )

config = {"configurable": {"session_id": "test-session"}}


@app.post("/send-message")
async def send_message(request: Message):
    user_message = request.message

    response = agent_with_chat_history.invoke({"input": user_message},
                                              config,
                                              )

    ai_message = response["output"]

    return {"response": ai_message}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)