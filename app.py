import os
from flask import Flask, request, render_template
from math import radians, cos, sin, asin, sqrt
import requests
import openrouteservice

app = Flask(__name__)

ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjA5YzhkNjdlOWYyODQ1ZTk5YzBhMzI2MDVkYzM0MDEwIiwiaCI6Im11cm11cjY0In0="
client = openrouteservice.Client(key=ORS_API_KEY)

# Auction houses with pre-geocoded latitude and longitude
auction_houses = [
    # Pickles locations
    {"name": "Pickle's Fyshwick", "address": "179 Gladstone Street, Fyshwick, ACT, 2609", "lat": -35.3386743, "lon": 149.1625838},
    {"name": "Pickle's Belmore", "address": "36-40 Harp Street, Belmore, NSW 2192", "lat": -33.9241295, "lon": 151.0930431},
    {"name": "Pickle's Dubbo", "address": "21L Yarrandale Road, Dubbo, NSW 2830", "lat": -32.2502921, "lon": 148.5945432},
    {"name": "Pickle's Newcastle", "address": "150 Bulls Garden Road, Gateshead NSW 2290", "lat": -32.9521318, "lon": 151.7008958},
    {"name": "Pickle's Tamworth", "address": "37-39 Armstrong Street, Tamworth, NSW, 2340", "lat": -31.0838434, "lon": 150.9226114},
    {"name": "Pickle's Wagga Wagga", "address": "36 Nagle Street, Wagga Wagga, NSW, 2650", "lat": -35.1098761, "lon": 147.3525076},
    {"name": "Pickle's Darwin", "address": "36 Hickman Street, Winnellie, NT, 0821", "lat": -12.4065157, "lon": 130.8764958},
    {"name": "Pickle's Alice Springs", "address": "2 Brown Street, Alice Springs, NT, 0870", "lat": -23.7009919, "lon": 133.8807471},
    {"name": "Pickle's Brendale", "address": "14 Tapnor Crescent, Brendale QLD 4500", "lat": -27.3261688, "lon": 152.9782409},
    {"name": "Pickle's Townsville", "address": "787 Ingham Road, Bohle, QLD, 4810", "lat": -19.2557941, "lon": 146.7627701},
    {"name": "Pickle's Rockhampton", "address": "35-51 Somerset Road, Gracemere, QLD, 4702", "lat": -23.4252674, "lon": 150.4893567},
    {"name": "Pickle's Salisbury", "address": "1754 Main North Road, Salisbury Plains, SA 5109", "lat": -34.7625389, "lon": 138.6157778},
    {"name": "Pickle's Hobart", "address": "56 Sunderland Street, Moonah, TAS, 7009", "lat": -42.8404266, "lon": 147.3008284},
    {"name": "Pickle's Sunshine", "address": "41–45 McIntyre Road, Sunshine VIC, 3020", "lat": -37.7910133, "lon": 144.8114056},
    {"name": "Pickle's Bibra Lake", "address": "Corner Phoenix & Sudlow Roads, Bibra Lake, WA, 6163", "lat": -32.1265221, "lon": 115.8104582},

    # Slattery updated locations
    {"name": "Slattery's Milperra (Sydney)", "address": "2 Ashford Avenue, Milperra, NSW, 2214", "lat": -33.9189883, "lon": 150.9557699},
    {"name": "Slattery's Hexham (Newcastle)", "address": "230 Old Maitland Road, Hexham, NSW, 2322", "lat": -32.8495152, "lon": 151.6697654},
    {"name": "Slattery's Dandenong South (Melbourne)", "address": "140–152 National Drive, Dandenong South, VIC, 3175", "lat": -38.031341, "lon": 145.213222},
    {"name": "Slattery's Pinkenba (Brisbane)", "address": "131 Main Beach Road, Pinkenba, QLD 4008", "lat": -27.420635, "lon": 153.115622},
    {"name": "Slattery's Roma", "address": "142 Roma Downs Road, Roma QLD 4455", "lat": -26.5731456, "lon": 148.7963721},
    {"name": "Slattery's Mackay", "address": "119A Boundary Road, Paget QLD 4740", "lat": -21.164828, "lon": 149.148532},
    {"name": "Slattery's Townsville (Grays / Slattery)", "address": "13–17 Lorna Court, Bohle, QLD 4818", "lat": -19.271935, "lon": 146.711052},
    {"name": "Slattery's Perth", "address": "6 Spartan Street, Jandakot, WA 6164", "lat": -32.095694, "lon": 115.864571},
    {"name": "Slattery's Karratha", "address": "Lot 38, Exploration Drive, Gap Ridge, Karratha, WA", "lat": -20.706278, "lon": 116.821754},
    {"name": "Slattery's Adelaide (Grays / Slattery)", "address": "3 Maxwell Road, Pooraka, SA 5095", "lat": -34.829736, "lon": 138.626892},
    {"name": "Slattery's Canberra", "address": "8/22 Lithgow Street, Fyshwick, ACT, 2609", "lat": -35.329512, "lon": 149.169945},
    {"name": "Slattery's Yarrawonga (Grays / Slattery)", "address": "38 Toupein Road, Yarrawonga, NT 0830", "lat": -12.476311, "lon": 130.973214}
]

