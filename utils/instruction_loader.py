def load_instructions(instruction_file):
    print("Loading instructions...")
    with open(instruction_file, 'r', encoding='utf-8') as file:
        instructions = file.read().strip()
    print("Instructions loaded.")
    return instructions
