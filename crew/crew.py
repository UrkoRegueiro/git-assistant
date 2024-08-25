from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from tools.agent_tools import InformationTool
from langchain_openai import ChatOpenAI
import os

from tools.functions import load_html_template
from dotenv import load_dotenv
load_dotenv()


@CrewBase
class NewsletterCrew:

    agents_config = "agents/agents.yaml"
    tasks_config = "tasks/tasks.yaml"

    def llm(self):
        llm = ChatOpenAI(temperature=0, model="gpt-4o-mini", openai_api_key=os.getenv('OPENAI_API_KEY'))

        return llm

    @agent
    def analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["analyst"],
            tools=[InformationTool()],
            verbose=True,
            allow_delegation=False,
            llm=self.llm(),
        )

    @agent
    def editor(self) -> Agent:
        return Agent(
            config=self.agents_config["editor"],
            verbose=True,
            allow_delegation=False,
            llm=self.llm(),
        )

    @task
    def analyst_task(self) -> Task:
        return Task(
            config=self.tasks_config["analyst_task"],
            agent=self.analyst(),
        )

    @task
    def editor_task(self) -> Task:
        return Task(
            config=self.tasks_config["editor_task"],
            agent=self.editor(),
            output_file="../index.html",
        )

    @crew
    def crew(self) -> Crew:
        return Crew(agents=self.agents,
                    tasks=self.tasks,
                    process=Process.sequential,
                    verbose=1,
                    )

def run():
    inputs = {'html_template': load_html_template()}
    NewsletterCrew().crew().kickoff(inputs=inputs)

run()