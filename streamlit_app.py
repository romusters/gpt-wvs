import streamlit as st

pg = st.navigation([st.Page("streamlit_pages/homepage.py", title='Homepage'), 
                    st.Page("streamlit_pages/a_verschil.py", title="Verschil"), 
                    st.Page("streamlit_pages/b_impact.py", title="Impact")])
pg.run()

