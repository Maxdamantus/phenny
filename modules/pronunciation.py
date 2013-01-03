#!/usr/bin/env python
# coding=utf-8

import subprocess

def pronounce(phenny, input): 
	stuff = input.groups()[1]
	defaultvoices = ["en-uk", "en-us"]
	voices = []
	while stuff.startswith(':') and (' ' in stuff):
		voice, stuff = stuff.split(' ', 1)
		voices.append(voice[1:])
	if voices == []:
		voices = defaultvoices
	try:
		msg = []
		for v in voices:
			msg.append(v + ": [" + speak(v, stuff) + "]")
		msg = ", ".join(msg)
	except subprocess.CalledProcessError as e:
		msg = "fail: " + e.output
	phenny.say(msg)
pronounce.commands = ['pr']
pronounce.example = '.pr :fi terve'

def prls(phenny, input):
	stuff = (input.groups()[1] or "").strip()
	msg = [v for v in voices() if v.startswith(stuff)]
	phenny.say("prls: " + " ".join(msg))
prls.commands = ['prls']
prls.example = '.prls en'

def speak(voice, stuff):
	return subprocess.check_output(["espeak", "-w", "/dev/null", "--ipa", "-v", voice, stuff], stderr=subprocess.STDOUT).decode("utf-8").strip()

def voices():
	lines = subprocess.check_output(["espeak", "--voices"], stderr=subprocess.STDOUT).decode("utf-8").split("\n")
	lines = [l for l in lines[1:] if " " in l]
	voices = []
	for l in lines:
		words = [s for s in l.split(" ") if s != ""]
		voices.append(words[1])
	return voices
