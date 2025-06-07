import streamlit as st
from src import db_manager, file_manager, vision_analyzer
import json

# --- Page Config ---
st.set_page_config(page_title="Image Catalog", layout="wide")

# --- Initialize Database ---
db_manager.create_table()

# --- Session State ---
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# --- UI ---
st.title("🖼️ AI-Powered Image Catalog")
st.markdown("Upload an image and use AI to generate its metadata, then save it to the catalog.")

# --- Main Layout ---
col1, col2 = st.columns(2)

with col1:
    st.header("1. Upload Image")
    uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        if st.button("🤖 Analyze with AI", use_container_width=True, type="primary"):
            with st.spinner("AI is analyzing the image... This may take a moment."):
                # Save the file to a temporary location for analysis
                file_path, _ = file_manager.save_uploaded_file(uploaded_file)
                st.session_state.analysis_result = vision_analyzer.analyze_image_with_gpt(file_path)

with col2:
    st.header("2. Review & Save Metadata")
    if uploaded_file and st.session_state.analysis_result:
        data = st.session_state.analysis_result
        
        # Add file paths to the data before saving
        file_path, thumb_path = file_manager.save_uploaded_file(uploaded_file)
        data['image_path'] = file_path
        data['image_thumbnail'] = thumb_path
        
        with st.form("metadata_form"):
            st.subheader("Core Identifiers")
            data['image_id'] = st.text_input("Image ID", value=data.get('image_id', ''))
            data['image_type'] = st.selectbox("Image Type", ["AI-Generated", "Real Photograph"], index=["AI-Generated", "Real Photograph"].index(data.get('image_type', 'AI-Generated')))
            data['style_name'] = st.text_input("Style Name", value=data.get('style_name', ''))

            with st.expander("Visual & Technical Specifications"):
                data['composition_structure'] = st.text_area("Composition & Structure", value=data.get('composition_structure', ''), height=100)
                data['color_palette'] = st.text_area("Color Palette", value=data.get('color_palette', ''), height=100)
                data['lighting'] = st.text_area("Lighting", value=data.get('lighting', ''), height=100)
                data['texture_finish'] = st.text_area("Texture & Finish", value=data.get('texture_finish', ''), height=100)
                data['geometry_flow'] = st.text_area("Geometry & Flow", value=data.get('geometry_flow', ''), height=100)

            with st.expander("Emotional & Narrative Framework"):
                data['primary_emotional_tone'] = st.text_input("Primary Emotional Tone", value=data.get('primary_emotional_tone', ''))
                data['emotional_keyword_tags'] = st.text_input("Emotional Keyword Tags", value=data.get('emotional_keyword_tags', ''))
                data['narrative_metaphor'] = st.text_area("Narrative or Metaphor", value=data.get('narrative_metaphor', ''), height=150)

            with st.expander("Usage & Recreation"):
                data['ai_generation_prompt'] = st.text_area("AI Generation Prompt", value=data.get('ai_generation_prompt', ''), height=150)
                data['recreation_guidelines'] = st.text_area("Recreation Guidelines", value=data.get('recreation_guidelines', ''), height=150)
                data['recommended_use_cases'] = st.text_input("Recommended Use Cases", value=data.get('recommended_use_cases', ''))

            if st.form_submit_button("💾 Save to Catalog", use_container_width=True):
                # Reorder dict to match database schema before inserting
                final_data = {
                    'image_id': data.get('image_id'), 'image_path': data.get('image_path'), 
                    'image_thumbnail': data.get('image_thumbnail'), 'image_type': data.get('image_type'),
                    'style_name': data.get('style_name'), 'composition_structure': data.get('composition_structure'),
                    'color_palette': data.get('color_palette'), 'lighting': data.get('lighting'),
                    'texture_finish': data.get('texture_finish'), 'geometry_flow': data.get('geometry_flow'),
                    'primary_emotional_tone': data.get('primary_emotional_tone'),
                    'emotional_keyword_tags': data.get('emotional_keyword_tags'),
                    'narrative_metaphor': data.get('narrative_metaphor'),
                    'ai_generation_prompt': data.get('ai_generation_prompt'),
                    'recreation_guidelines': data.get('recreation_guidelines'),
                    'recommended_use_cases': data.get('recommended_use_cases')
                }
                db_manager.insert_image_record(final_data)
                st.success(f"Successfully saved image '{data['image_id']}' to the catalog!")
                st.session_state.analysis_result = None # Clear state for next upload
    else:
        st.info("Upload an image and click 'Analyze with AI' to populate metadata fields.")


# --- Display Catalog ---
st.header("📚 Image Catalog")
catalog_df = db_manager.get_all_images()
if not catalog_df.empty:
    st.dataframe(catalog_df, use_container_width=True)
else:
    st.write("The catalog is empty. Upload and save an image to see it here.") 