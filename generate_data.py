"""
Census Data Generator — 300 Realistic Rows
Generates synthetic but realistic Indian census data for fine-tuning Llama 3.1.
Output: census_data.csv & census_data.json
"""

import csv
import json
import random
import os

random.seed(42)  # Reproducible results

# ===== Realistic Name Pools =====
MALE_FIRST = [
    "Ravi", "Suresh", "Ramesh", "Venkatesh", "Srinivas", "Gopal", "Manoj", "Anil",
    "Vijay", "Rajesh", "Prakash", "Naveen", "Satish", "Mahesh", "Ganesh", "Kishore",
    "Harish", "Dinesh", "Mohan", "Kiran", "Ashok", "Deepak", "Santosh", "Naresh",
    "Balaji", "Sekhar", "Chandra", "Murali", "Pavan", "Srikanth", "Venu", "Prasad",
    "Sai", "Hari", "Raghu", "Jagadish", "Anand", "Krishna", "Shiva", "Lakshman",
    "Bhaskar", "Nagaraj", "Raju", "Ramana", "Subba", "Apparao", "Satyam", "Madhu",
    "Yellaiah", "Mallesh", "Pochaiah", "Narsimha", "Lingaiah", "Peddi", "Thirupathi",
]

FEMALE_FIRST = [
    "Lakshmi", "Saraswathi", "Padma", "Anitha", "Sunitha", "Kavitha", "Radha",
    "Sujatha", "Vijaya", "Manga", "Rani", "Devi", "Savithri", "Parvathi", "Geetha",
    "Bharathi", "Jyothi", "Kumari", "Nirmala", "Vani", "Priya", "Swathi", "Divya",
    "Rajeshwari", "Nagamani", "Shanthi", "Vasantha", "Aruna", "Pushpa", "Sridevi",
    "Kalyani", "Renuka", "Anjali", "Bhavani", "Tulasi", "Madhavi", "Ramadevi",
    "Sarojini", "Susheela", "Mahalakshmi", "Yellamma", "Pochamma", "Laxmamma",
]

LAST_NAMES = [
    "Reddy", "Naidu", "Rao", "Sharma", "Kumar", "Gupta", "Yadav", "Singh",
    "Patil", "Goud", "Chary", "Setty", "Mudiraj", "Kamma", "Velama", "Padmashali",
    "Munnuru", "Kapu", "Balija", "Boya", "Lambadi", "Madiga", "Mala", "Chakali",
    "Mangali", "Kuruma", "Golla", "Uppara", "Kummari", "Vaddera", "Erukala",
    "Thogata", "Jangam", "Budiga", "Dasari", "Nayak", "Rathod", "Pawar",
]

# ===== Option Pools (matching website questions) =====
FLOOR_MATERIALS = ['Soil/Mud', 'Tiles/Bricks', 'Stone-slab flooring', 'Stones', 'Cement', 'Mosaic / Vitrified tiles', 'Other materials']
FLOOR_WEIGHTS   = [15, 20, 5, 8, 30, 18, 4]

WALL_MATERIALS = ['Soil/Mud', 'Tiles/Bricks', 'Stone-slab flooring', 'Stones', 'Cement', 'Mosaic / Vitrified tiles', 'Other materials']
WALL_WEIGHTS   = [12, 28, 3, 10, 25, 18, 4]

CEILING_MATERIALS = ['Polythene', 'Mud', 'Penkulu', 'Burnt Bricks', 'Stone', 'Asbestos Sheets', 'Concrete', 'Other materials']
CEILING_WEIGHTS   = [3, 8, 10, 5, 6, 20, 40, 8]

BUILDING_USAGE = ['House', 'Rent', 'Shop', 'School', 'Hotel', 'Hospital', 'Devotional Place', 'Empty']
USAGE_WEIGHTS  = [50, 15, 12, 4, 3, 2, 5, 9]

