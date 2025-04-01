import streamlit as st
import requests
import google.generativeai as genai

# Load API keys from Streamlit secrets
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
HOTEL_API_KEY = st.secrets["HOTEL_API_KEY"]
UNSPLASH_ACCESS_KEY = st.secrets["UNSPLASH_ACCESS_KEY"]

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# Function to fetch travel plan from Gemini
def fetch_travel_plan(budget, destination, num_people):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"Create a travel plan for {num_people} people going to {destination} with a budget of {budget} INR."
        response = model.generate_content(prompt)
        return response.text if response else "No response from AI."
    except Exception as e:
        st.error(f"Error with Gemini API: {e}")
        return "Error fetching travel plan."

# Function to fetch hotels
def fetch_hotels(budget, destination, hotel_type):
    HOTEL_API_URL = "https://api.makcorps.com/v1/hotels"
    params = {
        'destination': destination,
        'hotel_type': hotel_type,
        'budget': budget,
        'api_key': HOTEL_API_KEY
    }
    response = requests.get(HOTEL_API_URL, params=params)
    return response.json().get("data", []) if response.status_code == 200 else []

# Function to fetch images from Unsplash
def fetch_images(destination):
    UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"
    params = {
        'query': destination,
        'per_page': 2,  # Fetch 2 images
        'client_id': UNSPLASH_ACCESS_KEY
    }
    response = requests.get(UNSPLASH_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return [img["urls"]["regular"] for img in data["results"][:2]]
    return []

# Streamlit UI
st.title("AI Travel Planner Bot")

# User inputs
budget = st.number_input("Enter your total budget (in INR)", min_value=1000, value=50000)
origin = st.text_input("Where are you starting your journey from?")
destination = st.text_input("Enter destination (e.g., Goa, Delhi, etc.)")
hotel_type = st.selectbox("Select hotel type", ['Budget', '2-Star', '3-Star', '5-Star'])
num_people = st.number_input("Number of travelers", min_value=1, value=1)
rent_car = st.selectbox("Do you want to rent a car?", ["Yes", "No"])

if st.button("Generate Plan"):
    if destination and budget and num_people and origin:
        # Generate travel plan
        travel_plan = fetch_travel_plan(budget, destination, num_people)
        st.subheader(f"Travel Plan for {destination}")
        st.write(travel_plan)

        # Fetch hotels
        hotels = fetch_hotels(budget * 0.4, destination, hotel_type)
        st.subheader(f"Hotels in {destination} within budget:")
        for hotel in hotels:
            st.write(f"**{hotel['name']}** - ₹{hotel['price']} per night")

        # Fetch images
        images = fetch_images(destination)
        if images:
            col1, col2 = st.columns(2)
            with col1:
                st.image(images[0], use_column_width=True)
            with col2:
                if len(images) > 1:
                    st.image(images[1], use_column_width=True)

        # Calculate costs
        car_rental = 0.2 * budget if rent_car == "Yes" else 0
        fuel_cost = 0.05 * budget if rent_car == "Yes" else 0
        total_cost = budget * 0.4 + car_rental + fuel_cost

        # Show summary
        st.subheader("Summary of Your Plan")
        st.write(f"**Starting Point:** {origin}")
        st.write(f"**Destination:** {destination}")
        st.write(f"**Budget:** ₹{budget}")
        st.write(f"**Car Rental Cost:** ₹{car_rental}")
        st.write(f"**Fuel Cost:** ₹{fuel_cost}")
        st.write(f"**Total Estimated Cost:** ₹{total_cost}")
    else:
        st.error("Please fill in all required details.")

