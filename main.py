import math
import time

import pygame

pygame.init()


#system setup
screen_size = (750, 500)
desired_fps = 60

print(pygame.display.get_desktop_sizes())

screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("super cool graphics testing")
clock = pygame.time.Clock()

running = True

system_font = pygame.font.SysFont("Times New Roman", 12)

#rendering variables
focalLength = 300
moveSpeed = 10
targetTransform = [0, 0, 0]
targetRotation = [0, 0, 0]
clippingDistance = 50
frame = 0
doOpacity = False
startTime = time.time()
depthBuffer = []
drawOrder = []

cubePoints = [
    [-50,-50,50],
    [50,-50,50],
    [50,50,50],
    [-50,50,50],
    [-50,-50,150],
    [50,-50,150],
    [50,50,150],
    [-50,50,150]
    ]
    
planePoints = [
    [-50,-50,0],
    [50,-50,0],
    [50,50,0],
    [-50,50,0]
]

trianglePoints = [
    [-50,50,0],
    [0,-50,0],
    [50,50,0],
    [-50,50,0]
]

#point data, position, color
objects = [
    [trianglePoints, [0,0,1000], (155,155,155)],

    [planePoints, [0,0,250], (155,155,155)],
    [planePoints, [100,0,250], (5,155,155)],
    [planePoints, [200,0,250], (155,155,155)],
    [planePoints, [0,0,500], (155,200,155)],
    [planePoints, [100,0,500], (155,155,155)],
    [planePoints, [200,0,500], (155,55,155)],
    [planePoints, [0,0,750], (155,155,155)],
    [planePoints, [100,0,750], (155,155,5)],
    [planePoints, [200,0,750], (155,155,155)]
]

def get_FPS():
    fps = int(frame / (time.time() - startTime))
    return fps
        
def onKeyHold(keys):
    ry = targetRotation[1]

    if keys[pygame.key.key_code('r')] == True:
        targetTransform[1] += moveSpeed
    if keys[pygame.key.key_code('f')] == True:
        targetTransform[1] -= moveSpeed
        
    if keys[pygame.key.key_code('q')] == True:
        targetRotation[1] += 0.01
    if keys[pygame.key.key_code('e')] == True:
        targetRotation[1] -= 0.01
        
    if keys[pygame.key.key_code('a')] == True:
        targetTransform[0] += math.cos(ry) * moveSpeed
        targetTransform[2] += math.sin(ry) * moveSpeed
    if keys[pygame.key.key_code('d')] == True:
        targetTransform[0] -= math.cos(ry) * moveSpeed
        targetTransform[2] -= math.sin(ry) * moveSpeed
        
    if keys[pygame.key.key_code('s')] == True:
        targetTransform[0] -= math.sin(ry) * moveSpeed
        targetTransform[2] += math.cos(ry) * moveSpeed
    if keys[pygame.key.key_code('w')] == True:
        targetTransform[0] += math.sin(ry) * moveSpeed
        targetTransform[2] -= math.cos(ry) * moveSpeed

def rotatePoints(points, rotation):
    
    rotatedPoints = []
    #rx = rotation[0]
    ry = rotation[1]
    #rz = rotation[2]
    
    for point in points:
        x = point[0]
        y = point[1]
        z = point[2]
        
        rotatedPoints.append(
            [
                z * math.sin(ry) + x * math.cos(ry),
                y,
                z * math.cos(ry) - x * math.sin(ry)
            ]
        )
        
    return rotatedPoints

def transformPoints(points, transform):
    
    transformedPoints = []
    tx = transform[0]
    ty = transform[1]
    tz = transform[2]
    
    for point in points:
        x = point[0]
        y = point[1]
        z = point[2]
        
        transformedPoints.append(
            [
                x + tx,
                y + ty,
                z + tz
            ]
        )
        
    return transformedPoints

def projectPoints(points, focal):
    
    flatPoints = []
    for point in points:
        if point[2] < 1:
            continue
        
        x = point[0]
        y = point[1]
        z = point[2]
        flatPoints.append([focal * (x / z) + (screen_size[0] / 2), focal * (y / z) + (screen_size[1] / 2)])
    
    return flatPoints
    
def renderObject(objectID):
    points = objects[objectID][0]
    position = objects[objectID][1]
    color = objects[objectID][2]
    
    transformedPoints = transformPoints(points, [
        targetTransform[0] + position[0],
        targetTransform[1] + position[1],
        targetTransform[2] + position[2]
        ])
    
    rotatedPoints = rotatePoints(transformedPoints, targetRotation)
    
    flatPoints = projectPoints(rotatedPoints, focalLength)
    
    if len(flatPoints) < 4:
        return
    
    zValues = []
    for point in rotatedPoints:
        zValues.append(point[2])
    
    
    #populate debth buffer with current object's id and max z value
    depthBuffer[objectID] = ([objectID, max(zValues)])
        
        
    xValues = []
    yValues = []
    for point in flatPoints:
        xValues.append(point[0])
        yValues.append(point[1])
        
    #opacity = abs(min(100, (min(zValues)-clippingDistance))) if doOpacity else 100
    
    if not (max(xValues) <= 0 or min(xValues) >= screen_size[0]):
        for i in range(0, len(flatPoints), 4):

            if len(flatPoints) % 4 == 0:
                pygame.draw.polygon(
                    screen,
                    color,
                    [
                    (flatPoints[i][0],
                    flatPoints[i][1]),

                    (flatPoints[i + 1][0],
                    flatPoints[i + 1][1]),

                    (flatPoints[i + 2][0],
                    flatPoints[i + 2][1]),

                    (flatPoints[i + 3][0],
                    flatPoints[i + 3][1])
                    ],
                    width=0
                    )

            if len(flatPoints) % 3 == 0:
                pygame.draw.polygon(
                    screen,
                    color,
                    [
                    (flatPoints[i][0],
                    flatPoints[i][1]),

                    (flatPoints[i + 1][0],
                    flatPoints[i + 1][1]),

                    (flatPoints[i + 2][0],
                    flatPoints[i + 2][1])
                    ],
                    width=0
                    )

def sortKey(obj):
    return obj[1]

def onStep():
    global frame
    global drawOrder

    if frame == 0:
        initialize()

    data_string = f"FPS: {get_FPS()}\nFRAME: {frame}"

    screen.blit(system_font.render(data_string, True, (255, 255, 255)), (20, 20))
    
    frame += 1
    
    drawOrder = list(depthBuffer)
    
    drawOrder.sort(key=sortKey, reverse=True)

    for obj in drawOrder:
        renderObject(obj[0])
    
def initialize():
    
    for i in range(len(objects)):
        depthBuffer.append([i, 100])
        renderObject(i)
    
while running:


    screen.fill((30, 30, 30)) #clear screen

    onStep() #main loop

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    onKeyHold(pygame.key.get_pressed()) #get input

    pygame.display.flip() #render everything
    clock.tick(desired_fps) #60 fps