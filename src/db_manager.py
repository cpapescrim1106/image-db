import sqlite3
import os
import pandas as pd

# This path points to the persistent volume inside the container
DB_PATH = "/app/data/catalog.db"

def create_table():
    """Creates the images table if it doesn't exist, based on the full schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS images (
        image_id TEXT PRIMARY KEY,
        image_path TEXT,
        image_thumbnail TEXT,
        image_type TEXT,
        style_name TEXT,
        composition_structure TEXT,
        color_palette TEXT,
        lighting TEXT,
        texture_finish TEXT,
        geometry_flow TEXT,
        primary_emotional_tone TEXT,
        emotional_keyword_tags TEXT,
        narrative_metaphor TEXT,
        ai_generation_prompt TEXT,
        recreation_guidelines TEXT,
        recommended_use_cases TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_image_record(data):
    """Inserts a new image record into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO images (
        image_id, image_path, image_thumbnail, image_type, style_name,
        composition_structure, color_palette, lighting, texture_finish,
        geometry_flow, primary_emotional_tone, emotional_keyword_tags,
        narrative_metaphor, ai_generation_prompt, recreation_guidelines,
        recommended_use_cases
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tuple(data.values()))
    conn.commit()
    conn.close()

def get_all_images():
    """Retrieves all image records as a Pandas DataFrame."""
    if not os.path.exists(DB_PATH):
        return pd.DataFrame() # Return empty dataframe if DB doesn't exist
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT image_id, style_name, image_type, image_path FROM images", conn)
    conn.close()
    return df 