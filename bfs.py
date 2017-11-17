import pygame
from settings import *
from enum import Enum
vec = pygame.math.Vector2

class Direction(Enum):
	stat 	= 0
	left	= 1
	right	= -1
	up		= 2
	down	= -2

def isValid(x,y):
	if (x<0 or x>=HEIGHT/TILESIZE):
		return False
	if (y<0 or y>=WIDTH/TILESIZE):
		return False

	return True

def bfs(start,stepsMap,Wall):

	queue = [start]
	explored = []
	parent = {}
	while queue:
		node = queue.pop(0)
		explored.append(node)
		for i in range(-1,2):
			for j in range(-1,2):
				node1 = vec(node.x+i,node.y+j)
				if isValid(node.x+i,node.y+j) and node1 not in explored and node1 not in Wall:
					queue.append(node1)
					explored.append(node1)
					parent[str(node1)]=node
	for key in parent :
		stepsMap[str([key,start])] = parent[key]


def generateSteps(Wall):
	
	stepsMap = {}
	count = 0
	for i in range(WIDTH//TILESIZE):
		for j in range(HEIGHT//TILESIZE):
			stepsMap[str([vec(i,j),vec(i,j)])]=vec(i,j)
	
	for i in range(WIDTH//TILESIZE):
		for j in range(HEIGHT//TILESIZE):
			print("Here",count)
			count = count + 1
			bfs(vec(i,j),stepsMap,Wall)

	return stepsMap

