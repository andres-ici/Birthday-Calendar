import streamlit as st
from supabase import create_client, Client
import pandas as pd 
from streamlit_calendar import calendar

# Initialize connection.
# Uses st.cache_resource to only run once.
#@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
#@st.cache_data(ttl=600)
def run_query():
    return supabase.table("birthdays").select("*").execute()

rows = run_query()

calendar_options = {
    "editable": "true",
    "navLinks": "true",
    "selectable": "true",
            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "dayGridDay,dayGridWeek,dayGridMonth",
            },
            "initialView": "dayGridMonth",
}
calendar_events = [

]
custom_css="""
    .fc-event-past {
        opacity: 0.8;
    }
    .fc-event-time {
        font-style: italic;
    }
    .fc-event-title {
        font-weight: 700;
    }
    .fc-toolbar-title {
        font-size: 2rem;
    }
"""

all_birthdays = supabase.table("birthdays").select("*").execute()
if all_birthdays.data is not None:
    # Convert data to pandas dataframe
    df = pd.DataFrame(all_birthdays.data)

    # Sort birthdays by date
    df = df.sort_values(by="fechaBD")

    for index, row in df.iterrows():
        event = {
            "title": row["nombre"],
            "start": row["fechaBD"], 
        }
        calendar_events.append(event)

st.title("LIFIC BIRTHDAYS")

calendar(events=calendar_events, options=calendar_options, custom_css=custom_css)

st.subheader("All Birthdays:")
for index, row in df.iterrows():
    st.write(f"{row['nombre']} - {row['fechaBD']}")
    

st.subheader("Add your Birthday")
name = st.text_input("Enter your name")
birthday = st.date_input("Add your birthday")
st.write('Your birthday is:', birthday)

if st.button("Submit Birthday"):
    # Prepare data dictionary
    data = {
        "nombre": name,
        "fechaBD": str(birthday),
    }

    # Insert data into Supabase table
    all_birthdays = supabase.table("birthdays").insert(data)

    # Execute the query (no change needed)
    all_birthdays.execute()
    st.success("Birthday saved successfully!")
    
    # Reload page 
    st.rerun()

