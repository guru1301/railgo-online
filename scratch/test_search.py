import urllib.request, json

tests = [
    ('MS',  'KKDI', 'Chennai -> Karaikkudi (full route)'),
    ('VM',  'KKDI', 'Villupuram -> Karaikkudi (mid)'),
    ('TPJ', 'KKDI', 'Trichy -> Karaikkudi (mid)'),
    ('TBM', 'VM',   'Tambaram -> Villupuram (mid)'),
    ('MS',  'TPJ',  'Chennai -> Trichy (mid)'),
]

for src, dst, label in tests:
    url = f'http://127.0.0.1:8001/api/trains/search?source={src}&destination={dst}&date=2026-05-04'
    try:
        data = json.loads(urllib.request.urlopen(url).read())
        trains = {}
        for r in data:
            trains[r['trainNumber']] = r
        print(f"{label}: {len(trains)} train(s)")
        for tn, r in trains.items():
            print(f"   {r['name']} ({tn}) | DEP {r['departureTime']} ARR {r['arrivalTime']}")
    except Exception as e:
        print(f"{label}: ERROR - {e}")
