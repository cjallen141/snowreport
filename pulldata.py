
import urllib2, datetime, re, json, os, time
from pytz import timezone 
import pytz
from datetime import datetime, timedelta
from bs4 import BeautifulSoup



resort_gps_coordinates= {\
"Stevens Pass": (47.74,-121.09), \
"Alpental": (47.445, -121.425),\
"Crystal Mountain": (46.934,-121.479),\
"Summit at Snoqualmie": (47.421,-121.419),\
"Mt Baker": (48.862, -121.653)
}

snow_report_summary_urls = { \
"Stevens Pass": "https://www.stevenspass.com/site/mountain/reports/snow-and-weather-report/@@snow-and-weather-report", \
"Crystal Mountain": "https://crystalmountainresort.com/the-mountain/current-conditions",\
"Summit at Snoqualmie": "http://www.summitatsnoqualmie.com/conditions",\
"Alpental": "http://www.summitatsnoqualmie.com/conditions", \
"Mt Baker": "http://www.mtbaker.us/snow-report"}


class Report(object):
	def update(self):
		pass

class ResortReport(Report):
	def __init__(self, url):
		self.page_html = ""
		self.page_report = ""
		self.url = url
		self.snow_totals = {'overnight':0, '24hr':0, '48hr':0}

		self.html_valid = False 
		self.snow_totals_valid = False
		self.page_report_valid = False

	def _update_page_html(self):
		path = self.url
		headers= {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
		req = urllib2.Request(path,None,headers)

		try: 
	   		response = urllib2.urlopen(req)
	   		#print response.read()
		except urllib2.HTTPError, e:
			print 'HTTPError = ' + str(e.code)
		except urllib2.URLError, e:
			print 'URLError = ' + str(e.reason)
		except Exception:
			import traceback
			print 'generic exception: ' + traceback.format_exc()

		self.page_html = response.read()
		print "\tsuccess!"
		self.html_valid = True

	def update(self):
		if not self.html_valid:
			print "requesting: %s" % (str(self.url))
			self._update_page_html()
			self._scrape_html_for_report()
			self._scrape_html_for_snow_totals()
		#delete this later.......
		#-------------------------
		return self.page_report

	def data_timeout(self):
		#simple function to use later when scheduling. 
		self.html_valid = False
		self.snow_totals_valid = False
		self.page_report_valid = False

		##

	def _scrape_html_for_report(self):
		#define this method in child classes to implement the logic to scrape the website and return only the wanted paragraph text
		pass 
	def _scrape_html_for_snow_totals():
		#define in child implementations to scrape HTML and populate the snow totals
		print "child did not implement update..."
		pass

class StevensReport(ResortReport):
	def __init__(self,url):
		super(StevensReport,self).__init__(url)

	def _scrape_html_for_report(self):
		soup = BeautifulSoup(self.page_html, "html.parser")
		page_report_soup = soup.find(id="page-report")
		idx = 0 
		for div in page_report_soup.find_all("div"):
			if idx == 1 or idx==2:
				self.page_report = self.page_report + div.get_text(r"</br></br>", strip=True) + r"</br></br>"
			idx +=1
		print self.page_report
		self.page_report_valid = True


	def _scrape_html_for_snow_totals(self):
		soup = BeautifulSoup(self.page_html,"html.parser")
		totals = []
		for div in soup.find_all('div', attrs={'class':'page-report-snowfall-value'}):
			totals.append(int(div.get_text()[:-1])) #convert to integer and remove the inches unit from end

		self.snow_totals['overnight'] = totals[0]
		self.snow_totals['24hr'] = totals[1]
		self.snow_totals['48hr'] = totals[2]
		print "Snow Totals:"
		print self.snow_totals
		self.snow_totals_valid = True

class CrystalMountainReport(ResortReport):
	def __init__(self,url):
		super(CrystalMountainReport,self).__init__(url)

	def _scrape_html_for_report(self):
		soup = BeautifulSoup(self.page_html, "html.parser")
		page_report_soup = soup.find('div', attrs={'class': 'entry-content'})	
		p = [p for p in page_report_soup.find_all('p')][1]
		self.page_report = p.get_text()
		print self.page_report
		self.page_report_valid = True

	def _scrape_html_for_snow_totals(self):
		soup = BeautifulSoup(self.page_html,"html.parser")
		table_soup = soup.find('div', attrs={'class':'col grid_9_of_12 st-tables'}).find('tr', attrs={'class':'row-1'})

		self.snow_totals['overnight']= int(table_soup.find('span',attrs={'id':'overnight'}).get_text()[:-1])
		self.snow_totals['24hr']= int(table_soup.find('span',attrs={'id':'hours-24'}).get_text()[:-1])
		self.snow_totals['48hr']= int(table_soup.find('span',attrs={'id':'hours-48'}).get_text()[:-1])
		print "Snow Totals:"
		print self.snow_totals
		self.snow_totals_valid = True

class SummitAtSnoqualmieReport(ResortReport):
	def __init__(self,url):
		super(SummitAtSnoqualmieReport,self).__init__(url)
	def _scrape_html_for_report(self):
		soup = BeautifulSoup(self.page_html, "html.parser")
		content = soup.find('div', attrs={'id': 'block-conditions-snow-comments'}).find('div', attrs={'class': 'content'}).find('p').find('p')
		self.page_report = content
		print self.page_report
		self.page_report_valid = True

	def _scrape_html_for_snow_totals(self):
		soup = BeautifulSoup(self.page_html, "html.parser")
		soup = soup.find('div',attrs={'id':'block-weather-area-overview'}).find('div', attrs={'class':'snowfall'})

		vals = soup.find_all('span',attrs={'class':'value'})
		self.snow_totals['overnight'] = int(vals[1].get_text())
		self.snow_totals['24hr'] = int(vals[2].get_text())
		self.snow_totals['48hr'] = int(vals[3].get_text())
		self.snow_totals_valid = True
		
		print "Snow Totals:"
		print self.snow_totals

class AlpentalReport(ResortReport):
	def __init__(self,url):
		super(AlpentalReport,self).__init__(url)
	def _scrape_html_for_report(self):
		soup = BeautifulSoup(self.page_html, "html.parser")
		content = soup.find('div', attrs={'id': 'block-conditions-snow-comments'}).find('div', attrs={'class': 'content'}).find('p').find('p')
		self.page_report = content
		print self.page_report
		self.page_report_valid = True

	def _scrape_html_for_snow_totals(self):
		soup = BeautifulSoup(self.page_html, "html.parser")
		snow_lists = soup.find('div',attrs={'id':'block-weather-area-overview'}).find_all('div', attrs={'class':'snowfall'})
		soup= snow_lists[1]
		vals = soup.find_all('span',attrs={'class':'value'})
		self.snow_totals['overnight'] = int(vals[1].get_text())
		self.snow_totals['24hr'] = int(vals[2].get_text())
		self.snow_totals['48hr'] = int(vals[3].get_text())
		self.snow_totals_valid = True
		
		print "Snow Totals:"
		print self.snow_totals


class CameraImageManager(Report):

	def __init__(self,set_name,cam_list):
		#cam list should be list of camera dictionaries
		# {'url': <the cam location, 'name': <nametosavecamas>}
		self.name = set_name
		self.cam_list = cam_list
		self.storage_path = ""
		self.cam_images_valid = False
	def get_latest_cameras(self):

		headers= {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}

		if not self.cam_images_valid:
			print "downloading %s cameras.." % self.name
			for cam in self.cam_list:
				print "\t"+str(cam['name'])
				path = cam['url']
				req = urllib2.Request(path,None,headers)
				try: 
			   		response = urllib2.urlopen(req)
				except urllib2.HTTPError, e:
					print 'HTTPError = ' + str(e.code)
				except urllib2.URLError, e:
					print 'URLError = ' + str(e.reason)
				except Exception:
					import traceback
					print 'generic exception: ' + traceback.format_exc()
				self._save_cam_pic(response.read(),cam['name'])
			self.cam_images_valid = True
			print "success!"
	def _save_cam_pic(self,img,name):
		path = os.getcwd() + "\\" + self.name
		self.storage_path = path
		if not os.path.exists(path):
			os.makedirs(path)

		f_path = path + "\\" +str(name) + ".jpg"
		with open(f_path,'wb')as localFile:
			localFile.write(img)

	# def get_latest_camera_pic(cam_list):

	# path = os.getcwd()
	# #print path
	# for cam in cam_list:
	# 	#print cam
	# 	f_path = path + "\\" + str(cam["CameraID"]) + ".jpg"
	# 	print "downloading camera: " + cam["ImageURL"]
	# 	img = urllib2.urlopen(cam["ImageURL"])

	# 	with open(f_path, 'wb') as localFile:
	# 		localFile.write(img.read())
	# return


class DarkSkyForecast(Report):
	def __init__(self,name,coordinates):
		#! add error checking to inputs

		self.darksky_key = "5430b5325e121250ecb4f797c346d68d"
		self.latitude = coordinates[0]
		self.longitude = coordinates[1]
		self.path = "https://api.darksky.net/forecast/%s/%s,%s" % (self.darksky_key,str(self.latitude),str(self.longitude))
		self.name = name
		self.forecast_valid = False
		self.forecast_json_valid = False

	def update(self):
		if not self.forecast_json_valid and not self.forecast_valid:
			print "connecting to... " + self.path
			headers = {'User-Agent': 'WA-Snow-Report', 'Accept': 'application/ld+json'}
			req = urllib2.Request(self.path,None,headers)
			try: 
				response = urllib2.urlopen(req)
			except urllib2.HTTPError, e:
				print 'HTTPError = ' + str(e.code)
			except urllib2.URLError, e:
				print 'URLError = ' + str(e.reason)
			except Exception:
				import traceback
				print 'generic exception: ' + traceback.format_exc()

			jsonData = json.load(response) ##needs error checking on correctness of data
			self.forecast_json = jsonData
			self.forecast_json_valid = True 
			print "success!"
	def print_json(self):
		print json.dumps(self.forecast_json, indent=4,sort_keys=True)


class WaTravelerAPI(Report):
	def __init__(self,name,coordinates,req_type):
		pass_names = ['Stevens Pass US2','Snoqualmie Pass I-90','Crystal to Greenwater SR410']

		if name in pass_names:
			self.name = name
		else:
			print "you didn't provide a correct name"
			raise SystemExit(1)

		self.latitude = coordinates[0]
		self.longitude = coordinates[1]

		self.urls = {\
		"HighwayCams" : "http://wsdot.com/Traffic/api/HighwayCameras/HighwayCamerasREST.svc/GetCamerasAsJson", \
		"AllMountainPassConditions": "http://wsdot.com/Traffic/api/MountainPassConditions/MountainPassConditionsREST.svc/GetMountainPassConditionsAsJson"}

		self.mountain_pass_conditions_valid = False
		self.type= req_type
		self.access_code = "2e243012-d8a0-4aaa-9082-60352049c211"

	def _update_json(self,path):
		path = path 
		headers= {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
		req = urllib2.Request(path,None,headers)

		try: 
	   		response = urllib2.urlopen(req)
	   		#print response.read()
		except urllib2.HTTPError, e:
			print 'HTTPError = ' + str(e.code)
		except urllib2.URLError, e:
			print 'URLError = ' + str(e.reason)
		except Exception:
			import traceback
			print 'generic exception: ' + traceback.format_exc()

		return json.load(response)

	def update(self):
		#update mountain_pass_conditions
		if not self.mountain_pass_conditions_valid:
			path = self.urls[self.type] + "?AccessCode=" + self.access_code
			j = self._update_json(path)
			for item in j:
				if item["MountainPassName"] == self.name:
					self.mountain_pass_conditions = item
			self.mountain_pass_conditions_valid = True
			print self.name + " Pass road conditions updated..."


class NOAAForecast(Report):
	def __init__(self,name,coordinates):
		self.latitude = coordinates[0]
		self.longitude = coordinates[1]
		self.name = name

		self.point_forecast_valid = False

	def _update_json(self,in_path):
		path = in_path 

		print "connecting to... " + path
		headers= {'User-Agent': 'snow-report', 'Accept': 'application/ld+json',}
		req = urllib2.Request(path,None,headers)
		try: 
   			response = urllib2.urlopen(req)
   			#print response.read()
		except urllib2.HTTPError, e:
			print 'HTTPError = ' + str(e.code)
		except urllib2.URLError, e:
			print 'URLError = ' + str(e.reason)
		except Exception:
			import traceback
			print 'generic exception: ' + traceback.format_exc()
		return json.load(response)

	def update(self):
		if not self.point_forecast_valid: 
			self.point_forecast = self._update_json("https://api-v1.weather.gov/points/%s,%s/forecast" % (str(self.latitude),str(self.longitude)))
			self.point_forecast_valid = True
			print "successfully updated point forecast."

	def get_current_detail(self):
		#
		return self.point_forecast['periods'][0]['detailedForecast']


# utilites and old functions: 
def get_traveler_info_json(type):

	url = urls[type] + "?AccessCode=" + access_code

	f = urllib2.urlopen(url)
	jsonData = json.load(f)
	return jsonData

def get_stevens_summit_forecast_data_update():

	#http request current weather.gov forecast data and create soup object
	url = "http://forecast.weather.gov/MapClick.php?lat=47.75&lon=-121.09#.WFxdDlwWzif"
	f = urllib2.urlopen(url)
	soup = BeautifulSoup(f.read(), "html.parser")

	print soup.prettify()

	#search for the "detailed forecast", which contains the updated forecast text 
	forecast_section = soup.find(id="detailed-forecast")

	#create list of tuple forcast [('day', 'forecast') ... ]
	forecast_headers=[]
	for forecast in forecast_section.find_all(attrs={'class': "col-sm-2 forecast-label"}):
		forecast_headers.append(str(forecast.string))

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

	#for item in forecast:
	#	print item
	return forecast

def get_weather_forecast(coordinates):
	latitude = coordinates[0]
	longitude = coordinates[1]
	#path = "https://api.weather.gov/points/%s,%s/forecast" % (str(lat), str(long))
	path = "https://api-v1.weather.gov/points/%s,%s/forecast" % (str(latitude),str(longitude))
	print path
	
	headers= {'User-Agent': 'snow-report', 'Accept': 'application/ld+json',}
	req = urllib2.Request(path,None,headers)

	try: 
   		response = urllib2.urlopen(req)
   		#print response.read()
	except urllib2.HTTPError, e:
		print 'HTTPError = ' + str(e.code)
	except urllib2.URLError, e:
		print 'URLError = ' + str(e.reason)
	except Exception:
		import traceback
		print 'generic exception: ' + traceback.format_exc()

	jsonData = json.load(response)

	#print jsonData["updated"]
	updated_time = jsonData["updated"]
	print json.dumps(jsonData, indent=4, sort_keys=True)

def test_weather_gov_api(path):
	path = "http://api.weather.gov/points/%s,%s/forecast" % (str(lat), str(long))
	
	print path
	
	headers= {'User-Agent': 'snow-report', 'Accept': 'application/ld+json',}
	#headers= {'User-Agent': 'snow-report', 'Accept': 'application/vnd.noaa.dwml+xml;version=1',}
	req = urllib2.Request(path,None,headers)

	try: 
   		response = urllib2.urlopen(req)
   		#print response.read()
	except urllib2.HTTPError, e:
		print 'HTTPError = ' + str(e.code)
	except urllib2.URLError, e:
		print 'URLError = ' + str(e.reason)
	except Exception:
		import traceback
		print 'generic exception: ' + traceback.format_exc()

	jsonData = json.load(response)

	#print response.read()
	print json.dumps(jsonData, indent=4, sort_keys=True)
	
def unix_to_datetime(unix_time,timezone_str):
	utc_dt = pytz.timezone('UTC').localize(datetime.utcfromtimestamp(unix_time))
	return utc_dt.astimezone(pytz.timezone(timezone_str))

if __name__ == '__main__':

# 1. testing Traffic Camera Manager 
	stevens_traffic_cameras = [\
	{'name': 'W-Stevens-Pass',  'url': 'http://images.wsdot.wa.gov/us2/oldfaithful/oldfaithful.jpg'},\
	{'name': 'Big-Windy',       'url': 'http://images.wsdot.wa.gov/us2/bigwindy/us2bigwindy.jpg'},\
	{'name': 'W-Stevens-Summit','url': 'http://images.wsdot.wa.gov/us2/stvldg/sumtwest.jpg'},\
	{'name': 'E-Stevens-Summit','url': 'http://images.wsdot.wa.gov/us2/stevens/sumteast.jpg'},\
	{'name': 'Lower-Mill-Creek','url': 'http://images.wsdot.wa.gov/US2/LowerMillCrk/LowerMillCrk.jpg'},\
	{'name': 'Coles-Corner-E',  'url': 'http://images.wsdot.wa.gov/US2/ColesCorner/US2West/US2West.jpg'},\
	{'name': 'Coles-Corner-W',  'url': 'http://images.wsdot.wa.gov/US2/ColesCorner/US2East/US2East.jpg'},\
	{'name': 'E-SR207',         'url': 'http://images.wsdot.wa.gov/us2/winton/winton.jpg'} ]

	summit_alpental_traffic_cameras = [\
	{'name': 'Denny-Creek',   'url': 'http://images.wsdot.wa.gov/sc/090VC04680.jpg'},\
	{'name': 'Asahel-Curtis', 'url': 'http://images.wsdot.wa.gov/sc/090VC04810.jpg'},\
	{'name': 'Franklin-Falls','url': 'http://images.wsdot.wa.gov/sc/090VC05130.jpg'},\
	{'name': 'Summit-West',   'url': 'http://images.wsdot.wa.gov/sc/090VC05200.jpg'},\
	{'name': 'Summit-East',   'url': 'http://images.wsdot.wa.gov/sc/090VC05347.jpg'},\
	{'name': 'Hyak',          'url': 'http://images.wsdot.wa.gov/sc/090VC05517.jpg'},\
	{'name': 'Keechelus-SnowShed','url': 'http://images.wsdot.wa.gov/sc/090VC05771.jpg'},\
	{'name': 'Easton-Hill',   'url': 'http://images.wsdot.wa.gov/sc/090VC06740.jpg'} ]

	traffic_cams = []

	stevens_traffic_cam_mgr = CameraImageManager("Stevens_Pass_Traffic_Cams",stevens_traffic_cameras)
	traffic_cams.append(stevens_traffic_cam_mgr)
	summit_alpental_t_mgr = CameraImageManager("Summit_Alpental_Traffic_Cams",summit_alpental_traffic_cameras)
	traffic_cams.append(summit_alpental_t_mgr)


	stevens_resort_cameras = [\
	{'name': 'base1',   'url': 'https://www.stevenspass.com/cams/base1'},\
	{'name': 'jupiter', 'url': 'https://www.stevenspass.com/cams/jupiter'},\
	{'name': 'cowboy',  'url': 'https://www.stevenspass.com/cams/cowboy'},\
	{'name': 'mountain','url': 'https://www.stevenspass.com/cams/mountain'}]

	crystal_mountain_resort_cameras = [\
	{'name': 'CRYMB1','url': 'http://wwc.instacam.com/instacamimg/CRYMB/CRYMB_l.jpg'},\
	{'name': 'CRYM4', 'url': 'http://wwc.instacam.com/instacamimg/CRYM4/CRYM4_l.jpg'},\
	{'name': 'CRYM2', 'url': 'http://wwc.instacam.com/instacamimg/CRYM2/CRYM2_l.jpg'},\
	{'name': 'CRYM5', 'url': 'http://instacam.weatherbug.com/instacamimg/CRYM5/CRYM5_l.jpg'},\
	{'name': 'CRYM3', 'url': 'http://instacam.weatherbug.com/instacamimg/CRYM3/CRYM3_l.jpg'},\
	{'name': 'CRYM6', 'url': 'http://instacam.weatherbug.com/instacamimg/CRYM6/CRYM6_l.jpg'}]


	snoqualmie_resort_cameras = [\
	{'name': 'centcam',   'url': 'http://www.summitatsnoqualmie.com/webcams/Centcam.jpg'},\
	{'name': 'silverfir', 'url': 'http://www.summitatsnoqualmie.com/webcams/silverfir.jpg'}]

	alpental_resort_cameras = [\
	{'name': 'Alpcam',     'url': 'http://www.summitatsnoqualmie.com/webcams/Alpcam.jpg'},\
	{'name': 'Alpentalmid','url': 'http://www.summitatsnoqualmie.com/webcams/Alpentalmid.jpg'},\
	{'name': 'Chair2',     'url': 'http://www.summitatsnoqualmie.com/webcams/Chair2.jpg'}]
	
	resort_cameras= []
	resort_cameras.append(CameraImageManager("Stevens-Resort-Cameras",stevens_resort_cameras))
	resort_cameras.append(CameraImageManager("Crystal-Mtn-Cameras",crystal_mountain_resort_cameras))
	resort_cameras.append(CameraImageManager("Snoqualmie-Cameras",snoqualmie_resort_cameras))
	resort_cameras.append(CameraImageManager("Alpental-Cameras",alpental_resort_cameras))

	for mgr in traffic_cams:
		mgr.get_latest_cameras()
		time.sleep(.3)

	for mgr in resort_cameras:
		mgr.get_latest_cameras()
		time.sleep(.3)

# 2. testing the ResortReport class functionality
	reports = []
	
	reports.append(StevensReport(snow_report_summary_urls["Stevens Pass"]))
	##report.get_report_update()
	reports.append(CrystalMountainReport(snow_report_summary_urls["Crystal Mountain"]))
	##report.get_report_update()
	reports.append(SummitAtSnoqualmieReport(snow_report_summary_urls["Summit at Snoqualmie"]))
	##report.get_report_update()
	reports.append(AlpentalReport(snow_report_summary_urls["Alpental"]))

	for report in reports:
		report.update()
		time.sleep(.3)

  ################################

# 3. Testing DarkSkyForecast class for each location
	dks_forecasts = []
	stevens_dks_forecast = DarkSkyForecast("Stevens Pass",resort_gps_coordinates["Stevens Pass"])
	dks_forecasts.append(stevens_dks_forecast)

	alpental_dks_forecast= DarkSkyForecast("Alpental",resort_gps_coordinates["Alpental"])
	dks_forecasts.append(alpental_dks_forecast)

	dks_forecasts.append(DarkSkyForecast("Summit at Snoqualmie", resort_gps_coordinates["Summit at Snoqualmie"]))
	dks_forecasts.append(DarkSkyForecast("Crystal Mountain", resort_gps_coordinates["Crystal Mountain"]))

	for forecast in dks_forecasts:
		forecast.update()
		time.sleep(.3)
		print "(DkSky) %s summary: %s \n" % (forecast.name, forecast.forecast_json['currently']['summary'])

# 4. Test NoaaForecast class 

	noaa_forecasts = []
	noaa_forecasts.append(NOAAForecast("Stevens Pass", resort_gps_coordinates["Stevens Pass"]))
	noaa_forecasts.append(NOAAForecast("Summit at Snoqualmie", resort_gps_coordinates["Summit at Snoqualmie"]))
	noaa_forecasts.append(NOAAForecast("Crystal Mountain", resort_gps_coordinates["Crystal Mountain"]))
	noaa_forecasts.append(NOAAForecast("Alpental", resort_gps_coordinates["Alpental"]))
	for forecast in noaa_forecasts:
		forecast.update()
		time.sleep(.3)
		print "(NOAA Forecast) %s:: Now: %s \n" %(forecast.name,forecast.get_current_detail())

# 5. Test WATravlerAPI class 
	wadot_travelers = []
	
	wadot_travelers.append(WaTravelerAPI("Stevens Pass US2", resort_gps_coordinates["Stevens Pass"],"AllMountainPassConditions"))
	wadot_travelers.append(WaTravelerAPI("Snoqualmie Pass I-90", resort_gps_coordinates["Summit at Snoqualmie"], "AllMountainPassConditions"))
	wadot_travelers.append(WaTravelerAPI("Snoqualmie Pass I-90", resort_gps_coordinates["Alpental"], "AllMountainPassConditions"))
	wadot_travelers.append(WaTravelerAPI("Crystal to Greenwater SR410", resort_gps_coordinates["Crystal Mountain"], "AllMountainPassConditions"))

	for t in wadot_travelers:
		t.update()
		time.sleep(.3)
		print "Name: " + t.name
		print " (%s) Restrictions: %s" % ( t.mountain_pass_conditions["RestrictionOne"]["TravelDirection"], t.mountain_pass_conditions["RestrictionOne"]["RestrictionText"])
		print " (%s) Restrictions: %s" % ( t.mountain_pass_conditions["RestrictionTwo"]["TravelDirection"], t.mountain_pass_conditions["RestrictionTwo"]["RestrictionText"])
		print " Road Conditions: %s\n" %    t.mountain_pass_conditions["RoadCondition"]
		 
	#### 'Mt. Baker Hwy SR542'  <--- saving string for when adding in Mt. Baker
#


#	old stuff
	#data = get_traveler_info_json("HighwayCams")
	
	#print data
	#get_latest_camera_pic(data)
	##################################################################

	#  get stevens pass summit forecast data ... this is old way to scrape the forecast data

	#forecast_stevens_summit_t = get_stevens_summit_forecast_data_update()

	#Steven's pass location is 47.75, -121.09
	#data = get_weather_forecast(47.75, -121.09)

	########test weather.gov api #########
	##latitude = 47.74 
	##longitude = -121.09
	##path = "https://api-v1.weather.gov/points/%s,%s/forecast" % (str(latitude),str(longitude))
	##station = "TSTEV"
	#path ="http://api-v1.weather.gov/zones/forecast/WAZ568"
	#test_weather_gov_api(path)
	######################################


	#######################

	#### other stuff ##########
	unix_time = 1483335294
	timezone_text ="America/Los_Angeles"

	#print unix_to_datetime(unix_time,timezone_text).strftime("%Y-%m-%d %H:%M:%S")
	#print str(u"Snow (1\u20132 in.) throughout the day".encode('utf8'))