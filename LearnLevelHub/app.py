import streamlit as st
import pandas as pd
import datetime
import time
import re
from translations import get_text
from property_manager import (
    get_properties, add_property, update_property, delete_property,
    get_property_details, calculate_property_metrics
)
from booking_manager import (
    get_bookings, add_booking, update_booking, cancel_booking,
    get_booking_details, calculate_booking_metrics
)
from guest_communication import (
    generate_welcome_message, generate_checkout_instructions,
    send_automated_message, get_message_history
)
from llama_integration import (
    get_llama_response, setup_llama_model
)
from utils import (
    format_currency, format_date, generate_unique_id
)

# Set page configuration
st.set_page_config(
    page_title="CiaoHost - AI Co-Host for B&B",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global styles - DARK THEME
st.markdown("""
<style>
    /* Overall theme - Dark background */
    .main {
        background-color: #121212 !important;
        color: #ffffff !important;
    }
    
    body {
        background-color: #121212 !important;
        color: #ffffff !important;
    }
    
    /* Headers */
    h1, h2, h3, .stTitleContainer h1 {
        color: #ff5252 !important;
        font-weight: 600 !important;
    }
    
    /* Subheaders */
    h4, h5, h6 {
        color: #ce93d8 !important;
    }
    
    /* Text */
    p, span, div {
        color: #ffffff !important;
    }
    
    /* Links */
    a {
        color: #82b1ff !important;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #ff5252 !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }
    
    .stButton button:hover {
        background-color: #ff8a80 !important;
        box-shadow: 0 2px 5px rgba(255,255,255,0.2);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1e1e1e !important;
        border-right: 1px solid #333333 !important;
    }
    
    /* Sidebar buttons and content */
    .css-1d391kg, .css-163ttbj, .css-6qob1r, .st-ae, .css-pkbazv {
        background-color: #1e1e1e !important;
        color: white !important;
    }
    
    .css-1d391kg button, section[data-testid="stSidebar"] .stButton button {
        background-color: #673ab7 !important;
        color: white !important;
        border: 1px solid #4a148c !important;
    }
    
    /* Container boxes */
    div[data-testid="stContainer"] {
        background-color: #1e1e1e !important;
        border-radius: 10px !important;
        border: 1px solid #333333 !important;
        padding: 10px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.5) !important;
    }
    
    /* Cards and boxes */
    .element-container, .stDateInput, div[data-baseweb="select"], div[data-baseweb="base-input"] {
        background-color: #1e1e1e !important;
        border-radius: 8px !important;
    }
    
    /* Dataframe and tables */
    .dataframe, .stTable {
        background-color: #1e1e1e !important;
        color: white !important;
    }
    
    .dataframe th {
        background-color: #333333 !important;
        color: white !important;
    }
    
    .dataframe td {
        color: white !important;
    }
    
    /* Chat messages */
    div[data-testid="stChatMessage"] {
        padding: 12px !important;
        border-radius: 8px !important;
        margin: 10px 0 !important;
    }
    
    /* User chat messages */
    div[data-testid="stChatMessage"][data-testid*="user"] {
        background-color: #d32f2f !important;
        color: white !important;
    }
    
    /* Assistant chat messages */
    div[data-testid="stChatMessage"][data-testid*="assistant"] {
        background-color: #7b1fa2 !important;
        color: white !important;
    }
    
    /* Info boxes */
    div[data-testid="stAlert"] {
        background-color: #192734 !important;
        color: #82b1ff !important;
        border: 1px solid #333333 !important;
        border-radius: 8px !important;
    }
    
    /* Text inputs */
    input, textarea, div[data-baseweb="input"] input {
        background-color: #212121 !important;
        color: white !important;
        border-radius: 8px !important;
        border: 2px solid #ff5252 !important;
    }
    
    /* Metrics */
    div[data-testid="stMetric"] {
        background-color: #1a237e !important;
        padding: 15px !important;
        border-radius: 8px !important;
        border-left: 4px solid #3f51b5 !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #8c9eff !important;
    }
    
    div[data-testid="stMetricValue"] {
        color: #c5cae9 !important;
    }
    
    /* Expanders */
    .streamlit-expander {
        background-color: #212121 !important;
        border: 1px solid #333333 !important;
    }
    
    /* Radio buttons */
    .stRadio label {
        color: white !important;
    }
    
    /* Sliders */
    .stSlider div[data-baseweb="slider"] {
        background-color: #333333 !important;
    }
    
    .stSlider div[role="slider"] {
        background-color: #ff5252 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for language and other variables
if 'language' not in st.session_state:
    st.session_state.language = 'italian'  # Default italiano
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'
if 'selected_property' not in st.session_state:
    st.session_state.selected_property = None
if 'selected_booking' not in st.session_state:
    st.session_state.selected_booking = None
if 'llama_model' not in st.session_state:
    st.session_state.llama_model = setup_llama_model()
if 'user_mode' not in st.session_state:
    st.session_state.user_mode = 'owner'  # 'owner' or 'client'
if 'chat_history_client' not in st.session_state:
    st.session_state.chat_history_client = []
if 'booking_in_progress' not in st.session_state:
    st.session_state.booking_in_progress = False
if 'booking_data' not in st.session_state:
    st.session_state.booking_data = {
        'guest_name': '',
        'guest_email': '',
        'guest_phone': '',
        'property_id': '',
        'check_in': None,
        'check_out': None,
        'guests_count': 0,
        'special_requests': '',
        'stage': 'initial'  # initial, collecting_info, confirmation, completed
    }
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = 'Tutte'

# Function to switch language
def switch_language():
    if st.session_state.language == 'english':
        st.session_state.language = 'italian'
    else:
        st.session_state.language = 'english'
    st.rerun()

# Function to switch user mode
def switch_user_mode():
    if st.session_state.user_mode == 'owner':
        st.session_state.user_mode = 'client'
        st.session_state.current_page = 'client_chat'
    else:
        st.session_state.user_mode = 'owner'
        st.session_state.current_page = 'dashboard'
    st.rerun()

# Sidebar for navigation
with st.sidebar:
    # Logo and app name
    st.markdown("""
    <div style="text-align: center">
        <h1>CiaoHost</h1>
        <p>AI Co-Host for B&B Management</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Language selector
    lang_label = "🇮🇹 Italiano" if st.session_state.language == 'english' else "🇬🇧 English"
    st.button(lang_label, on_click=switch_language)
    
    # User mode switcher
    if st.session_state.user_mode == 'owner':
        if st.button(get_text("switch_to_client", st.session_state.language), use_container_width=True):
            switch_user_mode()
    else:
        if st.button(get_text("switch_to_owner", st.session_state.language), use_container_width=True):
            switch_user_mode()
    
    # Only show navigation if in owner mode
    if st.session_state.user_mode == 'owner':
        # Navigation
        st.subheader(get_text("navigation", st.session_state.language))
        
        if st.button(get_text("dashboard", st.session_state.language), use_container_width=True):
            st.session_state.current_page = 'dashboard'
            st.session_state.selected_property = None
            st.session_state.selected_booking = None
            st.rerun()
            
        if st.button(get_text("properties", st.session_state.language), use_container_width=True):
            st.session_state.current_page = 'properties'
            st.session_state.selected_booking = None
            st.rerun()
            
        if st.button(get_text("bookings", st.session_state.language), use_container_width=True):
            st.session_state.current_page = 'bookings'
            st.rerun()
            
        if st.button(get_text("guest_communication", st.session_state.language), use_container_width=True):
            st.session_state.current_page = 'communication'
            st.rerun()
            
        if st.button(get_text("ai_cohost", st.session_state.language), use_container_width=True):
            st.session_state.current_page = 'ai_cohost'
            st.rerun()
            
        if st.button(get_text("automated_checkin", st.session_state.language), use_container_width=True):
            st.session_state.current_page = 'automated_checkin'
            st.rerun()
            
        if st.button(get_text("automated_bookings", st.session_state.language), use_container_width=True):
            st.session_state.current_page = 'automated_bookings'
            st.rerun()
            
        if st.button(get_text("automated_maintenance", st.session_state.language), use_container_width=True):
            st.session_state.current_page = 'automated_maintenance'
            st.rerun()
            
        if st.button(get_text("cleaning_management", st.session_state.language), use_container_width=True):
            st.session_state.current_page = 'cleaning_management'
            st.rerun()
    else:
        # Client navigation
        st.subheader(get_text("navigation", st.session_state.language))
        
        if st.button(get_text("make_reservation", st.session_state.language), use_container_width=True):
            st.session_state.current_page = 'client_reservation'
            st.rerun()
            
        if st.button(get_text("browse_properties", st.session_state.language), use_container_width=True):
            st.session_state.current_page = 'client_properties'
            st.rerun()
            
        if st.button(get_text("check_availability", st.session_state.language), use_container_width=True):
            st.session_state.current_page = 'client_availability'
            st.rerun()
            
        if st.button(get_text("contact_support", st.session_state.language), use_container_width=True):
            st.session_state.current_page = 'client_support'
            st.rerun()

# Main content
def render_dashboard():
    st.title(get_text("dashboard_title", st.session_state.language))
    
    # AI Co-Host introduction
    st.markdown("""
    <div style="padding: 20px; background-color: #f0f5ff; border-radius: 10px; margin-bottom: 20px;">
        <h2 style="color: #3366CC;">CiaoHost: AI-Powered Co-Hosting</h2>
        <p>Welcome to the future of B&B management. CiaoHost offers a unique co-hosting service that uses Llama 3.3 AI to handle your property from check-in to check-out.</p>
        <p>✅ 24/7 automated guest assistance</p>
        <p>✅ Automated check-in/check-out management</p>
        <p>✅ Lower costs compared to traditional co-hosts</p>
        <p>✅ Consistent, professional guest communication</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get data for dashboard
    properties = get_properties()
    bookings = get_bookings()
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label=get_text("total_properties", st.session_state.language),
            value=len(properties)
        )
    
    with col2:
        active_bookings = len([b for b in bookings if 
                               pd.to_datetime(b['check_in']) <= datetime.datetime.now() <= 
                               pd.to_datetime(b['check_out'])])
        st.metric(
            label=get_text("active_bookings", st.session_state.language),
            value=active_bookings
        )
    
    with col3:
        upcoming_bookings = len([b for b in bookings if 
                                pd.to_datetime(b['check_in']) > datetime.datetime.now()])
        st.metric(
            label=get_text("upcoming_bookings", st.session_state.language),
            value=upcoming_bookings
        )
    
    with col4:
        monthly_income = sum([b['total_price'] for b in bookings if 
                             pd.to_datetime(b['check_in']).month == datetime.datetime.now().month])
        st.metric(
            label=get_text("monthly_income", st.session_state.language),
            value=format_currency(monthly_income)
        )
    
    # AI co-host stats
    st.subheader(get_text("ai_cohost_stats", st.session_state.language))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label=get_text("ai_response_time", st.session_state.language),
            value="< 1 min",
            delta="Faster than human co-hosts"
        )
    with col2:
        st.metric(
            label=get_text("cost_savings", st.session_state.language),
            value="70%",
            delta="Compared to traditional co-hosting"
        )
    with col3:
        st.metric(
            label=get_text("guest_satisfaction", st.session_state.language),
            value="4.9/5",
            delta="Based on recent reviews"
        )
    
    # Recent bookings
    st.subheader(get_text("recent_bookings", st.session_state.language))
    
    if bookings:
        recent_bookings = sorted(bookings, 
                                key=lambda b: pd.to_datetime(b['check_in']), 
                                reverse=True)[:5]
        
        for booking in recent_bookings:
            with st.container():
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    property_info = next((p for p in properties if p['id'] == booking['property_id']), None)
                    if property_info:
                        st.subheader(property_info['name'])
                with col2:
                    st.write(f"**{get_text('guest', st.session_state.language)}:** {booking['guest_name']}")
                    st.write(f"**{get_text('dates', st.session_state.language)}:** {format_date(booking['check_in'])} - {format_date(booking['check_out'])}")
                    st.write(f"**{get_text('total', st.session_state.language)}:** {format_currency(booking['total_price'])}")
                with col3:
                    st.write("**AI Co-Host Status:**")
                    st.success("✅ Check-in prepared")
                    st.info("ℹ️ Guest instructions sent")
                st.divider()
    else:
        st.info(get_text("no_bookings", st.session_state.language))

def render_properties():
    st.title(get_text("properties_title", st.session_state.language))
    
    # Get all properties
    properties = get_properties()
    
    # Add new property button
    if st.button(get_text("add_property", st.session_state.language), key="add_property_btn"):
        st.session_state.selected_property = "new"
        st.rerun()
    
    # If a property is selected or we're adding a new one
    if st.session_state.selected_property:
        if st.session_state.selected_property == "new":
            render_property_form(None)
        else:
            property_details = get_property_details(st.session_state.selected_property)
            render_property_form(property_details)
    else:
        # Display property list
        if properties:
            for prop in properties:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.subheader(prop['name'])
                    st.write(prop['address'])
                
                with col2:
                    st.write(f"**{get_text('bedrooms', st.session_state.language)}:** {prop['bedrooms']}")
                    st.write(f"**{get_text('bathrooms', st.session_state.language)}:** {prop['bathrooms']}")
                
                with col3:
                    if st.button(get_text("view_details", st.session_state.language), key=f"view_{prop['id']}"):
                        st.session_state.selected_property = prop['id']
                        st.rerun()
                
                st.divider()
        else:
            st.info(get_text("no_properties", st.session_state.language))

def render_property_form(property_data):
    if property_data:
        st.subheader(get_text("edit_property", st.session_state.language))
        property_id = property_data['id']
    else:
        st.subheader(get_text("add_property", st.session_state.language))
        property_id = generate_unique_id()
    
    with st.form(key="property_form"):
        name = st.text_input(get_text("property_name", st.session_state.language), 
                            value=property_data['name'] if property_data else "")
        
        address = st.text_input(get_text("address", st.session_state.language), 
                               value=property_data['address'] if property_data else "")
        
        col1, col2 = st.columns(2)
        with col1:
            bedrooms = st.number_input(get_text("bedrooms", st.session_state.language), 
                                      min_value=0, max_value=20, 
                                      value=property_data['bedrooms'] if property_data else 1)
        
        with col2:
            bathrooms = st.number_input(get_text("bathrooms", st.session_state.language), 
                                       min_value=0, max_value=20, 
                                       value=property_data['bathrooms'] if property_data else 1)
        
        description = st.text_area(get_text("description", st.session_state.language), 
                                  value=property_data['description'] if property_data else "")
        
        price_per_night = st.number_input(get_text("price_per_night", st.session_state.language), 
                                         min_value=0.0, 
                                         value=property_data['price_per_night'] if property_data else 100.0)
        
        amenities = st.multiselect(
            get_text("amenities", st.session_state.language),
            options=["WiFi", "Air Conditioning", "Kitchen", "TV", "Pool", "Parking", "Washer", "Dryer"],
            default=property_data['amenities'] if property_data else []
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submit_button = st.form_submit_button(get_text("save", st.session_state.language))
        
        with col2:
            cancel_button = st.form_submit_button(get_text("cancel", st.session_state.language))
    
    if submit_button:
        new_property = {
            "id": property_id,
            "name": name,
            "address": address,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "description": description,
            "price_per_night": price_per_night,
            "amenities": amenities
        }
        
        if property_data:
            update_property(property_id, new_property)
            st.success(get_text("property_updated", st.session_state.language))
        else:
            add_property(new_property)
            st.success(get_text("property_added", st.session_state.language))
        
        st.session_state.selected_property = None
        st.rerun()
    
    if cancel_button:
        st.session_state.selected_property = None
        st.rerun()
    
    # Delete button (only for existing properties)
    if property_data:
        if st.button(get_text("delete_property", st.session_state.language), key="delete_property"):
            delete_property(property_id)
            st.success(get_text("property_deleted", st.session_state.language))
            st.session_state.selected_property = None
            st.rerun()

def render_bookings():
    st.title(get_text("bookings_title", st.session_state.language))
    
    # Get all bookings and properties
    bookings = get_bookings()
    properties = get_properties()
    
    # Add new booking button
    if st.button(get_text("add_booking", st.session_state.language), key="add_booking_btn"):
        st.session_state.selected_booking = "new"
        st.rerun()
    
    # If a booking is selected or we're adding a new one
    if st.session_state.selected_booking:
        if st.session_state.selected_booking == "new":
            render_booking_form(None, properties)
        else:
            booking_details = get_booking_details(st.session_state.selected_booking)
            render_booking_form(booking_details, properties)
    else:
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            filter_property = st.selectbox(
                get_text("filter_by_property", st.session_state.language),
                options=["All"] + [p['name'] for p in properties],
                index=0
            )
        
        with col2:
            booking_status = st.selectbox(
                get_text("filter_by_status", st.session_state.language),
                options=["All", "Upcoming", "Active", "Past"],
                index=0
            )
        
        # Apply filters
        filtered_bookings = bookings
        if filter_property != "All":
            property_id = next((p['id'] for p in properties if p['name'] == filter_property), None)
            filtered_bookings = [b for b in filtered_bookings if b['property_id'] == property_id]
        
        if booking_status != "All":
            now = datetime.datetime.now()
            if booking_status == "Upcoming":
                filtered_bookings = [b for b in filtered_bookings if pd.to_datetime(b['check_in']) > now]
            elif booking_status == "Active":
                filtered_bookings = [b for b in filtered_bookings if 
                                    pd.to_datetime(b['check_in']) <= now <= pd.to_datetime(b['check_out'])]
            elif booking_status == "Past":
                filtered_bookings = [b for b in filtered_bookings if pd.to_datetime(b['check_out']) < now]
        
        # Display bookings
        if filtered_bookings:
            for booking in filtered_bookings:
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    property_info = next((p for p in properties if p['id'] == booking['property_id']), None)
                    if property_info:
                        st.subheader(property_info['name'])
                    st.write(f"**{get_text('guest', st.session_state.language)}:** {booking['guest_name']}")
                
                with col2:
                    st.write(f"**{get_text('dates', st.session_state.language)}:** {format_date(booking['check_in'])} - {format_date(booking['check_out'])}")
                    st.write(f"**{get_text('total', st.session_state.language)}:** {format_currency(booking['total_price'])}")
                
                with col3:
                    if st.button(get_text("view_details", st.session_state.language), key=f"view_booking_{booking['id']}"):
                        st.session_state.selected_booking = booking['id']
                        st.rerun()
                
                st.divider()
        else:
            st.info(get_text("no_bookings_found", st.session_state.language))

def render_booking_form(booking_data, properties):
    if booking_data:
        st.subheader(get_text("edit_booking", st.session_state.language))
        booking_id = booking_data['id']
    else:
        st.subheader(get_text("add_booking", st.session_state.language))
        booking_id = generate_unique_id()
    
    with st.form(key="booking_form"):
        property_options = {p['id']: p['name'] for p in properties}
        selected_property = st.selectbox(
            get_text("select_property", st.session_state.language),
            options=list(property_options.keys()),
            format_func=lambda x: property_options[x],
            index=list(property_options.keys()).index(booking_data['property_id']) if booking_data else 0
        )
        
        col1, col2 = st.columns(2)
        with col1:
            guest_name = st.text_input(get_text("guest_name", st.session_state.language), 
                                      value=booking_data['guest_name'] if booking_data else "")
        
        with col2:
            guest_email = st.text_input(get_text("guest_email", st.session_state.language), 
                                       value=booking_data['guest_email'] if booking_data else "")
        
        col1, col2 = st.columns(2)
        with col1:
            check_in = st.date_input(
                get_text("check_in_date", st.session_state.language),
                value=pd.to_datetime(booking_data['check_in']).date() if booking_data else datetime.datetime.now().date()
            )
        
        with col2:
            check_out = st.date_input(
                get_text("check_out_date", st.session_state.language),
                value=pd.to_datetime(booking_data['check_out']).date() if booking_data else (datetime.datetime.now() + datetime.timedelta(days=1)).date(),
                min_value=check_in
            )
        
        # Calculate total price based on selected property and dates
        selected_property_data = next((p for p in properties if p['id'] == selected_property), None)
        if selected_property_data:
            num_nights = (check_out - check_in).days
            price_per_night = selected_property_data['price_per_night']
            total_price = num_nights * price_per_night
            
            st.write(f"**{get_text('total_nights', st.session_state.language)}:** {num_nights}")
            st.write(f"**{get_text('price_per_night', st.session_state.language)}:** {format_currency(price_per_night)}")
            st.write(f"**{get_text('total_price', st.session_state.language)}:** {format_currency(total_price)}")
        
        guest_count = st.number_input(
            get_text("number_of_guests", st.session_state.language),
            min_value=1,
            max_value=20,
            value=booking_data['guest_count'] if booking_data else 2
        )
        
        special_requests = st.text_area(
            get_text("special_requests", st.session_state.language),
            value=booking_data['special_requests'] if booking_data else ""
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submit_button = st.form_submit_button(get_text("save", st.session_state.language))
        
        with col2:
            cancel_button = st.form_submit_button(get_text("cancel", st.session_state.language))
    
    if submit_button:
        num_nights = (check_out - check_in).days
        selected_property_data = next((p for p in properties if p['id'] == selected_property), None)
        total_price = num_nights * selected_property_data['price_per_night']
        
        new_booking = {
            "id": booking_id,
            "property_id": selected_property,
            "guest_name": guest_name,
            "guest_email": guest_email,
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "guest_count": guest_count,
            "total_price": total_price,
            "special_requests": special_requests,
            "status": "confirmed"
        }
        
        if booking_data:
            update_booking(booking_id, new_booking)
            st.success(get_text("booking_updated", st.session_state.language))
        else:
            add_booking(new_booking)
            st.success(get_text("booking_added", st.session_state.language))
        
        st.session_state.selected_booking = None
        st.rerun()
    
    if cancel_button:
        st.session_state.selected_booking = None
        st.rerun()
    
    # Cancel booking button (only for existing bookings)
    if booking_data and booking_data['status'] != "cancelled":
        if st.button(get_text("cancel_booking", st.session_state.language), key="cancel_booking"):
            cancel_booking(booking_id)
            st.success(get_text("booking_cancelled", st.session_state.language))
            st.session_state.selected_booking = None
            st.rerun()

def render_communication():
    st.title(get_text("communication_title", st.session_state.language))
    
    # Get bookings and properties
    bookings = get_bookings()
    properties = get_properties()
    
    # Select a booking for communication
    booking_options = {}
    for booking in bookings:
        if booking['status'] != 'cancelled':
            property_info = next((p for p in properties if p['id'] == booking['property_id']), None)
            if property_info:
                option_text = f"{booking['guest_name']} - {property_info['name']} ({format_date(booking['check_in'])} - {format_date(booking['check_out'])})"
                booking_options[booking['id']] = option_text
    
    selected_booking_id = st.selectbox(
        get_text("select_booking", st.session_state.language),
        options=list(booking_options.keys()),
        format_func=lambda x: booking_options[x],
        index=0 if booking_options else None
    )
    
    if selected_booking_id:
        booking = get_booking_details(selected_booking_id)
        property_info = next((p for p in properties if p['id'] == booking['property_id']), None)
        
        st.subheader(get_text("guest_details", st.session_state.language))
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**{get_text('name', st.session_state.language)}:** {booking['guest_name']}")
            st.write(f"**{get_text('email', st.session_state.language)}:** {booking['guest_email']}")
        
        with col2:
            st.write(f"**{get_text('check_in', st.session_state.language)}:** {format_date(booking['check_in'])}")
            st.write(f"**{get_text('check_out', st.session_state.language)}:** {format_date(booking['check_out'])}")
        
        st.subheader(get_text("automated_messages", st.session_state.language))
        
        tab1, tab2, tab3 = st.tabs([
            get_text("welcome_message", st.session_state.language),
            get_text("instructions", st.session_state.language),
            get_text("custom_message", st.session_state.language)
        ])
        
        with tab1:
            welcome_message = generate_welcome_message(booking, property_info, st.session_state.language)
            st.text_area(get_text("message_preview", st.session_state.language), welcome_message, height=200)
            if st.button(get_text("send_welcome", st.session_state.language), key="send_welcome"):
                success = send_automated_message(booking['guest_email'], "Welcome", welcome_message)
                if success:
                    st.success(get_text("message_sent", st.session_state.language))
                else:
                    st.error(get_text("message_error", st.session_state.language))
        
        with tab2:
            checkout_instructions = generate_checkout_instructions(booking, property_info, st.session_state.language)
            st.text_area(get_text("message_preview", st.session_state.language), checkout_instructions, height=200)
            if st.button(get_text("send_instructions", st.session_state.language), key="send_instructions"):
                success = send_automated_message(booking['guest_email'], "Checkout Instructions", checkout_instructions)
                if success:
                    st.success(get_text("message_sent", st.session_state.language))
                else:
                    st.error(get_text("message_error", st.session_state.language))
        
        with tab3:
            custom_subject = st.text_input(get_text("message_subject", st.session_state.language))
            custom_message = st.text_area(get_text("message_content", st.session_state.language), height=200)
            if st.button(get_text("send_message", st.session_state.language), key="send_custom"):
                if custom_subject and custom_message:
                    success = send_automated_message(booking['guest_email'], custom_subject, custom_message)
                    if success:
                        st.success(get_text("message_sent", st.session_state.language))
                    else:
                        st.error(get_text("message_error", st.session_state.language))
                else:
                    st.warning(get_text("complete_all_fields", st.session_state.language))
        
        # Message history
        st.subheader(get_text("message_history", st.session_state.language))
        messages = get_message_history(selected_booking_id)
        
        if messages:
            for msg in messages:
                with st.container():
                    st.write(f"**{format_date(msg['date'])} - {msg['subject']}**")
                    st.write(msg['content'])
                    st.divider()
        else:
            st.info(get_text("no_messages", st.session_state.language))
    else:
        st.info(get_text("no_active_bookings", st.session_state.language))

def render_ai_cohost():
    st.title(get_text("ai_cohost_title", st.session_state.language))
    
    # AI Co-Host introduction
    st.markdown("""
    <div style="padding: 20px; background-color: #1e1e1e; border-radius: 10px; margin-bottom: 20px; border: 1px solid #333333;">
        <h3 style="color: #ff5252;">Llama 3.3 Co-Host AI</h3>
        <p style="color: #ffffff;">Il tuo co-host basato su intelligenza artificiale è pronto ad assisterti in tutti gli aspetti della gestione delle proprietà. 
        Chiedi informazioni su messaggi agli ospiti, strategie di prezzo, raccomandazioni locali, procedure di check-in o qualsiasi altro argomento di gestione B&B.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    prompt = st.chat_input(get_text("ask_cohost", st.session_state.language))
    
    if prompt:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner(get_text("thinking", st.session_state.language)):
                response = get_llama_response(prompt, st.session_state.llama_model, st.session_state.language)
                st.write(response)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Sample questions
    with st.expander("Sample Questions"):
        sample_questions = [
            "How can I create an automated welcome sequence for guests?",
            "What's the best pricing strategy during high season?",
            "How can I improve my property's guest reviews?",
            "Write a friendly message for explaining the check-in process",
            "What should be included in my digital guidebook?"
        ]
        
        for question in sample_questions:
            if st.button(question, key=f"sample_{hash(question)}"):
                # Add user message to chat history
                st.session_state.chat_history.append({"role": "user", "content": question})
                
                # Get AI response
                response = get_llama_response(question, st.session_state.llama_model, st.session_state.language)
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()

def render_automated_checkin():
    st.title(get_text("automated_checkin_title", st.session_state.language))
    
    # Automated check-in introduction
    st.markdown("""
    <div style="padding: 20px; background-color: #1e1e1e; border-radius: 10px; margin-bottom: 20px; border: 1px solid #333333;">
        <h3 style="color: #ff5252;">Sistema di Check-in Automatizzato</h3>
        <p style="color: #ffffff;">Il tuo co-host AI gestisce l'intero processo di check-in, fornendo un'esperienza fluida per i tuoi ospiti 
        senza richiedere la tua presenza. Configura codici automatici per le porte, invia istruzioni 
        e monitora gli arrivi degli ospiti - tutto senza muovere un dito.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get all bookings with upcoming check-ins
    bookings = get_bookings()
    properties = get_properties()
    
    # Filter for upcoming check-ins
    upcoming_checkins = [b for b in bookings if 
                        pd.to_datetime(b['check_in']) > datetime.datetime.now() and
                        b['status'] != 'cancelled']
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Upcoming Check-ins", "Access Codes", "Settings"])
    
    with tab1:
        if upcoming_checkins:
            st.subheader(f"{len(upcoming_checkins)} Upcoming Check-ins")
            
            for booking in upcoming_checkins:
                with st.container():
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col1:
                        check_in_date = pd.to_datetime(booking['check_in']).date()
                        days_until = (check_in_date - datetime.datetime.now().date()).days
                        st.markdown(f"### {format_date(booking['check_in'])}")
                        st.markdown(f"**{days_until} days from now**")
                    
                    with col2:
                        property_info = next((p for p in properties if p['id'] == booking['property_id']), None)
                        if property_info:
                            st.markdown(f"**Property:** {property_info['name']}")
                        st.markdown(f"**Guest:** {booking['guest_name']}")
                        st.markdown(f"**Email:** {booking['guest_email']}")
                    
                    with col3:
                        st.markdown("**Status:**")
                        if days_until <= 3:
                            st.success("✅ Instructions sent")
                            st.success("✅ Access code generated")
                        elif days_until <= 7:
                            st.success("✅ Initial message sent")
                            st.info("⏳ Access code pending")
                        else:
                            st.info("⏳ Scheduled for later")
                    
                    st.divider()
        else:
            st.info("No upcoming check-ins scheduled")
    
    with tab2:
        st.subheader("Codici di Accesso Digitali")
        st.markdown("Il tuo co-host AI genera e gestisce automaticamente i codici di accesso digitali per le tue proprietà.")
        
        # Sample table of access codes
        data = {
            "Proprietà": ["Villa Vista Mare", "Rifugio in Montagna", "Villa Vista Mare"],
            "Ospite": ["Giovanni Bianchi", "Maria Rossi", "Prossimo Ospite"],
            "Codice": ["1234#", "5678#", "9012#"],
            "Valido Da": ["20 Ago, 2023", "27 Ago, 2023", "15 Set, 2023"],
            "Valido Fino": ["23 Ago, 2023", "30 Ago, 2023", "20 Set, 2023"],
            "Stato": ["Attivo", "Programmato", "Programmato"]
        }
        
        df = pd.DataFrame(data)
        st.dataframe(df)
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("Genera Nuovo Codice", disabled=True)
        with col2:
            st.button("Revoca Codice di Accesso", disabled=True)
    
    with tab3:
        st.subheader("Impostazioni Check-in Automatizzato")
        
        st.checkbox("Invia istruzioni di check-in 3 giorni prima dell'arrivo", value=True)
        st.checkbox("Genera codici di accesso automaticamente", value=True)
        st.checkbox("Invia codici di accesso 24 ore prima del check-in", value=True)
        st.checkbox("Notifica il proprietario dopo il check-in riuscito", value=True)
        st.checkbox("Invia messaggio di benvenuto all'arrivo rilevato", value=True)
        
        st.selectbox("Orario di check-in predefinito", options=["14:00", "15:00", "16:00", "Flessibile"])
        st.selectbox("Orario di check-out predefinito", options=["10:00", "11:00", "12:00", "Flessibile"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Giorni minimi prima dell'arrivo per inviare il primo messaggio", min_value=1, max_value=14, value=7)
        with col2:
            st.number_input("Ore prima del check-in per inviare il codice di accesso", min_value=1, max_value=48, value=24)
        
        st.button("Salva Impostazioni", disabled=True)

def render_automated_bookings():
    st.title(get_text("automated_bookings_title", st.session_state.language))
    
    # Automated bookings introduction
    st.markdown("""
    <div style="padding: 20px; background-color: #1e1e1e; border-radius: 10px; margin-bottom: 20px; border: 1px solid #333333;">
        <h3 style="color: #ff5252;">Gestione Prenotazioni con AI</h3>
        <p style="color: #ffffff;">Il tuo co-host AI gestisce automaticamente le prenotazioni degli ospiti, raccoglie informazioni, elabora i pagamenti 
        e sincronizza le prenotazioni su tutte le tue piattaforme senza richiedere intervento manuale.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Gestione Prenotazioni Automatizzata", "Informazioni Ospiti", "Impostazioni"])
    
    with tab1:
        st.subheader("Integrazione Canali di Prenotazione")
        st.markdown("Il tuo co-host AI monitora e sincronizza le prenotazioni da più piattaforme:")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.image("https://upload.wikimedia.org/wikipedia/commons/6/69/Airbnb_Logo_B%C3%A9lo.svg", width=100)
            st.checkbox("Airbnb", value=True)
        with col2:
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Booking.com_logo.svg/2560px-Booking.com_logo.svg.png", width=100)
            st.checkbox("Booking.com", value=True)
        with col3:
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Vrbo_logo.svg/2560px-Vrbo_logo.svg.png", width=100)
            st.checkbox("VRBO", value=False)
        with col4:
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Tripadvisor.svg/2560px-Tripadvisor.svg.png", width=100)
            st.checkbox("TripAdvisor", value=False)
        
        st.divider()
        
        st.subheader("Elaborazione Prenotazioni con AI")
        st.markdown("Quando arrivano nuove prenotazioni, il tuo co-host AI:")
        
        st.checkbox("Verifica automaticamente le informazioni dell'ospite", value=True)
        st.checkbox("Controlla prenotazioni in conflitto tra piattaforme", value=True)
        st.checkbox("Conferma la prenotazione con l'ospite via email/messaggio", value=True)
        st.checkbox("Aggiorna la disponibilità su tutte le altre piattaforme", value=True)
        st.checkbox("Pianifica il processo di check-in", value=True)
        st.checkbox("Crea un profilo ospite per un servizio personalizzato", value=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("Connetti Nuova Piattaforma", disabled=True)
        with col2:
            st.button("Verifica Connessione", disabled=True)
    
    with tab2:
        st.subheader("Raccolta Informazioni Ospiti con AI")
        st.markdown("Il tuo co-host AI raccoglie e gestisce automaticamente le informazioni degli ospiti:")
        
        # Sample table of guest information (this would normally be populated from database)
        data = {
            "Nome Ospite": ["Giovanni Bianchi", "Maria Rossi", "Ospite Futuro"],
            "Email": ["giovanni@esempio.com", "maria@esempio.com", "ospite@esempio.com"],
            "Telefono": ["+39-555-123-4567", "+39-123-456-7890", "+33-123-456-789"],
            "ID Verificato": ["Sì", "Sì", "In attesa"],
            "Richieste Speciali": ["Check-in tardivo", "Colazione senza glutine", "Prelievo in aeroporto"],
            "Soggiorni Precedenti": ["1", "0", "0"],
            "Note AI": ["Ospite abituale, preferisce cuscini rigidi", "Ospite per la prima volta, interessato alla cucina locale", "Viene per viaggio d'affari"]
        }
        
        df = pd.DataFrame(data)
        st.dataframe(df)
        
        st.divider()
        
        st.subheader("Processo di Raccolta Informazioni AI")
        st.markdown("""
        Dopo la conferma della prenotazione, il tuo co-host AI automaticamente:
        1. Invia un messaggio di benvenuto personalizzato richiedendo informazioni aggiuntive
        2. Elabora le risposte e aggiorna il profilo dell'ospite
        3. Identifica richieste speciali e preferenze
        4. Crea esperienze personalizzate basate sul profilo dell'ospite
        5. Memorizza le informazioni per soggiorni futuri
        """)
        
        st.checkbox("Richiedi verifica ID", value=True)
        st.checkbox("Raccogli informazioni di arrivo", value=True)
        st.checkbox("Chiedi requisiti dietetici speciali", value=True)
        st.checkbox("Richiedi informazioni sullo scopo del viaggio", value=True)
    
    with tab3:
        st.subheader("Automated Booking Settings")
        
        st.checkbox("Auto-accept bookings that meet criteria", value=True)
        st.checkbox("Require manual approval for bookings with special requests", value=True)
        st.checkbox("Automatically update calendar across all platforms", value=True)
        st.checkbox("Send booking confirmation to owner", value=True)
        st.checkbox("Request guest ID for verification", value=True)
        
        st.selectbox("Minimum advance booking time", options=["No minimum", "24 hours", "48 hours", "72 hours", "1 week"])
        st.selectbox("Maximum advance booking time", options=["No maximum", "3 months", "6 months", "1 year"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Minimum stay (nights)", min_value=1, max_value=30, value=2)
        with col2:
            st.number_input("Maximum stay (nights)", min_value=1, max_value=365, value=30)
        
        st.button("Save Settings", disabled=True)

def render_automated_maintenance():
    st.title(get_text("automated_maintenance_title", st.session_state.language))
    
    # Maintenance management introduction
    st.markdown("""
    <div style="padding: 20px; background-color: #f0f5ff; border-radius: 10px; margin-bottom: 20px;">
        <h3 style="color: #3366CC;">AI Maintenance Management</h3>
        <p>Your AI co-host detects, schedules, and coordinates property maintenance automatically. 
        Track maintenance history, schedule preventive maintenance, and get alerted about potential issues before they become problems.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Active Maintenance", "Maintenance History", "Preventive Maintenance"])
    
    with tab1:
        st.subheader("Current Maintenance Tasks")
        
        # Sample maintenance tasks
        maintenance_data = {
            "Property": ["Seaside Villa", "Seaside Villa", "Mountain Retreat"],
            "Issue": ["Leaking faucet in master bathroom", "AC maintenance", "Fireplace inspection"],
            "Priority": ["Medium", "High", "Low"],
            "Status": ["Scheduled", "In Progress", "Pending"],
            "Assigned To": ["Plumber Mario", "AC Technician", "Pending Assignment"],
            "Scheduled Date": ["Aug 25, 2023", "Aug 22, 2023", "Sep 10, 2023"]
        }
        
        df = pd.DataFrame(maintenance_data)
        st.dataframe(df)
        
        st.divider()
        
        # AI detected issues
        st.subheader("AI-Detected Potential Issues")
        st.markdown("Based on guest feedback, property sensors, and usage patterns, your AI co-host has detected these potential maintenance needs:")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("⚠️ Seaside Villa: Water usage higher than normal, possible leak")
            st.info("⚠️ Mountain Retreat: Heating system inefficiency detected")
        with col2:
            st.success("✅ Seaside Villa: Recent AC maintenance has improved energy efficiency by 15%")
            st.warning("⚠️ Seaside Villa: Dishwasher approaching end of expected lifespan")
    
    with tab2:
        st.subheader("Maintenance History")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Property", ["All Properties", "Seaside Villa", "Mountain Retreat"])
        with col2:
            st.selectbox("Time Period", ["Last Month", "Last 3 Months", "Last 6 Months", "Last Year", "All Time"])
        
        # Sample maintenance history
        history_data = {
            "Date": ["Jul 15, 2023", "Jun 20, 2023", "May 10, 2023", "Apr 05, 2023"],
            "Property": ["Seaside Villa", "Mountain Retreat", "Seaside Villa", "Mountain Retreat"],
            "Maintenance Type": ["Plumbing", "Electrical", "General", "Heating"],
            "Description": ["Fixed kitchen sink clog", "Replaced living room light fixtures", "Annual property inspection", "Heating system maintenance"],
            "Cost": ["€120", "€250", "€350", "€180"],
            "Service Provider": ["Plumber Mario", "Electrician Luigi", "Property Inspector", "Heating Specialist"]
        }
        
        df = pd.DataFrame(history_data)
        st.dataframe(df)
        
        # Maintenance analytics
        st.subheader("Maintenance Analytics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Maintenance Costs (YTD)", "€1,780", "-8% vs. last year")
        with col2:
            st.metric("Average Issue Resolution Time", "1.8 days", "-15% vs. last year")
        with col3:
            st.metric("Preventive vs. Reactive", "70%/30%", "+15% preventive vs. last year")
    
    with tab3:
        st.subheader("AI-Managed Preventive Maintenance")
        st.markdown("Your AI co-host automatically schedules and manages preventive maintenance based on manufacturer recommendations, usage patterns, and seasonal needs.")
        
        # Sample scheduled preventive maintenance
        preventive_data = {
            "Property": ["Seaside Villa", "Seaside Villa", "Mountain Retreat", "Mountain Retreat"],
            "Maintenance Type": ["HVAC Service", "Plumbing Inspection", "Roof Inspection", "Chimney Cleaning"],
            "Frequency": ["Every 6 months", "Annual", "Annual", "Annual"],
            "Last Done": ["Feb 15, 2023", "Jan 10, 2023", "Nov 5, 2022", "Oct 15, 2022"],
            "Next Scheduled": ["Aug 15, 2023", "Jan 10, 2024", "Nov 5, 2023", "Oct 15, 2023"],
            "Status": ["Due Soon", "Scheduled", "Scheduled", "Scheduled"]
        }
        
        df = pd.DataFrame(preventive_data)
        st.dataframe(df)
        
        st.divider()
        
        st.subheader("Add New Preventive Maintenance")
        
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Select Property", ["Seaside Villa", "Mountain Retreat"])
            st.text_input("Maintenance Description", "")
        with col2:
            st.selectbox("Frequency", ["Monthly", "Quarterly", "Every 6 months", "Annual", "Every 2 years"])
            st.date_input("First Scheduled Date")
        
        st.text_area("Notes for Service Provider")
        
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Estimated Cost", min_value=0, value=100)
        with col2:
            st.text_input("Preferred Service Provider")
        
        st.button("Schedule Preventive Maintenance", disabled=True)

def render_cleaning_management():
    st.title(get_text("cleaning_management_title", st.session_state.language))
    
    # Cleaning management introduction
    st.markdown("""
    <div style="padding: 20px; background-color: #f0f5ff; border-radius: 10px; margin-bottom: 20px;">
        <h3 style="color: #3366CC;">AI Cleaning Management</h3>
        <p>Your AI co-host automatically schedules and coordinates cleaning services based on guest check-ins and check-outs. 
        Ensure your property is always pristine with automated quality checks, cleaning verification, and inventory management.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Cleaning Schedule", "Cleaning Quality & Reports", "Inventory Management"])
    
    with tab1:
        st.subheader("Upcoming Cleaning Schedule")
        
        # Sample cleaning schedule
        cleaning_data = {
            "Property": ["Seaside Villa", "Mountain Retreat", "Seaside Villa"],
            "Type": ["Checkout/Checkin", "Maintenance Cleaning", "Checkout/Checkin"],
            "Date": ["Aug 23, 2023", "Aug 25, 2023", "Aug 30, 2023"],
            "Time": ["11:00 AM - 2:00 PM", "10:00 AM - 12:00 PM", "11:00 AM - 2:00 PM"],
            "Status": ["Scheduled", "Scheduled", "Scheduled"],
            "Cleaning Service": ["CleanMasters", "MountainClean", "CleanMasters"],
            "Special Instructions": ["Deep clean bathroom", "None", "Replace all linens"]
        }
        
        df = pd.DataFrame(cleaning_data)
        st.dataframe(df)
        
        st.divider()
        
        # Automated scheduling feature
        st.subheader("AI Cleaning Scheduling")
        st.markdown("Your AI co-host automatically schedules cleanings based on bookings and property needs:")
        
        st.checkbox("Schedule cleaning after every checkout", value=True)
        st.checkbox("Schedule additional cleaning for longer stays (>7 days)", value=True)
        st.checkbox("Send reminder to cleaning service 24h before scheduled cleaning", value=True)
        st.checkbox("Request cleaning confirmation and photos", value=True)
        st.checkbox("Notify owner of completed cleanings", value=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Hours needed between checkout and next checkin", min_value=1, max_value=72, value=5)
        with col2:
            st.selectbox("Default cleaning service", ["CleanMasters", "MountainClean", "EcoClean"])
    
    with tab2:
        st.subheader("Cleaning Quality Management")
        st.markdown("Your AI co-host monitors cleaning quality and provides feedback:")
        
        # Sample cleaning reports
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Recent Cleaning Verification**")
            st.image("https://media.istockphoto.com/id/1356322272/photo/handsome-african-american-man-smiling-looking-at-his-cleaning-check-list-while-cleaning-at-home.jpg?s=612x612&w=0&k=20&c=wxc35yvzNnqqtM1WUYtCltCjXCcRZu8dHCGi4bTUkM0=", use_column_width=True)
            st.markdown("**Seaside Villa - August 15, 2023**")
            st.success("✅ Verification photos received")
            st.success("✅ All checklist items completed")
            st.success("✅ Cleaning verified by AI analysis")
        
        with col2:
            st.markdown("**Cleaning Quality Metrics**")
            st.metric("Average Cleaning Rating", "4.8/5", "+0.3 from last month")
            st.metric("Issues Detected by AI", "2%", "-3% from last month")
            st.metric("Guest Cleanliness Satisfaction", "96%", "+4% from last month")
            st.progress(96, text="Guest Satisfaction")
        
        st.divider()
        
        st.subheader("Cleaning Verification Process")
        st.markdown("""
        Your AI co-host verifies cleaning quality through:
        1. **Photo Verification**: Analyzing photos submitted by cleaning staff
        2. **Checklist Completion**: Ensuring all required tasks were completed
        3. **Guest Feedback**: Monitoring comments about cleanliness
        4. **Smart Home Integration**: Temperature, humidity, and air quality sensors
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("Download Cleaning Checklist", "Dummy data", disabled=True)
        with col2:
            st.button("View Cleaning History Report", disabled=True)
    
    with tab3:
        st.subheader("Inventory Management")
        st.markdown("Your AI co-host automatically tracks inventory and supplies:")
        
        # Inventory status
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Consumable Supplies**")
            
            supplies_data = {
                "Item": ["Toilet Paper", "Hand Soap", "Dishwasher Tablets", "Coffee Capsules", "Laundry Detergent"],
                "Current Stock": ["12 rolls", "3 bottles", "15 tablets", "24 capsules", "1 bottle"],
                "Status": ["Adequate", "Low", "Adequate", "Adequate", "Low"],
                "Auto-Order": ["Yes", "Yes", "Yes", "Yes", "Yes"]
            }
            
            df = pd.DataFrame(supplies_data)
            st.dataframe(df)
        
        with col2:
            st.markdown("**Linen Inventory**")
            
            linen_data = {
                "Item": ["Bed Sheets", "Pillowcases", "Bath Towels", "Hand Towels", "Kitchen Towels"],
                "Total Inventory": ["12 sets", "16 pieces", "20 pieces", "12 pieces", "10 pieces"],
                "In Use/Laundering": ["4 sets", "6 pieces", "8 pieces", "4 pieces", "4 pieces"],
                "Available": ["8 sets", "10 pieces", "12 pieces", "8 pieces", "6 pieces"]
            }
            
            df = pd.DataFrame(linen_data)
            st.dataframe(df)
        
        st.divider()
        
        st.subheader("AI Inventory Management")
        st.markdown("Your AI co-host automatically manages inventory:")
        
        st.checkbox("Track inventory usage by cleaning staff", value=True)
        st.checkbox("Automatically reorder supplies when low", value=True)
        st.checkbox("Send inventory alerts to owner", value=True)
        st.checkbox("Generate monthly inventory reports", value=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Preferred Supplier", "SupplyMaster Inc.")
        with col2:
            st.selectbox("Reorder Frequency", ["As needed", "Weekly", "Bi-weekly", "Monthly"])
        
        st.button("Update Inventory", disabled=True)

# Client-facing pages
def preprocess_user_input(text):
    """Process user input to detect booking intent and extract info"""
    text = text.lower()
    
    booking_intent = any(word in text for word in [
        "prenot", "book", "affitt", "rent", "stanz", "room", "alloggi", 
        "allogg", "soggiorn", "stay", "dormir", "sleep"
    ])
    
    # Extract potential dates
    dates = re.findall(r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b', text)
    dates += re.findall(r'\b\d{1,2}\s+(?:gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre|january|february|march|april|may|june|july|august|september|october|november|december|gen|feb|mar|apr|mag|giu|lug|ago|set|ott|nov|dic|jan|aug|oct|dec)\s+\d{2,4}\b', text, re.IGNORECASE)
    
    # Extract cities
    cities = []
    city_keywords = ["milano", "milan", "roma", "rome", "napoli", "naples", "portici", "firenze", "florence"]
    for city in city_keywords:
        if city in text.lower():
            cities.append(city)
    
    # Extract guest count 
    guest_count = None
    for match in re.finditer(r'(\d+)\s+(?:person|ospiti|guests?|persone)', text, re.IGNORECASE):
        guest_count = int(match.group(1))
    
    # Extract name
    name_match = re.search(r'(?:mi chiamo|sono|name is|chiamarsi)\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)', text, re.IGNORECASE)
    name = name_match.group(1) if name_match else None
    
    # Extract email
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    email = email_match.group(0) if email_match else None
    
    # Extract phone
    phone_match = re.search(r'(?:\+\d{1,3}[-\s]?)?\(?\d{3,4}\)?[-\s]?\d{3}[-\s]?\d{3,4}', text)
    phone = phone_match.group(0) if phone_match else None
    
    return {
        "booking_intent": booking_intent,
        "dates": dates,
        "cities": cities,
        "guest_count": guest_count,
        "name": name,
        "email": email,
        "phone": phone
    }

def update_booking_data(extracted_info):
    """Update booking data based on extracted information"""
    # Update booking data in session state based on extracted info
    if extracted_info["name"] and not st.session_state.booking_data["guest_name"]:
        st.session_state.booking_data["guest_name"] = extracted_info["name"]
    
    if extracted_info["email"] and not st.session_state.booking_data["guest_email"]:
        st.session_state.booking_data["guest_email"] = extracted_info["email"]
    
    if extracted_info["phone"] and not st.session_state.booking_data["guest_phone"]:
        st.session_state.booking_data["guest_phone"] = extracted_info["phone"]
    
    if extracted_info["guest_count"] and not st.session_state.booking_data["guests_count"]:
        st.session_state.booking_data["guests_count"] = extracted_info["guest_count"]
    
    # If booking intent detected, advance the booking stage
    if extracted_info["booking_intent"] and st.session_state.booking_data["stage"] == "initial":
        st.session_state.booking_data["stage"] = "collecting_info"
        st.session_state.booking_in_progress = True

def generate_assistant_response(user_input, extracted_info):
    """Generate contextual response based on booking stage and extracted info"""
    booking_data = st.session_state.booking_data
    
    # Determine what information we still need
    missing_info = []
    if not booking_data["guest_name"]:
        missing_info.append("nome")
    if not booking_data["guest_email"]:
        missing_info.append("email")
    if not booking_data["check_in"]:
        missing_info.append("data di check-in")
    if not booking_data["check_out"]:
        missing_info.append("data di check-out")
    if not booking_data["guests_count"]:
        missing_info.append("numero di ospiti")
    if not booking_data["property_id"]:
        missing_info.append("proprietà desiderata")
    
    # Build context for the AI response
    properties = get_properties()
    
    # Filter properties based on selected city if any
    if extracted_info["cities"]:
        city_properties = []
        for city in extracted_info["cities"]:
            city_matches = [p for p in properties if city.lower() in p.get('city', '').lower()]
            city_properties.extend(city_matches)
        if city_properties:
            properties = city_properties
    
    properties_context = ""
    for prop in properties[:6]:  # Limit to avoid too long context
        city = prop.get('city', 'Italia')
        properties_context += f"- {prop['name']}: {prop['bedrooms']} camere, {prop['bathrooms']} bagni, {format_currency(prop['price_per_night'])}/notte, {city}, {prop['description'][:100]}...\n"
    
    # Build AI prompt based on booking stage
    if booking_data["stage"] == "initial":
        if extracted_info["booking_intent"]:
            prompt = f"""
            Sei un assistente AI di prenotazione intelligente per CiaoHost. L'utente ha espresso interesse a prenotare. 
            Rispondi in modo conversazionale, in italiano, aiutando ad avviare una prenotazione.
            
            Input utente: {user_input}
            
            Informazioni estratte: {extracted_info}
            
            Proprietà disponibili:
            {properties_context}
            
            Rispondi in modo amichevole e colloquiale, chiedendo le informazioni ancora necessarie per procedere con la prenotazione.
            Suggerisci opzioni basate sulle città/date menzionate se disponibili, oppure proponendo le proprietà popolari.
            
            IMPORTANTE: Non usare il formato "Assistant:" nella tua risposta. Rispondi direttamente come faresti in una conversazione naturale.
            """
        else:
            prompt = f"""
            Sei un assistente AI di prenotazione intelligente per CiaoHost. L'utente ha fatto una domanda generale.
            
            Input utente: {user_input}
            
            Proprietà disponibili:
            {properties_context}
            
            Rispondi in modo amichevole e colloquiale in italiano, fornendo informazioni utili e cercando di capire se l'utente è interessato a prenotare.
            Se appropriate, chiedi delicatamente in quali città italiane stanno cercando alloggio e in quali date.
            
            IMPORTANTE: Non usare il formato "Assistant:" nella tua risposta. Rispondi direttamente come faresti in una conversazione naturale.
            """
    
    elif booking_data["stage"] == "collecting_info":
        prompt = f"""
        Sei un assistente AI di prenotazione intelligente per CiaoHost. L'utente sta fornendo informazioni per una prenotazione.
        
        Input utente: {user_input}
        
        Informazioni estratte: {extracted_info}
        
        Informazioni di prenotazione attuali:
        - Nome: {booking_data["guest_name"] or "Non fornito"}
        - Email: {booking_data["guest_email"] or "Non fornita"}
        - Telefono: {booking_data["guest_phone"] or "Non fornito"}
        - Check-in: {booking_data["check_in"] or "Non fornito"}
        - Check-out: {booking_data["check_out"] or "Non fornito"}
        - Numero ospiti: {booking_data["guests_count"] or "Non fornito"}
        - Proprietà: {booking_data["property_id"] or "Non selezionata"}
        
        Proprietà disponibili:
        {properties_context}
        
        Informazioni mancanti: {", ".join(missing_info) if missing_info else "Nessuna"}
        
        Rispondi in modo amichevole e colloquiale in italiano, ringraziando per le informazioni fornite e chiedendo gentilmente quelle ancora mancanti.
        Se l'utente non ha ancora scelto una proprietà, suggerisci quelle più adatte in base alle preferenze emerse.
        
        IMPORTANTE: Non usare il formato "Assistant:" nella tua risposta. Rispondi direttamente come faresti in una conversazione naturale.
        """
    
    elif booking_data["stage"] == "confirmation":
        # Get property details for confirmation
        property_details = next((p for p in properties if p['id'] == booking_data["property_id"]), None)
        property_name = property_details['name'] if property_details else "proprietà selezionata"
        
        prompt = f"""
        Sei un assistente AI di prenotazione intelligente per CiaoHost. La prenotazione è pronta per la conferma.
        
        Input utente: {user_input}
        
        Dettagli prenotazione:
        - Nome ospite: {booking_data["guest_name"]}
        - Email: {booking_data["guest_email"]}
        - Telefono: {booking_data["guest_phone"]}
        - Proprietà: {property_name}
        - Check-in: {booking_data["check_in"]}
        - Check-out: {booking_data["check_out"]}
        - Numero ospiti: {booking_data["guests_count"]}
        
        Rispondi in modo amichevole e colloquiale in italiano, chiedendo all'utente di confermare i dettagli della prenotazione.
        Se confermano, informali che la prenotazione è stata registrata e che riceveranno presto un'email di conferma.
        
        IMPORTANTE: Non usare il formato "Assistant:" nella tua risposta. Rispondi direttamente come faresti in una conversazione naturale.
        """
    
    else:  # completed or other states
        prompt = f"""
        Sei un assistente AI di prenotazione intelligente per CiaoHost.
        
        Input utente: {user_input}
        
        La prenotazione è stata completata. L'utente potrebbe avere domande di follow-up.
        
        Rispondi in modo amichevole e colloquiale in italiano, fornendo assistenza per qualsiasi domanda post-prenotazione.
        Ricorda all'utente che riceveranno presto istruzioni dettagliate per il check-in via email.
        
        IMPORTANTE: Non usare il formato "Assistant:" nella tua risposta. Rispondi direttamente come faresti in una conversazione naturale.
        """
    
    # Get response from Llama
    response = get_llama_response(prompt, st.session_state.llama_model, st.session_state.language)
    
    return response

def handle_property_selection(property_id):
    """Handle when a user selects a property through buttons"""
    st.session_state.booking_data["property_id"] = property_id
    if st.session_state.booking_data["stage"] == "initial":
        st.session_state.booking_data["stage"] = "collecting_info"
        st.session_state.booking_in_progress = True
    
    # Add system message to chat history
    property_details = get_property_details(property_id)
    
    if property_details:
        # Extract address to get city if 'city' field is not directly available
        address = property_details.get('address', '')
        city = property_details.get('city', '')
        
        # If city is not available, try to extract from address
        if not city and ',' in address:
            city = address.split(',')[-1].strip()
        elif not city:
            city = "Italia"  # Default fallback
            
        system_msg = f"Ho selezionato {property_details['name']} a {city}. Prezzo: {format_currency(property_details['price_per_night'])} per notte."
        st.session_state.chat_history_client.append({"role": "system", "content": system_msg})
        
        # Also add assistant response
        assistant_response = f"Ottima scelta! {property_details['name']} è una sistemazione fantastica a {city}. Per procedere con la prenotazione, avrei bisogno di alcune informazioni. Potresti dirmi le date di check-in e check-out che preferisci, e per quante persone è la prenotazione?"
        st.session_state.chat_history_client.append({"role": "assistant", "content": assistant_response})

def render_client_chat():
    st.title(get_text("client_view_title", st.session_state.language))
    
    # AI Booking Assistant introduction
    st.markdown(f"""
    <div style="padding: 20px; background-color: #d32f2f; border-radius: 10px; margin-bottom: 20px; color: white;">
        <h3 style="color: #ffffff; font-weight: bold;">{get_text("smart_assistant", st.session_state.language)}</h3>
        <p style="color: #ffffff; font-size: 16px;">CiaoHost offre un assistente AI che gestisce automaticamente tutto il processo di prenotazione.
        Prova a chiedere informazioni, prenotare un alloggio o avere assistenza specifica per la tua vacanza in Italia.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # City filter
    st.subheader("Filtra per città")
    
    cities = ["Tutte", "Milano", "Roma", "Napoli", "Portici"]
    
    city_cols = st.columns(len(cities))
    
    for i, city in enumerate(cities):
        with city_cols[i]:
            if st.button(city, key=f"city_{city}"):
                st.session_state.selected_city = city
                st.rerun()
    
    # Show featured properties filtered by city
    st.markdown(f"""
    <h3 style="color: #003366; font-weight: bold; margin-top: 20px; border-bottom: 2px solid #003366; padding-bottom: 5px;">
        {"Proprietà in Evidenza" if st.session_state.selected_city == "Tutte" else f"Proprietà a {st.session_state.selected_city}"}
    </h3>
    """, unsafe_allow_html=True)
    
    # Get properties for display
    properties = get_properties()
    
    # Filter properties by city if a specific city is selected
    if st.session_state.selected_city != "Tutte":
        properties = [p for p in properties if st.session_state.selected_city.lower() in p.get('city', '').lower()]
    
    # Display property cards in two columns
    if properties:
        col1, col2 = st.columns(2)
        
        for i, property_data in enumerate(properties):
            with col1 if i % 2 == 0 else col2:
                with st.container(border=True):
                    st.subheader(property_data['name'])
                    st.write(f"**Posizione:** {property_data['address']}")
                    st.write(f"**Caratteristiche:** {property_data['bedrooms']} camere, {property_data['bathrooms']} bagni")
                    st.write(f"**Prezzo:** {format_currency(property_data['price_per_night'])}/notte")
                    st.write(f"**Servizi:** {', '.join(property_data['amenities'][:3])}...")
                    
                    # Add "Prenota" button that initiates a chatbot-guided booking
                    if st.button(f"Prenota: {property_data['name']}", key=f"book_{property_data['id']}"):
                        handle_property_selection(property_data['id'])
                        st.rerun()
    else:
        st.info(f"Nessuna proprietà disponibile a {st.session_state.selected_city}")
    
    st.divider()
    
    # Initialize chat history if needed
    if "chat_history_client" not in st.session_state:
        st.session_state.chat_history_client = []
    
    # Chat interface container with custom styles
    chat_container = st.container(height=400)
    st.markdown("""
    <style>
    .chat-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        border: 2px solid #003366;
        padding: 15px;
        margin-bottom: 20px;
    }
    .stChatMessage {
        background-color: white !important;
        border: 1px solid #e6e6e6 !important;
        padding: 10px !important;
        border-radius: 8px !important;
        margin-bottom: 10px !important;
    }
    .stChatMessage .content {
        color: #333333 !important;
        font-size: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with chat_container:
        # Display chat header
        st.subheader("Parla con il nostro Assistente AI")
        
        # If empty, show a welcome message
        if not st.session_state.chat_history_client:
            with st.chat_message("assistant", avatar="🤖"):
                welcome_text = get_text("chat_welcome", st.session_state.language)
                st.write(welcome_text)
        else:
            # Display chat history
            for message in st.session_state.chat_history_client:
                if message["role"] == "system":
                    # System messages displayed as info boxes
                    st.info(message["content"])
                else:
                    avatar = "🤖" if message["role"] == "assistant" else "👤"
                    with st.chat_message(message["role"], avatar=avatar):
                        st.write(message["content"])
    
    # Chat input below the container
    prompt = st.chat_input("Scrivi qui la tua domanda...")
    
    if prompt:
        # Process user input
        extracted_info = preprocess_user_input(prompt)
        
        # Update booking data with extracted information
        update_booking_data(extracted_info)
        
        # Add user message to chat history
        st.session_state.chat_history_client.append({"role": "user", "content": prompt})
        
        # Generate AI response
        response = generate_assistant_response(prompt, extracted_info)
        
        # Add assistant response to chat history
        st.session_state.chat_history_client.append({"role": "assistant", "content": response})
        
        # Advance booking stage if all required info is collected
        booking_data = st.session_state.booking_data
        if (booking_data["stage"] == "collecting_info" and 
            booking_data["guest_name"] and 
            booking_data["guest_email"] and 
            booking_data["property_id"] and 
            booking_data["check_in"] and 
            booking_data["check_out"] and 
            booking_data["guests_count"]):
            
            st.session_state.booking_data["stage"] = "confirmation"
            
            # Add system message with booking summary
            property_details = get_property_details(booking_data["property_id"])
            if property_details:
                property_name = property_details['name']
                total_price = property_details['price_per_night'] * 3  # Assuming 3 nights as placeholder
                
                summary = f"""
                **Riepilogo Prenotazione:**
                - Proprietà: {property_name}
                - Check-in: {booking_data['check_in']}
                - Check-out: {booking_data['check_out']}
                - Ospiti: {booking_data['guests_count']}
                - Nome: {booking_data['guest_name']}
                - Email: {booking_data['guest_email']}
                - Prezzo totale stimato: {format_currency(total_price)}
                """
                
                st.session_state.chat_history_client.append({"role": "system", "content": summary})
        
        # Immediately rerun to show the updated chat
        st.rerun()

def render_client_reservation():
    st.title(get_text("make_reservation", st.session_state.language))
    
    # Reservation form
    st.markdown("""
    <div style="padding: 20px; background-color: #f0f5ff; border-radius: 10px; margin-bottom: 20px;">
        <h3 style="color: #3366CC;">Easy Online Booking</h3>
        <p>Complete the form below to make your reservation. Our AI assistant will guide you through the process
        and ensure your booking details are correct.</p>
    </div>
    """, unsafe_allow_html=True)
    
    properties = get_properties()
    
    with st.form("booking_form"):
        # Property selection
        property_options = {p['id']: p['name'] for p in properties}
        selected_property = st.selectbox(
            "Select Property",
            options=list(property_options.keys()),
            format_func=lambda x: property_options[x]
        )
        
        selected_property_data = next((p for p in properties if p['id'] == selected_property), None)
        
        if selected_property_data:
            st.write(f"Price per night: {format_currency(selected_property_data['price_per_night'])}")
        
        # Dates
        col1, col2 = st.columns(2)
        with col1:
            check_in = st.date_input("Check-in Date", min_value=datetime.datetime.now().date())
        with col2:
            check_out = st.date_input("Check-out Date", min_value=check_in + datetime.timedelta(days=1))
        
        # Calculate nights and total price
        if check_in and check_out and selected_property_data:
            nights = (check_out - check_in).days
            total_price = nights * selected_property_data['price_per_night']
            st.write(f"Total nights: {nights}")
            st.write(f"Total price: {format_currency(total_price)}")
        
        # Guest information
        st.subheader("Guest Information")
        
        col1, col2 = st.columns(2)
        with col1:
            guest_name = st.text_input("Full Name")
        with col2:
            guest_email = st.text_input("Email Address")
        
        col1, col2 = st.columns(2)
        with col1:
            guest_phone = st.text_input("Phone Number")
        with col2:
            guest_count = st.number_input("Number of Guests", min_value=1, max_value=10, value=2)
        
        special_requests = st.text_area("Special Requests (optional)")
        
        # Terms and conditions
        st.checkbox("I agree to the terms and conditions", key="terms_agreed")
        
        # Submit button
        submit_button = st.form_submit_button("Complete Reservation")
    
    if submit_button:
        # This would normally create the booking in the database
        # For demo purposes, show a success message and booking details
        st.success("Booking request received! Our AI assistant is processing your reservation.")
        
        # Simulate AI processing
        with st.spinner("AI co-host processing your booking..."):
            time.sleep(2)
        
        st.success("Your booking has been confirmed!")
        st.balloons()
        
        # Display confirmation details
        st.subheader("Booking Confirmation")
        st.write(f"**Property:** {property_options[selected_property]}")
        st.write(f"**Dates:** {check_in.strftime('%b %d, %Y')} to {check_out.strftime('%b %d, %Y')}")
        st.write(f"**Guest:** {guest_name}")
        st.write(f"**Total:** {format_currency(total_price)}")
        
        # Display next steps
        st.info("""
        **Next Steps:**
        1. You will receive a confirmation email shortly
        2. Our AI co-host will send check-in instructions 24 hours before arrival
        3. Digital access codes will be provided on the day of check-in
        """)

def render_client_properties():
    st.title(get_text("browse_properties", st.session_state.language))
    
    # Property browsing interface
    st.markdown("""
    <div style="padding: 20px; background-color: #f0f5ff; border-radius: 10px; margin-bottom: 20px;">
        <h3 style="color: #3366CC;">Find Your Perfect Stay</h3>
        <p>Browse our curated selection of properties. Use the filters to find the perfect match for your needs.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filters
    st.subheader("Filters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_price = st.slider("Min Price (€)", min_value=50, max_value=500, value=100, step=10)
    with col2:
        max_price = st.slider("Max Price (€)", min_value=min_price, max_value=500, value=300, step=10)
    with col3:
        bedrooms = st.select_slider("Bedrooms", options=["Any", "1+", "2+", "3+", "4+"], value="Any")
    
    # Amenities filter
    st.multiselect("Amenities", options=["WiFi", "Pool", "Kitchen", "Air Conditioning", "Parking", "Washer", "Dryer", "Fireplace"], default=[])
    
    # Get properties
    properties = get_properties()
    
    # Filter properties based on criteria
    filtered_properties = [
        p for p in properties 
        if p['price_per_night'] >= min_price and p['price_per_night'] <= max_price
    ]
    
    # If no bedroom filter is set to "Any"
    if bedrooms != "Any":
        min_bedrooms = int(bedrooms[0])
        filtered_properties = [p for p in filtered_properties if p['bedrooms'] >= min_bedrooms]
    
    # Display filtered properties
    st.subheader(f"Properties ({len(filtered_properties)})")
    
    for property_data in filtered_properties:
        with st.container(border=True):
            col1, col2 = st.columns([2, 3])
            
            with col1:
                # This would normally be an image of the property
                st.image("https://images.unsplash.com/photo-1580587771525-78b9dba3b914?q=80&w=500", 
                         use_column_width=True, caption=property_data['name'])
            
            with col2:
                st.subheader(property_data['name'])
                st.write(f"**Location:** {property_data['address']}")
                st.write(f"**{property_data['bedrooms']} bedrooms, {property_data['bathrooms']} bathrooms**")
                st.write(f"**Price:** {format_currency(property_data['price_per_night'])}/night")
                st.write(f"**Amenities:** {', '.join(property_data['amenities'])}")
                st.write(property_data['description'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.button(f"Book Now: {property_data['name']}", key=f"book_{property_data['id']}")
                with col2:
                    st.button(f"More Details: {property_data['name']}", key=f"details_{property_data['id']}")

def render_client_availability():
    st.title(get_text("check_availability", st.session_state.language))
    
    # Availability checker
    st.markdown("""
    <div style="padding: 20px; background-color: #f0f5ff; border-radius: 10px; margin-bottom: 20px;">
        <h3 style="color: #3366CC;">Check Property Availability</h3>
        <p>Enter your desired dates to check availability across all our properties. 
        Our AI assistant will help you find available options that match your criteria.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input("Check-in Date", min_value=datetime.datetime.now().date())
    with col2:
        end_date = st.date_input("Check-out Date", min_value=start_date + datetime.timedelta(days=1))
    with col3:
        guests = st.number_input("Number of Guests", min_value=1, max_value=10, value=2)
    
    if st.button("Check Availability", use_container_width=True):
        st.success(f"Checking availability for {(end_date - start_date).days} nights from {start_date.strftime('%b %d, %Y')} for {guests} guests")
        
        with st.spinner("AI assistant is searching for available properties..."):
            time.sleep(2)
        
        # Get all properties and bookings
        properties = get_properties()
        bookings = get_bookings()
        
        # This would normally check the database for conflicts
        # For demo purposes, randomly mark some properties as available
        available_properties = []
        for prop in properties:
            # Simple algorithm to simulate availability
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            # Check for booking conflicts
            conflicts = False
            for booking in bookings:
                if booking['property_id'] == prop['id']:
                    booking_check_in = pd.to_datetime(booking['check_in']).date()
                    booking_check_out = pd.to_datetime(booking['check_out']).date()
                    
                    # Check if dates overlap
                    if (start_date <= booking_check_out and end_date >= booking_check_in):
                        conflicts = True
                        break
            
            if not conflicts:
                available_properties.append(prop)
        
        # Display available properties
        if available_properties:
            st.subheader(f"{len(available_properties)} Properties Available")
            
            for property_data in available_properties:
                with st.container(border=True):
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        # Calculate total price
                        nights = (end_date - start_date).days
                        total_price = nights * property_data['price_per_night']
                        
                        st.subheader(property_data['name'])
                        st.write(f"**{nights} nights:** {format_currency(total_price)}")
                        st.write(f"**Per night:** {format_currency(property_data['price_per_night'])}")
                    
                    with col2:
                        st.write(f"**Location:** {property_data['address']}")
                        st.write(f"**{property_data['bedrooms']} bedrooms, {property_data['bathrooms']} bathrooms**")
                        st.write(f"**Amenities:** {', '.join(property_data['amenities'][:3])}")
                    
                    st.button(f"Book {property_data['name']}", key=f"avail_book_{property_data['id']}")
        else:
            st.warning("No properties available for the selected dates")
            st.write("Try different dates or browse our properties for availability")

def render_client_support():
    st.title(get_text("contact_support", st.session_state.language))
    
    # Contact support
    st.markdown("""
    <div style="padding: 20px; background-color: #f0f5ff; border-radius: 10px; margin-bottom: 20px;">
        <h3 style="color: #3366CC;">Get Help from Our AI Support</h3>
        <p>Our AI assistant is ready to help you with any questions or concerns. 
        Just start chatting below or browse through our frequently asked questions.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # FAQ section
    with st.expander("Frequently Asked Questions"):
        st.subheader("Booking & Cancellation")
        st.markdown("""
        **What is your cancellation policy?**  
        You can cancel for free up to 7 days before check-in. After that, the first night is non-refundable.
        
        **How do I modify my reservation?**  
        You can modify your reservation by contacting our AI assistant through chat or email.
        
        **Is there a security deposit?**  
        Yes, a refundable security deposit of €200 is required for all bookings.
        """)
        
        st.subheader("Check-in & Check-out")
        st.markdown("""
        **What are the check-in and check-out times?**  
        Check-in is from 2:00 PM to 8:00 PM. Check-out is by 11:00 AM.
        
        **How do I get the keys to the property?**  
        Our AI co-host will send you digital access codes 24 hours before your arrival.
        
        **Can I check in early or check out late?**  
        Early check-in and late check-out may be available upon request, subject to availability.
        """)
    
    # Live support chat
    st.subheader("Live Support Chat")
    
    # Initialize support chat history
    if "support_chat" not in st.session_state:
        st.session_state.support_chat = [
            {"role": "assistant", "content": "Hi there! I'm your AI support assistant. How can I help you today?"}
        ]
    
    # Display chat history
    for message in st.session_state.support_chat:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    support_prompt = st.chat_input("Ask your question here...")
    
    if support_prompt:
        # Add user message to chat history
        st.session_state.support_chat.append({"role": "user", "content": support_prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(support_prompt)
        
        # Get AI response with support context
        with st.chat_message("assistant"):
            with st.spinner(get_text("thinking", st.session_state.language)):
                # Add support context to the model
                support_context = f"""
                As a support assistant for CiaoHost B&B properties, help the user with: {support_prompt}
                
                Common policies:
                - Check-in: 2:00 PM to 8:00 PM
                - Check-out: by 11:00 AM
                - Cancellation: Free up to 7 days before check-in
                - Security deposit: €200 (refundable)
                - Pets: Only allowed in certain properties with prior approval
                - Smoking: Not allowed in any properties
                
                Contact information:
                - Email: support@ciaohost.com
                - Phone: +39 123 456 7890
                - Address: Via Roma 123, Rome, Italy
                """
                
                response = get_llama_response(support_context, st.session_state.llama_model, st.session_state.language)
                st.write(response)
        
        # Add assistant response to chat history
        st.session_state.support_chat.append({"role": "assistant", "content": response})

# Render the appropriate page based on current_page in session state
if st.session_state.user_mode == 'owner':
    # Owner pages
    if st.session_state.current_page == 'dashboard':
        render_dashboard()
    elif st.session_state.current_page == 'properties':
        render_properties()
    elif st.session_state.current_page == 'bookings':
        render_bookings()
    elif st.session_state.current_page == 'communication':
        render_communication()
    elif st.session_state.current_page == 'ai_cohost':
        render_ai_cohost()
    elif st.session_state.current_page == 'automated_checkin':
        render_automated_checkin()
    elif st.session_state.current_page == 'automated_bookings':
        render_automated_bookings()
    elif st.session_state.current_page == 'automated_maintenance':
        render_automated_maintenance()
    elif st.session_state.current_page == 'cleaning_management':
        render_cleaning_management()
else:
    # Client pages
    if st.session_state.current_page == 'client_chat':
        render_client_chat()
    elif st.session_state.current_page == 'client_reservation':
        render_client_reservation()
    elif st.session_state.current_page == 'client_properties':
        render_client_properties()
    elif st.session_state.current_page == 'client_availability':
        render_client_availability()
    elif st.session_state.current_page == 'client_support':
        render_client_support()
