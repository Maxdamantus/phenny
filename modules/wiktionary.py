#!/usr/bin/env python
"""
wiktionary.py - Phenny Wiktionary Module
Copyright 2009, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re
import web
import HTMLParser

uri = 'http://%s.wiktionary.org/w/index.php?title=%s&printable=yes'
r_tag = re.compile(r'<[^>]+>')
r_ul = re.compile(r'(?ims)<ul>.*?</ul>')

def text(html): 
   text = r_tag.sub('', html).strip()
   text = text.replace('\n', ' ')
   text = text.replace('\r', '')
   text = text.replace('(intransitive', '(intr.')
   text = text.replace('(transitive', '(trans.')
   return text
   return HTMLParser.HTMLParser().unescape(text)

anomalies = {
  "h4": ["ru", "nl"],
  "h2": ["hi"],
  "p": ["ko"]
}

def wiktionary(lang, word, filter): 
   bytes = web.get(uri % (lang, web.urllib.quote(word.encode('utf-8'))))
   bytes = r_ul.sub('', bytes)

   mode = None
   etymology = None
   definitions = {}
   head = "h3"
   listtype = None
   for h, langs in anomalies.items():
      if lang in langs:
         head = h
   for line in bytes.splitlines(): 
      if line.endswith("</%s>" % head) and "id=\"" in line:
         sub = text(line)
#         if "</span>" in sub:
#            sub = sub.split("</span>")[0]
#         if ">" in sub:
#            sub = sub.split(">")[-1]
         mode = sub.lower()
         if filter and not (mode in filter):
            mode = None
      else:
         if listtype != None and '</' + listtype + '>' in line: 
            mode = None
         elif listtype == None:
            for lt in ["ul", "ol"]:
               if '<' + lt + '>' in line:
                 listtype = lt

         elif (mode == 'etmyology') and ('<p>' in line): 
            etymology = text(line)
         elif (mode is not None) and ('<li>' in line):
            definitions.setdefault(mode, []).append(text(line))

      if '<hr' in line: 
         break
   return etymology, definitions

parts = ('preposition', 'particle', 'noun', 'verb', 
   'adjective', 'adverb', 'interjection', 'proverb',
   'determiner', 'article', 'suffix', 'prefix',
   'pronoun')

def format(word, definitions, number=2): 
   result = '%s' % word.encode('utf-8')
   for part in definitions.keys(): 
      if definitions.has_key(part): 
         defs = definitions[part][:number]
         result += u' \u2014 '.encode('utf-8') + ('%s: ' % part)
         n = ['%s. %s' % (i + 1, e.strip(' .')) for i, e in enumerate(defs)]
         result += ', '.join(n)
   return result.strip(' .,')

def w(phenny, input): 
   if not input.group(2):
      return phenny.reply("Nothing to define.")
   word = input.group(2)
   filter = []
   while word.startswith('#') and (' ' in word):
      a, b = word.split(' ', 1)
      a = a.lstrip('#')
      if a.isalpha():
         filter.append(a)
         word = b
   language = "en"
   if word.startswith(':') and (' ' in word): 
      a, b = word.split(' ', 1)
      a = a.lstrip(':')
      if a.isalpha(): 
         language, word = a, b
   etymology, definitions = wiktionary(language, word, filter)
   if not definitions: 
      phenny.say("Couldn't get any definitions for %s." % word)
      return

   result = format(word, definitions)
   if len(result) < 150: 
      result = format(word, definitions, 3)
   if len(result) < 150: 
      result = format(word, definitions, 5)

   if len(result) > 300: 
      result = result[:295] + '[...]'
   phenny.say(result)
w.commands = ['w']
w.example = '.w bailiwick'

def encarta(phenny, input): 
   return phenny.reply('Microsoft removed Encarta, try .w instead!')
encarta.commands = ['dict']

if __name__ == '__main__': 
   print __doc__.strip()
