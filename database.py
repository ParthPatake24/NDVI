from modules.lib import *

# Function to initialize the database with separate tables
def sep_initialize_database():
    conn = sqlite3.connect("Vegetation_index_DB_new.db")
    cursor = conn.cursor()

    # Create table for Graph Data  
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Graph_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_name TEXT,
            location TEXT,
            date TEXT,
            vegetation_index_value REAL,
            report_type TEXT 
        )
    ''')
    
    # Create table for Histogram Data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Histogram_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_name TEXT,
            location TEXT,
            data REAL,
            report_type TEXT 
        )
    ''')

    # Create table for Histogram Statistical Data
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS Histogram_statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_name TEXT,
            location TEXT,
            mean REAL,
            median REAL,
            std_dev REAL,
            min_value REAL,
            max_value REAL,
            report_type TEXT
        )
    ''')


    # Create table for Heatmap Data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Heatmap_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_name TEXT,
            location TEXT,
            latitude REAL,
            longitude REAL,
            vegetation_index_value REAL,
            report_type TEXT 
        )
    ''')
    # Create table for Surface Plot Data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Surface_data_report (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_name TEXT,
            location TEXT,
            latitude REAL,
            longitude REAL,
            ndvi_value REAL,
            report_type TEXT 
        )
    ''')
    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User_Feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feedback TEXT
        )
    ''')

    conn.commit()
    conn.close()


# Call this function when starting the app to ensure tables exist
sep_initialize_database()


def clear_database():
    conn = sqlite3.connect("Vegetation_index_DB_new.db")
    cursor = conn.cursor()

    # Fetch all table names dynamically
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    for table in tables:
        cursor.execute(f"DELETE FROM {table}") 

    conn.commit()
    conn.close()
    st.success("✅ All database tables have been cleared!")

# Register cleanup function when Streamlit stops
atexit.register(clear_database)
