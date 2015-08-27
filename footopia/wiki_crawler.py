import urllib, json
import os

DEFAULT_IMG_EXTENSION = ".jpg"
DEFAULT_IMG_NAME = "None/no-logo.png"
API_URL ="http://en.wikipedia.org/w/api.php?action=query&titles=Dummy&prop=pageimages&format=json&pithumbsize=100"
team_name = ""
DIRECTORY = "team_logos/"
saveDir = os.path.join(os.path.dirname( __file__ ), '..' ) + "/media/" + DIRECTORY

# This method gets the name of the team from the available team wiki url
def get_team_name(url):
	split = url.split("/")
	global team_name
	team_name = split[4]
	return team_name

# This method cleans the API_URL and provides the appropriate team name from the given team wiki url
def form_url(url):	
	return API_URL.replace("Dummy", get_team_name(url))

# This method loads the image in DEFAULT_IMG_NAME. This image must be copied and stored in the media directory using django
def load_logo(url):
	response = urllib.urlopen(form_url(url))
	data = json.loads(response.read())
	return retrieveImage(processJSON(data))

# This method returns the image url from the JSON object
def processJSON(data):
	# imageUrl = data.
	needed = data['query']['pages']
	for items in needed:
		list = needed[items]
		return list['thumbnail']['source']

def retrieveImage(url):
	try:
		imageName = team_name + DEFAULT_IMG_EXTENSION
		image = urllib.URLopener()
		current_directory = os.getcwd()
		os.chdir(saveDir)
		image.retrieve(url, imageName)
		os.chdir(current_directory)
		return DIRECTORY+imageName
	except:
		return DEFAULT_IMG_NAME

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

# Test call	
# load_logo("http://en.wikipedia.org/wiki/India_national_football_team")