"""
Script to enhance spend_data.csv with more suppliers, geographic diversity, and transactions.
"""
import pandas as pd
import random
from datetime import datetime, timedelta
import os

# Set seed for reproducibility
random.seed(42)

# Read existing data
existing_df = pd.read_csv('data/structured/spend_data.csv')

# Get the max supplier ID
max_supplier_id = max([int(s.replace('S', '')) for s in existing_df['Supplier_ID'].unique()])
next_supplier_id = max_supplier_id + 1

# Define regions with countries and cities
REGIONS = {
    'Americas': {
        'USA': ['New York', 'Chicago', 'Los Angeles', 'Houston', 'Seattle', 'Miami', 'Dallas', 'Boston', 'Denver', 'Phoenix'],
        'Canada': ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa'],
        'Brazil': ['Sao Paulo', 'Rio de Janeiro', 'Brasilia', 'Porto Alegre', 'Belo Horizonte'],
        'Mexico': ['Mexico City', 'Guadalajara', 'Monterrey', 'Tijuana', 'Puebla'],
        'Argentina': ['Buenos Aires', 'Cordoba', 'Rosario', 'Mendoza'],
        'Chile': ['Santiago', 'Valparaiso', 'Concepcion'],
        'Colombia': ['Bogota', 'Medellin', 'Cali', 'Barranquilla'],
        'Peru': ['Lima', 'Arequipa', 'Trujillo'],
    },
    'Europe': {
        'Germany': ['Berlin', 'Munich', 'Frankfurt', 'Hamburg', 'Dusseldorf'],
        'UK': ['London', 'Manchester', 'Birmingham', 'Edinburgh', 'Leeds'],
        'France': ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Bordeaux'],
        'Netherlands': ['Amsterdam', 'Rotterdam', 'The Hague', 'Utrecht'],
        'Italy': ['Rome', 'Milan', 'Turin', 'Florence', 'Naples'],
        'Spain': ['Madrid', 'Barcelona', 'Seville', 'Valencia', 'Bilbao'],
        'Switzerland': ['Zurich', 'Geneva', 'Basel', 'Bern'],
        'Poland': ['Warsaw', 'Krakow', 'Gdansk', 'Wroclaw'],
        'Sweden': ['Stockholm', 'Gothenburg', 'Malmo'],
        'Belgium': ['Brussels', 'Antwerp', 'Ghent'],
    },
    'APAC': {
        'China': ['Shanghai', 'Beijing', 'Shenzhen', 'Guangzhou', 'Hangzhou', 'Chengdu'],
        'Japan': ['Tokyo', 'Osaka', 'Nagoya', 'Yokohama', 'Fukuoka'],
        'India': ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad', 'Pune'],
        'South Korea': ['Seoul', 'Busan', 'Incheon', 'Daegu'],
        'Singapore': ['Singapore'],
        'Australia': ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide'],
        'Malaysia': ['Kuala Lumpur', 'Penang', 'Johor Bahru'],
        'Thailand': ['Bangkok', 'Chiang Mai', 'Phuket'],
        'Vietnam': ['Ho Chi Minh City', 'Hanoi', 'Da Nang'],
        'Indonesia': ['Jakarta', 'Surabaya', 'Bandung', 'Medan'],
        'Philippines': ['Manila', 'Cebu', 'Davao'],
        'Taiwan': ['Taipei', 'Kaohsiung', 'Taichung'],
    },
    'Middle East': {
        'UAE': ['Dubai', 'Abu Dhabi', 'Sharjah'],
        'Saudi Arabia': ['Riyadh', 'Jeddah', 'Dammam', 'Mecca'],
        'Israel': ['Tel Aviv', 'Jerusalem', 'Haifa'],
        'Qatar': ['Doha'],
        'Kuwait': ['Kuwait City'],
        'Bahrain': ['Manama'],
        'Oman': ['Muscat'],
        'Jordan': ['Amman'],
        'Turkey': ['Istanbul', 'Ankara', 'Izmir', 'Bursa'],
    },
    'Africa': {
        'South Africa': ['Johannesburg', 'Cape Town', 'Durban', 'Pretoria'],
        'Egypt': ['Cairo', 'Alexandria', 'Giza'],
        'Nigeria': ['Lagos', 'Abuja', 'Port Harcourt'],
        'Kenya': ['Nairobi', 'Mombasa'],
        'Morocco': ['Casablanca', 'Rabat', 'Marrakech', 'Tangier'],
        'Ghana': ['Accra', 'Kumasi'],
        'Ethiopia': ['Addis Ababa'],
        'Tanzania': ['Dar es Salaam', 'Dodoma'],
        'Tunisia': ['Tunis', 'Sfax'],
    }
}

