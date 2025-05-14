import streamlit as st
import pandas as pd
import json
import io
from datetime import datetime, timedelta
import os
from utils.database import get_all_properties, get_property, get_all_bookings, get_all_invoices, get_booking
from utils.pdf_export import create_property_report_pdf, create_financial_report_pdf
from utils.report_generator import generate_report_template, add_section_to_report, render_report_in_streamlit, generate_pdf_report, download_report, generate_ai_report

def main():
    st.markdown("<h1 class='main-header'>Report Builder</h1>", unsafe_allow_html=True)
    
    # Load property and booking data
    properties = st.session_state.properties
    bookings = st.session_state.bookings
    
    if not properties or not bookings:
        st.warning("Per utilizzare il Report Builder, devi prima aggiungere immobili e prenotazioni.")
        return
    
    # Convert to dataframe
    df_bookings = pd.DataFrame(bookings)
    df_properties = pd.DataFrame(properties)
    
    # Join data for a complete view
    if not df_bookings.empty and not df_properties.empty:
        try:
            df = df_bookings.merge(df_properties, how='left', left_on='property_id', right_on='id', suffixes=('', '_property'))
        except:
            st.error("Errore nell'unione dei dati. Assicurati che i dati siano nel formato corretto.")
            df = df_bookings
    else:
        df = df_bookings
    
    # Create tabs
    tabs = st.tabs(["Report Personalizzato", "Report AI", "Report Salvati"])
    
    with tabs[0]:
        build_custom_report(df)
        
    with tabs[1]:
        create_ai_report(df)
        
    with tabs[2]:
        view_saved_reports(df)

