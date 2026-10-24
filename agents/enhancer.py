from langchain_core.messages import HumanMessage
from .agent_utils import LLMS, get_logger
from graph.helper_functions.prompt_utils import smart_truncate

def run_enhancer(draft: str, query: str, style: str) -> str:
    """
    Enhances the draft for style, clarity, and engagement.
    """
    logger = get_logger()
    logger.info("Executing enhancer...")

    prompt = f"""User Question: {query}

Draft:
{smart_truncate(draft, 3000)}

Please rewrite and format this answer to make it exceptionally clean, easy to understand, and pleasant to read:
1. Strict Formatting Rule: NEVER use complex markdown tables or ASCII tables. If the draft contains a table or multi-column data, ALWAYS convert it into a clean, well-spaced list with bullet points.
2. Structure:
   - Begin with a direct, warm, 1-2 sentence core answer.
   - Present all details, attributes, or steps as a clean bulleted list (e.g., • **Key Point**: Clear explanation).
   - Keep points concise, organized, and human-readable.
3. Language & Tone: Natural, conversational, and simple human language. Avoid robotic phrasing or overwhelming blocks of unorganized text.
"""

    try:
        response = LLMS['enhancer'].invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
        logger.error(f"Enhancer agent failed: {e}")
        return f"Error during enhancement: {e}"