import pandas as pd
import os
import json
from utils import generate_unique_id

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Path to properties data file
PROPERTIES_FILE = 'data/properties.csv'

# Initialize properties file if it doesn't exist
if not os.path.exists(PROPERTIES_FILE):
    initial_properties = pd.DataFrame({
        'id': ['prop1', 'prop2', 'prop3', 'prop4', 'prop5', 'prop6'],
        'name': ['Appartamento Elegante', 'Villa Vista Mare', 'Loft Navigli', 'Casa Spaccanapoli', 'Villetta Colosseo', 'Appartamento Vesuvio'],
        'address': ['Via Montenapoleone 12, Milano', 'Via Posillipo 45, Napoli', 'Ripa di Porta Ticinese 17, Milano', 'Via San Gregorio Armeno 8, Napoli', 'Via dei Fori Imperiali 23, Roma', 'Via Nazionale 42, Portici'],
        'city': ['Milano', 'Napoli', 'Milano', 'Napoli', 'Roma', 'Portici'],
        'bedrooms': [2, 4, 1, 3, 2, 2],
        'bathrooms': [1, 3, 1, 2, 1, 1],
        'description': [
            'Elegante appartamento in centro a Milano con finiture di pregio e vista sulla città.', 
            'Splendida villa con vista sul Golfo di Napoli, terrazza panoramica e accesso privato al mare.',
            'Moderno loft nella zona dei Navigli, perfetto per coppie, a pochi passi dai locali.',
            'Tipica casa napoletana nel cuore del centro storico, vicino alle principali attrazioni.',
            'Accogliente villetta con vista sul Colosseo, giardino privato e aria condizionata.',
            'Appartamento con vista sul Vesuvio, recentemente ristrutturato e ben collegato con Napoli.'
        ],
        'price_per_night': [180.0, 350.0, 120.0, 150.0, 220.0, 100.0],
        'amenities': [
            json.dumps(['WiFi', 'Smart TV', 'Aria Condizionata', 'Lavastoviglie']),
            json.dumps(['WiFi', 'Piscina', 'Terrazza', 'Parcheggio', 'Aria Condizionata']),
            json.dumps(['WiFi', 'Smart TV', 'Netflix', 'Cucina Attrezzata']),
            json.dumps(['WiFi', 'Lavatrice', 'Balcone', 'Aria Condizionata']),
            json.dumps(['WiFi', 'Giardino', 'Barbecue', 'Parcheggio']),
            json.dumps(['WiFi', 'Smart TV', 'Terrazza', 'Cucina Attrezzata'])
        ]
    })
    initial_properties.to_csv(PROPERTIES_FILE, index=False)

def get_properties():
    """
    Get all properties from the CSV file.
    
    Returns:
        list: List of property dictionaries
    """
    try:
        df = pd.read_csv(PROPERTIES_FILE)
        
        # Convert amenities from JSON string to list
        df['amenities'] = df['amenities'].apply(lambda x: json.loads(x))
        
        # Convert DataFrame to list of dictionaries
        properties = df.to_dict('records')
        return properties
    except Exception as e:
        print(f"Error loading properties: {e}")
        return []

def get_property_details(property_id):
    """
    Get details of a specific property.
    
    Args:
        property_id (str): The ID of the property
    
    Returns:
        dict: Property details or None if not found
    """
    properties = get_properties()
    property_data = next((p for p in properties if p['id'] == property_id), None)
    return property_data

def add_property(property_data):
    """
    Add a new property to the CSV file.
    
    Args:
        property_data (dict): Property data to add
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure property has a unique ID
        if 'id' not in property_data:
            property_data['id'] = generate_unique_id()
        
        # Convert amenities list to JSON string for storage
        if isinstance(property_data['amenities'], list):
            property_data_copy = property_data.copy()
            property_data_copy['amenities'] = json.dumps(property_data['amenities'])
        else:
            property_data_copy = property_data
        
        # Read existing properties
        df = pd.read_csv(PROPERTIES_FILE)
        
        # Add new property
        df = pd.concat([df, pd.DataFrame([property_data_copy])], ignore_index=True)
        
        # Save to CSV
        df.to_csv(PROPERTIES_FILE, index=False)
        
        return True
    except Exception as e:
        print(f"Error adding property: {e}")
        return False

def update_property(property_id, property_data):
    """
    Update an existing property.
    
    Args:
        property_id (str): The ID of the property to update
        property_data (dict): Updated property data
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read existing properties
        df = pd.read_csv(PROPERTIES_FILE)
        
        # Find property to update
        property_index = df[df['id'] == property_id].index
        
        if len(property_index) == 0:
            return False
        
        # Convert amenities list to JSON string for storage
        if isinstance(property_data['amenities'], list):
            property_data_copy = property_data.copy()
            property_data_copy['amenities'] = json.dumps(property_data['amenities'])
        else:
            property_data_copy = property_data
        
        # Update property
        for key, value in property_data_copy.items():
            df.loc[property_index, key] = value
        
        # Save to CSV
        df.to_csv(PROPERTIES_FILE, index=False)
        
        return True
    except Exception as e:
        print(f"Error updating property: {e}")
        return False

def delete_property(property_id):
    """
    Delete a property.
    
    Args:
        property_id (str): The ID of the property to delete
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read existing properties
        df = pd.read_csv(PROPERTIES_FILE)
        
        # Remove property
        df = df[df['id'] != property_id]
        
        # Save to CSV
        df.to_csv(PROPERTIES_FILE, index=False)
        
        return True
    except Exception as e:
        print(f"Error deleting property: {e}")
        return False

def calculate_property_metrics():
    """
    Calculate metrics for all properties.
    
    Returns:
        dict: Dictionary with property metrics
    """
    try:
        properties = get_properties()
        
        # Import booking data to calculate occupancy metrics
        from booking_manager import get_bookings
        bookings = get_bookings()
        
        metrics = {
            'total_properties': len(properties),
            'average_price': sum(p['price_per_night'] for p in properties) / len(properties) if properties else 0,
            'property_types': {
                'small': len([p for p in properties if p['bedrooms'] <= 1]),
                'medium': len([p for p in properties if 1 < p['bedrooms'] <= 3]),
                'large': len([p for p in properties if p['bedrooms'] > 3])
            }
        }
        
        # Calculate occupancy rates by property
        if bookings:
            property_occupancy = {}
            for prop in properties:
                prop_bookings = [b for b in bookings if b['property_id'] == prop['id']]
                total_days_booked = sum([(pd.to_datetime(b['check_out']) - pd.to_datetime(b['check_in'])).days 
                                        for b in prop_bookings])
                # Assuming metrics for the last 30 days
                occupancy_rate = min(total_days_booked / 30, 1.0)
                property_occupancy[prop['id']] = {
                    'name': prop['name'],
                    'occupancy_rate': occupancy_rate,
                    'total_bookings': len(prop_bookings)
                }
            metrics['property_occupancy'] = property_occupancy
        
        return metrics
    except Exception as e:
        print(f"Error calculating property metrics: {e}")
        return {}