def build_custom_report(df):
    """Build a custom report with user-defined sections"""
    st.subheader("Crea Report Personalizzato")
    st.markdown("Costruisci un report personalizzato selezionando i dati, gli intervalli e le visualizzazioni che desideri includere.")
    
    # Initialize report structure if not exists
    if 'current_report' not in st.session_state:
        st.session_state.current_report = generate_report_template(
            title="Report Personalizzato",
            description="Report personalizzato creato con CiaoHost Report Builder",
            sections=[],
            author="",
            date=datetime.now().strftime("%d/%m/%Y")
        )
    
    # Report basic info
    with st.expander("Informazioni Report", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            report_title = st.text_input("Titolo Report", value=st.session_state.current_report.get("title", ""))
            report_author = st.text_input("Autore", value=st.session_state.current_report.get("author", ""))
        
        with col2:
            report_description = st.text_area("Descrizione", value=st.session_state.current_report.get("description", ""))
            report_date = st.date_input("Data Report", value=datetime.now())
        
        # Update report details
        if st.button("Aggiorna Dettagli Report"):
            st.session_state.current_report["title"] = report_title
            st.session_state.current_report["author"] = report_author
            st.session_state.current_report["description"] = report_description
            st.session_state.current_report["date"] = report_date.strftime("%d/%m/%Y")
            st.success("Dettagli report aggiornati!")
    
    # Date filter for data
    with st.expander("Filtra Dati", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Data Inizio",
                value=(datetime.now() - timedelta(days=180)).date()
            )
        
        with col2:
            end_date = st.date_input(
                "Data Fine",
                value=datetime.now().date()
            )
        
        # Property filter
        properties = st.session_state.properties
        property_options = {p["id"]: p["name"] for p in properties}
        property_options["all"] = "Tutti gli Immobili"
        
        selected_property = st.selectbox(
            "Immobile",
            options=["all"] + list(property_options.keys() - {"all"}),
            format_func=lambda x: property_options.get(x, x)
        )
        
        # Apply filters to dataframe
        filtered_df = df.copy()
        
        # Date filters
        if 'checkin_date' in filtered_df.columns:
            try:
                filtered_df['checkin_date'] = pd.to_datetime(filtered_df['checkin_date'])
                filtered_df = filtered_df[filtered_df['checkin_date'].dt.date >= start_date]
            except:
                st.warning("Errore nella conversione delle date di check-in. Il filtro per data di check-in non è stato applicato.")
        
        if 'checkout_date' in filtered_df.columns:
            try:
                filtered_df['checkout_date'] = pd.to_datetime(filtered_df['checkout_date'])
                filtered_df = filtered_df[filtered_df['checkout_date'].dt.date <= end_date]
            except:
                st.warning("Errore nella conversione delle date di check-out. Il filtro per data di check-out non è stato applicato.")
        
        # Property filter
        if selected_property != "all" and 'property_id' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['property_id'] == selected_property]
        
        # Show filtered data preview
        if not filtered_df.empty:
            st.write(f"Dati filtrati: {len(filtered_df)} record")
            st.dataframe(filtered_df.head(5))
        else:
            st.warning("Nessun dato corrisponde ai filtri selezionati.")
    
    # Add new section
    with st.expander("Aggiungi Sezione", expanded=True):
        st.subheader("Aggiungi una nuova sezione al report")
        
        section_title = st.text_input("Titolo Sezione", key="new_section_title")
        section_content = st.text_area("Contenuto", key="new_section_content", height=150)
        
        # Visualization options
        add_visualization = st.checkbox("Aggiungi Visualizzazione")
        
        if add_visualization:
            viz_type = st.selectbox(
                "Tipo di Visualizzazione",
                options=["bar", "line", "pie", "scatter", "histogram", "heatmap"]
            )
            
            # Configure visualization based on type
            if viz_type == "bar":
                x_col = st.selectbox("Asse X", options=filtered_df.columns.tolist(), key="bar_x")
                y_col = st.selectbox("Asse Y", options=filtered_df.columns.tolist(), key="bar_y")
                
                viz_config = {
                    "x_column": x_col,
                    "y_column": y_col,
                    "title": f"{y_col} per {x_col}"
                }
            
            elif viz_type == "line":
                x_col = st.selectbox("Asse X (data)", options=filtered_df.columns.tolist(), key="line_x")
                y_cols = st.multiselect("Assi Y (metriche)", options=filtered_df.columns.tolist(), key="line_y")
                
                viz_config = {
                    "x_column": x_col,
                    "y_columns": y_cols,
                    "title": f"Trend di {', '.join(y_cols)} nel tempo"
                }
            
            elif viz_type == "pie":
                value_col = st.selectbox("Colonna dei Valori", options=filtered_df.columns.tolist(), key="pie_values")
                
                viz_config = {
                    "column": value_col,
                    "title": f"Distribuzione di {value_col}"
                }
            
            elif viz_type in ["scatter", "histogram", "heatmap"]:
                st.info(f"La configurazione per grafici di tipo {viz_type} sarà disponibile in una versione futura.")
            
            viz_caption = st.text_input("Didascalia Visualizzazione")
        
        # Add section button
        if st.button("Aggiungi Sezione al Report"):
            if section_title and section_content:
                visualizations = []
                
                if add_visualization:
                    visualizations.append({
                        "type": viz_type,
                        "config": viz_config,
                        "caption": viz_caption
                    })
                
                # Add section to report
                st.session_state.current_report = add_section_to_report(
                    st.session_state.current_report,
                    section_title,
                    section_content,
                    visualizations
                )
                
                st.success(f"Sezione '{section_title}' aggiunta al report!")
                
                # Clear inputs
                st.session_state.new_section_title = ""
                st.session_state.new_section_content = ""
            else:
                st.error("Il titolo e il contenuto della sezione sono obbligatori.")
    
    # Preview report
    if len(st.session_state.current_report.get("sections", [])) > 0:
        with st.expander("Anteprima Report", expanded=True):
            st.subheader("Anteprima del Report")
            
            render_report_in_streamlit(st.session_state.current_report, filtered_df)
            
            # Download options
            st.subheader("Download Report")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Download PDF"):
                    pdf_buffer = generate_pdf_report(st.session_state.current_report, filtered_df)
                    
                    st.download_button(
                        label="Scarica PDF",
                        data=pdf_buffer,
                        file_name=f"report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
            
            with col2:
                if st.button("Download Excel"):
                    # Create Excel file with report data
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        # Add filtered data
                        filtered_df.to_excel(writer, sheet_name="Dati", index=False)
                        
                        # Add report metadata
                        metadata = pd.DataFrame([
                            {"Campo": "Titolo", "Valore": st.session_state.current_report.get("title", "")},
                            {"Campo": "Descrizione", "Valore": st.session_state.current_report.get("description", "")},
                            {"Campo": "Autore", "Valore": st.session_state.current_report.get("author", "")},
                            {"Campo": "Data", "Valore": st.session_state.current_report.get("date", "")},
                            {"Campo": "Sezioni", "Valore": len(st.session_state.current_report.get("sections", []))}
                        ])
                        
                        metadata.to_excel(writer, sheet_name="Metadata", index=False)
                        
                        # Add a sheet for each section
                        for i, section in enumerate(st.session_state.current_report.get("sections", [])):
                            # Create a dataframe with section data
                            section_df = pd.DataFrame([
                                {"Campo": "Titolo", "Valore": section.get("title", "")},
                                {"Campo": "Contenuto", "Valore": section.get("content", "")}
                            ])
                            
                            section_df.to_excel(writer, sheet_name=f"Sezione {i+1}", index=False)
                    
                    buffer.seek(0)
                    
                    st.download_button(
                        label="Scarica Excel",
                        data=buffer,
                        file_name=f"report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.ms-excel"
                    )
            
            with col3:
                if st.button("Salva Report"):
                    # Create reports directory if it doesn't exist
                    os.makedirs('data/reports', exist_ok=True)
                    
                    # Generate a filename
                    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    filepath = os.path.join('data/reports', filename)
                    
                    # Save report to file
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(st.session_state.current_report, f, ensure_ascii=False, indent=2)
                    
                    st.success(f"Report salvato come {filename}!")
    else:
        st.info("Aggiungi almeno una sezione per visualizzare l'anteprima del report.")

def create_ai_report(df):
    """Create a report using AI-generated content"""
    st.subheader("Report con AI")
    st.markdown("Genera automaticamente un report completo utilizzando l'intelligenza artificiale per analizzare i tuoi dati.")
    
    # Filter data
    with st.expander("Filtra Dati", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Data Inizio",
                value=(datetime.now() - timedelta(days=90)).date(),
                key="ai_start_date"
            )
        
        with col2:
            end_date = st.date_input(
                "Data Fine",
                value=datetime.now().date(),
                key="ai_end_date"
            )
        
        # Property filter
        properties = st.session_state.properties
        property_options = {p["id"]: p["name"] for p in properties}
        property_options["all"] = "Tutti gli Immobili"
        
        selected_property = st.selectbox(
            "Immobile",
            options=["all"] + list(property_options.keys() - {"all"}),
            format_func=lambda x: property_options.get(x, x),
            key="ai_property"
        )
        
        # Apply filters to dataframe
        filtered_df = df.copy()
        
        # Date filters
        if 'checkin_date' in filtered_df.columns:
            try:
                filtered_df['checkin_date'] = pd.to_datetime(filtered_df['checkin_date'])
                filtered_df = filtered_df[filtered_df['checkin_date'].dt.date >= start_date]
            except:
                st.warning("Errore nella conversione delle date di check-in. Il filtro per data di check-in non è stato applicato.")
        
        if 'checkout_date' in filtered_df.columns:
            try:
                filtered_df['checkout_date'] = pd.to_datetime(filtered_df['checkout_date'])
                filtered_df = filtered_df[filtered_df['checkout_date'].dt.date <= end_date]
            except:
                st.warning("Errore nella conversione delle date di check-out. Il filtro per data di check-out non è stato applicato.")
        
        # Property filter
        if selected_property != "all" and 'property_id' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['property_id'] == selected_property]
    
    # Report type and settings
    report_type = st.selectbox(
        "Tipo di Report",
        options=["overview", "detailed", "executive"],
        format_func=lambda x: {
            "overview": "Report di Sintesi",
            "detailed": "Report Dettagliato",
            "executive": "Report Dirigenziale"
        }.get(x)
    )
    
    report_title = st.text_input("Titolo Report", value="Analisi Prestazioni Immobili")
    
    # Generate report button
    if st.button("Genera Report AI"):
        with st.spinner("L'IA sta analizzando i dati e generando il report... Questo potrebbe richiedere alcuni secondi."):
            try:
                # Generate AI report
                ai_report = generate_ai_report(filtered_df, report_type, report_title)
                
                # Store in session state
                st.session_state.ai_report = ai_report
                
                st.success("Report generato con successo!")
            except Exception as e:
                st.error(f"Errore nella generazione del report: {str(e)}")
                st.error("Il report verrà generato con contenuto simulato.")
                
                # Create a simulated report
                sections = [
                    {
                        "title": "Panoramica Prestazioni",
                        "content": "Questa panoramica mostra le prestazioni degli immobili nel periodo selezionato. I dati indicano un tasso di occupazione medio del 75% con un prezzo medio di €120 per notte. Le prenotazioni sono distribuite uniformemente durante la settimana, con picchi nel fine settimana.",
                        "visualizations": [
                            {
                                "type": "bar",
                                "config": {
                                    "x_column": "property_name",
                                    "y_column": "total_price",
                                    "title": "Ricavi per Immobile"
                                },
                                "caption": "Distribuzione dei ricavi per immobile nel periodo selezionato"
                            }
                        ]
                    },
                    {
                        "title": "Analisi Stagionalità",
                        "content": "L'analisi della stagionalità mostra un chiaro pattern di prenotazioni, con alta stagione nei mesi estivi e durante le festività invernali. I prezzi seguono questo trend, con un aumento medio del 30% durante l'alta stagione.",
                        "visualizations": []
                    },
                    {
                        "title": "Raccomandazioni",
                        "content": "Basandoci sui dati analizzati, raccomandiamo di:\n- Aumentare i prezzi del 10-15% nei weekend\n- Offrire sconti per soggiorni di lunga durata durante la bassa stagione\n- Migliorare la visibilità degli immobili con meno prenotazioni",
                        "visualizations": []
                    }
                ]
                
                ai_report = generate_report_template(
                    title=report_title,
                    description=f"Report generato automaticamente per il periodo {start_date} - {end_date}",
                    sections=sections,
                    author="CiaoHost AI Assistant",
                    date=datetime.now().strftime("%d/%m/%Y")
                )
                
                # Store in session state
                st.session_state.ai_report = ai_report
    
    # Show report if available
    if 'ai_report' in st.session_state:
        with st.expander("Anteprima Report AI", expanded=True):
            st.subheader("Anteprima del Report Generato con AI")
            
            render_report_in_streamlit(st.session_state.ai_report, filtered_df)
            
            # Download options
            st.subheader("Download Report")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Download PDF", key="ai_pdf"):
                    pdf_buffer = generate_pdf_report(st.session_state.ai_report, filtered_df)
                    
                    st.download_button(
                        label="Scarica PDF",
                        data=pdf_buffer,
                        file_name=f"ai_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
            
            with col2:
                if st.button("Download Excel", key="ai_excel"):
                    # Create Excel file with report data
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        # Add filtered data
                        filtered_df.to_excel(writer, sheet_name="Dati", index=False)
                        
                        # Add report metadata
                        metadata = pd.DataFrame([
                            {"Campo": "Titolo", "Valore": st.session_state.ai_report.get("title", "")},
                            {"Campo": "Descrizione", "Valore": st.session_state.ai_report.get("description", "")},
                            {"Campo": "Autore", "Valore": st.session_state.ai_report.get("author", "")},
                            {"Campo": "Data", "Valore": st.session_state.ai_report.get("date", "")},
                            {"Campo": "Sezioni", "Valore": len(st.session_state.ai_report.get("sections", []))}
                        ])
                        
                        metadata.to_excel(writer, sheet_name="Metadata", index=False)
                        
                        # Add a sheet for each section
                        for i, section in enumerate(st.session_state.ai_report.get("sections", [])):
                            # Create a dataframe with section data
                            section_df = pd.DataFrame([
                                {"Campo": "Titolo", "Valore": section.get("title", "")},
                                {"Campo": "Contenuto", "Valore": section.get("content", "")}
                            ])
                            
                            section_df.to_excel(writer, sheet_name=f"Sezione {i+1}", index=False)
                    
                    buffer.seek(0)
                    
                    st.download_button(
                        label="Scarica Excel",
                        data=buffer,
                        file_name=f"ai_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.ms-excel"
                    )
            
            with col3:
                if st.button("Salva Report", key="ai_save"):
                    # Create reports directory if it doesn't exist
                    os.makedirs('data/reports', exist_ok=True)
                    
                    # Generate a filename
                    filename = f"ai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    filepath = os.path.join('data/reports', filename)
                    
                    # Save report to file
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(st.session_state.ai_report, f, ensure_ascii=False, indent=2)
                    
                    st.success(f"Report AI salvato come {filename}!")

def view_saved_reports(df):
    """View and manage saved reports"""
    st.subheader("Report Salvati")
    
    # Create reports directory if it doesn't exist
    os.makedirs('data/reports', exist_ok=True)
    
    # Get list of saved reports
    report_files = [f for f in os.listdir('data/reports') if f.endswith('.json')]
    
    if not report_files:
        st.info("Nessun report salvato. Crea un report utilizzando le schede 'Report Personalizzato' o 'Report AI'.")
        return
    
    # Sort reports by date (newest first)
    report_files.sort(reverse=True)
    
    # Create a list of reports with metadata
    reports_meta = []
    
    for file in report_files:
        filepath = os.path.join('data/reports', file)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                report = json.load(f)
                
                # Extract creation date from filename or use report date
                if "_" in file:
                    date_str = file.split("_")[1].split(".")[0]
                    if len(date_str) == 8:  # YYYYMMDD format
                        created_date = f"{date_str[6:8]}/{date_str[4:6]}/{date_str[0:4]}"
                    else:
                        created_date = report.get("date", "N/A")
                else:
                    created_date = report.get("date", "N/A")
                
                reports_meta.append({
                    "filename": file,
                    "title": report.get("title", "Untitled"),
                    "date": report.get("date", "N/A"),
                    "created": created_date,
                    "author": report.get("author", ""),
                    "sections": len(report.get("sections", [])),
                    "type": "AI" if "ai_report" in file else "Custom"
                })
        except:
            reports_meta.append({
                "filename": file,
                "title": "Error loading report",
                "date": "N/A",
                "created": "N/A",
                "author": "",
                "sections": 0,
                "type": "Unknown"
            })
    
    # Display reports in a table
    reports_df = pd.DataFrame(reports_meta)
    st.dataframe(reports_df, use_container_width=True)
    
    # Select a report to view
    selected_report = st.selectbox(
        "Seleziona un Report da Visualizzare",
        options=report_files,
        format_func=lambda x: next((r["title"] for r in reports_meta if r["filename"] == x), x)
    )
    
    if selected_report:
        filepath = os.path.join('data/reports', selected_report)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            with st.expander("Visualizza Report", expanded=True):
                st.subheader(report.get("title", "Untitled Report"))
                st.markdown(f"**Data:** {report.get('date', 'N/A')} | **Autore:** {report.get('author', 'N/A')}")
                st.markdown(report.get("description", ""))
                
                # Render report
                render_report_in_streamlit(report, df)
                
                # Actions
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Download PDF", key="saved_pdf"):
                        pdf_buffer = generate_pdf_report(report, df)
                        
                        st.download_button(
                            label="Scarica PDF",
                            data=pdf_buffer,
                            file_name=f"{selected_report.split('.')[0]}.pdf",
                            mime="application/pdf"
                        )
                
                with col2:
                    if st.button("Edit Report", key="edit_report"):
                        # Load report into current_report for editing
                        st.session_state.current_report = report
                        st.success("Report caricato per la modifica nella scheda 'Report Personalizzato'")
                
                with col3:
                    if st.button("Delete Report", key="delete_report"):
                        os.remove(filepath)
                        st.success(f"Report {selected_report} eliminato.")
                        st.rerun()
        except Exception as e:
            st.error(f"Errore nel caricamento del report: {str(e)}")

if __name__ == "__main__":
    main()