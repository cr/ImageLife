#!/usr/bin/env python
# -*- encoding: utf-8 -*-

try:
	import sys
	from random import random, randint
	from copy import deepcopy
	import pygame
	from pygame import gfxdraw
	from pygame.locals import *

except ImportError, err:
	print "Error, couldn't load module. %s" % (err)
	sys.exit(2)

# TODO: Are we causing slowdown by deepcopying on too many levels?

class Amino( object):
	"""Class representing an geometric object (triangle, circle asf)"""
	
	def __init__( self, base = None ):
		if base:
			self.base = deepcopy( base )
		else:
			Ax, Ay = random(), random()
			Bx, By = random(), random()
			Cx, Cy = random(), random()
			r = random()
			g = random()
			b = random()
			a = random()
			self.base = [ r, g, b, a, Ax, Ay, Bx, By, Cx, Cy ]
		return

	def mutate( self ):
		""" Mutate on property """
		# TODO: make little variance more likely
		self.base[randint( 0, len( self.base )-1 )] = random()

	def render( self, surface ):
		r, g, b, a, Ax, Ay, Bx, By, Cx, Cy = self.base
		r, g, b, a = int(256*r), int(256*g), int(256*b), int(256*a)
		w, h = surface.get_size()
		Ax, Ay, Bx, By, Cx, Cy = int(Ax*w), int(Ay*h), int(Bx*w), int(By*h), int(Cx*w), int(Cy*h)
		pygame.gfxdraw.filled_trigon( surface, Ax, Ay, Bx, By, Cx, Cy, (r,g,b,a) )


class DNA( object ):
	"""Class reppresenting a DNA string, consisting of Aminos"""
		
	def __init__( self, genome = None ):
		if genome:
			self.genome = deepcopy( genome )
		else:
			self.genome = []
			for gene in xrange( 5 ):
					self.genome.append( Amino() )

	def mutate( self ):
		self.genome[randint( 0, len( self.genome ) - 1 )].mutate()

	def mate( self, mother, father ):
		crossover = randint( 0, len( self.genome ) - 1 )
		if randint( 0, 1 ) == 0:
			father, mother = mother, father
		child = DNA( father.genome[:crossover] + mother.genome[crossover:] )
		child.mutate()
		return child

	def __mul__( self, spouse ):
		"""Syntactic sugar for mating"""
		return self.mate( self, spouse )

	def render( self, surface ):
		for amino in self.genome:
			amino.render( surface )


SIZE = ( 600, 600 )

class Imagesh( object ):
	"""Class representing an individual of the population"""

	def __init__( self, mother = None, father = None ):
		if mother and father:
			self.dna = mother.dna * father.dna
		else:
			self.dna = DNA()
		self.surface = pygame.Surface( SIZE )
		self.surface.fill( (0,0,0) )
		self.dna.render( self.surface )
		return

	def fitness( self ):
		return 0.5

class Screen( object ):

	def __init__( self, resolution = SIZE ):
		pygame.init()
		self.color = (0,0,0)
		self.resolution = resolution
		if "--fullscreen" in sys.argv:
			self.window = \
			    pygame.display.set_mode(self.resolution, pygame.FULLSCREEN) 
		else:
			self.window = pygame.display.set_mode(self.resolution)
		pygame.display.set_caption('A Simple Yet Insightful Pygame Example') 
		#pygame.mouse.set_visible(0)
		self.surface = pygame.display.get_surface()
		self.surface.fill( self.color )
		self.screen_rect = self.surface.get_rect()
		self.clock = pygame.time.Clock()
		
	def size(self):
		return self.screen_rect
	
	def clear(self):
		self.surface.fill(self.color)

	def blit( self, surface ):
		self.surface.blit( surface, (0,0) )

	def update( self ):
		pygame.display.update()
	
	def sync( self, fps=25 ):	
		self.clock.tick( fps )

	def events( self ):
		for event in pygame.event.get():
			if event.type == QUIT:
				sys.exit( 0 )
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				sys.exit( 0 )
			elif event.type == KEYDOWN and event.key == K_f:
				pygame.display.toggle_fullscreen()

screen = Screen()

def main():

	#population = []
	#for i in xrange( 23 ):
	#	population.append( Imagesh() )
	

	im = Imagesh()
	done = False
	while not done:
		child = Imagesh( im, im )
		if child.fitness() <= im.fitness():
			im = child
		done = im.fitness < 0.1

		screen.events()
		screen.clear()
		screen.blit( im.surface )
		screen.update()
		#screen.sync( 60 )

if __name__ == "__main__":
	main()

