import os
os.environ['SDL_AUDIODRIVER'] = 'dummy'  # ऑडियो एरर फिक्स करने के लिए

import pygame
import random
import math

# --- INITIALIZE PYGAME ---
pygame.init()
WIDTH, HEIGHT = 500, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Portal Assistant")
clock = pygame.time.Clock()

# --- COLORS ---
BG_COLOR = (20, 20, 30)
CARD_COLOR = (45, 45, 55)
INPUT_COLOR = (30, 30, 38)
TEXT_COLOR = (230, 215, 195)
ORANGE = (235, 140, 40)
GREEN = (40, 180, 100)
RED = (220, 60, 60)

# --- 3D CUBE CONFIGURATION ---
vertices = [
    [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
    [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
]
edges = [
    (0,1), (1,2), (2,3), (3,0),
    (4,5), (5,6), (6,7), (7,4),
    (0,4), (1,5), (2,6), (3,7)
]
angle_x = angle_y = 0

def draw_3d_cube():
    global angle_x, angle_y
    angle_x += 0.01
    angle_y += 0.01
    
    projected_vertices = []
    for vertex in vertices:
        y1 = vertex[1] * math.cos(angle_x) - vertex[2] * math.sin(angle_x)
        z1 = vertex[1] * math.sin(angle_x) + vertex[2] * math.cos(angle_x)
        x2 = vertex[0] * math.cos(angle_y) + z1 * math.sin(angle_y)
        z2 = -vertex[0] * math.sin(angle_y) + z1 * math.cos(angle_y)
        
        distance = 3
        focal_length = 250
        z_offset = z2 + distance
        if z_offset == 0: z_offset = 0.1
        
        x_proj = int(WIDTH / 2 + (x2 * focal_length) / z_offset)
        y_proj = int(HEIGHT / 4 + (y1 * focal_length) / z_offset)
        projected_vertices.append((x_proj, y_proj))
        
    for edge in edges:
        pygame.draw.line(screen, (70, 70, 90), projected_vertices[edge[0]], projected_vertices[edge[1]], 2)

# --- STATE VARIABLES & FONTS ---
current_screen = "login"  
username_text = ""
password_text = ""
command_text = ""
output_text = "Mera naam Launce hai. Mai aapki kya madad karu?"
active_box = "username"  
login_error = ""

# Linux Compatible Default Fonts
font = pygame.font.SysFont(None, 24)
font_large = pygame.font.SysFont(None, 32, bold=True)
font_small = pygame.font.SysFont(None, 18)

# --- PORTAL LOGIC ---
def process_portal_command(cmd):
    cmd = cmd.strip()
    if not cmd: return "Mera naam Launce hai.\nMai aapki kya madad karu?"
    try:
        if cmd.startswith("1"):
            expr = cmd[1:].strip()
            if not expr: return "Calc: Type '1 [math]'\nExample: '1 25*4'"
            if all(c in "0123456789+-*/.()" for c in expr): return f"Result: {expr} = {eval(expr)}"
            return "Invalid Math Characters!"
        elif cmd.startswith("2"):
            args = cmd[2:].split()
            if len(args) < 3: return "SBI FD: '2 [Amt] [Rate] [Yrs]'\nExample: '2 100000 6.5 3'"
            p, r, t = float(args[0]), float(args[1]), float(args[2])
            return f"SBI FD Maturity:\nPrincipal: INR {p:,.0f}\nMaturity: INR {p*(1+(r/100))**t:,.0f}"
        elif cmd.startswith("3"):
            args = cmd[1:].split()
            if len(args) < 2: return "GST: Type '3 [Amt] [%]'\nExample: '3 5000 18'"
            amt, rate = float(args[0]), float(args[1])
            return f"GST Invoice:\nBase: {amt}\nGST ({rate}%): {(amt*rate)/100}\nTotal: {amt+((amt*rate)/100)}"
        elif cmd.startswith("4"):
            args = cmd[1:].split()
            if not args: return "Grade: Type '4 [Marks]'"
            m = float(args[0])
            g = "A+" if m>=90 else "A" if m>=60 else "C" if m>=33 else "F"
            return f"Report Card:\nMarks: {m}/100 | Grade: {g}"
        elif cmd == "5": return f"Dice Roll: {random.randint(1, 6)}"
        elif cmd == "6": return f"Coin Result: {random.choice(['HEADS', 'TAILS'])}"
        elif cmd.startswith("7"):
            nums = [float(x) for x in cmd[1:].split()]
            return f"Average Value = {sum(nums)/len(nums):.2f}" if nums else "Example: '7 10 20'"
        elif cmd.startswith("8"):
            args = cmd[1:].split()
            p, r, n = float(args[0]), float(args[1]), float(args[2])
            mr = (r/12)/100
            emi = (p*mr*(1+mr)**n)/(((1+mr)**n)-1)
            return f"EMI: INR {emi:,.2f}/mo\nTotal: INR {emi*n:,.2f}"
        return "Option unknown!"
    except: return "Format Error! Check examples."

# --- MAIN LOOP ---
running = True
while running:
    pygame.event.pump() # Linux background processing handler
    screen.fill(BG_COLOR)
    draw_3d_cube()  
    
    # Events Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if current_screen == "login":
                if 100 <= x <= 400 and 320 <= y <= 365: active_box = "username"
                elif 100 <= x <= 400 and 400 <= y <= 445: active_box = "password"
                elif 150 <= x <= 350 and 480 <= y <= 525: 
                    if username_text == "admin" and password_text == "admin123":
                        current_screen = "dashboard"
                        active_box = "command"
                    else: login_error = "Invalid Username or Password!"
            elif current_screen == "dashboard":
                if 50 <= x <= 450 and 580 <= y <= 625: active_box = "command"
                elif 200 <= x <= 300 and 640 <= y <= 675: 
                    output_text = process_portal_command(command_text)
                    command_text = ""

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                if current_screen == "login":
                    active_box = "password" if active_box == "username" else "username"
            elif event.key == pygame.K_RETURN:
                if current_screen == "login":
                    if username_text == "admin" and password_text == "admin123":
                        current_screen = "dashboard"
                        active_box = "command"
                    else: login_error = "Invalid Username or Password!"
                elif current_screen == "dashboard":
                    output_text = process_portal_command(command_text)
                    command_text = ""
            elif event.key == pygame.K_BACKSPACE:
                if active_box == "username": username_text = username_text[:-1]
                elif active_box == "password": password_text = password_text[:-1]
                elif active_box == "command": command_text = command_text[:-1]
            else:
                if event.unicode.isprintable():
                    if active_box == "username": username_text += event.unicode
                    elif active_box == "password": password_text += event.unicode
                    elif active_box == "command": command_text += event.unicode

    # Render Visual Components
    if current_screen == "login":
        pygame.draw.rect(screen, (10, 10, 15), (75, 255, 360, 310), border_radius=15)
        pygame.draw.rect(screen, CARD_COLOR, (70, 250, 360, 310), border_radius=15)
        
        lbl = font_large.render("3D ASSISTANT LOGIN", True, ORANGE)
        screen.blit(lbl, (WIDTH/2 - lbl.get_width()/2, 270))
        
        u_box_color = ORANGE if active_box == "username" else INPUT_COLOR
        pygame.draw.rect(screen, u_box_color, (100, 320, 300, 45), 2, border_radius=8)
        u_txt = username_text if username_text else "Username: 'admin'"
        screen.blit(font.render(u_txt, True, TEXT_COLOR if username_text else (100,100,110)), (110, 332))
        
        p_box_color = ORANGE if active_box == "password" else INPUT_COLOR
        pygame.draw.rect(screen, p_box_color, (100, 400, 300, 45), 2, border_radius=8)
        p_txt = "*" * len(password_text) if password_text else "Password: 'admin123'"
        screen.blit(font.render(p_txt, True, TEXT_COLOR if password_text else (100,100,110)), (110, 412))
        
        pygame.draw.rect(screen, ORANGE, (150, 480, 200, 45), border_radius=10)
        btn_lbl = font.render("LOGIN", True, BG_COLOR)
        screen.blit(btn_lbl, (WIDTH/2 - btn_lbl.get_width()/2, 492))
        
        if login_error:
            err_lbl = font.render(login_error, True, RED)
            screen.blit(err_lbl, (WIDTH/2 - err_lbl.get_width()/2, 535))
            
    elif current_screen == "dashboard":
        pygame.draw.rect(screen, CARD_COLOR, (40, 240, 420, 140), border_radius=12)
        lines = output_text.split('\n')
        for i, line in enumerate(lines):
            screen.blit(font.render(line, True, ORANGE), (55, 255 + i*25))
            
        pygame.draw.rect(screen, INPUT_COLOR, (40, 400, 420, 150), border_radius=10)
        menu_items = [
            "1. Normal Calc ('1 5*5')", "2. SBI FD ('2 10000 6.5 3')",
            "3. GST Calc ('3 500 18')", "4. Grade Checker ('4 85')",
            "5. Dice (Type '5')", "6. Coin (Type '6')",
            "7. Avg Calc ('7 10 20')", "8. Loan EMI ('8 200000 9.5 12')"
        ]
        for i, item in enumerate(menu_items):
            x_pos = 50 if i % 2 == 0 else 260
            y_pos = 415 + (i // 2) * 30
            screen.blit(font_small.render(item, True, TEXT_COLOR), (x_pos, y_pos))
            
        pygame.draw.rect(screen, ORANGE if active_box == "command" else CARD_COLOR, (50, 580, 400, 45), 2, border_radius=8)
        cmd_display = command_text if command_text else "Type option code here..."
        screen.blit(font.render(cmd_display, True, TEXT_COLOR if command_text else (120,120,130)), (60, 592))
        
        pygame.draw.rect(screen, GREEN, (200, 640, 100, 35), border_radius=6)
        sub_lbl = font.render("Submit", True, BG_COLOR)
        screen.blit(sub_lbl, (225, 645))

    pygame.display.flip() #,
    clock.tick(60)

pygame.quit()
