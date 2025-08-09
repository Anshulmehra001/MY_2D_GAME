import pygame
import sys
import os
import importlib
import time

# --- Configuration ---
WIDTH, HEIGHT = 800, 480
FPS = 60
MAX_LEVEL = 10

# --- Initialization ---
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Doraemon: Nobita's Visionary Swordsmen")
clock = pygame.time.Clock()

# --- Paths ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(ROOT_DIR, "assets")
sys.path.append(ASSET_DIR)

# --- Fonts ---
title_font = pygame.font.SysFont("lucidaconsole", 48, bold=True)
menu_font = pygame.font.SysFont("lucidaconsole", 36, bold=True)
cheat_font = pygame.font.SysFont("consolas", 28, bold=True)
# NEW: Fonts for the enhanced splash screen
creator_font = pygame.font.SysFont("lucidaconsole", 42, bold=True)
presents_font = pygame.font.SysFont("lucidaconsole", 24)

# --- Music Manager ---
music = {
    "intro": os.path.join(ASSET_DIR, "bgm_intro.wav"),
    "menu": os.path.join(ASSET_DIR, "bgm.wav"),
    "gameplay": os.path.join(ASSET_DIR, "bgm_gameplay.wav")
}
current_music = None


def play_music(track_name):
    global current_music
    if track_name != current_music and os.path.exists(music[track_name]):
        pygame.mixer.music.load(music[track_name])
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        current_music = track_name


# --- Colors ---
WHITE, BLACK, GOLD, GREY, RED, LIME_GREEN = (255, 255, 255), (0, 0, 0), (255, 215, 0), (100, 100, 100), (200, 0, 0), (
    50, 205, 50)


# --- Utility Functions ---
def fade_out(duration=500):
    fade_surface = pygame.Surface((WIDTH, HEIGHT));
    fade_surface.fill(BLACK)
    for alpha in range(0, 255, 15):
        fade_surface.set_alpha(alpha);
        screen.blit(fade_surface, (0, 0));
        pygame.display.update();
        pygame.time.delay(int(duration / (255 / 15)))


def load_img(name, scale=None):
    path = os.path.join(ASSET_DIR, name)
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, scale) if scale else img
    except pygame.error:
        print(f"Error loading image: {path}. Using placeholder.")
        fallback = pygame.Surface(scale if scale else (50, 50), pygame.SRCALPHA);
        fallback.fill((255, 0, 255));
        return fallback


# --- Asset Loading for Menu ---
title_logo = load_img("title_logo.png", (WIDTH, HEIGHT))

# --- Game State Variables ---
game_state = "INTRO";
previous_game_state = "MAIN_MENU";
current_level = 1;
cheat_input_text = ""


# --- Enhanced Splash Screen Function ---
def show_creator_screen():
    """Displays a professional, animated splash screen."""
    # --- Animation Timings (in seconds) ---
    FADE_IN_TIME = 1.5
    STAY_TIME = 2.0
    FADE_OUT_TIME = 1.5
    TOTAL_DURATION = FADE_IN_TIME + STAY_TIME + FADE_OUT_TIME

    # --- Text Surfaces ---
    presents_text = presents_font.render("A Game By", True, WHITE)
    creator_text = creator_font.render("ANIKET MEHRA", True, WHITE)

    start_time = time.time()
    while True:
        # Check for a quit event so the user can close the window during the splash
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        elapsed_time = time.time() - start_time

        # Exit the loop after the total duration has passed
        if elapsed_time > TOTAL_DURATION:
            break

        # --- Calculate Alpha (Transparency) ---
        alpha = 0
        if elapsed_time < FADE_IN_TIME:
            # Fading In
            alpha = int((elapsed_time / FADE_IN_TIME) * 255)
        elif elapsed_time < FADE_IN_TIME + STAY_TIME:
            # Staying Solid
            alpha = 255
        else:
            # Fading Out
            time_left = TOTAL_DURATION - elapsed_time
            alpha = int((time_left / FADE_OUT_TIME) * 255)

        alpha = max(0, min(255, alpha))  # Ensure alpha is within 0-255

        # --- Drawing ---
        screen.fill(BLACK)

        # Set alpha for both text surfaces
        presents_text.set_alpha(alpha)
        creator_text.set_alpha(alpha)

        # Position and blit the text
        screen.blit(presents_text, presents_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 30)))
        screen.blit(creator_text, creator_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 20)))

        pygame.display.update()
        clock.tick(FPS)


# --- Game State Screens ---
def draw_main_menu(events):
    global game_state, current_level
    screen.blit(title_logo, (0, 0))
    start_btn = pygame.Rect(WIDTH / 2 - 150, 280, 300, 60);
    quit_btn = pygame.Rect(WIDTH / 2 - 150, 360, 300, 60)
    mouse_pos = pygame.mouse.get_pos()
    pygame.draw.rect(screen, GOLD if start_btn.collidepoint(mouse_pos) else GREY, start_btn, border_radius=15)
    pygame.draw.rect(screen, RED if quit_btn.collidepoint(mouse_pos) else GREY, quit_btn, border_radius=15)
    start_text = menu_font.render("Start Game", True, WHITE);
    screen.blit(start_text, start_text.get_rect(center=start_btn.center))
    quit_text = menu_font.render("Quit", True, WHITE);
    screen.blit(quit_text, quit_text.get_rect(center=quit_btn.center))
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if start_btn.collidepoint(mouse_pos): fade_out(); game_state = "PLAYING"; current_level = 1
            if quit_btn.collidepoint(mouse_pos): pygame.quit(); sys.exit()


