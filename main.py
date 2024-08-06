import csv
import random
import requests
from datetime import datetime

# using OpenWeatherMap API !
api_key = '06efeae8d563644b75d5db61030a2359'

class Item:
    def __init__(self, item_type, color, style, description, clean, since_last_worn):
        self.item_type = item_type
        self.color = color
        self.style = style
        self.description = description
        self.clean = clean.lower() == 'yes'
        self.since_last_worn = int(since_last_worn)
        
    def __str__(self):
        return f"{self.item_type}, {self.color}, {self.style}, {self.description}"

# store csv of clothes into dict
def read_clothes_csv(file_path):
    closet = {'top': [], 'bottom': [], 'shoes': [], 'outerwear': []}
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            item = Item(*row)
            closet[item.item_type].append(item)
    return closet

def get_weather_data(city):
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    return data

# Celsius -> Fahrenheit because I'm American caw caw
def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

# Calculate avg, highest, and lowest temp. also rain chance. from 8-4 because that's basically my school day
def analyze_weather_data(data):
    now = datetime.now()
    start_time = datetime(now.year, now.month, now.day, 8, 0)
    end_time = datetime(now.year, now.month, now.day, 16, 0)

    temps = []
    rain_chances = []
    for entry in data['list']:
        forecast_time = datetime.strptime(entry['dt_txt'], '%Y-%m-%d %H:%M:%S')
        if start_time <= forecast_time <= end_time:
            temps.append(entry['main']['temp'])
            rain_chances.append(entry['pop'])  # prob of precipitation

    if not temps:
        return None, None, None, None

    avg_temp_celsius = sum(temps) / len(temps)
    avg_temp_fahrenheit = celsius_to_fahrenheit(avg_temp_celsius)
    max_temp_fahrenheit = celsius_to_fahrenheit(max(temps))
    min_temp_fahrenheit = celsius_to_fahrenheit(min(temps))
    avg_rain_chance = sum(rain_chances) / len(rain_chances) * 100  # to percentage

    return avg_temp_fahrenheit, max_temp_fahrenheit, min_temp_fahrenheit, avg_rain_chance

def suggest_outfit(avg_temp, avg_rain_chance, clothing):
    def select_item(category, style_priority=None):
        items = [
            item
            for item in clothing[category]
                if item.clean and (style_priority is None or item.style == style_priority)
            ]
        if not items:
            items = [item for item in clothing[category] if item.clean]
        if not items:
            return None
        # less worn at top
        items.sort(key=lambda x: x.since_last_worn, reverse=True)
        return items[0] 

    outfit = []
    
    # make sure there's always a top, bottom, and shoes!
    outfit.append(select_item('top'))
    outfit.append(select_item('bottom'))
    outfit.append(select_item('shoes'))

    # outerwear selected based on weather
    if avg_rain_chance > 30:
        # raincoats if it's likely to rain
        outerwear = select_item('outerwear', 'rain')
        if outerwear:
            outfit.append(outerwear)
    elif avg_temp < 55:
        # jacket if the temp is low
        outerwear = select_item('outerwear')
        if outerwear:
            outfit.append(outerwear)
            
    # Display outfit
    print("Outfit suggestion:")
    for item in outfit:
        print(item)

    # optional alternative... currently displays exact same outfit
    alternative = input("Would you like an alternative outfit? (yes/no): ").strip().lower()
    if alternative == 'yes':
        return suggest_outfit(avg_temp, avg_rain_chance, clothing)  # recursive
    return outfit

def reset_clothing(clothing):
    for category in clothing.values():
        for item in category:
            item.since_last_worn += 1

def main_menu():
    print("Welcome to your outfit generator.")
    city = "Merced,US"
    weather_data = get_weather_data(city)
    avg_temp, max_temp, min_temp, avg_rain_chance = analyze_weather_data(weather_data)
    closet = read_clothes_csv('clothes.csv')  # update with your CSV file path

    if avg_temp is not None and avg_rain_chance is not None:
        print(f"\nTemperatures from 8 AM to 4 PM:")
        print(f"Average: {avg_temp:.2f}°F")  
        print(f"Highest: {max_temp:.2f}°F")
        print(f"Lowest: {min_temp:.2f}°F")
        print(f"Average chance of rain: {avg_rain_chance:.2f}%\n")
    else:
        print("No weather data available for the specified time range.\n")

    while True:
        print("Menu:")
        print("1. Generate an outfit")
        print("2. Reset clothing items")
        print("3. Close the program")
        choice = input("Please choose an option (1, 2, or 3): ")

        if choice == '1':
            if avg_temp is not None and avg_rain_chance is not None:
                print(" ")
                outfit_suggestion = suggest_outfit(avg_temp, avg_rain_chance, clothing)
                print(" ")
            else:
                print("Weather data is not available for generating an outfit.")
                print(" ")
        elif choice == '2':
            reset_clothing(clothing)
            print("All clothing items have been reset. Happy laundry day.")
            print(" ")
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please choose again.")

if __name__ == "__main__":
    main_menu()
