import streamlit as st
import pydeck as pdk
from geopy.geocoders import Nominatim
import pandas as pd

# Initialize geolocator
geolocator = Nominatim(user_agent="city_visualizer")

# Function to get coordinates of a city
def get_coordinates(city_name):
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Title of the Streamlit app
st.title('City Visualization with Streamlit and Pydeck')

# Input for city name
city_name = st.text_input('Enter a city name', '')

if city_name:
    lat, lon = get_coordinates(city_name)
    if lat is not None and lon is not None:
        st.success(f"Coordinates of {city_name}: {lat}, {lon}")

        # Create a DataFrame with the city coordinates
        data = pd.DataFrame({
            'lat': [lat],
            'lon': [lon],
            'name': [city_name]
        })

        # Pydeck layer for scatterplot
        layer = pdk.Layer(
            'ScatterplotLayer',
            data,
            get_position='[lon, lat]',
            get_radius=50000,
            get_color=[255, 0, 0],
            pickable=True
        )

        # Pydeck view state
        view_state = pdk.ViewState(
            latitude=lat,
            longitude=lon,
            zoom=10,
            pitch=0
        )

        # Pydeck deck
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "{name}"}
        )

        # Render the deck.gl map in Streamlit
        st.pydeck_chart(deck)
    else:
        st.error("City not found. Please enter a valid city name.")

