from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import database
import ai

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup: initialize database
    print("Initializing database...")
    database.init_db()
    yield
    # On shutdown: no-op

app = FastAPI(
    title="Census Survey System API",
    description="Backend API for the Census Survey System and AI Assistant",
    lifespan=lifespan
)

# CORS open for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files and HTML pages
app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/js", StaticFiles(directory="js"), name="js")

@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.get("/chat.html")
async def read_chat():
    return FileResponse("chat.html")

@app.get("/records.html")
async def read_records():
    return FileResponse("records.html")


@app.post("/submit")
async def submit_record(data: dict = Body(...)):
    """Accepts JSON with all census fields, validates them, and inserts them into the DB."""
    required_keys = [
        "census_house_number", "floor_material", "wall_material", "ceiling_material",
        "building_usage", "building_condition", "number_of_people", "head_of_family_name",
        "gender", "rooms", "married_pairs", "drinking_water_source", "water_source_location",
        "light_source", "sanitation_facilities", "rest_room", "sewage_flow", "bathing_facilities",
        "cooking_gas", "cooking_fuel", "radio", "tv", "internet", "laptop_computer",
        "transportation", "primary_food", "phone_number"
    ]
    
    # Check for missing keys
    missing = [k for k in required_keys if k not in data]
    if missing:
        raise HTTPException(
            status_code=400, 
            detail=f"Validation failed. Missing required fields: {', '.join(missing)}"
        )
    
    # Validate that none of the required string fields are empty or None (excluding head_of_family_name if usage is Empty)
    is_empty_building = data.get("building_usage") == "Empty"
    for key in required_keys:
        val = data.get(key)
        if key == "head_of_family_name" and is_empty_building:
            continue
        if val is None or str(val).strip() == "":
            raise HTTPException(
                status_code=400,
                detail=f"Validation failed. Field '{key}' cannot be empty."
            )
            
    # Validate phone number
    phone = str(data["phone_number"]).strip()
    if not phone.isdigit() or len(phone) != 10:
        raise HTTPException(
            status_code=400, 
            detail="Validation failed. Phone number must be exactly 10 digits."
        )
        
    # Validate integer fields
    for int_field in ["number_of_people", "rooms", "married_pairs"]:
        try:
            int(data[int_field])
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400, 
                detail=f"Validation failed. Field '{int_field}' must be a valid integer."
            )
            
    try:
        database.insert_record(data)
        return {"status": "success", "message": "Census record saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.post("/ask")
async def ask_question(payload: dict = Body(...)):
    """Receives natural language question, processes it using AI, and returns the response."""
    question = payload.get("question")
    if not question or str(question).strip() == "":
        raise HTTPException(status_code=400, detail="Missing required field 'question'")
        
    answer = ai.ask_question(question)
    return {"answer": answer}

@app.get("/stats")
async def get_stats():
    """Returns database summary stats."""
    return database.get_stats()

@app.get("/records")
async def get_records():
    """Returns all database records (latest first) for admin view."""
    try:
        records = database.run_query("SELECT * FROM census ORDER BY id DESC")
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch records: {e}")

@app.post("/run-sql")
async def run_sql(payload: dict = Body(...)):
    """Runs a read-only SQL query on the database for the client-side AI assistant."""
    sql = payload.get("sql")
    if not sql or str(sql).strip() == "":
        raise HTTPException(status_code=400, detail="Missing required field 'sql'")
        
    cleaned_sql = str(sql).strip()
    # Basic check to reject database modification queries
    forbidden_keywords = ["insert ", "update ", "delete ", "drop ", "alter ", "create ", "replace ", "truncate "]
    if any(k in cleaned_sql.lower() for k in forbidden_keywords):
        raise HTTPException(
            status_code=403,
            detail="Database modification queries are not allowed via this endpoint."
        )
        
    try:
        results = database.run_query(cleaned_sql)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SQL Execution Error: {str(e)}")

