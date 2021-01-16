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

score = 0
lives = 3

inv_timer = 0
isPlayerHit = False

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
        [1,0,2,3,0,2,0,1,2,6,2,1],
        [4,0,0,0,0,0,0,1,0,0,0,1],
        [1,0,2,0,0,2,0,1,0,0,0,1],
        [1,0,2,2,2,2,0,1,0,0,0,1],
        [1,0,0,0,0,0,0,1,0,0,0,1],
        [1,1,1,0,0,1,1,1,1,1,0,1],
        [1,0,0,0,0,0,0,1,0,0,0,1],
        [4,0,3,2,2,3,0,7,0,0,0,4],
        [1,0,0,0,0,0,0,1,0,0,0,1],
        [1,1,1,1,1,1,1,1,1,1,1,1]
    ],
    [
        [1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0],
        [1,0,0,0,1,0,0,0,0,0,0,1,0,0,0,1,1,1,1,1],
        [1,0,0,0,1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,1],
        [1,0,0,0,1,0,0,0,0,0,0,1,1,1,1,1,1,2,1,1],
        [1,0,0,0,1,1,1,0,0,1,1,1,0,0,0,1,0,0,0,1],
        [1,1,0,1,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
        [1,0,0,0,1,0,0,0,0,0,0,1,1,1,1,1,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
        [1,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ]
]
levelMapDims = [
    {"x":12, "y":12},
    {"x":20, "y":10}
]
levelPlayerData = [
    {"x":9.5, "y":9.5, "aX":-1.0001, "aY":0.0001, "pX":0, "pY":0.66},
    {"x":2.5, "y":2.5, "aX":0.0001, "aY":1.0001, "pX":0.66, "pY":0}
]
levelTextures = [
    [
        "grf/brickWall.png", "grf/bookcase.png", "grf/potionShelf.png", "grf/doorOnBrickWall.png", "grf/stairsUp.png", "grf/bookcase_hDoor.png", "grf/door_red.png"
    ],
    [
        "grf/brickWall.png", "grf/door_red.png"
    ]
]
levelDoors = [
    [
        [9, 2, "hidden"], # x y type                                 - types - hidden = regular or hidden door, red, yellow, blue, exit
        [7, 9, "red"],
        [9, 0, "exit"]
    ],
    [
        [17,3, "red"]
    ]
]
levelSprites = [
    [
        [4, 4, "furn", 0, False],  # x y type texture taken         - types - furn = furniture, keyr = red key, keyb = blue key, keyy = yellow key, gold = money
        [8.5, 5, "furn", 1, False],
        [1.5, 1.5, "gold", 2, False],
        [8.5, 1.5, "gold", 2, False],
        [10.5, 1.5, "gold", 2, False],
        [4.5, 2.5, "gold", 2, False],
        [1.5, 10.5, "gold", 2, False],
        [8.5, 6.5, "keyr", 3, False]
    ], 
    [
        [18.5, 8.5, "furn", 0, False]
    ]
]
spriteTextures = [
    [
        "grf/sprites/chair.png",
        "grf/sprites/table.png",
        "grf/sprites/moneyBag.png",
        "grf/sprites/keyr.png"
    ],
    [
        "grf/sprites/table.png"
    ]
]
levelObstacles = [
    [],
    [
        [1.5, 4.5, 1.5, 4.5, 3.5, 4.5, 0.1, True] # curr x y, start x y, end x y, speed, toEnd
    ]
]

levelBackground = pygame.image.load("grf/levelBackground.png")
obstacle = pygame.image.load("grf/sprites/magicObstacle.png")

currLevelTextures = []
currLevelSprites = []
currLevelInventory = {"keyr": False, "keyy": False, "keyb": False}

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
                dark = pygame.Surface(strip.get_size()).convert_alpha()
                dark.fill((0,0,0,127))
                strip.blit(dark, (0,0))
            # scale strip
            strip = pygame.transform.scale(strip, (4, lineHeight))
            # blit to screen
            DISPLAY.blit(strip, (x*4, drawStartY))
    drawSprites(zBuffer)
    drawObstacles(zBuffer)
    
# handles drawing sprites
def drawSprites(zBuffer):
    # sort sprites
    levelSprites[currLevel].sort(key=cmp_to_key(sprite_compare))
    # draw sprites
    for spr in levelSprites[currLevel]:
        if not spr[4]:
            # get texture
            sprTex = currLevelSprites[spr[3]]
            renderSprite(spr, sprTex, zBuffer)

# handles drawing sprites
def drawObstacles(zBuffer):
    # sort sprites
    levelObstacles[currLevel].sort(key=cmp_to_key(sprite_compare))
    # draw sprites
    for spr in levelObstacles[currLevel]:
        # get texture
        sprTex = obstacle
        renderSprite(spr, sprTex, zBuffer)
        
    
def renderSprite(spr, sprTex, zBuffer):
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
    drawEndX = int(spriteWidth / 2 + spriteScreenX)
    # draw by strips
    for stripX in range(drawStartX, drawEndX):
        # texture x coord
        texX = math.floor(256 * (stripX - (-spriteWidth / 2 + spriteScreenX)) * sprTex.get_width() / spriteWidth) / 256
        if texX < 0: texX = 0                                           # fix black stripes
        if texX >= sprTex.get_width(): texX = sprTex.get_width() - 1
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

# if player is within certain distance of a sprite marked as "gold", "keyr", "keyy", "keyb", they will pick it up
# gold adds to score
# keys are for opening coloured doors
def getPickups():
    global score
    for spr in levelSprites[currLevel]:
        if spr[2] == "gold" or spr[2] == "keyr" or spr[2] == "keyy" or spr[2] == "keyb":
            spriteX = spr[0] - playerPos["x"]
            spriteY = spr[1] - playerPos["y"]
            distToPlayer = math.sqrt(spriteX ** 2 + spriteY ** 2)
            if distToPlayer < 0.3:
                if spr[2] == "gold" and spr[4] == False: 
                    score += 10
                    print(score)
                    spr[4] = True
                if spr[2] == "keyr" and spr[4] == False: 
                    currLevelInventory["keyr"] = True
                    print("Found red key")
                    spr[4] = True
                if spr[2] == "keyy" and spr[4] == False: 
                    currLevelInventory["keyy"] = True
                    print("Found yellow key")
                    spr[4] = True
                if spr[2] == "keyb" and spr[4] == False: 
                    currLevelInventory["keyb"] = True
                    print("Found blue key")
                    spr[4] = True

# if level timer runs out, game over
def outOfTime():
    pass

# if colliding with level exit, transition to the next level with blank screen for one second
# if last level, transition to win screen & back to menu
def nextLevel():
    global currLevel
    currLevel += 1
    updateGameVars(currLevel)

# if colliding with a door, player can open it if certain conditions are met
def openDoor():
    newPosX = playerPos["x"] + 0.5 * playerDir["x"]
    newPosY = playerPos["y"] + 0.5 * playerDir["y"]
    for door in levelDoors[currLevel]:
        if (door[0] == math.floor(newPosX)) and (door[1] == math.floor(newPosY)):
            if (door[2] == "hidden") or (door[2] == "red" and currLevelInventory["keyr"]) or (door[2] == "yellow" and currLevelInventory["keyy"]) or (door[2] == "blue" and currLevelInventory["keyb"]):
                levelMaps[currLevel][door[1]][door[0]] = 0
            if (door[2] == "exit"):
                nextLevel()

# move obstacles
def moveObstacles():
    for obs in levelObstacles[currLevel]:
        # from start to end
        if obs[7]:
            if obs[2] == obs[4]: stepX = 0
            else: stepX = obs[6] / (obs[4] - obs[2])
            if obs[3] == obs[5]: stepY = 0
            else: stepY = obs[6] / (obs[5] - obs[3])
            if round(obs[0], 2) != obs[4]: obs[0] += stepX
            if round(obs[1], 2) != obs[5]: obs[1] += stepY
            if round(obs[0], 2) == obs[4] and round(obs[1], 2) == obs[5]: obs[7] = False
        # from end to start
        else:
            if obs[2] == obs[4]: stepX = 0
            else: stepX = obs[6] / (obs[2] - obs[4])
            if obs[3] == obs[5]: stepY = 0
            else: stepY = obs[6] / (obs[3] - obs[5])
            if round(obs[0], 2) != obs[2]: obs[0] += stepX
            if round(obs[1], 2) != obs[3]: obs[1] += stepY
            if round(obs[0], 2) == obs[2] and round(obs[1], 2) == obs[3]: obs[7] = True

# obstacle collision - take a hit, lose a life
def collideWithObstacle():
    global isPlayerHit, lives, inv_timer
    for obs in levelObstacles[currLevel]:
        # distance from player
        dist = math.sqrt((obs[0] - playerPos["x"]) ** 2 + (obs[1] - playerPos["y"]) ** 2)
        if dist < 0.3:
            if not isPlayerHit:
                isPlayerHit = True
                print("Previous lives:", lives)
                lives -= 1
                print("New lives:", lives)
                inv_timer = 30

def updateGameVars(currLevel):
    global currLevelTextures, currLevelSprites, currLevelInventory, planeX, planeY
    playerPos["x"] = levelPlayerData[currLevel]["x"]
    playerPos["y"] = levelPlayerData[currLevel]["y"]
    playerDir["x"] = levelPlayerData[currLevel]["aX"]
    playerDir["y"] = levelPlayerData[currLevel]["aY"]
    planeY = levelPlayerData[currLevel]["pY"]
    planeX = levelPlayerData[currLevel]["pX"]
    currLevelInventory = {"keyr": False, "keyy": False, "keyb": False}
    currLevelTextures = []
    for tex in levelTextures[currLevel]:
        currLevelTextures.append((pygame.image.load(tex)).convert())
    currLevelSprites = []
    for spr in spriteTextures[currLevel]:
        currLevelSprites.append((pygame.image.load(spr)).convert())

def initLevelLoop(surface):
    global currLevel, levelBackground, DISPLAY, obstacle
    DISPLAY = surface
    currLevel = 0
    levelBackground = levelBackground.convert()
    obstacle = obstacle.convert()
    updateGameVars(currLevel)
    levelLoop()

def levelLoop():
    global currLevel, playerSpeed, clock, drawMap, DISPLAY, planeX, planeY, isPlayerHit, inv_timer
    
    # game loop
    while True:
        DISPLAY.blit(levelBackground, (0,0))

        raycast()

        if drawMap:
            automap = pygame.Surface((640, 480))
            automap.fill(0xff00ff)
            automap.set_colorkey(0xff00ff)
            # draw map
            mapDx = 640 / levelMapDims[currLevel]["x"]
            mapDy = 480 / levelMapDims[currLevel]["y"]
            for mapY in range(0,levelMapDims[currLevel]["y"]):
                for mapX in range(0,levelMapDims[currLevel]["x"]):
                    if levelMaps[currLevel][mapY][mapX] > 0:
                        pygame.draw.rect(automap, 0x44aaff, Rect((mapX * mapDx) + 1, (mapY * mapDy) + 1, mapDx - 2, mapDy - 2))
            # draw player on map
            playerScreenX = playerPos["x"] * mapDx
            playerScreenY = playerPos["y"] * mapDy
            pygame.draw.rect(automap, 0xffaa44, Rect(playerScreenX-2,playerScreenY-2,5,5))
            pygame.draw.line(automap,0xffaa44,(playerScreenX, playerScreenY), (playerScreenX + 30*playerDir["x"], playerScreenY + 30*playerDir["y"]), 3)
            # blit to screen
            automap = pygame.transform.flip(automap, True, False)
            DISPLAY.blit(automap, (0,0))

        pygame.display.update()

        getPickups()
        moveObstacles()
        collideWithObstacle()

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
                    openDoor()
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
        # invincibility timer
        if inv_timer > 0:
            inv_timer -= 1
        else:
            isPlayerHit = False
        # limit framerate
        clock.tick(20)
