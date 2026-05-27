import tkinter as tk
import random
import time

# ================= WINDOW =================
root = tk.Tk()
root.title("MODERN SHOT CHALLENGE - CLEAN REWRITE")
root.geometry("1200x800")
root.configure(bg="#101820")

canvas = tk.Canvas(root, width=1200, height=800, bg="#101820", highlightthickness=0)
canvas.pack()

# ================= STATES =================
MENU = "menu"
PLAY = "play"
OVER = "over"
PAUSE = "pause"

state = MENU

# ================= GAME VARS =================
score = 0
streak = 0
best_score = 0

bar_x = 250
bar_y = 650
bar_w = 700

indicator_x = bar_x
indicator_dir = 1
indicator_speed = 8

target_x = 500
target_w = 80
target_dir = 3

time_left = 60
timer_start = 0
timed_mode = True

shot_anim_active = False
shot_anim_t = 0
shot_anim_duration = 0.35
shot_start_x = 0
shot_start_y = 0
shot_end_x = 900
shot_end_y = 160

shake_frames = 0
shake_intensity = 0

particles = []


# ================= HELPERS =================
def trigger_shake(intensity=6, frames=10):
    global shake_frames, shake_intensity
    shake_frames = frames
    shake_intensity = intensity

def get_shake_offset():
    if shake_frames > 0:
        return random.randint(-shake_intensity, shake_intensity), random.randint(-shake_intensity, shake_intensity)
    return 0, 0

def create_particles(x, y, color):
    for _ in range(25):
        particles.append({
            "x": x,
            "y": y,
            "dx": random.uniform(-5, 5),
            "dy": random.uniform(-5, 5),
            "life": 25,
            "color": color
        })

def reset_meter():
    global indicator_x, indicator_dir, target_x, target_w, target_dir
    indicator_x = bar_x
    indicator_dir = 1

    target_w = random.randint(40, 90)
    target_x = random.randint(bar_x + 20, bar_x + bar_w - target_w - 20)
    target_dir = random.choice([-3, 3])


# ================= DRAW =================
def draw_court():
    ox, oy = get_shake_offset()
    canvas.create_rectangle(0+ox,0+oy,1200+ox,800+oy,fill="#101820",outline="")
    canvas.create_rectangle(0+ox,170+oy,1200+ox,350+oy,fill="#2a2a2a",outline="")
    canvas.create_rectangle(0+ox,350+oy,1200+ox,800+oy,fill="#b87333",outline="")

def draw_hoop():
    ox, oy = get_shake_offset()
    hx = 900 + ox
    canvas.create_rectangle(hx-70,80+oy,hx+70,220+oy,fill="#dfe7fd",outline="#fff",width=4)
    canvas.create_rectangle(hx-18,110+oy,hx+22,150+oy,outline="red",width=4)
    canvas.create_oval(hx-40,150+oy,hx+40,168+oy,fill="#ff7b00",outline="#ff8800",width=4)

def draw_ball():
    if shot_anim_active:
        t = max(0, min(1, shot_anim_t / shot_anim_duration))
        x = shot_start_x + (shot_end_x - shot_start_x) * t
        y = shot_start_y + (shot_end_y - shot_start_y) * t - (1 - (2*t-1)**2) * 120
    else:
        x = indicator_x
        y = bar_y + 15

    ox, oy = get_shake_offset()
    r = 24
    canvas.create_oval(x-r+ox,y-r+oy,x+r+ox,y+r+oy,fill="#f77f00",outline="#ffb703",width=3)

def draw_particles():
    for p in particles[:]:
        canvas.create_oval(p["x"],p["y"],p["x"]+5,p["y"]+5,fill=p["color"],outline="")
        p["x"] += p["dx"]
        p["y"] += p["dy"]
        p["life"] -= 1
        if p["life"] <= 0:
            particles.remove(p)

def draw_ui():
    canvas.create_rectangle(0,0,1200,80,fill="#0a0f1f",outline="")
    canvas.create_text(140,40,text=f"SCORE {score}",fill="#00ffcc",font=("Arial",22,"bold"))
    canvas.create_text(400,40,text=f"BEST {best_score}",fill="#ffe066",font=("Arial",22,"bold"))
    canvas.create_text(650,40,text=f"STREAK {streak}",fill="#ff4d6d",font=("Arial",22,"bold"))
    if timed_mode and state == PLAY:
        canvas.create_text(900,40,text=f"TIME {max(0,int(time_left))}",fill="#ffb703",font=("Arial",22,"bold"))

