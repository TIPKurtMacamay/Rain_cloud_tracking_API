from faker import Faker
import requests
import random
import datetime
import json
import time
import argparse


API_URL = 'http://localhost:5000'

fake = Faker()

def startDevice(id):
    pass


def runWeatherDummy(device_id):    
    timestamp = fake.date_time_between(start_date='-7d', end_date='now')  # Generate a random timestamp within the last 7 days
    rainfall_amount = round(random.uniform(0.0, 10.0), 2)  # Generate random rainfall amount between 0 and 10 mm
    air_temperature = round(random.uniform(-20.0, 40.0), 2)  # Generate random air temperature between -20°C and 40°C
    humidity = round(random.uniform(0.0, 100.0), 2)  # Generate random humidity between 0% and 100%
    pressure = round(random.uniform(900.0, 1100.0), 2)  # Generate random pressure between 900 hPa and 1100 hPa
    
    x = requests.post(
        f"{API_URL}/log-weather-data", 
        json = {
            "device_id":device_id,
            "rainfall_amount":rainfall_amount,
            "air_temperature":air_temperature,
            "humidity":humidity,
            "pressure":pressure
        }
    )
    
    print(x)
    time.sleep(2)
    


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Process a number ID.")
    parser.add_argument("number_id", type=int, help="The number ID to process.")
    args = parser.parse_args()

    # Access the number ID provided as an argument
    number_id = args.number_id
    print("Number ID:", number_id)
    
    while True:
        runWeatherDummy(number_id)