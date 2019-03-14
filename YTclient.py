import os, bisect, curses, threading, subprocess, re
from ast import literal_eval
from datetime import datetime
import google.oauth2.credentials

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_SECRETS_FILE = "/run/media/k/SBP/home/k/Projects/YTclient/client_secret_477034682950-ma45nt994mr7258a7jilfd0jgpn90nm3.apps.googleusercontent.com.json"
SCOPES = ['https://www.googleapis.com/auth/youtube']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

class AuthService :
	maxResultsSubs = 50
	maxResultsActivities = 50

	subscriptions = []
	activities = []
	videos = []
	activities = []
	comments = []
	metaData = dict()

	def getAuthenticatedService():
		flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
		credentials = flow.run_console()
		return build(API_SERVICE_NAME, API_VERSION, credentials = credentials) 

	def subscriptionsListByChannelID(service, **kwargs):
		results = service.subscriptions().list(**kwargs).execute()
		return results

	def activitiesListByChannelID(service, **kwargs):
		results = service.activities().list(**kwargs).execute()
		return results

	Service = getAuthenticatedService()

	def sortActivitiesByChronologicalOrder(self, videos):

		sortedVideos = []
		sortedFeed = []
		for x in range(len(videos)) :
		 recentIndexY = 0
		 recentIndexZ = 0
		 for y in range(len(videos)) :
		  for z in range(len(videos[y]['items'])):
		   if datetime.strptime(videos[recentIndexY]['items'][recentIndexZ]['snippet']['publishedAt'],
			   '%Y-%m-%dT%H:%M:%S.000Z') < datetime.strptime(videos[y]['items'][z]['snippet']['publishedAt'],'%Y-%m-%dT%H:%M:%S.000Z'):
		    recentIndexY, recentIndexZ = y, z
		 sortedFeed.append(videos[recentIndexY]['items'][recentIndexZ])
		 sortedVideos.append(videos[recentIndexY]['items'][recentIndexZ])
		 videos[recentIndexY]['items'].pop(recentIndexZ) 
		return sortedFeed, sortedVideos

	def listActivitiesInChannels(self,channels) :

		videos = []
		for x in range(len(channels)) :
		 for y in range(len(channels[x]['items'])) :
		  videos.append(self.Service.search().list(part='snippet',
		   channelId=channels[x]['items'][y]['snippet']['resourceId']['channelId'],
		   order='date',
		   safeSearch='none',
		   type='video',
		   maxResults=50).execute())
		  videos.append(self.Service.search().list(part='snippet',
		   channelId=channels[x]['items'][y]['snippet']['resourceId']['channelId'],
		   order='date',
		   safeSearch='none',
		   type='video',
		   eventType='live',
		   maxResults=50).execute())

		return videos

	def listSubscriptionsForUser(self):
		index = 0
		subscriptions = [self.Service.subscriptions().list(part='snippet,id',mine=1,order='alphabetical',maxResults=self.maxResultsSubs).execute()]
		resultsToQuery = subscriptions[0]['pageInfo']['totalResults'] - self.maxResultsSubs
		while True :
		 index += 1
		 if resultsToQuery > 0 :
		  subscriptions.append(self.Service.subscriptions().list(part='snippet,id',
		   mine=1,
		   order='alphabetical',
		   maxResults=self.maxResultsSubs,
		   pageToken=subscriptions[index - 1]['nextPageToken']).execute())
		  resultsToQuery = resultsToQuery - self.maxResultsSubs
		 else:
		  break
 
		return subscriptions

	def getSubPage(self) :
		self.subscriptions = self.listSubscriptionsForUser()
		self.activities = self.listActivitiesInChannels(self.subscriptions)
		self.activities, self.videos = self.sortActivitiesByChronologicalOrder(self.activities)

		return self.activities, self.videos
'''	
	def addObj(self) :

	return 

	def purge(self) :
'''
		
'''
	def getVideoInfo(self) :
		return Description, likeRatio, reccomendedVideos

	def writeComment(self) :
		return True

	def getSearchResults(self) :
		return Videos

	def getLibrary(self) :
		return Playlists
'''

