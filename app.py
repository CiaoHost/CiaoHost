import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import json
from utils.database import initialize_session_state_from_db, get_all_properties, get_all_bookings
from utils.pdf_export import create_property_report_pdf, create_financial_report_pdf

# Set page configuration
st.set_page_config(
    page_title="CiaoHost - Gestione Immobili B&B",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inizializza directory dati
os.makedirs('data', exist_ok=True)

# Initialize session state variables
if 'properties' not in st.session_state:
    # Load sample properties or create empty list
    if os.path.exists('data/properties.json'):
        with open('data/properties.json', 'r', encoding='utf-8') as f:
            st.session_state.properties = json.load(f)
    else:
        st.session_state.properties = []

if 'bookings' not in st.session_state:
    # Load sample bookings or create empty list
    if os.path.exists('data/bookings.json'):
        with open('data/bookings.json', 'r', encoding='utf-8') as f:
            st.session_state.bookings = json.load(f)
    else:
        st.session_state.bookings = []

if 'chatbot_history' not in st.session_state:
    st.session_state.chatbot_history = {}

if 'active_conversations' not in st.session_state:
    st.session_state.active_conversations = {}

if 'current_page' not in st.session_state:
    st.session_state.current_page = "dashboard"

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #1976D2;
        font-weight: bold;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .dashboard-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 10px rgba(0,0,0,0.1);
    }
    .highlight {
        color: #1E88E5;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
        border-radius: 4px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1565C0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0 0;
        font-weight: 500;
        background-color: #f0f2f6;
        border-bottom-color: #1E88E5;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5 !important;
        color: white !important;
    }
    div.stSidebar [data-testid="stSidebarNav"] {
        background-color: #f8f9fa;
        padding-top: 1rem;
        border-radius: 10px;
    }
    div.stSidebar [data-testid="stSidebarNav"]>ul {
        padding-left: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Save logo to data directory
import shutil
os.makedirs('data', exist_ok=True)
logo_src = 'attached_assets/CiaoHost-removebg-preview.png'
logo_dest = 'data/logo.png'
if os.path.exists(logo_src) and not os.path.exists(logo_dest):
    shutil.copy(logo_src, logo_dest)

# Sidebar navigation with logo
if os.path.exists(logo_dest):
    st.sidebar.image(logo_dest, width=200)
else:
    st.sidebar.markdown("<h1 style='text-align: center;'>🏠 CiaoHost</h1>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Navigation menu
menu_options = {
    "dashboard": "📊 Dashboard",
    "properties": "🏘️ Gestione Immobili",
    "bookings": "📅 Prenotazioni",
    "co_host": "🤖 Co-Host Virtuale",
    "pricing": "💰 Prezzi Dinamici",
    "cleaning": "🧹 Gestione Pulizie",
    "fiscal": "📑 Archivio Fiscale",
    "settings": "⚙️ Impostazioni"
}

selected_page = st.sidebar.radio("Navigazione", list(menu_options.values()))

# Set current page based on selection
for key, value in menu_options.items():
    if value == selected_page:
        st.session_state.current_page = key

# Display user information in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("👤 **Utente:** Demo")
st.sidebar.markdown("📈 **Piano:** Pro")
st.sidebar.markdown("---")

# Function to save data (would connect to database in production)
def save_data():
    os.makedirs('data', exist_ok=True)
    with open('data/properties.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.properties, f, ensure_ascii=False, indent=4)
    with open('data/bookings.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.bookings, f, ensure_ascii=False, indent=4)

# Export section in sidebar
st.sidebar.markdown("### Esportazione Rapporti")
report_type = st.sidebar.selectbox(
    "Tipo di Rapporto",
    ["Riepilogo Finanziario", "Report Immobile", "Report Prenotazioni"]
)

# Date range for reports
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.sidebar.date_input(
        "Data Inizio",
        value=(datetime.now() - timedelta(days=30)).date()
    )
with col2:
    end_date = st.sidebar.date_input(
        "Data Fine",
        value=datetime.now().date()
    )

if st.sidebar.button("Genera PDF"):
    if report_type == "Riepilogo Finanziario":
        # Create financial report
        pdf_buffer = create_financial_report_pdf(
            st.session_state.bookings, 
            period={"start_date": start_date.strftime("%Y-%m-%d"), "end_date": end_date.strftime("%Y-%m-%d")},
            properties_data=st.session_state.properties
        )
        
        # Download button
        st.sidebar.download_button(
            label="Scarica PDF",
            data=pdf_buffer,
            file_name=f"report_finanziario_{start_date}_{end_date}.pdf",
            mime="application/pdf"
        )
    elif report_type == "Report Immobile":
        if st.session_state.properties:
            # Property selection
            property_options = {p.get("id"): p.get("name") for p in st.session_state.properties}
            selected_property_id = st.sidebar.selectbox(
                "Seleziona Immobile",
                options=list(property_options.keys()),
                format_func=lambda x: property_options.get(x)
            )
            
            if selected_property_id:
                # Get property and related bookings
                property_data = next((p for p in st.session_state.properties if p.get("id") == selected_property_id), None)
                related_bookings = [b for b in st.session_state.bookings if b.get("property_id") == selected_property_id]
                
                # Create property report
                pdf_buffer = create_property_report_pdf(
                    property_data,
                    related_bookings,
                    period={"start_date": start_date.strftime("%Y-%m-%d"), "end_date": end_date.strftime("%Y-%m-%d")}
                )
                
                # Download button
                st.sidebar.download_button(
                    label="Scarica PDF",
                    data=pdf_buffer,
                    file_name=f"report_immobile_{property_data.get('name')}_{start_date}_{end_date}.pdf",
                    mime="application/pdf"
                )
        else:
            st.sidebar.warning("Non hai ancora registrato immobili.")
    elif report_type == "Report Prenotazioni":
        st.sidebar.info("In un'applicazione completa, qui verrebbe generato un report delle prenotazioni.")

# Main content based on selected page
if st.session_state.current_page == "dashboard":
    st.markdown("<h1 class='main-header'>Dashboard Host</h1>", unsafe_allow_html=True)
    
    # Summary metrics in beautiful cards
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Immobili", len(st.session_state.properties))
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        active_bookings = len([b for b in st.session_state.bookings if b.get("status") == "attiva"])
        st.metric("Prenotazioni Attive", active_bookings)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        # Calculate occupancy rate
        total_days = 0
        booked_days = 0
        for p in st.session_state.properties:
            total_days += 30  # Assuming 30 days for calculation
            for b in st.session_state.bookings:
                if b.get("property_id") == p.get("id") and b.get("status") in ["attiva", "confermata"]:
                    checkin_date = None
                    checkout_date = None
                    
                    if isinstance(b.get("checkin_date"), str):
                        try:
                            checkin_date = datetime.fromisoformat(b.get("checkin_date")).date()
                        except ValueError:
                            continue
                    else:
                        checkin_date = b.get("checkin_date")
                        
                    if isinstance(b.get("checkout_date"), str):
                        try:
                            checkout_date = datetime.fromisoformat(b.get("checkout_date")).date()
                        except ValueError:
                            continue
                    else:
                        checkout_date = b.get("checkout_date")
                    
                    if checkin_date and checkout_date:
                        diff_days = (checkout_date - checkin_date).days
                        if diff_days > 0:
                            booked_days += diff_days
        
        occupancy_rate = (booked_days / total_days * 100) if total_days > 0 else 0
        st.metric("Tasso Occupazione", f"{occupancy_rate:.1f}%")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        # Calculate monthly revenue
        monthly_revenue = sum([b.get("total_price", 0) for b in st.session_state.bookings 
                              if b.get("status") in ["attiva", "confermata", "completata"]])
        st.metric("Entrate Mensili", f"€{monthly_revenue:.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Recent bookings
    st.markdown("<h2 class='sub-header'>Prenotazioni Recenti</h2>", unsafe_allow_html=True)
    
    if st.session_state.bookings:
        # Convert dates if needed
        processed_bookings = []
        for booking in st.session_state.bookings:
            processed_booking = booking.copy()
            if isinstance(booking.get("checkin_date"), str):
                try:
                    processed_booking["checkin_date"] = datetime.fromisoformat(booking.get("checkin_date")).date()
                except ValueError:
                    continue
            if isinstance(booking.get("checkout_date"), str):
                try:
                    processed_booking["checkout_date"] = datetime.fromisoformat(booking.get("checkout_date")).date()
                except ValueError:
                    continue
            processed_bookings.append(processed_booking)
        
        # Sort bookings
        if processed_bookings:
            sorted_bookings = sorted(processed_bookings, key=lambda b: b.get("checkin_date", datetime.now().date()), reverse=True)
            
            # Create DataFrame
            bookings_df = pd.DataFrame(sorted_bookings)
            if not bookings_df.empty:
                # Convert property_id to property_name
                property_dict = {p["id"]: p["name"] for p in st.session_state.properties}
                bookings_df["property"] = bookings_df["property_id"].map(property_dict)
                
                # Select columns to display
                display_cols = ["guest_name", "property", "checkin_date", "checkout_date", "total_price", "status"]
                cols_in_df = [col for col in display_cols if col in bookings_df.columns]
                
                st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
                st.dataframe(bookings_df[cols_in_df].head(5), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
            st.info("Nessuna prenotazione registrata con date valide")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.info("Nessuna prenotazione registrata")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Properties overview
    st.markdown("<h2 class='sub-header'>Panoramica Immobili</h2>", unsafe_allow_html=True)
    
    if st.session_state.properties:
        # Create a dataframe with property details
        properties_overview = []
        for prop in st.session_state.properties:
            # Count active bookings for this property
            active_bookings = len([b for b in st.session_state.bookings 
                                 if b.get("property_id") == prop.get("id") and b.get("status") == "attiva"])
            
            # Calculate average rating
            ratings = [b.get("rating", 0) for b in st.session_state.bookings 
                      if b.get("property_id") == prop.get("id") and b.get("rating") is not None]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            
            properties_overview.append({
                "Nome": prop.get("name"),
                "Città": prop.get("city"),
                "Prezzo/Notte": f"€{prop.get('current_price', 0):.2f}",
                "Ospiti Max": prop.get("max_guests"),
                "Prenotazioni Attive": active_bookings,
                "Valutazione Media": f"{avg_rating:.1f}/5"
            })
        
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(properties_overview), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.info("Nessun immobile registrato")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Upcoming activities
    st.markdown("<h2 class='sub-header'>Attività Imminenti</h2>", unsafe_allow_html=True)
    
    today = datetime.today()
    upcoming_activities = []
    
    # Add check-ins
    for booking in st.session_state.bookings:
        if booking.get("status") == "confermata":
            checkin_date = booking.get("checkin_date")
            if isinstance(checkin_date, str):
                try:
                    checkin_date = datetime.fromisoformat(checkin_date).date()
                except ValueError:
                    continue
                
            if checkin_date and (checkin_date - today.date()).days <= 7:
                property_name = next((p.get("name") for p in st.session_state.properties 
                                    if p.get("id") == booking.get("property_id")), "Unknown")
                
                upcoming_activities.append({
                    "Data": checkin_date.strftime("%d/%m/%Y"),
                    "Attività": "Check-in",
                    "Dettagli": f"{booking.get('guest_name')} presso {property_name}",
                    "Stato": "Programmato"
                })
    
    # Add check-outs
    for booking in st.session_state.bookings:
        if booking.get("status") == "attiva":
            checkout_date = booking.get("checkout_date")
            if isinstance(checkout_date, str):
                try:
                    checkout_date = datetime.fromisoformat(checkout_date).date()
                except ValueError:
                    continue
                
            if checkout_date and (checkout_date - today.date()).days <= 7:
                property_name = next((p.get("name") for p in st.session_state.properties 
                                    if p.get("id") == booking.get("property_id")), "Unknown")
                
                upcoming_activities.append({
                    "Data": checkout_date.strftime("%d/%m/%Y"),
                    "Attività": "Check-out",
                    "Dettagli": f"{booking.get('guest_name')} presso {property_name}",
                    "Stato": "Programmato"
                })
    
    # Add cleaning activities
    for booking in st.session_state.bookings:
        if booking.get("status") == "attiva":
            checkout_date = booking.get("checkout_date")
            if isinstance(checkout_date, str):
                try:
                    checkout_date = datetime.fromisoformat(checkout_date).date()
                except ValueError:
                    continue
                
            if checkout_date:
                cleaning_date = checkout_date + timedelta(days=1)  # Schedule cleaning the day after checkout
                if (cleaning_date - today.date()).days <= 7:
                    property_name = next((p.get("name") for p in st.session_state.properties 
                                        if p.get("id") == booking.get("property_id")), "Unknown")
                    
                    upcoming_activities.append({
                        "Data": cleaning_date.strftime("%d/%m/%Y"),
                        "Attività": "Pulizia",
                        "Dettagli": f"Pulizia programmata per {property_name}",
                        "Stato": "Da confermare"
                    })
    
    if upcoming_activities:
        # Sort by date
        upcoming_df = pd.DataFrame(upcoming_activities)
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.dataframe(upcoming_df, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.info("Nessuna attività imminente per i prossimi 7 giorni")
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.current_page == "properties":
    from pages.property_management import show_property_management
    show_property_management()

elif st.session_state.current_page == "bookings":
    from pages.bookings import show_bookings
    show_bookings()

elif st.session_state.current_page == "co_host":
    from pages.virtual_co_host import show_virtual_co_host
    show_virtual_co_host()

elif st.session_state.current_page == "pricing":
    from pages.dynamic_pricing import show_dynamic_pricing
    show_dynamic_pricing()

elif st.session_state.current_page == "cleaning":
    from pages.cleaning_management import show_cleaning_management
    show_cleaning_management()

elif st.session_state.current_page == "fiscal":
    from pages.fiscal_management import show_fiscal_management
    show_fiscal_management()

elif st.session_state.current_page == "settings":
    from pages.settings import show_settings
    show_settings()

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center;'>© 2025 CiaoHost - Sistema di Gestione per Immobili a Breve Termine</p>", unsafe_allow_html=True)