import sqlite3
import os
import json

DB_FILE = "census.db"

# Exact keys in the database schema
DB_KEYS = [
    "census_house_number", "floor_material", "wall_material", "ceiling_material",
    "building_usage", "building_condition", "number_of_people", "head_of_family_name",
    "gender", "rooms", "married_pairs", "drinking_water_source", "water_source_location",
    "light_source", "sanitation_facilities", "rest_room", "sewage_flow", "bathing_facilities",
    "cooking_gas", "cooking_fuel", "radio", "tv", "internet", "laptop_computer",
    "transportation", "primary_food", "phone_number"
]

def init_db():
    """Initializes the database, creating the census table if it doesn't exist.
    If the database is empty, seeds it from census_data.json if available.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS census (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        census_house_number TEXT,
        floor_material TEXT,
        wall_material TEXT,
        ceiling_material TEXT,
        building_usage TEXT,
        building_condition TEXT,
        number_of_people INTEGER,
        head_of_family_name TEXT,
        gender TEXT,
        rooms INTEGER,
        married_pairs INTEGER,
        drinking_water_source TEXT,
        water_source_location TEXT,
        light_source TEXT,
        sanitation_facilities TEXT,
        rest_room TEXT,
        sewage_flow TEXT,
        bathing_facilities TEXT,
        cooking_gas TEXT,
        cooking_fuel TEXT,
        radio TEXT,
        tv TEXT,
        internet TEXT,
        laptop_computer TEXT,
        transportation TEXT,
        primary_food TEXT,
        phone_number TEXT,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    
    # Check if empty
    cursor.execute("SELECT COUNT(*) FROM census")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Check if census_data.json exists to seed from
        json_path = "census_data.json"
        if os.path.exists(json_path):
            print("Seeding database from census_data.json...")
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Insert records
                for row in data:
                    # Seeding mappings to match frontend options
                    floor_map = {
                        "Soil/Mud": "Mud/Dirt", "Tiles/Bricks": "Brick", "Stone-slab flooring": "Stone",
                        "Stones": "Stone", "Cement": "Cement", "Mosaic / Vitrified tiles": "Mosaic/Tile",
                        "Other materials": "Other"
                    }
                    wall_map = {
                        "Soil/Mud": "Mud", "Tiles/Bricks": "Burnt Brick", "Stone-slab flooring": "Stone",
                        "Stones": "Stone", "Cement": "Cement", "Mosaic / Vitrified tiles": "Cement",
                        "Other materials": "Other"
                    }
                    ceiling_map = {
                        "Polythene": "Plastic", "Mud": "Grass/Thatch", "Penkulu": "Tiles",
                        "Burnt Bricks": "Brick/Lime", "Stone": "Tiles", "Asbestos Sheets": "Other",
                        "Concrete": "RCC", "Other materials": "Other"
                    }
                    usage_map = {
                        "House": "Residential", "Rent": "Residential-cum-other use", "Shop": "Shop",
                        "School": "School", "Hotel": "Other", "Hospital": "Other",
                        "Devotional Place": "Other", "Empty": "Other"
                    }
                    condition_map = {
                        "Livable": "Liveable", "Non Livable": "Dilapidated", "Broken": "Dilapidated"
                    }
                    water_map = {
                        "Purified water": "Tap/Piped water", "Well": "Well", "Hand pump": "Hand pump",
                        "Lake": "River/Canal", "River": "River/Canal", "Packaged water": "Other",
                        "Other sources": "Other"
                    }
                    water_loc_map = {
                        "In premises": "Within premises", "Community": "Within 100m",
                        "In range of 500m": "100m to 500m"
                    }
                    sanitation_map = {
                        "Usage only for family": "Flush/Pour flush", "Shared by community": "Pit latrine",
                        "Walkable distance": "Open defecation"
                    }
                    sewage_map = {
                        "Septic tank": "Closed drainage", "Rings": "Open drainage", "N/A": "No drainage"
                    }
                    bathing_map = {
                        "Bathroom": "Yes", "No roof": "No", "N/A": "No"
                    }
                    gas_map = {
                        "LPG/PNG": "Yes", "N/A": "No"
                    }
                    fuel_map = {
                        "Wood": "Firewood", "Grass (dry)": "Crop residue", "Cow dung cakes": "Cow dung",
                        "Kerosene": "Kerosene", "Electricity": "Electricity", "Solar cooker": "Other",
                        "Biogas": "Biogas"
                    }
                    trans_map = {
                        "Cycle": "Bicycle", "Bike": "Motorcycle/Scooter", "Car": "Car/Jeep",
                        "ATB": "Auto/Taxi", "N/A": "Walking"
                    }
                    
                    # Food mapping helper
                    raw_food = row.get("primary_food", "")
                    if "Fish" in raw_food or "Chicken" in raw_food or "Mutton" in raw_food:
                        food_val = "Non-Vegetarian"
                    elif "Dal" in raw_food or "Vegetables" in raw_food or "Sambar" in raw_food or "Rasam" in raw_food or "Idli" in raw_food:
                        food_val = "Vegetarian"
                    elif "Veg" in raw_food:
                        food_val = "Vegetarian"
                    else:
                        food_val = "Mixed"

                    # Map from JSON keys (generate_data.py keys) to database schema keys
                    mapped_row = {
                        "census_house_number": str(row.get("census_house_number", "")),
                        "floor_material": floor_map.get(row.get("floor_material"), "Other"),
                        "wall_material": wall_map.get(row.get("wall_material"), "Other"),
                        "ceiling_material": ceiling_map.get(row.get("ceiling_material"), "Other"),
                        "building_usage": usage_map.get(row.get("building_usage"), "Other"),
                        "building_condition": condition_map.get(row.get("building_condition"), "Liveable"),
                        "number_of_people": int(row.get("num_people", 0)),
                        "head_of_family_name": row.get("head_of_family", "N/A"),
                        "gender": row.get("gender", "Other") if row.get("gender") in ["Male", "Female"] else "Other",
                        "rooms": int(row.get("rooms", 0)),
                        "married_pairs": int(row.get("married_pairs", 0)),
                        "drinking_water_source": water_map.get(row.get("water_source"), "Other"),
                        "water_source_location": water_loc_map.get(row.get("water_location"), "Within premises"),
                        "light_source": "Electricity" if row.get("light_source") == "Electricity" else ("Kerosene" if row.get("light_source") == "Kerosene" else ("Solar" if row.get("light_source") == "Solar power" else "Other")),
                        "sanitation_facilities": sanitation_map.get(row.get("sanitation"), "Other"),
                        "rest_room": row.get("restroom", "No"),
                        "sewage_flow": sewage_map.get(row.get("sewage"), "No drainage"),
                        "bathing_facilities": bathing_map.get(row.get("bathing"), "No"),
                        "cooking_gas": gas_map.get(row.get("cooking_gas"), "No"),
                        "cooking_fuel": fuel_map.get(row.get("cooking_fuel"), "Other"),
                        "radio": "Yes" if row.get("radio_transmitter") in ["Radio", "Smartphone"] else "No",
                        "tv": "Yes" if row.get("tv") in ["Doordarshan", "DTH connection", "Cable connection", "Other"] else "No",
                        "internet": row.get("internet", "No"),
                        "laptop_computer": row.get("laptop_computer", "No"),
                        "transportation": trans_map.get(row.get("transportation"), "Other"),
                        "primary_food": food_val,
                        "phone_number": row.get("phone_number", "")
                    }
                    
                    # Perform SQL insert
                    fields = [mapped_row[k] for k in DB_KEYS]
                    insert_query = f"INSERT INTO census ({', '.join(DB_KEYS)}) VALUES ({', '.join(['?'] * len(DB_KEYS))})"
                    cursor.execute(insert_query, fields)
                
                conn.commit()
                print(f"Successfully seeded {len(data)} records into the database.")
            except Exception as e:
                print(f"Error seeding database: {e}")
        else:
            print("No census_data.json found. Database left empty.")
            
    conn.close()

def insert_record(data: dict):
    """Inserts a single census record. Handles mapping and default values."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Extract values and apply type casting where needed
    record = {}
    for key in DB_KEYS:
        val = data.get(key)
        if key in ["number_of_people", "rooms", "married_pairs"]:
            try:
                record[key] = int(val) if val is not None and str(val).strip() != "" else 0
            except ValueError:
                record[key] = 0
        else:
            record[key] = str(val) if val is not None else ""
            
    fields = [record[k] for k in DB_KEYS]
    insert_query = f"INSERT INTO census ({', '.join(DB_KEYS)}) VALUES ({', '.join(['?'] * len(DB_KEYS))})"
    cursor.execute(insert_query, fields)
    conn.commit()
    conn.close()

