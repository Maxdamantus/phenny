#!/usr/bin/env python
# coding=utf-8

from fractions import Fraction
from decimal import Decimal

# meh, just don't mutate it
class idict(dict):
	def __hash__(self):
		return hash(tuple(sorted(self.items())))

class Value:
	# data :: (String → Value) → Fraction
	# sum [ val * product [ a^b | a→b <- set ] | set→val <- data ]
	def __init__(self, data):
		self.data = data
	
	def __eq__(self, other):
		return other and self.data == other.data
	
	def __ne__(self, other):
		return not other or self.data != other.data
	
	def __hash__(self):
		return hash(self.data)
	
	def __add__(a, b):
		out = dict(a.data)
		for bpart, bmult in b.data.items():
			if bpart in out:
				out[bpart] += bmult
				if out[bpart] == 0:
					del out[bpart]
			else:
				out[bpart] = bmult
		return Value(idict(out))
	
	def __mul__(a, b):
		out = zero
		for apart, amult in a.data.items():
			for bpart, bmult in b.data.items():
				newpart = dict(apart)
				for bpartpart, bpartexp in bpart.items():
					if bpartpart in newpart:
						newpart[bpartpart] += bpartexp
						if newpart[bpartpart] == zero:
							del newpart[bpartpart]
					else:
						newpart[bpartpart] = bpartexp
				out += Value({ idict(newpart): amult*bmult })
		return out
	
	def __sub__(a, b):
		return b.__add__(a.negate())
	
	def __truediv__(a, b):
		return b.__mul__(a.invert())
	
	def negate(a):
		out = dict(a.data)
		for k in out.keys():
			out[k] *= -1
		return Value(idict(out))
	
	def invert(a):
		out = {}
		for part, mult in a.data.items():
			parts = {}
			for partpart, exp in part.items():
				parts[partpart] = exp.negate()
			out[idict(parts)] = 1/mult
		return Value(idict(out))
	
	def tree(self):
		out = None
		for part, mult in self.data.items():
			outpart = mult
			for partpart, exp in part.items():
				outpartpart = partpart
				if exp != one:
					outpartpart = ("^", [outpartpart, exp.tree()])
				outpart = ("*", [outpart, outpartpart])
			if out == None:
				out = outpart
			else:
				out = ("+", [out, outpart])
		if out == None:
			out = Fraction(0)
		return out

	def __repr__(self):
		return "Value(" + str(self.data) + ")"
	
	def __str__(self):
		return self.__repr__()

def makeValue(v):
	if isinstance(v, int):
		return zero if v == 0 else Value(idict({ idict({}): Fraction(v) }))
	if all(map(str.isdigit, v)):
		return makeValue(int(v))
	return Value(idict({ idict({ str(v): one }): Fraction(1) }))

# defined simply for convenience; other such objects might exist—they'll be equal to these ones .. hopefully
zero = Value(idict({}))
one = makeValue(1)

def binop(fn):
	return lambda s: s.append(fn(s.pop(), s.pop()))

def val(v):
	return lambda s: s.append(v)

def parsetok(s):
	if s == "*": return binop(Value.__mul__)
	if s == "/": return binop(Value.__truediv__)
	if s == "+": return binop(Value.__add__)
	if s == "-": return binop(Value.__sub__)
	return val(makeValue(s))

def evalrpn(s):
	if isinstance(s, str):
		s = filter(None, s.split(" "))
	stack = []
	for i in map(parsetok, s):
		i(stack)
	return stack

def treetorpn(t):
	if isinstance(t, Fraction):
		if t.denominator == 1:
			return [str(t.numerator)]
		# TODO: fraction
		return [str(t.numerator), str(t.denominator), "/"]
	if isinstance(t, str):
		return [t]
	op, operands = t
	return sum(map(treetorpn, operands), []) + [op]

def compose(fns):
	out = lambda x: x
	for fn in reversed(fns):
		out = compose2(fn, out)
	return out

def compose2(a, b):
	return lambda c: a(b(c))

def runrpn(input):
	return "; ".join(map(compose([" ".join, treetorpn, Value.tree]), evalrpn(input)))

def rc(phenny, input):
	phenny.say("rc: " + runrpn(input.group(2).encode("utf-8")))
rc.commands = ['rc']
rc.example = '.rc 5 3 +'
