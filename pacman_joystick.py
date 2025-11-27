import threading, serial, time, sys, math, random
import pygame

SERIAL_PORT = "COM11" #change to your port
BAUD = 9600
DEADZONE = 80  #joystick deadzone around centre
ANALOG_MIN = 0
ANALOG_MAX = 1023
SPEED = 120
BUTTON_SPEED_MULT = 1.6 #multiplier while button pressed
FPS = 60

#shared joystick state
joy = {"x": 512, "y": 512, "button": 1}
running = True

def serial_thread(port, baud):
    global joy, running
    try:
        ser = serial.Serial(port, baud, timeout=1)
    except Exception as e:
        print("Could not open serial:", e)
        print("Exiting.")
        running = False
        return

    time.sleep(1.0)
    ser.reset_input_buffer()

    while running:
        try:
            line = ser.readline().decode(errors='ignore').strip()
            if not line:
                continue
            parts = line.split(',')
            if len(parts) < 3:
                continue
            x = int(parts[0])
            y = int(parts[1])
            b = int(parts[2])
            joy["x"] = max(ANALOG_MIN, min(ANALOG_MAX, x))
            joy["y"] = max(ANALOG_MIN, min(ANALOG_MAX, y))
            joy["button"] = b
        except Exception:
            continue
    ser.close()

def axis_value(a):
    mid = (ANALOG_MAX + ANALOG_MIN) / 2.0
    v = (a - mid) / (mid)  # -1 .. 1
    if abs(v) < (DEADZONE / mid):
        return 0.0
    return max(-1.0, min(1.0, v))

#using pygame
pygame.init()
CELL = 24
COLS = 28
ROWS = 31
W = COLS * CELL
H = ROWS * CELL
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
pygame.display.set_caption("Pac-Man (Arduino Joystick)")

game_map = [[0 for _ in range(COLS)] for __ in range(ROWS)]

#walls border
for r in range(ROWS):
    for c in range(COLS):
        if r == 0 or r == ROWS-1 or c == 0 or c == COLS-1:
            game_map[r][c] = 1
#interior walls
for r in range(4, ROWS-4, 2):
    for c in range(2, COLS-2):
        if (c % 4) != 0:
            game_map[r][c] = 1

#pellets
for r in range(ROWS):
    for c in range(COLS):
        if game_map[r][c] == 0:
            game_map[r][c] = 2

#clear spawn zone
for r in range(ROWS-4, ROWS-1):
    for c in range(2, 6):
        game_map[r][c] = 0

