import os
from flask import Flask, request, render_template
from math import radians, cos, sin, asin, sqrt
import requests

app = Flask(__name__)

# Auction houses with pre-geocoded latitude and longitude
auction_houses = [
    {"name": "Pickle's Fyshwick", "address": "179 Gladstone Street, Fyshwick, ACT, 2609", "lat": -35.3386743, "lon": 149.1625838},
    {"name": "Pickle's Belmore", "address": "36-40 Harp Street, Belmore, NSW 2192", "lat": -33.9241295, "lon": 151.0930431},
    {"name": "Pickle's Dubbo", "address": "21L Yarrandale Road, Dubbo, NSW 2830", "lat": -32.2502921, "lon": 148.5945432},
    {"name": "Pickle's Newcastle", "address": "150 Bulls Garden Road, Gateshead NSW 2290", "lat": -32.9521318, "lon": 151.7008958},
    {"name": "Pickle's Tamworth", "address": "37-39 Armstrong Street, Tamworth, NSW, 2340", "lat": -31.0838434, "lon": 150.9226114},
    {"name": "Pickle's Wagga Wagga", "address": "36 Nagle Street, Wagga Wagga, NSW, 2650", "lat": -35.1098761, "lon": 147.3525076},
    {"name": "Slattery's Milperra", "address": "2 Ashford Avenue, Milperra NSW 2214", "lat": -33.9189883, "lon": 150.9557699},
    {"name": "Slattery's Hexham (Newcastle)", "address": "230 Old Maitland Road, Hexham, NSW 2322", "lat": -32.8495152, "lon": 151.6697654},
    {"name": "Pickle's Darwin", "address": "36 Hickman Street, Winnellie, NT, 0821", "lat": -12.4065157, "lon": 130.8764958},
    {"name": "Pickle's Alice Springs", "address": "2 Brown Street, Alice Springs, NT, 0870", "lat": -23.7009919, "lon": 133.8807471},
    {"name": "Slattery's Pinelands (Darwin)", "address": "129 McKinnon Road, Pinelands NT 0829", "lat": -12.4112194, "lon": 130.8497862},
    {"name": "Pickle's Brendale", "address": "14 Tapnor Crescent, Brendale QLD 4500", "lat": -27.3261688, "lon": 152.9782409},
    {"name": "Pickle's Townsville", "address": "787 Ingham Road, Bohle, QLD, 4810", "lat": -19.2557941, "lon": 146.7627701},
    {"name": "Pickle's Rockhampton", "address": "35-51 Somerset Road, Gracemere, QLD, 4702", "lat": -23.4252674, "lon": 150.4893567},
    {"name": "Slattery's Stafford", "address": "3/57 Hayward Street, Stafford, QLD 4053", "lat": -27.4025375, "lon": 153.0111098},
    {"name": "Slattery's Roma", "address": "142 Roma Downs Road, Roma QLD 4455", "lat": -26.5731456, "lon": 148.7963721},
    {"name": "Pickle's Salisbury", "address": "1754 Main North Road, Salisbury Plains, SA 5109", "lat": -34.7625389, "lon": 138.6157778},
    {"name": "Slattery's Adelaide", "address": "3-5 Bollen Street, Kilkenny, SA 5009", "lat": -34.8908293, "lon": 138.5307754},
    {"name": "Pickle's Hobart", "address": "56 Sunderland Street, Moonah, TAS, 7009", "lat": -42.8404266, "lon": 147.3008284},
    {"name": "Pickle's Sunshine", "address": "41–45 McIntyre Road, Sunshine VIC, 3020", "lat": -37.7910133, "lon": 144.8114056},
    {"name": "Slattery's Dandenong South", "address": "41-45 Hydrive Close, Dandenong South, VIC 3175", "lat": -38.0152605, "lon": 145.2145941},
    {"name": "Pickle's Bibra Lake", "address": "Corner Phoenix & Sudlow Roads, Bibra Lake, WA, 6163", "lat": -32.1265221, "lon": 115.8104582},
    {"name": "Slattery's Welshpool", "address": "96 Poole Street, Welshpool WA 6106", "lat": -32.0366853, "lon": 115.9330627}
]

def geocode_address(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': 'Jzivkovic461@gmail.com'  # Your email here per Nominatim policy
    }
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    if data:
        return float(data[0]['lat']), float(data[0]['lon'])
    return None

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

@app.route('/', methods=['GET', 'POST'])
def index():
    nearest_houses = []
    error = None

    if request.method == 'POST':
        user_address = request.form['address']
        user_coords = geocode_address(user_address)
        if not user_coords:
            error = "Could not find that address. Please check and try again."
            return render_template('index.html', results=None, error=error)

        distances = []

        for house in auction_houses:
            distance = haversine(user_coords[0], user_coords[1], house["lat"], house["lon"])
            distances.append({
                "name": house["name"],
                "address": house["address"],
                "distance_km": round(distance, 2)
            })

        # Sort all by distance
        sorted_distances = sorted(distances, key=lambda x: x["distance_km"])

        # Get top 4 results
        nearest_houses = sorted_distances[:4]

        # If less than 4, pad with empty entries to avoid template errors
        while len(nearest_houses) < 4:
            nearest_houses.append({
                "name": "N/A",
                "address": "N/A",
                "distance_km": "N/A"
            })

    return render_template('index.html', results=nearest_houses, error=error)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
