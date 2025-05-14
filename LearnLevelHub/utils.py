import uuid
import datetime
import locale
import pandas as pd

def generate_unique_id():
    """
    Generate a unique ID for properties, bookings, etc.
    
    Returns:
        str: A unique ID
    """
    return str(uuid.uuid4())[:8]

def format_currency(amount, currency_symbol='€'):
    """
    Format a number as currency.
    
    Args:
        amount (float): Amount to format
        currency_symbol (str): Currency symbol to use
    
    Returns:
        str: Formatted currency string
    """
    return f"{currency_symbol}{amount:.2f}"

def format_date(date_str):
    """
    Format a date string.
    
    Args:
        date_str (str): Date string in ISO format (YYYY-MM-DD)
    
    Returns:
        str: Formatted date string (e.g., "Jan 15, 2023")
    """
    try:
        date_obj = pd.to_datetime(date_str).date()
        return date_obj.strftime("%b %d, %Y")
    except:
        return date_str

def calculate_nights(check_in, check_out):
    """
    Calculate the number of nights between check-in and check-out dates.
    
    Args:
        check_in (str): Check-in date in ISO format
        check_out (str): Check-out date in ISO format
    
    Returns:
        int: Number of nights
    """
    try:
        check_in_date = pd.to_datetime(check_in).date()
        check_out_date = pd.to_datetime(check_out).date()
        nights = (check_out_date - check_in_date).days
        return nights
    except:
        return 0

def get_month_name(month_number):
    """
    Get the name of a month from its number.
    
    Args:
        month_number (int): Month number (1-12)
    
    Returns:
        str: Month name (e.g., "January")
    """
    try:
        return datetime.date(1900, month_number, 1).strftime('%B')
    except:
        return ""