# Player
player_pos = [CELL*2 + CELL//2, CELL*(ROWS-3) + CELL//2]
score = 0

# Ghosts
ghosts = []
for i in range(3):
    gx = CELL*(COLS//2 + i) + CELL//2
    gy = CELL*(ROWS//2) + CELL//2
    ghosts.append({"pos":[gx,gy], "dir":[random.choice([-1,0,1]), random.choice([-1,0,1])], "speed":80})

font = pygame.font.SysFont(None, 24)

def is_wall(px, py):
    c = int(px // CELL)
    r = int(py // CELL)
    if r < 0 or r >= ROWS or c < 0 or c >= COLS:
        return True
    return game_map[r][c] == 1

def try_move(px, py, dx, dy, dt, speed):
    nx = px + dx * speed * dt
    ny = py + dy * speed * dt

    radius = CELL * 0.4
    corners = [(nx+radius, ny+radius), (nx-radius, ny+radius),
               (nx+radius, ny-radius), (nx-radius, ny-radius)]
    blocked = False
    for (cx, cy) in corners:
        if is_wall(cx, cy):
            blocked = True
            break
    if not blocked:
        return nx, ny

    nx2 = px + dx * speed * dt
    ny2 = py
    blocked_x = any(is_wall(cx, cy) for (cx, cy) in
                    [(nx2+radius, ny2+radius), (nx2-radius, ny2+radius),
                     (nx2+radius, ny2-radius), (nx2-radius, ny2-radius)])
    if not blocked_x:
        return nx2, ny2

    nx3 = px
    ny3 = py + dy * speed * dt
    blocked_y = any(is_wall(cx, cy) for (cx, cy) in
                    [(nx3+radius, ny3+radius), (nx3-radius, ny3+radius),
                     (nx3+radius, ny3-radius), (nx3-radius, ny3-radius)])
    if not blocked_y:
        return nx3, ny3
    return px, py

#start serial thread
t = threading.Thread(target=serial_thread, args=(SERIAL_PORT, BAUD), daemon=True)
t.start()

while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ax = axis_value(joy["x"])
    ay = axis_value(joy["y"])
    btn = (joy["button"] == 0)

    if abs(ax) > abs(ay):
        dx = math.copysign(1, ax) if abs(ax) > 0 else 0
        dy = 0
    else:
        dy = math.copysign(1, ay) if abs(ay) > 0 else 0
        dx = 0

    move_speed = SPEED * (BUTTON_SPEED_MULT if btn else 1.0)
    player_pos[0], player_pos[1] = try_move(player_pos[0], player_pos[1], dx, dy, dt, move_speed)

    pr = int(player_pos[1] // CELL)
    pc = int(player_pos[0] // CELL)
    if 0 <= pr < ROWS and 0 <= pc < COLS and game_map[pr][pc] == 2:
        game_map[pr][pc] = 0
        score += 10

    for g in ghosts:
        if random.random() < 0.02:
            dirs = [(1,0),(-1,0),(0,1),(0,-1)]
            random.shuffle(dirs)
            chosen = (0,0)
            for d in dirs:
                nx = g["pos"][0] + d[0] * CELL
                ny = g["pos"][1] + d[1] * CELL
                if not is_wall(nx, ny):
                    chosen = d
                    break
            g["dir"] = [chosen[0], chosen[1]]

        gnx = g["pos"][0] + g["dir"][0] * g["speed"] * dt
        gny = g["pos"][1] + g["dir"][1] * g["speed"] * dt

        if is_wall(gnx, gny):
            g["dir"][0] *= -1
            g["dir"][1] *= -1
        else:
            g["pos"][0] = gnx
            g["pos"][1] = gny

        dist = math.hypot(player_pos[0]-g["pos"][0], player_pos[1]-g["pos"][1])
        if dist < CELL * 0.7:
            player_pos = [CELL*2 + CELL//2, CELL*(ROWS-3) + CELL//2]
            score = max(0, score - 50)

    #frame
    screen.fill((0,0,0))
    for r in range(ROWS):
        for c in range(COLS):
            x = c * CELL
            y = r * CELL
            if game_map[r][c] == 1:
                pygame.draw.rect(screen, (33,33,150), (x, y, CELL, CELL))
            elif game_map[r][c] == 2:
                pygame.draw.circle(screen, (255, 200, 0), (x + CELL//2, y + CELL//2), 3)

    #ghosts
    for g in ghosts:
        pygame.draw.circle(screen, (255,0,0),
                           (int(g["pos"][0]), int(g["pos"][1])), CELL//2 - 2)

    #pacman
    px, py = int(player_pos[0]), int(player_pos[1])
    mouth = 0.25 if dx != 0 or dy != 0 else 0.05
    ang = 0
    if dx > 0: ang = 0
    elif dx < 0: ang = math.pi
    elif dy < 0: ang = -math.pi/2
    elif dy > 0: ang = math.pi/2

    r = CELL//2 - 2
    start = ang + mouth*math.pi
    end = ang - mouth*math.pi
    points = [(px,py)]
    steps = 16
    for i in range(steps+1):
        t = start + (end - start) * (i/steps)
        points.append((px + math.cos(t)*r, py + math.sin(t)*r))
    pygame.draw.polygon(screen, (255,255,0), points)

    hud = font.render(f"Score: {score}  Joystick: x={joy['x']} y={joy['y']} btn={joy['button']}",
                      True, (255,255,255))
    screen.blit(hud, (6,6))

    pygame.display.flip()

running = False
pygame.quit()
sys.exit()

