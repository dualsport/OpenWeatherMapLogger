import requests
import json
import math
from datetime import datetime
from urllib.parse import urljoin
try:
    import dev_settings as s
except:
    import settings as s


def api_get(base_url, api, parameters=None):
    api_endpoint = urljoin(base_url, api)
    headers = {'accept': 'application/json',
               }
    r = requests.get(url=api_endpoint, headers=headers, params=parameters)
    if r.status_code == 200:
        return r.json()
    else:
        print('GET request failed')
        print('Status:', r.status_code)
        print('Reason:', r.reason)
        print('Response text:', r.text)
        print('Requested URL:', r.url)
        print('\n\n')
        return None


def api_post(base_url, api, token=None, parameters=None):
    api_endpoint = urljoin(base_url, api)
    headers = {'Content-Type': 'application/json',
                }
    if token:
        headers['Authorization'] = token

    post = requests.post(url=api_endpoint, headers=headers, json=parameters)
    return post


def dewpoint(temp, humidity):
    # Magnus calculation from https://www.azosensors.com/article.aspx?ArticleID=23
    # table of Magnus coefficients for dew point calculation
    # [minTempC, maxTempC, C1(mbar), C2(-), C3(C)]
    mag = ((-50.9,0,6.1078,17.84362,254.425),(0,100,6.1078,17.08085,234.175))
    for i in range(2):
        if temp > mag[i][0] and temp <= mag[i][1]:
            ms = i
            break
    if ms:
        # Saturated water vapor pressure
        ps = mag[ms][2] * math.exp((mag[ms][3] * temp)/(mag[ms][4] + temp))
        # Partial water vapor pressure
        pd = ps * (humidity / 100)
        return ((-math.log(pd / mag[ms][2]) * mag[ms][4])
                / (math.log(pd / mag[ms][2]) - mag[ms][3])
                )
    else:
        print(f"Temperature {temp} is out of range for dewpoint calculation.")
        return 999


def wx_payload(weather):
    payload = {}
    payload['timestamp'] = datetime.utcfromtimestamp(int(weather['dt']))
    payload['temperature'] = weather['main']['temp']
    payload['dewpoint'] = round(
        dewpoint(weather['main']['temp'],
                 weather['main']['humidity'])
        ,2)
    payload['temp_uom'] = 'degC'
    payload['wind_speed'] = weather['wind']['speed']
    if 'gust' in weather['wind']:
        payload['wind_gust'] = weather['wind']['gust']
    payload['wind_uom'] = 'm/sec'
    payload['wind_dir'] = weather['wind']['deg']
    payload['dir_uom'] = 'degAngle'
    payload['pressure'] = weather['main']['pressure']
    payload['press_uom'] = 'mbar'
    return payload
 

if __name__ == "__main__":
    api = 'weather'
    for station in s.wx_stations:
        parameters = {'appid': s.api_token,
                      'lat': station[1],
                      'lon': station[2],
                      'units': 'metric'}
        weather = api_get(s.wx_base, api, parameters)

        if weather:
            payload = wx_payload(weather)
            payload['identifier'] = station[0]

        dewpt = round(
            dewpoint(weather['main']['temp'],
                     weather['main']['humidity'])
            ,2)

        dt_object = datetime.utcfromtimestamp(int(weather['dt']))
        print(f"timestamp: {dt_object}")
        print(f"identifier: {station[0]}")
        print(f"temperature: {weather['main']['temp']}")
        print(f"dewpoint: {dewpt}")
        print(f"temp_uom: degC")
        print(f"humidity: {weather['main']['humidity']}")
        print(f"pressure: {weather['main']['pressure']}")
        print(f"press_uom: mbar")
        print(f"wind_speed: {weather['wind']['speed']}")
        if 'gust' in weather['wind']:
            print(f"wind_gust: {weather['wind']['gust']}")
        print(f"wind_uom: m/sec")
        print(f"wind_dir: {weather['wind']['deg']}")
        print(f"dir_uom: degAngle")