def draw_game_over_screen(events):
    global game_state
    play_music("menu")
    screen.fill(BLACK)
    msg_text = title_font.render("Game Over", True, RED);
    screen.blit(msg_text, msg_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 50)))
    menu_btn = pygame.Rect(WIDTH / 2 - 150, 350, 300, 60);
    mouse_pos = pygame.mouse.get_pos()
    pygame.draw.rect(screen, GOLD if menu_btn.collidepoint(mouse_pos) else GREY, menu_btn, border_radius=15)
    menu_text = menu_font.render("Main Menu", True, WHITE);
    screen.blit(menu_text, menu_text.get_rect(center=menu_btn.center))
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and menu_btn.collidepoint(mouse_pos):
            fade_out();
            game_state = "MAIN_MENU"


def draw_victory_screen(events):
    global game_state
    play_music("menu")
    screen.fill(BLACK)
    msg_text = title_font.render("YOU ARE VICTORIOUS!", True, GOLD);
    screen.blit(msg_text, msg_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 50)))
    menu_btn = pygame.Rect(WIDTH / 2 - 150, 350, 300, 60);
    mouse_pos = pygame.mouse.get_pos()
    pygame.draw.rect(screen, GOLD if menu_btn.collidepoint(mouse_pos) else GREY, menu_btn, border_radius=15)
    menu_text = menu_font.render("Main Menu", True, WHITE);
    screen.blit(menu_text, menu_text.get_rect(center=menu_btn.center))
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and menu_btn.collidepoint(mouse_pos):
            fade_out();
            game_state = "MAIN_MENU"


def draw_cheat_menu(events):
    global game_state, previous_game_state, current_level, cheat_input_text
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA);
    overlay.fill((0, 0, 0, 180));
    screen.blit(overlay, (0, 0))
    box_rect = pygame.Rect(WIDTH / 2 - 250, HEIGHT / 2 - 100, 500, 200)
    pygame.draw.rect(screen, BLACK, box_rect, border_radius=15);
    pygame.draw.rect(screen, LIME_GREEN, box_rect, width=3, border_radius=15)
    title_text = cheat_font.render("--- MASTER CONTROL ---", True, LIME_GREEN);
    screen.blit(title_text, title_text.get_rect(center=(WIDTH / 2, box_rect.y + 40)))
    prompt_text = cheat_font.render("Enter Level (1-10), then press ENTER", True, WHITE);
    screen.blit(prompt_text, prompt_text.get_rect(center=(WIDTH / 2, box_rect.y + 80)))
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                try:
                    level_num = int(cheat_input_text)
                    if 1 <= level_num <= MAX_LEVEL:
                        print(f"CHEAT: Warping to Level {level_num}");
                        current_level = level_num;
                        game_state = "PLAYING";
                        cheat_input_text = ""
                    else:
                        cheat_input_text = ""
                except ValueError:
                    cheat_input_text = ""
            elif event.key == pygame.K_ESCAPE:
                game_state = previous_game_state;
                cheat_input_text = ""
            elif event.key == pygame.K_BACKSPACE:
                cheat_input_text = cheat_input_text[:-1]
            elif event.unicode.isdigit() and len(cheat_input_text) < 2:
                cheat_input_text += event.unicode
    input_box = pygame.Rect(WIDTH / 2 - 50, box_rect.y + 120, 100, 40);
    pygame.draw.rect(screen, GREY, input_box)
    input_text_render = cheat_font.render(cheat_input_text, True, LIME_GREEN);
    screen.blit(input_text_render, input_text_render.get_rect(center=input_box.center))


# --- Main Game Controller ---
def main_game_loop():
    global game_state, previous_game_state, current_level, cheat_input_text
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                if game_state != "CHEAT_MENU": previous_game_state = game_state; game_state = "CHEAT_MENU"; print(
                    "Cheat menu activated.")

        if game_state == "INTRO":
            from level_logic import show_intro
            play_music("intro")
            show_intro(screen, clock);
            game_state = "MAIN_MENU"

        elif game_state == "MAIN_MENU":
            play_music("menu")
            draw_main_menu(events)

        elif game_state == "PLAYING":
            play_music("gameplay")
            from level_logic import show_level_transition, show_cutscene
            try:
                if 1 <= current_level <= 3:
                    level_module_name, level_function_name = "level_logic", f"run_level_{current_level}"
                else:
                    level_module_name, level_function_name = f"level{current_level}", "main"

                level_module = importlib.import_module(level_module_name)
                level_function = getattr(level_module, level_function_name)

                print(f"--- Starting Level {current_level} ---")
                level_result = level_function(screen, clock)
                print(f"--- Level {current_level} finished with result: {level_result} ---")

                if level_result == "COMPLETED":
                    if current_level == 1:
                        show_cutscene(screen, clock)
                    elif current_level == 3:
                        show_level_transition(screen, clock, 3, "Nobita and Gian join forces!")
                    elif current_level < MAX_LEVEL:
                        show_level_transition(screen, clock, current_level)
                    current_level += 1
                    if current_level > MAX_LEVEL: game_state = "VICTORY"
                elif level_result == "GAME_OVER":
                    game_state = "GAME_OVER"
                elif level_result == "QUIT_TO_MENU":
                    game_state = "MAIN_MENU"
            except (ImportError, AttributeError) as e:
                print(f"FATAL ERROR: Could not load Level {current_level}. Details: {e}");
                game_state = "MAIN_MENU";
                time.sleep(5)
            except Exception as e:
                print(f"An unexpected error in Level {current_level}: {e}");
                game_state = "MAIN_MENU";
                time.sleep(5)

        elif game_state == "GAME_OVER":
            draw_game_over_screen(events)

        elif game_state == "VICTORY":
            draw_victory_screen(events)

        elif game_state == "CHEAT_MENU":
            draw_cheat_menu(events)

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    show_creator_screen()
    main_game_loop()