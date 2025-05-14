import pandas as pd
import os
import datetime
from utils import generate_unique_id

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Path to bookings data file
BOOKINGS_FILE = 'data/bookings.csv'

# Initialize bookings file if it doesn't exist
if not os.path.exists(BOOKINGS_FILE):
    # Create sample booking data
    today = datetime.datetime.now()
    checkout_date = today + datetime.timedelta(days=3)
    next_checkin = today + datetime.timedelta(days=7)
    next_checkout = today + datetime.timedelta(days=10)
    
    initial_bookings = pd.DataFrame({
        'id': ['book1', 'book2'],
        'property_id': ['prop1', 'prop2'],
        'guest_name': ['John Smith', 'Maria Rossi'],
        'guest_email': ['john@example.com', 'maria@example.com'],
        'check_in': [today.strftime('%Y-%m-%d'), next_checkin.strftime('%Y-%m-%d')],
        'check_out': [checkout_date.strftime('%Y-%m-%d'), next_checkout.strftime('%Y-%m-%d')],
        'guest_count': [2, 3],
        'total_price': [750.0, 540.0],
        'special_requests': ['Late check-in required', 'Gluten-free breakfast options'],
        'status': ['confirmed', 'confirmed']
    })
    initial_bookings.to_csv(BOOKINGS_FILE, index=False)

def get_bookings():
    """
    Get all bookings from the CSV file.
    
    Returns:
        list: List of booking dictionaries
    """
    try:
        df = pd.read_csv(BOOKINGS_FILE)
        bookings = df.to_dict('records')
        return bookings
    except Exception as e:
        print(f"Error loading bookings: {e}")
        return []

def get_booking_details(booking_id):
    """
    Get details of a specific booking.
    
    Args:
        booking_id (str): The ID of the booking
    
    Returns:
        dict: Booking details or None if not found
    """
    bookings = get_bookings()
    booking_data = next((b for b in bookings if b['id'] == booking_id), None)
    return booking_data

def add_booking(booking_data):
    """
    Add a new booking to the CSV file.
    
    Args:
        booking_data (dict): Booking data to add
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure booking has a unique ID
        if 'id' not in booking_data:
            booking_data['id'] = generate_unique_id()
        
        # Read existing bookings
        df = pd.read_csv(BOOKINGS_FILE)
        
        # Add new booking
        df = pd.concat([df, pd.DataFrame([booking_data])], ignore_index=True)
        
        # Save to CSV
        df.to_csv(BOOKINGS_FILE, index=False)
        
        return True
    except Exception as e:
        print(f"Error adding booking: {e}")
        return False

def update_booking(booking_id, booking_data):
    """
    Update an existing booking.
    
    Args:
        booking_id (str): The ID of the booking to update
        booking_data (dict): Updated booking data
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read existing bookings
        df = pd.read_csv(BOOKINGS_FILE)
        
        # Find booking to update
        booking_index = df[df['id'] == booking_id].index
        
        if len(booking_index) == 0:
            return False
        
        # Update booking
        for key, value in booking_data.items():
            df.loc[booking_index, key] = value
        
        # Save to CSV
        df.to_csv(BOOKINGS_FILE, index=False)
        
        return True
    except Exception as e:
        print(f"Error updating booking: {e}")
        return False

def cancel_booking(booking_id):
    """
    Cancel a booking (update status to cancelled).
    
    Args:
        booking_id (str): The ID of the booking to cancel
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read existing bookings
        df = pd.read_csv(BOOKINGS_FILE)
        
        # Find booking to cancel
        booking_index = df[df['id'] == booking_id].index
        
        if len(booking_index) == 0:
            return False
        
        # Update status to cancelled
        df.loc[booking_index, 'status'] = 'cancelled'
        
        # Save to CSV
        df.to_csv(BOOKINGS_FILE, index=False)
        
        return True
    except Exception as e:
        print(f"Error cancelling booking: {e}")
        return False

def calculate_booking_metrics():
    """
    Calculate metrics for all bookings.
    
    Returns:
        dict: Dictionary with booking metrics
    """
    try:
        bookings = get_bookings()
        now = datetime.datetime.now()
        
        # Count active, upcoming, and past bookings
        active_bookings = [b for b in bookings if 
                          pd.to_datetime(b['check_in']) <= now <= pd.to_datetime(b['check_out']) and
                          b['status'] != 'cancelled']
        
        upcoming_bookings = [b for b in bookings if 
                            pd.to_datetime(b['check_in']) > now and
                            b['status'] != 'cancelled']
        
        past_bookings = [b for b in bookings if 
                        pd.to_datetime(b['check_out']) < now and
                        b['status'] != 'cancelled']
        
        cancelled_bookings = [b for b in bookings if b['status'] == 'cancelled']
        
        # Calculate total revenue
        total_revenue = sum([b['total_price'] for b in bookings if b['status'] != 'cancelled'])
        
        # Calculate monthly revenue
        this_month = now.month
        this_year = now.year
        monthly_revenue = sum([b['total_price'] for b in bookings 
                              if pd.to_datetime(b['check_in']).month == this_month and
                              pd.to_datetime(b['check_in']).year == this_year and
                              b['status'] != 'cancelled'])
        
        # Average length of stay
        lengths_of_stay = [(pd.to_datetime(b['check_out']) - pd.to_datetime(b['check_in'])).days 
                          for b in bookings if b['status'] != 'cancelled']
        avg_stay = sum(lengths_of_stay) / len(lengths_of_stay) if lengths_of_stay else 0
        
        # Metrics dictionary
        metrics = {
            'total_bookings': len(bookings),
            'active_bookings': len(active_bookings),
            'upcoming_bookings': len(upcoming_bookings),
            'past_bookings': len(past_bookings),
            'cancelled_bookings': len(cancelled_bookings),
            'total_revenue': total_revenue,
            'monthly_revenue': monthly_revenue,
            'average_stay_length': avg_stay
        }
        
        return metrics
    except Exception as e:
        print(f"Error calculating booking metrics: {e}")
        return {}
