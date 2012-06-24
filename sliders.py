#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import pygame
from pygame.locals import *
from pygame import gfxdraw
import sys
from random import randint


class Slider( object ):

	"""Class representing a pygame slider object"""

	def __init__( self, size, label=None, labelwidth=0, padding=5, fontsize=15, \
			getfunc=(lambda x: x), setfunc=(lambda x: x) ):

		# Structual naming of elements:
		# | label | slider | value |
		#
		# Internal element structure:
		#      |      width      |
		#      | pad + len + pad |
		#       start^     ^end    (absolute)

		self.value = 0.0
		self.size = size
		self.width, self.height = size
		self.center = self.height / 2
		self.pad = padding
		self.getfunc = getfunc
		self.setfunc = setfunc

		self.surface = pygame.surface.Surface( self.size )
		self.surface = self.surface.convert_alpha()

		self.fgcolor = pygame.Color( 255,255,255,220 )
		self.bgcolor = pygame.Color( 0,0,0,127 )

		self.font = pygame.font.Font( None, fontsize )

		if label:
			self.labeltext = label
			self.label = self.font.render( label, 1, self.fgcolor )
			self.labelstart = self.pad
			self.labellen = self.label.get_width()
			if self.labellen < labelwidth - 2*self.pad:
				self.labellen = labelwidth - 2*self.pad
				self.labelwidth = labelwidth
			else:
				self.labelwidth = self.labellen + 2*self.pad
		else:
			self.labeltext = None
			self.label = None
			self.labelwidth = 0
			self.labellen = 0
		
		self.valuelen, self.fontheight = self.font.size( '-0,000' )
		self.valuewidth = self.valuelen + 2*self.pad
		self.valueend = self.width - self.pad
		self.valuestart = self.valueend - self.valuelen

		self.sliderstart = self.labelwidth + self.pad
		self.sliderend = self.width - self.valuewidth - self.pad
		self.sliderlen = self.sliderend - self.sliderstart
		self.sliderwidth = self.width - self.labelwidth - self.valuewidth

		self.update()

	def valuetox( self, value ):
		return int( value * self.sliderlen ) + self.sliderstart

	def xtovalue( self, x ):
		return float( x - self.sliderstart ) / self.sliderlen

	def clear( self ):
		self.surface.fill( self.bgcolor )

	def update( self ):
		self.clear()

		if self.label:
			pos = self.label.get_rect( centery=self.center+1, left = self.labelstart )
			self.surface.blit( self.label, pos )

		x = self.valuetox( self.value )
		pygame.gfxdraw.hline( self.surface, self.sliderstart, self.sliderend, self.center, self.fgcolor )
		pygame.gfxdraw.aacircle( self.surface, x, self.center, 2, self.fgcolor )

		valuestring = "%.3g" % self.get()
		valuesurface = self.font.render( valuestring, 1, self.fgcolor )
		pos = valuesurface.get_rect( centery=self.center+1, left = self.valuestart )
		self.surface.blit( valuesurface, pos )

	def set( self, value ):
		self.value = float( self.setfunc( value ) )
		self.update()

	def get( self ):
		return self.getfunc( self.value )

	def render( self, surface, pos=(0,0) ):
		surface.blit( self.surface, pos )
	
	def isclicked( self, click, corner=(0,0) ):
		"""Check if click is within slider relative to corner"""
		xcorner, ycorner = corner
		xclick, yclick = click
		xrel, yrel = xclick-xcorner, yclick-ycorner
		left, right = self.sliderstart, self.sliderend
		top, bottom = 0, self.height
		if xrel>=left and xrel<right:
			if yrel>=top and yrel<bottom:
				return True
		return False

	def clickvalue( self, click, corner=(0,0) ):
		"""Returns slider value of click relative to corner"""
		xcorner, ycorner = corner
		xclick, yclick = click
		xrel, yrel = xclick-xcorner, yclick-ycorner
		left, right = self.sliderstart, self.sliderend
		top, bottom = 0, self.height
		xslider = float( xrel - left ) / self.sliderlen
		if xslider < 0.0:
			xslider = 0.0
		elif xslider > 1.0:
			xslider = 1.0
		return self.getfunc( xslider )

screendim = 600, 400
sliderdim = 400, 15
sliderpad = 5
sliderbox = sliderdim[0], sliderdim[1]*6+sliderpad*5 

