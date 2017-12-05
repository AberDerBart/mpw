#!/usr/bin/python
import mpd
import json
import argparse
import sys

c=mpd.MPDClient()

def isAvailable():
	return True

def getTasks():
	alarms=None
	c.sendmessage("scheduler","list_json")
	c.idle("message")
	for m in c.readmessages():
		if(m["channel"]=="scheduled"):
			alarms=json.loads(m["message"])
	return alarms

def addAlarm(time):
	c.sendmessage("scheduler","alarm "+time)

def addSleep(time):
	c.sendmessage("scheduler","alarm "+time)

def cancel(index):
	c.sendmessage("scheduler","cancel "+index)

def main():
	parser=argparse.ArgumentParser()
	subParsers=parser.add_subparsers(dest="command")
	subParsers.required=False

	alarmParser=subParsers.add_parser("alarm",help="sets an alarm")
	alarmParser.add_argument("time",help="time specified in the format +MIN or HH:MM")

	sleepParser=subParsers.add_parser("sleep",help="sets a sleep timer")
	sleepParser.add_argument("time",help="time specified in the format +MIN or HH:MM")

	listParser=subParsers.add_parser("list",help="lists the scheduled tasks")

	cancelParser=subParsers.add_parser("cancel",help="cancels the specified tasks")
	cancelParser.add_argument("index", help="index of the task to be canceled")

	args=parser.parse_args()

	c.connect("localhost",6600)

	c.subscribe("scheduled")

	if(not isAvailable()):
		print("MpdScheduler not available.",file=sys.stdout)
		exit(-1)

	if(not args.command or args.command=="list"):
		print("list")
	else:
		pass

if __name__ == '__main__':
	main()
