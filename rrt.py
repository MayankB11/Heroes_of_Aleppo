import math, sys, pygame, random
from math import *
from settings import *
import time
vec = pygame.math.Vector2

class Node(object):
    def __init__(self, point, parent):
        super(Node, self).__init__()
        self.point = point
        self.parent = parent

XDIM = 960
YDIM = 800
delta = 50.0
GAME_LEVEL = 1
GOAL_RADIUS = 50
MIN_DISTANCE_TO_ADD = 50.0
NUMNODES = 500


count = 0

def dist(p1,p2):    #distance between two points
    return sqrt((p1.x-p2.x)*(p1.x-p2.x)+(p1.y-p2.y)*(p1.y-p2.y))


def point_circle_collision(p1, p2, radius):
    distance = dist(p1,p2)
    if (distance <= radius):
        return True
    return False

def step_from_to(p1,p2):
    if dist(p1,p2) < delta:
        return p2
    else:
        theta = atan2(p2.y-p1.y,p2.x-p1.x)
        return vec(p1.x + delta*cos(theta), p1.y + delta*sin(theta))


def get_random_clear(Walls):
    while True:
        p = vec(random.random()*XDIM, random.random()*YDIM)
        noCollision = collides(p,Walls)
        if noCollision == False:
            return p


def collides(point,Walls):  #initialized the obstacle
    for wall in Walls:
        wall_rect=wall.rect
        wall_pos = vec(wall.rect.center[0],wall.rect.center[1])
        if dist(point,wall_pos) < TILESIZE/2:
            return True
    return False



def reset():
    global count
    count = 0

def rrt(start,end,Wall):
    global count
    initPoseSet = True
    initialPoint = Node(vec(start.x, start.y),None)
    goalPoseSet = True
    goalPoint = Node(vec(end.x, end.y),None)
    currentState = 'init'
    t = time.time()
    nodes = []
    nodes.append(initialPoint)
    reset()
    while True:
        if time.time()-t > 0.015 :
            if len(nodes) < 5:
                return nodes[len(nodes)-1]
            else :
                return nodes[4]
        if currentState == 'goalFound':
            currNode = goalNode.parent
            if len(nodes) < 5:
                return nodes[len(nodes)-1]
            else :
                return nodes[4]
        else:
            count = count+1
            if count < NUMNODES:
                foundNext = False
                temp_count = 0
                while foundNext == False :
                    rand = get_random_clear(Wall)
                    parentNode = nodes[0]
                    for p in nodes:
                        if dist(p.point,rand) <= dist(parentNode.point,rand):
                            newPoint = step_from_to(p.point,rand)
                            if collides(newPoint,Wall) == False:
                                parentNode = p
                                foundNext = True  
                newnode = step_from_to(parentNode.point,rand)
                nodes.append(Node(newnode, parentNode))

                if point_circle_collision(newnode, goalPoint.point, GOAL_RADIUS):
                    currentState = 'goalFound'
                    goalNode = nodes[len(nodes)-1]

                
            else:
                print("Ran out of nodes... :(")
                if len(nodes) < 5:
                    return nodes[len(nodes)-1]
                else :
                    return nodes[4]
