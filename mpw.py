#!/usr/bin/python

import mpd
import json

c=mpd.MPDClient()

c.connect("faultier",6600)

c.subscribe("scheduled")

alarms=None

def listAlarms():
	alarms=None
	c.sendmessage("scheduler","list_json")
	c.idle("message")
	for m in c.readmessages():
		if(m["channel"]=="scheduled"):
			alarms=json.loads(m["message"])
	return alarms

def addAlarm(h,m):
	c.sendmessage("scheduler","alarm "+str(h)+":"+str(m))
