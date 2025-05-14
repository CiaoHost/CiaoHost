import streamlit as st
import pandas as pd
import json
import os
import time
import uuid
from datetime import datetime, timedelta
import re
import random
from utils.ai_assistant import generate_response, virtual_co_host
from utils.database import get_all_properties, get_property, get_all_bookings, get_booking

def show_virtual_co_host():
    st.markdown("<h1 class='main-header'>Co-Host Virtuale AI</h1>", unsafe_allow_html=True)
    
    # Create tabs for different sections
    tabs = st.tabs(["Chat con Ospiti", "Conversazioni Attive", "Analisi Messaggi", "Gestione FAQ"])
    
    with tabs[0]:
        show_chat_simulator()
    
    with tabs[1]:
        show_active_chats()
    
    with tabs[2]:
        show_message_analysis()
    
    with tabs[3]:
        show_faq_management()

def show_chat_simulator():
    st.subheader("Simulatore Chat con Ospiti")
    
    # Initialize chat history if not exists
    if 'active_chat' not in st.session_state:
        st.session_state.active_chat = {
            "guest_name": "",
            "property_id": "",
            "booking_id": "",
            "messages": []
        }
    
    # Get properties
    properties = st.session_state.properties
    
    # Sidebar settings
    with st.sidebar:
        st.subheader("Impostazioni Chat")
        
        # Select guest type
        guest_type = st.radio(
            "Tipo di Ospite",
            ["Ospite Esistente", "Nuovo Ospite"]
        )
        
        if guest_type == "Ospite Esistente":
            # Get bookings
            bookings = st.session_state.bookings
            
            if bookings:
                # Create selection options
                booking_options = []
                for booking in bookings:
                    property_name = next((p["name"] for p in properties if p["id"] == booking.get("property_id")), "Sconosciuto")
                    # Convert dates if needed
                    checkin_date = booking.get("checkin_date")
                    if isinstance(checkin_date, str):
                        try:
                            checkin_date = datetime.fromisoformat(checkin_date).date()
                        except ValueError:
                            checkin_date = "Data non valida"
                    
                    checkout_date = booking.get("checkout_date")
                    if isinstance(checkout_date, str):
                        try:
                            checkout_date = datetime.fromisoformat(checkout_date).date()
                        except ValueError:
                            checkout_date = "Data non valida"
                            
                    option_text = f"{booking.get('guest_name')} - {property_name} ({checkin_date} a {checkout_date})"
                    booking_options.append({"id": booking.get("id"), "text": option_text})
                
                selected_booking_idx = st.selectbox(
                    "Seleziona Prenotazione",
                    range(len(booking_options)),
                    format_func=lambda i: booking_options[i]["text"] if i < len(booking_options) else ""
                )
                
                if selected_booking_idx is not None and selected_booking_idx < len(booking_options):
                    selected_booking_id = booking_options[selected_booking_idx]["id"]
                    selected_booking = next((b for b in bookings if b["id"] == selected_booking_id), None)
                    
                    if selected_booking and selected_booking["id"] != st.session_state.active_chat.get("booking_id"):
                        # Reset chat if different booking selected
                        property_data = next((p for p in properties if p["id"] == selected_booking.get("property_id")), None)
                        
                        st.session_state.active_chat = {
                            "guest_name": selected_booking.get("guest_name"),
                            "property_id": selected_booking.get("property_id"),
                            "property_name": property_data.get("name") if property_data else "Sconosciuto",
                            "booking_id": selected_booking.get("id"),
                            "messages": []
                        }
            else:
                st.info("Nessuna prenotazione disponibile. Aggiungi prenotazioni dalla sezione Prenotazioni.")
        else:
            # New guest chat
            guest_name = st.text_input("Nome Ospite", value=st.session_state.active_chat.get("guest_name", ""))
            
            if properties:
                property_options = {p["id"]: p["name"] for p in properties}
                selected_property_id = st.selectbox(
                    "Immobile di Interesse",
                    options=list(property_options.keys()),
                    format_func=lambda x: property_options.get(x, ""),
                    index=list(property_options.keys()).index(st.session_state.active_chat.get("property_id")) if st.session_state.active_chat.get("property_id") in property_options else 0
                )
                
                if guest_name and selected_property_id and (guest_name != st.session_state.active_chat.get("guest_name") or selected_property_id != st.session_state.active_chat.get("property_id")):
                    # Reset chat if different property or guest
                    st.session_state.active_chat = {
                        "guest_name": guest_name,
                        "property_id": selected_property_id,
                        "property_name": property_options.get(selected_property_id),
                        "booking_id": "",
                        "messages": []
                    }
            else:
                st.info("Nessun immobile disponibile. Aggiungi immobili dalla sezione Gestione Immobili.")
        
        # Language selection
        language = st.selectbox(
            "Lingua",
            ["Italiano", "English", "Français", "Español", "Deutsch"]
        )
        
        # AI response mode
        ai_mode = st.radio(
            "Modalità Risposta AI",
            ["Automatica", "Manuale"]
        )
        
        # Save conversation button
        if st.button("Salva Conversazione") and st.session_state.active_chat.get("messages"):
            save_conversation(st.session_state.active_chat)
            st.success("Conversazione salvata con successo!")
    
    # Display chat header
    if st.session_state.active_chat.get("guest_name"):
        st.markdown(f"### Chat con {st.session_state.active_chat.get('guest_name')}")
        if st.session_state.active_chat.get("property_name"):
            st.markdown(f"**Immobile:** {st.session_state.active_chat.get('property_name')}")
    else:
        st.info("Seleziona un ospite o inserisci un nome per iniziare una nuova chat.")
        return

    # Display message history
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for msg in st.session_state.active_chat.get("messages", []):
        if msg["sender"] == "guest":
            st.markdown(f"""
            <div style='display: flex; margin-bottom: 10px;'>
                <div style='background-color: #E8F4FA; padding: 10px; border-radius: 10px; max-width: 70%; margin-left: auto;'>
                    <p style='margin: 0;'><strong>Ospite:</strong></p>
                    <p style='margin: 0;'>{msg["text"]}</p>
                    <p style='margin: 0; font-size: 0.8em; text-align: right; color: #666;'>{msg["timestamp"]}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='display: flex; margin-bottom: 10px;'>
                <div style='background-color: #F0F2F6; padding: 10px; border-radius: 10px; max-width: 70%;'>
                    <p style='margin: 0;'><strong>Co-Host:</strong></p>
                    <p style='margin: 0;'>{msg["text"]}</p>
                    <p style='margin: 0; font-size: 0.8em; text-align: right; color: #666;'>{msg["timestamp"]}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Message input
    with st.form("message_form", clear_on_submit=True):
        user_input = st.text_area("Messaggio", height=100, key="user_message_input")
        submitted = st.form_submit_button("Invia")
        
        if submitted and user_input.strip():
            # Get current timestamp
            timestamp = datetime.now().strftime("%H:%M %d/%m/%Y")
            
            # Add user message to chat
            st.session_state.active_chat["messages"].append({
                "sender": "guest",
                "text": user_input,
                "timestamp": timestamp
            })
            
            # If auto mode, generate AI response
            if ai_mode == "Automatica":
                with st.spinner("L'AI sta generando una risposta..."):
                    # Get property data for context
                    property_data = next((p for p in properties if p["id"] == st.session_state.active_chat.get("property_id")), None)
                    
                    # Generate response
                    ai_response = virtual_co_host(
                        user_input, 
                        property_data=property_data,
                        conversation_history=get_conversation_history(),
                        language=language.lower()
                    )
                    
                    # Add AI response to chat
                    st.session_state.active_chat["messages"].append({
                        "sender": "host",
                        "text": ai_response,
                        "timestamp": datetime.now().strftime("%H:%M %d/%m/%Y")
                    })
            
            # Rerun to update chat display
            st.rerun()
    
    # Manual response section
    if ai_mode == "Manuale":
        with st.form("manual_response_form", clear_on_submit=True):
            # Generate AI suggestions
            if st.session_state.active_chat.get("messages") and st.session_state.active_chat["messages"][-1]["sender"] == "guest":
                property_data = next((p for p in properties if p["id"] == st.session_state.active_chat.get("property_id")), None)
                
                with st.spinner("Generazione di suggerimenti..."):
                    ai_suggestion = virtual_co_host(
                        st.session_state.active_chat["messages"][-1]["text"],
                        property_data=property_data,
                        conversation_history=get_conversation_history(),
                        language=language.lower()
                    )
                    
                    st.markdown("**Suggerimento AI:**")
                    st.markdown(f"<div style='padding: 10px; border-radius: 5px; background-color: #F0F2F6;'>{ai_suggestion}</div>", unsafe_allow_html=True)
            
            manual_response = st.text_area("Risposta Manuale", height=100)
            send_manual = st.form_submit_button("Invia Risposta")
            
            if send_manual and manual_response.strip():
                # Add manual response to chat
                st.session_state.active_chat["messages"].append({
                    "sender": "host",
                    "text": manual_response,
                    "timestamp": datetime.now().strftime("%H:%M %d/%m/%Y")
                })
                
                # Rerun to update chat display
                st.rerun()

def show_active_chats():
    st.subheader("Conversazioni Attive")
    
    # Initialize active conversations if not exists
    if 'active_conversations' not in st.session_state:
        st.session_state.active_conversations = {}
    
    # Load saved conversations
    conversations = load_conversations()
    
    if not conversations:
        st.info("Nessuna conversazione attiva. Vai alla scheda 'Chat con Ospiti' per iniziare una nuova conversazione.")
        return
    
    # Display conversations
    for conv_id, conv in conversations.items():
        with st.expander(f"{conv.get('guest_name')} - {conv.get('property_name')} ({len(conv.get('messages', []))} messaggi)"):
            # Display conversation details
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**Ospite:** {conv.get('guest_name')}")
                
            with col2:
                st.markdown(f"**Immobile:** {conv.get('property_name')}")
                
            with col3:
                if conv.get('booking_id'):
                    booking = next((b for b in st.session_state.bookings if b["id"] == conv.get('booking_id')), None)
                    if booking:
                        checkin_date = booking.get("checkin_date")
                        checkout_date = booking.get("checkout_date")
                        if isinstance(checkin_date, str):
                            try:
                                checkin_date = datetime.fromisoformat(checkin_date).date()
                            except ValueError:
                                checkin_date = "Data non valida"
                        if isinstance(checkout_date, str):
                            try:
                                checkout_date = datetime.fromisoformat(checkout_date).date()
                            except ValueError:
                                checkout_date = "Data non valida"
                        st.markdown(f"**Prenotazione:** {checkin_date} - {checkout_date}")
            
            # Display last few messages
            st.markdown("**Ultimi messaggi:**")
            
            messages = conv.get('messages', [])
            for msg in messages[-3:]:  # Show last 3 messages
                sender = "Ospite" if msg["sender"] == "guest" else "Co-Host"
                st.markdown(f"**{sender}** ({msg['timestamp']}): {msg['text']}")
            
            # Actions
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Continua Conversazione", key=f"continue_{conv_id}"):
                    st.session_state.active_chat = conv.copy()
                    st.session_state.current_page = "co_host"
                    st.rerun()
            
            with col2:
                if st.button("Archivia", key=f"archive_{conv_id}"):
                    # Archive conversation logic would go here
                    if conv_id in st.session_state.active_conversations:
                        # Mark as archived
                        st.session_state.active_conversations[conv_id]["archived"] = True
                        save_all_conversations()
                        st.success("Conversazione archiviata!")
                        st.rerun()

def show_message_analysis():
    st.subheader("Analisi Messaggi")
    
    # Load conversations for analysis
    conversations = load_conversations()
    
    if not conversations:
        st.info("Nessuna conversazione disponibile per l'analisi.")
        return
    
    # Calculate analytics
    total_conversations = len(conversations)
    total_messages = sum(len(conv.get('messages', [])) for conv in conversations.values())
    avg_messages_per_conv = total_messages / total_conversations if total_conversations > 0 else 0
    
    # Messages by property
    property_messages = {}
    for conv in conversations.values():
        property_name = conv.get('property_name', 'Sconosciuto')
        if property_name not in property_messages:
            property_messages[property_name] = 0
        property_messages[property_name] += len(conv.get('messages', []))
    
    # Metrics
    st.markdown("### Metriche Conversazioni")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Totale Conversazioni", total_conversations)
    
    with col2:
        st.metric("Totale Messaggi", total_messages)
    
    with col3:
        st.metric("Media Messaggi per Conversazione", f"{avg_messages_per_conv:.1f}")
    
    # Messages by property chart
    st.markdown("### Messaggi per Immobile")
    
    if property_messages:
        chart_data = pd.DataFrame({
            'Immobile': list(property_messages.keys()),
            'Messaggi': list(property_messages.values())
        })
        
        st.bar_chart(chart_data.set_index('Immobile'))
    
    # FAQ detection
    st.markdown("### Rilevamento Domande Frequenti")
    st.markdown("Analisi delle domande più frequenti dai messaggi degli ospiti:")
    
    # Extract questions
    questions = []
    for conv in conversations.values():
        for msg in conv.get('messages', []):
            if msg['sender'] == 'guest':
                # Simple question detection
                text = msg['text']
                if '?' in text or any(q in text.lower() for q in ['come', 'dove', 'quando', 'chi', 'cosa', 'perché', 'quale']):
                    questions.append(text)
    
    # Group similar questions
    if questions:
        # Here we'd use more sophisticated clustering in a real app
        # For now, just group by keywords
        question_keywords = {
            'check-in': ['check-in', 'arrivo', 'arrivare', 'chiavi'],
            'check-out': ['check-out', 'partenza', 'partire', 'lasciare'],
            'wifi': ['wifi', 'internet', 'password', 'connessione'],
            'trasporti': ['trasporto', 'metro', 'bus', 'treno', 'taxi'],
            'pulizie': ['pulizia', 'pulire', 'pulito'],
            'pagamento': ['pagamento', 'pagare', 'soldi', 'prezzo']
        }
        
        grouped_questions = {k: [] for k in question_keywords.keys()}
        
        for q in questions:
            q_lower = q.lower()
            assigned = False
            for category, keywords in question_keywords.items():
                if any(keyword in q_lower for keyword in keywords):
                    grouped_questions[category].append(q)
                    assigned = True
                    break
            
            if not assigned:
                # Add a "misc" category if needed
                if 'altro' not in grouped_questions:
                    grouped_questions['altro'] = []
                grouped_questions['altro'].append(q)
        
        # Display grouped questions
        for category, q_list in grouped_questions.items():
            if q_list:
                with st.expander(f"{category.capitalize()} ({len(q_list)} domande)"):
                    for q in q_list[:5]:  # Show at most 5 questions per category
                        st.markdown(f"- {q}")
                    if len(q_list) > 5:
                        st.markdown(f"*... e altre {len(q_list) - 5} domande*")
    else:
        st.info("Nessuna domanda rilevata nelle conversazioni.")
    
    # Sentiment analysis
    st.markdown("### Analisi del Sentimento")
    st.markdown("Un'analisi del tono e del sentimento nei messaggi degli ospiti:")
    
    # In a real app, this would use a proper sentiment analysis model
    # For demo, we're simulating results
    sentiment_data = {'Positivo': 65, 'Neutro': 30, 'Negativo': 5}
    
    sentiment_df = pd.DataFrame({
        'Sentimento': list(sentiment_data.keys()),
        'Percentuale': list(sentiment_data.values())
    })
    
    st.bar_chart(sentiment_df.set_index('Sentimento'))
    
    st.markdown("**Argomenti positivi più frequenti:**")
    st.markdown("1. Posizione dell'immobile")
    st.markdown("2. Pulizia e confort")
    st.markdown("3. Comunicazione con l'host")
    
    st.markdown("**Argomenti negativi più frequenti:**")
    st.markdown("1. Rumore esterno")
    st.markdown("2. Problemi con il WiFi")
    st.markdown("3. Temperature (riscaldamento/aria condizionata)")

def show_faq_management():
    st.subheader("Gestione FAQ")
    
    # Initialize FAQ data if not exists
    if 'faq_data' not in st.session_state:
        if os.path.exists('data/faq.json'):
            try:
                with open('data/faq.json', 'r', encoding='utf-8') as f:
                    st.session_state.faq_data = json.load(f)
            except:
                st.session_state.faq_data = create_sample_faq()
        else:
            st.session_state.faq_data = create_sample_faq()
    
    # Tabs for FAQ sections
    faq_tabs = st.tabs(["FAQ Generali", "FAQ per Immobili", "Risposte Predefinite"])
    
    with faq_tabs[0]:
        # General FAQs
        st.markdown("### FAQ Generali")
        st.markdown("Queste FAQ si applicano a tutti gli immobili")
        
        general_faqs = st.session_state.faq_data.get("general", [])
        
        # Display existing FAQs
        if general_faqs:
            for i, faq in enumerate(general_faqs):
                with st.expander(f"Q: {faq['question']}"):
                    st.text_area("Risposta", faq['answer'], key=f"gen_faq_answer_{i}", height=100, on_change=update_general_faq, args=(i, "answer"))
                    
                    # Categories
                    categories = st.multiselect(
                        "Categorie",
                        options=["check-in", "check-out", "pulizie", "pagamenti", "servizi", "regole", "trasporti", "altro"],
                        default=faq.get('categories', []),
                        key=f"gen_faq_cat_{i}",
                        on_change=update_general_faq,
                        args=(i, "categories")
                    )
                    
                    # Delete button
                    if st.button("Elimina", key=f"delete_gen_faq_{i}"):
                        general_faqs.pop(i)
                        save_faq_data()
                        st.rerun()
        else:
            st.info("Nessuna FAQ generale. Aggiungi la tua prima FAQ usando il form qui sotto.")
        
        # Add new FAQ
        st.markdown("### Aggiungi Nuova FAQ")
        with st.form("add_general_faq"):
            new_question = st.text_area("Domanda", placeholder="Inserisci la domanda...")
            new_answer = st.text_area("Risposta", placeholder="Inserisci la risposta...")
            new_categories = st.multiselect(
                "Categorie",
                options=["check-in", "check-out", "pulizie", "pagamenti", "servizi", "regole", "trasporti", "altro"]
            )
            submit_button = st.form_submit_button("Aggiungi FAQ")
            
            if submit_button and new_question and new_answer:
                general_faqs.append({
                    "question": new_question,
                    "answer": new_answer,
                    "categories": new_categories
                })
                save_faq_data()
                st.success("FAQ aggiunta con successo!")
                st.rerun()
    
    with faq_tabs[1]:
        # Property-specific FAQs
        st.markdown("### FAQ per Immobili")
        st.markdown("Queste FAQ sono specifiche per ogni immobile")
        
        # Get properties
        properties = st.session_state.properties
        
        if properties:
            property_options = {p["id"]: p["name"] for p in properties}
            selected_property_id = st.selectbox(
                "Seleziona Immobile",
                options=list(property_options.keys()),
                format_func=lambda x: property_options.get(x, "")
            )
            
            if selected_property_id:
                # Initialize property FAQs if needed
                if "properties" not in st.session_state.faq_data:
                    st.session_state.faq_data["properties"] = {}
                
                if selected_property_id not in st.session_state.faq_data["properties"]:
                    st.session_state.faq_data["properties"][selected_property_id] = []
                
                property_faqs = st.session_state.faq_data["properties"][selected_property_id]
                
                # Display existing property FAQs
                if property_faqs:
                    for i, faq in enumerate(property_faqs):
                        with st.expander(f"Q: {faq['question']}"):
                            st.text_area(
                                "Risposta", 
                                faq['answer'], 
                                key=f"prop_faq_answer_{selected_property_id}_{i}", 
                                height=100,
                                on_change=update_property_faq,
                                args=(selected_property_id, i, "answer")
                            )
                            
                            # Categories
                            categories = st.multiselect(
                                "Categorie",
                                options=["check-in", "check-out", "pulizie", "pagamenti", "servizi", "regole", "trasporti", "altro"],
                                default=faq.get('categories', []),
                                key=f"prop_faq_cat_{selected_property_id}_{i}",
                                on_change=update_property_faq,
                                args=(selected_property_id, i, "categories")
                            )
                            
                            # Delete button
                            if st.button("Elimina", key=f"delete_prop_faq_{selected_property_id}_{i}"):
                                property_faqs.pop(i)
                                save_faq_data()
                                st.rerun()
                else:
                    st.info(f"Nessuna FAQ specifica per {property_options.get(selected_property_id)}. Aggiungi la tua prima FAQ usando il form qui sotto.")
                
                # Add new property FAQ
                st.markdown("### Aggiungi Nuova FAQ per questo Immobile")
                with st.form(f"add_property_faq_{selected_property_id}"):
                    new_question = st.text_area("Domanda", placeholder="Inserisci la domanda...")
                    new_answer = st.text_area("Risposta", placeholder="Inserisci la risposta...")
                    new_categories = st.multiselect(
                        "Categorie",
                        options=["check-in", "check-out", "pulizie", "pagamenti", "servizi", "regole", "trasporti", "altro"]
                    )
                    submit_button = st.form_submit_button("Aggiungi FAQ")
                    
                    if submit_button and new_question and new_answer:
                        property_faqs.append({
                            "question": new_question,
                            "answer": new_answer,
                            "categories": new_categories
                        })
                        save_faq_data()
                        st.success("FAQ aggiunta con successo!")
                        st.rerun()
        else:
            st.info("Nessun immobile disponibile. Aggiungi immobili dalla sezione Gestione Immobili.")
    
    with faq_tabs[2]:
        # Predefined responses
        st.markdown("### Risposte Predefinite")
        st.markdown("Crea risposte predefinite per situazioni comuni")
        
        response_categories = [
            "Benvenuto", "Check-in", "Check-out", "Pulizie", 
            "WiFi", "Trasporti", "Ristoranti", "Attrazioni",
            "Problema", "Emergenza", "Ringraziamento", "Altro"
        ]
        
        selected_category = st.selectbox("Categoria", response_categories)
        
        if "responses" not in st.session_state.faq_data:
            st.session_state.faq_data["responses"] = {}
        
        if selected_category not in st.session_state.faq_data["responses"]:
            st.session_state.faq_data["responses"][selected_category] = []
        
        responses = st.session_state.faq_data["responses"][selected_category]
        
        # Display existing responses
        if responses:
            for i, response in enumerate(responses):
                with st.expander(f"Risposta #{i+1}: {response['title']}"):
                    st.text_area(
                        "Testo", 
                        response['text'], 
                        key=f"response_text_{selected_category}_{i}", 
                        height=150,
                        on_change=update_predefined_response,
                        args=(selected_category, i, "text")
                    )
                    
                    # Variables used
                    st.markdown("**Variabili utilizzate:**")
                    for var in response.get('variables', []):
                        st.markdown(f"- `{{{var}}}`")
                    
                    # Delete button
                    if st.button("Elimina", key=f"delete_response_{selected_category}_{i}"):
                        responses.pop(i)
                        save_faq_data()
                        st.rerun()
        else:
            st.info(f"Nessuna risposta predefinita nella categoria '{selected_category}'.")
        
        # Add new response
        st.markdown("### Aggiungi Nuova Risposta Predefinita")
        with st.form(f"add_response_{selected_category}"):
            new_title = st.text_input("Titolo", placeholder="Titolo breve per questa risposta...")
            new_text = st.text_area("Testo", placeholder="Testo della risposta...\nPuoi usare variabili come {guest_name}, {property_name}, {checkin_date}, etc.")
            
            available_vars = ["guest_name", "property_name", "property_address", "checkin_date", "checkout_date", "wifi_password"]
            selected_vars = st.multiselect("Variabili Disponibili", available_vars)
            
            submit_button = st.form_submit_button("Aggiungi Risposta")
            
            if submit_button and new_title and new_text:
                # Extract variables used
                used_vars = []
                for var in available_vars:
                    if "{" + var + "}" in new_text:
                        used_vars.append(var)
                
                responses.append({
                    "title": new_title,
                    "text": new_text,
                    "variables": used_vars
                })
                
                save_faq_data()
                st.success("Risposta predefinita aggiunta con successo!")
                st.rerun()
        
        st.markdown("### Anteprima Risposta")
        st.markdown("Vedi come appare una risposta predefinita con i dati inseriti")
        
        # Get all responses across categories
        all_responses = []
        for category, resp_list in st.session_state.faq_data.get("responses", {}).items():
            for resp in resp_list:
                all_responses.append((f"{category}: {resp['title']}", resp))
        
        if all_responses:
            selected_resp_idx = st.selectbox(
                "Seleziona Risposta da Visualizzare",
                range(len(all_responses)),
                format_func=lambda i: all_responses[i][0] if i < len(all_responses) else ""
            )
            
            if selected_resp_idx is not None and selected_resp_idx < len(all_responses):
                selected_resp = all_responses[selected_resp_idx][1]
                
                # Sample data for preview
                sample_data = {
                    "guest_name": "Carlo Rossi",
                    "property_name": "Appartamento Centro",
                    "property_address": "Via Roma 123, Milano",
                    "checkin_date": "15/06/2025",
                    "checkout_date": "20/06/2025",
                    "wifi_password": "Wifi2025!"
                }
                
                # Display inputs for variables used in the response
                preview_data = {}
                for var in selected_resp.get('variables', []):
                    if var in sample_data:
                        preview_data[var] = st.text_input(f"{var}", value=sample_data[var])
                    else:
                        preview_data[var] = st.text_input(f"{var}")
                
                # Generate preview
                preview_text = selected_resp['text']
                for var, value in preview_data.items():
                    preview_text = preview_text.replace("{" + var + "}", value)
                
                st.markdown("**Anteprima:**")
                st.markdown(f"<div style='background-color: #f0f2f6; padding: 15px; border-radius: 5px;'>{preview_text}</div>", unsafe_allow_html=True)

# Helper functions
def get_conversation_history():
    """Get formatted conversation history for AI context"""
    messages = st.session_state.active_chat.get("messages", [])
    history = []
    
    for msg in messages:
        role = "user" if msg["sender"] == "guest" else "assistant"
        history.append({"role": role, "content": msg["text"]})
    
    return history

def save_conversation(conversation):
    """Save a conversation to the active conversations"""
    if 'active_conversations' not in st.session_state:
        st.session_state.active_conversations = {}
    
    # Generate a UUID if needed
    if "id" not in conversation:
        conversation["id"] = str(uuid.uuid4())
    
    # Add timestamp
    conversation["last_updated"] = datetime.now().isoformat()
    
    # Save to session state
    st.session_state.active_conversations[conversation["id"]] = conversation
    
    # Save all conversations to file
    save_all_conversations()

def save_all_conversations():
    """Save all conversations to file"""
    os.makedirs('data', exist_ok=True)
    with open('data/conversations.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.active_conversations, f, ensure_ascii=False, indent=2)

def load_conversations():
    """Load saved conversations"""
    if 'active_conversations' in st.session_state and st.session_state.active_conversations:
        return st.session_state.active_conversations
    
    if os.path.exists('data/conversations.json'):
        try:
            with open('data/conversations.json', 'r', encoding='utf-8') as f:
                st.session_state.active_conversations = json.load(f)
                return st.session_state.active_conversations
        except:
            return {}
    
    return {}

def update_general_faq(index, field):
    """Update a field in a general FAQ"""
    if field == "answer":
        st.session_state.faq_data["general"][index]["answer"] = st.session_state[f"gen_faq_answer_{index}"]
    elif field == "categories":
        st.session_state.faq_data["general"][index]["categories"] = st.session_state[f"gen_faq_cat_{index}"]
    
    save_faq_data()

def update_property_faq(property_id, index, field):
    """Update a field in a property FAQ"""
    if field == "answer":
        st.session_state.faq_data["properties"][property_id][index]["answer"] = st.session_state[f"prop_faq_answer_{property_id}_{index}"]
    elif field == "categories":
        st.session_state.faq_data["properties"][property_id][index]["categories"] = st.session_state[f"prop_faq_cat_{property_id}_{index}"]
    
    save_faq_data()

def update_predefined_response(category, index, field):
    """Update a field in a predefined response"""
    if field == "text":
        st.session_state.faq_data["responses"][category][index]["text"] = st.session_state[f"response_text_{category}_{index}"]
    
    save_faq_data()

def save_faq_data():
    """Save FAQ data to file"""
    os.makedirs('data', exist_ok=True)
    with open('data/faq.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.faq_data, f, ensure_ascii=False, indent=2)

def create_sample_faq():
    """Create sample FAQ data"""
    return {
        "general": [
            {
                "question": "Come funziona il check-in?",
                "answer": "Il check-in è disponibile dalle 15:00 alle 20:00. Ti contatteremo il giorno prima per confermare l'orario. Per check-in al di fuori di questi orari, è necessario un preavviso.",
                "categories": ["check-in"]
            },
            {
                "question": "Come funziona il check-out?",
                "answer": "Il check-out deve essere effettuato entro le 10:00. È sufficiente lasciare le chiavi sul tavolo e chiudere la porta dietro di te.",
                "categories": ["check-out"]
            },
            {
                "question": "C'è il WiFi?",
                "answer": "Sì, tutti i nostri immobili sono dotati di WiFi gratuito ad alta velocità. Le credenziali di accesso sono disponibili nel manuale dell'ospite all'interno dell'immobile.",
                "categories": ["servizi"]
            }
        ],
        "properties": {},
        "responses": {
            "Benvenuto": [
                {
                    "title": "Messaggio di benvenuto standard",
                    "text": "Gentile {guest_name}, benvenuto/a! Siamo felici di ospitarti presso {property_name}. Il check-in è confermato per il {checkin_date}. Se hai domande prima del tuo arrivo, non esitare a contattarci. A presto!",
                    "variables": ["guest_name", "property_name", "checkin_date"]
                }
            ],
            "Check-in": [
                {
                    "title": "Istruzioni check-in",
                    "text": "Ecco le istruzioni per il check-in presso {property_name}, {property_address}:\n\n1. All'arrivo, suona il campanello 'Appartamento X'\n2. Ti accoglierà il nostro staff\n3. WiFi: {wifi_password}\n\nIn caso di ritardi, chiamaci al +39 123 456 7890.",
                    "variables": ["property_name", "property_address", "wifi_password"]
                }
            ],
            "Check-out": [
                {
                    "title": "Promemoria check-out",
                    "text": "Gentile {guest_name}, ti ricordiamo che domani ({checkout_date}) è previsto il check-out entro le ore 10:00. Ti preghiamo di lasciare le chiavi sul tavolo e chiudere la porta dietro di te. Grazie per aver scelto il nostro alloggio!",
                    "variables": ["guest_name", "checkout_date"]
                }
            ]
        }
    }