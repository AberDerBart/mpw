#!/usr/bin/python
import mpd
import json
import argparse
import sys
from tabulate import tabulate

c=mpd.MPDClient()

def connect():
	c.connect("localhost",6600)

	c.subscribe("scheduled")
	return True

def getTasks():
	alarms=None
	c.sendmessage("scheduler","list_json")
	c.idle("message")
	for m in c.readmessages():
		if(m["channel"]=="scheduled"):
			alarms=json.loads(m["message"])
	return alarms

def addAlarm(args):
	c.sendmessage("scheduler","alarm "+args.time)

def addSleep(args):
	c.sendmessage("scheduler","alarm "+args.time)

def cancel(args):
	c.sendmessage("scheduler","cancel "+args.index)

def listTasks(args):
	tasks=getTasks()["data"]
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

	if(not connect()):
		exit(-1)

	callDict[args.command](args)
	


if __name__ == '__main__':
	main()
