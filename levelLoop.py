import sys
import math
import pygame
from pygame.locals import *
from functools import cmp_to_key

DISPLAY = None

playerPos = {"x":0, "y":0}
playerAng = 0
playerSpeed = 0.075
clock = pygame.time.Clock()

drawMap = False

w = 640
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
    {"x":9.5, "y":9.5, "a":math.pi}
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
        (4.5, 4.5, "furn", 0)
    ]
]
spriteTextures = [
    "grf/sprites/chair.png"
]

levelBackground = pygame.image.load("grf/levelBackground.png")

currLevelTextures = []
currLevelSprites = []

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
    global fov, fovInc, playerAng, currLevel, w, h, DISPLAY
    rayAngle = playerAng - (fov / 2)
    zBuffer = []
    dirY = math.sin(playerAng)
    dirX = math.cos(playerAng)
    planeX = 0
    planeY = 0.66
    for x in range(0, w):
        # ray pos & dir
        cameraX = float(2 * x / float(w) - 1) # x coord in camera space
        rayPosX = playerPos["x"]
        rayPosY = playerPos["y"]
        rayDirX = dirX + planeX * cameraX
        rayDirY = dirY + planeY * cameraX
        # where on map are we
        mapX = int(rayPosX)
        mapY = int(rayPosY)
        # ray length from curr pos to the next x or y side
        sideDistX = 0.
        sideDistY = 0.
        # ray length from one x/y side to the next
        deltaDistX = math.sqrt(1 + (rayDirY * rayDirY) / (rayDirX * rayDirX))
        if rayDirY == 0: 
            rayDirY = 0.00001
        deltaDistY = math.sqrt(1 + (rayDirX * rayDirX) / (rayDirY * rayDirY))
        perpWallDist = 0.
        # step direction (+/- 1)
        stepX = 0
        stepY = 0
        # wall hit
        hit = 0 # was there?
        side = 0 # NS or EW?
        # step & init side dist
        if rayDirX < 0:
            stepX = -1
            sideDistX = (rayPosX - mapX) * deltaDistX
        else:
            stepX = 1
            sideDistX = (mapX + 1.0 * rayPosX) * deltaDistX
        if rayDirY < 0:
            stepY = -1
            sideDistY = (rayPosY - mapY) * deltaDistY
        else:
            stepY = 1
            sideDistY = (mapY + 1.0 - rayPosY) * deltaDistY
        # DDA
        while hit == 0:
            if sideDistX < sideDistY:
                sideDistX += deltaDistX
                mapX += stepX
                side = 0
            else:
                sideDistY += deltaDistY
                mapY += stepY
                side = 1
            # check hit
            if(levelMaps[currLevel][mapY][mapX] > 0):
                hit = 1
        # distance projected on camera direction (fix fisheye)
        if side == 0:
            perpWallDist = abs((mapX - rayPosX + (1 - stepX) / 2) / rayDirX)
        else:
            perpWallDist = abs((mapY - rayPosY + (1 - stepY) / 2) / rayDirY)
        # append to zBuffer
        zBuffer.append(perpWallDist)
        # calculate strip height
        if perpWallDist == 0:
            perpWallDist = 0.000001
        lineHeight = abs(int(h / perpWallDist))
        # lo-hi coords
        drawStart = -lineHeight / 2 + h / 2
        drawEnd = lineHeight / 2 + h / 2
        # texture
        tex = currLevelTextures[levelMaps[currLevel][mapY][mapX] - 1]
        texWidth = tex.get_width()
        texHeight = tex.get_height()
        # wallX - where the wall was hit
        wallX = 0
        if side == 1:
            wallX = rayPosX + ((mapY - rayPosY + (1 - stepY) / 2) / rayDirY) * rayDirX
        else:
            wallX = rayPosY + ((mapX - rayPosX + (1 - stepX) / 2) / rayDirX) * rayDirY
        wallX -= math.floor((wallX))
        # x coord on tex
        texX = int(wallX * float(texWidth))
        if side == 0 and rayDirX > 0:
            texX = texWidth - texX - 1
        if side == 1 and rayDirY < 0:
            texX = texWidth - texX - 1
        # draw wall
        if lineHeight > 10000:
            lineHeight = 10000
            drawStart = -10000 / 2 + h / 2
        stripe = pygame.Surface((1, texHeight)) # get texture stripe
        stripe.blit(tex,(0,0),(texX,0,texX+1,texHeight))
        stripe = pygame.transform.scale(stripe, (1, lineHeight)) # scale to proper size
        DISPLAY.blit(stripe, ((w - x), drawStart)) # blit to screen
        """ # ray    rayN == x
        ray = {"x": playerPos["x"], "y": playerPos["y"]}
        rayCos = dirX / 64
        raySin = dirY / 64
        # wall checking
        wall = 0
        while wall == 0:
            ray["x"] += rayCos
            ray["y"] += raySin
            wall = levelMaps[currLevel][math.floor(ray["y"])][math.floor(ray["x"])]
        # calculate distance to wall
        distance = math.sqrt(math.pow(playerPos["x"] - ray["x"], 2) + math.pow(playerPos["y"] - ray["y"], 2))
        distance *= math.cos(rayAngle - playerAng) # fisheye effect fix
        zBuffer.append(distance)
        wallHeight = math.floor((h / 2) / distance)
        # textured walls
        texture = currLevelTextures[wall - 1]
        # get column within texture
        texturePosX = math.floor(texture.get_width() * (ray["x"] + ray["y"])) % int(texture.get_width())
        # extract texture strip
        stripe = pygame.Surface((1, texture.get_height()))
        stripe.blit(texture,(0,0),(texturePosX,0,texturePosX+1,texture.get_height()))
        # scale to proper height
        stripe = pygame.transform.scale(stripe,(4,2*wallHeight))
        # darken by distance - SLOW!!!
        darken = pygame.Surface(stripe.get_size())
        shade = 255 / 0.5 / distance
        if shade > 255:
            shade = 255
        darken.fill(pygame.Color((shade,shade,shade)))
        stripe.blit(darken,(0,0),special_flags=BLEND_RGB_MULT)
        # blit to screen
        DISPLAY.blit(stripe, (rayN*4, (h/2) - wallHeight))
        # increase ray angle by increment
        rayAngle += fovInc """
    # sort sprites
    levelSprites[currLevel].sort(key=cmp_to_key(sprite_compare))
    # draw sprites
    for spr in levelSprites[currLevel]:
        # sprite transform
        spriteX = spr[0] - playerPos["x"]
        spriteY = spr[1] - playerPos["y"]
        invDet = 1.0 / (planeX * dirY - planeY * dirX)
        transformX = invDet * (dirY * spriteX - dirX * spriteY)
        transformY = invDet * (-planeY * spriteX + planeX * spriteY)
        spriteSurfaceX = int((w / 2) * (1 + transformX / transformY))
        # sprite height
        spriteHeight = abs(int(h / transformY))
        drawStartY = -spriteHeight / 2 + h / 2
        drawEndY = spriteHeight / 2 + h / 2
        # sprite width
        spriteWidth = abs(int(h / transformY))
        drawStartX = int(-spriteWidth / 2 + spriteSurfaceX)
        drawEndX = int(spriteWidth / 2 + spriteSurfaceX)
        # draw sprite stripe by stripe
        if spriteHeight < 1000:
            for stripe in range(drawStartX, drawEndX):
                sprTex = currLevelSprites[spr[3]]
                texX = math.floor(256 * (stripe - (-spriteWidth / 2 + spriteSurfaceX)) * sprTex.get_width() / spriteWidth) / 256
                if(transformY > 0 and stripe > 0 and stripe < w and transformY < zBuffer[stripe]):
                    sprStrip = pygame.Surface((1, sprTex.get_height()))
                    sprStrip.blit(sprTex, (0,0), (texX,0,texX+1,sprTex.get_height()))
                    sprStrip = pygame.transform.scale(sprStrip, (1, 2 * spriteHeight))
                    sprStrip.set_colorkey(0xff00ff)
                    DISPLAY.blit(sprStrip, ((w -stripe), (h/2) - spriteHeight))

