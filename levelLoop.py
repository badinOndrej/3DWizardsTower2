import sys
import math
import pygame
from pygame.locals import *
from functools import cmp_to_key

DISPLAY = None

textureDebug = False

playerPos = {"x":0, "y":0}
playerDir = {"x": -1, "y": 0}
rotSpeed = 0.1
playerSpeed = 0.075
clock = pygame.time.Clock()

planeX = 0
planeY = 0.66

drawMap = False

w = 160
h = 480

fov = math.radians(60)
fovInc = math.radians(0.375)

keypressed = {"up":False, "down":False, "left":False, "right":False}

currLevel = 0
levelMaps = [
    [
        [1,1,1,1,1,1,1,1,1,5,1,1],
        [1,0,0,0,0,0,0,1,0,0,0,1],
        [1,0,2,3,0,2,0,1,2,2,2,1],
        [4,0,0,0,0,0,0,1,0,0,0,1],
        [1,0,2,0,0,2,0,1,0,0,0,1],
        [1,0,2,2,2,2,0,1,0,0,0,1],
        [1,0,0,0,0,0,0,1,0,0,0,1],
        [1,1,1,0,0,1,1,1,1,1,0,1],
        [1,0,0,0,0,0,0,1,0,0,0,1],
        [4,0,3,2,2,3,0,0,0,0,0,4],
        [1,0,0,0,0,0,0,1,0,0,0,1],
        [1,1,1,1,1,1,1,1,1,1,1,1]
    ]
]
levelMapDims = [
    {"x":12, "y":12}
]
levelPlayerData = [
    {"x":9.5, "y":9.5, "aX":-1, "aY":0}
]
levelTextures = [
    [
        "grf/brickWall.png", "grf/bookcase.png", "grf/potionShelf.png", "grf/doorOnBrickWall.png", "grf/stairsUp.png"
    ]
]
levelDoors = [
    [
        [9, 2, "hidden"] # x y type
    ]
]
levelSprites = [
    [
        (4, 4, "furn", 0)
    ]
]
spriteTextures = [
    "grf/sprites/chair.png"
]

levelBackground = pygame.image.load("grf/levelBackground.png")

currLevelTextures = []
currLevelSprites = []

debugColoursA = [0xff0000, 0x00ff00, 0x0000ff, 0xffff00, 0xff00ff, 0x00ffff, 0xffffff]
debugColoursB = [0x800000, 0x008000, 0x000080, 0x808000, 0x800080, 0x008080, 0x808080]

def sprite_compare(s1, s2):
    s1dist = math.sqrt((s1[0] - playerPos["x"]) ** 2 + (s1[1] - playerPos["y"]) ** 2)
    s2dist = math.sqrt((s2[0] - playerPos["x"]) ** 2 + (s2[1] - playerPos["y"]) ** 2)
    if s1dist>s2dist:
        return -1
    elif s1dist==s2dist:
        return 0
    else:
        return 1

