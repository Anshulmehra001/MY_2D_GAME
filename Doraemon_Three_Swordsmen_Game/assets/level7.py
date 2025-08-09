import pygame
import sys
import os
import random


def main(screen, clock):
    # --- Local Level Setup ---
    WIDTH, HEIGHT = screen.get_size()
    FPS = 60
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    LEVEL7_ASSETS = os.path.join(CURRENT_DIR, "level7_assets")

    # --- Sound & Asset Loading ---
    def load_sound(path):
        if os.path.exists(path): return pygame.mixer.Sound(path)

        # Create a dummy sound object if file is missing
        class DummySound:
            def play(self): pass

        return DummySound()

    slash_sound = load_sound(os.path.join(CURRENT_DIR, "slash.wav"))
    hit_sound = load_sound(os.path.join(CURRENT_DIR, "hit.wav"))
    player_hit_sound = load_sound(os.path.join(CURRENT_DIR, "hit.wav"))

    def safe_load(folder, name, scale=None):
        path = os.path.join(folder, name)
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, scale) if scale else img
        except:
            print(f"WARN: Missing asset {name} in level7.py. Using placeholder.")
            surface = pygame.Surface(scale or (50, 50), pygame.SRCALPHA);
            surface.fill((255, 0, 255));
            return surface

    bg = safe_load(LEVEL7_ASSETS, "bg_level7.png", (WIDTH, HEIGHT))
    nobita_idle = safe_load(CURRENT_DIR, "nobita_idle.png", (70, 100))
    slash_effect = safe_load(CURRENT_DIR, "sword_slash.png", (80, 40))
    spider1_idle = safe_load(LEVEL7_ASSETS, "spider1_idle.png", (100, 100));
    spider1_attack = safe_load(LEVEL7_ASSETS, "spider1_attack.png", (100, 100));
    spider1_death = safe_load(LEVEL7_ASSETS, "spider1_death.png", (100, 100))
    spider2_idle = safe_load(LEVEL7_ASSETS, "spider2_idle.png", (110, 110));
    spider2_attack = safe_load(LEVEL7_ASSETS, "spider2_move.png", (110, 110));
    spider2_death = spider2_idle
    villain3_idle = safe_load(LEVEL7_ASSETS, "villain3.png", (120, 120));
    villain3_attack = villain3_idle;
    villain3_death = safe_load(LEVEL7_ASSETS, "villain3_death.png", (120, 120))
    web1 = safe_load(LEVEL7_ASSETS, "web1.png", (50, 20));
    web2 = safe_load(LEVEL7_ASSETS, "web2.png", (80, 35))
    WHITE, RED, GREEN, YELLOW, BLACK = (255, 255, 255), (200, 0, 0), (0, 200, 0), (255, 220, 0), (0, 0, 0)
    font = pygame.font.SysFont("Arial", 24, bold=True);
    big_font = pygame.font.SysFont("Impact", 50)

    # --- Classes ---
    class Player:
        def __init__(self):
            self.image = nobita_idle;
            self.rect = self.image.get_rect(midbottom=(100, HEIGHT - 80));
            self.vel_y = 0;
            self.jump_power = -19;
            self.speed = 5
            self.on_ground = True;
            self.facing_right = True;
            self.health = 100;
            self.max_health = 100;
            self.lives = 3;
            self.attacking = False
            self.attack_cooldown = 400;
            self.attack_duration = 150;
            self.attack_start_time = 0;
            self.last_attack_time = 0;
            self.attack_has_hit = False
            self.is_invincible = False;
            self.invincibility_duration = 1200;
            self.hit_time = 0

        def handle_input(self, keys, events):
            for e in events:
                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE and not self.attacking:
                    now = pygame.time.get_ticks()
                    if now - self.last_attack_time > self.attack_cooldown:
                        self.attacking = True;
                        self.attack_has_hit = False;
                        self.attack_start_time = now;
                        self.last_attack_time = now
                        if slash_sound: slash_sound.play()
            if self.is_invincible and pygame.time.get_ticks() - self.hit_time < 200: return
            if keys[pygame.K_LEFT] and self.rect.left > 0: self.rect.x -= self.speed; self.facing_right = False
            if keys[pygame.K_RIGHT] and self.rect.right < WIDTH: self.rect.x += self.speed; self.facing_right = True
            if keys[pygame.K_UP] and self.on_ground: self.vel_y = self.jump_power; self.on_ground = False

        def update(self):
            self.vel_y += 0.9;
            self.rect.y += self.vel_y
            if self.rect.bottom >= HEIGHT - 80: self.rect.bottom = HEIGHT - 80; self.on_ground = True; self.vel_y = 0
            now = pygame.time.get_ticks()
            if self.attacking and now - self.attack_start_time > self.attack_duration: self.attacking = False
            if self.is_invincible and now - self.hit_time > self.invincibility_duration: self.is_invincible = False

        def take_damage(self, amount):
            if not self.is_invincible:
                self.health -= amount;
                self.is_invincible = True;
                self.hit_time = pygame.time.get_ticks()
                if player_hit_sound: player_hit_sound.play()
                if self.health <= 0:
                    self.lives -= 1
                    if self.lives > 0: self.health = self.max_health; self.rect.midbottom = (100,
                                                                                             HEIGHT - 80); self.is_invincible = True; self.hit_time = pygame.time.get_ticks()

        def draw(self, surface):
            img = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)
            if not (self.is_invincible and pygame.time.get_ticks() % 200 < 100): surface.blit(img, self.rect)
            if self.attacking:
                slash_rect = slash_effect.get_rect(centery=self.rect.centery)
                if self.facing_right:
                    slash_rect.left = self.rect.right - 20;
                    surface.blit(slash_effect, slash_rect)
                else:
                    flipped_slash = pygame.transform.flip(slash_effect, True,
                                                          False);
                    slash_rect.right = self.rect.left + 20;
                    surface.blit(
                        flipped_slash, slash_rect)
            if self.health < self.max_health:
                bar_width = 80;
                bar_height = 8;
                bar_x = self.rect.centerx - bar_width / 2;
                bar_y = self.rect.top - 15
                health_ratio = max(0, self.health / self.max_health)
                health_color = GREEN if health_ratio > 0.6 else YELLOW if health_ratio > 0.3 else RED
                pygame.draw.rect(surface, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(surface, health_color, (bar_x, bar_y, bar_width * health_ratio, bar_height))
                pygame.draw.rect(surface, BLACK, (bar_x, bar_y, bar_width, bar_height), 1)
            ui_bar_width = 200;
            ui_bar_height = 20;
            ui_bar_x = 10;
            ui_bar_y = 10
            ui_health_ratio = max(0, self.health / self.max_health)
            ui_health_color = GREEN if ui_health_ratio > 0.6 else YELLOW if ui_health_ratio > 0.3 else RED
            pygame.draw.rect(surface, (40, 40, 40), (ui_bar_x, ui_bar_y, ui_bar_width, ui_bar_height))
            pygame.draw.rect(surface, ui_health_color,
                             (ui_bar_x, ui_bar_y, ui_bar_width * ui_health_ratio, ui_bar_height))
            pygame.draw.rect(surface, BLACK, (ui_bar_x, ui_bar_y, ui_bar_width, ui_bar_height), 2)
            surface.blit(font.render(f"Lives: {self.lives}", True, WHITE), (15, 35))

    class Web:
        def __init__(self, x, y, speed, image, direction):
            self.image = pygame.transform.flip(image, True, False) if direction < 0 else image;
            self.rect = self.image.get_rect(center=(x, y));
            self.speed = speed * direction;
            self.damage = 15

        def update(self): self.rect.x += self.speed

        def draw(self, surface): surface.blit(self.image, self.rect)

    class Boss:
        def __init__(self, idle, attack, death, web, health, move=False, melee=False, speed=2, is_strong=False,
                     evade=False, can_get_tired=False):
            self.idle_image, self.attack_image, self.death_image = idle, attack, death;
            self.web_image = web;
            self.rect = self.idle_image.get_rect(midbottom=(WIDTH - 150, HEIGHT - 80))
            self.webs = [];
            self.health = self.max_health = health;
            self.move, self.melee, self.speed = move, melee, speed;
            self.is_strong = is_strong;
            self.evade = evade
            self.can_get_tired = can_get_tired;
            self.alive = True;
            self.state = "IDLE";
            self.state_timer = 0;
            self.ranged_cooldown = 2200;
            self.melee_cooldown = 1500
            self.last_attack_time = 0;
            self.death_time = 0;
            self.evade_direction = 1;
            self.melee_slash_rect = None

        def attack(self, player):
            if not self.alive or self.state != "IDLE": return
            now = pygame.time.get_ticks();
            distance = abs(self.rect.centerx - player.rect.centerx)
            if self.melee and distance < 100 and now - self.last_attack_time > self.melee_cooldown:
                self.state = "ATTACKING";
                self.state_timer = now;
                self.last_attack_time = now
                if self.rect.inflate(30, 0).colliderect(player.rect): player.take_damage(
                    30 if self.is_strong else 20); self.melee_slash_rect = slash_effect.get_rect(
                    center=player.rect.center)
            elif self.web_image and now - self.last_attack_time > self.ranged_cooldown and distance > 80:
                self.state = "ATTACKING";
                self.state_timer = now;
                self.last_attack_time = now;
                self.webs.append(Web(self.rect.centerx, self.rect.centery, 6, self.web_image,
                                     -1 if player.rect.centerx < self.rect.centerx else 1))

        def update(self, player):
            if not self.alive: return
            now = pygame.time.get_ticks();
            self.attack(player)
            if self.state == "ATTACKING":
                if now - self.state_timer > 400: self.melee_slash_rect = None; self.state = "EVADING" if self.evade else "IDLE"; self.evade_direction = -1 if player.rect.centerx < self.rect.centerx else 1; self.state_timer = now
            elif self.state == "EVADING":
                self.rect.x += self.speed * 2 * self.evade_direction
                if now - self.state_timer > 350 or not (
                        0 < self.rect.centerx < WIDTH): self.state = "TIRED" if self.can_get_tired else "IDLE"; self.state_timer = now
            elif self.state == "TIRED":
                if now - self.state_timer > 2000: self.state = "IDLE"
            elif self.state == "IDLE" and self.move and abs(player.rect.centerx - self.rect.centerx) > 100:
                self.rect.x += self.speed if player.rect.centerx > self.rect.centerx else -self.speed
            for web in self.webs: web.update()
            self.webs = [w for w in self.webs if 0 < w.rect.centerx < WIDTH]
            if self.health <= 0 and self.alive: self.alive, self.death_time = False, now

        def draw(self, surface):
            img = self.death_image if not self.alive else self.attack_image if self.state == "ATTACKING" else self.idle_image
            surface.blit(img, self.rect)
            if self.state == "TIRED" and pygame.time.get_ticks() % 200 > 100:
                tint = pygame.Surface(img.get_size(), pygame.SRCALPHA);
                tint.fill((255, 220, 0, 80));
                surface.blit(tint, self.rect)
            for web in self.webs: web.draw(surface)
            if self.melee_slash_rect: surface.blit(slash_effect, self.melee_slash_rect)
            if self.alive:
                ratio = max(0, self.health / self.max_health)
                color = GREEN if ratio > 0.6 else YELLOW if ratio > 0.3 else RED
                bar_rect = pygame.Rect(WIDTH // 2 - 150, 20, 300, 20)
                health_rect = pygame.Rect(bar_rect.x, bar_rect.y, int(bar_rect.width * ratio), bar_rect.height)
                pygame.draw.rect(surface, (40, 40, 40), bar_rect)
                pygame.draw.rect(surface, color, health_rect)
                pygame.draw.rect(surface, BLACK, bar_rect, 2)

    def run_game_instance():
        player = Player()
        bosses = [Boss(spider1_idle, spider1_attack, spider1_death, web1, 100),
                  Boss(spider2_idle, spider2_attack, spider2_death, web2, 150, True, True),
                  Boss(villain3_idle, villain3_attack, villain3_death, None, 200, True, True, 2.5, False, True, True)]
        current_boss_index = 0
        intro_time = pygame.time.get_ticks()

        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return "QUIT_TO_MENU"

            keys = pygame.key.get_pressed()
            player.handle_input(keys, events);
            player.update()

            if player.lives <= 0: return "GAME_OVER"

            # --- FIX: This line now correctly returns "VICTORY" which the outer loop is expecting. ---
            if current_boss_index >= len(bosses): return "VICTORY"

            boss = bosses[current_boss_index];
            boss.update(player)

            if player.attacking and not player.attack_has_hit and boss.alive:
                slash_hitbox = pygame.Rect(player.rect.centerx, player.rect.centery - 20, 70, 40)
                if not player.facing_right: slash_hitbox.right = player.rect.centerx
                if slash_hitbox.colliderect(boss.rect):
                    damage_to_deal = 10
                    if boss.state == "TIRED" and boss.can_get_tired: damage_to_deal = 25
                    boss.health -= damage_to_deal
                    player.attack_has_hit = True
                    if hit_sound: hit_sound.play()

            for web in boss.webs[:]:
                if web.rect.colliderect(player.rect): player.take_damage(web.damage); boss.webs.remove(web)

            if not boss.alive and pygame.time.get_ticks() - boss.death_time > 2000:
                current_boss_index += 1
                if current_boss_index < len(
                        bosses): player.is_invincible = True; player.hit_time = pygame.time.get_ticks()

            screen.blit(bg, (0, 0));
            player.draw(screen)
            if current_boss_index < len(bosses): bosses[current_boss_index].draw(screen)
            if pygame.time.get_ticks() - intro_time < 4000:
                subtitle = font.render("Use Arrow Keys to Move, UP to Jump, and SPACE to Attack", True, WHITE)
                screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, HEIGHT - 40))

            pygame.display.update();
            clock.tick(FPS)

    # --- Level Start and Restart Loop ---
    while True:
        game_result = run_game_instance()
        if game_result == "QUIT_TO_MENU": return "QUIT_TO_MENU"
        if game_result == "VICTORY": return "COMPLETED"
        if game_result == "GAME_OVER":
            screen.fill((0, 0, 0))
            msg = big_font.render("Game Over", True, RED);
            screen.blit(msg, msg.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 40)))
            prompt = font.render("Press 'R' to Restart or 'Esc' to Quit to Menu", True, WHITE);
            screen.blit(prompt, prompt.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 20)))
            pygame.display.flip()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r: waiting = False
                        if event.key == pygame.K_ESCAPE: return "QUIT_TO_MENU"