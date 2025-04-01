import streamlit as st
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up API Keys
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
HOTEL_API_KEY = os.getenv('HOTEL_API_KEY')
UNSPLASH_API_KEY = os.getenv('UNSPLASH_API_KEY')

# Initialize Gemini AI client
genai.configure(api_key=GEMINI_API_KEY)

# Function to get travel plan using Gemini API
def fetch_travel_plan(budget, destination, num_people, start_location):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = (f"Create a travel plan for {num_people} people starting from {start_location} "
                  f"to {destination} with a budget of {budget} INR.")
        response = model.generate_content(prompt)
        return response.text if response else "No response from AI."
    except Exception as e:
        st.error(f"Error with Gemini API: {e}")
        return "Error fetching travel plan."

# Function to fetch hotels using HotelAPI
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
def fetch_place_images(place):
    UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"
    params = {
        "query": place,
        "client_id": UNSPLASH_API_KEY,
        "per_page": 2  # Fetch 2 images
    }
    response = requests.get(UNSPLASH_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return [img["urls"]["regular"] for img in data["results"][:2]]  # Return top 2 images
    return []

# Streamlit UI
st.title("AI Travel Planner Bot")

# User inputs
start_location = st.text_input("Enter your starting location (e.g., Mumbai, Kolkata, etc.)")
budget = st.number_input("Enter your total budget (in INR)", min_value=1000, value=50000)
destination = st.text_input("Enter destination (e.g., Goa, Delhi, etc.)")
hotel_type = st.selectbox("Select hotel type", ['Budget', '2-Star', '3-Star', '5-Star'])
num_people = st.number_input("Number of travelers", min_value=1, value=1)
rent_car = st.selectbox("Do you want to rent a car?", ["Yes", "No"])

if st.button("Generate Travel Plan"):
    if destination and budget and num_people and start_location:
        travel_plan = fetch_travel_plan(budget, destination, num_people, start_location)
        st.subheader(f"Travel Plan from {start_location} to {destination}")
        st.write(travel_plan)

        hotels = fetch_hotels(budget * 0.4, destination, hotel_type)
        st.subheader(f"Hotels in {destination} within budget:")
        if hotels:
            for hotel in hotels:
                st.write(f"**{hotel['name']}** - ₹{hotel['price']} per night")
        else:
            st.write("No hotels found within your budget.")

        # Car rental and fuel cost calculation
        car_rental = 0.2 * budget if rent_car == "Yes" else 0
        fuel_cost = 0.05 * budget if rent_car == "Yes" else 0
        total_cost = budget * 0.4 + car_rental + fuel_cost

        st.write(f"**Car Rental Cost:** ₹{car_rental}")
        st.write(f"**Fuel Cost:** ₹{fuel_cost}")
        st.write(f"**Total Estimated Cost:** ₹{total_cost}")

        # Fetch and display images of destination
        images = fetch_place_images(destination)
        if images:
            col1, col2 = st.columns(2)  # Display two images side by side
            with col1:
                st.image(images[0], width=300)
            with col2:
                st.image(images[1], width=300)
        else:
            st.write("No images found for this destination.")

    else:
        st.error("Please fill in all required details.")

# Button for Gemini to suggest a destination
if st.button("Suggest Me a Destination"):
    if budget:
        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            prompt = f"Suggest a travel destination in India within a budget of {budget} INR."
            response = model.generate_content(prompt)
            suggested_destination = response.text.strip()
            st.subheader(f"Suggested Destination: {suggested_destination}")

            # Fetch and display images for suggested destination
            images = fetch_place_images(suggested_destination)
            if images:
                col1, col2 = st.columns(2)
                with col1:
                    st.image(images[0], width=300)
                with col2:
                    st.image(images[1], width=300)
            else:
                st.write("No images found for this destination.")

        except Exception as e:
            st.error(f"Error fetching suggestion: {e}")
    else:
        st.error("Please enter your budget before getting a suggestion.")