def raycast():
    zBuffer = []
    dirX = playerDir["x"]
    dirY = playerDir["y"]
    for x in range(0, w):
        cameraX = 2 * x / float(w) - 1
        rayDirX = dirX + planeX * cameraX
        rayDirY = dirY + planeY * cameraX
        # where on map
        mapX = int(playerPos["x"])
        mapY = int(playerPos["y"])
        # length of ray from curr pos to next xy side
        sideDistX = 0.0
        sideDistY = 0.0
        # from one xy side to the next
        if rayDirX == 0: rayDirX = 0.00001
        deltaDistX = abs(1 / rayDirX)
        if rayDirY == 0: rayDirY = 0.00001
        deltaDistY = abs(1 / rayDirY)
        perpWallDist = 0.0
        # step direction
        stepX = 0
        stepY = 0
        # wall hit
        hit = 0
        side = 0
        # step & init sideDist
        if rayDirX < 0:
            stepX = -1
            sideDistX = (playerPos["x"] - mapX) * deltaDistX
        else:
            stepX = 1
            sideDistX = (mapX + 1.0 - playerPos["x"]) * deltaDistX
        if rayDirY < 0:
            stepY = -1
            sideDistY = (playerPos["y"] - mapY) * deltaDistY
        else:
            stepY = 1
            sideDistY = (mapY + 1.0 - playerPos["y"]) * deltaDistY
        # DDA
        while hit == 0:
            if(sideDistX < sideDistY):
                sideDistX += deltaDistX
                mapX += stepX
                side = 0
            else:
                sideDistY += deltaDistY
                mapY += stepY
                side = 1
            # was a wall hit
            if levelMaps[currLevel][mapY][mapX] > 0: hit = 1
        # calc distance
        if side == 0:
            perpWallDist = (mapX - playerPos["x"] + (1 - stepX) / 2) / rayDirX
        else:
            perpWallDist = (mapY - playerPos["y"] + (1 - stepY) / 2) / rayDirY
        zBuffer.append(perpWallDist)
        # calc line height
        lineHeight = int(h / perpWallDist)
        drawStartY = -lineHeight / 2 + h / 2
        drawEndY = lineHeight / 2 + h / 2
        # get texture
        texture = currLevelTextures[levelMaps[currLevel][mapY][mapX] - 1]
        # if debug, draw solid colours
        if textureDebug == True:
            img = pygame.Surface((4, lineHeight))
            col = debugColoursA[levelMaps[currLevel][mapY][mapX] - 1]
            if side==1: col = debugColoursB[levelMaps[currLevel][mapY][mapX] - 1]
            img.fill(col)
            DISPLAY.blit(img, (x*4, drawStartY))
        else:
            # calc texture hit
            wallX = 0
            if side == 0:
                wallX = playerPos["y"] + perpWallDist * rayDirY
            else:
                wallX = playerPos["x"] + perpWallDist * rayDirX
            wallX -= math.floor((wallX))
            # calc x coord
            texX = int(wallX * texture.get_width())
            if side == 0 and rayDirX > 0:
                texX = texture.get_width() - texX - 1
            if side == 1 and rayDirY < 0:
                texX = texture.get_width() - texX - 1
            # get strip
            strip = pygame.Surface((1, texture.get_height()))
            strip.blit(texture, (0,0), (texX,0,texX+1,texture.get_height()))
            # if side 1, darken
            if side == 1:
                dark = pygame.Surface(texture.get_size()).convert_alpha()
                dark.fill((0,0,0,127))
                strip.blit(dark, (0,0))
            # scale strip
            strip = pygame.transform.scale(strip, (4, lineHeight))
            # blit to screen
            DISPLAY.blit(strip, (x*4, drawStartY))
    drawSprites(zBuffer)
    
# handles drawing sprites
def drawSprites(zBuffer):
    # sort sprites
    levelSprites[currLevel].sort(key=cmp_to_key(sprite_compare))
    # draw sprites
    for spr in levelSprites[currLevel]:
        # get texture
        sprTex = currLevelSprites[spr[3]]
        # sprite pos
        spriteX = spr[0] - playerPos["x"]
        spriteY = spr[1] - playerPos["y"]
        # inverse matrix transform
        invDet = 1.0 / (planeX * playerDir["y"] - playerDir["x"] * planeY)
        transformX = invDet * (playerDir["y"] * spriteX - playerDir["x"] * spriteY)
        transformY = invDet * (-planeY * spriteX + planeX * spriteY)    # z-depth
        # screen x coord
        spriteScreenX = int((w/2) * (1 + transformX / transformY))
        # height on screen
        spriteHeight = abs(int(h / transformY))
        drawStartY = int(-spriteHeight / 2 + h / 2)
        # width on screen
        spriteWidth = abs(int(w / transformY))
        drawStartX = int(-spriteWidth / 2 + spriteScreenX)
        if drawStartX < 0: drawStartX = 0
        drawEndX = int(spriteWidth / 2 + spriteScreenX)
        if drawEndX >= w: drawEndX = w-1
        # draw by strips
        for stripX in range(drawStartX, drawEndX):
            # texture x coord
            texX = math.floor(256 * (stripX - (-spriteWidth / 2 + spriteScreenX)) * sprTex.get_width() / spriteWidth) / 256
            # draw if
            # in front of camera
            # on screen - left
            # on screen - right
            # not occluded
            if transformY > 0 and stripX > 0 and stripX < w and transformY < zBuffer[stripX]:
                strip = pygame.Surface((1, sprTex.get_height()))
                strip.blit(sprTex, (0,0), (texX, 0, texX+1, sprTex.get_height()))
                strip.set_colorkey(0xff00ff)
                strip = pygame.transform.scale(strip, (4, spriteHeight))
                DISPLAY.blit(strip, (stripX * 4, drawStartY))
        

def updateGameVars(currLevel):
    playerPos["x"] = levelPlayerData[currLevel]["x"]
    playerPos["y"] = levelPlayerData[currLevel]["y"]
    playerDir["x"] = levelPlayerData[currLevel]["aX"]
    playerDir["y"] = levelPlayerData[currLevel]["aY"]
    for tex in levelTextures[currLevel]:
        currLevelTextures.append((pygame.image.load(tex)).convert())
    for spr in levelSprites[currLevel]:
        currLevelSprites.append((pygame.image.load(spriteTextures[spr[3]])).convert())

def initLevelLoop(surface):
    global currLevel, levelBackground, DISPLAY
    DISPLAY = surface
    currLevel = 0
    levelBackground = levelBackground.convert()
    updateGameVars(currLevel)
    levelLoop()

