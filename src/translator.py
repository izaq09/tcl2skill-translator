import argparse

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

1.  **Variables:**
    * TCL: `set variable_name value`  -> SKILL: `variable_name = value`
    * TCL: `$variable_name` -> SKILL: `variableName` (SKILL does not use '$' for variable access)

2.  **Standard Output:**
    * TCL: `puts "string"` -> SKILL: `printf("string\n")`

3.  **Procedures/Functions:**
    * TCL: `proc name {{args}} {{ ... }}` -> SKILL: `procedure(name(args) ... )`

4. **Localize variables in Procedures:**
    * SKILL uses `prog` to define local variables within procedures.
    # `procedure(procName(args) prog((local_variable) ... );prog);procedure`

5.  **Loops:**
    * TCL: `for {{init}} {{end_condition}} {{increment}} {{ ... }}` -> SKILL: `for(var_name start_value end_value ... )` (For loop in SKILL defines start and end values explicitly)

6.  **Mathematical Operations:**
    * TCL: `[expr $x + $y]` -> SKILL: `x + y`
    * TCL: `[expr $x * $y]` -> SKILL: `x * y`

7.  **Control Flow:**
    * TCL: `if {{condition}} {{ ... }} else {{ ... }}` -> SKILL: `if(condition then ... else ...)`

### Example 1
TCL Input:
```tcl
proc procName {{arg1 arg2}} {{
    puts "Hello, World!"
}}
```

SKILL Output:
```skill
procedure(procName(arg1 arg2)
    prog(()
        printf("%s %s\\n" arg1 arg2)
    );prog
);procedure
```

### Example 2
TCL Input:
```tcl
proc procName {{arg1 arg2}} {{
    for {{set i 0}} {{$i <= 10}} {{incr i}} {{
        puts "Iteration $i: $arg1 $arg2"
    }}
}}
```

SKILL Output:
```skill
procedure(procName(arg1 arg2)
    prog(()
        for(i 0 10
            printf("Iteration %d: %s %s\n" i arg1 arg2)
        );for
    );prog
);procedure
```

### Target Translation
TCL Input:
```tcl
{tcl_code}
```

"""


def parse_args():
    parser = argparse.ArgumentParser(description="Translate TCL file to SKILL file")
    parser.add_argument("--tcl_file", type=str, help="Path to the input TCL file")
    parser.add_argument("--skill_file", type=str, help="Path to the output SKILL file")
    return parser.parse_args()


def generate_prompt(tcl_code: str) -> str:
    """
    Generate a prompt for the translation task.

    Args:
        tcl_code (str): The TCL code to be translated.

    Returns:
        str: The generated prompt.
    """
    return ChatPromptTemplate.from_template(PROMPT_TEMPLATE).format(tcl_code=tcl_code)


def inference(prompt: str) -> str | None:
    """
    Inference function that would use a language model to translate TCL to SKILL.

    Args:
        prompt (str): The prompt containing the TCL code to be translated.

    Returns:
        str: The translated SKILL code.
    """
    logger.info("Starting inference for code generation...")

    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-05-20",
        config=types.GenerateContentConfig(
            system_instruction="You are an expert EDA (Electronic Design Automation) engineer with extensive knowledge of both TCL and Cadence SKILL programming. Your task is to translate TCL scripts into functionally equivalent SKILL code. "
        ),
        contents=prompt,
    )

    return response.text if response else None


def translate_tcl_to_skill(tcl_file: str, skill_file: str):
    """
    Translates a TCL file to a SKILL file.

    Args:
        tcl_file (str): Path to the input TCL file.
        skill_file (str): Path to the output SKILL file.
    """
    logger.info("Translating TCL to SKILL...")

    with open(tcl_file, "r") as infile, open(skill_file, "w") as outfile:
        content = infile.read()

        prompt = generate_prompt(content)

        response = inference(prompt)

        if response:
            logger.info("Translation successful. Writing to output file...")
            outfile.write(response)
        else:
            logger.error("Failed to generate SKILL code from TCL input.")


if __name__ == "__main__":
    args = parse_args()
    translate_tcl_to_skill(args.tcl_file, args.skill_file)
