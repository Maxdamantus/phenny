#!/usr/bin/env python
# coding=utf-8

import subprocess

def pronounce(phenny, input): 
	stuff = input.groups()[1]
	voice = "en"
	if stuff.startswith(':') and ' ' in stuff:
		voice, stuff = stuff.split(' ')
		voice = voice[1:]
	try:
		msg = "pr: " + subprocess.check_output(["espeak", "-w", "/dev/null", "--ipa", "-v", voice, stuff], stderr=subprocess.STDOUT)
	except subprocess.CalledProcessError as e:
		msg = "fail: " + e.output
	phenny.say(msg)
pronounce.commands = ['pr']
pronounce.example = u'.pr :fi höyryjyrä'
