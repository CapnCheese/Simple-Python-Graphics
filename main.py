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
turnSpeed = 1
targetTransform = [0, 0, 0]
targetRotation = [0, 0, 0]

clippingDistance = 1
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
    [trianglePoints, (0,0,1000), (155,155,155), (45,0,0), (1,1,1)],
    [trianglePoints, (100,0,1000), (155,155,155), (0,45,0), (1,1,1)],
    [trianglePoints, (200,0,1000), (155,155,155), (0,0,45), (1,1,1)],

    [planePoints, (0,0,250), (155,0,0), (0,0,0), (1,1,1)],
    
    [planePoints, (100,0,250), (0,155,0), (0,0,0), (1,1,1)],
    [planePoints, (200,0,250), (0,0,155), (0,0,0), (1,1,1)],
    [planePoints, (0,0,500), (65,50,0), (0,0,0), (1,1,1)],
    [planePoints, (100,0,500), (50,175,80), (0,0,0), (1,1,1)],
    [planePoints, (200,0,500), (0,100,200), (0,0,0), (1,1,1)],
    [planePoints, (0,0,750), (155,155,155), (0,0,0), (1,1,1)],
    [planePoints, (100,0,750), (155,155,155), (0,0,0), (1,1,1)],
    [planePoints, (200,0,750), (155,155,155), (0,0,0), (1,1,1)],
     
    [planePoints, [0,-50,0], (155,155,155), (45,0,0), (5,5,1)]

]

def get_FPS():
    fps = int(frame / (time.time() - startTime))
    return fps
        
def onKeyHold(keys):
    ry = targetRotation[1] * (math.pi / 180)

    if keys[pygame.key.key_code('r')] == True:
        targetTransform[1] += moveSpeed
    if keys[pygame.key.key_code('f')] == True:
        targetTransform[1] -= moveSpeed
        
    if keys[pygame.key.key_code('q')] == True:
        targetRotation[1] += turnSpeed
    if keys[pygame.key.key_code('e')] == True:
        targetRotation[1] -= turnSpeed
        
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
    rx = rotation[0] * (math.pi / 180)
    ry = rotation[1] * (math.pi / 180)
    rz = rotation[2] * (math.pi / 180)
    
    for x, y, z in points:
        x1 = x
        y1 = y * math.cos(rx) - z * math.sin(rx)
        z1 = y * math.sin(rx) + z * math.cos(rx)

        x2 = z1 * math.sin(ry) + x1 * math.cos(ry)
        y2 = y1
        z2 = z1 * math.cos(ry) - x1 * math.sin(ry)



        x3 = x2 * math.cos(rz) - y2 * math.sin(rz)
        y3 = x2 * math.sin(rz) + y2 * math.cos(rz)
        z3 = z2
        
        rotatedPoints.append([x3, y3, z3])
        
    return rotatedPoints

def transformPoints(points, transform):
    
    transformedPoints = []
    tx, ty, tz = transform
    
    for point in points:
        x, y, z = point
        
        transformedPoints.append(
            [
                x + tx,
                y + ty,
                z + tz
            ]
        )
        
    return transformedPoints

def scalePoints(points, scale):
    
    scaledPoints = []
    sx, sy, sz = scale
    
    for point in points:
        x, y, z = point

        scaledPoints.append(
            [
                x * sx,
                y * sy,
                z * sz
            ]
        )
        
    return scaledPoints

def projectPoints(points):
    
    flatPoints = []
    for point in points:
        x, y, z = point

        if z <= clippingDistance:
            return

        fx = focalLength * (x / z) + (screen_size[0] / 2)
        fy = focalLength * (y / z) + (screen_size[1] / 2)

        flatPoints.append([fx, fy])
    
    return flatPoints
    
def renderObject(objectID):
    points = objects[objectID][0]
    position = objects[objectID][1]
    color = objects[objectID][2]
    objectRotation = objects[objectID][3]
    scale = objects[objectID][4]

    #scales object
    scaledPoints = scalePoints(points, scale)
    
    #rotates the object around its own axis
    locallyRotatedPoints = rotatePoints(scaledPoints, objectRotation)

    #transform points to desired position
    transformedPoints = transformPoints(locallyRotatedPoints, [
        targetTransform[0] + position[0],
        targetTransform[1] + position[1],
        targetTransform[2] + position[2]
        ])

    #rotate around camera
    rotatedPoints = rotatePoints(transformedPoints, targetRotation)
    
    #project onto 2D screen
    flatPoints = projectPoints(rotatedPoints)

    if flatPoints is None:
        return
        
    xValues = []
    yValues = []
    for point in flatPoints:
        xValues.append(point[0])
        yValues.append(point[1])
        
    #opacity = abs(min(100, (min(zValues)-clippingDistance))) if doOpacity else 100
    
    if not len(xValues) > 0:
        return

    zValues = []

    for point in rotatedPoints:
        zValues.append(point[2])
    
    
    #populate debth buffer with current object's id and max z value
    depthBuffer[objectID] = ([objectID, sum(zValues)/len(zValues)])
    
    if not max(xValues) <= -100 and not min(xValues) >= screen_size[0] + 100:
        for i in range(0, len(flatPoints), 4):

            #draw square
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

            #draw triangle
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

def onStep():
    global frame
    global drawOrder

    #clear screen
    screen.fill((30, 30, 30)) 

    if frame == 0:
        initialize()

    #debug information
    screen.blit(system_font.render(f"FPS: {get_FPS()}", True, (255, 255, 255)), (20, 20))
    screen.blit(system_font.render(f"Frame: {frame}", True, (255, 255, 255)), (20, 40))
    screen.blit(system_font.render(f"Objects: {len(depthBuffer)}", True, (255, 255, 255)), (20, 60))
    screen.blit(system_font.render(f"Position: {int(targetTransform[0]), int(targetTransform[1]), int(targetTransform[2])}", True, (255, 255, 255)), (20, 80))
    
    frame += 1
    
    drawOrder = list(depthBuffer)
    
    drawOrder.sort(key = lambda obj: obj[1], reverse=True)

    for obj in drawOrder:
        renderObject(obj[0])
    
def initialize():
    for i in range(len(objects)):
        depthBuffer.append([i, 100])
        renderObject(i)
    
while running:
    onStep() #main loop

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    onKeyHold(pygame.key.get_pressed()) #get input

    pygame.display.flip() #render everything
    clock.tick(desired_fps) #60 fps