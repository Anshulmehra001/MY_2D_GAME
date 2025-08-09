# assets/level4.py
import pygame
import sys
import os
from math import copysign


def main(screen, clock):
    # --- Local Level Setup ---
    WIDTH, HEIGHT = screen.get_size()
    GROUND_Y = HEIGHT - 50
    FPS = 60
    PLAYER_SPEED = 200
    COLLAPSE_DISTANCE = 80
    font = pygame.font.SysFont("lucidaconsole", 24, bold=True)
    big_font = pygame.font.SysFont("lucidaconsole", 48, bold=True)
    BASE = os.path.dirname(os.path.abspath(__file__))

    # --- Asset Loading ---
    def load_image(name, size=None):
        try:
            image = pygame.image.load(os.path.join(BASE, name)).convert_alpha()
            if size: image = pygame.transform.scale(image, size)
            return image
        except pygame.error as e:
            print(f"Error loading image {name} in level4.py: {e}")
            surf = pygame.Surface(size or (50, 50), pygame.SRCALPHA);
            surf.fill((255, 0, 255));
            return surf

    # --- Sounds ---
    slash_sound = pygame.mixer.Sound(os.path.join(BASE, "slash.wav"))
    hit_sound = pygame.mixer.Sound(os.path.join(BASE, "hit.wav"))

    bg = load_image("background_level4.png", (1600, HEIGHT))
    nobita_img = load_image("nobita_idle.png", (64, 64))
    gian_idle = load_image("gian_idle.png", (64, 64))
    gian_run = load_image("gian_run.png", (64, 64))
    gian_attack = load_image("gian_attack.png", (80, 80))
    sandman_idle = load_image("sandman.png", (80, 80))
    sandman_left = load_image("sandman_leftattack.png", (80, 80))
    sandman_right = load_image("sandman_rightattack.png", (80, 80))
    sandman_defeat = load_image("sandman_defeat.png", (80, 80))
    wall_img = load_image("wall.png", (40, 80))
    sword_splash_img = load_image("sword_slash.png", (100, 100))

    # --- Classes (Based on your original code) ---
    class Player(pygame.sprite.Sprite):
        def __init__(self, name, frames, attack_img, x, is_nobita=True):
            super().__init__();
            self.name = name;
            self.frames = frames;
            self.attack_img = attack_img;
            self.image = self.frames[0]
            self.world_x = float(x);
            self.rect = self.image.get_rect(midbottom=(self.world_x, GROUND_Y));
            self.alive = True
            self.attacking = False;
            self.attack_start = 0;
            self.attack_dur = 300;
            self.speed = PLAYER_SPEED;
            self.facing_right = True
            self.attack_cooldown = 500;
            self.last_attack = 0;
            self.sword_splash = None;
            self.is_nobita = is_nobita
            self.walk_frame = 0;
            self.walk_timer = 0

        def update(self, keys, is_ctrl, target, walls, dt):
            now = pygame.time.get_ticks()
            if self.sword_splash and now - self.sword_splash[1] > 200: self.sword_splash = None
            if self.attacking and now - self.attack_start >= self.attack_dur: self.attacking = False
            if not self.alive: return
            dx = 0
            if is_ctrl:
                dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed
                if dx > 0:
                    self.facing_right = True
                elif dx < 0:
                    self.facing_right = False
                if dx != 0 and len(self.frames) > 1:
                    self.walk_timer += dt * 1000
                    if self.walk_timer > 200: self.walk_frame = (self.walk_frame + 1) % (
                                len(self.frames) - 1); self.walk_timer = 0
            elif target:
                follow_distance = 80
                target_pos = target.world_x - follow_distance if target.facing_right else target.world_x + follow_distance
                if abs(self.world_x - target_pos) > 5:
                    dx = self.speed if self.world_x < target_pos else -self.speed
                self.facing_right = target.facing_right
            if is_ctrl and not self.attacking and keys[
                pygame.K_SPACE] and now - self.last_attack >= self.attack_cooldown:
                self.attacking = True;
                self.attack_start = now;
                self.last_attack = now;
                slash_sound.play()
                if self.is_nobita:
                    splash_x = self.world_x + self.rect.width if self.facing_right else self.world_x - sword_splash_img.get_width()
                    self.sword_splash = (pygame.transform.flip(sword_splash_img, not self.facing_right, False), now,
                                         (splash_x, self.rect.centery - 50))
            move = dx * dt
            if move != 0:
                next_world_x = self.world_x + move
                spec_rect_screen = self.rect.copy();
                spec_rect_screen.x += move
                if not any(spec_rect_screen.colliderect(w.rect) for w in walls):
                    self.world_x = next_world_x
            if not self.attacking:
                self.image = self.frames[self.walk_frame + 1] if dx != 0 and len(self.frames) > 1 else self.frames[0]
            else:
                self.image = self.attack_img
            if not self.facing_right: self.image = pygame.transform.flip(self.image, True, False)

    class Wall(pygame.sprite.Sprite):
        def __init__(self, wx):
            super().__init__();
            self.world_x = wx;
            self.image = wall_img;
            self.rect = self.image.get_rect(midbottom=(wx, GROUND_Y))

        def update(self, cam_x): self.rect.x = self.world_x - cam_x; self.rect.bottom = GROUND_Y

    class Enemy(pygame.sprite.Sprite):
        def __init__(self, wx, wy, left, right, order):
            super().__init__();
            self.images = {"idle": sandman_idle, "att_left": sandman_left, "att_right": sandman_right,
                           "defeat": sandman_defeat}
            self.image = self.images["idle"];
            self.world_x = float(wx);
            self.rect = self.image.get_rect(midbottom=(int(wx), GROUND_Y))
            self.left, self.right = left, right;
            self.speed = 100.0;
            self.dir = 1;
            self.order = order;
            self.alive = True
            self.attack_range = 50;
            self.attack_cooldown = 1000;
            self.last_attack = 0;
            self.attacking = False
            self.patrolling = True;
            self.defeat_time = 0;
            self.defeat_duration = 500;
            self.damage_range = 30
            self.attack_anim_start = 0;
            self.attack_anim_duration = 300;
            self.attack_delivered = False

        def update(self, walls, cam_x, chase, hero_world_x, active_enemy, dt):
            now = pygame.time.get_ticks()
            if not self.alive:
                if now - self.defeat_time < self.defeat_duration: self.image = self.images["defeat"]
                return False
            if self.attacking:
                if now - self.attack_anim_start < self.attack_anim_duration:
                    self.image = self.images["att_left"] if hero_world_x < self.world_x else self.images["att_right"]
                    if not self.attack_delivered and abs(
                        self.world_x - hero_world_x) <= self.damage_range: self.attack_delivered = True; return True
                else:
                    self.attacking = False; self.image = self.images["idle"]; self.attack_delivered = False
                return False
            if self.order != active_enemy: self.image = self.images["idle"]; return False
            if walls and self.patrolling:
                move_x = self.speed * self.dir * dt;
                self.world_x += move_x
                if self.world_x <= self.left or self.world_x >= self.right: self.dir *= -1; self.world_x = max(
                    self.left, min(self.world_x, self.right))
                self.rect.x = int(self.world_x - cam_x);
                self.image = self.images["idle"];
                return False
            if not walls: self.patrolling = False
            if not self.patrolling:
                if abs(hero_world_x - self.world_x) > self.attack_range:
                    move_x = copysign(self.speed, hero_world_x - self.world_x) * dt;
                    self.world_x += move_x
            if abs(self.world_x - hero_world_x) <= self.attack_range and now - self.last_attack >= self.attack_cooldown:
                self.attacking = True;
                self.attack_anim_start = now;
                self.last_attack = now;
                self.attack_delivered = False;
                slash_sound.play()
            self.rect.x = int(self.world_x - cam_x)
            return False

        def defeat(self):
            if self.alive: self.alive = False; self.defeat_time = pygame.time.get_ticks(); self.image = self.images[
                "defeat"]; self.rect.bottom = GROUND_Y

    def run_game_instance():
        nobita = Player("Nobita", [nobita_img], nobita_img, 100, True)
        gian = Player("Gian", [gian_idle, gian_run], gian_attack, 160, False)
        players = pygame.sprite.Group(nobita, gian);
        walls = pygame.sprite.Group(Wall(400), Wall(1100))
        enemies = [Enemy(460, GROUND_Y, 450, 600, 1), Enemy(800, GROUND_Y, 750, 950, 2)]
        controlled, follower = nobita, gian;
        camera_x = 0;
        wall_break_time = None
        active_enemy_order = 1;
        message = "";
        message_time = 0;
        bg_width = bg.get_width()
        level_start_time = pygame.time.get_ticks()

        while True:
            dt = clock.tick(FPS) / 1000.0
            if dt > 0.1: dt = 0.1
            keys = pygame.key.get_pressed()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE: return "QUIT_TO_MENU"
                    if ev.key == pygame.K_1:
                        controlled, follower = nobita, gian
                    elif ev.key == pygame.K_2:
                        controlled, follower = gian, nobita

            controlled.update(keys, True, None, walls, dt);
            follower.update(keys, False, controlled, walls, dt)
            now = pygame.time.get_ticks();
            chase = bool(wall_break_time and now - wall_break_time > 500)

            for e in enemies:
                if e.update(walls, camera_x, chase, controlled.world_x, active_enemy_order, dt):
                    hit_sound.play();
                    return "GAME_OVER"

            controlled_screen_rect = controlled.rect.copy();
            controlled_screen_rect.x = controlled.world_x - camera_x
            if walls and controlled.name == "Gian" and controlled.attacking:
                for wall in walls:
                    if abs(controlled_screen_rect.centerx - wall.rect.centerx) <= COLLAPSE_DISTANCE:
                        walls.remove(wall);
                        wall_break_time = now;
                        message = "Gian smashed the wall!";
                        message_time = now + 2000;
                        hit_sound.play()
                        for e in enemies: e.patrolling = False
                        break
            if controlled.name == "Nobita" and controlled.sword_splash:
                splash_img_ref, _, splash_pos = controlled.sword_splash
                splash_rect_on_screen = splash_img_ref.get_rect(topleft=(splash_pos[0] - camera_x, splash_pos[1]))
                for e in enemies:
                    if e.order == active_enemy_order and e.alive and splash_rect_on_screen.colliderect(e.rect):
                        e.defeat();
                        active_enemy_order += 1;
                        message = f"Enemy {e.order} defeated!";
                        message_time = now + 2000;
                        hit_sound.play()

            if all(not e.alive for e in enemies):
                if controlled.world_x > bg_width - 150: return "COMPLETED"
                message = "All enemies defeated! Move to the right to escape!";
                message_time = now + 2000

            cam_target = controlled.world_x - WIDTH // 3;
            camera_x = max(0, min(cam_target, bg_width - WIDTH))

            screen.blit(bg, (-camera_x, 0));
            walls.update(camera_x);
            walls.draw(screen)
            for e in enemies:
                if e.alive or (now - e.defeat_time < e.defeat_duration): screen.blit(e.image, e.rect)
            if controlled.sword_splash: img, _, pos = controlled.sword_splash; screen.blit(img,
                                                                                           (pos[0] - camera_x, pos[1]))
            for player in players:
                if player.alive: player.rect.x = player.world_x - camera_x; screen.blit(player.image, player.rect)
            if now < message_time: screen.blit(font.render(message, True, (255, 255, 255)),
                                               (WIDTH // 2 - font.size(message)[0] // 2, 50))

            ui_surf = pygame.Surface((180, 70), pygame.SRCALPHA);
            ui_surf.fill((0, 0, 0, 120));
            screen.blit(ui_surf, (5, 5))
            nob_ind = "> NOBITA" if controlled == nobita else "  NOBITA";
            gian_ind = "> GIAN" if controlled == gian else "  GIAN"
            screen.blit(font.render(nob_ind, True, (70, 130, 180)), (15, 15));
            screen.blit(font.render(gian_ind, True, (200, 60, 60)), (15, 45))

            if now - level_start_time < 5000:
                control_text = "Arrows: Move | SPACE: Attack | 1/2: Switch"
                text_surf = font.render(control_text, True, (255, 255, 255));
                text_rect = text_surf.get_rect(center=(WIDTH / 2, HEIGHT - 30))
                bg_rect = text_rect.inflate(20, 10);
                bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA);
                bg_surf.fill((0, 0, 0, 150));
                screen.blit(bg_surf, bg_rect);
                screen.blit(text_surf, text_rect)

            pygame.display.flip()

    # --- Level Start and Restart Loop ---
    while True:
        result = run_game_instance()
        if result == "QUIT_TO_MENU" or result == "COMPLETED":
            return result
        elif result == "GAME_OVER":
            screen.fill((0, 0, 0))
            msg = big_font.render("Game Over", True, (255, 0, 0));
            screen.blit(msg, msg.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 40)))
            prompt = font.render("Press 'R' to Restart or 'Esc' to Quit to Menu", True, (255, 255, 255));
            screen.blit(prompt, prompt.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 20)))
            pygame.display.flip()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r: waiting = False  # Breaks to outer loop to restart
                        if event.key == pygame.K_ESCAPE: return "QUIT_TO_MENU"
