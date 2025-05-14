import streamlit as st
import pandas as pd
import json
import uuid
from datetime import datetime, timedelta
import os
from utils.ai_assistant import generate_automated_messages

def show_bookings():
    st.markdown("<h1 class='main-header'>Gestione Prenotazioni</h1>", unsafe_allow_html=True)
    
    # Create tabs for different booking management sections
    tabs = st.tabs(["Elenco Prenotazioni", "Nuova Prenotazione", "Check-in/Check-out", "Messaggi Automatici"])
    
    with tabs[0]:
        show_booking_list()
    
    with tabs[1]:
        add_new_booking()
    
    with tabs[2]:
        manage_checkin_checkout()
    
    with tabs[3]:
        automated_messages()

def show_booking_list():
    st.subheader("Prenotazioni")
    
    if not st.session_state.bookings:
        st.info("Nessuna prenotazione registrata.")
        return
    
    # Add filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.multiselect(
            "Filtra per Stato",
            ["confermata", "attiva", "completata", "cancellata"],
            default=["confermata", "attiva"]
        )
    
    with col2:
        if st.session_state.properties:
            property_options = {p.get("id"): p.get("name") for p in st.session_state.properties}
            property_filter = st.multiselect(
                "Filtra per Immobile",
                options=list(property_options.keys()),
                format_func=lambda x: property_options.get(x)
            )
        else:
            property_filter = []
            st.info("Nessun immobile disponibile.")
    
    with col3:
        date_range = st.date_input(
            "Intervallo Date",
            [(datetime.now() - timedelta(days=30)).date(), (datetime.now() + timedelta(days=30)).date()],
            key="booking_date_range"
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = (datetime.now() - timedelta(days=30)).date()
            end_date = (datetime.now() + timedelta(days=30)).date()
    
    # Apply filters
    filtered_bookings = []
    
    for booking in st.session_state.bookings:
        # Skip if status doesn't match filter
        if status_filter and booking.get("status") not in status_filter:
            continue
        
        # Skip if property doesn't match filter
        if property_filter and booking.get("property_id") not in property_filter:
            continue
        
        # Check date range
        checkin = booking.get("checkin_date")
        checkout = booking.get("checkout_date")
        
        # Convert string dates to datetime if needed
        if isinstance(checkin, str):
            checkin = datetime.strptime(checkin, "%Y-%m-%d").date()
        if isinstance(checkout, str):
            checkout = datetime.strptime(checkout, "%Y-%m-%d").date()
        
        # Skip if dates don't overlap with filter range
        if checkin > end_date or checkout < start_date:
            continue
        
        filtered_bookings.append(booking)
    
    # Create DataFrame for display
    if filtered_bookings:
        booking_data = []
        
        for booking in filtered_bookings:
            # Get property name
            property_name = next((p.get("name") for p in st.session_state.properties 
                                if p.get("id") == booking.get("property_id")), "Unknown")
            
            # Format dates
            checkin = booking.get("checkin_date")
            checkout = booking.get("checkout_date")
            
            if isinstance(checkin, str):
                checkin = datetime.strptime(checkin, "%Y-%m-%d").date()
            if isinstance(checkout, str):
                checkout = datetime.strptime(checkout, "%Y-%m-%d").date()
            
            booking_data.append({
                "ID": booking.get("id"),
                "Ospite": booking.get("guest_name"),
                "Immobile": property_name,
                "Check-in": checkin,
                "Check-out": checkout,
                "Notti": (checkout - checkin).days,
                "Persone": booking.get("guests"),
                "Totale": f"€{booking.get('total_price'):.2f}",
                "Stato": booking.get("status")
            })
        
        df = pd.DataFrame(booking_data)
        st.dataframe(df, use_container_width=True)
        
        # Booking details
        st.subheader("Dettagli Prenotazione")
        
        selected_booking_id = st.selectbox(
            "Seleziona una prenotazione per i dettagli",
            [b.get("id") for b in filtered_bookings],
            format_func=lambda x: next((b.get("guest_name") + " - " + 
                                      next((p.get("name") for p in st.session_state.properties 
                                          if p.get("id") == next((booking.get("property_id") for booking in filtered_bookings 
                                                              if booking.get("id") == x), None)), "Unknown")
                                      for b in filtered_bookings if b.get("id") == x), x)
        )
        
        if selected_booking_id:
            selected_booking = next((b for b in filtered_bookings if b.get("id") == selected_booking_id), None)
            
            if selected_booking:
                with st.expander("Visualizza dettagli completi", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Ospite:** {selected_booking.get('guest_name')}")
                        st.markdown(f"**Email:** {selected_booking.get('guest_email', 'N/A')}")
                        st.markdown(f"**Telefono:** {selected_booking.get('guest_phone', 'N/A')}")
                        
                        property_name = next((p.get("name") for p in st.session_state.properties 
                                           if p.get("id") == selected_booking.get("property_id")), "Unknown")
                        st.markdown(f"**Immobile:** {property_name}")
                        
                        # Format dates
                        checkin = selected_booking.get("checkin_date")
                        checkout = selected_booking.get("checkout_date")
                        
                        if isinstance(checkin, str):
                            checkin = datetime.strptime(checkin, "%Y-%m-%d").date()
                        if isinstance(checkout, str):
                            checkout = datetime.strptime(checkout, "%Y-%m-%d").date()
                        
                        st.markdown(f"**Check-in:** {checkin.strftime('%d/%m/%Y')}")
                        st.markdown(f"**Check-out:** {checkout.strftime('%d/%m/%Y')}")
                        st.markdown(f"**Durata:** {(checkout - checkin).days} notti")
                    
                    with col2:
                        st.markdown(f"**Numero Ospiti:** {selected_booking.get('guests')}")
                        st.markdown(f"**Prezzo per Notte:** €{selected_booking.get('price_per_night'):.2f}")
                        st.markdown(f"**Pulizie:** €{selected_booking.get('cleaning_fee'):.2f}")
                        st.markdown(f"**Tasse:** €{selected_booking.get('taxes', 0):.2f}")
                        st.markdown(f"**Totale:** €{selected_booking.get('total_price'):.2f}")
                        st.markdown(f"**Stato:** {selected_booking.get('status')}")
                        st.markdown(f"**Pagamento:** {selected_booking.get('payment_status', 'In attesa')}")
                    
                    if selected_booking.get("notes"):
                        st.markdown("### Note")
                        st.write(selected_booking.get("notes"))
                    
                    # Actions for this booking
                    st.markdown("### Azioni")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button("Check-in", key="do_checkin", 
                                   disabled=selected_booking.get("status") != "confermata"):
                            handle_checkin(selected_booking)
                    
                    with col2:
                        if st.button("Check-out", key="do_checkout",
                                   disabled=selected_booking.get("status") != "attiva"):
                            handle_checkout(selected_booking)
                    
                    with col3:
                        if st.button("Modifica", key="edit_booking"):
                            st.session_state.booking_to_edit = selected_booking.get("id")
                            st.rerun()
                    
                    with col4:
                        if st.button("Cancella", key="cancel_booking"):
                            if selected_booking.get("status") not in ["completata", "cancellata"]:
                                # Find booking index
                                idx = next((i for i, b in enumerate(st.session_state.bookings) 
                                         if b.get("id") == selected_booking.get("id")), None)
                                
                                if idx is not None:
                                    st.session_state.bookings[idx]["status"] = "cancellata"
                                    st.session_state.bookings[idx]["cancelled_at"] = datetime.now().isoformat()
                                    
                                    # Save the updated data
                                    save_data()
                                    st.success("Prenotazione cancellata.")
                                    st.rerun()
                            else:
                                st.error("Non è possibile cancellare una prenotazione completata o già cancellata.")
    else:
        st.info("Nessuna prenotazione trovata con i filtri selezionati.")

def add_new_booking():
    st.subheader("Nuova Prenotazione")
    
    if not st.session_state.properties:
        st.warning("Devi prima aggiungere degli immobili.")
        if st.button("Vai a Gestione Immobili"):
            st.session_state.current_page = "properties"
            st.rerun()
        return
    
    # Check if we're editing
    editing = False
    booking_to_edit = None
    
    if "booking_to_edit" in st.session_state and st.session_state.booking_to_edit:
        editing = True
        booking_to_edit = next((b for b in st.session_state.bookings 
                              if b.get("id") == st.session_state.booking_to_edit), None)
        
        if not booking_to_edit:
            st.error("Prenotazione non trovata.")
            if "booking_to_edit" in st.session_state:
                del st.session_state.booking_to_edit
            return
    
    with st.form("booking_form"):
        # Guest information
        st.markdown("### Informazioni Ospite")
        col1, col2 = st.columns(2)
        
        with col1:
            guest_name = st.text_input("Nome Ospite*", 
                                     value=booking_to_edit.get("guest_name", "") if editing else "")
            guest_email = st.text_input("Email Ospite", 
                                      value=booking_to_edit.get("guest_email", "") if editing else "")
        
        with col2:
            guest_phone = st.text_input("Telefono Ospite", 
                                      value=booking_to_edit.get("guest_phone", "") if editing else "")
            guests_count = st.number_input("Numero Ospiti*", min_value=1, value=booking_to_edit.get("guests", 1) if editing else 1)
        
        # Property selection
        st.markdown("### Dettagli Prenotazione")
        
        # Property selection with pricing info
        property_options = {p.get("id"): p.get("name") for p in st.session_state.properties if p.get("status") != "Inattivo"}
        
        selected_property_id = st.selectbox(
            "Immobile*",
            options=list(property_options.keys()),
            index=list(property_options.keys()).index(booking_to_edit.get("property_id")) if editing and booking_to_edit.get("property_id") in property_options else 0,
            format_func=lambda x: property_options.get(x)
        )
        
        # Get property details
        selected_property = next((p for p in st.session_state.properties if p.get("id") == selected_property_id), None)
        
        if selected_property:
            # Display property details
            st.markdown(f"**Tipo:** {selected_property.get('type')}")
            st.markdown(f"**Capacità massima:** {selected_property.get('max_guests')} ospiti")
            
            # Warn if guests count exceeds property capacity
            if guests_count > selected_property.get('max_guests', 0):
                st.warning(f"Il numero di ospiti supera la capacità massima dell'immobile ({selected_property.get('max_guests')} ospiti).")
            
            # Date selection
            today = datetime.now().date()
            
            col1, col2 = st.columns(2)
            
            with col1:
                checkin_date = st.date_input(
                    "Data Check-in*",
                    value=booking_to_edit.get("checkin_date") if editing else today,
                    min_value=today
                )
            
            with col2:
                checkout_date = st.date_input(
                    "Data Check-out*",
                    value=booking_to_edit.get("checkout_date") if editing else today + timedelta(days=1),
                    min_value=checkin_date + timedelta(days=1)
                )
            
            # Calculate number of nights
            nights = (checkout_date - checkin_date).days
            st.markdown(f"**Durata soggiorno:** {nights} notti")
            
            # Calculate price
            price_per_night = selected_property.get("current_price", 0)
            cleaning_fee = selected_property.get("cleaning_fee", 0)
            
            # Allow price adjustment
            col1, col2 = st.columns(2)
            
            with col1:
                adjusted_price = st.number_input(
                    "Prezzo per Notte (€)",
                    min_value=0.0,
                    value=booking_to_edit.get("price_per_night", price_per_night) if editing else price_per_night
                )
            
            with col2:
                adjusted_cleaning = st.number_input(
                    "Costo Pulizie (€)",
                    min_value=0.0,
                    value=booking_to_edit.get("cleaning_fee", cleaning_fee) if editing else cleaning_fee
                )
            
            # Additional options
            col1, col2 = st.columns(2)
            
            with col1:
                payment_method = st.selectbox(
                    "Metodo Pagamento",
                    ["Carta di Credito", "Bonifico", "Contanti", "PayPal", "Altro"],
                    index=["Carta di Credito", "Bonifico", "Contanti", "PayPal", "Altro"].index(booking_to_edit.get("payment_method", "Carta di Credito")) if editing else 0
                )
                
                payment_status = st.selectbox(
                    "Stato Pagamento",
                    ["Pagato", "In attesa", "Parziale"],
                    index=["Pagato", "In attesa", "Parziale"].index(booking_to_edit.get("payment_status", "In attesa")) if editing else 1
                )
            
            with col2:
                booking_source = st.selectbox(
                    "Fonte Prenotazione",
                    ["Diretta", "Airbnb", "Booking.com", "VRBO", "Altro"],
                    index=["Diretta", "Airbnb", "Booking.com", "VRBO", "Altro"].index(booking_to_edit.get("source", "Diretta")) if editing else 0
                )
                
                booking_status = st.selectbox(
                    "Stato Prenotazione",
                    ["confermata", "attiva", "completata", "cancellata"],
                    index=["confermata", "attiva", "completata", "cancellata"].index(booking_to_edit.get("status", "confermata")) if editing else 0
                )
            
            # Notes
            booking_notes = st.text_area(
                "Note",
                value=booking_to_edit.get("notes", "") if editing else "",
                placeholder="Inserisci eventuali note o richieste speciali..."
            )
            
            # Calculate total price
            nights = (checkout_date - checkin_date).days
            subtotal = adjusted_price * nights
            total = subtotal + adjusted_cleaning
            
            # Display price breakdown
            st.markdown("### Riepilogo Costi")
            st.markdown(f"**Prezzo per notte:** €{adjusted_price:.2f} x {nights} notti = €{subtotal:.2f}")
            st.markdown(f"**Pulizie:** €{adjusted_cleaning:.2f}")
            st.markdown(f"**Totale:** €{total:.2f}")
            
            # Submit button
            if editing:
                submit_text = "Aggiorna Prenotazione"
            else:
                submit_text = "Crea Prenotazione"
            
            submit_button = st.form_submit_button(submit_text)
    
    # Handle form submission (outside the form)
    if submit_button:
        # Validate required fields
        if not (guest_name and checkin_date and checkout_date):
            st.error("Compila tutti i campi obbligatori (contrassegnati con *).")
            return
        
        # Calculate total price
        nights = (checkout_date - checkin_date).days
        subtotal = adjusted_price * nights
        total = subtotal + adjusted_cleaning
        
        # Prepare booking data
        booking_data = {
            "guest_name": guest_name,
            "guest_email": guest_email,
            "guest_phone": guest_phone,
            "property_id": selected_property_id,
            "checkin_date": checkin_date,
            "checkout_date": checkout_date,
            "guests": guests_count,
            "price_per_night": adjusted_price,
            "cleaning_fee": adjusted_cleaning,
            "nights": nights,
            "total_price": total,
            "payment_method": payment_method,
            "payment_status": payment_status,
            "source": booking_source,
            "status": booking_status,
            "notes": booking_notes
        }
        
        if editing:
            # Update existing booking
            idx = next((i for i, b in enumerate(st.session_state.bookings) 
                      if b.get("id") == st.session_state.booking_to_edit), None)
            
            if idx is not None:
                # Preserve the original ID and created_at
                booking_data["id"] = st.session_state.bookings[idx].get("id")
                booking_data["created_at"] = st.session_state.bookings[idx].get("created_at")
                booking_data["updated_at"] = datetime.now().isoformat()
                
                st.session_state.bookings[idx] = booking_data
                success_message = "Prenotazione aggiornata con successo!"
            else:
                st.error("Errore nell'aggiornamento della prenotazione.")
                return
        else:
            # Add new booking
            booking_data["id"] = str(uuid.uuid4())
            booking_data["created_at"] = datetime.now().isoformat()
            
            st.session_state.bookings.append(booking_data)
            success_message = "Prenotazione creata con successo!"
        
        # Save the updated data
        save_data()
        
        st.success(success_message)
        
        # Clear editing state
        if "booking_to_edit" in st.session_state:
            del st.session_state.booking_to_edit
        
        st.rerun()
    
    # Cancel button (outside the form)
    if editing and st.button("Annulla Modifiche"):
        if "booking_to_edit" in st.session_state:
            del st.session_state.booking_to_edit
        st.rerun()

def manage_checkin_checkout():
    st.subheader("Gestione Check-in & Check-out")
    
    # Create two columns for check-in and check-out
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Check-in di Oggi")
        
        # Find today's check-ins
        today = datetime.now().date()
        todays_checkins = []
        
        for booking in st.session_state.bookings:
            checkin_date = booking.get("checkin_date")
            
            if isinstance(checkin_date, str):
                checkin_date = datetime.strptime(checkin_date, "%Y-%m-%d").date()
            
            if checkin_date == today and booking.get("status") == "confermata":
                property_name = next((p.get("name") for p in st.session_state.properties 
                                   if p.get("id") == booking.get("property_id")), "Unknown")
                
                todays_checkins.append({
                    "id": booking.get("id"),
                    "guest": booking.get("guest_name"),
                    "property": property_name,
                    "guests": booking.get("guests"),
                    "status": booking.get("status")
                })
        
        if todays_checkins:
            for i, checkin in enumerate(todays_checkins):
                with st.container():
                    st.markdown(f"**Ospite:** {checkin['guest']}")
                    st.markdown(f"**Immobile:** {checkin['property']}")
                    st.markdown(f"**Ospiti:** {checkin['guests']}")
                    
                    if st.button(f"Effettua Check-in", key=f"checkin_{i}"):
                        handle_checkin(next((b for b in st.session_state.bookings if b.get("id") == checkin["id"]), None))
                
                if i < len(todays_checkins) - 1:
                    st.markdown("---")
        else:
            st.info("Nessun check-in previsto per oggi.")
    
    with col2:
        st.markdown("### Check-out di Oggi")
        
        # Find today's check-outs
        todays_checkouts = []
        
        for booking in st.session_state.bookings:
            checkout_date = booking.get("checkout_date")
            
            if isinstance(checkout_date, str):
                checkout_date = datetime.strptime(checkout_date, "%Y-%m-%d").date()
            
            if checkout_date == today and booking.get("status") == "attiva":
                property_name = next((p.get("name") for p in st.session_state.properties 
                                   if p.get("id") == booking.get("property_id")), "Unknown")
                
                todays_checkouts.append({
                    "id": booking.get("id"),
                    "guest": booking.get("guest_name"),
                    "property": property_name,
                    "guests": booking.get("guests"),
                    "status": booking.get("status")
                })
        
        if todays_checkouts:
            for i, checkout in enumerate(todays_checkouts):
                with st.container():
                    st.markdown(f"**Ospite:** {checkout['guest']}")
                    st.markdown(f"**Immobile:** {checkout['property']}")
                    st.markdown(f"**Ospiti:** {checkout['guests']}")
                    
                    if st.button(f"Effettua Check-out", key=f"checkout_{i}"):
                        handle_checkout(next((b for b in st.session_state.bookings if b.get("id") == checkout["id"]), None))
                
                if i < len(todays_checkouts) - 1:
                    st.markdown("---")
        else:
            st.info("Nessun check-out previsto per oggi.")
    
    # Upcoming check-ins and check-outs
    st.markdown("### Prossimi Arrivi e Partenze")
    
    upcoming_days = 7  # Show next 7 days
    
    # Create tabs for check-ins and check-outs
    tabs = st.tabs(["Prossimi Check-in", "Prossimi Check-out"])
    
    with tabs[0]:
        upcoming_checkins = []
        
        for booking in st.session_state.bookings:
            checkin_date = booking.get("checkin_date")
            
            if isinstance(checkin_date, str):
                checkin_date = datetime.strptime(checkin_date, "%Y-%m-%d").date()
            
            if (checkin_date > today and 
                checkin_date <= today + timedelta(days=upcoming_days) and 
                booking.get("status") == "confermata"):
                
                property_name = next((p.get("name") for p in st.session_state.properties 
                                   if p.get("id") == booking.get("property_id")), "Unknown")
                
                upcoming_checkins.append({
                    "Data": checkin_date.strftime("%d/%m/%Y"),
                    "Ospite": booking.get("guest_name"),
                    "Immobile": property_name,
                    "Ospiti": booking.get("guests"),
                    "Stato": booking.get("status")
                })
        
        if upcoming_checkins:
            upcoming_df = pd.DataFrame(upcoming_checkins)
            st.dataframe(upcoming_df, use_container_width=True)
        else:
            st.info(f"Nessun check-in previsto nei prossimi {upcoming_days} giorni.")
    
    with tabs[1]:
        upcoming_checkouts = []
        
        for booking in st.session_state.bookings:
            checkout_date = booking.get("checkout_date")
            
            if isinstance(checkout_date, str):
                checkout_date = datetime.strptime(checkout_date, "%Y-%m-%d").date()
            
            if (checkout_date > today and 
                checkout_date <= today + timedelta(days=upcoming_days) and 
                booking.get("status") == "attiva"):
                
                property_name = next((p.get("name") for p in st.session_state.properties 
                                   if p.get("id") == booking.get("property_id")), "Unknown")
                
                upcoming_checkouts.append({
                    "Data": checkout_date.strftime("%d/%m/%Y"),
                    "Ospite": booking.get("guest_name"),
                    "Immobile": property_name,
                    "Ospiti": booking.get("guests"),
                    "Stato": booking.get("status")
                })
        
        if upcoming_checkouts:
            upcoming_df = pd.DataFrame(upcoming_checkouts)
            st.dataframe(upcoming_df, use_container_width=True)
        else:
            st.info(f"Nessun check-out previsto nei prossimi {upcoming_days} giorni.")

def automated_messages():
    st.subheader("Messaggi Automatici")
    
    # Select a booking to send messages for
    active_bookings = [b for b in st.session_state.bookings 
                     if b.get("status") in ["confermata", "attiva"]]
    
    if not active_bookings:
        st.info("Non ci sono prenotazioni attive o confermate per cui inviare messaggi.")
        return
    
    # Create a selection list
    booking_options = {}
    for booking in active_bookings:
        property_name = next((p.get("name") for p in st.session_state.properties 
                           if p.get("id") == booking.get("property_id")), "Unknown")
        booking_options[booking.get("id")] = f"{booking.get('guest_name')} - {property_name}"
    
    selected_booking_id = st.selectbox(
        "Seleziona una prenotazione",
        options=list(booking_options.keys()),
        format_func=lambda x: booking_options.get(x)
    )
    
    selected_booking = next((b for b in active_bookings if b.get("id") == selected_booking_id), None)
    
    if selected_booking:
        # Get property data
        property_data = next((p for p in st.session_state.properties 
                           if p.get("id") == selected_booking.get("property_id")), None)
        
        # Display booking info
        st.markdown(f"**Ospite:** {selected_booking.get('guest_name')}")
        
        checkin_date = selected_booking.get("checkin_date")
        checkout_date = selected_booking.get("checkout_date")
        
        if isinstance(checkin_date, str):
            checkin_date = datetime.strptime(checkin_date, "%Y-%m-%d").date()
        if isinstance(checkout_date, str):
            checkout_date = datetime.strptime(checkout_date, "%Y-%m-%d").date()
        
        st.markdown(f"**Check-in:** {checkin_date.strftime('%d/%m/%Y')}")
        st.markdown(f"**Check-out:** {checkout_date.strftime('%d/%m/%Y')}")
        
        # Create message tabs
        message_tabs = st.tabs(["Benvenuto", "Check-in", "Durante Soggiorno", "Check-out", "Personalizzato"])
        
        with message_tabs[0]:
            st.subheader("Messaggio di Benvenuto")
            
            if st.button("Genera Messaggio di Benvenuto", key="gen_welcome"):
                with st.spinner("Generazione messaggio in corso..."):
                    try:
                        welcome_message = generate_automated_messages(
                            "welcome",
                            selected_booking,
                            selected_booking.get("guest_name"),
                            property_data
                        )
                        st.session_state.welcome_message = welcome_message
                    except Exception as e:
                        st.error(f"Errore nella generazione del messaggio: {str(e)}")
            
            welcome_message = st.session_state.get("welcome_message", "")
            edited_welcome = st.text_area("Messaggio di Benvenuto", value=welcome_message, height=200)
            
            if st.button("Invia", key="send_welcome", disabled=not edited_welcome):
                st.success("Messaggio inviato con successo!")
                # In a real app, this would send the message through SMS, email, etc.
        
        with message_tabs[1]:
            st.subheader("Istruzioni Check-in")
            
            if st.button("Genera Istruzioni Check-in", key="gen_checkin"):
                with st.spinner("Generazione istruzioni in corso..."):
                    try:
                        checkin_message = generate_automated_messages(
                            "check_in",
                            selected_booking,
                            selected_booking.get("guest_name"),
                            property_data
                        )
                        st.session_state.checkin_message = checkin_message
                    except Exception as e:
                        st.error(f"Errore nella generazione del messaggio: {str(e)}")
            
            checkin_message = st.session_state.get("checkin_message", "")
            edited_checkin = st.text_area("Istruzioni Check-in", value=checkin_message, height=200)
            
            if st.button("Invia", key="send_checkin", disabled=not edited_checkin):
                st.success("Istruzioni inviate con successo!")
                # In a real app, this would send the message through SMS, email, etc.
        
        with message_tabs[2]:
            st.subheader("Messaggio Durante Soggiorno")
            
            if st.button("Genera Messaggio Durante Soggiorno", key="gen_during"):
                with st.spinner("Generazione messaggio in corso..."):
                    try:
                        during_message = generate_automated_messages(
                            "during_stay",
                            selected_booking,
                            selected_booking.get("guest_name"),
                            property_data
                        )
                        st.session_state.during_message = during_message
                    except Exception as e:
                        st.error(f"Errore nella generazione del messaggio: {str(e)}")
            
            during_message = st.session_state.get("during_message", "")
            edited_during = st.text_area("Messaggio Durante Soggiorno", value=during_message, height=200)
            
            if st.button("Invia", key="send_during", disabled=not edited_during):
                st.success("Messaggio inviato con successo!")
                # In a real app, this would send the message through SMS, email, etc.
        
        with message_tabs[3]:
            st.subheader("Istruzioni Check-out")
            
            if st.button("Genera Istruzioni Check-out", key="gen_checkout"):
                with st.spinner("Generazione istruzioni in corso..."):
                    try:
                        checkout_message = generate_automated_messages(
                            "check_out",
                            selected_booking,
                            selected_booking.get("guest_name"),
                            property_data
                        )
                        st.session_state.checkout_message = checkout_message
                    except Exception as e:
                        st.error(f"Errore nella generazione del messaggio: {str(e)}")
            
            checkout_message = st.session_state.get("checkout_message", "")
            edited_checkout = st.text_area("Istruzioni Check-out", value=checkout_message, height=200)
            
            if st.button("Invia", key="send_checkout", disabled=not edited_checkout):
                st.success("Istruzioni inviate con successo!")
                # In a real app, this would send the message through SMS, email, etc.
        
        with message_tabs[4]:
            st.subheader("Messaggio Personalizzato")
            
            custom_message = st.text_area("Messaggio Personalizzato", height=200,
                                        placeholder="Scrivi un messaggio personalizzato...")
            
            if st.button("Invia", key="send_custom", disabled=not custom_message):
                st.success("Messaggio inviato con successo!")
                # In a real app, this would send the message through SMS, email, etc.

def handle_checkin(booking):
    """Handle the check-in process for a booking"""
    if not booking:
        st.error("Prenotazione non trovata.")
        return
    
    # Find booking index
    idx = next((i for i, b in enumerate(st.session_state.bookings) 
               if b.get("id") == booking.get("id")), None)
    
    if idx is None:
        st.error("Prenotazione non trovata.")
        return
    
    # Update booking status
    st.session_state.bookings[idx]["status"] = "attiva"
    st.session_state.bookings[idx]["checkin_completed_at"] = datetime.now().isoformat()
    
    # Save the updated data
    save_data()
    
    st.success(f"Check-in completato per {booking.get('guest_name')}!")
    
    # Get property data for messaging
    property_data = next((p for p in st.session_state.properties 
                       if p.get("id") == booking.get("property_id")), None)
    
    # Generate welcome message (in a real app, this would also send the message)
    with st.spinner("Generazione messaggio di benvenuto..."):
        try:
            welcome_message = generate_automated_messages(
                "welcome",
                booking,
                booking.get("guest_name"),
                property_data
            )
            
            with st.expander("Messaggio di Benvenuto (Da Inviare)", expanded=True):
                st.write(welcome_message)
                
                if st.button("Invia Messaggio"):
                    st.success("Messaggio inviato con successo!")
                    # In a real app, this would send the message
        except Exception as e:
            st.error(f"Errore nella generazione del messaggio: {str(e)}")

def handle_checkout(booking):
    """Handle the check-out process for a booking"""
    if not booking:
        st.error("Prenotazione non trovata.")
        return
    
    # Find booking index
    idx = next((i for i, b in enumerate(st.session_state.bookings) 
               if b.get("id") == booking.get("id")), None)
    
    if idx is None:
        st.error("Prenotazione non trovata.")
        return
    
    # Update booking status
    st.session_state.bookings[idx]["status"] = "completata"
    st.session_state.bookings[idx]["checkout_completed_at"] = datetime.now().isoformat()
    
    # Save the updated data
    save_data()
    
    # Send cleaning notification
    try:
        from utils.message_service import notify_cleaning_service
        property_id = booking.get("property_id")
        checkout_date = booking.get("check_out")
        
        if property_id and checkout_date:
            # Notifica il servizio di pulizia
            with st.spinner("Invio notifica al servizio di pulizia..."):
                result = notify_cleaning_service(property_id, booking, checkout_date)
                
                if result["status"] in ["success", "simulated"]:
                    st.success(f"Notifica pulizia inviata: {result['message']}")
                else:
                    st.warning(f"Notifica pulizia non inviata: {result['message']}")
    except Exception as e:
        st.error(f"Errore nell'invio della notifica di pulizia: {str(e)}")
    
    st.success(f"Check-out completato per {booking.get('guest_name')}!")
    
    # Schedule cleaning (in a real app, this would send a notification to cleaning service)
    property_name = next((p.get("name") for p in st.session_state.properties 
                       if p.get("id") == booking.get("property_id")), "Unknown")
    
    st.info(f"Pulizia programmata per {property_name}.")
    
    # In a real app, this would block the property for bookings during cleaning
    st.info(f"Immobile bloccato per 1 giorno per consentire la pulizia.")
    
    # Rating request (in a real app, this would send a review request to the guest)
    st.success("Richiesta di recensione inviata all'ospite.")

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