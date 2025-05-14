# CiaoHost - Gestione Immobili B&B e Affitti Brevi

CiaoHost è un'applicazione completa per la gestione di immobili destinati ad affitti a breve termine, come B&B, case vacanze e appartamenti. Progettata specificamente per host e property manager italiani, CiaoHost semplifica tutte le attività di gestione quotidiana grazie a un'interfaccia intuitiva e funzionalità avanzate.

## Funzionalità Principali

### 🏘️ Gestione Immobili
- Registrazione e gestione di tutti i tuoi immobili
- Archiviazione dettagli come descrizioni, foto, servizi e istruzioni check-in
- Monitoraggio stato di occupazione e manutenzione

### 📅 Gestione Prenotazioni
- Calendario integrato con visualizzazione per immobile o complessiva
- Gestione check-in/check-out con notifiche automatiche
- Registrazione dati ospiti e tracciamento comunicazioni

### 🤖 Co-Host Virtuale
- Assistente AI per comunicazione con gli ospiti
- Risposte automatiche a domande frequenti
- Supporto multilingua per ospiti internazionali

### 💰 Dynamic Pricing
- Ottimizzazione dei prezzi basata su stagionalità, eventi locali e domanda
- Monitoraggio tariffe della concorrenza
- Analisi delle performance e suggerimenti di prezzo

### 🧹 Gestione Pulizie
- Programmazione automatica pulizie post check-out
- Notifiche SMS/WhatsApp ai servizi di pulizia
- Monitoraggio completamento attività

### 📑 Archivio Fiscale
- Generazione e archiviazione fatture per ogni prenotazione
- Esportazione dati fiscali in formati standard
- Gestione IVA e impostazioni fiscali personalizzate

### 📊 Dashboard e Report
- Panoramica completa delle performance
- Report dettagliati per immobile, periodo o tipologia
- Esportazione dati in PDF, Excel e CSV

## Requisiti Tecnici

- Python 3.10+
- Streamlit
- SQLAlchemy
- Twilio (opzionale, per invio messaggi)
- OpenAI API (opzionale, per funzionalità AI)

## Installazione

1. Clona il repository:
```
git clone https://github.com/username/ciaohost.git
cd ciaohost
```

2. Installa le dipendenze:
```
pip install -r requirements.txt
```

3. Configura le variabili d'ambiente (opzionale per funzionalità avanzate):
```
OPENAI_API_KEY=your_openai_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
```

4. Avvia l'applicazione:
```
streamlit run app.py
```

## Struttura del Progetto

```
ciaohost/
├── app.py                    # Entry point dell'applicazione
├── data/                     # Directory per i dati locali
│   └── logs/                 # Log di messaggi e operazioni
├── pages/                    # Pagine dell'applicazione Streamlit
│   ├── bookings.py           # Gestione prenotazioni
│   ├── cleaning_management.py # Gestione pulizie
│   ├── dynamic_pricing.py    # Prezzi dinamici
│   ├── fiscal_management.py  # Archivio fiscale
│   ├── property_management.py # Gestione immobili 
│   ├── settings.py           # Impostazioni
│   └── virtual_co_host.py    # Co-host virtuale
└── utils/                    # Funzioni e moduli di utilità
    ├── ai_assistant.py       # Integrazione OpenAI
    ├── database.py           # Funzioni database
    ├── message_service.py    # Invio messaggi (SMS/WhatsApp)
    ├── pdf_export.py         # Esportazione PDF
    └── report_generator.py   # Generazione report
```

## Licenza

Questo progetto è rilasciato sotto licenza MIT.

## Contatti

Per supporto o informazioni aggiuntive, contattare: info@ciaohost.com