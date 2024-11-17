import streamlit as st
import pandas as pd
import sqlite3


# Database connection setup
@st.cache_resource
def get_database_connection(db_file):
    return sqlite3.connect(db_file)


# Initialize database from Excel file
@st.cache_resource
def initialize_database(excel_file, db_file, table_name):
    try:
        updated_data = pd.read_excel(excel_file)
        st.success(f"Loaded updated data from '{excel_file}' successfully!")
    except Exception as e:
        st.error(f"Failed to read the Excel file: {e}")
        return None

    conn = sqlite3.connect(db_file)

    try:
        updated_data.to_sql(table_name, conn, if_exists="replace", index=False)
        st.success(f"Data successfully loaded into the '{table_name}' table in {db_file}")
    except Exception as e:
        st.error(f"An error occurred while saving data to the new database: {e}")

    return conn


# File paths
excel_file = "updatedVehicles1.xls"  # Replace with the correct file path
new_db_file = "updated_vehicles.db"
table_name = "vehicles"

# Initialize the database and connection
conn = initialize_database(excel_file, new_db_file, table_name)

# Streamlit UI
st.title("Toyota Financial Services App")
st.header("Vehicle Fuel Economy Data Analyzer")

# Inputs for make and model
user_input = st.text_input("Enter the make (e.g., Toyota):")
user_input2 = st.text_input("Enter the model (e.g., Corolla):")

# Define columns for checkboxes
checkbox_columns = {
    "Charging Information For Electric Vehicles": ["charge120", "charge240"],
    "City Fuel Economy For Regular And Alternative Fuels": ["city08","city08U", "cityA08", "cityA08U"],
    "City Driving Conditions": ["cityCD", "cityE", "cityUF"],
    "Carbon Dioxide Emissions": ["co2", "co2A"],
    "Tailpipe CO2 Emissions": ["co2TailpipeAGpm", "co2TailpipeGpm"],
    "Combined Electric/Fuel Economy": ["comb08", "comb08U", "combA08", "combA08U", "combE"],
    "Combined Driving Conditions": ["combinedCD", "combinedUF"],
    "Engine Cylinders and Displacement": ["cylinders", "displ"],    
    "drive type": ["drive"], "high fuel economy": ["highway08", "highway08U", "highwayA08", "highwayA08U"], 
    "high driving conditions": ["highwayCD", "highwayE", "highwayUF"],
    "driving range": ["range", "rangeCity", "rangeCityA", "rangeHwy", "rangeHwyA"],
    "transmission": ["trany", "trans_dscr"],
    "unadjusted fuel economy": ["UCity", "UCityA", "UHighway", "UHighwayA"],
    "vehicle class": ["VClass"],
    "guzzler": ["guzzler"],
    "turbocharger and supercharger": ["tCharger", "sCharger"],
    "secondary fuel": ["fuelType2"], "additional charging details": ["c240Dscr", "charge240b", "ch240bDscr"],
    "creation/modification dates": ["createdOn", "modifiedOn"],
    "plug-in hybrid metrics": ["phevCity", "pdhevHwy", "phevComb"],
    "miscellaneous": ["ghgScore", "ghgScoreA", "hlv", "hpv", "lv2", "lv4", "pv2", "pv4", "phevBlended", "atvType", "rangeA", "evMotor", "mfrCode", "startStop"],
    }
all_all = ["model"], ["year"], ["barrels08"], ["barrelsA08"], ["engId"], ["eng_dscr"], ["feScore"], ["fuelCost08"], ["fuelCostA08"], ["fuelType"], ["fuelType1"], ["id"], ["mpgData"], ["youSaveSpend"]


# Display checkboxes and collect selected columns
selected_columns = []
for columns in all_all:
    selected_columns.extend(columns)  # Add columns to the list
    
for label, columns in checkbox_columns.items():
    if st.checkbox(label):
        selected_columns.extend(columns)  # Add columns to the list

# Basic analysis button
if st.button("Advanced Analysis"):
    if user_input and user_input2:
        if selected_columns:
            # Dynamically construct SELECT clause based on selected columns
            columns_to_select = ", ".join(selected_columns)
            query = f"""
                SELECT make, baseModel, {columns_to_select}
                FROM vehicles
                WHERE make = ? AND baseModel = ?
            """

            try:
                # Execute the query
                filtered_data = pd.read_sql_query(query, conn, params=(user_input, user_input2))
                if not filtered_data.empty:
                    st.write(f"Results for selected columns triggered by checkboxes:\nTo sort by numerical value, click on each heading to rearrange.")
                    st.write(filtered_data)
                else:
                    st.warning("No data found for the given inputs and selected columns.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please select at least one checkbox to include columns.")
    else:
        st.warning("Please enter both make and model.")