# Supplier name prefixes/patterns by category
SUPPLIER_PATTERNS = {
    'Edible Oils': ['Global Oils', 'Premium Oils', 'Natural Oils', 'Organic Oils', 'Quality Oils', 'Fresh Oils', 'Pure Oils', 'Select Oils'],
    'Grains & Cereals': ['Grain Masters', 'Agri Corp', 'Farm Fresh', 'Harvest Co', 'Golden Grain', 'Prime Harvest', 'Agro Trade'],
    'Proteins': ['Meat Pro', 'Protein Source', 'Premium Meats', 'Quality Foods', 'Fresh Farms', 'Prime Cuts', 'Select Proteins'],
    'Dairy Products': ['Dairy Fresh', 'Milk Masters', 'Cream Co', 'Farm Dairy', 'Premium Dairy', 'Quality Milk', 'Fresh Dairy'],
    'Sweeteners': ['Sweet Source', 'Sugar Co', 'Sweetness Inc', 'Natural Sweet', 'Premium Sugar', 'Quality Sweet'],
    'Beverages': ['Beverage Co', 'Drink Masters', 'Refreshment Inc', 'Quality Beverages', 'Premium Drinks', 'Fresh Brew'],
    'Spices & Seasonings': ['Spice World', 'Flavor Co', 'Seasoning Masters', 'Herb Gardens', 'Exotic Spices', 'Premium Flavors'],
    'Packaging Materials': ['Pack Pro', 'Container Co', 'Packaging Solutions', 'Box Masters', 'Wrap Inc', 'Pack Tech'],
    'Hardware': ['Tech Hardware', 'Digital Systems', 'Compute Pro', 'Hardware Solutions', 'Tech Mart', 'Digital Depot'],
    'Cloud Services': ['Cloud Pro', 'Sky Services', 'Digital Cloud', 'Tech Cloud', 'Virtual Solutions', 'Cloud Masters'],
    'Software': ['Soft Solutions', 'Code Masters', 'App Pro', 'Digital Software', 'Tech Apps', 'Software Hub'],
    'Cybersecurity': ['Secure Pro', 'Cyber Shield', 'Security Masters', 'Digital Defense', 'Safe Tech', 'Guard Systems'],
    'Telecommunications': ['Telecom Pro', 'Connect Co', 'Network Solutions', 'Comm Tech', 'Signal Masters', 'Link Pro'],
    'Raw Materials - Metals': ['Metal Pro', 'Steel Masters', 'Alloy Co', 'Metal Works', 'Forge Inc', 'Prime Metals'],
    'Raw Materials - Plastics': ['Plastic Pro', 'Polymer Co', 'Resin Masters', 'Plastic Solutions', 'Poly Tech'],
    'Chemicals': ['Chem Pro', 'Chemical Solutions', 'Lab Chemicals', 'Industrial Chem', 'Specialty Chem', 'Pure Chemicals'],
    'Equipment & Machinery': ['Machine Pro', 'Equipment Masters', 'Industrial Machines', 'Tech Machinery', 'Precision Equipment'],
    'MRO Supplies': ['MRO Pro', 'Maintenance Co', 'Supply Masters', 'Industrial Supply', 'Parts Pro', 'Service Supply'],
    'Pharmaceuticals': ['Pharma Pro', 'Med Source', 'Health Pharma', 'Life Sciences', 'Bio Pharma', 'Medical Solutions'],
    'Medical Devices': ['Med Tech', 'Device Pro', 'Health Devices', 'Medical Systems', 'Care Tech', 'Diagnostic Pro'],
    'Medical Supplies': ['Med Supply', 'Health Supplies', 'Care Supplies', 'Medical Mart', 'Health Pro', 'Supply Care'],
    'Laboratory Equipment': ['Lab Pro', 'Science Equipment', 'Research Tools', 'Lab Masters', 'Analytical Pro'],
    'Electricity': ['Power Pro', 'Energy Co', 'Electric Solutions', 'Grid Masters', 'Power Source', 'Energy Plus'],
    'Fuels': ['Fuel Pro', 'Energy Fuels', 'Petro Co', 'Gas Masters', 'Fuel Solutions', 'Power Fuels'],
    'Renewable Equipment': ['Green Energy', 'Solar Pro', 'Wind Masters', 'Eco Power', 'Renewable Tech', 'Clean Energy'],
    'Building Materials': ['Build Pro', 'Construction Materials', 'Material Masters', 'Build Solutions', 'Structure Co'],
    'MEP Systems': ['MEP Pro', 'Systems Masters', 'Building Systems', 'Install Pro', 'Technical Systems'],
    'Construction Equipment': ['Build Equipment', 'Construction Pro', 'Heavy Machines', 'Site Equipment', 'Builder Tools'],
    'Freight Services': ['Freight Pro', 'Cargo Masters', 'Ship Co', 'Transport Solutions', 'Logistics Plus'],
    'Warehousing': ['Warehouse Pro', 'Storage Masters', 'Logistics Hub', 'Distribution Pro', 'Store Solutions'],
    'Fleet Services': ['Fleet Pro', 'Vehicle Masters', 'Auto Fleet', 'Transport Fleet', 'Drive Solutions'],
    'Consulting': ['Consult Pro', 'Advisory Masters', 'Strategy Co', 'Business Consulting', 'Expert Advisors'],
    'Legal Services': ['Legal Pro', 'Law Masters', 'Justice Co', 'Legal Solutions', 'Counsel Pro'],
    'Financial Services': ['Finance Pro', 'Money Masters', 'Capital Co', 'Financial Solutions', 'Investment Pro'],
    'Marketing Services': ['Marketing Pro', 'Brand Masters', 'Creative Co', 'Ad Solutions', 'Media Pro'],
    'Facilities Management': ['Facility Pro', 'Building Services', 'Maintenance Masters', 'Property Services', 'Site Pro'],
    'Office Services': ['Office Pro', 'Workspace Solutions', 'Business Services', 'Office Masters', 'Work Pro'],
    'Travel & Events': ['Travel Pro', 'Event Masters', 'Journey Co', 'Meeting Solutions', 'Destination Pro'],
    'Staffing Services': ['Staff Pro', 'Talent Masters', 'HR Solutions', 'Recruit Co', 'People Pro'],
    'HR Technology': ['HR Tech', 'People Systems', 'Workforce Pro', 'Talent Tech', 'HR Solutions'],
    'Learning & Development': ['Learn Pro', 'Training Masters', 'Skill Co', 'Development Pro', 'Education Solutions'],
}

