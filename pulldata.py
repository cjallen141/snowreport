
import urllib2, datetime, re, json, os
from bs4 import BeautifulSoup



access_code = "2e243012-d8a0-4aaa-9082-60352049c211"

urls = { "HighwayCams" : "http://wsdot.com/Traffic/api/HighwayCameras/HighwayCamerasREST.svc/GetCamerasAsJson"}

stevens_west_cams = {"W Stevens Pass" : 9145,
		"Big Windy": 9437,
		"W Stevens Summit": 8063,
		"E Stevens Summit": 8062}


def get_traveler_info_json(type):
	url = urls[type] + "?AccessCode=" + access_code

	f = urllib2.urlopen(url)
	jsonData = json.load(f)
	del f

	d =[]
	for item in jsonData:
		for id in stevens_west_cams.values(): 
			if item["CameraID"] == id:
				d.append(item)

	#print d 
	return d

def get_latest_camera_pic(cam_list):

	path = os.getcwd()
	#print path
	for cam in cam_list:
		#print cam
		f_path = path + "\\" + str(cam["CameraID"]) + ".jpg"
		print "downloading camera: " + cam["ImageURL"]
		img = urllib2.urlopen(cam["ImageURL"])

		with open(f_path, 'wb') as localFile:
			localFile.write(img.read())
	return

def get_stevens_forecast_data_update():

	#http request current weather.gov forecast data and create soup object
	url = "http://forecast.weather.gov/MapClick.php?lat=47.75&lon=-121.09#.WFxdDlwWzif"
	f = urllib2.urlopen(url)
	soup = BeautifulSoup(f.read(), "html.parser")


	#search for the "detailed forecast", which contains the updated forecast text 
	forecast_section = soup.find(id="detailed-forecast")
	#print forecast_section.prettify()
	#print '\n'


	#create list of tuple forcast [('day', 'forecast') ... ]

	#get forecast headers
	forecast_headers=[]
	for forecast in forecast_section.find_all(attrs={'class': "col-sm-2 forecast-label"}):
		forecast_headers.append(str(forecast.string))

	#get forecast content
	forecast_text = [] 
	for forecast in forecast_section.find_all(attrs={'class': "col-sm-10 forecast-text"}):
		forecast_text.append(str(forecast.string))
	#print forecast_section.prettify()

	#combine into list of tuples
	forecast = []
	idx =0
	for header in forecast_headers:
		forecast.append( (header,forecast_text[idx]))
		idx+= 1

	for item in forecast:
		print item
	return

if __name__ == '__main__':
	
	data = get_traveler_info_json("HighwayCams")

	#get_latest_camera_pic(data)

	get_stevens_forecast_data_update()