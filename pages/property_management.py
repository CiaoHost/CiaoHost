import streamlit as st
import pandas as pd
import json
import uuid
from datetime import datetime
import os
from utils.ai_assistant import generate_property_description

def show_property_management():
    st.markdown("<h1 class='main-header'>Gestione Immobili</h1>", unsafe_allow_html=True)
    
    # Create tabs for different property management sections
    tabs = st.tabs(["Elenco Immobili", "Aggiungi Immobile", "Modifica Immobile"])
    
    with tabs[0]:
        show_property_list()
    
    with tabs[1]:
        add_new_property()
    
    with tabs[2]:
        edit_property()

def show_property_list():
    st.subheader("I Tuoi Immobili")
    
    if not st.session_state.properties:
        st.info("Non hai ancora registrato immobili. Vai alla scheda 'Aggiungi Immobile' per iniziare.")
        return
    
    # Create a DataFrame for better display
    property_list = []
    for prop in st.session_state.properties:
        # Count bookings for this property
        bookings_count = len([b for b in st.session_state.bookings if b.get("property_id") == prop.get("id")])
        
        property_list.append({
            "ID": prop.get("id"),
            "Nome": prop.get("name"),
            "Città": prop.get("city"),
            "Indirizzo": prop.get("address"),
            "Tipo": prop.get("type"),
            "Camere": prop.get("bedrooms"),
            "Bagni": prop.get("bathrooms"),
            "Ospiti Max": prop.get("max_guests"),
            "Prezzo Base": f"€{prop.get('base_price'):.2f}",
            "Prezzo Attuale": f"€{prop.get('current_price'):.2f}",
            "Prenotazioni": bookings_count,
            "Stato": prop.get("status", "Attivo")
        })
    
    df = pd.DataFrame(property_list)
    st.dataframe(df, use_container_width=True)
    
    # Property details expander
    st.subheader("Dettagli Immobile")
    selected_id = st.selectbox("Seleziona un immobile per vedere i dettagli", 
                              [p.get("name") for p in st.session_state.properties],
                              format_func=lambda x: x)
    
    if selected_id:
        selected_property = next((p for p in st.session_state.properties if p.get("name") == selected_id), None)
        
        if selected_property:
            with st.expander("Visualizza dettagli completi", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Nome:** {selected_property.get('name')}")
                    st.markdown(f"**Tipo:** {selected_property.get('type')}")
                    st.markdown(f"**Indirizzo:** {selected_property.get('address')}")
                    st.markdown(f"**Città:** {selected_property.get('city')}")
                    st.markdown(f"**Camere:** {selected_property.get('bedrooms')}")
                    st.markdown(f"**Bagni:** {selected_property.get('bathrooms')}")
                    st.markdown(f"**Capacità:** {selected_property.get('max_guests')} ospiti")
                
                with col2:
                    st.markdown(f"**Prezzo Base:** €{selected_property.get('base_price'):.2f}")
                    st.markdown(f"**Prezzo Attuale:** €{selected_property.get('current_price'):.2f}")
                    st.markdown(f"**Pulizie:** €{selected_property.get('cleaning_fee'):.2f}")
                    st.markdown(f"**Check-in:** {selected_property.get('check_in_instructions', 'N/A')}")
                    st.markdown(f"**WiFi:** {selected_property.get('wifi_details', 'N/A')}")
                    st.markdown(f"**Stato:** {selected_property.get('status', 'Attivo')}")
                
                st.markdown("### Descrizione")
                st.write(selected_property.get('description', 'Nessuna descrizione disponibile.'))
                
                st.markdown("### Servizi")
                amenities = selected_property.get('amenities', [])
                if amenities:
                    # Display amenities in a grid
                    amenity_cols = st.columns(3)
                    for i, amenity in enumerate(amenities):
                        amenity_cols[i % 3].markdown(f"✓ {amenity}")
                else:
                    st.info("Nessun servizio registrato.")
                
                # Property actions
                st.markdown("### Azioni")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Modifica", key="edit_selected"):
                        st.session_state.property_to_edit = selected_property.get("id")
                        st.rerun()
                
                with col2:
                    if st.button("Disattiva/Attiva", key="toggle_active"):
                        # Toggle active status
                        idx = next((i for i, p in enumerate(st.session_state.properties) 
                                  if p.get("id") == selected_property.get("id")), None)
                        
                        if idx is not None:
                            current_status = st.session_state.properties[idx].get("status", "Attivo")
                            new_status = "Inattivo" if current_status == "Attivo" else "Attivo"
                            st.session_state.properties[idx]["status"] = new_status
                            
                            # Save the updated data
                            save_data()
                            st.success(f"Stato dell'immobile aggiornato a: {new_status}")
                            st.rerun()
                
                with col3:
                    if st.button("Elimina", key="delete_selected"):
                        # Confirm deletion
                        st.warning("Sei sicuro di voler eliminare questo immobile?")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("Sì, elimina", key="confirm_delete"):
                                # Delete property
                                st.session_state.properties = [p for p in st.session_state.properties 
                                                            if p.get("id") != selected_property.get("id")]
                                
                                # Also remove related bookings
                                st.session_state.bookings = [b for b in st.session_state.bookings 
                                                          if b.get("property_id") != selected_property.get("id")]
                                
                                # Save the updated data
                                save_data()
                                st.success("Immobile eliminato con successo!")
                                st.rerun()
                        
                        with col2:
                            if st.button("No, annulla", key="cancel_delete"):
                                st.rerun()

def add_new_property():
    st.subheader("Aggiungi Nuovo Immobile")
    
    with st.form("add_property_form"):
        # Basic info
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nome Immobile*", placeholder="Es: Appartamento Centro Storico")
            property_type = st.selectbox("Tipo*", 
                                        ["Appartamento", "Casa", "Villa", "B&B", "Camera Privata", "Altro"])
            city = st.text_input("Città*", placeholder="Es: Napoli")
            address = st.text_input("Indirizzo*", placeholder="Es: Via Roma, 123")
        
        with col2:
            bedrooms = st.number_input("Camere da letto*", min_value=0, value=1)
            bathrooms = st.number_input("Bagni*", min_value=0.0, value=1.0, step=0.5)
            max_guests = st.number_input("Ospiti Massimi*", min_value=1, value=2)
            base_price = st.number_input("Prezzo Base per Notte (€)*", min_value=0.0, value=50.0)
            cleaning_fee = st.number_input("Costo Pulizie (€)", min_value=0.0, value=30.0)
        
        # Property details
        st.subheader("Dettagli Immobile")
        
        # Upload property photos
        st.subheader("Foto Immobile")
        uploaded_files = st.file_uploader("Carica Foto dell'Immobile", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
        
        if uploaded_files:
            st.success(f"Caricate {len(uploaded_files)} foto")
            
            # Display thumbnails of uploaded photos
            cols = st.columns(min(4, len(uploaded_files)))
            for i, uploaded_file in enumerate(uploaded_files):
                with cols[i % 4]:
                    st.image(uploaded_file, caption=f"Foto {i+1}", width=150)
        
        check_in_instructions = st.text_area("Istruzioni Check-in", placeholder="Es: Ritirare le chiavi presso...")
        wifi_details = st.text_input("Dettagli WiFi", placeholder="Es: Nome rete: xxx, Password: yyy")
        
        # Checkout instructions
        checkout_instructions = st.text_area("Istruzioni Check-out", placeholder="Es: Lasciare le chiavi sul tavolo...")
        
        # Amenities
        st.subheader("Servizi")
        amenities_options = ["WiFi", "Aria Condizionata", "Riscaldamento", "Cucina", "Lavatrice", 
                             "Asciugatrice", "TV", "Parcheggio", "Ascensore", "Piscina", 
                             "Palestra", "Colazione", "Vista Mare", "Terrazza", "Balcone"]
        
        # Display amenities in multiple columns
        amenities_cols = st.columns(3)
        selected_amenities = []
        
        for i, amenity in enumerate(amenities_options):
            if amenities_cols[i % 3].checkbox(amenity, key=f"amenity_{i}"):
                selected_amenities.append(amenity)
        
        # Description
        st.subheader("Descrizione")
        manual_description = st.text_area("Descrizione Manuale", 
                                        placeholder="Descrivi il tuo immobile...", 
                                        height=100)
        
        use_ai_description = st.checkbox("Genera descrizione con AI")
        
        # Submit button
        submit_button = st.form_submit_button("Aggiungi Immobile")
    
    # Outside the form
    if submit_button:
        # Validate required fields
        if not (name and property_type and city and address):
            st.error("Compila tutti i campi obbligatori (contrassegnati con *).")
            return
        
        # Generate property ID
        property_id = str(uuid.uuid4())
        
        # Process and save uploaded photos
        photos = []
        if uploaded_files:
            # Create directory for property photos
            photo_dir = os.path.join("data", "property_photos", property_id)
            os.makedirs(photo_dir, exist_ok=True)
            
            for i, file in enumerate(uploaded_files):
                file_ext = os.path.splitext(file.name)[1].lower()
                photo_path = os.path.join(photo_dir, f"photo_{i+1}{file_ext}")
                
                with open(photo_path, "wb") as f:
                    f.write(file.getbuffer())
                
                photos.append(photo_path)
                
        # Prepare property data
        property_data = {
            "id": property_id,
            "name": name,
            "type": property_type,
            "city": city,
            "address": address,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "max_guests": max_guests,
            "base_price": base_price,
            "current_price": base_price,  # Initially set to base price
            "cleaning_fee": cleaning_fee,
            "check_in_instructions": check_in_instructions,
            "wifi_details": wifi_details,
            "checkout_instructions": checkout_instructions if 'checkout_instructions' in locals() else "",
            "amenities": selected_amenities,
            "photos": photos,
            "status": "Attivo",
            "cleaning_contact": "",  # Will be set in cleaning management
            "created_at": datetime.now().isoformat()
        }
        
        # Generate AI description if requested
        if use_ai_description:
            with st.spinner("Generazione descrizione con AI in corso..."):
                try:
                    ai_description = generate_property_description(property_data)
                    property_data["description"] = ai_description
                except Exception as e:
                    st.error(f"Errore nella generazione della descrizione AI: {str(e)}")
                    property_data["description"] = manual_description
        else:
            property_data["description"] = manual_description
        
        # Add property to session state
        st.session_state.properties.append(property_data)
        
        # Save the updated data
        save_data()
        
        st.success(f"Immobile '{name}' aggiunto con successo!")
        st.rerun()

def edit_property():
    st.subheader("Modifica Immobile")
    
    # Check if we're editing a specific property
    property_to_edit_id = st.session_state.get("property_to_edit")
    
    # Property selection
    if not property_to_edit_id:
        if not st.session_state.properties:
            st.info("Non hai ancora registrato immobili. Vai alla scheda 'Aggiungi Immobile' per iniziare.")
            return
        
        property_to_edit_id = st.selectbox("Seleziona l'immobile da modificare",
                                         [p.get("id") for p in st.session_state.properties],
                                         format_func=lambda x: next((p.get("name") for p in st.session_state.properties if p.get("id") == x), x))
    
    # Get the selected property
    selected_property = next((p for p in st.session_state.properties if p.get("id") == property_to_edit_id), None)
    
    if not selected_property:
        st.error("Immobile non trovato.")
        return
    
    with st.form("edit_property_form"):
        # Basic info
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nome Immobile*", value=selected_property.get("name", ""))
            property_type = st.selectbox("Tipo*", 
                                        ["Appartamento", "Casa", "Villa", "B&B", "Camera Privata", "Altro"],
                                        index=["Appartamento", "Casa", "Villa", "B&B", "Camera Privata", "Altro"].index(selected_property.get("type", "Appartamento")))
            city = st.text_input("Città*", value=selected_property.get("city", ""))
            address = st.text_input("Indirizzo*", value=selected_property.get("address", ""))
        
        with col2:
            bedrooms = st.number_input("Camere da letto*", min_value=0, value=selected_property.get("bedrooms", 1))
            bathrooms = st.number_input("Bagni*", min_value=0.0, value=float(selected_property.get("bathrooms", 1.0)), step=0.5)
            max_guests = st.number_input("Ospiti Massimi*", min_value=1, value=selected_property.get("max_guests", 2))
            base_price = st.number_input("Prezzo Base per Notte (€)*", min_value=0.0, value=selected_property.get("base_price", 50.0))
            cleaning_fee = st.number_input("Costo Pulizie (€)", min_value=0.0, value=selected_property.get("cleaning_fee", 30.0))
        
        # Property details
        st.subheader("Dettagli Immobile")
        
        # Show existing photos
        st.subheader("Foto dell'Immobile")
        existing_photos = selected_property.get("photos", [])
        
        if existing_photos:
            st.write("Foto esistenti:")
            photo_cols = st.columns(min(4, len(existing_photos)))
            for i, photo_path in enumerate(existing_photos):
                if os.path.exists(photo_path):
                    with photo_cols[i % 4]:
                        st.image(photo_path, caption=f"Foto {i+1}", width=150)
        
        # Upload new photos
        uploaded_files = st.file_uploader("Carica Nuove Foto", 
                                         accept_multiple_files=True, 
                                         type=["jpg", "jpeg", "png"],
                                         key="edit_property_photos")
        
        if uploaded_files:
            st.success(f"Caricate {len(uploaded_files)} nuove foto")
            new_photo_cols = st.columns(min(4, len(uploaded_files)))
            for i, uploaded_file in enumerate(uploaded_files):
                with new_photo_cols[i % 4]:
                    st.image(uploaded_file, caption=f"Nuova Foto {i+1}", width=150)
                    
        # Other details
        check_in_instructions = st.text_area("Istruzioni Check-in", value=selected_property.get("check_in_instructions", ""))
        wifi_details = st.text_input("Dettagli WiFi", value=selected_property.get("wifi_details", ""))
        checkout_instructions = st.text_area("Istruzioni Check-out", value=selected_property.get("checkout_instructions", ""))
        
        # Amenities
        st.subheader("Servizi")
        amenities_options = ["WiFi", "Aria Condizionata", "Riscaldamento", "Cucina", "Lavatrice", 
                            "Asciugatrice", "TV", "Parcheggio", "Ascensore", "Piscina", 
                            "Palestra", "Colazione", "Vista Mare", "Terrazza", "Balcone"]
        
        current_amenities = selected_property.get("amenities", [])
        
        # Display amenities in multiple columns
        amenities_cols = st.columns(3)
        selected_amenities = []
        
        for i, amenity in enumerate(amenities_options):
            if amenities_cols[i % 3].checkbox(amenity, 
                                            value=amenity in current_amenities,
                                            key=f"edit_amenity_{i}"):
                selected_amenities.append(amenity)
        
        # Description
        st.subheader("Descrizione")
        description = st.text_area("Descrizione", 
                                value=selected_property.get("description", ""),
                                height=150)
        
        update_ai_description = st.checkbox("Aggiorna descrizione con AI")
        
        # Status
        status = st.selectbox("Stato", ["Attivo", "Inattivo"], 
                            index=0 if selected_property.get("status", "Attivo") == "Attivo" else 1)
        
        # Submit button
        submit_button = st.form_submit_button("Aggiorna Immobile")
    
    # Outside the form
    if submit_button:
        # Validate required fields
        if not (name and property_type and city and address):
            st.error("Compila tutti i campi obbligatori (contrassegnati con *).")
            return
        
        # Find the index of the property to update
        idx = next((i for i, p in enumerate(st.session_state.properties) 
                    if p.get("id") == property_to_edit_id), None)
        
        if idx is None:
            st.error("Errore nell'aggiornamento dell'immobile.")
            return
        
        # Update property data
        property_data = st.session_state.properties[idx].copy()
        property_data.update({
            "name": name,
            "type": property_type,
            "city": city,
            "address": address,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "max_guests": max_guests,
            "base_price": base_price,
            "cleaning_fee": cleaning_fee,
            "check_in_instructions": check_in_instructions,
            "wifi_details": wifi_details,
            "amenities": selected_amenities,
            "status": status,
            "updated_at": datetime.now().isoformat()
        })
        
        # Generate AI description if requested
        if update_ai_description:
            with st.spinner("Aggiornamento descrizione con AI in corso..."):
                try:
                    ai_description = generate_property_description(property_data)
                    property_data["description"] = ai_description
                except Exception as e:
                    st.error(f"Errore nella generazione della descrizione AI: {str(e)}")
                    property_data["description"] = description
        else:
            property_data["description"] = description
        
        # Update property in session state
        st.session_state.properties[idx] = property_data
        
        # Save the updated data
        save_data()
        
        st.success(f"Immobile '{name}' aggiornato con successo!")
        
        # Clear the editing selection
        if "property_to_edit" in st.session_state:
            del st.session_state.property_to_edit
        
        st.rerun()
    
    # Cancel button outside the form
    if st.button("Annulla Modifiche"):
        if "property_to_edit" in st.session_state:
            del st.session_state.property_to_edit
        st.rerun()

def save_data():
    """Save property and booking data to files"""
    # Make sure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Save properties
    with open('data/properties.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.properties, f, ensure_ascii=False, indent=4, default=str)
    
    # Save bookings
    with open('data/bookings.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.bookings, f, ensure_ascii=False, indent=4, default=str)