BUILDING_CONDITION = ['Livable', 'Non Livable', 'Broken']
CONDITION_WEIGHTS  = [72, 18, 10]

GENDER_OPTIONS = ['Male', 'Female', 'N/A']
GENDER_WEIGHTS = [55, 43, 2]

WATER_SOURCES = ['Purified water', 'Well', 'Hand pump', 'Lake', 'River', 'Packaged water', 'Other sources']
WATER_WEIGHTS = [18, 22, 25, 3, 5, 15, 12]

WATER_LOCATIONS = ['In premises', 'Community', 'In range of 500m']
WATER_LOC_WEIGHTS = [45, 30, 25]

LIGHT_SOURCES = ['Electricity', 'Kerosene', 'Solar power', 'Any oil', 'No sunlight', 'Any other']
LIGHT_WEIGHTS = [65, 10, 12, 5, 3, 5]

SANITATION = ['Usage only for family', 'Shared by community', 'Walkable distance']
SANIT_WEIGHTS = [50, 28, 22]

RESTROOM = ['Yes', 'No']
RESTROOM_WEIGHTS = [62, 38]

SEWAGE = ['Septic tank', 'Rings', 'N/A']
SEWAGE_WEIGHTS = [45, 30, 25]

BATHING = ['Bathroom', 'No roof', 'N/A']
BATHING_WEIGHTS = [55, 25, 20]

COOKING_GAS = ['LPG/PNG', 'N/A']
GAS_WEIGHTS = [68, 32]

COOKING_FUEL = ['Wood', 'Grass (dry)', 'Cow dung cakes', 'Kerosene', 'Electricity', 'Solar cooker', 'Biogas']
FUEL_WEIGHTS = [30, 8, 15, 10, 20, 5, 12]

RADIO_TRANS = ['Radio', 'Smartphone', 'N/A']
RADIO_WEIGHTS = [10, 70, 20]

TV_OPTIONS = ['Doordarshan', 'DTH connection', 'Cable connection', 'Other', 'N/A']
TV_WEIGHTS = [12, 35, 25, 8, 20]

INTERNET = ['Yes', 'No']
INTERNET_WEIGHTS = [55, 45]

LAPTOP = ['Yes', 'No']
LAPTOP_WEIGHTS = [30, 70]

TRANSPORT = ['Cycle', 'Bike', 'Car', 'ATB', 'N/A']
TRANSPORT_WEIGHTS = [15, 35, 12, 8, 30]

FOOD_ITEMS = [
    'Rice', 'Wheat', 'Rice and Dal', 'Roti and Dal', 'Millets', 'Rice and Vegetables',
    'Jowar Roti', 'Bajra Roti', 'Rice and Fish', 'Rice and Sambar', 'Chapati',
    'Rice and Curry', 'Pulao', 'Idli and Rice', 'Ragi Mudde', 'Rice and Rasam',
    'Dal Rice', 'Khichdi', 'Rice and Pickle', 'Wheat Roti and Sabzi',
]
FOOD_WEIGHTS = [25, 10, 12, 8, 5, 8, 4, 3, 3, 5, 4, 5, 2, 2, 1, 1, 2, 1, 2, 2]


def weighted_choice(options, weights):
    return random.choices(options, weights=weights, k=1)[0]


def generate_phone():
    """Generate realistic 10-digit Indian phone number starting with 6-9."""
    prefix = random.choice(['6', '7', '8', '9'])
    rest = ''.join([str(random.randint(0, 9)) for _ in range(9)])
    return prefix + rest


def generate_name(gender):
    """Generate a realistic Indian full name based on gender."""
    if gender == 'Male':
        first = random.choice(MALE_FIRST)
    elif gender == 'Female':
        first = random.choice(FEMALE_FIRST)
    else:
        first = random.choice(MALE_FIRST + FEMALE_FIRST)
    last = random.choice(LAST_NAMES)
    return f"{first} {last}"


