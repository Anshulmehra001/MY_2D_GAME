import pygame
import os
import random
import math
# *** FIX: The line below is removed to solve the 'pygame.locals' error ***
# from pygame.locals import *


def main(screen, clock):
    # --- Configuration from main.py ---
    WIDTH, HEIGHT = screen.get_size()
    FPS = 60

    # --- Asset Paths ---
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSET_DIR = os.path.join(CURRENT_DIR, "level9_assets")
    LEVEL8_ASSET_DIR = os.path.join(CURRENT_DIR, "level8_assets")

    # --- Asset Loading ---
    def safe_load(folder, name, scale=None, can_fail=False):
        path = os.path.join(folder, name)
        try:
            img = pygame.image.load(path).convert_alpha()
            if scale: return pygame.transform.scale(img, scale)
            return img
        except pygame.error:
            if can_fail: return None
            print(f"ERROR: Asset not found in Level 9: {path}")
            fallback = pygame.Surface(scale or (50, 50), pygame.SRCALPHA);
            fallback.fill((255, 0, 255))
            return fallback

    # --- Fonts and Colors ---
    WHITE, RED, GREEN, BLACK, GOLD = (255, 255, 255), (200, 0, 0), (0, 200, 0), (0, 0, 0), (255, 215, 0)
    font = pygame.font.SysFont("Arial", 24, bold=True)
    big_font = pygame.font.SysFont("Impact", 60)
    boss_font = pygame.font.SysFont("Impact", 40)
    dialogue_font = pygame.font.SysFont("Georgia", 22, italic=True)
    subtitle_font = pygame.font.SysFont("Arial", 28, bold=True, italic=True)

    # --- Load All Assets ---
    bg_image = safe_load(ASSET_DIR, "bg_level9.png", (WIDTH, HEIGHT))
    nobita_sprite = safe_load(LEVEL8_ASSET_DIR, "nobita_level8.png", (70, 100))
    slash_effect = safe_load(CURRENT_DIR, "sword_slash.png", (80, 40), can_fail=True)
    if slash_effect is None:
        slash_effect = pygame.Surface((80, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(slash_effect, WHITE, (0, 0, 80, 40), 5)

    toriho_sprites = {
        "flying": safe_load(ASSET_DIR, "toriho_flying.png", (150, 130)),
        "powerup": safe_load(ASSET_DIR, "toriho_powerup.png", (150, 130)),
        "ultimate": safe_load(ASSET_DIR, "toriho_ultimatepowerup.png", (160, 140)),
        "ground": safe_load(ASSET_DIR, "toriho_inground.png", (140, 120))
    }
    uncle_sprite = safe_load(ASSET_DIR, "toriho_uncle.png", (80, 100))
    uncle_portrait = pygame.transform.scale(uncle_sprite, (80, 80))
    toriho_portrait = pygame.transform.scale(toriho_sprites["flying"], (80, 80))

    homing_orb_sprite = pygame.Surface((25, 25), pygame.SRCALPHA)
    pygame.draw.circle(homing_orb_sprite, (100, 0, 180), (12, 12), 12)
    chaos_orb_sprite = pygame.Surface((15, 15), pygame.SRCALPHA)
    pygame.draw.circle(chaos_orb_sprite, (200, 0, 50), (7, 7), 7)

    screen_shake_ref = [0]

    # --- Subtitle System ---
    subtitle = {"text": "", "end_time": 0}

    def set_subtitle(text, duration_ms):
        subtitle["text"] = text
        subtitle["end_time"] = pygame.time.get_ticks() + duration_ms

    def draw_subtitle(surface):
        if subtitle["end_time"] > pygame.time.get_ticks():
            text_surf = subtitle_font.render(subtitle["text"], True, WHITE)
            text_rect = text_surf.get_rect(center=(WIDTH / 2, HEIGHT - 100))
            bg_rect = text_rect.inflate(20, 10)
            bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surf.fill((0, 0, 0, 180))
            surface.blit(bg_surf, bg_rect)
            surface.blit(text_surf, text_rect)

    def draw_text_box(surface, text, speaker_name, speaker_portrait, pos):
        box_rect = pygame.Rect(pos[0], pos[1], WIDTH - 100, 100)
        box_surf = pygame.Surface(box_rect.size, pygame.SRCALPHA)
        box_surf.fill((0, 0, 0, 200))
        pygame.draw.rect(box_surf, WHITE, box_surf.get_rect(), width=3, border_radius=15)

        speaker_name_text = font.render(speaker_name, True, GOLD)
        box_surf.blit(speaker_name_text, (110, 10))
        box_surf.blit(speaker_portrait, (15, 10))

        words = text.split(' ')
        lines, current_line = [], ""
        for word in words:
            if dialogue_font.size(current_line + word)[0] < box_rect.width - 130:
                current_line += word + " "
            else:
                lines.append(current_line);
                current_line = word + " "
        lines.append(current_line)
        for i, line in enumerate(lines):
            box_surf.blit(dialogue_font.render(line, True, WHITE), (110, 40 + i * 25))
        surface.blit(box_surf, pos)

    # --- Game Classes ---
    class Player:
        def __init__(self, platforms):
            self.platforms = platforms
            self.image = nobita_sprite
            self.rect = self.image.get_rect(midbottom=(150, self.platforms[0].top))
            self.hitbox = pygame.Rect(0, 0, 45, 90)
            self.hitbox.midbottom = self.rect.midbottom
            self.vel_y, self.dx = 0, 0
            self.jump_power, self.speed = -18, 7
            self.on_ground = True
            self.facing_right = True
            self.health, self.max_health, self.lives = 100, 100, 3
            self.attacking, self.attack_has_hit = False, False
            self.last_attack_time, self.hit_time = 0, 0
            self.is_invincible, self.knockback_speed = False, 0

        def handle_input(self, keys, events):
            self.dx = 0
            if self.knockback_speed > 0:
                self.dx = self.knockback_speed if not self.facing_right else -self.knockback_speed
                self.knockback_speed -= 0.5;
                return
            for e in events:
                # *** FIX: Added 'pygame.' prefix ***
                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE and not self.attacking:
                    if pygame.time.get_ticks() - self.last_attack_time > 400:
                        self.attacking, self.last_attack_time, self.attack_has_hit = True, pygame.time.get_ticks(), False
            # *** FIX: Added 'pygame.' prefix ***
            if keys[pygame.K_LEFT] and self.hitbox.left > 0: self.dx, self.facing_right = -self.speed, False
            if keys[pygame.K_RIGHT] and self.hitbox.right < WIDTH: self.dx, self.facing_right = self.speed, True
            if keys[pygame.K_UP] and self.on_ground: self.vel_y = self.jump_power

        def update(self):
            self.hitbox.x += self.dx
            for plat in self.platforms:
                if self.hitbox.colliderect(plat):
                    if self.dx > 0: self.hitbox.right = plat.left
                    if self.dx < 0: self.hitbox.left = plat.right
            self.vel_y += 0.9
            self.hitbox.y += self.vel_y
            self.on_ground = False
            for plat in self.platforms:
                if self.hitbox.colliderect(plat):
                    if self.vel_y > 0:
                        self.hitbox.bottom, self.on_ground, self.vel_y = plat.top, True, 0
                    elif self.vel_y < 0:
                        self.hitbox.top, self.vel_y = plat.bottom, 0
            self.rect.midbottom = self.hitbox.midbottom
            now = pygame.time.get_ticks()
            if self.attacking and now - self.last_attack_time > 150: self.attacking = False
            if self.is_invincible and now - self.hit_time > 1000: self.is_invincible = False

        def take_damage(self, amount, damage_source_rect):
            if not self.is_invincible:
                self.health -= amount
                self.is_invincible, self.hit_time, self.knockback_speed = True, pygame.time.get_ticks(), 8
                self.facing_right = self.hitbox.centerx < damage_source_rect.centerx
                screen_shake_ref[0] = 15
                if self.health <= 0:
                    self.lives -= 1
                    if self.lives > 0:
                        self.health = self.max_health
                        self.hitbox.midbottom = (WIDTH // 2, self.platforms[0].top)

        def draw(self, surface):
            img = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)
            if not (self.is_invincible and pygame.time.get_ticks() % 200 < 100): surface.blit(img, self.rect)
            hud_bg = pygame.Surface((220, 70), pygame.SRCALPHA);
            hud_bg.fill((0, 0, 0, 120));
            surface.blit(hud_bg, (0, 0))
            pygame.draw.rect(surface, RED, (10, 10, 200, 20))
            pygame.draw.rect(surface, GREEN, (10, 10, 200 * (self.health / self.max_health), 20))
            surface.blit(font.render(f"Lives: {self.lives}", True, WHITE), (10, 35))
            if self.attacking:
                slash_img = slash_effect if self.facing_right else pygame.transform.flip(slash_effect, True, False)
                slash_rect = slash_img.get_rect(center=self.rect.center)
                slash_rect.x += 40 if self.facing_right else -40
                surface.blit(slash_img, slash_rect)

    class Boss:
        def __init__(self, platforms):
            self.platforms = platforms
            self.phase, self.state = 1, "IDLE"
            self.image = toriho_sprites["flying"]
            self.rect = self.image.get_rect(center=(WIDTH / 2, -150))
            self.health, self.max_health, self.alive = 600, 600, True
            self.projectiles = []
            self.last_action_time, self.is_hit, self.hit_flash_end_time = 0, False, 0
            self.bob_angle, self.vel_y, self.telegraph_alpha = 0, 0, 0
            self.has_healed, self.fast_orb_count, self.last_fast_orb_time = False, 0, 0

        def set_image(self, key):
            self.image = toriho_sprites[key];
            self.rect = self.image.get_rect(center=self.rect.center)

        def take_damage(self, amount):
            if self.alive and self.state != "HEALING":
                self.health -= amount;
                self.is_hit, self.hit_flash_end_time = True, pygame.time.get_ticks() + 100
                if self.health <= 0: self.alive, self.health = False, 0

        def update(self, player):
            now = pygame.time.get_ticks()
            if self.alive and self.health <= self.max_health * 0.2 and not self.has_healed:
                self.has_healed, self.state, self.last_action_time = True, "HEALING", now
                set_subtitle("I WILL NOT BE DEFEATED!", 3000);
                self.health += self.max_health * 0.3
            if self.phase == 1 and self.health <= self.max_health * 0.5:
                self.phase, self.state = 2, "IDLE";
                set_subtitle("ENOUGH! FEEL MY TRUE POWER!", 3000)
            if not self.alive:
                self.set_image("ground")
                if self.rect.bottom < self.platforms[0].top:
                    self.vel_y += 1; self.rect.y += self.vel_y
                else:
                    self.rect.bottom, self.vel_y = self.platforms[0].top, 0
                return
            if self.state == "HEALING":
                if now - self.last_action_time > 1500: self.state = "IDLE"
                return
            attack_image_key = "ultimate" if self.phase == 2 else "powerup"
            dist_x = player.hitbox.centerx - self.rect.centerx
            self.bob_angle += 0.05
            if self.phase == 1:
                self.rect.y = 100 + math.sin(self.bob_angle) * 20
                if self.state == "IDLE":
                    self.set_image("flying")
                    if now - self.last_action_time > 1800: self.state, self.last_action_time = random.choice(
                        ["DIVE_PREP", "HOMING_ORBS"]), now
                elif self.state == "DIVE_PREP":
                    self.set_image(attack_image_key)
                    if now - self.last_action_time > 500: self.state = "DIVE"
                elif self.state == "DIVE":
                    self.rect.x += 14 if dist_x > 0 else -14
                    if now - self.last_action_time > 1700: self.state = "IDLE"
                elif self.state == "HOMING_ORBS":
                    self.set_image(attack_image_key)
                    if now - self.last_action_time > 400: self.projectiles.append(
                        Projectile(self.rect.center, target=player)); self.state = "IDLE"
            elif self.phase == 2:
                self.rect.y = 150 + math.sin(self.bob_angle * 2) * 10
                if self.state == "IDLE":
                    self.set_image("flying");
                    self.telegraph_alpha = max(0, self.telegraph_alpha - 15)
                    if now - self.last_action_time > 800: self.state, self.last_action_time = random.choice(
                        ["TELEPORT_PREP", "FAST_ORBS_PREP"]), now
                elif self.state == "TELEPORT_PREP":
                    self.set_image(attack_image_key);
                    self.telegraph_alpha = min(255, self.telegraph_alpha + 25)
                    if self.telegraph_alpha >= 255: self.state = "TELEPORT_ATTACK"
                elif self.state == "TELEPORT_ATTACK":
                    self.set_image(attack_image_key);
                    self.rect.center = (random.randint(100, WIDTH - 100), random.randint(100, 250))
                    for angle in range(0, 360, 18): self.projectiles.append(
                        Projectile(self.rect.center, angle=angle)); self.state = "IDLE"
                elif self.state == "FAST_ORBS_PREP":
                    self.set_image(attack_image_key)
                    if now - self.last_action_time > 300: self.state, self.fast_orb_count, self.last_fast_orb_time = "FAST_ORBS_ATTACK", 3, now
                elif self.state == "FAST_ORBS_ATTACK":
                    if self.fast_orb_count > 0 and now - self.last_fast_orb_time > 150:
                        self.projectiles.append(Projectile(self.rect.center, target=player, speed=7));
                        self.fast_orb_count -= 1;
                        self.last_fast_orb_time = now
                    if self.fast_orb_count <= 0: self.state = "IDLE"
            for p in self.projectiles: p.update(player)
            self.projectiles = [p for p in self.projectiles if screen.get_rect().colliderect(p.rect)]

        def draw(self, surface, player):
            img = self.image if player.hitbox.x > self.rect.x else pygame.transform.flip(self.image, True, False)
            if self.is_hit and pygame.time.get_ticks() < self.hit_flash_end_time:
                mask_surface = pygame.mask.from_surface(img).to_surface(setcolor=WHITE, unsetcolor=(0, 0, 0));
                mask_surface.set_colorkey((0, 0, 0));
                mask_surface.set_alpha(180)
                surface.blit(mask_surface, self.rect)
            else:
                surface.blit(img, self.rect)

            if self.alive:
                bar_w, bar_x, bar_y = WIDTH - 40, 20, HEIGHT - 55
                pygame.draw.rect(surface, BLACK, (bar_x - 5, bar_y - 5, bar_w + 10, 40))
                pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_w, 30))
                health_percentage = self.health / self.max_health if self.max_health > 0 else 0
                pygame.draw.rect(surface, GOLD, (bar_x, bar_y, bar_w * health_percentage, 30))
                surface.blit(boss_font.render("TORIHO, THE SHAPESHIFTER", True, WHITE), (bar_x + 10, bar_y - 2))

            for p in self.projectiles: p.draw(surface)

    class Projectile:
        def __init__(self, pos, target=None, angle=0, speed=None):
            self.pos = list(pos);
            self.target = target;
            self.angle = angle
            self.is_homing = (target is not None)
            self.image = homing_orb_sprite if self.is_homing else chaos_orb_sprite
            self.speed = speed or (5 if self.is_homing else 8)
            self.rect = self.image.get_rect(center=self.pos)

        def update(self, player):
            if self.is_homing:
                dir_vec = pygame.math.Vector2(player.hitbox.center) - self.rect.center
                if dir_vec.length_squared() > 0: dir_vec.scale_to_length(self.speed); self.rect.move_ip(dir_vec)
            else:
                self.rect.x += math.cos(math.radians(self.angle)) * self.speed; self.rect.y += math.sin(
                    math.radians(self.angle)) * self.speed

        def draw(self, surface):
            surface.blit(self.image, self.rect)

    class Ally:
        def __init__(self, platform):
            self.image = uncle_sprite
            self.rect = self.image.get_rect(midbottom=platform.midtop)

        def draw(self, surface):
            surface.blit(self.image, self.rect)

    # --- Game Instance Runner ---
    def run_game_instance():
        platforms = [pygame.Rect(0, HEIGHT - 80, WIDTH, 80), pygame.Rect(20, HEIGHT - 250, 220, 40)]
        player = Player(platforms)
        boss = Boss(platforms)
        ally = Ally(platforms[1])
        game_state, intro_stage, end_alpha = "INTRO", 0, 0

        while True:
            events = pygame.event.get()
            for event in events:
                # *** FIX: Added 'pygame.' prefix ***
                if event.type == pygame.QUIT: return "QUIT_TO_MENU"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: return "QUIT_TO_MENU"
                    if game_state == "INTRO" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        intro_stage += 1
            keys = pygame.key.get_pressed()

            render_surface = pygame.Surface((WIDTH, HEIGHT))
            render_surface.blit(bg_image, (0, 0))

            if game_state == "INTRO":
                if intro_stage == 1:
                    if boss.rect.centery < 100: boss.rect.centery += 4
                elif intro_stage > 1:
                    game_state = "PLAYING"

                player.draw(render_surface)
                boss.draw(render_surface, player)

                if intro_stage == 0:
                    # *** This logic is from YOUR code. Uncle is drawn here. ***

                    draw_text_box(render_surface, "Nobita! You made it! This is Toriho...", "Uncle", uncle_portrait,
                                  (50, HEIGHT - 120))
                elif intro_stage == 1 and boss.rect.centery >= 100:
                    draw_text_box(render_surface, "A mortal? How amusing...", "Toriho", toriho_portrait, (50, 20))

            elif game_state == "PLAYING":
                player.handle_input(keys, events);
                player.update();
                boss.update(player)

                if player.attacking and not player.attack_has_hit and boss.alive and player.rect.inflate(40,
                                                                                                         20).colliderect(
                        boss.rect):
                    boss.take_damage(15);
                    player.attack_has_hit = True
                for p in boss.projectiles[:]:
                    if p.rect.colliderect(player.hitbox):
                        player.take_damage(10, p.rect);
                        boss.projectiles.remove(p)
                if boss.state == "DIVE" and boss.rect.colliderect(player.hitbox):
                    player.take_damage(20, boss.rect)

                if player.lives <= 0: game_state = "GAME_OVER"
                if not boss.alive and boss.vel_y == 0: game_state = "VICTORY"

                player.draw(render_surface)
                boss.draw(render_surface, player)
                draw_subtitle(render_surface)

            elif game_state in ["VICTORY", "GAME_OVER"]:
                player.draw(render_surface)
                boss.draw(render_surface, player)
                if end_alpha < 180: end_alpha += 4
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA);
                overlay.fill((0, 0, 0, end_alpha))
                render_surface.blit(overlay, (0, 0))
                if end_alpha >= 180: return game_state

            if screen_shake_ref[0] > 0:
                screen.blit(render_surface, (random.randint(-5, 5), random.randint(-5, 5)))
                screen_shake_ref[0] -= 1
            else:
                screen.blit(render_surface, (0, 0))
            pygame.display.update()
            clock.tick(FPS)

    # --- Level's Main Controller ---
    while True:
        result = run_game_instance()
        if result == "VICTORY": return "COMPLETED"
        if result == "QUIT_TO_MENU": return "QUIT_TO_MENU"
        if result == "GAME_OVER":
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    # *** FIX: Added 'pygame.' prefix ***
                    if event.type == pygame.QUIT: return "QUIT_TO_MENU"
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r: waiting = False
                        if event.key == pygame.K_ESCAPE: return "QUIT_TO_MENU"
                        if event.key == pygame.K_s: return "COMPLETED"
                screen.fill(BLACK)
                msg = big_font.render("Game Over", True, RED)
                screen.blit(msg, msg.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 60)))
                prompt1 = font.render("Press 'R' to Restart or 'Esc' for Menu", True, WHITE)
                screen.blit(prompt1, prompt1.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 20)))
                prompt2 = font.render("Press 'S' to Skip Level", True, GOLD)
                screen.blit(prompt2, prompt2.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 60)))
                pygame.display.flip()
                clock.tick(FPS)

