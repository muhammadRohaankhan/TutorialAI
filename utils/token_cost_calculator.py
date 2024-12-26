import math
import tiktoken
from utils.openai_helper import get_openai_client

MODEL_PRICING = {
    "gpt-4o-mini": {
        "input_cost_per_million_tokens": 0.150,
        "cached_input_cost_per_million_tokens": 0.075,
        "output_cost_per_million_tokens": 0.600
    },
    "gpt-4o-mini-2024-07-18": {
        "input_cost_per_million_tokens": 0.150,
        "cached_input_cost_per_million_tokens": 0.075,
        "output_cost_per_million_tokens": 0.600
    },
    "gpt-4o-mini-audio-preview": {
        "Text": {
            "input_cost_per_million_tokens": 0.150,
            "output_cost_per_million_tokens": 0.600
        },
        "Audio": {
            "input_cost_per_million_tokens": 10.000,
            "output_cost_per_million_tokens": 20.000
        }
    },
    "gpt-4o-mini-audio-preview-2024-12-17": {
        "Text": {
            "input_cost_per_million_tokens": 0.150,
            "output_cost_per_million_tokens": 0.600
        },
        "Audio": {
            "input_cost_per_million_tokens": 10.000,
            "output_cost_per_million_tokens": 20.000
        }
    },
    "o1": {
        "input_cost_per_million_tokens": 15.00,
        "cached_input_cost_per_million_tokens": 7.50,
        "output_cost_per_million_tokens": 60.00
    },
    "o1-2024-12-17": {
        "input_cost_per_million_tokens": 15.00,
        "cached_input_cost_per_million_tokens": 7.50,
        "output_cost_per_million_tokens": 60.00
    },
    "o1-preview": {
        "input_cost_per_million_tokens": 15.00,
        "cached_input_cost_per_million_tokens": 7.50,
        "output_cost_per_million_tokens": 60.00
    },
    "o1-preview-2024-09-12": {
        "input_cost_per_million_tokens": 15.00,
        "cached_input_cost_per_million_tokens": 7.50,
        "output_cost_per_million_tokens": 60.00
    },
    "gpt-4o": {
        "input_cost_per_million_tokens": 2.50,
        "cached_input_cost_per_million_tokens": 1.25,
        "output_cost_per_million_tokens": 10.00
    },
    "gpt-4o-2024-11-20": {
        "input_cost_per_million_tokens": 2.50,
        "cached_input_cost_per_million_tokens": 1.25,
        "output_cost_per_million_tokens": 10.00
    },
    "gpt-4o-2024-08-06": {
        "input_cost_per_million_tokens": 2.50,
        "cached_input_cost_per_million_tokens": 1.25,
        "output_cost_per_million_tokens": 10.00
    },
    "gpt-4o-audio-preview": {
        "Text": {
            "input_cost_per_million_tokens": 2.50,
            "output_cost_per_million_tokens": 10.00
        },
        "Audio": {
            "input_cost_per_million_tokens": 100.00,
            "output_cost_per_million_tokens": 200.00
        }
    },
    "gpt-4o-audio-preview-2024-12-17": {
        "Text": {
            "input_cost_per_million_tokens": 2.50,
            "output_cost_per_million_tokens": 10.00
        },
        "Audio": {
            "input_cost_per_million_tokens": 40.00,
            "output_cost_per_million_tokens": 80.00
        }
    },
    "gpt-4o-audio-preview-2024-10-01": {
        "Text": {
            "input_cost_per_million_tokens": 2.50,
            "output_cost_per_million_tokens": 10.00
        },
        "Audio": {
            "input_cost_per_million_tokens": 100.00,
            "output_cost_per_million_tokens": 200.00
        }
    },
    "gpt-4o-2024-05-13": {
        "input_cost_per_million_tokens": 5.00,
        "cached_input_cost_per_million_tokens": 2.50,
        "output_cost_per_million_tokens": 15.00,
        "cached_output_cost_per_million_tokens": 7.50
    }
}

IMAGE_COST = 0.019125  

def get_token_count(text, model="gpt-4o-mini"):
    """
    Use tiktoken to count the number of tokens for a given text and model.
    """
    supported_models = [
        "gpt-4o-mini",
        "gpt-4o-mini-2024-07-18",
        "gpt-4o-mini-audio-preview",
        "gpt-4o-mini-audio-preview-2024-12-17",
        "o1",
        "o1-2024-12-17",
        "o1-preview",
        "o1-preview-2024-09-12",
        "gpt-4o",
        "gpt-4o-2024-11-20",
        "gpt-4o-2024-08-06",
        "gpt-4o-audio-preview",
        "gpt-4o-audio-preview-2024-12-17",
        "gpt-4o-audio-preview-2024-10-01",
        "gpt-4o-2024-05-13"
    ]
    
    if model not in supported_models:
        raise ValueError(f"Unsupported model: {model}")
    
    encoding = tiktoken.get_encoding("cl100k_base")
    
    tokens = encoding.encode(text)
    return len(tokens)

def get_model_text_pricing(model):
    """
    Retrieves the text-based input and output cost per million tokens for the specified model.
    """
    model_pricing = MODEL_PRICING.get(model)
    if not model_pricing:
        raise ValueError(f"Model '{model}' not found in pricing information.")
    
    if "Text" in model_pricing:
        text_pricing = model_pricing["Text"]
        input_cost = text_pricing.get("input_cost_per_million_tokens")
        output_cost = text_pricing.get("output_cost_per_million_tokens")
    else:
        input_cost = model_pricing.get("input_cost_per_million_tokens")
        output_cost = model_pricing.get("output_cost_per_million_tokens")
    
    if input_cost is None or output_cost is None:
        raise ValueError(f"Pricing information incomplete for model '{model}'.")
    
    return input_cost, output_cost

def calculate_tokens_and_cost(instructions, row_data, image_contents=None, model="gpt-4o-mini"):
    """
    Calculates the total tokens and associated costs for the given instructions and row data.
    
    Parameters:
    - instructions (str): The instruction text.
    - row_data (dict): The row data containing various fields.
    - image_contents (list, optional): List of image dictionaries. Each dictionary should have 'url' and 'column_name'.
    - model (str): The model name to use for pricing.
    
    Returns:
    dict: A dictionary containing detailed token and cost information.
    """
    instruction_tokens = get_token_count(instructions, model)
    
    text_content = (
        f"Main Statements: {row_data.get('Main Statements', '')}, "
        f"Child Statement: {row_data.get('child statement', '')}, "
        f"Question: {row_data.get('Question', '')}, "
        f"Individual Marks: {row_data.get('Individual Marks', '')}, "
        f"Student Answer: {row_data.get('Student Answer', '')}, "
        f"Marking Scheme: {row_data.get('Marking Scheme', '')}"
    )
    
    text_tokens = get_token_count(text_content, model)
    
    total_input_tokens = instruction_tokens + text_tokens
    
    image_cost = 0
    if image_contents:
        image_cost = len(image_contents) * IMAGE_COST
    
    input_cost_per_million, output_cost_per_million = get_model_text_pricing(model)
    
    input_token_cost = (total_input_tokens / 1_000_000) * input_cost_per_million
    output_token_cost = (total_input_tokens / 1_000_000) * output_cost_per_million
    
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