# Contract types and payment terms
CONTRACT_TYPES = ['Annual Contract', 'Spot Purchase', 'Multi-Year Contract', 'Framework Agreement', 'Blanket Order']
PAYMENT_TERMS = ['Net 30', 'Net 45', 'Net 60', 'Net 15', 'Net 90', '2/10 Net 30']
RISK_SCORES = ['LOW', 'MEDIUM', 'HIGH']

def generate_supplier_name(category, country, existing_names):
    """Generate a unique supplier name."""
    patterns = SUPPLIER_PATTERNS.get(category, ['Global', 'Premier', 'Quality', 'Prime', 'Select'])

    for _ in range(100):  # Max attempts
        pattern = random.choice(patterns)
        suffix = random.choice(['Inc', 'Ltd', 'Corp', 'Co', 'Group', 'International', 'Trading', 'Solutions', 'Enterprises'])

        # Add country flavor sometimes
        if random.random() > 0.5:
            name = f"{country} {pattern} {suffix}"
        else:
            name = f"{pattern} {suffix}"

        if name not in existing_names:
            return name

    # Fallback with random number
    return f"{random.choice(patterns)} {random.randint(100, 999)}"

def generate_transactions(supplier_id, supplier_name, country, region, city, client_id, sector, category, subcategory, num_transactions=3):
    """Generate multiple transactions for a supplier."""
    transactions = []

    # Base spend varies by category
    base_spend_ranges = {
        'Pharmaceuticals': (500000, 3000000),
        'Medical Devices': (400000, 2000000),
        'Equipment & Machinery': (300000, 2500000),
        'Hardware': (200000, 1500000),
        'Cloud Services': (100000, 800000),
        'Consulting': (200000, 2000000),
        'Raw Materials - Metals': (300000, 2000000),
        'Building Materials': (200000, 1500000),
        'Electricity': (200000, 1500000),
        'Freight Services': (150000, 1000000),
        'default': (100000, 800000)
    }

    spend_range = base_spend_ranges.get(category, base_spend_ranges['default'])
    base_spend = random.randint(spend_range[0], spend_range[1])

    # Generate transactions across the year
    start_date = datetime(2025, 1, 1)

    for i in range(num_transactions):
        # Random date within the year
        days_offset = random.randint(0, 365)
        trans_date = start_date + timedelta(days=days_offset)

        # Vary spend by +/- 20%
        spend = int(base_spend * random.uniform(0.8, 1.2))
        # Round to nearest 100
        spend = round(spend / 100) * 100

        # Generate quality and delivery ratings
        quality_rating = round(random.uniform(3.8, 5.0), 1)
        delivery_rating = round(random.uniform(3.5, 5.0), 1)

        # Risk score based on region and other factors
        if region in ['Africa', 'Middle East']:
            risk_weights = [0.3, 0.4, 0.3]  # LOW, MEDIUM, HIGH
        elif region == 'APAC':
            risk_weights = [0.4, 0.4, 0.2]
        else:
            risk_weights = [0.6, 0.3, 0.1]

        risk_score = random.choices(RISK_SCORES, weights=risk_weights)[0]

        transactions.append({
            'Client_ID': client_id,
            'Sector': sector,
            'Category': category,
            'SubCategory': subcategory,
            'Supplier_ID': supplier_id,
            'Supplier_Name': supplier_name,
            'Supplier_Country': country,
            'Supplier_Region': region,
            'Supplier_City': city,
            'Transaction_Date': trans_date.strftime('%Y-%m-%d'),
            'Spend_USD': spend,
            'Contract_Type': random.choice(CONTRACT_TYPES),
            'Payment_Terms': random.choice(PAYMENT_TERMS),
            'Quality_Rating': quality_rating,
            'Delivery_Rating': delivery_rating,
            'Risk_Score': risk_score
        })

    return transactions

