from pydantic import Field

from backend.agent.toolcall import ToolCallAgent
from backend.prompt.manus import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from backend.tool import Terminate, ToolCollection
from backend.tool.browser_use_tool import BrowserUseTool
from backend.tool.file_saver import FileSaver
from backend.tool.google_search import GoogleSearch
from backend.tool.python_execute import PythonExecute


class Manus(ToolCallAgent):
    """
    A versatile general-purpose agent that uses planning to solve various tasks.

    This agent extends PlanningAgent with a comprehensive set of tools and capabilities,
    including Python execution, web browsing, file operations, and information retrieval
    to handle a wide range of user requests.
    """

    name: str = "Manus"
    description: str = (
        "A versatile agent that can solve various tasks using multiple tools"
    )

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT

    # Add general-purpose tools to the tool collection
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            PythonExecute(), GoogleSearch(), BrowserUseTool(), FileSaver(), Terminate()
        )
    )