def draw_meter():
    canvas.create_rectangle(bar_x,bar_y,bar_x+bar_w,bar_y+30,fill="#222",outline="#666",width=3)
    canvas.create_rectangle(target_x,bar_y,target_x+target_w,bar_y+30,fill="#ff0033",outline="#ff4d6d",width=2)
    canvas.create_line(indicator_x,bar_y,indicator_x,bar_y+30,fill="#00e5ff",width=4)

def draw():
    canvas.delete("all")
    draw_court()
    draw_hoop()
    draw_ui()
    draw_meter()
    draw_ball()
    draw_particles()


# ================= GAME FLOW =================
def start_game():
    global state, score, streak, time_left, timer_start, shot_anim_active
    state = PLAY
    score = 0
    streak = 0
    shot_anim_active = False
    if timed_mode:
        time_left = 60
        timer_start = time.time()
    reset_meter()

def game_over():
    global state, best_score
    state = OVER
    if score > best_score:
        best_score = score
    trigger_shake(10, 20)


# ================= SHOOT =================
def start_shot_animation():
    global shot_anim_active, shot_anim_t, shot_start_x, shot_start_y
    shot_anim_active = True
    shot_anim_t = 0
    shot_start_x = indicator_x
    shot_start_y = bar_y + 15

def shoot(event):
    global score, streak, shot_anim_active

    # if animation stuck, free it
    if shot_anim_active:
        shot_anim_active = False

    if state == MENU:
        start_game()
        return
    if state == OVER:
        start_game()
        return
    if state == PAUSE:
        return

    # actual shot
    center = target_x + target_w / 2
    if abs(indicator_x - center) <= target_w / 2:
        streak += 1
        score += 10 + streak * 2
        create_particles(900,160,"#00ff88")
        trigger_shake(5,8)
    else:
        game_over()
        return

    start_shot_animation()
    reset_meter()


# ================= PAUSE =================
def toggle_pause(event):
    global state
    if state == PLAY:
        state = PAUSE
    elif state == PAUSE:
        state = PLAY


# ================= UPDATE =================
def update():
    global indicator_x, indicator_dir
    global target_x, target_dir
    global shot_anim_t, shot_anim_active
    global shake_frames
    global time_left

    now = time.time()

    if state == PLAY:
        # timer
        if timed_mode:
            time_left = 60 - (now - timer_start)
            if time_left <= 0:
                game_over()

        # indicator movement
        indicator_x += indicator_speed * indicator_dir
        if indicator_x <= bar_x:
            indicator_x = bar_x
            indicator_dir = 1
        if indicator_x >= bar_x + bar_w:
            indicator_x = bar_x + bar_w
            indicator_dir = -1

        # target movement
        target_x += target_dir
        if target_x <= bar_x + 10 or target_x + target_w >= bar_x + bar_w - 10:
            target_dir *= -1

        # shot animation
        if shot_anim_active:
            shot_anim_t += 0.016
            if shot_anim_t >= shot_anim_duration:
                shot_anim_active = False

        # shake decay
        if shake_frames > 0:
            shake_frames -= 1

        draw()

    elif state == MENU:
        canvas.delete("all")
        canvas.create_text(600,180,text="🏀 MODERN SHOT CHALLENGE",fill="white",font=("Arial",40,"bold"))
        canvas.create_text(600,280,text="PRESS SPACE TO START",fill="#00e5ff",font=("Arial",28,"bold"))
        canvas.create_text(600,340,text=f"BEST SCORE: {best_score}",fill="#ffd60a",font=("Arial",22))
        canvas.create_text(600,420,text="SPACE = Shoot   ESC = Pause",fill="#ffffff",font=("Arial",20))

    elif state == OVER:
        canvas.delete("all")
        canvas.create_text(600,200,text="GAME OVER",fill="#ff0033",font=("Arial",50,"bold"))
        canvas.create_text(600,300,text=f"SCORE: {score}",fill="white",font=("Arial",30))
        canvas.create_text(600,360,text=f"BEST: {best_score}",fill="#ffd60a",font=("Arial",26))
        canvas.create_text(600,460,text="PRESS SPACE TO PLAY AGAIN",fill="#00e5ff",font=("Arial",24,"bold"))

    elif state == PAUSE:
        canvas.create_rectangle(0,0,1200,800,fill="#000000",stipple="gray50",outline="")
        canvas.create_text(600,360,text="PAUSED",fill="#ffffff",font=("Arial",40,"bold"))
        canvas.create_text(600,420,text="Press ESC to resume",fill="#00e5ff",font=("Arial",24,"bold"))

    root.after(16, update)


# ================= KEYBINDS =================
root.bind("<space>", shoot)
root.bind("<Escape>", toggle_pause)

# ================= START =================
update()
root.mainloop()