def get_random_location():
    """Get a random region, country, and city."""
    # Weight regions to add more diversity
    region_weights = {
        'Americas': 0.25,
        'Europe': 0.25,
        'APAC': 0.25,
        'Middle East': 0.15,
        'Africa': 0.10
    }

    region = random.choices(list(region_weights.keys()), weights=list(region_weights.values()))[0]
    country = random.choice(list(REGIONS[region].keys()))
    city = random.choice(REGIONS[region][country])

    return region, country, city

# Get existing supplier names
existing_names = set(existing_df['Supplier_Name'].unique())

# Get all category/subcategory combinations from existing data
category_subcategory = existing_df.groupby(['Client_ID', 'Sector', 'Category', 'SubCategory']).size().reset_index()[['Client_ID', 'Sector', 'Category', 'SubCategory']]

# Generate new suppliers and transactions
new_rows = []

print("Generating enhanced data...")

for _, row in category_subcategory.iterrows():
    client_id = row['Client_ID']
    sector = row['Sector']
    category = row['Category']
    subcategory = row['SubCategory']

    # Count existing suppliers for this subcategory
    existing_suppliers = existing_df[
        (existing_df['Category'] == category) &
        (existing_df['SubCategory'] == subcategory)
    ]['Supplier_ID'].nunique()

    # Add more suppliers to reach at least 5-7 per subcategory
    target_suppliers = random.randint(5, 8)
    suppliers_to_add = max(0, target_suppliers - existing_suppliers)

    for _ in range(suppliers_to_add):
        region, country, city = get_random_location()
        supplier_name = generate_supplier_name(category, country, existing_names)
        existing_names.add(supplier_name)

        supplier_id = f"S{next_supplier_id}"
        next_supplier_id += 1

        # Generate 2-4 transactions per supplier
        num_transactions = random.randint(2, 4)
        transactions = generate_transactions(
            supplier_id, supplier_name, country, region, city,
            client_id, sector, category, subcategory, num_transactions
        )
        new_rows.extend(transactions)

