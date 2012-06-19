#!/usr/bin/env python
# -*- encoding: utf-8 -*-

try:
	import sys
	import time
	from random import random, randint
	from copy import deepcopy
	import pygame
	from pygame import gfxdraw
	from pygame.locals import *
	import numpy

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
			z = random()
			r = random()
			g = random()
			b = random()
			a = random()*0.3
			self.base = [ r, g, b, a, z, Ax, Ay, Bx, By, Cx, Cy ]
		return

	def depth( self ):
		return self.base[4]

	def mutate( self ):
		""" Mutate on property """
		# TODO: make small variance more likely
		#for i in xrange( 0, len( self.base ) ):
		#	self.base[i] = random()

		what = randint( 0, 7 )
		if what  == 0:
			self.base[0] = random()
		elif what == 1:
			self.base[1] = random()
		elif what == 2:
			self.base[2] = random()
		elif what == 3:
			# make alpha preferably small
			self.base[3] = numpy.random.beta(3, 5)
		elif what == 4:
			self.base[4] = random()
		elif what == 5:
			self.base[5:7] = random(), random()
		elif what == 6:
			self.base[7:9] = random(), random()
		elif what == 7:
			self.base[9:11] = random(), random()


	def render( self, surface ):
		r, g, b, a, z, Ax, Ay, Bx, By, Cx, Cy = self.base
		r, g, b, a = int(256*r), int(256*g), int(256*b), int(256*a)
		w, h = surface.get_size()
		Ax, Ay, Bx, By, Cx, Cy = int(Ax*w), int(Ay*h), int(Bx*w), int(By*h), int(Cx*w), int(Cy*h)
		pygame.gfxdraw.filled_trigon( surface, Ax, Ay, Bx, By, Cx, Cy, pygame.Color(r,g,b,a) )


class DNA( object ):
	"""Class reppresenting a DNA string, consisting of Aminos"""
		
	def __init__( self, genome = None ):
		if genome:
			self.genome = deepcopy( genome )
		else:
			self.genome = []
			for gene in xrange( 120 ):
					self.genome.append( Amino() )

	def mutate( self ):
		#for i in xrange( 0, len( self.genome )/10 ):
		for i in xrange( 0, 2 ):
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
		for amino in sorted( self.genome, key = lambda x: x.depth() ):
			amino.render( surface )


class Imagesh( object ):
	"""Class representing an individual of the population"""

	goddesssurface = None
	goddess = None
	size = None

	def __init__( self, mother = None, father = None ):
		if Imagesh.goddess != None:
			assert Imagesh.size
			if mother and father:
				self.dna = mother.dna * father.dna
			else:
				self.dna = DNA()
			self.surface = pygame.Surface.convert_alpha( pygame.Surface( Imagesh.size ) )
			self.surface.fill( (0,0,0) )
			self.dna.render( self.surface )
			self.fit = None
		return

	def convert( self, surface ):
		"""Converts pygame surface to numpy array for fitness function"""
		array = numpy.ndarray \
		        (shape=(surface.get_width(), surface.get_height(), 3),
		         dtype=numpy.uint8, buffer=surface.get_buffer(),
		         offset=1, strides=(4, surface.get_pitch(), 1))
		return array

	def target( self, goddess ):
		"""Sets target surface for fitness function"""
		goddess = pygame.Surface.convert_alpha( goddess )
		Imagesh.goddesssurface = goddess
		Imagesh.goddess = Imagesh.convert( self, goddess )
		Imagesh.size = ( goddess.get_width(), goddess.get_height() )

	def fitness( self ):
		"""Fitness of individual compared to target"""
		if not self.fit:
			pygame.surfarray.use_arraytype( "numpy" )
			#print "INFO:", self.surface.get_shifts(), Imagesh.goddesssurface.get_shifts()
			likeness = Imagesh.convert( self, self.surface )
			#print "SELF:", selfarray
			difference = numpy.abs( Imagesh.goddess - likeness )
			self.fit = numpy.average( difference )
		return self.fit


class Screen( object ):

	def __init__( self, resolution = (400,400) ):
		pygame.init()
		self.color = (0,0,0)
		self.resolution = resolution
		if "--fullscreen" in sys.argv:
			self.window = \
			    pygame.display.set_mode(self.resolution, pygame.FULLSCREEN) 
		else:
			self.window = pygame.display.set_mode(self.resolution)
		pygame.display.set_caption( "ImageLife" ) 
		#pygame.mouse.set_visible( 0 )
		self.surface = pygame.display.get_surface()
		self.surface.fill( self.color )
		self.rect = self.surface.get_rect()
		self.clock = pygame.time.Clock()
		
	def size(self):
		return self.rect
	
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


def main():

	# CAVE: crucial sequence:
	# pygame must be intialized per Screen() before
    # Imagesh.target() can convert target surface
	goddess = pygame.image.load( sys.argv[-1] )
	screen = Screen( ( goddess.get_width(), goddess.get_height() ) )

	# Dummy instance for calling class methods
	# TODO: This is odd. There must be a better way.
	tmp = Imagesh()
	Imagesh.target( tmp, goddess )

	# Play god, create population
	populationsize = 12
	population = []
	for i in xrange( 0, populationsize ):
		population.append( Imagesh() )
	# Impose hierarchy for mating
	population.sort( key = lambda x: x.fitness() )

	done = False
	start = time.time()
	prev = start
	generation = 0
	while not done:
		generation += 1
		# The fittest shall procreate
		for i in xrange( 0, len( population )/4 ):
			#Perhaps monogamy is better ofter all?
			mother = int( (1.0-numpy.random.beta(5, 1)) * len( population ) )
			father = mother
			while father == mother:
				father = int( (1.0-numpy.random.beta(5, 1)) * len( population ) )
			#print "MATING:", mother, father
			population.append( Imagesh( population[mother], population[father] ) )
			population.append( Imagesh( population[mother], population[father] ) )

		# The least fit must perish, keep population size constant
		population.sort( key = lambda x: x.fitness() )
		population = population[:populationsize]

		now = time.time()
		if now-prev > 0.5:
			prev = now
			screen.events()
			screen.clear()
			screen.blit( population[0].surface )
			#screen.blit( goddess )
			screen.update()
			#screen.sync( 60 )

		print generation, now-start, population[0].fitness(), population[1].fitness(), population[2].fitness(), population[-1].fitness()
		done = population[0].fitness() < 10

if __name__ == "__main__":
	main()

