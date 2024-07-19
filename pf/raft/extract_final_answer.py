from promptflow import tool

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def extract_final_answer(cot_answer: str) -> str:
    """
    Extracts the final answer from the cot_answer field
    """
    return cot_answer.split("<ANSWER>: ")[-1]