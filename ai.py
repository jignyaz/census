import os
import re
import time
import anthropic
import google.generativeai as genai
from dotenv import load_dotenv
import database

# Load environment variables
load_dotenv()

def call_ai(system_prompt: str, user_message: str) -> str:
    """Calls Gemini API if GEMINI_API_KEY is configured, or Anthropic API if ANTHROPIC_API_KEY is configured."""
    load_dotenv(override=True)
    g_key = os.getenv("GEMINI_API_KEY")
    a_key = os.getenv("ANTHROPIC_API_KEY")
    
    if g_key and g_key.strip() != "" and g_key != "your_gemini_api_key_here":
        # Configure and call Google Gemini API with retry for rate limits
        genai.configure(api_key=g_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_prompt
        )
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = model.generate_content(user_message)
                return response.text
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "quota" in err_str.lower() or "rate" in err_str.lower():
                    # Parse retry delay from error message if available
                    delay_match = re.search(r'retry in (\d+(?:\.\d+)?)', err_str, re.IGNORECASE)
                    wait_time = float(delay_match.group(1)) if delay_match else (15 * (attempt + 1))
                    wait_time = min(wait_time + 2, 60)  # Add buffer, cap at 60s
                    
                    if attempt < max_retries - 1:
                        print(f"Rate limited (attempt {attempt + 1}/{max_retries}). Waiting {wait_time:.0f}s...")
                        time.sleep(wait_time)
                    else:
                        raise Exception(
                            f"Gemini API rate limit exceeded after {max_retries} retries. "
                            f"The free tier allows only 20 requests/day. "
                            f"Please wait a minute and try again, or upgrade your Gemini API plan."
                        )
                else:
                    raise
    elif a_key and a_key.strip() != "" and a_key != "your_api_key_here":
        # Configure and call Anthropic Claude API
        client = anthropic.Anthropic(api_key=a_key)
        models = ["claude-sonnet-4-20250514", "claude-3-5-sonnet-latest", "claude-3-5-sonnet-20241022"]
        last_err = None
        
        for model_name in models:
            try:
                message = client.messages.create(
                    model=model_name,
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_message}
                    ]
                )
                return message.content[0].text
            except Exception as e:
                last_err = e
                print(f"Failed to use model {model_name}: {e}. Retrying fallback...")
        raise last_err
    else:
        raise ValueError("No valid API keys found. Please set GEMINI_API_KEY or ANTHROPIC_API_KEY in your .env file.")

def clean_sql(sql_str: str) -> str:
    """Cleans up markdown, backticks, and newlines from the SQL response."""
    cleaned = sql_str.strip()
    
    # Remove markdown code block syntax if present
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
        
    # Remove single or double backticks surrounding the statement
    cleaned = cleaned.strip("`").strip()
    
    # Clean newlines and simplify whitespace
    cleaned = cleaned.replace("\n", " ").replace("\r", "")
    while "  " in cleaned:
        cleaned = cleaned.replace("  ", " ")
        
    return cleaned.strip()

def ask_question(question: str) -> str:
    """End-to-end question handling: SQL generation, execution, and humanization."""
    load_dotenv(override=True)
    g_key = os.getenv("GEMINI_API_KEY")
    a_key = os.getenv("ANTHROPIC_API_KEY")
    
    has_gemini = g_key and g_key.strip() != "" and g_key != "your_gemini_api_key_here"
    has_anthropic = a_key and a_key.strip() != "" and a_key != "your_api_key_here"
    
    if not has_gemini and not has_anthropic:
        return "Error: Neither GEMINI_API_KEY nor ANTHROPIC_API_KEY is configured in the .env file. Please add a valid key to proceed."
        
    # System prompt for SQL generation
    system_prompt_sql = (
        "You are a census data analyst for an Indian government "
        "socioeconomic survey. You have access to a SQLite database "
        "called census.db with one table called 'census' with these "
        "exact columns:\n"
        "id, census_house_number, floor_material, wall_material, "
        "ceiling_material, building_usage, building_condition, "
        "number_of_people, head_of_family_name, gender, rooms, "
        "married_pairs, drinking_water_source, water_source_location, "
        "light_source, sanitation_facilities, rest_room, sewage_flow, "
        "bathing_facilities, cooking_gas, cooking_fuel, radio, tv, "
        "internet, laptop_computer, transportation, primary_food, "
        "phone_number, registered_at.\n\n"
        "Respond ONLY with a valid SQLite SQL query. "
        "No explanation. No markdown. No backticks. "
        "Just the raw SQL query on one line."
    )
    
    # Step 1: Generate SQL query
    try:
        raw_sql = call_ai(system_prompt_sql, question)
        cleaned_sql = clean_sql(raw_sql)
        print(f"Generated SQL: {cleaned_sql}")
    except Exception as e:
        return f"AI Error (SQL Generation): Failed to communicate with AI API. Details: {e}"
        
    # Step 2: Run query against SQLite database
    try:
        result = database.run_query(cleaned_sql)
        print(f"SQL Result: {result}")
    except Exception as e:
        return f"Database Error: I executed the SQL query `{cleaned_sql}` but it failed. Error: {e}"
        
    # Step 3: Humanize query result
    system_prompt_human = "You are a helpful socioeconomic survey analyst for the Indian government."
    user_message_human = (
        f"The user asked: {question}\n"
        f"The SQL query result was: {result}\n"
        "Write a clear friendly human-readable answer in 1-2 sentences. "
        "Be specific with numbers. If result is empty say no records found."
    )
    
    try:
        human_answer = call_ai(system_prompt_human, user_message_human)
        return human_answer.strip()
    except Exception as e:
        return f"AI Error (Humanizing): Failed to convert the result into a human message. Details: {e}. Raw Database Result: {result}"
