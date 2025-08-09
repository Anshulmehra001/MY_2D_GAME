import pygame
import sys
import os
import random
import math


def main(screen, clock):
    # --- Configuration (Derived from main.py's screen object) ---
    WIDTH, HEIGHT = screen.get_size()
    FPS = 60
    GROUND_Y = HEIGHT - 60

    # --- Asset Path Configuration (FIXED) ---
    # This new logic correctly finds the asset folders because we know
    # this script (level10.py) is located INSIDE the main 'assets' folder.
    ASSET_DIR = os.path.dirname(os.path.abspath(__file__))

    # The sub-folders are inside the current directory.
    LEVEL10_ASSET_DIR = os.path.join(ASSET_DIR, "level10_assets")
    LEVEL8_ASSET_DIR = os.path.join(ASSET_DIR, "level8_assets")

    # --- Asset Loading Utilities ---
    def safe_load(folder, name, scale=None, can_fail=False):
        path = os.path.join(folder, name)
        try:
            img = pygame.image.load(path)
            img = img.convert_alpha() if name.lower().endswith('.png') else img.convert()
            if scale: return pygame.transform.scale(img, scale)
            return img
        except pygame.error:
            if can_fail: return None
            print(f"--- LEVEL 10 FATAL ERROR ---\nCould not find resource: {path}")
            return None

    class DummySound:
        def play(self, loops=0): pass

        def stop(self): pass

        def set_volume(self, vol): pass

    def load_sound(folder, name, volume):
        path = os.path.join(folder, name)
        if os.path.exists(path):
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)
            return sound
        return DummySound()

    # --- Sounds ---
    slash_sound = load_sound(ASSET_DIR, "slash.wav", 0.5)
    player_hit_sound = load_sound(ASSET_DIR, "player_hit.wav", 0.8)
    boss_hit_sound = load_sound(ASSET_DIR, "boss_hit.wav", 0.6)
    orb_fire_sound = load_sound(ASSET_DIR, "orb_fire.wav", 0.7)
    laser_sound = load_sound(ASSET_DIR, "laser.wav", 0.8)

    # --- Colors ---
    WHITE, RED, GREEN, BLACK, GOLD, GREY, ORANGE, PURPLE = (255, 255, 255), (200, 0, 0), (0, 200, 0), (0, 0, 0), (255,
                                                                                                                  215,
                                                                                                                  0), (
        100, 100, 100), (255, 140, 0), (148, 0, 211)

    # --- Load All Assets ---
    bg_phase1 = safe_load(LEVEL10_ASSET_DIR, "first_bg.jpeg", (WIDTH, HEIGHT))
    bg_phase2 = safe_load(LEVEL10_ASSET_DIR, "flying_background.png", (WIDTH, HEIGHT))
    bg_phase3 = safe_load(LEVEL10_ASSET_DIR, "last_bg.png", (WIDTH, HEIGHT))
    bg_initial = safe_load(LEVEL10_ASSET_DIR, "initialoffinallevel.png", (WIDTH, HEIGHT))
    nobita_sprite = safe_load(LEVEL8_ASSET_DIR, "nobita_level8.png", (70, 100))
    slash_effect = safe_load(ASSET_DIR, "sword_slash.png", (80, 40), can_fail=True)

    if any(asset is None for asset in [bg_phase1, bg_phase2, bg_phase3, bg_initial, nobita_sprite]):
        return "QUIT_TO_MENU"

    if not slash_effect:
        slash_effect = pygame.Surface((80, 40), pygame.SRCALPHA);
        pygame.draw.ellipse(slash_effect, WHITE, (0, 0, 80, 40), 5)

    boss_sprites = {
        "ground_idle": safe_load(LEVEL10_ASSET_DIR, "villain1.png", (180, 160)),
        "ground_attack": safe_load(LEVEL10_ASSET_DIR, "villain5.png", (180, 160)),
        "fly_idle": safe_load(LEVEL10_ASSET_DIR, "villain7.png", (180, 160)),
        "shadow_orb": safe_load(LEVEL10_ASSET_DIR, "villain4.png", (190, 170)),
        "beam_prep": safe_load(LEVEL10_ASSET_DIR, "villain8.png", (180, 160)),
        "beam_fire": safe_load(LEVEL10_ASSET_DIR, "villain9.png", (200, 160)),
        "fire_burst": safe_load(LEVEL10_ASSET_DIR, "villain10.png", (180, 160)),
        "transition": safe_load(LEVEL10_ASSET_DIR, "villain11.png", (190, 170)),
        "defeated": safe_load(LEVEL10_ASSET_DIR, "villain3.png", (160, 140))
    }
    if any(sprite is None for sprite in boss_sprites.values()):
        return "QUIT_TO_MENU"

    shadow_orb_sprite = pygame.Surface((30, 30), pygame.SRCALPHA);
    pygame.draw.circle(shadow_orb_sprite, PURPLE, (15, 15), 15);
    pygame.draw.circle(shadow_orb_sprite, BLACK, (15, 15), 10)
    fire_orb_sprite = pygame.Surface((20, 20), pygame.SRCALPHA);
    pygame.draw.circle(fire_orb_sprite, ORANGE, (10, 10), 10);
    pygame.draw.circle(fire_orb_sprite, RED, (10, 10), 6)
    energy_blast_sprite = pygame.transform.rotozoom(fire_orb_sprite, 0, 1.5)
    shockwave_sprite = pygame.Surface((60, 20), pygame.SRCALPHA);
    pygame.draw.ellipse(shockwave_sprite, PURPLE, shockwave_sprite.get_rect(), width=4)
    boss_portrait = pygame.Surface((80, 80), pygame.SRCALPHA);
    boss_portrait.blit(boss_sprites["fly_idle"], (-50, -30))
    nobita_portrait = pygame.transform.scale(nobita_sprite, (60, 80))

    font = pygame.font.SysFont("Arial", 24, bold=True);
    boss_font = pygame.font.SysFont("Impact", 40);
    dialogue_font = pygame.font.SysFont("Georgia", 22, italic=True)
    subtitle_font = pygame.font.SysFont("Arial", 28, bold=True, italic=True)

    screen_shake = 0
    subtitle = {"text": "", "end_time": 0}
    platforms = [pygame.Rect(0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y)]

    def set_subtitle(text, duration_ms):
        subtitle["text"] = text;
        subtitle["end_time"] = pygame.time.get_ticks() + duration_ms

    def draw_subtitle(surface):
        if subtitle["end_time"] > pygame.time.get_ticks():
            text_surf = subtitle_font.render(subtitle["text"], True, GOLD);
            text_rect = text_surf.get_rect(center=(WIDTH / 2, HEIGHT - 80))
            bg_rect = text_rect.inflate(20, 10);
            bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA);
            bg_surf.fill((0, 0, 0, 150));
            surface.blit(bg_surf, bg_rect);
            surface.blit(text_surf, text_rect)

    def draw_text_box(surface, text, speaker_name, speaker_portrait):
        box_rect = pygame.Rect(50, HEIGHT - 140, WIDTH - 100, 120);
        pygame.draw.rect(surface, (0, 0, 0, 200), box_rect, border_radius=15);
        pygame.draw.rect(surface, WHITE, box_rect, width=3, border_radius=15)
        speaker_name_text = font.render(speaker_name, True, GOLD);
        surface.blit(speaker_name_text, (box_rect.x + 110, box_rect.y + 10));
        surface.blit(speaker_portrait, (box_rect.x + 15, box_rect.y + 20))
        words = text.split(' ');
        lines = [];
        current_line = ""
        for word in words:
            if dialogue_font.size(current_line + word)[0] < box_rect.width - 130:
                current_line += word + " "
            else:
                lines.append(current_line); current_line = word + " "
        lines.append(current_line)
        for i, line in enumerate(lines): surface.blit(dialogue_font.render(line, True, WHITE),
                                                      (box_rect.x + 110, box_rect.y + 45 + i * 25))

    class Player:
        def __init__(self):
            self.image = nobita_sprite;
            self.rect = self.image.get_rect();
            self.hitbox = pygame.Rect(0, 0, 45, 90);
            self.hitbox.midbottom = (150, GROUND_Y)
            self.rect.midbottom = self.hitbox.midbottom;
            self.vel_y = 0;
            self.jump_power = -18;
            self.speed = 7;
            self.on_ground = True;
            self.facing_right = True
            self.health = 100;
            self.max_health = 100;
            self.lives = 3;
            self.attacking = False;
            self.attack_cooldown = 400;
            self.attack_duration = 150
            self.last_attack_time = 0;
            self.is_invincible = False;
            self.invincibility_duration = 1000;
            self.hit_time = 0;
            self.attack_has_hit = False
            self.is_flying = False;
            self.has_power_up = False

        def grant_power_up(self):
            self.has_power_up = True

        def set_flying_mode(self, fly_enabled):
            self.is_flying = fly_enabled
            if fly_enabled: self.vel_y = 0; self.hitbox.centery = GROUND_Y - 100; platforms.clear()

        def handle_input(self, keys, events):
            dx, dy = 0, 0
            if self.is_flying:
                if keys[pygame.K_LEFT]: dx = -self.speed
                if keys[pygame.K_RIGHT]: dx = self.speed
                if keys[pygame.K_UP]: dy = -self.speed
                if keys[pygame.K_DOWN]: dy = self.speed
                self.hitbox.move_ip(dx, dy);
                self.hitbox.clamp_ip(screen.get_rect())
            else:
                if keys[pygame.K_LEFT]: dx = -self.speed
                if keys[pygame.K_RIGHT]: dx = self.speed
                if keys[pygame.K_UP] and self.on_ground: self.vel_y = self.jump_power
                self.hitbox.x += dx
            if dx != 0: self.facing_right = dx > 0
            for e in events:
                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE and not self.attacking:
                    now = pygame.time.get_ticks()
                    if now - self.last_attack_time > self.attack_cooldown: self.attacking = True; self.last_attack_time = now; self.attack_has_hit = False; slash_sound.play()

        def update(self):
            nonlocal screen_shake
            if not self.is_flying:
                self.vel_y += 0.9;
                self.hitbox.y += self.vel_y;
                self.on_ground = False
                for plat in platforms:
                    if self.hitbox.colliderect(
                        plat) and self.vel_y > 0: self.hitbox.bottom = plat.top; self.on_ground = True; self.vel_y = 0
                if self.hitbox.top > HEIGHT: self.take_damage(10); self.hitbox.midbottom = (150,
                                                                                            GROUND_Y); self.vel_y = 0
            self.rect.midbottom = self.hitbox.midbottom
            now = pygame.time.get_ticks()
            if self.attacking and now - self.last_attack_time > self.attack_duration: self.attacking = False
            if self.is_invincible and now - self.hit_time > self.invincibility_duration: self.is_invincible = False

        def take_damage(self, amount):
            nonlocal screen_shake
            if not self.is_invincible:
                self.health -= amount;
                self.is_invincible = True;
                self.hit_time = pygame.time.get_ticks();
                screen_shake = 15;
                player_hit_sound.play()
                if self.health <= 0:
                    self.lives -= 1
                    if self.lives > 0: self.health = self.max_health; self.hitbox.midbottom = (150, GROUND_Y)

        def draw(self, surface):
            img = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)
            if self.has_power_up and pygame.time.get_ticks() % 600 < 300:
                aura_surf = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA);
                pygame.draw.ellipse(aura_surf, (255, 223, 0, 100), aura_surf.get_rect());
                surface.blit(aura_surf, (self.rect.x - 10, self.rect.y - 10))
            if not (self.is_invincible and pygame.time.get_ticks() % 200 < 100): surface.blit(img, self.rect)
            hud_bg = pygame.Surface((220, 70), pygame.SRCALPHA);
            hud_bg.fill((0, 0, 0, 120));
            surface.blit(hud_bg, (0, 0))
            pygame.draw.rect(surface, (139, 0, 0), (10, 10, 200, 20));
            pygame.draw.rect(surface, GREEN, (10, 10, max(0, 200 * (self.health / self.max_health)), 20))
            surface.blit(font.render(f"Lives: {self.lives}", True, WHITE), (10, 35))
            if self.attacking:
                slash_img = slash_effect if self.facing_right else pygame.transform.flip(slash_effect, True, False)
                slash_rect = slash_img.get_rect(center=self.rect.center);
                slash_rect.x += 40 if self.facing_right else -40
                surface.blit(slash_img, slash_rect)

    class FinalBoss:
        def __init__(self):
            self.image = boss_sprites["ground_idle"];
            self.rect = self.image.get_rect(midbottom=(WIDTH - 150, GROUND_Y));
            self.health = 2000;
            self.max_health = 2000;
            self.alive = True
            self.projectiles = [];
            self.lasers = [];
            self.hazards = [];
            self.state = "IDLE";
            self.last_action_time = 0;
            self.is_hit = False
            self.hit_flash_end_time = 0;
            self.bob_angle = 0;
            self.vel_y = 0;
            self.entered = False;
            self.facing_right = False

        def set_sprite(self, key):
            if self.image != boss_sprites[key]: center = self.rect.center; self.image = boss_sprites[
                key]; self.rect = self.image.get_rect(center=center)

        def take_damage(self, amount):
            if self.alive and self.state != "BEAM_FIRE": self.health -= amount; self.is_hit = True; self.hit_flash_end_time = pygame.time.get_ticks() + 100; boss_hit_sound.play()
            if self.health <= 0: self.alive = False; self.health = 0

        def update(self, player, current_phase):
            now = pygame.time.get_ticks()
            if not self.alive:
                self.set_sprite("defeated");
                if self.rect.bottom < HEIGHT - 20:
                    self.vel_y += 0.5; self.rect.y += self.vel_y
                else:
                    self.rect.bottom = HEIGHT - 20; self.vel_y = 0
                return
            self.facing_right = player.hitbox.centerx > self.rect.centerx
            if current_phase == 1:
                self.update_ground(player, now)
            else:
                self.update_flying(player, now, current_phase)
            for p in self.projectiles: p.update(player)
            self.projectiles = [p for p in self.projectiles if p.is_active]
            for l in self.lasers: l.update()
            self.lasers = [l for l in self.lasers if now < l.end_time]
            for h in self.hazards: h.update()
            self.hazards = [h for h in self.hazards if h.is_active]

        def update_ground(self, player, now):
            self.rect.bottom = GROUND_Y
            if self.state == "IDLE":
                self.set_sprite("ground_idle")
                if now - self.last_action_time > 1800: self.state = random.choice(
                    ["TELEPORT", "ENERGY_BLAST", "SHOCKWAVE", "SHADOW_SPIKES"]); self.last_action_time = now
            elif self.state == "TELEPORT":
                if now - self.last_action_time > 500: self.rect.centerx = random.choice(
                    [150, WIDTH - 150]); self.state = "IDLE"; self.last_action_time = now
            elif self.state == "ENERGY_BLAST":
                self.set_sprite("ground_attack");
                if now - self.last_action_time > 600: self.projectiles.append(
                    Projectile('energy', self.rect.center, target=player,
                               speed=10)); self.state = "IDLE"; self.last_action_time = now; orb_fire_sound.play()
            elif self.state == "SHOCKWAVE":
                self.set_sprite("ground_attack")
                if now - self.last_action_time > 400: self.projectiles.append(
                    Projectile('shockwave', self.rect.midbottom, speed=8,
                               facing_right=self.facing_right)); self.state = "IDLE"; self.last_action_time = now; orb_fire_sound.play()
            elif self.state == "SHADOW_SPIKES":
                self.set_sprite("ground_attack")
                if now - self.last_action_time > 700: self.hazards.append(ArenaHazard('spikes',
                                                                                      pos=(player.hitbox.centerx,
                                                                                           GROUND_Y))); self.state = "IDLE"; self.last_action_time = now

        def update_flying(self, player, now, current_phase):
            target_y = 100 if current_phase == 2 else player.hitbox.centery;
            self.rect.y += (target_y - self.rect.y) * 0.02
            self.rect.bottom = min(self.rect.bottom, HEIGHT - 20)
            self.bob_angle = (self.bob_angle + 0.04) % (2 * math.pi);
            self.rect.y += math.sin(self.bob_angle) * 0.5
            if self.state == "IDLE":
                self.set_sprite("fly_idle")
                cooldown = 1500 if current_phase == 2 else 900
                if now - self.last_action_time > cooldown:
                    attacks = ["SHADOW_ORBS", "BEAM_PREP"]
                    if current_phase == 3: attacks.append("FIRE_BURST")
                    self.state = random.choice(attacks);
                    self.last_action_time = now
            elif self.state == "TRANSITION":
                self.set_sprite("transition")
                if now - self.last_action_time > 2000: self.state = "IDLE"
            elif self.state == "SHADOW_ORBS":
                self.set_sprite("shadow_orb")
                if now - self.last_action_time > 500:
                    count = 3 if current_phase == 2 else 5
                    for i in range(count): self.projectiles.append(
                        Projectile('shadow', self.rect.center, target=player, angle_offset=(i - count // 2) * 10,
                                   speed=6));
                    self.state = "IDLE";
                    self.last_action_time = now;
                    orb_fire_sound.play()
            elif self.state == "BEAM_PREP":
                self.set_sprite("beam_prep")
                if now - self.last_action_time > 1000: self.state = "BEAM_FIRE"; self.last_action_time = now; self.lasers.append(
                    LaserBeam(player.hitbox.y)); laser_sound.play()
            elif self.state == "BEAM_FIRE":
                self.set_sprite("beam_fire")
                if now - self.last_action_time > 800: self.lasers.clear(); self.state = "IDLE"; self.last_action_time = now
            elif self.state == "FIRE_BURST":
                self.set_sprite("transition")
                if now - self.last_action_time > 600:
                    for angle in range(0, 360, 30): self.projectiles.append(
                        Projectile('fire', self.rect.center, angle=angle, speed=9))
                    self.state = "IDLE";
                    self.last_action_time = now;
                    orb_fire_sound.play()

        def draw(self, surface):
            img_flipped = self.image if not self.facing_right else pygame.transform.flip(self.image, True, False)
            surface.blit(img_flipped, self.rect)
            if self.is_hit and pygame.time.get_ticks() < self.hit_flash_end_time:
                mask = pygame.mask.from_surface(img_flipped);
                mask_surface = mask.to_surface(setcolor=WHITE, unsetcolor=(0, 0, 0));
                mask_surface.set_colorkey((0, 0, 0));
                mask_surface.set_alpha(180);
                surface.blit(mask_surface, self.rect)
            else:
                self.is_hit = False
            if self.alive:
                bar_w = WIDTH - 40;
                bar_x = 20
                pygame.draw.rect(surface, BLACK, (bar_x - 5, HEIGHT - 55, bar_w + 10, 40));
                pygame.draw.rect(surface, RED, (bar_x, HEIGHT - 50, bar_w, 30))
                pygame.draw.rect(surface, PURPLE,
                                 (bar_x, HEIGHT - 50, max(0, bar_w * (self.health / self.max_health)), 30))
                surface.blit(boss_font.render("LORD OBLIVION, THE ETERNAL KING", True, WHITE),
                             (bar_x + 10, HEIGHT - 52))
            for p in self.projectiles: p.draw(surface)
            for l in self.lasers: l.draw(surface)
            for h in self.hazards: h.draw(surface)

    class Projectile:
        def __init__(self, type, pos, target=None, angle=0, angle_offset=0, speed=8, facing_right=True):
            self.type = type;
            self.pos = list(pos);
            self.speed = speed;
            self.is_active = True
            if type == 'shadow':
                self.image = shadow_orb_sprite; self.damage = 15
            elif type == 'fire':
                self.image = fire_orb_sprite; self.damage = 15
            elif type == 'energy':
                self.image = energy_blast_sprite; self.damage = 10
            elif type == 'shockwave':
                self.image = shockwave_sprite; self.damage = 20
            self.rect = self.image.get_rect(center=self.pos)
            if type == 'shockwave':
                self.vel_x = self.speed if facing_right else -self.speed; self.vel_y = 0; self.rect.midbottom = self.pos
            else:
                if target:
                    direction = pygame.math.Vector2(target.hitbox.center) - pygame.math.Vector2(
                        self.rect.center); self.angle = direction.angle_to(pygame.math.Vector2(1, 0)) + angle_offset
                else:
                    self.angle = angle
                self.vel_x = math.cos(math.radians(self.angle)) * self.speed;
                self.vel_y = -math.sin(math.radians(self.angle)) * self.speed

        def update(self, player):
            self.pos[0] += self.vel_x
            self.pos[1] += self.vel_y
            self.rect.center = self.pos
            if not screen.get_rect().colliderect(self.rect):
                self.is_active = False

        def draw(self, surface):
            surface.blit(self.image, self.rect)

    class LaserBeam:
        def __init__(self, y_pos):
            self.rect = pygame.Rect(0, y_pos, WIDTH, 30);
            self.warning_rect = pygame.Rect(0, y_pos, WIDTH, 30);
            self.fire_time = pygame.time.get_ticks() + 800;
            self.end_time = self.fire_time + 400;
            self.active = False

        def update(self):
            if not self.active and pygame.time.get_ticks() > self.fire_time: self.active = True

        def draw(self, surface):
            now = pygame.time.get_ticks()
            if not self.active:
                alpha = (now % 250) / 250 * 150 + 50;
                warn_surf = pygame.Surface(self.warning_rect.size, pygame.SRCALPHA);
                warn_surf.fill((255, 100, 100, alpha));
                surface.blit(warn_surf, self.warning_rect.topleft)
            elif now < self.end_time:
                beam_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA); beam_surf.fill(
                    (255, 0, 0, 200)); surface.blit(beam_surf, self.rect.topleft)

    class ArenaHazard:
        def __init__(self, type, pos):
            self.type = type;
            self.pos = pos;
            self.is_active = True;
            self.state = 'warning';
            self.damage = 25;
            self.warning_time = pygame.time.get_ticks() + 1000;
            self.active_time = self.warning_time + 800
            self.warn_rect = pygame.Rect(0, GROUND_Y - 10, 80, 10);
            self.warn_rect.centerx = pos[0];
            self.spike_image = pygame.Surface((60, 100), pygame.SRCALPHA);
            pygame.draw.polygon(self.spike_image, PURPLE, [(0, 100), (30, 0), (60, 100)]);
            self.rect = self.spike_image.get_rect(midbottom=pos)

        def update(self):
            now = pygame.time.get_ticks()
            if self.state == 'warning' and now > self.warning_time: self.state = 'active'
            if now > self.active_time: self.is_active = False

        def draw(self, surface):
            if self.state == 'warning':
                alpha = (pygame.time.get_ticks() % 500) / 500 * 100 + 50; warn_surf = pygame.Surface(
                    self.warn_rect.size, pygame.SRCALPHA); warn_surf.fill((180, 0, 180, alpha)); surface.blit(warn_surf,
                                                                                                              self.warn_rect)
            elif self.state == 'active':
                surface.blit(self.spike_image, self.rect)

    player = Player()
    boss = FinalBoss()
    game_state = "STORY_INTRO"
    dialogue_stage = 0
    current_phase = 1
    phase_transitioned = {2: False, 3: False}

    running = True
    while running:
        events = pygame.event.get()
        keys = pygame.key.get_pressed()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "QUIT_TO_MENU"
                if game_state in ["STORY_INTRO", "INTRO_DIALOGUE", "VICTORY_CUTSCENE"] and (
                        event.key == pygame.K_RETURN or event.key == pygame.K_SPACE):
                    dialogue_stage += 1

        if game_state == "PLAYING":
            player.handle_input(keys, events)
            player.update()
            if boss.entered:
                boss.update(player, current_phase)
            else:
                if boss.rect.bottom < GROUND_Y:
                    boss.rect.bottom += 4
                else:
                    boss.rect.bottom = GROUND_Y; boss.entered = True; boss.last_action_time = pygame.time.get_ticks()

            health_percent = boss.health / boss.max_health
            if health_percent <= 0.66 and not phase_transitioned[2]:
                current_phase = 2;
                phase_transitioned[2] = True;
                boss.state = "TRANSITION";
                boss.last_action_time = pygame.time.get_ticks();
                player.set_flying_mode(True);
                set_subtitle("The very foundation crumbles!", 4000);
                screen_shake = 30;
                player.grant_power_up()
            elif health_percent <= 0.33 and not phase_transitioned[3]:
                current_phase = 3;
                phase_transitioned[3] = True;
                boss.state = "TRANSITION";
                boss.last_action_time = pygame.time.get_ticks()
                set_subtitle("ENOUGH! FACE YOUR DOOM!", 4000);
                screen_shake = 30

            damage_dealt = 25 if player.has_power_up else 15
            if player.attacking and not player.attack_has_hit and boss.alive and player.hitbox.inflate(80,
                                                                                                       20).colliderect(
                    boss.rect):
                boss.take_damage(damage_dealt)
                player.attack_has_hit = True
            for p in boss.projectiles:
                if p.rect.colliderect(player.hitbox):
                    player.take_damage(p.damage)  # Removed second argument
                    p.is_active = False
            for l in boss.lasers:
                if l.active and l.rect.colliderect(player.hitbox):
                    player.take_damage(25)  # Removed second argument
            for h in boss.hazards:
                if h.state == 'active' and h.rect.colliderect(player.hitbox):
                    player.take_damage(h.damage)  # Removed second argument

            if player.lives <= 0:
                return "GAME_OVER"
            if not boss.alive and boss.vel_y == 0:
                game_state = "VICTORY_CUTSCENE"
                dialogue_stage = 0

        bg = bg_phase1 if current_phase == 1 else (bg_phase2 if current_phase == 2 else bg_phase3)
        if game_state == "STORY_INTRO":
            screen.blit(bg_initial, (0, 0))
        else:
            screen.blit(bg, (0, 0))

        if game_state not in ["STORY_INTRO"]:
            player.draw(screen)
            if boss.entered or game_state == "VICTORY_CUTSCENE":
                boss.draw(screen)

        if game_state == "STORY_INTRO":
            set_subtitle("Lord Oblivion: 'Shatter their fate.'", 99999)
            if dialogue_stage > 0:
                game_state = "INTRO_DIALOGUE"
                dialogue_stage = 0
                subtitle["text"] = ""
        elif game_state == "INTRO_DIALOGUE":
            dialogue = [("Lord Oblivion", "So, the little hero arrives..."), ("Nobita", "I'm not afraid of you!"),
                        ("Lord Oblivion", "Then come! Face your oblivion!")]
            if dialogue_stage < len(dialogue):
                speaker, text = dialogue[dialogue_stage]
                portrait = boss_portrait if speaker == "Lord Oblivion" else nobita_portrait
                draw_text_box(screen, text, speaker, portrait)
            else:
                game_state = "PLAYING"
        elif game_state == "VICTORY_CUTSCENE":
            dialogue = [("Nobita", "It's... finally over. The world is safe."),
                        ("Nobita", "I faced my fears... and I won. It's time to go home.")]
            if dialogue_stage < len(dialogue):
                draw_text_box(screen, dialogue[dialogue_stage][1], "Nobita", nobita_portrait)
            else:
                return "COMPLETED"

        draw_subtitle(screen)
        if screen_shake > 0:
            screen.blit(screen.copy(),
                        (random.randint(-screen_shake, screen_shake), random.randint(-screen_shake, screen_shake)))
            screen_shake -= 1

        pygame.display.update()
        clock.tick(FPS)