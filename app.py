import streamlit as st
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Team Transport", page_icon="🏎️", layout="centered")

# 2. Load Data (With Safety Fixes)
@st.cache_data
def load_data():
    try:
        # Read the file as text (dtype=str) to keep phone numbers/codes safe
        data = pd.read_csv("bookings.csv", dtype=str)
        
        # ### NEW: Fix Empty Cells ###
        # If you left the guest's code blank in Excel, this copies the code from the person above
        data['Code'] = data['Code'].ffill()
        
        # ### NEW: Cleanup ###
        # Forces all codes to Uppercase and removes invisible spaces
        data['Code'] = data['Code'].str.strip().str.upper()
        
        return data
    except FileNotFoundError:
        return None

df = load_data()

# 3. Main App Interface
try:
    st.logo("logo.png") # Will show if you have a logo.png
except:
    pass

st.title("🎄 Christmas Party Transport")

if df is None:
    st.error("⚠️ System Error: 'bookings.csv' not found.")
    st.stop()

# 4. Login Box
with st.container(border=True):
    st.write("Please enter your booking reference.")
    with st.form(key='login_form'):
        # ### NEW: Auto-uppercase input so 'ham44' works for 'HAM44'
        user_code = st.text_input("Booking Code").upper().strip()
        submit_button = st.form_submit_button(label='Find My Booking', type="primary")

# 5. Results Logic (The fix is here)
if submit_button:
    # Find ALL rows that match the code
    bookings = df[df['Code'] == user_code]

    if not bookings.empty:
        st.success(f"✅ Found {len(bookings)} passengers")
        
        # ### NEW: The Loop ###
        # This goes through EVERY person found, not just the first one
        for index, row in bookings.iterrows():
            with st.expander(f"🎫 TICKET: {row['Name']}", expanded=True):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.write(f"**Route:** {row['Route']}")
                    st.write(f"**Pickup:** {row['Pickup']}")
                with c2:
                    if pd.notna(row['MapLink']):
                        st.link_button("🗺️ Map", row['MapLink'])
                    else:
                        st.write("*(No Map)*")
        
        # Email Amendment Button
        st.divider()
        main_contact = bookings.iloc[0]['Name']
        subject = f"Change Request: {user_code}"
        body = f"Hello Transport Team,%0D%0A%0D%0AI need to request a change for booking {user_code} (Main Contact: {main_contact})."
        
        st.markdown(
            f'<div style="text-align: center;"><a href="mailto:transport@yourteam.com?subject={subject}&body={body}" '
            f'style="text-decoration:none; background-color:#FF4B4B; color:white; padding:10px 20px; border-radius:5px;">'
            f'✉️ Request Amendment for Group</a></div>', 
            unsafe_allow_html=True
        )

    else:
        st.error("❌ Code not found. Please check your reference.")
