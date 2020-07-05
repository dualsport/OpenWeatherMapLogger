# Settings file for OpenWeatherMapLogger
import os

# Open Weather Base URL
wx_base = 'https://api.openweathermap.org/data/2.5/'
#Open Weather token
ow_app_token = os.environ.get('OW_APP_TOKEN')

# Comma separated string containing StationIDs, Latitudes, Longitides
# Example "OW_STATION1_US,40.32,-95.96,OW_STATION2_US,42.3171215,-88.4975607"
stat_list = os.environ.get('STATION_LIST')

# Convert stat_list into list of tuples
sl = stat_list.split(',')
wx_stations = []
for i in range(0, len(sl), 3):
    wx_stations.append((sl[i], sl[i+1], sl[i+2]))

#Endpoint for posting weather data
endp_base = os.environ.get('IOT_ENDP_BASE_URL')

endp_data_add = 'weatherdata/add/'
endp_current_data = 'weatherdata/current/'
endp_station_list = 'weatherstation/list/'
endp_station_add = 'weatherstation/add/'

# Iot Authentication token
api_token = os.environ.get('IOT_ENDP_TOKEN')



