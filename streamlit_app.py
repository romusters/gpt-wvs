import streamlit as st
import pandas as pd
from io import StringIO


# Dummy data voor het DataFrame
from azure.storage.blob import BlobClient, BlobServiceClient

st.set_page_config(layout="wide")

conn_str = st.secrets["CONN_STR"]


@st.cache_data
def get_data():
    blob_client = BlobClient.from_connection_string(conn_str=conn_str, container_name="data", blob_name="cjib_applicable_new_book.csv")
    csv_data = blob_client.download_blob().content_as_text()
    df = pd.read_csv(StringIO(csv_data)).sample(10)
    return df


def save_results(df):
    blob_service_client = BlobServiceClient.from_connection_string(conn_str)

    import string
    import random
    from datetime import datetime
    prefix = ''.join(random.choice(string.ascii_letters) for i in range(4))
    blob_client = blob_service_client.get_blob_client(container="data", blob=f"results\{datetime.now()}_{prefix}_result.csv")
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    # Upload de CSV string als een blob
    blob_client.upload_blob(csv_buffer.getvalue(), overwrite=True)

df = get_data()

# Initialiseer de antwoordenlijst in de session state als deze nog niet bestaat
if 'antwoorden' not in st.session_state:
    st.session_state.antwoorden = []

# Initialiseer de huidige rij-index in de session state als deze nog niet bestaat
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0


# Functie om de huidige rij en vraag te tonen
def show_question():
    current_index = st.session_state.current_index
    if current_index < len(df):
        row = df.iloc[current_index]
        
        # Maak drie kolommen
        col1, col2,col3 = st.columns([1,5,5])
        
        # Toon de waarden in de kolommen
        col1.write(f"{row['article']}")
        col2.write(f"{row['text']}")
        col3.write(f"**AI oordeel:** {row['cjib_applicable_explanation']}")

        # Unieke sleutel voor elke input en knop
        input_key = f"input_{current_index}_{row['article']}"
        button_key = f"button_{current_index}_{row['article']}"
        true_checkbox_key = f"true_checkbox_{current_index}_{row['article']}"
        false_checkbox_key = f"false_checkbox_{current_index}_{row['article']}"
        
        # antwoord = st.checkbox(f"Is het oordeel van de AI correct over de relevantie van het artikel voor het CJIB?", key=input_key)
        st.write("Is het oordeel van de AI correct over de relevantie van het artikel voor het CJIB?")
       
        true_check = st.checkbox(f"Correct", key=true_checkbox_key)
        false_check = st.checkbox(f"Incorrect", key=false_checkbox_key)
       

        # if st.button("Verstuur", key=button_key):
        if true_check:
            # Voeg het antwoord toe aan de antwoordenlijst
            st.session_state.antwoorden.append({
                'Artikel': row['article'],
                'AI oordeel': row['cjib_applicable_explanation'],
                'Gebruiker oordeel': "correct"
            })
            st.success(f"Antwoord voor {row['article']} is opgeslagen!")
            # Verhoog de rij-index om naar de volgende rij te gaan
            st.session_state.current_index += 1
            # Herlaad de pagina om de volgende vraag te tonen
            st.rerun()
        elif false_check:
            # Voeg het antwoord toe aan de antwoordenlijst
            st.session_state.antwoorden.append({
                'Artikel': row['article'],
                'AI oordeel': row['cjib_applicable_explanation'],
                'Gebruiker oordeel': "incorrect" #row['Antwoord']
            })
            st.success(f"Antwoord voor {row['article']} is opgeslagen!")
            # Verhoog de rij-index om naar de volgende rij te gaan
            st.session_state.current_index += 1
            # Herlaad de pagina om de volgende vraag te tonen
            st.rerun()
        else:
            st.error("Vul alstublieft een antwoord in.")
    else:
        st.write("Alle vragen zijn beantwoord!")
        results_df = pd.DataFrame(st.session_state.antwoorden)
        st.dataframe(results_df)
        save_results(results_df)

# Streamlit interface
st.title("Evaluatie AI oordeel CJIB relevantie")
st.subheader("Beoordeel of het artikel relevant is voor het CJIB.")
# Toon de vraag voor de huidige rij
show_question()




