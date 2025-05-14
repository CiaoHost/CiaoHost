import pandas as pd
import os
import datetime
import json
from utils import generate_unique_id, format_date

# Path to message history file
MESSAGES_FILE = 'data/messages.csv'

# Initialize messages file if it doesn't exist
if not os.path.exists(MESSAGES_FILE):
    os.makedirs('data', exist_ok=True)
    initial_messages = pd.DataFrame({
        'id': ['msg1', 'msg2'],
        'booking_id': ['book1', 'book1'],
        'date': [datetime.datetime.now().strftime('%Y-%m-%d'), 
                (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')],
        'subject': ['Welcome to Seaside Villa', 'Check-in Instructions'],
        'content': [
            'Dear John Smith, welcome to our Seaside Villa! We look forward to hosting you.',
            'Dear John Smith, here are the check-in instructions for your stay at Seaside Villa.'
        ]
    })
    initial_messages.to_csv(MESSAGES_FILE, index=False)

def generate_welcome_message(booking, property_info, language='english'):
    """
    Generate a welcome message for a guest.
    
    Args:
        booking (dict): Booking details
        property_info (dict): Property details
        language (str): The language to use for the message
    
    Returns:
        str: Welcome message
    """
    check_in_date = format_date(booking['check_in'])
    check_out_date = format_date(booking['check_out'])
    
    if language == 'italian':
        message = f"""
Gentile {booking['guest_name']},

Benvenuto a {property_info['name']}! Siamo lieti di averla con noi dal {check_in_date} al {check_out_date}.

Informazioni importanti sul suo soggiorno:
- Check-in: dalle 14:00 alle 20:00
- Check-out: entro le 11:00
- WiFi: disponibile in tutta la struttura (la password sarà nella sua camera)
- Colazione: servita dalle 7:30 alle 10:00

La proprietà dispone di {property_info['bedrooms']} camere da letto e {property_info['bathrooms']} bagni.

Servizi disponibili:
"""
        for amenity in property_info['amenities']:
            message += f"- {amenity}\n"
        
        message += f"""
Per qualsiasi domanda o richiesta durante il suo soggiorno, non esiti a contattarci.

Cordiali saluti,
Il team di CiaoHost
"""
    else:
        message = f"""
Dear {booking['guest_name']},

Welcome to {property_info['name']}! We're delighted to have you staying with us from {check_in_date} to {check_out_date}.

Important information about your stay:
- Check-in: from 2:00 PM to 8:00 PM
- Check-out: by 11:00 AM
- WiFi: available throughout the property (password will be in your room)
- Breakfast: served from 7:30 AM to 10:00 AM

The property features {property_info['bedrooms']} bedrooms and {property_info['bathrooms']} bathrooms.

Available amenities:
"""
        for amenity in property_info['amenities']:
            message += f"- {amenity}\n"
        
        message += f"""
If you have any questions or requests during your stay, please don't hesitate to contact us.

Best regards,
The CiaoHost Team
"""
    
    return message

def generate_checkout_instructions(booking, property_info, language='english'):
    """
    Generate checkout instructions for a guest.
    
    Args:
        booking (dict): Booking details
        property_info (dict): Property details
        language (str): The language to use for the message
    
    Returns:
        str: Checkout instructions
    """
    check_out_date = format_date(booking['check_out'])
    
    if language == 'italian':
        message = f"""
Gentile {booking['guest_name']},

Speriamo che il suo soggiorno a {property_info['name']} sia stato piacevole.

Ecco le istruzioni per il check-out del {check_out_date}:

1. Il check-out è previsto entro le ore 11:00
2. Si prega di lasciare le chiavi sul tavolo della camera
3. Controllare di aver preso tutti gli effetti personali
4. Se ha utilizzato la cucina, si prega di lavarla e riporla

Consigli per il check-out senza problemi:
- Si prepari con anticipo per evitare la fretta dell'ultimo minuto
- Controlli tutte le stanze, gli armadi e i cassetti
- Lasci accese le luci del bagno per facilitare la pulizia

Grazie per aver scelto di soggiornare con noi. Le auguriamo buon viaggio e speriamo di rivederla presto!

Cordiali saluti,
Il team di CiaoHost
"""
    else:
        message = f"""
Dear {booking['guest_name']},

We hope your stay at {property_info['name']} has been enjoyable.

Here are the checkout instructions for {check_out_date}:

1. Checkout time is by 11:00 AM
2. Please leave the keys on the table in your room
3. Check that you've taken all your personal belongings
4. If you've used the kitchen, please wash and put away any dishes

Tips for a smooth checkout:
- Prepare in advance to avoid last-minute rush
- Check all rooms, closets, and drawers
- Leave bathroom lights on to facilitate cleaning

Thank you for choosing to stay with us. We wish you safe travels and hope to see you again soon!

Best regards,
The CiaoHost Team
"""
    
    return message

def send_automated_message(guest_email, subject, content):
    """
    Send an automated message to a guest.
    In a real implementation, this would send an actual email.
    For this prototype, it just records the message in the history.
    
    Args:
        guest_email (str): Guest's email address
        subject (str): Email subject
        content (str): Email content
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # In a real implementation, this would use an email service
        # For now, just record the message in the history
        from booking_manager import get_bookings
        
        # Find booking by guest email
        bookings = get_bookings()
        booking = next((b for b in bookings if b['guest_email'] == guest_email), None)
        
        if not booking:
            return False
        
        # Create message record
        message = {
            'id': generate_unique_id(),
            'booking_id': booking['id'],
            'date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'subject': subject,
            'content': content
        }
        
        # Add to message history
        df = pd.read_csv(MESSAGES_FILE)
        df = pd.concat([df, pd.DataFrame([message])], ignore_index=True)
        df.to_csv(MESSAGES_FILE, index=False)
        
        # In a real implementation, this would send an actual email
        # For this prototype, we'll just return True
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def get_message_history(booking_id=None):
    """
    Get message history for a booking.
    
    Args:
        booking_id (str, optional): Booking ID to filter messages
    
    Returns:
        list: List of message dictionaries
    """
    try:
        df = pd.read_csv(MESSAGES_FILE)
        
        if booking_id:
            df = df[df['booking_id'] == booking_id]
        
        # Sort by date (newest first)
        df = df.sort_values(by='date', ascending=False)
        
        messages = df.to_dict('records')
        return messages
    except Exception as e:
        print(f"Error loading message history: {e}")
        return []
