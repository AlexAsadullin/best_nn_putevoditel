import os

cities = ['arzamas', 'pavlovo', 'ichalki', 'boldino', 'bogorodsk', 'kstovo', 'bor', 'arzamas']
files = ['sights.txt', 'housing.txt', 'cafe.txt', 'transport.txt']

for city in cities:
    city_dir = os.path.join('data', city)
    os.makedirs(city_dir, exist_ok=True)
    for file in files:
        file_path = os.path.join(city_dir, file)
        open(file_path, 'w').close()