class UI :
	lastDrawnLine = 1
	selectedIndex = 0
	AuthSerivce = AuthService()
	Feed, Videos = AuthSerivce.getSubPage()
	stdscr = curses.initscr()
	def __init__(self) :
		curses.start_color()
		curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
		curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)
		self.stdscr.immedok(True)
		self.stdscr.keypad(0)
		curses.noecho()
		self.stdscr.refresh()

	def update(self) :
		quit = False
		while not quit :
		 self.lastDrawnLine = 1
		 feedWin = curses.newwin(0, 0, 1, 1)
		 feedWin.box()
		 lastDrawnIndex = self.drawFeed(self.Videos, feedWin)
		 feedWin.refresh()
		 self.stdscr.refresh()
		 key = self.stdscr.getkey()
		 if key == 'q':
		  quit = True
		 elif key == 'j' and lastDrawnIndex > self.selectedIndex :
		  self.selectedIndex += 1
		 elif key == 'k' and self.selectedIndex > 0 :
		   self.selectedIndex -= 1
		 elif key == 'm' :
		  p = subprocess.Popen(['/usr/bin/mpv' + ' https://youtube.com/watch/' + self.Videos[self.selectedIndex]['id']['videoId'] + ' --pause'],
		  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		  threading.Thread(target=p.communicate).start()
		 elif key == 'i' :
		  try :
		   p = subprocess.Popen(['/usr/bin/feh ' + self.Videos[self.selectedIndex]['snippet']['thumbnails']['maxres']['url']],
		                        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		  except :
		   try :
		    p = subprocess.Popen(['/usr/bin/feh ' + self.Videos[self.selectedIndex]['snippet']['thumbnails']['standard']['url']],
		                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		   except :
		    try :
		     p = subprocess.Popen(['/usr/bin/feh ' + self.Videos[self.selectedIndex]['snippet']['thumbnails']['high']['url']],
		                       shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		    except : 
		     try :
		      p = subprocess.Popen(['/usr/bin/feh ' + self.Videos[self.selectedIndex]['snippet']['thumbnails']['medium']['url']],
		                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		     except :
		      try :
		       p = subprocess.Popen(['/usr/bin/feh ' + self.Videos[self.selectedIndex]['snippet']['thumbnails']['default']['url']],
		                          shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		      except :
		       pass

		   threading.Thread(target=p.communicate).start()
		 if key == 't' :
		  #open video metadata and comments section
		  pass
		 elif key == 'enter' :
		  #do all actions excluding thumbnails
		  pass
		 elif key == 'r':
		  self.Feed, self.Videos = self.AuthSerivce.getSubPage()

	def drawstr(self, s, Win, mode) :
		dims = Win.getmaxyx()
		tmp = str
		if self.lastDrawnLine >= dims[0] - 2 :
		 return False
		stringToDraw = str
		while len(s) > 1 :
		 if len(s) > dims[1] - 4 :
		  stringToDraw = s[0:dims[1]-7] + '...'
		 else :
		  stringToDraw = s
		 s = ''
		 tmp = ''
		 if mode == 0 :
		  Win.addstr(self.lastDrawnLine, 1, stringToDraw, curses.A_BOLD)
		 if mode == 1 :
		  Win.addstr(self.lastDrawnLine, 1, stringToDraw, curses.A_UNDERLINE | curses.color_pair(1))
		 if mode == 2 :
		  Win.addstr(self.lastDrawnLine, 2, stringToDraw)
		 if mode == 3 :
		  Win.addstr(self.lastDrawnLine, 1, stringToDraw, curses.A_UNDERLINE | curses.color_pair(2))
		 else :
		  pass
		 self.lastDrawnLine += 1
		 s = tmp
		return True
		 
	def drawFeed(self, feed, feedWin) :
		canDraw = True
		index = 0

		while canDraw and len(feed) != index :
#		 if feed[index]['snippet']['type'] == 'upload' :
#		 log = open('log.txt', 'w+')
#		 log.write(repr(feed[index]['snippet']['description']))
#		 log.close()
		 canDraw = self.drawstr(feed[index]['snippet']['channelTitle'], feedWin, 0)
		 if self.selectedIndex == index :
		  canDraw = self.drawstr(feed[index]['snippet']['title'], feedWin, 3)
		 else :
		  canDraw = self.drawstr(feed[index]['snippet']['title'], feedWin, 1)
		 canDraw = self.drawstr(feed[index]['snippet']['description'], feedWin, 2)
		 index += 1
		return index

	def endWin(self) :
	 curses.endwin()
		
if __name__ == '__main__' :
	UI = UI()
	UI.update()
	UI.endWin()
