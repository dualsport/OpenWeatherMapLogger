import requests
import json
import math
from datetime import datetime, timezone
from urllib.parse import urljoin
try:
    import dev_settings as s
except:
    import settings as s


def api_get(base_url, api, token=None, parameters=None):
    api_endpoint = urljoin(base_url, api)
    headers = {'accept': 'application/json'}
    if token:
        headers['Authorization'] = token
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

    p = requests.post(url=api_endpoint, headers=headers, json=parameters)
    if p.status_code == 201:
        return p
    else:
        print('POST request failed')
        print('Status:', p.status_code)
        print('Reason:', p.reason)
        print('Response text:', p.text)
        print('Requested URL:', p.url)
        print('\n\n')
        return None


def station_list():
    #returns a list of weather stations known by IOT endpoint
    api_stations = api_get(s.endp_base, s.endp_station_list, s.api_token)
    station_li = []
    for station in api_stations:
        station_li.append(station['identifier'])
    return station_li
    return st


def create_station(station):
    #Creates new weather station
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    payload = {'identifier': station[0],
                'name': station[0],
                'description': 'Added by OpenWeatherMapLogger.py ' + ts,
                'latitude': station[1],
                'longitude': station[2],
                'type': 'Open Weather'}
    response = api_post(s.endp_base, s.endp_station_add, s.api_token, payload)
    if response.status_code == 201:
        print(f"Wx Station created: {station[0]}")
        return True
    else:
        print(f"Wx Station creation FAILED: {station[0]}")
        return False


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
    ts = datetime.fromtimestamp(weather['dt'], tz=timezone.utc)
    payload = {}
    payload['timestamp'] = ts.isoformat()
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
    api_stations = station_list()
    for station in s.wx_stations:
        if station[0] in api_stations:
            valid_station = True
        else:
            # Create new station
            valid_station = create_station(station)

        if valid_station:
            # Get Open Weather weather data
            parameters = {'appid': s.ow_app_token,
                          'lat': station[1],
                          'lon': station[2],
                          'units': 'metric'}
            weather = api_get(s.wx_base, 'weather', None, parameters)
            if weather:
                payload = wx_payload(weather)
                payload['identifier'] = station[0]

            #Get current record from IOT api
            cur = api_get(s.endp_base, s.endp_current_data + station[0], s.api_token)
            record_exists = False
            if len(cur) > 0:
                cur_ts = cur[0]['timestamp'].replace('Z', '+00:00')
                record_exists = (cur_ts == payload['timestamp'])
            if not record_exists:
                #Post station weather
                post = api_post(s.endp_base, s.endp_data_add, s.api_token, payload)
                print(f"{station[0]} posted new record for {payload['timestamp']}")
            else:
                print(f"{station[0]} has existing record for {payload['timestamp']}")


        #---- Print statements for testing - Comment out below code before deploying -----
        #dewpt = round(
        #    dewpoint(weather['main']['temp'],
        #             weather['main']['humidity'])
        #    ,2)

        #dt_object = datetime.utcfromtimestamp(int(weather['dt']))
        #print(f"timestamp: {dt_object}")
        #print(f"identifier: {station[0]}")
        #print(f"temperature: {weather['main']['temp']}")
        #print(f"dewpoint: {dewpt}")
        #print(f"temp_uom: degC")
        #print(f"humidity: {weather['main']['humidity']}")
        #print(f"pressure: {weather['main']['pressure']}")
        #print(f"press_uom: mbar")
        #print(f"wind_speed: {weather['wind']['speed']}")
        #if 'gust' in weather['wind']:
        #    print(f"wind_gust: {weather['wind']['gust']}")
        #print(f"wind_uom: m/sec")
        #print(f"wind_dir: {weather['wind']['deg']}")
        #print(f"dir_uom: degAngle")