def generate_row(house_num):
    """Generate a single census row with realistic correlations."""
    gender = weighted_choice(GENDER_OPTIONS, GENDER_WEIGHTS)
    name = generate_name(gender)
    
    building_usage = weighted_choice(BUILDING_USAGE, USAGE_WEIGHTS)
    building_condition = weighted_choice(BUILDING_CONDITION, CONDITION_WEIGHTS)
    
    # Correlations: broken buildings more likely to be empty
    if building_condition == 'Broken':
        if random.random() < 0.6:
            building_usage = 'Empty'
    
    # Correlations: empty buildings have fewer people
    if building_usage == 'Empty':
        num_people = 0
        married_pairs = 0
        rooms = random.randint(1, 3)
    elif building_usage in ['Shop', 'Hotel', 'Hospital', 'Devotional Place', 'School']:
        num_people = random.randint(1, 8)
        married_pairs = 0
        rooms = random.randint(1, 6)
    else:
        num_people = random.randint(1, 12)
        married_pairs = max(0, min(num_people // 3, random.randint(0, 4)))
        rooms = random.randint(1, max(2, num_people // 2 + 1))
    
    # Floor/Wall/Ceiling correlations with building condition
    if building_condition == 'Livable':
        floor = weighted_choice(FLOOR_MATERIALS, [8, 22, 5, 6, 30, 25, 4])
        wall = weighted_choice(WALL_MATERIALS, [6, 30, 3, 8, 28, 22, 3])
        ceiling = weighted_choice(CEILING_MATERIALS, [1, 4, 6, 5, 4, 18, 52, 10])
    elif building_condition == 'Non Livable':
        floor = weighted_choice(FLOOR_MATERIALS, [30, 18, 8, 15, 20, 5, 4])
        wall = weighted_choice(WALL_MATERIALS, [28, 22, 5, 18, 18, 5, 4])
        ceiling = weighted_choice(CEILING_MATERIALS, [8, 18, 20, 8, 12, 22, 8, 4])
    else:  # Broken
        floor = weighted_choice(FLOOR_MATERIALS, [40, 15, 5, 20, 12, 3, 5])
        wall = weighted_choice(WALL_MATERIALS, [35, 18, 3, 22, 12, 5, 5])
        ceiling = weighted_choice(CEILING_MATERIALS, [10, 25, 22, 5, 15, 15, 3, 5])
    
    # Water & sanitation correlations
    water_source = weighted_choice(WATER_SOURCES, WATER_WEIGHTS)
    water_location = weighted_choice(WATER_LOCATIONS, WATER_LOC_WEIGHTS)
    
    light = weighted_choice(LIGHT_SOURCES, LIGHT_WEIGHTS)
    sanitation = weighted_choice(SANITATION, SANIT_WEIGHTS)
    restroom = weighted_choice(RESTROOM, RESTROOM_WEIGHTS)
    sewage = weighted_choice(SEWAGE, SEWAGE_WEIGHTS)
    bathing = weighted_choice(BATHING, BATHING_WEIGHTS)
    
    # Cooking correlations
    cooking_gas = weighted_choice(COOKING_GAS, GAS_WEIGHTS)
    if cooking_gas == 'LPG/PNG':
        cooking_fuel = weighted_choice(COOKING_FUEL, [5, 2, 3, 5, 40, 15, 30])
    else:
        cooking_fuel = weighted_choice(COOKING_FUEL, [40, 15, 25, 8, 2, 3, 7])
    
    # Technology correlations
    smartphone = weighted_choice(RADIO_TRANS, RADIO_WEIGHTS)
    
    if smartphone == 'Smartphone':
        internet = weighted_choice(['Yes', 'No'], [75, 25])
        tv = weighted_choice(TV_OPTIONS, [5, 40, 30, 10, 15])
    else:
        internet = weighted_choice(['Yes', 'No'], [20, 80])
        tv = weighted_choice(TV_OPTIONS, [20, 20, 15, 5, 40])
    
    laptop = weighted_choice(LAPTOP, LAPTOP_WEIGHTS)
    if internet == 'No':
        laptop = weighted_choice(['Yes', 'No'], [10, 90])
    
    transport = weighted_choice(TRANSPORT, TRANSPORT_WEIGHTS)
    food = weighted_choice(FOOD_ITEMS, FOOD_WEIGHTS)
    phone = generate_phone()
    
    # Empty / non-residential adjustments
    if building_usage == 'Empty':
        phone = generate_phone()  # still generate for records
        name = "N/A"
        gender = "N/A"
        restroom = random.choice(['Yes', 'No'])
        sewage = 'N/A'
        cooking_gas = 'N/A'
        cooking_fuel = random.choice(['N/A', 'Wood'])
        smartphone = 'N/A'
        tv = 'N/A'
        internet = 'No'
        laptop = 'No'
        transport = 'N/A'
        food = 'N/A'
    
    return {
        'census_house_number': house_num,
        'floor_material': floor,
        'wall_material': wall,
        'ceiling_material': ceiling,
        'building_usage': building_usage,
        'building_condition': building_condition,
        'num_people': num_people,
        'head_of_family': name,
        'gender': gender,
        'rooms': rooms,
        'married_pairs': married_pairs,
        'water_source': water_source,
        'water_location': water_location,
        'light_source': light,
        'sanitation': sanitation,
        'restroom': restroom,
        'sewage': sewage,
        'bathing': bathing,
        'cooking_gas': cooking_gas,
        'cooking_fuel': cooking_fuel,
        'radio_transmitter': smartphone,
        'tv': tv,
        'internet': internet,
        'laptop_computer': laptop,
        'transportation': transport,
        'primary_food': food,
        'phone_number': phone,
    }


def main():
    print("🏘️  Generating 300 realistic census records...\n")
    
    # Column labels for CSV header
    HEADERS = [
        'Census House Number', 'Main Material of Floor', 'Main Material of Walls',
        'Main Material of Ceiling', 'Building Usage', 'Condition of Building',
        'Number of People', 'Name of Head of Family', 'Gender',
        'Rooms in House', 'Married Pairs', 'Drinking Water Source',
        'Location of Water Sources', 'Light Source', 'Sanitation Facilities',
        'Rest Room', 'Sewage Flow', 'In Premises Bathing Facilities',
        'Cooking Gas', 'Cooking Fuel', 'Radio Transmitter', 'TV',
        'Internet Connection', 'Laptop / Computer', 'Transportation Mode',
        'Primary Consumed Food', 'Phone Number',
    ]
    
    KEY_ORDER = [
        'census_house_number', 'floor_material', 'wall_material', 'ceiling_material',
        'building_usage', 'building_condition', 'num_people', 'head_of_family',
        'gender', 'rooms', 'married_pairs', 'water_source', 'water_location',
        'light_source', 'sanitation', 'restroom', 'sewage', 'bathing',
        'cooking_gas', 'cooking_fuel', 'radio_transmitter', 'tv',
        'internet', 'laptop_computer', 'transportation', 'primary_food', 'phone_number',
    ]
    
    # Generate 300 rows
    rows = []
    house_numbers = list(range(101, 401))  # House numbers 101–400
    
    for i, hnum in enumerate(house_numbers):
        row = generate_row(hnum)
        rows.append(row)
    
    # ===== Save as CSV =====
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'census_data.csv')
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        for row in rows:
            writer.writerow([row[k] for k in KEY_ORDER])
    
    print(f"✅ CSV saved: {csv_path}")
    
    # ===== Save as JSON =====
    json_path = os.path.join(script_dir, 'census_data.json')
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    
    print(f"✅ JSON saved: {json_path}")
    
    # ===== Save as JSONL (for fine-tuning) =====
    jsonl_path = os.path.join(script_dir, 'census_finetune.jsonl')
    
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for row in rows:
            # Create instruction-style entries for fine-tuning
            prompts = generate_finetune_pairs(row, HEADERS, KEY_ORDER)
            for pair in prompts:
                f.write(json.dumps(pair, ensure_ascii=False) + '\n')
    
    print(f"✅ JSONL (fine-tune) saved: {jsonl_path}")
    
    # ===== Stats Summary =====
    print(f"\n📊 Data Summary:")
    print(f"   Total records: {len(rows)}")
    print(f"   House numbers: {rows[0]['census_house_number']} – {rows[-1]['census_house_number']}")
    
    # Count distributions
    usage_counts = {}
    for r in rows:
        u = r['building_usage']
        usage_counts[u] = usage_counts.get(u, 0) + 1
    print(f"   Building usage distribution:")
    for k, v in sorted(usage_counts.items(), key=lambda x: -x[1]):
        print(f"     {k}: {v} ({v/len(rows)*100:.1f}%)")
    
    cond_counts = {}
    for r in rows:
        c = r['building_condition']
        cond_counts[c] = cond_counts.get(c, 0) + 1
    print(f"   Building condition distribution:")
    for k, v in sorted(cond_counts.items(), key=lambda x: -x[1]):
        print(f"     {k}: {v} ({v/len(rows)*100:.1f}%)")
    
    print(f"\n🎯 Files ready for Llama 3.1 fine-tuning!")


def generate_finetune_pairs(row, headers, key_order):
    """Generate instruction/response pairs for chatbot fine-tuning."""
    pairs = []
    
    hnum = row['census_house_number']
    name = row['head_of_family']
    
    # 1. Full record lookup
    details = "\n".join([f"- {headers[i]}: {row[key_order[i]]}" for i in range(len(headers))])
    pairs.append({
        "instruction": f"Show me the census details for house number {hnum}.",
        "input": "",
        "output": f"Here are the census details for house number {hnum}:\n{details}"
    })
    
    # 2. Specific field queries
    field_queries = [
        ("building_usage", f"What is the building usage for house number {hnum}?",
         f"House number {hnum} is used as: {row['building_usage']}."),
        ("building_condition", f"What is the condition of house number {hnum}?",
         f"The condition of house number {hnum} is: {row['building_condition']}."),
        ("floor_material", f"What material is the floor made of in house {hnum}?",
         f"The floor of house {hnum} is made of {row['floor_material']}."),
        ("water_source", f"What is the drinking water source for house {hnum}?",
         f"The drinking water source for house {hnum} is {row['water_source']}, located {row['water_location'].lower()}."),
        ("num_people", f"How many people live in house number {hnum}?",
         f"There are {row['num_people']} people living in house number {hnum}."),
        ("cooking_fuel", f"What cooking fuel does house {hnum} use?",
         f"House {hnum} uses {row['cooking_fuel']} as cooking fuel" +
         (f" with {row['cooking_gas']} gas." if row['cooking_gas'] != 'N/A' else ".")),
        ("internet", f"Does house {hnum} have internet connection?",
         f"{'Yes' if row['internet'] == 'Yes' else 'No'}, house {hnum} {'has' if row['internet'] == 'Yes' else 'does not have'} internet connection."),
    ]
    
    # Pick 3 random field queries per record to avoid too much data
    selected = random.sample(field_queries, min(3, len(field_queries)))
    for _, q, a in selected:
        pairs.append({"instruction": q, "input": "", "output": a})
    
    # 3. Head of family query
    if name != 'N/A':
        pairs.append({
            "instruction": f"Who is the head of family at house {hnum}?",
            "input": "",
            "output": f"The head of family at house {hnum} is {name} ({row['gender']})."
        })
    
    return pairs


if __name__ == '__main__':
    main()
