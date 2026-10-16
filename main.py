import math
import time

import pygame

pygame.init()


#system setup
screen_size = (750, 500)
target_fps = 60

print(pygame.display.get_desktop_sizes())

screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("super cool graphics testing")
clock = pygame.time.Clock()

running = True

system_font = pygame.font.SysFont("Times New Roman", 12)

#rendering variables
focal_length = 300
move_speed = 10
turn_speed = 1
target_transform = [0, 0, 0]
target_rotation = [0, 0, 0]

clipping_distance = 0.1
frame = 0
start_time = time.time()
depth_buffer = []
draw_order = []

cube_points = [
    [-50,-50,50],
    [50,-50,50],
    [50,50,50],
    [-50,50,50],
    [-50,-50,150],
    [50,-50,150],
    [50,50,150],
    [-50,50,150]
    ]
    
plane_points = [
    [-50,-50,0],
    [50,-50,0],
    [50,50,0],
    [-50,50,0]
]

triangle_points = [
    [-50,50,0],
    [0,-50,0],
    [50,50,0]
]

#point data, position, color
objects = [
    [triangle_points, (0,0,1000), (155,155,155), (45,0,0), (1,1,1)],
    [triangle_points, (100,0,1000), (155,155,155), (0,45,0), (1,1,1)],
    [triangle_points, (200,0,1000), (155,155,155), (0,0,45), (1,1,1)],

    [plane_points, (0,0,250), (155,0,0), (0,0,0), (1,1,1)],
    
    [plane_points, (100,0,250), (0,155,0), (0,0,0), (1,1,1)],
    [plane_points, (200,0,250), (0,0,155), (0,0,0), (1,1,1)],
    [plane_points, (0,0,500), (65,50,0), (0,0,0), (1,1,1)],
    [plane_points, (100,0,500), (50,175,80), (0,0,0), (1,1,1)],
    [plane_points, (200,0,500), (0,100,200), (0,0,0), (1,1,1)],
    [plane_points, (0,0,750), (155,155,155), (0,0,0), (1,1,1)],
    [plane_points, (100,0,750), (155,155,155), (0,0,0), (1,1,1)],
    [plane_points, (200,0,750), (155,155,155), (0,0,0), (1,1,1)],
     
    [plane_points, [0,-50,0], (155,155,155), (45,0,0), (5,5,1)]

]

def get_FPS():
    fps = int(frame / (time.time() - start_time))
    return fps
        
def on_key_hold(keys):
    ry = target_rotation[1] * (math.pi / 180)

    if keys[pygame.key.key_code('r')] == True:
        target_transform[1] += move_speed
    if keys[pygame.key.key_code('f')] == True:
        target_transform[1] -= move_speed
        
    if keys[pygame.key.key_code('q')] == True:
        target_rotation[1] += turn_speed
    if keys[pygame.key.key_code('e')] == True:
        target_rotation[1] -= turn_speed
        
    if keys[pygame.key.key_code('a')] == True:
        target_transform[0] += math.cos(ry) * move_speed
        target_transform[2] += math.sin(ry) * move_speed
    if keys[pygame.key.key_code('d')] == True:
        target_transform[0] -= math.cos(ry) * move_speed
        target_transform[2] -= math.sin(ry) * move_speed
        
    if keys[pygame.key.key_code('s')] == True:
        target_transform[0] -= math.sin(ry) * move_speed
        target_transform[2] += math.cos(ry) * move_speed
    if keys[pygame.key.key_code('w')] == True:
        target_transform[0] += math.sin(ry) * move_speed
        target_transform[2] -= math.cos(ry) * move_speed

def rotate_points(points, rotation):
    
    rotated_points = []
    rx = rotation[0] * (math.pi / 180)
    ry = rotation[1] * (math.pi / 180)
    rz = rotation[2] * (math.pi / 180)
    
    for x, y, z in points:
        #rotate x
        x1 = x
        y1 = y * math.cos(rx) - z * math.sin(rx)
        z1 = y * math.sin(rx) + z * math.cos(rx)

        #rotate y
        x2 = z1 * math.sin(ry) + x1 * math.cos(ry)
        y2 = y1
        z2 = z1 * math.cos(ry) - x1 * math.sin(ry)

        #rotate z
        x3 = x2 * math.cos(rz) - y2 * math.sin(rz)
        y3 = x2 * math.sin(rz) + y2 * math.cos(rz)
        z3 = z2
        
        rotated_points.append([x3, y3, z3])
        
    return rotated_points

