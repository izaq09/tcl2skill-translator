import argparse
import json

from google import genai
from google.genai import types
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

from utils import get_logger

logger = get_logger(__name__)

load_dotenv()

PROMPT_TEMPLATE = """
Translate the following TCL code snippets into clean, idiomatic SKILL code suitable for execution in Cadence Virtuoso. Ensure the translated code preserves the original logic and structure. Only output the SKILL code; do not include explanations or commentary.

### TCL to SKILL Syntax Reference

Please use the following conceptual mappings when translating:

{syntax_reference}

{translation_example}

### Target Translation
TCL Input:
```tcl
{tcl_code}
```

"""


def parse_args():
    """
    Parse command line arguments for the script.
    """
    parser = argparse.ArgumentParser(description="Translate TCL file to SKILL file")
    parser.add_argument("--tcl_file", type=str, help="Path to the input TCL file")
    parser.add_argument("--skill_file", type=str, help="Path to the output SKILL file")
    return parser.parse_args()


def get_syntax_reference(tcl_code: str) -> str:
    """
    Load the syntax reference from a file.

    Returns:
        str: The syntax reference content.
    """

    # Get the general syntax reference from a file
    with open("data/syntax_reference_general.txt", "r") as f:
        reference = f.read()

    # Get the specific syntax reference for the Standard Cell Placement Optimizer API
    with open("data/syntax_reference_api.json", "r") as f:
        api_reference = json.load(f)

    api_reference_list = []
    for key, value in api_reference.items():
        if key in tcl_code:
            api_reference_list += value

    if api_reference_list:
        reference += "\n**Standard Cell Placement Optimizer API**\n"
        reference += "\n".join(api_reference_list)

    return reference


def get_translation_example() -> str:
    """
    Load the translation example from a file.

    Returns:
        str: The translation example content.
    """
    with open("data/translation_example.txt", "r") as f:
        return f.read()


def generate_prompt(tcl_code: str) -> str:
    """
    Generate a prompt for the translation task.

    Args:
        tcl_code (str): The TCL code to be translated.

    Returns:
        str: The generated prompt.
    """

    return ChatPromptTemplate.from_template(PROMPT_TEMPLATE).format(
        syntax_reference=get_syntax_reference(tcl_code=tcl_code),
        translation_example=get_translation_example(),
        tcl_code=tcl_code,
    )


def inference(prompt: str) -> str | None:
    """
    Inference function that would use a language model to translate TCL to SKILL.

    Args:
        prompt (str): The prompt containing the TCL code to be translated.

    Returns:
        str: The translated SKILL code.
    """
    logger.info("Starting inference for code translation...")

    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-05-20",
        config=types.GenerateContentConfig(
            system_instruction="You are an expert EDA (Electronic Design Automation) engineer with extensive knowledge of both TCL and Cadence SKILL programming. Your task is to translate TCL scripts into functionally equivalent SKILL code without any markdown format"
        ),
        contents=prompt,
    )

    return response.text if response else None


def translate_tcl_code_to_skill_code(tcl_code: str) -> str | None:
    """
    Translates a given TCL code snippet to SKILL code.

    Args:
        tcl_code (str): The TCL code to be translated.

    Returns:
        str: The translated SKILL code.
    """
    logger.info("Translating TCL code to SKILL code...")

    prompt = generate_prompt(tcl_code)

    response_text = inference(prompt)

    if response_text:
        logger.info("Translation successful.")
        return response_text
    else:
        logger.error("Failed to generate SKILL code from TCL input.")
        return None


def translate_tcl_file_to_skill_file(tcl_file: str, skill_file: str):
    """
    Translates a TCL file to a SKILL file.

    Args:
        tcl_file (str): Path to the input TCL file.
        skill_file (str): Path to the output SKILL file.
    """
    with open(tcl_file, "r") as infile, open(skill_file, "w") as outfile:
        content = infile.read()

        response_text = translate_tcl_code_to_skill_code(tcl_code=content)

        if response_text:
            logger.info("Writing to output file...")
            outfile.write(response_text)
        else:
            logger.error("Failed to generate SKILL code from TCL input.")


if __name__ == "__main__":
    args = parse_args()
    translate_tcl_file_to_skill_file(args.tcl_file, args.skill_file)
