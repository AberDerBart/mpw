#!/usr/bin/python
import mpd
import json
import argparse
import sys
import os
import parse
from tabulate import tabulate

c=mpd.MPDClient()

def connect(host="localhost",port=6600):
	try:
		c.connect(host,port)

		c.subscribe("scheduled")
		
		if(not "scheduler" in c.channels()):
			print("MpdScheduler not found.",file=sys.stderr)
			return False

		return True
	except Exception as e:
		print(str(e),file=sys.stderr)
		return False
	return False

def timeValid(timeString):
	try:
		return None != (parse.parse("+{offset:d}", timeString) or parse.parse("{time:tt}", timeString))
	except:
		return False

def getTasks():
	tasks=None
	c.sendmessage("scheduler","list_json")
	c.idle("message")
	for m in c.readmessages():
		if(m["channel"]=="scheduled"):
			tasks=json.loads(m["message"])
	if "data" in tasks:
		return tasks["data"]
	else:
		return None

def addAlarm(args,parser):
	if(not timeValid(args.time)):
		parser.error("Invalid time format.")
		exit(-1)
	c.sendmessage("scheduler","alarm "+args.time)
	listTasks(args,parser)

def addSleep(args,parser):
	if(not timeValid(args.time)):
		parser.error("Invalid time format.")
		exit(-1)
	c.sendmessage("scheduler","alarm "+args.time)
	listTasks(args,parser)

def cancel(args,parser):
	tasks=getTasks()
	if(int(args.index) < len(tasks)):
		c.sendmessage("scheduler","cancel "+str(args.index))
		newTasks=getTasks()
		if(len(newTasks) >= len(tasks)):
			print("Error canceling task #"+str(args.index),file=sys.stderr)
			exit(-1)
		listTasks(args,parser)
	else:
		parser.error("Index out of bounds")

def listTasks(args,parser):
	tasks=getTasks()
	if(tasks):
		print(tabulate(tasks,headers="keys"))

callDict={
	"cancel":cancel,
	"sleep" :addSleep,
	"alarm" :addAlarm,
	"list"  :listTasks,
	None    :listTasks
}

def main():
	fallbackHost=os.environ.get("MPD_HOST") or "localhost"

	parser=argparse.ArgumentParser()
	subParsers=parser.add_subparsers(dest="command")
	subParsers.required=False

	alarmParser=subParsers.add_parser("alarm",help="sets an alarm")
	alarmParser.add_argument("time",help="time specified in the format +MIN or HH:MM")

	sleepParser=subParsers.add_parser("sleep",help="sets a sleep timer")
	sleepParser.add_argument("time",help="time specified in the format +MIN or HH:MM")

	listParser=subParsers.add_parser("list",help="lists the scheduled tasks")

	cancelParser=subParsers.add_parser("cancel",help="cancels the specified tasks")
	cancelParser.add_argument("index", help="index of the task to be canceled",type=int)

	parser.add_argument("--host", help="mpd host to connect to",default=fallbackHost)
	parser.add_argument("--port", help="port to connect on",default=6600,type=int)

	args=parser.parse_args()


	if(not connect(args.host,args.port)):
		exit(-1)

	callDict[args.command](args,parser)
	


if __name__ == '__main__':
	main()