def updateGameVars(currLevel):
    global playerAng
    playerPos["x"] = levelPlayerData[currLevel]["x"]
    playerPos["y"] = levelPlayerData[currLevel]["y"]
    playerAng = levelPlayerData[currLevel]["a"]
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
    global playerAng, currLevel, playerSpeed, clock, drawMap, DISPLAY
    
    # game loop
    while True:
        DISPLAY.blit(levelBackground, (0,0))

        raycast()

        if drawMap:
            # draw map
            mapDx = 640 / levelMapDims[currLevel]["x"]
            mapDy = 480 / levelMapDims[currLevel]["y"]
            for mapY in range(0,levelMapDims[currLevel]["y"]):
                for mapX in range(0,levelMapDims[currLevel]["x"]):
                    if levelMaps[currLevel][mapY][mapX] > 0:
                        pygame.draw.rect(DISPLAY, 0x44aaff, Rect((mapX * mapDx) + 1, (mapY * mapDy) + 1, mapDx - 2, mapDy - 2))

            # draw player on map
            playerScreenX = playerPos["x"] * mapDx
            playerScreenY = playerPos["y"] * mapDy
            pygame.draw.rect(DISPLAY, 0xffaa44, Rect(playerScreenX-2,playerScreenY-2,5,5))
            pygame.draw.line(DISPLAY,0xffaa44,(playerScreenX, playerScreenY), (playerScreenX + 30*math.cos(playerAng), playerScreenY + 30*math.sin(playerAng)), 3)

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
                    newPosX = playerPos["x"] + playerSpeed * math.cos(playerAng)
                    newPosY = playerPos["y"] + playerSpeed * math.sin(playerAng)
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
            newPosX = playerPos["x"] + playerSpeed * math.cos(playerAng)
            newPosY = playerPos["y"] + playerSpeed * math.sin(playerAng)
            if levelMaps[currLevel][math.floor(newPosY)][math.floor(newPosX)] == 0:
                playerPos["x"] = newPosX
                playerPos["y"] = newPosY
        if keypressed["down"]:
            newPosX = playerPos["x"] - playerSpeed * math.cos(playerAng)
            newPosY = playerPos["y"] - playerSpeed * math.sin(playerAng)
            if levelMaps[currLevel][math.floor(newPosY)][math.floor(newPosX)] == 0:
                playerPos["x"] = newPosX
                playerPos["y"] = newPosY
        if keypressed["left"]:
            playerAng -= 0.1
            if playerAng < 0:
                playerAng = 2*math.pi + playerAng
        if keypressed["right"]:
            playerAng += 0.1
            if playerAng > 2*math.pi:
                playerAng = playerAng - 2*math.pi
        # limit framerate
        clock.tick(20)
