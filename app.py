import streamlit as st
import pandas as pd

# 1. Page Configuration (Title and Icon)
st.set_page_config(page_title="Party Transport", page_icon="🏎️")

# 2. Load the Data
# We use a function with @st.cache_data so it doesn't reload the CSV every time someone clicks a button.
@st.cache_data
def load_data():
    # Ensure your CSV file is named exactly 'bookings.csv'
    # 'dtype=str' ensures phone numbers or codes aren't read as math numbers
    data = pd.read_csv("bookings.csv", dtype=str)
    # Clean up any whitespace in the codes (e.g. " HAM44 " becomes "HAM44")
    data['Code'] = data['Code'].str.strip()
    return data

try:
    df = load_data()
except FileNotFoundError:
    st.error("Error: 'bookings.csv' not found. Please upload your data file.")
    st.stop()

# 3. The Website Design
st.title("🎄 Christmas Party Transport")
st.write("Please enter your personal booking code to view your route.")

# 4. The Login Box
# The form container allows users to hit "Enter" on their keyboard to submit
with st.form(key='login_form'):
    user_code = st.text_input("Booking Code")
    submit_button = st.form_submit_button(label='Find My Seat')

# 5. Logic: Check the code
if submit_button:
    # Filter the database for the entered code
    booking = df[df['Code'] == user_code]

    if not booking.empty:
        # Get the first match (in case of duplicates, takes the first)
        details = booking.iloc[0]
        
        st.success(f"Welcome, {details['Name']}!")
        
        # Display Details nicely
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(label="Your Route", value=details['Route'])
        with col2:
            st.info(f"📍 **Pickup Point:**\n\n{details['Pickup']}")

        # Map Button
        if pd.notna(details['MapLink']):
            st.link_button("🗺️ View Pickup Location (Map)", details['MapLink'])
        
        st.divider()
        
        # Amendment / Cancellation Section
        st.subheader("Manage Booking")
        st.write("Need to change or cancel?")
        
        # Create a pre-filled email link
        subject = f"Transport Change Request: {details['Code']}"
        body = f"Hello, I would like to request a change for booking {details['Code']} ({details['Name']}). Details:"
        email_link = f"mailto:transport@yourteam.com?subject={subject}&body={body}"
        
        st.markdown(f'<a href="{email_link}" style="text-decoration:none; background-color:#ff4b4b; color:white; padding:10px 20px; border-radius:5px;">⚠️ Request Cancellation / Amendment</a>', unsafe_allow_html=True)
        
    else:
        st.error("Code not found. Please check and try again.")