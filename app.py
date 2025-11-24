import streamlit as st
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Team Transport", page_icon="🏎️", layout="centered")

# 2. Load Data
@st.cache_data
def load_data():
    try:
        # Read all as string first to protect codes/phones
        data = pd.read_csv("bookings.csv", dtype=str)
        
        # FIXES: Fill empty cells & Standardize Code
        data['Code'] = data['Code'].ffill()
        data['Code'] = data['Code'].str.strip().str.upper()
        
        # SAFETY: Default Direction if missing
        if 'Direction' not in data.columns:
            data['Direction'] = "Both"

        # MAPS: Convert Lat/Lon to numbers (so the map can read them)
        if 'Lat' in data.columns and 'Lon' in data.columns:
            data['Lat'] = pd.to_numeric(data['Lat'], errors='coerce')
            data['Lon'] = pd.to_numeric(data['Lon'], errors='coerce')
            
        return data
    except FileNotFoundError:
        return None

df = load_data()

# 3. Branding
try:
    st.logo("logo.png")
except:
    pass

st.title("🎄 Christmas Party Transport")

if df is None:
    st.error("⚠️ System Error: 'bookings.csv' not found.")
    st.stop()

# 4. Login
with st.container(border=True):
    st.write("Please enter your booking reference.")
    with st.form(key='login_form'):
        user_code = st.text_input("Booking Code").upper().strip()
        submit_button = st.form_submit_button(label='Find My Booking', type="primary")

# 5. Results
if submit_button:
    bookings = df[df['Code'] == user_code]

    if not bookings.empty:
        st.success(f"✅ Found {len(bookings)} passengers")
        
        for index, row in bookings.iterrows():
            with st.expander(f"🎫 TICKET: {row['Name']}", expanded=True):
                
                # --- TRAVEL BADGE ---
                direction = str(row['Direction']).title()
                if "Both" in direction:
                    badge_color, icon = "green", "🔄"
                elif "To" in direction:
                    badge_color, icon = "orange", "➡️"
                else:
                    badge_color, icon = "blue", "⬅️"

                st.markdown(f":{badge_color}[**{icon} Travel Direction: {direction}**]")
                st.divider()

                # --- DETAILS ---
                c1, c2 = st.columns([1.5, 2]) # Adjusted width for map
                with c1:
                    st.write(f"**Route:** {row['Route']}")
                    st.write(f"**Pickup:** {row['Pickup']}")
                    
                    # Link Button (Always useful as a backup)
                    if pd.notna(row['MapLink']):
                        st.link_button("📍 Open in Google Maps", row['MapLink'])
                        
                with c2:
                    # --- THE EMBEDDED MAP ---
                    # We check if we have valid numbers for this specific passenger
                    if 'Lat' in row and pd.notna(row['Lat']) and pd.notna(row['Lon']):
                        # Create a tiny dataframe for just this one spot
                        map_data = pd.DataFrame({'lat': [row['Lat']], 'lon': [row['Lon']]})
                        # Display the map (zoom=15 is street level)
                        st.map(map_data, zoom=14, size=50, use_container_width=True)
                    else:
                        # Fallback if no coordinates in CSV
                        st.info("🗺️ Map preview not available")

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
