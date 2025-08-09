# assets/level_logic.py
import pygame
import time
import os
import sys


# --- Shared Story/Transition Functions ---
def draw_subtitle(screen, text, font, y=400):
    WIDTH = screen.get_width()
    box = pygame.Surface((WIDTH - 100, 60), pygame.SRCALPHA);
    box.fill((0, 0, 0, 180));
    screen.blit(box, (50, y))
    text_render = font.render(text, True, (255, 255, 255));
    screen.blit(text_render, text_render.get_rect(center=(WIDTH // 2, y + 30)))


def fade_out(screen, duration=500):
    WIDTH, HEIGHT = screen.get_size()
    fade_surface = pygame.Surface((WIDTH, HEIGHT));
    fade_surface.fill((0, 0, 0))
    for alpha in range(0, 255, 15):
        fade_surface.set_alpha(alpha);
        screen.blit(fade_surface, (0, 0));
        pygame.display.update();
        pygame.time.delay(int(duration / (255 / 15)))


def wait_or_skip(duration_ms):
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < duration_ms:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                print("Intro skipped.")
                return True
    return False


def show_intro(screen, clock):
    WIDTH, HEIGHT = screen.get_size()
    ASSET_DIR = os.path.dirname(os.path.abspath(__file__))
    font = pygame.font.SysFont("lucidaconsole", 24)
    intro1 = pygame.transform.scale(pygame.image.load(os.path.join(ASSET_DIR, "intro_scene_1.png")).convert(),
                                    (WIDTH, HEIGHT))
    intro2 = pygame.transform.scale(pygame.image.load(os.path.join(ASSET_DIR, "intro_scene_2.png")).convert(),
                                    (WIDTH, HEIGHT))
    scene1 = pygame.transform.scale(pygame.image.load(os.path.join(ASSET_DIR, "scene1.png")).convert(), (WIDTH, HEIGHT))
    scene2 = pygame.transform.scale(pygame.image.load(os.path.join(ASSET_DIR, "scene2.png")).convert(), (WIDTH, HEIGHT))

    screen.blit(intro1, (0, 0));
    pygame.display.update()
    if wait_or_skip(3000): fade_out(screen, 200); return True
    fade_out(screen)

    screen.blit(intro2, (0, 0));
    draw_subtitle(screen, "A dream filled with swords, magic, and a hidden kingdom.", font);
    pygame.display.update()
    if wait_or_skip(4000): fade_out(screen, 200); return True
    fade_out(screen)

    screen.blit(scene1, (0, 0));
    pygame.display.update()
    if wait_or_skip(3000): fade_out(screen, 200); return True
    fade_out(screen)

    screen.blit(scene2, (0, 0));
    draw_subtitle(screen, "The adventure is about to begin…", font);
    pygame.display.update()
    if wait_or_skip(3000): fade_out(screen, 200); return True
    fade_out(screen)
    return False


def show_level_transition(screen, clock, level, special_message=None):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.SysFont("lucidaconsole", 24)
    screen.fill((0, 0, 0))
    msg = special_message if special_message else f"Level {level} Completed!"
    message = font.render(msg, True, (255, 255, 0));
    screen.blit(message, message.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
    sub = font.render(f"Get ready for Level {level + 1}...", True, (255, 255, 255));
    screen.blit(sub, sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
    pygame.display.update();
    pygame.time.wait(3000);
    fade_out(screen)


def show_cutscene(screen, clock):
    WIDTH, HEIGHT = screen.get_size()
    ASSET_DIR = os.path.dirname(os.path.abspath(__file__))
    font = pygame.font.SysFont("lucidaconsole", 24)
    cutscene_img = pygame.transform.scale(
        pygame.image.load(os.path.join(ASSET_DIR, "cutscene_nobita_gets_sword.png")).convert(), (WIDTH, HEIGHT))
    screen.blit(cutscene_img, (0, 0));
    draw_subtitle(screen, "Nobita receives the legendary armor and sword!", font);
    pygame.display.update();
    pygame.time.wait(4000);
    fade_out(screen)


# --- Base Gameplay Function for Levels 1-3 ---
def _run_level_base(screen, clock, level_params):
    # This outer loop handles the RESTART functionality
    while True:
        WIDTH, HEIGHT = screen.get_size();
        FPS = 60;
        ASSET_DIR = os.path.dirname(os.path.abspath(__file__))
        bg_img, nobita_img, enemy_img = level_params["bg_img"], level_params["nobita_img"], level_params["enemy_img"]
        total_enemies, dual_wave, hit_delay, player_start_health = level_params["total_enemies"], level_params[
            "dual_wave"], level_params["hit_delay"], level_params["player_health"]
        slash_img = pygame.transform.scale(
            pygame.image.load(os.path.join(ASSET_DIR, "sword_slash.png")).convert_alpha(), (64, 64))
        slash_sound = pygame.mixer.Sound(os.path.join(ASSET_DIR, "slash.wav"));
        hit_sound = pygame.mixer.Sound(os.path.join(ASSET_DIR, "hit.wav"))
        velocity = 5;
        nobita_x, nobita_y = 100, HEIGHT - 100;
        health = max_health = player_start_health
        last_hit = 0;
        is_attacking = False;
        attack_timer = 0;
        has_hit = False

        enemies = []
        for i in range(total_enemies):
            enemy_data = {
                "x": WIDTH + (i * 120), "y": HEIGHT - 100, "target_x": 500 + ((i % 2) * 90),
                "health": 5 if level_params["level"] == 3 else 2,  # BUG FIX: Level 3 enemies now have 5 health
                "max_health": 5 if level_params["level"] == 3 else 2,  # BUG FIX: Level 3 enemies now have 5 max_health
                "alive": i < (2 if level_params["level"] == 3 else 1), "active": i == 0, "walking_in": i == 0,
                "state": "default", "defeated": False
            }
            enemies.append(enemy_data)

        def draw_health_bar(x, y, hp, max_hp):
            bar_w, bar_h = 60, 8;
            fill = int((hp / max_hp) * bar_w)
            pygame.draw.rect(screen, (255, 0, 0), (x, y, bar_w, bar_h));
            pygame.draw.rect(screen, (0, 255, 0), (x, y, fill, bar_h))

        # This is the main gameplay loop for one life/attempt
        game_running = True
        while game_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return "QUIT_TO_MENU"
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and nobita_x > 0: nobita_x -= velocity
            if keys[pygame.K_RIGHT] and nobita_x < WIDTH - 64: nobita_x += velocity
            if keys[
                pygame.K_SPACE] and not is_attacking: is_attacking = True; has_hit = False; attack_timer = pygame.time.get_ticks(); slash_sound.play()
            if is_attacking and pygame.time.get_ticks() - attack_timer > 300: is_attacking = False
            if is_attacking and not has_hit:
                slash_rect = pygame.Rect(nobita_x + 60, nobita_y + 10, 40, 40)
                for i, enemy in enumerate(enemies):
                    if not enemy["alive"]: continue
                    enemy_rect = pygame.Rect(enemy["x"], enemy["y"], 64, 64)
                    if slash_rect.colliderect(enemy_rect):
                        hit_sound.play();
                        has_hit = True
                        enemy["health"] -= 1  # BUG FIX: Health now decreases correctly for all levels
                        if enemy["health"] <= 0:
                            enemy["alive"] = False
                            if level_params["level"] == 3: enemy["defeated"] = True  # Mark as defeated for drawing
                            next1, next2 = i + 1, i + 2
                            if dual_wave and next1 < total_enemies and next2 < total_enemies:
                                enemies[next1]["alive"] = True;
                                enemies[next1]["walking_in"] = True
                                enemies[next2]["alive"] = True;
                                enemies[next2]["walking_in"] = True
                            elif next1 < total_enemies:
                                enemies[next1]["alive"] = True; enemies[next1]["walking_in"] = True
            now = pygame.time.get_ticks()
            for enemy in enemies:
                if not enemy["alive"]: continue
                if enemy["walking_in"]:
                    if enemy["x"] > enemy["target_x"]:
                        enemy["x"] -= (3 if level_params["level"] == 3 else 2)
                    else:
                        enemy["x"] = enemy["target_x"]; enemy["walking_in"] = False; enemy["active"] = True
                elif enemy["active"]:
                    if level_params["level"] == 2:
                        enemy["x"] -= 1
                    elif level_params["level"] == 3:
                        dist = abs(nobita_x - enemy["x"]);
                        move_dir = -1 if nobita_x < enemy["x"] else 1
                        enemy[
                            "state"] = "left_attack" if move_dir == -1 and dist < 80 else "right_attack" if move_dir == 1 and dist < 80 else "default"
                        enemy["x"] += move_dir
                    player_rect = pygame.Rect(nobita_x, nobita_y, 64, 64);
                    enemy_rect = pygame.Rect(enemy["x"], enemy["y"], 64, 64)
                    if player_rect.colliderect(
                        enemy_rect) and now - last_hit > hit_delay: health -= 1; last_hit = now; hit_sound.play()
            screen.blit(bg_img, (0, 0));
            screen.blit(nobita_img, (nobita_x, nobita_y));
            draw_health_bar(nobita_x, nobita_y - 15, health, max_health)
            for enemy in enemies:
                if enemy["alive"] or enemy["defeated"]:
                    sprite = enemy_img["defeat"] if enemy["defeated"] else (
                        enemy_img[enemy["state"]] if level_params["level"] == 3 else enemy_img)
                    screen.blit(sprite, (enemy["x"], enemy["y"]))
                    if not enemy["defeated"]: draw_health_bar(enemy["x"], enemy["y"] - 15, enemy["health"],
                                                              enemy["max_health"])
            if is_attacking: screen.blit(slash_img, (nobita_x + 60, nobita_y + 10))
            pygame.display.update()

            if health <= 0:
                game_running = False  # Exit the gameplay loop to show the game over screen
            if all(not e["alive"] for e in enemies):
                return "COMPLETED"
            clock.tick(FPS)

        # --- Game Over Screen for this level ---
        font_big = pygame.font.SysFont("arial", 48);
        font_small = pygame.font.SysFont("arial", 24)
        screen.fill((0, 0, 0))
        text = font_big.render("Game Over", True, (255, 0, 0));
        screen.blit(text, text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 40)))
        restart = font_small.render("Press R to Restart or ESC to Quit to Menu", True, (255, 255, 255));
        screen.blit(restart, restart.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 20)))
        pygame.display.update()

        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        waiting_for_input = False  # This will cause the outer `while True` to loop, restarting the level
                    if event.key == pygame.K_ESCAPE:
                        return "QUIT_TO_MENU"


# --- Level-Specific Launchers ---
def run_level_1(screen, clock):
    ASSET_DIR = os.path.dirname(os.path.abspath(__file__))
    params = {"level": 1, "bg_img": pygame.transform.scale(
        pygame.image.load(os.path.join(ASSET_DIR, "background_forest.png")).convert(), screen.get_size()),
              "nobita_img": pygame.transform.scale(
                  pygame.image.load(os.path.join(ASSET_DIR, "nobita.png")).convert_alpha(), (64, 64)),
              "enemy_img": pygame.transform.scale(
                  pygame.image.load(os.path.join(ASSET_DIR, "enemy_knight.png")).convert_alpha(), (64, 64)),
              "total_enemies": 4, "dual_wave": False, "hit_delay": 1000, "player_health": 3}
    return _run_level_base(screen, clock, params)


def run_level_2(screen, clock):
    ASSET_DIR = os.path.dirname(os.path.abspath(__file__))
    params = {"level": 2, "bg_img": pygame.transform.scale(
        pygame.image.load(os.path.join(ASSET_DIR, "background_level2.png")).convert(), screen.get_size()),
              "nobita_img": pygame.transform.scale(
                  pygame.image.load(os.path.join(ASSET_DIR, "nobita_idle.png")).convert_alpha(), (64, 64)),
              "enemy_img": pygame.transform.scale(
                  pygame.image.load(os.path.join(ASSET_DIR, "enemy_level2.png")).convert_alpha(), (64, 64)),
              "total_enemies": 8, "dual_wave": True, "hit_delay": 1000, "player_health": 3}
    return _run_level_base(screen, clock, params)


def run_level_3(screen, clock):
    ASSET_DIR = os.path.dirname(os.path.abspath(__file__))
    params = {"level": 3, "bg_img": pygame.transform.scale(
        pygame.image.load(os.path.join(ASSET_DIR, "background_level3.png")).convert(), screen.get_size()),
              "nobita_img": pygame.transform.scale(
                  pygame.image.load(os.path.join(ASSET_DIR, "gian_idle.png")).convert_alpha(), (80, 80)),
              "enemy_img": {"default": pygame.transform.scale(
                  pygame.image.load(os.path.join(ASSET_DIR, "sandman.png")).convert_alpha(), (72, 72)),
                            "left_attack": pygame.transform.scale(
                                pygame.image.load(os.path.join(ASSET_DIR, "sandman_leftattack.png")).convert_alpha(),
                                (72, 72)),
                            "right_attack": pygame.transform.scale(
                                pygame.image.load(os.path.join(ASSET_DIR, "sandman_rightattack.png")).convert_alpha(),
                                (72, 72)),
                            "defeat": pygame.transform.scale(
                                pygame.image.load(os.path.join(ASSET_DIR, "sandman_defeat.png")).convert_alpha(),
                                (72, 72))},
              "total_enemies": 4, "dual_wave": True, "hit_delay": 500,
              "player_health": 3}  # BUG FIX: total_enemies is now 4
    return _run_level_base(screen, clock, params)