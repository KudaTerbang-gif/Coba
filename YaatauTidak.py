import pygame, math, random, sys

pygame.init()
screen = pygame.display.set_mode((0, 0))
SW, SH = screen.get_size()
pygame.display.set_caption("Loves me, loves me not")

# resolusi kecil biar kelihatan pixel-art, lalu di-scale ke layar
W, H = 180, 320
sc = min(SW / W, SH / H)
OUT = (int(W * sc), int(H * sc))
OFF = ((SW - OUT[0]) // 2, (SH - OUT[1]) // 2)
buf = pygame.Surface((W, H))
font = pygame.font.Font(None, 26)

PINK = (255, 130, 175)
BLUE = (90, 150, 255)
NPET = 11            # ganjil -> berakhir di "LOVES ME"
CX0, CY0 = 90, 120   # posisi bunga
GROUND_Y = 290

random.seed(7)

# ---------- background (dibuat sekali) ----------
def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

bg = pygame.Surface((W, H))
for y in range(H):
    t = y / 250
    c = lerp((12, 14, 60), (40, 60, 150), min(t, 1)) if t < 1 else (40, 60, 150)
    pygame.draw.line(bg, c, (0, y), (W, y))
# bulan + halo dithering
MX, MY = 150, 45
for dy in range(-22, 23):
    for dx in range(-22, 23):
        d = math.hypot(dx, dy)
        if 10 < d < 22 and (dx + dy) % 2 == 0 and random.random() < (22 - d) / 14:
            bg.set_at((MX + dx, MY + dy), (150, 160, 220))
pygame.draw.circle(bg, (250, 235, 150), (MX, MY), 10)
pygame.draw.circle(bg, (225, 205, 120), (MX + 3, MY + 2), 3)
# bukit
for x in range(W):
    y1 = 232 + 12 * math.sin(x * 0.035) + 6 * math.sin(x * 0.09 + 1)
    pygame.draw.line(bg, (28, 38, 110), (x, int(y1)), (x, H))
    y2 = 255 + 8 * math.sin(x * 0.05 + 2) + 4 * math.sin(x * 0.13)
    pygame.draw.line(bg, (18, 28, 85), (x, int(y2)), (x, H))
# rumput
for y in range(GROUND_Y - 12, H):
    pygame.draw.line(bg, lerp((40, 110, 40), (20, 70, 30), (y - GROUND_Y + 12) / 42), (0, y), (W, y))
for _ in range(500):
    x = random.randrange(W)
    y = random.randrange(GROUND_Y - 14, H)
    h = random.randint(3, 8)
    g = random.choice([(70, 160, 60), (50, 130, 50), (90, 180, 70)])
    pygame.draw.line(bg, g, (x, y), (x + random.randint(-1, 1), y - h))

stars = [(random.randrange(W), random.randrange(200), random.random() * 6) for _ in range(45)]

# ---------- helper ----------
HEART = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]

def draw_heart(x, y, col):
    for j, row in enumerate(HEART):
        for i, ch in enumerate(row):
            if ch == "1":
                buf.set_at((int(x) + i - 3, int(y) + j - 3), col)

def petal_poly(x, y, ang, length=28, width=6):
    pts = []
    n = 8
    for k in range(n + 1):
        t = k / n
        pts.append((t * length, -width * math.sin(math.pi * t) ** 0.8))
    for k in range(n, -1, -1):
        t = k / n
        pts.append((t * length, width * math.sin(math.pi * t) ** 0.8))
    ca, sa = math.cos(ang), math.sin(ang)
    return [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts]

