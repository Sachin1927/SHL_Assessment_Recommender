import streamlit as st
import requests
import json

# Configuration
API_URL = "http://localhost:8000/recommend"  # Ensure your API is running

st.set_page_config(page_title="SHL Assessment Recommender", layout="wide")

st.title(" SHL Intelligent Assessment Recommender")
st.markdown("Enter a Job Description, a Query, or a JD URL below to get assessment recommendations.")

# Input Section
query = st.text_area("Enter Query / JD / URL:", height=150, placeholder="E.g., Looking for a Java Developer who is also a good team player...")

if st.button("Get Recommendations"):
    if not query:
        st.warning("Please enter a query first.")
    else:
        with st.spinner("Analyzing requirements and searching catalog..."):
            try:
                # Call the Backend API
                payload = {"query": query}
                response = requests.post(API_URL, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    assessments = data.get("recommended_assessments", [])
                    
                    if not assessments:
                        st.info("No assessments found.")
                    else:
                        st.success(f"Found {len(assessments)} relevant assessments:")
                        
                        # Display Results
                        for idx, item in enumerate(assessments):
                            with st.expander(f"{idx+1}. {item['name']}"):
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(f"**Description:** {item['description']}")
                                    st.write(f"**Types:** {', '.join(item['test_type'])}")
                                with col2:
                                    st.metric("Duration", f"{item['duration']} min")
                                    st.write(f"**Adaptive:** {item['adaptive_support']}")
                                    st.markdown(f"[View on SHL]({item['url']})")
                else:
                    st.error(f"API Error: {response.status_code}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")

# Sidebar for Context
st.sidebar.header("About")
st.sidebar.info("This system uses RAG (Retrieval Augmented Generation) to match job requirements with SHL's assessment catalog, balancing technical and behavioral needs.")