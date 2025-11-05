import pygame, random, time, json, os

# Init
pygame.init()
pygame.mixer.init()

# Sounds (3 different eat sounds)
eat_sounds = []
for fname in ['eat.mp3', 'eat2.mp3', 'eat3.mp3']:
    if os.path.exists(fname):
        eat_sounds.append(pygame.mixer.Sound(fname))
over_sound = pygame.mixer.Sound('gameover.wav') if os.path.exists('gameover.wav') else None

#  Track which eat sound to play next
sound_index = 0  
def play_next_sound():
    global sound_index
    if eat_sounds:
        eat_sounds[sound_index].play()
        sound_index = (sound_index + 1) % len(eat_sounds)

# Display
W, H = 1000, 600
BLOCK = 20
dis = pygame.display.set_mode((W, H))
pygame.display.set_caption('🐍 Snake Game Pro')
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont('Arial', 25)
score_font = pygame.font.SysFont('Arial', 35)

# Background colors per level
bg_colors = [
    (50, 213, 153),   
    (40, 190, 140),   
    (30, 160, 120),  
    (20, 130, 100),  
    (10, 100, 80)     
]

# Load & Save Score
def load_score():
    if os.path.exists('highscore.json'):
        with open('highscore.json', 'r') as f:
            return json.load(f).get('high_score', 0)
    return 0

def save_score(score):
    with open('highscore.json', 'w') as f:
        json.dump({'high_score': score}, f)

# Text Drawing
def draw_text(txt, color, y_off=0, size=25):
    surf = pygame.font.SysFont('Arial', size).render(txt, True, color)
    rect = surf.get_rect(center=(W / 2, H / 2 + y_off))
    dis.blit(surf, rect)

# Draw Snake
def draw_snake(slst):
    for i, seg in enumerate(slst):
        blend = i / max(len(slst)-1, 1)
        col = (200 - int(blend*100), 0, 0)
        pygame.draw.rect(dis, col, (seg[0], seg[1], BLOCK, BLOCK), border_radius=5)
    if slst:
        hx, hy = slst[-1]
        pygame.draw.circle(dis, (255, 255, 255), (hx + 5, hy + 7), 3)
        pygame.draw.circle(dis, (255, 255, 255), (hx + 15, hy + 7), 3)

# Draw obstacles
def draw_obstacles(obs):
    for o in obs:
        pygame.draw.rect(dis, (213, 50, 80), (o[0], o[1], BLOCK, BLOCK))

# Draw animated food
def draw_food(pos):
    pulse = 4 * abs((time.time() % 1) - 0.5)
    radius = BLOCK // 2 - int(pulse * 5)
    center = (pos[0] + BLOCK // 2, pos[1] + BLOCK // 2)
    interp = abs((time.time() * 2) % 2 - 1)
    col = (
        int(255 * (1 - interp) + 255 * interp),
        int(165 * (1 - interp) + 69 * interp),
        0
    )
    pygame.draw.circle(dis, col, center, radius)

# Draw power-up
def draw_power_up(pos):
    if not pos: return
    glow = int(128 + 127 * abs((time.time() % 1) - 0.5) * 2)
    pygame.draw.circle(dis, (255, 215, 0), (pos[0] + BLOCK//2, pos[1]+BLOCK//2), 12)
    pygame.draw.circle(dis, (glow, glow, 0), (pos[0] + BLOCK//2, pos[1]+BLOCK//2), 8)

# Game over screen
def game_over_screen(score):
    if over_sound: over_sound.play()
    high = load_score()
    is_new = score > high
    save_score(max(score, high))
    dis.fill((0, 0, 0))
    draw_text("GAME OVER!", (255, 0, 0), -50, 40)
    draw_text(f"Score: {score}", (255, 255, 255), 0)
    if is_new:
        draw_text("New High Score!", (0, 255, 0), 50)
    draw_text("Press C to Replay or Q to Quit", (255, 255, 102), 100)
    pygame.display.update()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); quit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q: pygame.quit(); quit()
                if e.key == pygame.K_c: return

# Main menu
def main_menu():
    pygame.mixer.music.stop()
    while True:
        dis.fill((50, 153, 213))
        draw_text("🐍 Ultimate Snake Game", (255, 255, 102), -60, 40)
        draw_text(f"High Score: {load_score()}", (255, 255, 255), -10)
        draw_text("C: Start  P: Pause  Q: Quit", (255, 255, 102), 40)
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); quit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q: pygame.quit(); quit()
                if e.key == pygame.K_c:
                    if os.path.exists("bgmn.mp3"):
                        pygame.mixer.music.load("bgmn.mp3")
                        pygame.mixer.music.play(-1)
                    game_loop()

# Game loop
def game_loop():
    x = y = W // 2
    dx = dy = 0
    slst = []
    length = 1
    score = 0
    level = 1
    speed = 10
    level_timer = time.time()
    power_up = None
    power_timer = 0

    obs = [[random.randrange(0, W, BLOCK), random.randrange(0, H, BLOCK)] for _ in range(3)]

    def spawn_item(avoid_list):
        while True:
            pos = [random.randrange(0, W-BLOCK, BLOCK), random.randrange(0, H-BLOCK, BLOCK)]
            if pos not in avoid_list:
                return pos

    food = spawn_item(slst + obs)

    paused = False
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); quit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q: running = False
                elif e.key == pygame.K_p: paused = not paused
                elif e.key == pygame.K_LEFT and dx == 0: dx, dy = -BLOCK, 0
                elif e.key == pygame.K_RIGHT and dx == 0: dx, dy = BLOCK, 0
                elif e.key == pygame.K_UP and dy == 0: dx, dy = 0, -BLOCK
                elif e.key == pygame.K_DOWN and dy == 0: dx, dy = 0, BLOCK

        if paused:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            dis.blit(overlay, (0, 0))
            draw_text("Paused - Press P to Resume", (255, 255, 255), 0)
            pygame.display.update()
            continue

        x = (x + dx) % W
        y = (y + dy) % H

        if [x, y] in obs:
            x -= dx; y -= dy

        slst.append([x, y])
        if len(slst) > length:
            slst.pop(0)

        for seg in slst[:-1]:
            if seg == [x, y]:
                running = False

        bg = bg_colors[min(level-1, len(bg_colors)-1)]
        dis.fill(bg)
        draw_obstacles(obs)
        draw_snake(slst)
        draw_food(food)
        draw_power_up(power_up)
        draw_text(f"Score: {score}  Level: {level}", (255, 255, 102), y_off=-H//2+20, size=25)
        pygame.display.update()

        # Eat food
        if [x, y] == food:
            length += 1
            score += 10
            play_next_sound()  # 🔹 Cycle through sounds
            food = spawn_item(slst + obs)
            if random.random() < 0.2:
                power_up = spawn_item(slst + obs + [food])
                power_timer = time.time()

        if power_up and [x, y] == power_up:
            score += 50
            length += 3
            power_up = None

        if power_up and time.time() - power_timer > 7:
            power_up = None

        if time.time() - level_timer > 20:
            level += 1
            speed += 2
            obs.append(spawn_item(slst + obs + [food]))
            level_timer = time.time()

        clock.tick(speed)

    pygame.mixer.music.stop()
    game_over_screen(score)

if __name__ == "__main__":
    main_menu()
