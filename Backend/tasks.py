from tools import create_vector_database, setup_retriever, build_chatbot

# Task: Vectorize data
def vectorize_data(inputs):
    json_file_path = inputs.get("json_file_path")
    if not json_file_path:
        return {"error": "No JSON file path provided."}

    try:
        vector_db = create_vector_database(json_file_path)
        return {"database": vector_db}
    except Exception as e:
        return {"error": f"Vectorization error: {str(e)}"}

# Task: Design retriever
def design_retriever(inputs):
    vector_database = inputs.get("vector_database")
    if not vector_database:
        return {"error": "No vector database provided."}

    try:
        retriever = setup_retriever(vector_database)
        return {"retriever": retriever}
    except Exception as e:
        return {"error": f"Retriever design error: {str(e)}"}

# Task: Implement chatbot
def implement_chatbot(inputs):
    retriever = inputs.get("retriever")
    if not retriever:
        return {"error": "No retriever provided."}

    try:
        chatbot = build_chatbot(retriever)
        return {"chatbot": chatbot}
    except Exception as e:
        return {"error": f"Chatbot implementation error: {str(e)}"}

# Utility: Format responses
def format_responses(response, query_type):
    """
    Format the chatbot response based on query type.
    Removes markdown formatting and returns clean text.

    Args:
        response (str): The raw response from the chatbot.
        query_type (str): The type of query ('list' or 'paragraph').

    Returns:
        str: The formatted response without markdown.
    """
    # Remove markdown formatting
    clean_response = remove_markdown_formatting(response)
    
    if query_type == "list":
        return "\n".join(f"• {item.strip()}" for item in clean_response.split("\n") if item.strip())
    elif query_type == "paragraph":
        return clean_response.strip()
    return clean_response

def remove_markdown_formatting(text):
    """
    Remove common markdown formatting from text.
    
    Args:
        text (str): Text with potential markdown formatting
        
    Returns:
        str: Clean text without markdown
    """
    import re
    
    # Remove **text** or __text__
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    
    # Remove *text* or _text_
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    
    # Remove markdown headers (# ## ### etc.)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remove markdown links [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove markdown code blocks (```code```
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    
    # Remove inline code (`code`)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Convert markdown list markers to bullet points
    text = re.sub(r'^[\s]*[-*+]\s+', '• ', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '• ', text, flags=re.MULTILINE)
    
    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = text.strip()
    
    return text

def format_professional_response(response_data, is_out_of_scope=False):
    """
    Format response in a professional manner for the GenZ Marketing Bot.
    
    Args:
        response_data: The data from your knowledge base or None if out of scope
        is_out_of_scope (bool): Whether the question is outside the bot's knowledge
        
    Returns:
        str: Professional formatted response
    """
    if is_out_of_scope:
        return ("I apologize, but that question is outside my current scope of knowledge. "
                "I specialize in GenZ Marketing services, pricing, and lead generation strategies. "
                "Please feel free to ask me about our service packages, pricing, or marketing solutions.")
    
    # Format the response without markdown
    if isinstance(response_data, dict):
        # Handle structured data (like services or pricing)
        if 'services' in response_data:
            services_text = "We offer a range of services designed to enhance your LinkedIn marketing and lead generation efforts. Our key services include:\n\n"
            for service in response_data['services']:
                services_text += f"• {service['name']}: {service['description']}\n"
            services_text += "\nOur services are tailored to meet the unique needs of each client, ensuring a personalized approach to achieving your business goals."
            return services_text
            
        elif 'packages' in response_data:
            pricing_text = "Here are our service packages along with their costs:\n\n"
            for i, package in enumerate(response_data['packages'], 1):
                pricing_text += f"{i}. {package['name']}\n   - Price: {package['price']}\n\n"
            pricing_text += "Each package offers a range of services tailored to meet different business needs."
            return pricing_text
    
    # For plain text responses, clean them up
    return remove_markdown_formatting(str(response_data))
