import pygame
import sys
import os
import random
import math


def main(screen, clock):
    # --- Local Level Setup ---
    WIDTH, HEIGHT = screen.get_size()
    FPS = 60
    GROUND_HEIGHT = 50
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSET_DIR = os.path.join(CURRENT_DIR, "level8_assets")

    # --- Asset Loading ---
    class DummySound:
        def play(self): pass

        def stop(self): pass

    def load_sound(folder, name):
        path = os.path.join(folder, name)
        if os.path.exists(path): return pygame.mixer.Sound(path)
        return DummySound()

    def safe_load(folder, name, scale=None):
        path = os.path.join(folder, name)
        try:
            img = pygame.image.load(path).convert_alpha()
            if scale: return pygame.transform.scale(img, scale)
            return img
        except pygame.error:
            print(f"FATAL ERROR: Asset not found at path: {path}")
            return None

    # --- Load All Assets ---
    # BGM is handled by main.py. Only SFX are loaded here.
    slash_sound = load_sound(CURRENT_DIR, "slash.wav")
    player_hit_sound = load_sound(CURRENT_DIR, "hit.wav")

    initial_screen_img = safe_load(ASSET_DIR, "initail.png", (WIDTH, HEIGHT))
    backgrounds = [safe_load(ASSET_DIR, f"bg_{i}.png", (WIDTH, HEIGHT)) for i in range(1, 4)]
    nobita_sprite = safe_load(ASSET_DIR, "nobita_level8.png", (70, 100))
    slash_effect = safe_load(CURRENT_DIR, "sword_slash.png", (80, 40))
    enemy_sprites = {
        "spear": safe_load(ASSET_DIR, "enemy_1_level8.png", (100, 120)),
        "gargoyle": safe_load(ASSET_DIR, "enemy_2_level8.png", (120, 120)),
        "ghost": safe_load(ASSET_DIR, "enemy_ghost.png", (120, 120))
    }
    ghost_orb_sprite = pygame.Surface((20, 20), pygame.SRCALPHA);
    pygame.draw.circle(ghost_orb_sprite, (180, 0, 255), (10, 10), 10)

    if any(v is None for v in
           [initial_screen_img, nobita_sprite, slash_effect] + backgrounds + list(enemy_sprites.values())):
        return "QUIT_TO_MENU"

    # --- Fonts and Colors ---
    WHITE, RED, GREEN, BLACK = (255, 255, 255), (200, 0, 0), (0, 200, 0), (0, 0, 0)
    font = pygame.font.SysFont("Arial", 24, bold=True);
    big_font = pygame.font.SysFont("Impact", 60)
    prompt_font = pygame.font.SysFont("Arial", 30, bold=True);
    subtitle_font = pygame.font.SysFont("Georgia", 26, italic=True)

    # --- Game Classes ---
    screen_shake_ref = [0]

    class Player:
        def __init__(self):
            self.image = nobita_sprite;
            self.rect = self.image.get_rect(midbottom=(150, HEIGHT - GROUND_HEIGHT));
            self.vel_y = 0;
            self.jump_power = -20;
            self.speed = 6
            self.on_ground = True;
            self.facing_right = True;
            self.health = 100;
            self.max_health = 100;
            self.lives = 3;
            self.attacking = False
            self.attack_cooldown = 400;
            self.attack_duration = 150;
            self.last_attack_time = 0;
            self.is_invincible = False;
            self.invincibility_duration = 1000
            self.hit_time = 0;
            self.knockback_speed = 0;
            self.attack_has_hit = False

        def handle_input(self, keys, events):
            if self.knockback_speed > 0: return
            for e in events:
                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE and not self.attacking:
                    now = pygame.time.get_ticks()
                    if now - self.last_attack_time > self.attack_cooldown: self.attacking = True; self.last_attack_time = now; self.attack_has_hit = False; slash_sound.play()
            if keys[pygame.K_LEFT] and self.rect.left > 0: self.rect.x -= self.speed; self.facing_right = False
            if keys[pygame.K_RIGHT] and self.rect.right < WIDTH: self.rect.x += self.speed; self.facing_right = True
            if keys[pygame.K_UP] and self.on_ground: self.vel_y = self.jump_power; self.on_ground = False

        def update(self):
            if self.knockback_speed > 0: self.rect.x += self.knockback_speed if not self.facing_right else -self.knockback_speed; self.knockback_speed -= 0.5
            self.vel_y += 0.9;
            self.rect.y += self.vel_y
            if self.rect.bottom >= HEIGHT - GROUND_HEIGHT: self.rect.bottom = HEIGHT - GROUND_HEIGHT; self.on_ground = True; self.vel_y = 0
            now = pygame.time.get_ticks()
            if self.attacking and now - self.last_attack_time > self.attack_duration: self.attacking = False
            if self.is_invincible and now - self.hit_time > self.invincibility_duration: self.is_invincible = False

        def take_damage(self, amount, enemy_rect):
            if not self.is_invincible:
                self.health -= amount;
                self.is_invincible = True;
                self.hit_time = pygame.time.get_ticks();
                self.knockback_speed = 8
                self.facing_right = self.rect.centerx < enemy_rect.centerx;
                screen_shake_ref[0] = 15;
                player_hit_sound.play()
                if self.health <= 0:
                    self.lives -= 1
                    if self.lives > 0: self.health = self.max_health; self.rect.midbottom = (150,
                                                                                             HEIGHT - GROUND_HEIGHT)

        def draw(self, surface):
            img = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)
            if not (self.is_invincible and pygame.time.get_ticks() % 200 < 100): surface.blit(img, self.rect)
            pygame.draw.rect(surface, RED, (10, 10, 200, 20));
            pygame.draw.rect(surface, GREEN, (10, 10, 200 * (self.health / self.max_health), 20))
            surface.blit(font.render(f"Lives: {self.lives}", True, WHITE), (10, 35))
            if self.attacking:
                slash_img = slash_effect if self.facing_right else pygame.transform.flip(slash_effect, True, False)
                slash_rect = slash_img.get_rect(center=self.rect.center);
                slash_rect.x += 40 if self.facing_right else -40;
                surface.blit(slash_img, slash_rect)

    class Enemy:
        def __init__(self, name, health):
            self.image = enemy_sprites[name];
            self.rect = self.image.get_rect(midbottom=(WIDTH - 150, HEIGHT - GROUND_HEIGHT));
            self.health = self.max_health = health;
            self.alive = True;
            self.name = name
            self.speed = 4 if name == "spear" else 2.5;
            self.vel_y = 0;
            self.projectiles = [];
            self.last_action_time = 0;
            self.is_hit = False;
            self.hit_flash_end_time = 0
            self.state = "NORMAL";
            self.enraged_triggered = False;
            self.base_y = self.rect.y;
            self.bob_angle = 0

        def take_damage(self, amount):
            if self.alive: self.health -= amount; self.is_hit = True; self.hit_flash_end_time = pygame.time.get_ticks() + 100
            if self.health <= 0: self.alive = False

        def update(self, player):
            if not self.alive: return
            now = pygame.time.get_ticks();
            dist_x = player.rect.centerx - self.rect.centerx
            if self.name == "spear":
                if self.state == "NORMAL":
                    if now - self.last_action_time > 1500: self.state = "CHARGING"; self.last_action_time = now
                elif self.state == "CHARGING":
                    self.rect.x += self.speed if dist_x > 0 else -self.speed
                    if now - self.last_action_time > 2000: self.state = "RETREATING"; self.last_action_time = now
                elif self.state == "RETREATING":
                    self.rect.x -= self.speed if dist_x > 0 else -self.speed
                    if now - self.last_action_time > 1000: self.state = "NORMAL"; self.last_action_time = now

            elif self.name == "gargoyle":
                # Check for enrage trigger once
                if self.health < self.max_health * 0.4 and not self.enraged_triggered:
                    self.state = "ENRAGED_ASCEND"
                    self.enraged_triggered = True

                # --- State Machine Logic ---
                if self.state == "NORMAL":
                    on_ground = self.rect.bottom >= HEIGHT - GROUND_HEIGHT
                    self.vel_y += 0.8
                    self.rect.y += self.vel_y

                    if on_ground:
                        # Prevent constant small shakes from gravity
                        if self.vel_y > 1:
                            screen_shake_ref[0] = 10
                        self.vel_y = 0
                        # Jump attack timer
                        if now - self.last_action_time > 1800:
                            self.vel_y = -18  # Jump up
                            self.last_action_time = now
                    # Move towards player while in the air
                    if not on_ground:
                        self.rect.x += self.speed if dist_x > 0 else -self.speed

                # --- Corrected Enraged State Logic ---
                if self.state == "ENRAGED_ASCEND":
                    self.rect.y -= 4
                    # Transition to the next state when high enough
                    if self.rect.top <= 50:
                        self.state = "ENRAGED_DIVE_AIM"

                elif self.state == "ENRAGED_DIVE_AIM":
                    # Move horizontally to align with the player
                    self.rect.x += self.speed if dist_x > 0 else -self.speed
                    # Transition to the next state when aligned
                    if abs(dist_x) < 20:
                        self.state = "ENRAGED_DIVE_BOMB"
                        self.vel_y = 0  # Reset vertical velocity for the dive

                elif self.state == "ENRAGED_DIVE_BOMB":
                    self.vel_y += 1.5  # Accelerate downwards
                    self.rect.y += self.vel_y
                    # When it hits the ground, it should go back to its normal attack pattern
                    # It will automatically do this because the "NORMAL" state logic handles gravity
                    # and ground checks. When it lands, it will transition back to its jump attacks.
                    if self.rect.bottom >= HEIGHT - GROUND_HEIGHT:
                        screen_shake_ref[0] = 15  # Big shake for the dive bomb
                        self.state = "NORMAL"  # Return to normal jump attacks
                        self.last_action_time = now  # Reset timer to prevent immediate jump

            elif self.name == "ghost":
                self.bob_angle = (self.bob_angle + 0.04) % (2 * math.pi);
                self.rect.y = self.base_y + math.sin(self.bob_angle) * 30
                if now - self.last_action_time > 2000:
                    if random.choice(["shoot", "shoot", "teleport"]) == "shoot":
                        for _ in range(3): self.projectiles.append(
                            Projectile(self.rect.center, 1 if dist_x > 0 else -1))
                    else:
                        self.rect.centerx = random.randint(100, WIDTH - 100)
                    self.last_action_time = now

            for p in self.projectiles: p.update()
            self.projectiles = [p for p in self.projectiles if p.rect.colliderect(screen.get_rect())];
            self.rect.clamp_ip(screen.get_rect())
            if self.rect.bottom > HEIGHT - GROUND_HEIGHT: self.rect.bottom = HEIGHT - GROUND_HEIGHT

        def draw(self, surface, player):
            if self.alive:
                img = self.image
                if self.name == "gargoyle" and "ENRAGED" in self.state: img = self.image.copy(); img.fill(
                    (100, 0, 0, 100), special_flags=pygame.BLEND_RGBA_ADD)
                img_flipped = img if player.rect.x > self.rect.x else pygame.transform.flip(img, True, False)
                if self.is_hit and pygame.time.get_ticks() < self.hit_flash_end_time:
                    mask = pygame.mask.from_surface(img_flipped);
                    mask_surface = mask.to_surface(setcolor=WHITE, unsetcolor=(0, 0, 0));
                    mask_surface.set_colorkey((0, 0, 0));
                    mask_surface.set_alpha(180);
                    surface.blit(mask_surface, self.rect)
                else:
                    self.is_hit = False;
                    surface.blit(img_flipped, self.rect)
                bar_w = self.rect.width * 0.8;
                bar_x = self.rect.centerx - bar_w / 2
                pygame.draw.rect(surface, RED, (bar_x, self.rect.top - 15, bar_w, 7));
                pygame.draw.rect(surface, GREEN,
                                 (bar_x, self.rect.top - 15, bar_w * (self.health / self.max_health), 7))
                for p in self.projectiles: p.draw(surface)

    class Projectile:
        def __init__(self, pos, direction):
            self.image = ghost_orb_sprite;
            self.rect = self.image.get_rect(center=pos);
            self.vel_x = (7 + random.uniform(-1, 1)) * direction;
            self.vel_y = random.uniform(-1, 1);
            self.damage = 15

        def update(self): self.rect.x += self.vel_x; self.rect.y += self.vel_y

        def draw(self, surface): surface.blit(self.image, self.rect)

    def run_game_instance():
        player, enemies, current_enemy_index = Player(), [Enemy("spear", 120), Enemy("gargoyle", 180),
                                                          Enemy("ghost", 250)], 0
        game_state = "START_SCREEN";
        transition_timer = 0

        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: return "QUIT_TO_MENU"
                    if game_state == "START_SCREEN" and event.key == pygame.K_RETURN: game_state = "PLAYING"

            keys = pygame.key.get_pressed()
            if game_state == "PLAYING":
                player.handle_input(keys, events);
                player.update()
                boss = enemies[current_enemy_index];
                boss.update(player)
                if player.attacking and boss.alive and not player.attack_has_hit and player.rect.inflate(80,
                                                                                                         20).colliderect(
                    boss.rect):
                    boss.take_damage(25);
                    player.attack_has_hit = True
                for p in boss.projectiles[:]:
                    if p.rect.colliderect(player.rect): player.take_damage(p.damage, p.rect); boss.projectiles.remove(p)
                if boss.name != "ghost" and boss.rect.colliderect(player.rect): player.take_damage(20, boss.rect)
                if player.lives <= 0: return "GAME_OVER"
                if not boss.alive:
                    if current_enemy_index < len(enemies) - 1:
                        game_state = "TRANSITION";
                        transition_timer = pygame.time.get_ticks()
                    else:
                        return "VICTORY"

            render_surface = pygame.Surface((WIDTH, HEIGHT))
            if game_state == "START_SCREEN":
                render_surface.blit(initial_screen_img, (0, 0))
                subtitle = subtitle_font.render("The path is guarded. Defeat the three sentinels!", True, WHITE);
                render_surface.blit(subtitle, subtitle.get_rect(center=(WIDTH / 2, HEIGHT - 120)))
                if pygame.time.get_ticks() % 1000 < 500:
                    prompt = prompt_font.render("Press ENTER to Start", True, WHITE);
                    render_surface.blit(prompt, prompt.get_rect(center=(WIDTH / 2, HEIGHT - 70)))
            elif game_state == "TRANSITION":
                render_surface.blit(backgrounds[current_enemy_index], (0, 0))
                overlay = pygame.Surface((WIDTH, HEIGHT));
                overlay.set_alpha(min(255, (pygame.time.get_ticks() - transition_timer) / 4));
                render_surface.blit(overlay, (0, 0))
                if pygame.time.get_ticks() - transition_timer > 1000: current_enemy_index += 1; player.health = player.max_health; game_state = "PLAYING"
            elif game_state == "PLAYING":
                render_surface.blit(backgrounds[current_enemy_index], (0, 0))
                player.draw(render_surface);
                enemies[current_enemy_index].draw(render_surface, player)

            if screen_shake_ref[0] > 0:
                screen.blit(render_surface, (random.randint(-5, 5), random.randint(-5, 5)));
                screen_shake_ref[0] -= 1
            else:
                screen.blit(render_surface, (0, 0))
            pygame.display.update();
            clock.tick(FPS)

    # --- Level Start and Restart Loop ---
    while True:
        game_result = run_game_instance()

        if game_result == "VICTORY":
            return "COMPLETED"
        if game_result == "QUIT_TO_MENU":
            return "QUIT_TO_MENU"

        if game_result == "GAME_OVER":
            screen.fill(BLACK)
            msg = big_font.render("Game Over", True, RED)
            screen.blit(msg, msg.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 40)))
            prompt = font.render("Press 'R' to Restart or 'Esc' to Quit to Menu", True, WHITE)
            screen.blit(prompt, prompt.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 20)))
            pygame.display.flip()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r: waiting = False
                        if event.key == pygame.K_ESCAPE: return "QUIT_TO_MENU"
