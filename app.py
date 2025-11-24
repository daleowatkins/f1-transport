import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. Page Config
st.set_page_config(page_title="Team Transport", page_icon="🏎️", layout="centered")

# --- MEMORY FIX: Initialize Session State ---
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False
if 'booking_code' not in st.session_state:
    st.session_state.booking_code = ""

# 2. Load Data
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("bookings.csv", dtype=str)
        data.columns = data.columns.str.strip() # Clean messy headers
        
        # Fill empty cells & Standardize
        data['Code'] = data['Code'].ffill()
        data['Code'] = data['Code'].str.strip().str.upper()
        
        # SAFETY: Default columns if missing
        if 'Direction' not in data.columns:
            data['Direction'] = "Both"
        if 'PickupTime' not in data.columns:
            data['PickupTime'] = "TBC"  # Default if column is missing

        # Convert Lat/Lon to numbers
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

# 4. Login (Updated with Memory Logic)
with st.container(border=True):
    st.write("Please enter your booking reference.")
    
    # Callback to save the search
    def update_search():
        st.session_state.search_performed = True
        st.session_state.booking_code = st.session_state.widget_input.upper().strip()

    with st.form(key='login_form'):
        st.text_input("Booking Code", key="widget_input")
        st.form_submit_button(label='Find My Booking', type="primary", on_click=update_search)

# 5. Results Logic
if st.session_state.search_performed:
    user_code = st.session_state.booking_code
    bookings = df[df['Code'] == user_code]

    if not bookings.empty:
        st.success(f"✅ Found {len(bookings)} passengers")
        
        for index, row in bookings.iterrows():
            with st.expander(f"🎫 TICKET: {row['Name']}", expanded=True):
                
                # --- LOGIC: DETERMINE LABELS & MESSAGES ---
                direction = str(row['Direction']).title()
                
                # Defaults
                label_text = "Pickup:"
                show_pickup_time = False
                show_return_msg = False
                badge_color = "blue"
                icon = "🚌"

                if "Both" in direction:
                    label_text = "Pickup & Dropoff:"
                    show_pickup_time = True
                    show_return_msg = True
                    badge_color, icon = "green", "🔄"
                elif "To" in direction: # To Party Only
                    label_text = "Pickup:"
                    show_pickup_time = True
                    show_return_msg = False
                    badge_color, icon = "orange", "➡️"
                else: # Return Only
                    label_text = "Dropoff:"
                    show_pickup_time = False
                    show_return_msg = True
                    badge_color, icon = "blue", "⬅️"

                # --- DISPLAY BADGE ---
                st.markdown(f":{badge_color}[**{icon} Travel Direction: {direction}**]")
                st.divider()

                # --- DETAILS SECTION ---
                c1, c2 = st.columns([1.5, 2])
                with c1:
                    st.write(f"**Route:** {row['Route']}")
                    
                    # Dynamic Label (Pickup vs Dropoff)
                    st.write(f"**{label_text}** {row['Pickup']}")
                    
                    # Show Pickup Time (Only for Both or To Party)
                    if show_pickup_time:
                        # Get time safely (handle if cell is empty)
                        p_time = row.get('PickupTime')
                        if pd.isna(p_time): p_time = "TBC"
                        st.write(f"**⏱️ Pickup Time:** {p_time}")

                    # Show Return Message (Only for Both or Return)
                    if show_return_msg:
                        st.info("ℹ️ **Return:** All coaches depart Silverstone at 01:00 AM.")

                    if pd.notna(row['MapLink']):
                        st.link_button("📍 Google Maps Link", row['MapLink'])
                        
                with c2:
                    # --- PROFESSIONAL MAP (Folium) ---
                    lat = row.get('Lat')
                    lon = row.get('Lon')
                    
                    if pd.notna(lat) and pd.notna(lon):
                        m = folium.Map(location=[lat, lon], zoom_start=16)
                        folium.Marker(
                            [lat, lon], 
                            popup=row['Pickup'],
                            tooltip=row['Pickup']
                        ).add_to(m)
                        
                        st_folium(
                            m, 
                            height=200, 
                            use_container_width=True, 
                            returned_objects=[],
                            key=f"map_{index}" 
                        )
                    else:
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
        if st.button("Reset Search"):
            st.session_state.search_performed = False
            st.rerun()