def transform_points(points, transform):
    
    transformed_points = []
    tx, ty, tz = transform
    
    for point in points:
        x, y, z = point
        
        transformed_points.append(
            [
                x + tx,
                y + ty,
                z + tz
            ]
        )
        
    return transformed_points

def scale_points(points, scale):
    
    scaled_points = []
    sx, sy, sz = scale
    
    for point in points:
        x, y, z = point

        scaled_points.append(
            [
                x * sx,
                y * sy,
                z * sz
            ]
        )
        
    return scaled_points

def clip_points(points, distance):
    clipped_points = []
    previous = points[-1]

    for current in points:
        current_clipped = current[2] < distance
        previous_clipped = previous[2] < distance

        #calculate intersection point if two points cross clipping distance
        if current_clipped != previous_clipped:

            interpolant = (distance - previous[2]) / (current[2] - previous[2])

            intersection = [
                previous[0] + (current[0] - previous[0]) * interpolant,
                previous[1] + (current[1] - previous[1]) * interpolant,
                previous[2] + (current[2] - previous[2]) * interpolant
            ]

            clipped_points.append(intersection)

        if not current_clipped:
            clipped_points.append(current)

        previous = current

    return clipped_points

def project_points(points):
    
    flat_points = []
    for point in points:
        x, y, z = point

        fx = focal_length * (x / z) + (screen_size[0] / 2)
        fy = focal_length * (y / z) + (screen_size[1] / 2)

        flat_points.append([fx, fy])
    
    return flat_points
    
def render_object(objectID):
    points = objects[objectID][0]
    position = objects[objectID][1]
    color = objects[objectID][2]
    object_rotation = objects[objectID][3]
    scale = objects[objectID][4]

    #scales object
    scaled_points = scale_points(points, scale)
    
    #rotates the object around its own axis
    locally_rotated_points = rotate_points(scaled_points, object_rotation)

    #transform points to desired position
    transformed_points = transform_points(locally_rotated_points, [
        target_transform[0] + position[0],
        target_transform[1] + position[1],
        target_transform[2] + position[2]
        ])

    #rotate around camera
    rotated_points = rotate_points(transformed_points, target_rotation)

    #clip points near the camera
    clipped_points = clip_points(rotated_points, clipping_distance)

    if not clipped_points:
        return

    #project onto 2D screen
    flat_points = project_points(clipped_points)

    if not flat_points:
        return
        
    x_values = []
    y_values = []
    for point in flat_points:
        x_values.append(point[0])
        y_values.append(point[1])
            
    if not len(x_values) > 0:
        return

    z_values = []

    for point in clipped_points:
        z_values.append(point[2])
    
    
    #populate debth buffer with current object's id and max z value
    depth_buffer[objectID] = ([objectID, sum(z_values)/len(z_values)])
    
    if not max(x_values) <= 0 and not min(x_values) >= screen_size[0]:
        pygame.draw.polygon(
            screen,
            color,
            tuple(flat_points),
            width=0
        )

def on_step():
    global frame
    global draw_order

    #clear screen
    screen.fill((30, 30, 30)) 

    if frame == 0:
        initialize()

    #debug information
    screen.blit(system_font.render(f"FPS: {get_FPS()}", True, (255, 255, 255)), (20, 20))
    screen.blit(system_font.render(f"Frame: {frame}", True, (255, 255, 255)), (20, 40))
    screen.blit(system_font.render(f"Objects: {len(depth_buffer)}", True, (255, 255, 255)), (20, 60))
    screen.blit(system_font.render(f"Position: {int(target_transform[0]), int(target_transform[1]), int(target_transform[2])}", True, (255, 255, 255)), (20, 80))
    
    frame += 1
    
    draw_order = list(depth_buffer)
    
    draw_order.sort(key = lambda obj: obj[1], reverse=True)

    for obj in draw_order:
        render_object(obj[0])
    
def initialize():
    for i in range(len(objects)):
        depth_buffer.append([i, 100])
        render_object(i)
    
while running:
    on_step() #main loop

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    on_key_hold(pygame.key.get_pressed()) #get input

    pygame.display.flip() #render everything
    clock.tick(target_fps) #60 fps