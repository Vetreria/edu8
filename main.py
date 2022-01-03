from geopy import distance
import os
import os.path
import requests
import json
import dotenv
from pprint import pprint
import folium
from flask import Flask




def file_open():
    my_file = open("coffee.json", "r", encoding="cp1251")
    file_contents = json.loads(my_file.read())
    return file_contents


def get_coffe():
    list_coffe = []
    for coffe in file_open():
        coffee_name = coffe.get("Name")
        coffe_longitude = coffe.get("Longitude_WGS84")
        coffe_latitude = coffe.get("Latitude_WGS84")
        list_coffe.append(
            {
                "title": coffee_name,
                "distance": 0,
                "latitude": coffe_latitude,
                "longitude": coffe_longitude,
            }
        )
    return list_coffe


def get_dist(point):
    list_coffe_dist = []
    for item_coffe in get_coffe():
        lat = item_coffe["latitude"]
        lon = item_coffe["longitude"]
        point2 = lat, lon
        dist(point, point2)
        item_coffe.update(distance=dist(point, point2))
        list_coffe_dist.append(item_coffe)
    return list_coffe_dist


def dist_key(full_dist_list):
    return full_dist_list["distance"]


def map(point, nearest_five):
    m = folium.Map(location=[point[0], point[1]], zoom_start=16)
    folium.Marker(
        location=[point[0], point[1]],
        popup="Вы тут!",
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(m)
    for cafe in nearest_five:
        lat = cafe["latitude"]
        lon = cafe["longitude"]
        title = cafe["title"]
        print(lat, lon, title)
        folium.Marker([lat, lon], tooltip=title).add_to(m)
    m.save("index.html")


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(
        base_url,
        params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        },
    )
    response.raise_for_status()
    found_places = response.json()["response"]["GeoObjectCollection"]["featureMember"]
    if not found_places:
        return None
    most_relevant = found_places[0]
    lon, lat = most_relevant["GeoObject"]["Point"]["pos"].split(" ")
    print("Ваши координаты: ({}, {})".format(lon, lat))
    return lat, lon


def dist(point, point2):
    return distance.distance(point, point2).km


def hello_world():
    with open("index.html", "r", encoding="utf-8") as file:
        return file.read()


def start_site():
    app = Flask(__name__)
    app.add_url_rule("/", "hello", hello_world)
    app.run("0.0.0.0")


def main():
    dotenv.load_dotenv()
    apikey = os.getenv("KEY_YANDEX")
    address = input("Где Вы?:")
    point = fetch_coordinates(apikey, address)
    full_dist_list = get_dist(point)
    nearest_five = sorted(full_dist_list, key=dist_key)[:5]
    map(point, nearest_five)
    start_site()


if __name__ == "__main__":
    main()