def draw_text(txt, col):
    s = font.render(txt, False, col)
    sh = font.render(txt, False, (10, 10, 40))
    bob = 0
    if G["done_t"] is not None:
        bob = int(2 * math.sin(G["t"] * 6))
    r = s.get_rect(center=(W // 2, 32 + bob))
    buf.blit(sh, (r.x + 1, r.y + 1))
    buf.blit(s, r)

# ---------- state ----------
def reset():
    g = {}
    g["petals"] = [{"a": i * 2 * math.pi / NPET + 0.2, "on": True} for i in range(NPET)]
    g["fly"] = []
    g["hearts"] = []
    g["pulled"] = 0
    g["next"] = 1.5
    g["t"] = 0.0
    g["text"] = ""
    g["done_t"] = None
    g["hs"] = 0
    g["sparks"] = []
    g["shoot"] = None
    g["next_shoot"] = 3.0
    g["flies"] = [{"x": random.uniform(10, W - 10), "y": random.uniform(190, 300),
                   "ph": random.random() * 6, "sp": random.uniform(0.4, 1.0)} for _ in range(16)]
    return g

G = reset()
clock = pygame.time.Clock()

while True:
    dt = min(clock.tick(60) / 1000, 0.05)
    tap = False
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if e.type == pygame.MOUSEBUTTONDOWN:
            if G["done_t"] is not None:
                G = reset()      # sudah habis -> ketuk lagi untuk mengulang
            else:
                tap = True       # ketuk = cabut satu kelopak
    G["t"] += dt
    t = G["t"]

    # cabut kelopak
    left = [p for p in G["petals"] if p["on"]]
    if left and tap:
        p = random.choice(left)
        p["on"] = False
        G["pulled"] += 1
        G["text"] = "LOVES ME" if G["pulled"] % 2 else "LOVES ME NOT"
        a = p["a"] + math.sin(t * 1.3) * 0.05
        G["fly"].append({
            "x": CX0 + math.cos(a) * 6, "y": CY0 + math.sin(a) * 6, "a": a,
            "vx": math.cos(a) * 35 + random.uniform(10, 30),
            "vy": math.sin(a) * 35 - 25, "spin": random.uniform(-6, 6),
            "land": False, "gy": random.randint(GROUND_Y + 2, H - 8)})
        for _ in range(10):
            ang = random.uniform(0, 6.28); sp = random.uniform(15, 55)
            G["sparks"].append({"x": CX0 + math.cos(a) * 20, "y": CY0 + math.sin(a) * 20,
                                "vx": math.cos(ang) * sp, "vy": math.sin(ang) * sp - 10,
                                "life": random.uniform(0.4, 0.9)})
        if not [q for q in G["petals"] if q["on"]]:
            G["done_t"] = t
            for _ in range(30):      # ledakan hati + percikan saat selesai
                ang = random.uniform(0, 6.28); sp = random.uniform(20, 90)
                G["sparks"].append({"x": CX0, "y": CY0, "vx": math.cos(ang) * sp,
                                    "vy": math.sin(ang) * sp, "life": random.uniform(0.6, 1.4)})
    # update kelopak jatuh
    for f in G["fly"]:
        if not f["land"]:
            f["vy"] += 70 * dt
            f["vx"] += 8 * dt
            f["x"] += f["vx"] * dt
            f["y"] += f["vy"] * dt
            f["a"] += f["spin"] * dt
            if f["y"] >= f["gy"]:
                f["y"] = f["gy"]; f["land"] = True
                f["a"] = random.uniform(-0.3, 0.3) + random.choice([0, math.pi])
    for sp_ in G["sparks"]:
        sp_["x"] += sp_["vx"] * dt; sp_["y"] += sp_["vy"] * dt
        sp_["vy"] += 40 * dt; sp_["life"] -= dt
    G["sparks"] = [q for q in G["sparks"] if q["life"] > 0]
    # bintang jatuh
    if G["shoot"] is None and t > G["next_shoot"]:
        G["shoot"] = {"x": random.randint(90, W), "y": random.randint(10, 70), "life": 1.0}
    if G["shoot"]:
        G["shoot"]["x"] -= 120 * dt; G["shoot"]["y"] += 60 * dt; G["shoot"]["life"] -= dt
        if G["shoot"]["life"] <= 0:
            G["shoot"] = None; G["next_shoot"] = t + random.uniform(4, 8)
    # hati
    if G["done_t"] is not None and t - G["done_t"] > 0.5 and t > G["hs"]:
        G["hs"] = t + 0.1
        G["hearts"].append({"x": CX0 + random.uniform(-6, 6), "y": CY0 - 8,
                            "ph": random.random() * 6, "v": random.uniform(25, 45)})
    for h in G["hearts"]:
        h["y"] -= h["v"] * dt
    G["hearts"] = [h for h in G["hearts"] if h["y"] > 55]

    # ---------- gambar ----------
    buf.blit(bg, (0, 0))
    for sx, sy, ph in stars:
        if math.sin(t * 2 + ph) > -0.3:
            buf.set_at((sx, sy), (230, 230, 255))
            if ph > 5:
                buf.set_at((sx + 1, sy), (150, 150, 210))

    if G["shoot"]:
        sx_, sy_ = G["shoot"]["x"], G["shoot"]["y"]
        for k in range(10):
            c = max(40, 255 - k * 25)
            buf.set_at((int(sx_ + k * 2), int(sy_ - k)), (c, c, min(255, c + 20)))
    for f in G["flies"]:
        fx = f["x"] + math.sin(t * f["sp"] + f["ph"]) * 12
        fy = f["y"] + math.cos(t * f["sp"] * 0.8 + f["ph"]) * 8
        if math.sin(t * 3 + f["ph"]) > -0.2:
            for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                buf.set_at((int(fx) + ox, int(fy) + oy), (110, 120, 40))
            buf.set_at((int(fx), int(fy)), (255, 250, 150))

    sway = math.sin(t * 1.2) * 1.5
    cx, cy = CX0 + sway, CY0
    # batang (bezier)
    pts = []
    for k in range(21):
        u = k / 20
        bx = (1 - u) ** 2 * 90 + 2 * u * (1 - u) * (90 - 8 + sway) + u * u * cx
        by = (1 - u) ** 2 * (GROUND_Y + 2) + 2 * u * (1 - u) * 210 + u * u * cy
        pts.append((bx, by))
    pygame.draw.lines(buf, (40, 130, 50), False, pts, 4)
    pygame.draw.lines(buf, (80, 180, 70), False, [(x - 1, y) for x, y in pts], 1)
    # daun
    for idx, side in ((6, -1), (10, 1)):
        bx, by = pts[idx]
        upper = [(bx + u * 26 * side, by - u * 10 - 6 * math.sin(math.pi * u)) for u in [k / 8 for k in range(9)]]
        lower = [(bx + u * 26 * side, by - u * 10 + 4 * math.sin(math.pi * u)) for u in [k / 8 for k in range(8, -1, -1)]]
        pygame.draw.polygon(buf, (60, 160, 60), upper + lower)
        pygame.draw.line(buf, (30, 100, 40), (bx, by), (bx + 26 * side, by - 10))

    # kelopak jatuh / di tanah
    for f in G["fly"]:
        poly = petal_poly(f["x"], f["y"], f["a"], 22, 5)
        pygame.draw.polygon(buf, (255, 205, 40), poly)
        pygame.draw.polygon(buf, (215, 130, 20), poly, 1)

    # kelopak menempel
    for p in G["petals"]:
        if p["on"]:
            a = p["a"] + math.sin(t * 1.5 + p["a"]) * 0.03
            poly = petal_poly(cx + math.cos(a) * 8, cy + math.sin(a) * 8, a)
            pygame.draw.polygon(buf, (255, 205, 40), poly)
            pygame.draw.polygon(buf, (215, 130, 20), poly, 1)
            mid = (cx + math.cos(a) * 28, cy + math.sin(a) * 28)
            pygame.draw.line(buf, (240, 160, 25), (cx + math.cos(a) * 10, cy + math.sin(a) * 10), mid)

    # pusat bunga (biji matahari berpola spiral)
    glow = 0
    if G["done_t"] is not None:
        glow = int(2 + 2 * math.sin(t * 6))
        pygame.draw.circle(buf, (255, 220, 120), (int(cx), int(cy)), 11 + glow, 1)
    pygame.draw.circle(buf, (215, 125, 25), (int(cx), int(cy)), 11)
    pygame.draw.circle(buf, (85, 45, 20), (int(cx), int(cy)), 9)
    for k in range(1, 38):
        r_ = 1.35 * math.sqrt(k); an = k * 2.399963
        buf.set_at((int(cx + math.cos(an) * r_), int(cy + math.sin(an) * r_)),
                   (150, 90, 35) if k % 3 else (60, 30, 12))

    # rumput depan
    for x in range(0, W, 6):
        sw = math.sin(t * 2 + x) * 1.5
        pygame.draw.line(buf, (80, 180, 70), (x, H), (x + sw, H - 9 - (x * 7 % 5)))

    for q in G["sparks"]:
        c = (255, 240, 160) if q["life"] > 0.3 else (255, 180, 60)
        buf.set_at((int(q["x"]), int(q["y"])), c)
        buf.set_at((int(q["x"]) + 1, int(q["y"])), c)
    for h in G["hearts"]:
        draw_heart(h["x"] + math.sin(t * 3 + h["ph"]) * 10, h["y"], (230, 60, 90))

    if G["pulled"] == 0:
        hint = font.render("TAP!", False, (230, 230, 255))
        buf.blit(hint, hint.get_rect(center=(W // 2, 32)))
    if G["text"]:
        draw_text(G["text"], PINK if G["text"] == "LOVES ME" else BLUE)

    screen.fill((0, 0, 0))
    screen.blit(pygame.transform.scale(buf, OUT), OFF)
    pygame.display.flip()
