import math
import tiktoken
from utils.openai_helper import get_openai_client

# Pricing Constants
MODEL_PRICING = {
    "gpt-4o-mini": {
        "input_cost_per_million_tokens": 0.150,  # $0.150 per million tokens
        "output_cost_per_million_tokens": 0.600  # $0.600 per million tokens
    },
    "gpt-4o-2024-08-06": {
        "input_cost_per_million_tokens": 3.750,  # $3.750 per million tokens
        "output_cost_per_million_tokens": 15.000  # $15.000 per million tokens
    }
}

# Cost for each image (assumed fixed cost)
IMAGE_COST = 0.019125  # cost per image

def get_token_count(text, model="gpt-4o-mini"):
    """
    Use tiktoken to count the number of tokens for a given text and model.
    """
    if model == "gpt-4o-mini":
        encoding = tiktoken.get_encoding("cl100k_base")  
    elif model == "gpt-4o-2024-08-06":
        encoding = tiktoken.get_encoding("cl100k_base")
    else:
        raise ValueError(f"Unsupported model: {model}")

    # Encode the text to get the token count
    tokens = encoding.encode(text)
    return len(tokens)

def calculate_tokens_and_cost(instructions, row_data, image_contents=None, model="gpt-4o-mini"):
    instruction_tokens = get_token_count(instructions, model)
    
    # Calculate tokens for text content in row_data
    text_content = f"Main Statements: {row_data.get('Main Statements', '')}, " \
                   f"Child Statement: {row_data.get('child statement', '')}, " \
                   f"Question: {row_data.get('Question', '')}, " \
                   f"Individual Marks: {row_data.get('Individual Marks', '')}, " \
                   f"Student Answer: {row_data.get('Student Answer', '')}, " \
                   f"Marking Scheme: {row_data.get('Marking Scheme', '')}"
    
    text_tokens = get_token_count(text_content, model)

    total_input_tokens = instruction_tokens + text_tokens

    image_cost = 0
    if image_contents:
        image_cost = len(image_contents) * IMAGE_COST

    model_pricing = MODEL_PRICING.get(model)
    if not model_pricing:
        raise ValueError(f"Model {model} not found in pricing information.")
    
    input_token_cost = (total_input_tokens / 1_000_000) * model_pricing["input_cost_per_million_tokens"]
    output_token_cost = (total_input_tokens / 1_000_000) * model_pricing["output_cost_per_million_tokens"]

    total_cost = input_token_cost + output_token_cost + image_cost

    return {
        "total_input_tokens": total_input_tokens,
        "total_cost": round(total_cost, 6),
        "instruction_tokens": instruction_tokens,
        "text_tokens": text_tokens,
        "image_cost": round(image_cost, 6),
        "input_token_cost": round(input_token_cost, 6),
        "output_token_cost": round(output_token_cost, 6)
    }
