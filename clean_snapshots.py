#! /usr/bin/env python
# (c) 2015 br3d
# -*- coding: utf-8 -*-
'''
execute: python clean_snapshots.py 30 Name=ci2.gui-system Period=daily -p

first param - day number
params in between - tags "Tag_name=Tag_value"
last param - "-p" print found snapshots   OR  "-delete" delete found snapshots 

key file format AKIAIXXXXXXXXXXXXXXX:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

'''

import boto.ec2
import sys
from dateutil import parser
from datetime import timedelta, datetime

#
# CONFIGURE:
#

keypath = "keys.secret"   # test account
snap_own = "2***********" #test account

aws_region = "eu-west-1"
#eu-west-1 Ireland
#ap-southeast-2 Sydney
#us-east-1 N. Virginia
#eu-central-1 Frankfurt

snapl=[]

def get_key(file_name):
	for line in file(file_name):
		res = line.split(':')
	return res

def get_all_instances(self):
	res=[]
	for i_id in self.get_only_instances():
		res.append(i_id.id)
	return res

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def search_by_tags(snaps ,tag_key, tag_value):
	for snap in snaps:
		if tag_key in snap.tags:
			if snap.tags[tag_key] == tag_value:
				print snap.id," ", parser.parse(snap.start_time).date()," ",snap.tags[tag_key]

def search_by_date(snaps, day_num):        #gives snapshots older day_num days
	limit = datetime.now() - timedelta(days=day_num)
	for snap in snaps:
		if parser.parse(snap.start_time).date() <= limit.date():
			snapl.append(snap)
	return snapl

def search_by_date_tags(snaps, day_num, dic_tags):
	lifetime = datetime.now() - timedelta(days=day_num)
	for snap in snaps:
		flag = True
		if parser.parse(snap.start_time).date() <= lifetime.date():
			for dic_tag in dic_tags:
				if not check_tag(snap, dic_tag, dic_tags[dic_tag]):
					flag = False
			if flag:
				snapl.append(snap)
	return 0 if snapl==[] else snapl

def search_by_date_descr(snaps, day_num, discr):
	limit = datetime.now() - timedelta(days=day_num)
	for snap in snaps:
		if (parser.parse(snap.start_time).date() <= limit.date()) and (snap.description == discr):
			snapl.append(snap)
	return snapl


def show_snaps(snaps):
	for snap in snaps:
		line = ''
		for tag in snap.tags:
			line += tag+" = "+snap.tags[tag]+" | "
		print snap.id," |", parser.parse(snap.start_time).date()," |",snap.description," |", "snapshot not have tags!" if snap.tags =={} else line

def del_snap(snapl):
	conn = boto.ec2.connect_to_region(aws_region, aws_access_key_id = get_key(keypath)[0], aws_secret_access_key = get_key(keypath)[1] )
	lifetime = datetime.now() - timedelta(5)
	for snap in snapl:
		if parser.parse(snap.start_time).date() <= lifetime.date(): # foolproof
			line = ''
			for tag in snap.tags:
				line += tag+" = "+snap.tags[tag]+" | "
			print "delete- |",snap.id," |", parser.parse(snap.start_time).date()," |",snap.description," |", "snapshot not have tags!" if snap.tags =={} else line
			conn.delete_snapshot(snap.id)

def get_argv_tags():
	tags={}
	for argv in sys.argv:
		if "=" in argv:
			argv = argv.split("=")
			tags[argv[0]] = argv[1]
	return tags

def main():
	conn = boto.ec2.connect_to_region(aws_region, aws_access_key_id = get_key(keypath)[0], aws_secret_access_key = get_key(keypath)[1] )
	snaps = conn.get_all_snapshots(owner=snap_own)
	if (sys.argv[len(sys.argv)-1] != "-p") and (sys.argv[len(sys.argv)-1] != "-delete"):
		print "\t ERROR: Use key -p for print snapshots or -delete for delete snapshots"
	elif len(sys.argv) < 3:
		print "Enter argument"
	elif len(sys.argv) == 3:
		if is_int(sys.argv[1]):
			search_by_date(snaps,int(sys.argv[1]))
	elif (len(sys.argv) > 3):
		search_by_date_tags(snaps,int(sys.argv[1]), get_argv_tags())
	else: 
		print "Enter correct argv"

def check_tag(snap, tag_name, tag_value):
	if tag_name in snap.tags and snap.tags[tag_name] == tag_value:
		return True
	else:
		return False

def __init__(): 
	main()
	if sys.argv[len(sys.argv)-1] == "-p":
		show_snaps(snapl)

	if sys.argv[len(sys.argv)-1] == "-delete":
		del_snap(snapl)

__init__()