# Also add some additional transactions for existing suppliers to beef up the data
print("Adding more transactions for existing suppliers...")

# Get a sample of existing suppliers and add more transactions
existing_suppliers_sample = existing_df.drop_duplicates(subset=['Supplier_ID']).sample(frac=0.3, random_state=42)

for _, supplier in existing_suppliers_sample.iterrows():
    # Add 1-2 more transactions
    num_new = random.randint(1, 2)
    transactions = generate_transactions(
        supplier['Supplier_ID'],
        supplier['Supplier_Name'],
        supplier['Supplier_Country'],
        supplier['Supplier_Region'],
        supplier['Supplier_City'],
        supplier['Client_ID'],
        supplier['Sector'],
        supplier['Category'],
        supplier['SubCategory'],
        num_new
    )
    new_rows.extend(transactions)

# Create new dataframe and combine
new_df = pd.DataFrame(new_rows)

# Combine with existing data
combined_df = pd.concat([existing_df, new_df], ignore_index=True)

# Sort by Client_ID, Sector, Category, SubCategory, Transaction_Date
combined_df = combined_df.sort_values(
    ['Client_ID', 'Sector', 'Category', 'SubCategory', 'Transaction_Date']
).reset_index(drop=True)

# Save to file
output_path = 'data/structured/spend_data.csv'
combined_df.to_csv(output_path, index=False)

print("\n=== ENHANCED DATA SUMMARY ===")
print(f"Total rows: {len(combined_df)}")
print(f"New rows added: {len(new_rows)}")
print(f"Unique suppliers: {combined_df['Supplier_ID'].nunique()}")
print(f"Unique categories: {combined_df['Category'].nunique()}")
print(f"Unique subcategories: {combined_df['SubCategory'].nunique()}")

print("\n=== REGIONAL DISTRIBUTION ===")
print(combined_df['Supplier_Region'].value_counts())

print("\n=== SUPPLIERS PER SUBCATEGORY (Sample) ===")
supplier_counts = combined_df.groupby(['Category', 'SubCategory'])['Supplier_ID'].nunique().reset_index()
supplier_counts.columns = ['Category', 'SubCategory', 'Supplier_Count']
print(f"Min suppliers per subcategory: {supplier_counts['Supplier_Count'].min()}")
print(f"Max suppliers per subcategory: {supplier_counts['Supplier_Count'].max()}")
print(f"Average suppliers per subcategory: {supplier_counts['Supplier_Count'].mean():.1f}")

# Show any remaining low-count subcategories
low_count = supplier_counts[supplier_counts['Supplier_Count'] < 4]
if len(low_count) > 0:
    print(f"\nSubcategories with <4 suppliers: {len(low_count)}")
    print(low_count.to_string())
else:
    print("\nAll subcategories have 4+ suppliers!")

print(f"\nData saved to: {output_path}")