pygame.init()

fs = False
if pygame.display.list_modes():
	fs = True
	screendim = pygame.display.list_modes()[0]

if fs:
	screen = pygame.display.set_mode( screendim, pygame.FULLSCREEN, 32 )
else:
	screen = pygame.display.set_mode( screendim, 0, 32 )

pygame.display.set_caption( "PyGame Slider Demo" )
clock = pygame.time.Clock()

color = pygame.Color( randint( 0,255 ), randint( 0,255 ), randint( 0, 255 ), 255 )

x, y = (screendim[0]-sliderbox[0])/2, (screendim[1]-sliderbox[1])/2

# rgb converters
rgbf = ( lambda x: int(255.0*x) )
rgbif = ( lambda x: float(x) / 255.0 )
# hsv converters
hf = ( lambda x: 359.0*x )
hif = ( lambda x: x/359.0 )
svf = ( lambda x: 100.0*x )
svif = ( lambda x: x/100.0 )

config = (
	( "Red",   color.r, rgbf, rgbif ),
	( "Green", color.g, rgbf, rgbif ),
	( "Blue",  color.b, rgbf, rgbif ),
	( "Hue",   color.hsva[0], hf, hif ),
	( "Sat.",  color.hsva[1], svf, svif ),
	( "Value", color.hsva[2], svf, svif ),
)

sliders = {}
for label, init, gfunc, sfunc in config:
	slider = Slider( sliderdim, label, 40, getfunc=gfunc, setfunc=sfunc )
	slider.set( init )
	pos = x, y
	sliders[label] = (slider, pos)
	y += sliderdim[1]+sliderpad

updated = True
state = "IDLE"
clicked = None
pressedbefore = (False, False, False)
while True:

	if updated:
		screen.fill( color )
		for label, ( slider, pos ) in sliders.items():
			slider.render( screen, pos )
		pygame.display.update()

	clock.tick( 25 )
	
	mouse = pygame.mouse.get_pos()

	updated = False
	for event in pygame.event.get():
		if event.type == QUIT:
			sys.exit()
		elif event.type == KEYDOWN and event.key == K_ESCAPE:
			sys.exit()
		elif event.type == KEYDOWN and event.key == K_f:
			if fs:
				pygame.display.toggle_fullscreen()
		elif event.type == MOUSEBUTTONDOWN:
			pressednow = pygame.mouse.get_pressed()
			if pressednow[0] and not pressedbefore[0]:
				for label, ( slider, pos ) in sliders.items():
					if slider.isclicked( mouse, pos ):
						state = "MOVING"
						clicked = label
						updated = True
			pressedbefore = pressednow
		elif event.type == MOUSEBUTTONUP:
			pressednow = pygame.mouse.get_pressed()
			if pressedbefore[0] and not pressednow[0]:
				state = "IDLE"
				clicked = None
			pressedbefore = pressednow
		elif event.type == MOUSEMOTION:
			if state == "MOVING":
				updated = True

	if updated:
		if state == "MOVING":
			# lazy refactoring
			label = clicked
			click = mouse
			slider, pos = sliders[label]
			if label == "Red":
				color.r = slider.clickvalue( click, pos )
			elif label == "Green":
				color.g = slider.clickvalue( click, pos )
			elif label == "Blue":
				color.b = slider.clickvalue( click, pos )
			elif label == "Hue":
				new = slider.clickvalue( click, pos )
				hsva = ( new, color.hsva[1], color.hsva[2], color.hsva[3] )
				#print "DEBUG:", hsva
				color.hsva = hsva
			elif label == "Sat.":
				new = slider.clickvalue( click, pos )
				hsva = ( color.hsva[0], new, color.hsva[2], color.hsva[3] )
				#print "DEBUG:", hsva
				color.hsva = hsva
				slider.set( color.hsva[1] )
			elif label == "Value":
				new = slider.clickvalue( click, pos )
				hsva = ( color.hsva[0], color.hsva[1], new, color.hsva[3] )
				#print "DEBUG:", hsva
				color.hsva = hsva
			# update sliders
			sliders["Red"][0].set( color.r )
			sliders["Green"][0].set( color.g )
			sliders["Blue"][0].set( color.b )
			sliders["Hue"][0].set( color.hsva[0])
			sliders["Sat."][0].set( color.hsva[1])
			sliders["Value"][0].set( color.hsva[2])

