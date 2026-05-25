from geopy.distance import geodesic

Emission_factors = {
    "flight": 0.254,  # kg CO2e per passenger-kilometer
    "car": 0.120,     # kg CO2e per kilometer
    "train": 0.041,   # kg CO2e per passenger-kil
}

Detour_Index = {   
  "flight": 1.1,  # average detour factor for flights
    "car": 1.3,     # average detour factor for cars
    "train": 1.25,   # average detour factor for trains
}

def calculate_emissions(coord_a,coord_b):
    """coord_a, coord_b: (latitude, longitude)
    """
    distance = geodesic(coord_a, coord_b).kilometers
    if distance <= 400:
        mode = "car"
    elif 400 < distance <= 1500800:
        mode = "train"
    else:        
        mode = "flight"
        
    actual_distance = distance * Detour_Index[mode]
    emissions = actual_distance * Emission_factors[mode]
    return {
        "distance_km": round(distance, 1),
        "inferred_mode": mode,
        "estimated_co2_kg": round(emissions, 2),
        "carbon_category": classify_carbon_emissions(emissions)
    }
    
    
def classify_carbon_emissions(emissions):
    if emissions < 50:
            return "Extremely Low Carbon"
    if emissions < 200:
            return "Normal Carbon"
        
    return "High Carbon"