from crewai_tools import BaseTool
from typing import Union, Tuple, Dict
from crew.tools.functions import info_videos


class InformationTool(BaseTool):
    name: str = "Herramienta de análisis"
    description: str = ("Esta herramienta se utiliza para obtener información de videos de youtube")

    def _to_args_and_kwargs(self, tool_input: Union[str, Dict]) -> Tuple[Tuple, Dict]:
        return (), {}

    def _run(self):
        results = info_videos()
        return results