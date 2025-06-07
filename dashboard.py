import streamlit as st
from src import db_manager, file_manager, vision_analyzer
import json
import os

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
        
        # Add buttons for AI analysis and manual input
        col1a, col1b = st.columns(2)
        
        with col1a:
            if st.button("🤖 Analyze with AI", use_container_width=True, type="primary"):
                with st.spinner("AI is analyzing the image... This may take a moment."):
                    try:
                        # Save the file first
                        file_path, _ = file_manager.save_uploaded_file(uploaded_file)
                        st.success(f"✅ Image saved to: {file_path}")
                        
                        # Then analyze with AI
                        result = vision_analyzer.analyze_image_with_gpt(file_path)
                        if result:
                            st.session_state.analysis_result = result
                            st.success("🎉 AI analysis completed!")
                        else:
                            st.error("❌ AI analysis failed. Please check your OpenAI API key.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        with col1b:
            if st.button("📝 Manual Input", use_container_width=True):
                try:
                    # Save the file and setup manual input
                    file_path, _ = file_manager.save_uploaded_file(uploaded_file)
                    st.success(f"✅ Image saved to: {file_path}")
                    
                    # Create empty template for manual input
                    st.session_state.analysis_result = {
                        'image_id': f"IMG-{uploaded_file.name.split('.')[0]}",
                        'image_type': 'Real Photograph',
                        'style_name': '',
                        'composition_structure': '',
                        'color_palette': '',
                        'lighting': '',
                        'texture_finish': '',
                        'geometry_flow': '',
                        'primary_emotional_tone': '',
                        'emotional_keyword_tags': '',
                        'narrative_metaphor': '',
                        'ai_generation_prompt': 'N/A',
                        'recreation_guidelines': '',
                        'recommended_use_cases': ''
                    }
                    st.info("📝 Manual input mode activated. Fill in the fields below.")
                except Exception as e:
                    st.error(f"❌ Error saving image: {str(e)}")
                    
        # Add copy/paste section
        if uploaded_file:
            with st.expander("📋 Quick Copy/Paste Input"):
                st.markdown("**Paste JSON data here for quick input:**")
                json_input = st.text_area("Paste metadata JSON:", height=100, placeholder='{"image_id": "IMG-001", "style_name": "Modern Minimalist", ...}')
                if st.button("🔄 Load from JSON"):
                    try:
                        import json
                        parsed_data = json.loads(json_input)
                        st.session_state.analysis_result = parsed_data
                        st.success("✅ Data loaded from JSON!")
                    except Exception as e:
                        st.error(f"❌ Invalid JSON: {str(e)}")

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
    st.markdown(f"**Total Images: {len(catalog_df)}**")
    
    # Display images in a grid
    cols = st.columns(3)
    for idx, row in catalog_df.iterrows():
        col_idx = idx % 3
        with cols[col_idx]:
            # Try to display the image
            try:
                if os.path.exists(row['image_path']):
                    st.image(row['image_path'], caption=f"{row['image_id']}", use_column_width=True)
                else:
                    st.info(f"📷 {row['image_id']}")
            except:
                st.info(f"📷 {row['image_id']}")
            
            st.markdown(f"**Style:** {row['style_name']}")
            st.markdown(f"**Type:** {row['image_type']}")
            
            # Add expandable details
            with st.expander("View Details"):
                st.markdown(f"**Path:** `{row['image_path']}`")
    
    # Also show the dataframe for easy browsing
    with st.expander("📊 View as Table"):
        st.dataframe(catalog_df, use_container_width=True)
else:
    st.write("The catalog is empty. Upload and save an image to see it here.") 