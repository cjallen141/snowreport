
import urllib2, datetime, re, json, os



access_code = "2e243012-d8a0-4aaa-9082-60352049c211"

urls = { "HighwayCams" : "http://wsdot.com/Traffic/api/HighwayCameras/HighwayCamerasREST.svc/GetCamerasAsJson"}

stevens_west_cams = {"W Stevens Pass" : 9145,
		"Big Windy": 9437,
		"W Stevens Summit": 8063,
		"E Stevens Summit": 8062}


def getTravelerInfoJson(type):
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
	print path
	for cam in cam_list:
		print cam
		f_path = path + "\\" + str(cam["CameraID"]) + ".jpg"
		print f_path
		img = urllib2.urlopen(cam["ImageURL"])

		with open(f_path, 'wb') as localFile:
			localFile.write(img.read())

	return
if __name__ == '__main__':
	
	data = getTravelerInfoJson("HighwayCams")

	get_latest_camera_pic(data)