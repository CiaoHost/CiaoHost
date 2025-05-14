def get_text(key, language='english'):
    """
    Get translated text for a key in the specified language.
    
    Args:
        key (str): Translation key
        language (str): Language code ('english' or 'italian')
    
    Returns:
        str: Translated text
    """
    translations = {
        # Navigation
        'navigation': {
            'english': 'Navigation',
            'italian': 'Navigazione'
        },
        'dashboard': {
            'english': 'Dashboard',
            'italian': 'Pannello di controllo'
        },
        'properties': {
            'english': 'Properties',
            'italian': 'Proprietà'
        },
        'bookings': {
            'english': 'Bookings',
            'italian': 'Prenotazioni'
        },
        'guest_communication': {
            'english': 'Guest Communication',
            'italian': 'Comunicazione Ospiti'
        },
        'ai_cohost': {
            'english': 'AI Co-Host',
            'italian': 'Co-Host AI'
        },
        'automated_checkin': {
            'english': 'Automated Check-in',
            'italian': 'Check-in Automatizzato'
        },
        
        # Dashboard
        'dashboard_title': {
            'english': 'Property Dashboard',
            'italian': 'Pannello di Controllo Proprietà'
        },
        'total_properties': {
            'english': 'Total Properties',
            'italian': 'Proprietà Totali'
        },
        'active_bookings': {
            'english': 'Active Bookings',
            'italian': 'Prenotazioni Attive'
        },
        'upcoming_bookings': {
            'english': 'Upcoming Bookings',
            'italian': 'Prenotazioni Future'
        },
        'monthly_income': {
            'english': 'Monthly Income',
            'italian': 'Reddito Mensile'
        },
        'recent_bookings': {
            'english': 'Recent Bookings',
            'italian': 'Prenotazioni Recenti'
        },
        'no_bookings': {
            'english': 'No bookings to display',
            'italian': 'Nessuna prenotazione da visualizzare'
        },
        'guest': {
            'english': 'Guest',
            'italian': 'Ospite'
        },
        'dates': {
            'english': 'Dates',
            'italian': 'Date'
        },
        'total': {
            'english': 'Total',
            'italian': 'Totale'
        },
        
        # Properties
        'properties_title': {
            'english': 'Manage Properties',
            'italian': 'Gestione Proprietà'
        },
        'add_property': {
            'english': 'Add New Property',
            'italian': 'Aggiungi Nuova Proprietà'
        },
        'edit_property': {
            'english': 'Edit Property',
            'italian': 'Modifica Proprietà'
        },
        'property_name': {
            'english': 'Property Name',
            'italian': 'Nome Proprietà'
        },
        'address': {
            'english': 'Address',
            'italian': 'Indirizzo'
        },
        'bedrooms': {
            'english': 'Bedrooms',
            'italian': 'Camere da letto'
        },
        'bathrooms': {
            'english': 'Bathrooms',
            'italian': 'Bagni'
        },
        'description': {
            'english': 'Description',
            'italian': 'Descrizione'
        },
        'price_per_night': {
            'english': 'Price per Night',
            'italian': 'Prezzo per Notte'
        },
        'amenities': {
            'english': 'Amenities',
            'italian': 'Servizi'
        },
        'save': {
            'english': 'Save',
            'italian': 'Salva'
        },
        'cancel': {
            'english': 'Cancel',
            'italian': 'Annulla'
        },
        'delete_property': {
            'english': 'Delete Property',
            'italian': 'Elimina Proprietà'
        },
        'property_updated': {
            'english': 'Property updated successfully',
            'italian': 'Proprietà aggiornata con successo'
        },
        'property_added': {
            'english': 'Property added successfully',
            'italian': 'Proprietà aggiunta con successo'
        },
        'property_deleted': {
            'english': 'Property deleted successfully',
            'italian': 'Proprietà eliminata con successo'
        },
        'view_details': {
            'english': 'View Details',
            'italian': 'Visualizza Dettagli'
        },
        'no_properties': {
            'english': 'No properties to display',
            'italian': 'Nessuna proprietà da visualizzare'
        },
        
        # Bookings
        'bookings_title': {
            'english': 'Manage Bookings',
            'italian': 'Gestione Prenotazioni'
        },
        'add_booking': {
            'english': 'Add New Booking',
            'italian': 'Aggiungi Nuova Prenotazione'
        },
        'edit_booking': {
            'english': 'Edit Booking',
            'italian': 'Modifica Prenotazione'
        },
        'filter_by_property': {
            'english': 'Filter by Property',
            'italian': 'Filtra per Proprietà'
        },
        'filter_by_status': {
            'english': 'Filter by Status',
            'italian': 'Filtra per Stato'
        },
        'select_property': {
            'english': 'Select Property',
            'italian': 'Seleziona Proprietà'
        },
        'guest_name': {
            'english': 'Guest Name',
            'italian': 'Nome Ospite'
        },
        'guest_email': {
            'english': 'Guest Email',
            'italian': 'Email Ospite'
        },
        'check_in_date': {
            'english': 'Check-in Date',
            'italian': 'Data Check-in'
        },
        'check_out_date': {
            'english': 'Check-out Date',
            'italian': 'Data Check-out'
        },
        'total_nights': {
            'english': 'Total Nights',
            'italian': 'Notti Totali'
        },
        'total_price': {
            'english': 'Total Price',
            'italian': 'Prezzo Totale'
        },
        'number_of_guests': {
            'english': 'Number of Guests',
            'italian': 'Numero di Ospiti'
        },
        'special_requests': {
            'english': 'Special Requests',
            'italian': 'Richieste Speciali'
        },
        'cancel_booking': {
            'english': 'Cancel Booking',
            'italian': 'Annulla Prenotazione'
        },
        'booking_updated': {
            'english': 'Booking updated successfully',
            'italian': 'Prenotazione aggiornata con successo'
        },
        'booking_added': {
            'english': 'Booking added successfully',
            'italian': 'Prenotazione aggiunta con successo'
        },
        'booking_cancelled': {
            'english': 'Booking cancelled successfully',
            'italian': 'Prenotazione annullata con successo'
        },
        'no_bookings_found': {
            'english': 'No bookings found with the selected filters',
            'italian': 'Nessuna prenotazione trovata con i filtri selezionati'
        },
        'check_in': {
            'english': 'Check-in',
            'italian': 'Check-in'
        },
        'check_out': {
            'english': 'Check-out',
            'italian': 'Check-out'
        },
        
        # Communication
        'communication_title': {
            'english': 'Guest Communication',
            'italian': 'Comunicazione con gli Ospiti'
        },
        'select_booking': {
            'english': 'Select a Booking',
            'italian': 'Seleziona una Prenotazione'
        },
        'guest_details': {
            'english': 'Guest Details',
            'italian': 'Dettagli Ospite'
        },
        'name': {
            'english': 'Name',
            'italian': 'Nome'
        },
        'email': {
            'english': 'Email',
            'italian': 'Email'
        },
        'automated_messages': {
            'english': 'Automated Messages',
            'italian': 'Messaggi Automatici'
        },
        'welcome_message': {
            'english': 'Welcome Message',
            'italian': 'Messaggio di Benvenuto'
        },
        'instructions': {
            'english': 'Checkout Instructions',
            'italian': 'Istruzioni per il Check-out'
        },
        'custom_message': {
            'english': 'Custom Message',
            'italian': 'Messaggio Personalizzato'
        },
        'message_preview': {
            'english': 'Message Preview',
            'italian': 'Anteprima del Messaggio'
        },
        'send_welcome': {
            'english': 'Send Welcome Message',
            'italian': 'Invia Messaggio di Benvenuto'
        },
        'send_instructions': {
            'english': 'Send Checkout Instructions',
            'italian': 'Invia Istruzioni per il Check-out'
        },
        'message_subject': {
            'english': 'Message Subject',
            'italian': 'Oggetto del Messaggio'
        },
        'message_content': {
            'english': 'Message Content',
            'italian': 'Contenuto del Messaggio'
        },
        'send_message': {
            'english': 'Send Message',
            'italian': 'Invia Messaggio'
        },
        'message_sent': {
            'english': 'Message sent successfully',
            'italian': 'Messaggio inviato con successo'
        },
        'message_error': {
            'english': 'Error sending message',
            'italian': 'Errore nell\'invio del messaggio'
        },
        'complete_all_fields': {
            'english': 'Please complete all fields',
            'italian': 'Si prega di completare tutti i campi'
        },
        'message_history': {
            'english': 'Message History',
            'italian': 'Cronologia dei Messaggi'
        },
        'no_messages': {
            'english': 'No messages to display',
            'italian': 'Nessun messaggio da visualizzare'
        },
        'no_active_bookings': {
            'english': 'No active bookings to display',
            'italian': 'Nessuna prenotazione attiva da visualizzare'
        },
        
        # AI Co-Host
        'ai_cohost_title': {
            'english': 'AI Co-Host',
            'italian': 'Co-Host AI'
        },
        'ask_cohost': {
            'english': 'Ask a question about your B&B business...',
            'italian': 'Fai una domanda sulla tua attività B&B...'
        },
        'thinking': {
            'english': 'Thinking...',
            'italian': 'Sto pensando...'
        },
        'ai_cohost_stats': {
            'english': 'AI Co-Host Performance',
            'italian': 'Prestazioni Co-Host AI'
        },
        'ai_response_time': {
            'english': 'Response Time',
            'italian': 'Tempo di Risposta'
        },
        'cost_savings': {
            'english': 'Cost Savings',
            'italian': 'Risparmio sui Costi'
        },
        'guest_satisfaction': {
            'english': 'Guest Satisfaction',
            'italian': 'Soddisfazione Ospiti'
        },
        'automated_checkin_title': {
            'english': 'Automated Check-in',
            'italian': 'Check-in Automatizzato'
        },
        'checkin_instructions': {
            'english': 'Check-in Instructions',
            'italian': 'Istruzioni per il Check-in'
        },
        'digital_keys': {
            'english': 'Digital Keys',
            'italian': 'Chiavi Digitali'
        },
        'property_access': {
            'english': 'Property Access',
            'italian': 'Accesso alla Proprietà'
        },
        'automated_bookings': {
            'english': 'Automated Bookings',
            'italian': 'Prenotazioni Automatizzate'
        },
        'automated_bookings_title': {
            'english': 'Automated Booking Management',
            'italian': 'Gestione Prenotazioni Automatizzata'
        },
        'automated_maintenance': {
            'english': 'Maintenance Management',
            'italian': 'Gestione Manutenzione'
        },
        'automated_maintenance_title': {
            'english': 'Automated Maintenance Management',
            'italian': 'Gestione Manutenzione Automatizzata'
        },
        'cleaning_management': {
            'english': 'Cleaning Management',
            'italian': 'Gestione Pulizie'
        },
        'cleaning_management_title': {
            'english': 'Automated Cleaning Management',
            'italian': 'Gestione Pulizie Automatizzata'
        },
        'switch_to_client': {
            'english': 'Switch to Client View',
            'italian': 'Passa alla Vista Cliente'
        },
        'switch_to_owner': {
            'english': 'Switch to Owner View',
            'italian': 'Passa alla Vista Proprietario'
        },
        'client_view_title': {
            'english': 'CiaoHost - AI Booking Assistant',
            'italian': 'CiaoHost - Assistente Prenotazioni AI'
        },
        'client_chat_placeholder': {
            'english': 'Hi! I\'m your AI booking assistant. Ask me about available properties, booking details, or how to make a reservation...',
            'italian': 'Ciao! Sono il tuo assistente AI per le prenotazioni. Chiedimi informazioni sulle proprietà disponibili, dettagli sulle prenotazioni o come effettuare una prenotazione...'
        },
        'make_reservation': {
            'english': 'Make a Reservation',
            'italian': 'Effettua una Prenotazione'
        },
        'browse_properties': {
            'english': 'Browse Properties',
            'italian': 'Sfoglia Proprietà'
        },
        'contact_support': {
            'english': 'Contact Support',
            'italian': 'Contatta Assistenza'
        },
        'check_availability': {
            'english': 'Check Availability',
            'italian': 'Verifica Disponibilità'
        },
        'all_cities': {
            'english': 'All Cities',
            'italian': 'Tutte le Città'
        },
        'select_city': {
            'english': 'Select City',
            'italian': 'Seleziona Città'
        },
        'milano': {
            'english': 'Milan',
            'italian': 'Milano'
        },
        'roma': {
            'english': 'Rome',
            'italian': 'Roma'
        },
        'napoli': {
            'english': 'Naples',
            'italian': 'Napoli'
        },
        'portici': {
            'english': 'Portici',
            'italian': 'Portici'
        },
        'smart_assistant': {
            'english': 'Smart Booking Assistant',
            'italian': 'Assistente Prenotazioni Intelligente'
        },
        'chat_welcome': {
            'english': 'Hello! I\'m your AI booking assistant for CiaoHost. I can help you find the perfect property in Italy, make reservations, and answer any questions. What are you looking for today?',
            'italian': 'Ciao! Sono il tuo assistente di prenotazioni AI per CiaoHost. Posso aiutarti a trovare la proprietà perfetta in Italia, effettuare prenotazioni e rispondere a qualsiasi domanda. Cosa stai cercando oggi?'
        }
    }
    
    # Return the translated text, or the key itself if no translation is found
    if key in translations:
        return translations[key].get(language, translations[key]['english'])
    else:
        return key
