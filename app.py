import streamlit as st
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Team Transport", page_icon="🏎️", layout="centered")

# 2. Load Data
@st.cache_data
def load_data():
    try:
        # Read CSV as string to protect data
        data = pd.read_csv("bookings.csv", dtype=str)
        
        # FIXES: Fill empty cells and standardize Codes
        data['Code'] = data['Code'].ffill()
        data['Code'] = data['Code'].str.strip().str.upper()
        
        # SAFETY: If 'Direction' column is missing in CSV, assume 'Both' to prevent crash
        if 'Direction' not in data.columns:
            data['Direction'] = "Both"
            
        return data
    except FileNotFoundError:
        return None

df = load_data()

# 3. Logo & Title
try:
    st.logo("logo.png")
except:
    pass

st.title("🎄 Christmas Party Transport")

if df is None:
    st.error("⚠️ System Error: 'bookings.csv' not found.")
    st.stop()

# 4. Login Form
with st.container(border=True):
    st.write("Please enter your booking reference.")
    with st.form(key='login_form'):
        user_code = st.text_input("Booking Code").upper().strip()
        submit_button = st.form_submit_button(label='Find My Booking', type="primary")

# 5. Results Logic
if submit_button:
    bookings = df[df['Code'] == user_code]

    if not bookings.empty:
        st.success(f"✅ Found {len(bookings)} passengers")
        
        for index, row in bookings.iterrows():
            with st.expander(f"🎫 TICKET: {row['Name']}", expanded=True):
                
                # --- TRAVEL DIRECTION BADGE ---
                direction = str(row['Direction']).title() # Makes "both" -> "Both"
                
                # Color code the badge based on direction
                if "Both" in direction:
                    badge_color = "green"
                    icon = "🔄"
                elif "To" in direction:
                    badge_color = "orange"
                    icon = "➡️"
                else:
                    badge_color = "blue"
                    icon = "⬅️"

                # UPDATE: Changed text to "Travel Direction:"
                st.markdown(f":{badge_color}[**{icon} Travel Direction: {direction}**]")
                st.divider()
                # -------------------------------------------

                c1, c2 = st.columns([2, 1])
                with c1:
                    st.write(f"**Route:** {row['Route']}")
                    st.write(f"**Pickup:** {row['Pickup']}")
                with c2:
                    if pd.notna(row['MapLink']):
                        st.link_button("🗺️ Map", row['MapLink'])
                    else:
                        st.write("*(No Map)*")
        
        # Email Button
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