def run_query(sql: str) -> list:
    """Executes a custom SQL query and returns list of dictionaries."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        if cursor.description:
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        else:
            conn.commit()
            return [{"status": "success", "rows_affected": cursor.rowcount}]
    except Exception as e:
        raise e
    finally:
        conn.close()

def get_stats() -> dict:
    """Computes stats: total records, today's count, gender breakdown,
    average household size, internet penetration count, tv count.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Total records
        cursor.execute("SELECT COUNT(*) as total FROM census")
        total = cursor.fetchone()["total"]
        
        # Today's count (local time check)
        cursor.execute("SELECT COUNT(*) as today FROM census WHERE date(registered_at, 'localtime') = date('now', 'localtime')")
        today = cursor.fetchone()["today"]
        
        # Average household size (average of number_of_people)
        cursor.execute("SELECT AVG(number_of_people) as avg_size FROM census")
        avg_size = cursor.fetchone()["avg_size"]
        avg_size = round(avg_size, 2) if avg_size is not None else 0
        
        # Internet penetration count
        cursor.execute("SELECT COUNT(*) as internet_count FROM census WHERE internet = 'Yes'")
        internet_count = cursor.fetchone()["internet_count"]
        internet_pct = round((internet_count / total) * 100, 2) if total > 0 else 0
        
        # TV count (where tv is not 'N/A' and not 'No')
        cursor.execute("SELECT COUNT(*) as tv_count FROM census WHERE tv != 'N/A' AND tv IS NOT NULL")
        tv_count = cursor.fetchone()["tv_count"]
        
        # Gender breakdown
        cursor.execute("SELECT gender, COUNT(*) as count FROM census GROUP BY gender")
        gender_rows = cursor.fetchall()
        gender_breakdown = {row["gender"]: row["count"] for row in gender_rows}
        
    except Exception as e:
        print(f"Error computing database stats: {e}")
        total, today, avg_size, internet_count, internet_pct, tv_count, gender_breakdown = 0, 0, 0, 0, 0, 0, {}
    finally:
        conn.close()
        
    return {
        "total_records": total,
        "todays_count": today,
        "average_household_size": avg_size,
        "internet_count": internet_count,
        "internet_pct": internet_pct,
        "tv_count": tv_count,
        "gender_breakdown": gender_breakdown
    }