# Capital city coordinates
CAPITALS = {
    "NSW": (-33.8688, 151.2093),
    "VIC": (-37.8136, 144.9631),
    "QLD": (-27.4698, 153.0251),
    "SA": (-34.9285, 138.6007),
    "ACT": (-35.2809, 149.1300),
    "WA": (-31.9505, 115.8605),
    "NT": (-12.4634, 130.8456),
    "TAS": (-42.8821, 147.3272)
}

# --- ADDED: State name normalization for rubric ---
STATE_MAP = {
    "New South Wales": "NSW",
    "Victoria": "VIC",
    "Queensland": "QLD",
    "South Australia": "SA",
    "Western Australia": "WA",
    "Tasmania": "TAS",
    "Northern Territory": "NT",
    "Australian Capital Territory": "ACT"
}

def geocode_address(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1, "addressdetails": 1}
    headers = {"User-Agent": "Jzivkovic461@gmail.com"}
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    if data:
        addr = data[0]["address"]
        state_name = addr.get("state")
        state_code = STATE_MAP.get(state_name, state_name)
        return float(data[0]["lat"]), float(data[0]["lon"]), state_code
    return None

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * asin(sqrt(a))

@app.route('/', methods=['GET', 'POST'])
def index():
    nearest_houses = []
    note = None
    error = None

    if request.method == 'POST':
        user_address = request.form['address']
        outstanding = request.form.get('outstanding')

        geo = geocode_address(user_address)
        if not geo:
            error = "Could not find that address. Please check and try again."
            return render_template('index.html', results=None, error=error)

        lat, lon, state = geo
        is_metro = False

        if state in CAPITALS:
            cap_lat, cap_lon = CAPITALS[state]
            if haversine(lat, lon, cap_lat, cap_lon) <= 60:
                is_metro = True

        # --- Rubric logic ---
        if outstanding:
            amount = float(outstanding)
            if state in ["NSW", "VIC", "QLD"] and is_metro:
                if amount < 60000:
                    note = f"This vehicle is under $60,000 and is in {state} Metro. Please advise agent to deliver vehicle to a Pickles Auction House."
                else:
                    note = f"This vehicle is over $60,000 and is in {state} Metro. Please advise agent to deliver vehicle to a Slattery's Auction House."
            elif state in ["NSW", "VIC", "QLD"] and not is_metro:
                note = f"This vehicle is in {state} Regional. Please advise agent to deliver vehicle to a Pickles Auction House."
            elif state in ["SA", "ACT", "WA", "NT", "TAS"]:
                note = f"This vehicle is in {state}. Please advise agent to deliver vehicle to a Pickles Auction House."

        try:
            locations = [(lon, lat)] + [(h["lon"], h["lat"]) for h in auction_houses]
            matrix = client.distance_matrix(
                locations=locations,
                profile='driving-car',
                metrics=['distance']
            )

            for idx, house in enumerate(auction_houses, start=1):
                dist_m = matrix['distances'][0][idx]
                dist_km = round(dist_m / 1000, 2)
                nearest_houses.append({
                    "name": house["name"],
                    "address": house["address"],
                    "distance_km": dist_km
                })

            nearest_houses = sorted(nearest_houses, key=lambda x: x["distance_km"])[:5]

        except Exception as e:
            distances = []
            for house in auction_houses:
                distance = haversine(lat, lon, house["lat"], house["lon"])
                distances.append({
                    "name": house["name"],
                    "address": house["address"],
                    "distance_km": round(distance, 2)
                })
            nearest_houses = sorted(distances, key=lambda x: x["distance_km"])[:5]

    return render_template('index.html', results=nearest_houses, note=note, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