def levelLoop():
    global currLevel, playerSpeed, clock, drawMap, DISPLAY, planeX, planeY
    
    # game loop
    while True:
        DISPLAY.blit(levelBackground, (0,0))

        raycast()

        if drawMap:
            # draw map
            mapDx = 640 / levelMapDims[currLevel]["y"]
            mapDy = 480 / levelMapDims[currLevel]["x"]
            for mapY in range(0,levelMapDims[currLevel]["y"]):
                for mapX in range(0,levelMapDims[currLevel]["x"]):
                    if levelMaps[currLevel][mapX][mapY] > 0:
                        pygame.draw.rect(DISPLAY, 0x44aaff, Rect((mapX * mapDx) + 1, (mapY * mapDy) + 1, mapDx - 2, mapDy - 2))

            # draw player on map
            playerScreenX = playerPos["y"] * mapDx
            playerScreenY = playerPos["x"] * mapDy
            pygame.draw.rect(DISPLAY, 0xffaa44, Rect(playerScreenX-2,playerScreenY-2,5,5))
            pygame.draw.line(DISPLAY,0xffaa44,(playerScreenX, playerScreenY), (playerScreenX + 30*playerDir["y"], playerScreenY + 30*playerDir["x"]), 3)

        pygame.display.update()
        # manage events - quit, keyboard input
        for event in pygame.event.get():
            # keyboard
            if event.type == KEYDOWN:
                if event.__dict__["key"] == K_LEFT:
                    keypressed["left"] = True
                if event.__dict__["key"] == K_RIGHT:
                    keypressed["right"] = True
                if event.__dict__["key"] == K_UP:
                    keypressed["up"] = True
                if event.__dict__["key"] == K_DOWN:
                    keypressed["down"] = True
                if event.__dict__["key"] == K_m:
                    drawMap = not drawMap
                if event.__dict__["key"] == K_SPACE:
                    # try to open hidden door
                    newPosX = playerPos["x"] + playerSpeed * playerDir["x"]
                    newPosY = playerPos["y"] + playerSpeed * playerDir["y"]
                    for door in levelDoors[currLevel]:
                        if (door[0] == math.floor(newPosX)) and (door[1] == math.floor(newPosY)):
                            if door[2] == "hidden":
                                levelMaps[currLevel][door[1]][door[0]] = 0
            if event.type == KEYUP:
                if event.__dict__["key"] == K_LEFT:
                    keypressed["left"] = False
                if event.__dict__["key"] == K_RIGHT:
                    keypressed["right"] = False
                if event.__dict__["key"] == K_UP:
                    keypressed["up"] = False
                if event.__dict__["key"] == K_DOWN:
                    keypressed["down"] = False
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        # execute movement
        if keypressed["up"]:
            newPosX = playerPos["x"] + playerSpeed * playerDir["x"]
            newPosY = playerPos["y"] + playerSpeed * playerDir["y"]
            if levelMaps[currLevel][math.floor(newPosY)][math.floor(newPosX)] == 0:
                playerPos["x"] = newPosX
                playerPos["y"] = newPosY
        if keypressed["down"]:
            newPosX = playerPos["x"] - playerSpeed * playerDir["x"]
            newPosY = playerPos["y"] - playerSpeed * playerDir["y"]
            if levelMaps[currLevel][math.floor(newPosY)][math.floor(newPosX)] == 0:
                playerPos["x"] = newPosX
                playerPos["y"] = newPosY
        if keypressed["right"]:
            oldDirX = playerDir["x"]
            playerDir["x"] = playerDir["x"] * math.cos(-rotSpeed) - playerDir["y"] * math.sin(-rotSpeed)
            playerDir["y"] = oldDirX * math.sin(-rotSpeed) + playerDir["y"] * math.cos(-rotSpeed)
            oldPlaneX = planeX
            planeX = planeX * math.cos(-rotSpeed) - planeY * math.sin(-rotSpeed)
            planeY = oldPlaneX * math.sin(-rotSpeed) + planeY * math.cos(-rotSpeed)
        if keypressed["left"]:
            oldDirX = playerDir["x"]
            playerDir["x"] = playerDir["x"] * math.cos(rotSpeed) - playerDir["y"] * math.sin(rotSpeed)
            playerDir["y"] = oldDirX * math.sin(rotSpeed) + playerDir["y"] * math.cos(rotSpeed)
            oldPlaneX = planeX
            planeX = planeX * math.cos(rotSpeed) - planeY * math.sin(rotSpeed)
            planeY = oldPlaneX * math.sin(rotSpeed) + planeY * math.cos(rotSpeed)
        # limit framerate
        clock.tick(20)
