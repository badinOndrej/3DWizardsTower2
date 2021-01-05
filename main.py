import sys
import math
import random
import pygame
from pygame.locals import *
import levelLoop

#DISPLAY = pygame.display.set_mode((320,240),pygame.FULLSCREEN)
DISPLAY = pygame.display.set_mode((640,480))
pygame.display.set_caption("3D Wizard's Tower 2")

levelLoop.initLevelLoop(DISPLAY)