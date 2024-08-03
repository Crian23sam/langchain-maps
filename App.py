import cv2
import numpy as np
import geocoder
import requests

# Function to get coordinates from OpenCage Geocoding API
def get_coordinates(api_key, place_name):
    base_url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        "q": place_name,
        "key": api_key
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    
    # Print the response for debugging
    print("Geocoding API response:", data)
    
    if len(data['results']) == 0:
        raise ValueError("No results found for the given place name")
    
    location = data['results'][0]['geometry']
    return (location['lat'], location['lng'])

# Function to get directions from OpenRouteService
def get_directions(api_key, origin, destination):
    base_url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }
    body = {
        "coordinates": [
            [origin[1], origin[0]],
            [destination[1], destination[0]]
        ]
    }
    response = requests.post(base_url, headers=headers, json=body)
    directions = response.json()
    return directions

# Function to parse steps from directions
def parse_steps(directions):
    steps = []
    for segment in directions['routes'][0]['segments'][0]['steps']:
        instruction = segment['instruction']
        distance = segment['distance']
        steps.append((instruction, distance))
    return steps

# Replace with your OpenCage Geocoding API key and OpenRouteService API key
opencage_api_key = "fbd4459c5b124480b1f3011945e27bf4"
ors_api_key = "5b3ce3597851110001cf62482fecc4474ebd448f9734ba7e2bf1c1ef"

# Get the destination input from the user
destination_name = input("Enter the destination place name: ")

# Get the user's current location using geocoder
g = geocoder.ip('me')
current_location = g.latlng
print(f"Current Location: {current_location}")

# Get the destination coordinates using the place name
try:
    destination_coordinates = get_coordinates(opencage_api_key, destination_name)
    print(f"Destination Coordinates: {destination_coordinates}")
except ValueError as e:
    print(e)
    exit()

# Fetch the directions
origin = current_location
directions = get_directions(ors_api_key, origin, destination_coordinates)

# Parse the directions
steps = parse_steps(directions)

# Function to draw direction arrows on the frame
def draw_arrow(frame, instruction):
    if "left" in instruction.lower():
        cv2.arrowedLine(frame, (320, 240), (220, 240), (0, 255, 0), 5, tipLength=0.5)
    elif "right" in instruction.lower():
        cv2.arrowedLine(frame, (320, 240), (420, 240), (0, 255, 0), 5, tipLength=0.5)
    elif "straight" in instruction.lower() or "continue" in instruction.lower():
        cv2.arrowedLine(frame, (320, 240), (320, 140), (0, 255, 0), 5, tipLength=0.5)
    elif "turn around" in instruction.lower():
        cv2.arrowedLine(frame, (320, 240), (320, 340), (0, 255, 0), 5, tipLength=0.5)

# Initialize the camera
cap = cv2.VideoCapture(0)

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Error: Could not open video capture")
    exit()

step_index = 0
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    if not ret:
        print("Error: Could not read frame")
        break
    
    # Convert frame to grayscale (optional)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Overlay the directions on the frame
    if step_index < len(steps):
        instruction, distance = steps[step_index]
        
        # Draw the instructions on the frame
        draw_arrow(frame, instruction)
        cv2.putText(frame, instruction, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, f"Distance: {distance:.2f} meters", (50, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
    
    # Display the resulting frame
    cv2.imshow('AR Navigation', frame)
    
    # Break the loop on 'q' key press or move to next step on 'n' key press
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('n') and step_index < len(steps) - 1:
        step_index += 1

# Release the capture and close windows
cap.release()
cv2.destroyAllWindows()
