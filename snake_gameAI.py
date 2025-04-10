import tkinter as tk
import random
import heapq

# --- Constants ---
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
ROWS, COLS = HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE
SPEED = 100

# --- Game Variables ---
snake = [(5, 5)]
food = (10, 10)
direction = 'Right'
running = True
score = 0
mode = 'User'
path = []
blink_state = True
theme = 'light'

# --- Main Window ---
window = tk.Tk()
window.title("Smart Snake Game AI")
canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT)
canvas.pack()

# --- Top Frame for Controls ---
top_frame = tk.Frame(window)
top_frame.pack(pady=5, fill=tk.X)

# LEFT Controls (Mode + Switch)
left_frame = tk.Frame(top_frame)
left_frame.pack(side=tk.LEFT, padx=20)

mode_label = tk.Label(left_frame, text=f"Mode: {mode}", font=("Arial", 12))
mode_label.pack()

def switch_mode():
    global mode, path
    mode = 'AI' if mode == 'User' else 'User'
    path = []
    mode_label.config(text=f"Mode: {mode}")

mode_button = tk.Button(left_frame, text="Switch Mode", command=switch_mode, bg="lightblue")
mode_button.pack(pady=2)

# RIGHT Controls (Swapped: Restart first, then Theme)
right_frame = tk.Frame(top_frame)
right_frame.pack(side=tk.RIGHT, padx=20)

def restart_game():
    global snake, food, direction, running, score, mode, path
    snake = [(5, 5)]
    food = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
    direction = 'Right'
    running = True
    score = 0
    mode = 'User'
    path = []
    mode_label.config(text="Mode: User")
    draw()
    move()

restart_button = tk.Button(right_frame, text="Restart", command=restart_game, bg="lightgreen")
restart_button.pack(pady=2)

def toggle_theme():
    global theme
    theme = 'dark' if theme == 'light' else 'light'
    draw()

theme_button = tk.Button(right_frame, text="Dark Theme", command=toggle_theme, bg="lightgray")
theme_button.pack(pady=2)

# --- Drawing Functions ---
def draw_cell(x, y, color, oval=False, scale=1.0):
    x1, y1 = x * CELL_SIZE, y * CELL_SIZE
    x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
    if scale < 1.0:
        dx = (1 - scale) * CELL_SIZE / 2
        dy = (1 - scale) * CELL_SIZE / 2
        x1 += dx
        y1 += dy
        x2 -= dx
        y2 -= dy
    if oval:
        canvas.create_oval(x1+2, y1+2, x2-2, y2-2, fill=color, outline=color)
    else:
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")

def draw():
    canvas.delete("all")

    # Background
    for y in range(ROWS):
        color = "#2e2e2e" if theme == 'dark' else "#f0f8ff" if y % 2 == 0 else "#e6f7ff"
        if theme == 'light' and y % 2 == 1:
            color = "#e6f7ff"
        elif theme == 'light':
            color = "#f0f8ff"
        canvas.create_rectangle(0, y * CELL_SIZE, WIDTH, (y+1) * CELL_SIZE, fill=color, outline=color)

    # Snake
    for i, segment in enumerate(snake):
        scale = 0.7 + 0.3 * (i / len(snake)) if i == 0 else 1.0
        color = "#00ff00" if theme == 'light' else "#00cc00"
        draw_cell(segment[0], segment[1], color, oval=True, scale=scale)

    # AI path
    if mode == 'AI':
        for p in path:
            draw_cell(p[0], p[1], "#a3daff")

    # Blinking Food
    if blink_state:
        food_color = "red" if theme == 'light' else "#ff4444"
        draw_cell(food[0], food[1], food_color, oval=True)

    # Score
    score_color = "white" if theme == 'dark' else "black"
    canvas.create_text(60, 10, text=f"Score: {score}", fill=score_color, font=("Arial", 12, "bold"), anchor="w")

    if not running:
        canvas.create_text(WIDTH//2, HEIGHT//2, text="GAME OVER", fill="red", font=("Arial", 28, "bold"))

# --- A* Algorithm ---
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(start, goal):
    open_set = [(0, start)]
    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current != start:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
        
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            neighbor = (current[0]+dx, current[1]+dy)
            if (0 <= neighbor[0] < COLS and 0 <= neighbor[1] < ROWS and
                neighbor not in snake):
                temp_g = g_score[current] + 1
                if temp_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g
                    f_score = temp_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor))
    return []

# --- Move Function ---
def move():
    global direction, food, running, score, path

    if not running:
        draw()
        return

    head = snake[0]
    
    if mode == 'AI':
        path = astar(head, food)
        if path:
            next_cell = path[0]
            dx, dy = next_cell[0] - head[0], next_cell[1] - head[1]
            direction = 'Right' if dx == 1 else 'Left' if dx == -1 else 'Down' if dy == 1 else 'Up'

    if direction == 'Up': new_head = (head[0], head[1]-1)
    elif direction == 'Down': new_head = (head[0], head[1]+1)
    elif direction == 'Left': new_head = (head[0]-1, head[1])
    elif direction == 'Right': new_head = (head[0]+1, head[1])

    # Collision Check
    if (new_head in snake or new_head[0] < 0 or new_head[1] < 0 or
        new_head[0] >= COLS or new_head[1] >= ROWS):
        running = False
        draw()
        return

    snake.insert(0, new_head)
    if new_head == food:
        score += 1
        while True:
            food = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
            if food not in snake:
                break
    else:
        snake.pop()

    draw()
    window.after(SPEED, move)

# --- Keyboard Controls ---
def change_dir(event):
    global direction
    if mode != 'User': return
    if event.keysym in ['Up', 'w'] and direction != 'Down':
        direction = 'Up'
    elif event.keysym in ['Down', 's'] and direction != 'Up':
        direction = 'Down'
    elif event.keysym in ['Left', 'a'] and direction != 'Right':
        direction = 'Left'
    elif event.keysym in ['Right', 'd'] and direction != 'Left':
        direction = 'Right'

window.bind("<Key>", change_dir)

# --- Blinking Food Timer ---
def toggle_blink():
    global blink_state
    blink_state = not blink_state
    draw()
    window.after(500, toggle_blink)

# --- Start Game ---
draw()
move()
toggle_blink()
window.mainloop()
