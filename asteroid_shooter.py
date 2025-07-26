import pygame, sys
from random import randint, uniform, choice, randrange
import math
import os
import json

# --- Ship Data Structure ---
NEW_SHIP_IMAGES = [
    'assets/new_ships/playerShip1_blue.png',
    'assets/new_ships/playerShip1_green.png',
    'assets/new_ships/playerShip1_red.png',
    'assets/new_ships/playerShip2_blue.png',
    'assets/new_ships/playerShip2_green.png',
    'assets/new_ships/playerShip2_red.png',
    'assets/new_ships/playerShip3_blue.png',
    'assets/new_ships/playerShip3_green.png',
    'assets/new_ships/playerShip3_orange.png',
    'assets/new_ships/playerShip3_red.png',
]

DEFAULT_SHIP = {
    'id': 'default',
    'name': 'Star Ranger',
    'image': 'assets/ship/ship.png',
    'price': 0
}

# --- Ship Data ---
SHIP_NAMES = [
    "Star Falcon", "Nova Rider", "Cosmo Viper", "Astro Eagle", "Galactic Phoenix",
    "Solar Drifter", "Lunar Hawk", "Quantum Blazer", "Nebula Wraith", "Comet Specter"
]

# Build ship list
SHIPS = [DEFAULT_SHIP]
for idx, img_path in enumerate(NEW_SHIP_IMAGES):
    ship_name = SHIP_NAMES[idx % len(SHIP_NAMES)]
    SHIPS.append({
        'id': f'ship_{idx+1}',
        'name': ship_name,
        'image': img_path,
        'price': 25
    })

SAVE_FILE = 'save_data.json'

def load_save_data():
    if not os.path.exists(SAVE_FILE):
        # Default: 0 credits, only default ship unlocked, default ship selected
        return {
            'credits': 0,
            'unlocked_ships': ['default'],
            'last_selected_ship': 'default'
        }
    try:
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
        # Validate keys
        if 'credits' not in data or 'unlocked_ships' not in data or 'last_selected_ship' not in data:
            raise Exception('Corrupt save file')
        return data
    except Exception:
        # If corrupted, reset
        return {
            'credits': 0,
            'unlocked_ships': ['default'],
            'last_selected_ship': 'default'
        }

def save_save_data(data):
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f)

# Utility to get ship by id
def get_ship_by_id(ship_id):
    for ship in SHIPS:
        if ship['id'] == ship_id:
            return ship
    return DEFAULT_SHIP

# --- Global Save Data ---
save_data = load_save_data()

class Ship(pygame.sprite.Sprite):
    def __init__(self, groups, image_path=None):
        super().__init__(groups)
        if image_path is None:
            image_path = 'assets/ship/ship.png'
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.mask = pygame.mask.from_surface(self.image)

        self.can_shoot = True
        self.shoot_time = None
        
        self.shield_available = True
        self.shield_cooldown = None
        self.shield_destroyed = False
        self.ship_life = 4
        self.shield = None
        self.game_eval = True 

        self.ship_creation_time = pygame.time.get_ticks()

        self.damage_overlay = DamageOverlay(self, damageoverlay_group)

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time > 650:
                self.can_shoot = True

    def input_position(self):
        pos = pygame.mouse.get_pos()
        self.rect.center = pos

    def laser_shoot(self):
        curr_time = pygame.time.get_ticks()
        if curr_time - self.ship_creation_time > 500:
            if pygame.mouse.get_pressed()[0] and self.can_shoot:
                self.can_shoot = False
                self.shoot_time = pygame.time.get_ticks()
                Laser(self.rect.midtop, laser_group)
        
    def collide_check(self):
        if pygame.sprite.spritecollide(self, shield_power_up_group, True, pygame.sprite.collide_mask):
            if self.shield_available == False and not self.shield:
                self.shield_available = True
                zap.play()

        if pygame.sprite.spritecollide(self, meteor_group, True, pygame.sprite.collide_mask):
            if self.shield:
                self.shield.kill()
                shield_down.play()
                self.shield = None
            else:
                spaceship_damage.play()
                self.ship_life -= 1
                self.damage_overlay.update()

        if pygame.sprite.spritecollide(self, stone_meteor_group, True, pygame.sprite.collide_mask):
            if self.shield:
                self.shield.kill()
                shield_down.play()
                self.shield = None
            
            spaceship_damage.play()
            self.ship_life -= 1
            self.damage_overlay.update()

        if self.ship_life <= 0:
            crash.play()
            self.game_eval = False

        if self.rect.bottom < 0:
            self.kill()
        

    def shield_check(self):
        if pygame.mouse.get_pressed()[2] and self.shield_available and not self.shield:
            self.shield = Shield(shield_group, pos=self.rect.center)
            self.shield_available = False
            self.shield_cooldown = pygame.time.get_ticks()
            shield_up.play()

        if not self.shield_available:
            current_time = pygame.time.get_ticks()
            if current_time - self.shield_cooldown > 10000:
                # self.shield_available = True
                
                if not self.shield_destroyed and self.shield:
                    self.shield.kill()
                    shield_down.play()
                    self.shield = None
                    
            elif self.shield:
                self.shield.rect.center = self.rect.center

    def update(self):
        self.laser_timer()
        self.laser_shoot()
        self.input_position()
        self.shield_check()
        self.collide_check()

class Laser(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.image.load('assets/laser/laser.png').convert_alpha()
        self.rect = self.image.get_rect(midbottom=pos)

        self.mask = pygame.mask.from_surface(self.image)

        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(0, -1)
        self.speed = 600
        laser_shoot.play()
    
    def collide_check(self):
        #Normal Meteor
        if pygame.sprite.spritecollide(self, meteor_group, True, pygame.sprite.collide_mask):
            meteor_explosion.play()
            if randint(1, 10) == 2:
                ShieldPowerUp(groups=shield_power_up_group, pos=self.rect.midtop)
            self.kill()

        #Stone Meteor
        if pygame.sprite.spritecollide(self, stone_meteor_group, False, pygame.sprite.collide_mask):
            self.kill()

    def update(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        self.collide_check()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)


        self.meteor_image = METEOR_IMAGES[randint(0, len(METEOR_IMAGES)-1)]
        self.rand_size_mult = pygame.math.Vector2(self.meteor_image.get_size()) * uniform(0.5, 2.5)
        self.scaled_surf = pygame.transform.scale(self.meteor_image, (int(self.rand_size_mult.x), int(self.rand_size_mult.y)))
        self.image = self.scaled_surf
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)

        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(400, 600)
        
        self.rotation = 0
        self.rotation_speed = randint(30, 60)
    
    def rotate(self, dt):
        self.rotation += self.rotation_speed * dt
        rotated_surf = pygame.transform.rotozoom(self.scaled_surf, self.rotation, 1)
        self.image = rotated_surf
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)
    
    def meteor_pos_check(self):
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

    def meteor_collision_check(self):
        # Check collision with other normal meteors
        collisions = pygame.sprite.spritecollide(self, meteor_group, False, pygame.sprite.collide_mask)
        for other in collisions:
            if other != self:
                # Calculate size-based randomness (smaller = more random)
                my_width = self.rect.width
                other_width = other.rect.width
                my_rand = uniform(-0.2, 0.2) * (60 / my_width)
                other_rand = uniform(-0.2, 0.2) * (60 / other_width)
                # Reverse x-direction and add randomness
                self.direction.x = -self.direction.x + my_rand
                other.direction.x = -other.direction.x + other_rand
                # Nudge apart to prevent overlap
                if self.rect.centerx < other.rect.centerx:
                    self.pos.x -= 5
                    other.pos.x += 5
                else:
                    self.pos.x += 5
                    other.pos.x -= 5
                # Clamp x direction to [-1, 1] for stability
                self.direction.x = max(-1, min(1, self.direction.x))
                other.direction.x = max(-1, min(1, other.direction.x))

        # Check collision with stone meteors
        stone_collisions = pygame.sprite.spritecollide(self, stone_meteor_group, False, pygame.sprite.collide_mask)
        for stone in stone_collisions:
            # Only normal meteor changes direction
            my_width = self.rect.width
            my_rand = uniform(-0.2, 0.2) * (60 / my_width)
            self.direction.x = -self.direction.x + my_rand
            # Nudge apart
            if self.rect.centerx < stone.rect.centerx:
                self.pos.x -= 5
            else:
                self.pos.x += 5
            self.direction.x = max(-1, min(1, self.direction.x))

    def update(self, dt):
        self.meteor_collision_check()
        self.pos += self.direction * self.speed * dt
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        self.rotate(dt)
        self.meteor_pos_check()

class Stone_Meteor(pygame.sprite.Sprite):
    def __init__(self,pos, groups) -> None:
        super().__init__(groups)

        # self.stone_meteor = pygame.image.load('assets/stone_meteor.png').convert_alpha() 
        self.stone_meteor = STONE_METEOR_IMAGES[randint(0, len(STONE_METEOR_IMAGES) - 1)]
        self.rand_size_mult = pygame.math.Vector2(self.stone_meteor.get_size()) * uniform(1, 2.5)
        self.scaled_surf = pygame.transform.scale(self.stone_meteor, (int(self.rand_size_mult.x), int(self.rand_size_mult.y)))
        self.stone_meteor_image = self.scaled_surf
        self.rect = self.stone_meteor_image.get_rect(center = pos)
        self.mask = pygame.mask.from_surface(self.stone_meteor_image)

        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(uniform(-0.8, 0.8), 1)
        self.speed = randint(300, 700)

        self.rotation = 0
        self.rotation_speed = randint(40, 70)
    
    def rotate(self, dt):
        self.rotation += self.rotation_speed * dt
        rotated_surf = pygame.transform.rotozoom(self.scaled_surf, self.rotation, 1)
        self.image = rotated_surf
        self.rect = self.image.get_rect(center = self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)
    
    def meteor_pos_check(self):
        collisions = pygame.sprite.spritecollide(self, stone_meteor_group, False, pygame.sprite.collide_mask)

        if collisions:
            for meteor in collisions:
                if meteor != self:
                    self.direction.x *= -1
                    meteor.direction.x *= -1

        if self.rect.top > WINDOW_HEIGHT:
            self.kill()
    
    def update(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        self.rotate(dt)
        self.meteor_pos_check()
        
class Score:
    def __init__(self):
        self.font = pygame.font.Font('assets/font/subatomic.ttf', 50)
    
    def score_start(self):
        self.score_time = pygame.time.get_ticks()

    def display(self):
        self.ref_score = (pygame.time.get_ticks() - self.score_time) // 1000
        score_text = f'Score: {self.ref_score}'
        text_surf = self.font.render(score_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center = (int(WINDOW_WIDTH * 0.9), int(WINDOW_HEIGHT * 0.1)))
        display_surface.blit(text_surf, text_rect)

class Shield(pygame.sprite.Sprite):
    def __init__(self, groups, pos):
        super().__init__(groups)
        self.image = pygame.image.load('assets/ship/shield.png').convert_alpha()
        self.rect = self.image.get_rect(center=pos)

class DamageOverlay(pygame.sprite.Sprite):
    def __init__(self,ship,groups):
        super().__init__(groups)

        self.ship = ship        
        self.damage_images = [
            pygame.image.load('assets/damage_overlays/playerShip1_damage1.png').convert_alpha(),
            pygame.image.load('assets/damage_overlays/playerShip1_damage2.png').convert_alpha(),
            pygame.image.load('assets/damage_overlays/playerShip1_damage3.png').convert_alpha()
        ]
        self.image = self.damage_images[0]
        self.rect = self.image.get_rect(center=self.ship.rect.center)

    def update(self):
        if self.ship.ship_life == 3:
            self.image = self.damage_images[0]
            self.rect = self.image.get_rect(center=self.ship.rect.center)
        elif self.ship.ship_life == 2:
            self.image = self.damage_images[1]
            self.rect = self.image.get_rect(center=self.ship.rect.center)
        elif self.ship.ship_life == 1:
            self.image = self.damage_images[2]
            self.rect = self.image.get_rect(center=self.ship.rect.center)
        else:
            self.image = pygame.surface.Surface((0,0)) 

        if self.image:
            self.rect.center = self.ship.rect.center

class ShieldPowerUp(pygame.sprite.Sprite):
    def __init__(self, groups, pos):
        super().__init__(groups)
        self.image = pygame.image.load('assets/shield_power/shield_icon.png').convert_alpha()
        self.rect = self.image.get_rect(center=pos)

        self.mask = pygame.mask.from_surface(self.image)

        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2(0, 1)
        self.speed = 450
    
    def shield_icon_pos_check(self):
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()
    
    def update(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))

        self.shield_icon_pos_check()


    
# basic setup 
pygame.init()
# WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720 
WINDOW_WIDTH, WINDOW_HEIGHT = 1920, 1080
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Space shooter')
clock = pygame.time.Clock()

#assets
METEOR_IMAGES = [
    pygame.image.load('assets/meteors/meteor_big1.png').convert_alpha(),
    pygame.image.load('assets/meteors/meteor_big2.png').convert_alpha(),
    pygame.image.load('assets/meteors/meteor_big3.png').convert_alpha(),
    pygame.image.load('assets/meteors/meteor_big4.png').convert_alpha(),
    pygame.image.load('assets/meteors/meteor_med1.png').convert_alpha(),
    pygame.image.load('assets/meteors/meteor_med2.png').convert_alpha(),

]

STONE_METEOR_IMAGES = [
    pygame.image.load('assets/stone_meteors/stonemeteor_big1.png').convert_alpha(),
    pygame.image.load('assets/stone_meteors/stonemeteor_big2.png').convert_alpha(),
    pygame.image.load('assets/stone_meteors/stonemeteor_big3.png').convert_alpha(),
    pygame.image.load('assets/stone_meteors/stonemeteor_big4.png').convert_alpha(),
    pygame.image.load('assets/stone_meteors/stonemeteor_med1.png').convert_alpha(),
    pygame.image.load('assets/stone_meteors/stonemeteor_med2.png').convert_alpha(),
]

logo = pygame.image.load('assets/main_menu/logo.png').convert_alpha()
logo_rect = logo.get_rect(center = ( WINDOW_WIDTH//2 , int(WINDOW_HEIGHT *0.2)))

mm_background_image = pygame.image.load('assets/main_menu/background_image.png').convert()
scaled_mm_bg_image = pygame.transform.scale(mm_background_image, (WINDOW_WIDTH, WINDOW_HEIGHT)) 

brush_stroke = pygame.image.load('assets/main_menu/brush_stroke.png').convert_alpha()
scaled_brush_stroke = pygame.transform.scale(brush_stroke, (190, 90))



# background 
bg_surf = pygame.image.load('assets/game_background/background.png').convert()
background_surf = pygame.transform.scale(bg_surf, (WINDOW_WIDTH, WINDOW_HEIGHT))

# sprite groups 
spaceship_group = pygame.sprite.GroupSingle()
laser_group = pygame.sprite.Group()
meteor_group = pygame.sprite.Group()
shield_group = pygame.sprite.Group()
stone_meteor_group = pygame.sprite.Group()
damageoverlay_group = pygame.sprite.Group()
shield_power_up_group = pygame.sprite.Group()

font = pygame.font.Font('assets/main_menu/LEMONMILK-BoldItalic.otf', 50)
highscore_font = pygame.font.Font('assets/main_menu/LEMONMILK-BoldItalic.otf', 75)
version_font = pygame.font.Font('assets/main_menu/LEMONMILK-BoldItalic.otf', 20)

play_text = "Play"

play_text_surf = font.render(play_text, True, (255,255,255))
play_text_rect = play_text_surf.get_rect(center = (int(WINDOW_WIDTH * 0.85), (int(WINDOW_HEIGHT * 0.75))))
play_brush_stroke_rect = scaled_brush_stroke.get_rect(center = (int(WINDOW_WIDTH * 0.85), (int(WINDOW_HEIGHT * 0.75))))

credits_text = "Credits"

credits_text_surf = font.render(credits_text, True, (255,255,255))
credits_text_rect = play_text_surf.get_rect(center = (int(WINDOW_WIDTH * 0.85), (int(WINDOW_HEIGHT * 0.85))))

credits_scaled_brush_stroke = pygame.transform.scale(brush_stroke, (300, 90))
credits_brush_stroke_rect = scaled_brush_stroke.get_rect(center = (int(WINDOW_WIDTH * 0.85), (int(WINDOW_HEIGHT * 0.85))))

version_surf = version_font.render("V1.9.2 - UNSTABLE", True, (255,255,255))
version_rect = version_surf.get_rect(topleft = (int(WINDOW_WIDTH * 0.025), (int(WINDOW_HEIGHT * 0.95))))

dd_normal_image = pygame.image.load('assets/credits/credits_normal.jpg').convert()
dd_effect_image = pygame.image.load('assets/credits/credits_effect.jpg').convert()

dd_normal = pygame.transform.scale(dd_normal_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
dd_effect = pygame.transform.scale(dd_effect_image, (WINDOW_WIDTH, WINDOW_HEIGHT))


#Music and SFX
click = pygame.mixer.Sound('assets/music/click.wav')
crash = pygame.mixer.Sound('assets/music/crash.wav')
game_bg_music = pygame.mixer.Sound('assets/music/game_bg_music_2.mp3')
laser_shoot = pygame.mixer.Sound('assets/music/laser_shoot_to_edit.wav')
menu_bg_music = pygame.mixer.Sound('assets/music/menu_bg_music.wav')
mouse_hover = pygame.mixer.Sound('assets/music/mouse_hover.wav')

shield_down = pygame.mixer.Sound('assets/sfx/sfx_shieldDown.ogg')
shield_up = pygame.mixer.Sound('assets/sfx/sfx_ShieldUp.ogg')
zap = pygame.mixer.Sound('assets/sfx/sfx_zap.ogg')
meteor_explosion = pygame.mixer.Sound('assets/sfx/meteor_explosion.mp3')
spaceship_damage = pygame.mixer.Sound('assets/sfx/spaceship_damage.mp3')

play_mouse_hover_bool = True
credits_mouse_hover_bool = True

#Menu Screen Assets
WINDOW_WIDTH, WINDOW_HEIGHT = 1920, 1080
RES = WIDTH, HEIGHT = WINDOW_WIDTH, WINDOW_HEIGHT
NUM_STARS = 1500
CENTER = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
Z_DISTANCE = 50
ALPHA = 100

class Star:
    def __init__(self, app, mode):
        if mode!= "main":
            self.Z_DISTANCE = 140
            self.ALPHA = 30
        else:
            self.Z_DISTANCE = 50
            self.ALPHA = 100
        
        self.screen = app.screen
        self.pos3d = self.get_pos3d(mode)
        self.vel = uniform(0.05, 0.25) if mode == "main" else uniform(0.45, 0.95)
        self.meteor = choice(app.meteors)
        self.screen_pos = pygame.math.Vector2(0, 0)
        self.original_size = 15
        self.size = self.original_size * 0.1  # Start at 10% of original size
        

    def get_pos3d(self,mode, scale_pos=100):
        angle = uniform(0, 2 * math.pi)
        radius = randrange(HEIGHT // scale_pos, HEIGHT) * scale_pos if mode =="main" else randrange(HEIGHT // 2, HEIGHT) * scale_pos
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        return pygame.math.Vector3(x, y, self.Z_DISTANCE)

    def update(self, mode):
        self.pos3d.z -= self.vel
        self.pos3d = self.get_pos3d(mode) if self.pos3d.z < 1 else self.pos3d

        self.screen_pos = pygame.math.Vector2(self.pos3d.x, self.pos3d.y) / self.pos3d.z + CENTER
        
        # Calculate size based on z-distance
        z_factor = 1 - (self.pos3d.z / self.Z_DISTANCE)  # 0 when far, 1 when close
        size_factor = 0.1 + (3.0 * z_factor)  # 0.1 when far, 1.5 when close
        self.size = self.original_size * size_factor

        # rotate xy
        self.pos3d.xy = self.pos3d.xy.rotate(0.2)

    def draw(self):
        s = self.size
        if (-s < self.screen_pos.x < WIDTH + s) and (-s < self.screen_pos.y < HEIGHT + s):
            scaled_meteor = pygame.transform.scale(self.meteor, (int(s), int(s)))
            self.meteor_rect = scaled_meteor.get_rect(center=self.screen_pos)
            self.screen.blit(scaled_meteor, self.meteor_rect)

class Starfield:
    def __init__(self, app, mode):
        if mode!="main":
            self.NUM_STARS = 5000
        else:
            self.NUM_STARS = 1500
        self.stars = [Star(app, mode) for i in range(self.NUM_STARS)]

    def run(self, mode):
        [star.update(mode) for star in self.stars]
        self.stars.sort(key=lambda star: star.pos3d.z, reverse=True)
        [star.draw() for star in self.stars]
class App:
    def __init__(self, mode):
        if mode!= "main":
            self.ALPHA = 30
        else:
            self.ALPHA = 100 
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.alpha_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.alpha_surface.set_alpha(self.ALPHA)
        self.meteors = [pygame.image.load('assets/meteors/meteor_med1.png').convert_alpha(), 
                        pygame.image.load('assets/meteors/meteor_med2.png').convert_alpha(), 
                        pygame.image.load('assets/meteors/meteor_small1.png').convert_alpha(), 
                        pygame.image.load('assets/meteors/meteor_big1.png').convert_alpha(),
                        pygame.image.load('assets/stone_meteors/stonemeteor_med1.png').convert_alpha(),
                        pygame.image.load('assets/stone_meteors/stonemeteor_med2.png').convert_alpha(),
                        pygame.image.load('assets/stone_meteors/stonemeteor_small1.png').convert_alpha(),
                        pygame.image.load('assets/stone_meteors/stonemeteor_big3.png').convert_alpha()
                        ]
        self.clock = pygame.time.Clock()
        self.starfield = Starfield(self, mode)

    def update(self, mode):
        self.starfield.run(mode)

    def draw(self, surface, mode):
        surface.blit(self.alpha_surface, (0, 0))
        self.starfield.run(mode)

def retry_screen(highscore):

    menu_bg_music.set_volume(100)

    app = App(mode="retry")

    Star.vel = uniform(0.45, 0.95)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        app.update(mode="retry")
        display_surface.fill((0, 0, 0))  # Fill with black

        app.draw(display_surface, mode="credits")

        mx, my = pygame.mouse.get_pos()

        retry_surf = font.render(f"RETRY", True, (255,255,255))
        retry_rect = retry_surf.get_rect(center = (WINDOW_WIDTH //2, WINDOW_HEIGHT * 0.6))
        retry_brush_stroke_rect = scaled_brush_stroke.get_rect(center = (WINDOW_WIDTH //2, WINDOW_HEIGHT * 0.6))

        quit_surf = font.render(f"quit", True, (255,255,255))
        quit_rect = quit_surf.get_rect(center = (WINDOW_WIDTH //2, WINDOW_HEIGHT * 0.7))
        quit_brush_stroke_rect = scaled_brush_stroke.get_rect(center = (WINDOW_WIDTH //2, WINDOW_HEIGHT * 0.7))

        highscore_surf = highscore_font.render(f"Final Score: {highscore}", True, (255, 255, 255))
        highscore_rect = highscore_surf.get_rect(center = (WINDOW_WIDTH //2, WINDOW_HEIGHT * 0.4))

        display_surface.blit(highscore_surf, highscore_rect)

        display_surface.blit(retry_surf, retry_rect)
        display_surface.blit(quit_surf, quit_rect)

        if retry_rect.collidepoint((mx, my)):
            if not play_mouse_hover_bool:
                mouse_hover.play()
                play_mouse_hover_bool = True
            display_surface.blit(scaled_brush_stroke, retry_brush_stroke_rect)
            retry_surf = font.render("RETRY", True, (0,0,0))
            display_surface.blit(retry_surf, retry_rect)
            if pygame.mouse.get_pressed()[0]:
                click.play()
                # Ask if user wants to use last ship or select new
                last_ship_id = save_data.get('last_selected_ship', 'default')
                last_ship = get_ship_by_id(last_ship_id)
                # Dialog with proper layering and consistent fonts
                retry_dialog_font = pygame.font.Font('assets/main_menu/LEMONMILK-BoldItalic.otf', 32)
                retry_button_font = pygame.font.Font('assets/main_menu/LEMONMILK-BoldItalic.otf', 30)
                
                # Semi-transparent overlay to dim background
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                display_surface.blit(overlay, (0, 0))
                
                dialog_surf = pygame.Surface((650, 280), pygame.SRCALPHA)
                dialog_surf.fill((25, 25, 25, 250))
                dialog_rect = dialog_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
                
                # Draw dialog border
                pygame.draw.rect(display_surface, (100, 100, 100), dialog_rect, 3, border_radius=15)
                display_surface.blit(dialog_surf, dialog_rect)
                
                msg1 = retry_dialog_font.render(f'Use last ship: {last_ship["name"]}?', True, (255,255,255))
                msg2 = retry_dialog_font.render('Or select a new ship.', True, (255,255,255))
                msg1_rect = msg1.get_rect(center=(dialog_rect.centerx, dialog_rect.top + 70))
                msg2_rect = msg2.get_rect(center=(dialog_rect.centerx, dialog_rect.top + 120))
                display_surface.blit(msg1, msg1_rect)
                display_surface.blit(msg2, msg2_rect)
                
                # Buttons without overlays, moved higher with proper spacing
                use_last_rect = pygame.Rect(WINDOW_WIDTH//2-190, WINDOW_HEIGHT//2+40, 160, 50)
                select_new_rect = pygame.Rect(WINDOW_WIDTH//2+30, WINDOW_HEIGHT//2+40, 200, 50)
                
                # Simple colored backgrounds
                pygame.draw.rect(display_surface, (60,180,60), use_last_rect, border_radius=8)
                pygame.draw.rect(display_surface, (80,80,200), select_new_rect, border_radius=8)
                
                use_last_surf = retry_button_font.render('Use Last', True, (255,255,255))
                select_new_surf = retry_button_font.render('Select New', True, (255,255,255))
                use_last_surf_rect = use_last_surf.get_rect(center=use_last_rect.center)
                select_new_surf_rect = select_new_surf.get_rect(center=select_new_rect.center)
                display_surface.blit(use_last_surf, use_last_surf_rect)
                display_surface.blit(select_new_surf, select_new_surf_rect)
                pygame.display.update()
                # Wait for user input
                waiting = True
                while waiting:
                    for e in pygame.event.get():
                        if e.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                            mx2, my2 = pygame.mouse.get_pos()
                            use_last_rect = pygame.Rect(WINDOW_WIDTH//2-190, WINDOW_HEIGHT//2+40, 160, 50)
                            select_new_rect = pygame.Rect(WINDOW_WIDTH//2+30, WINDOW_HEIGHT//2+40, 160, 50)
                            if use_last_rect.collidepoint((mx2, my2)):
                                game(selected_ship_id=last_ship_id)
                                return
                            elif select_new_rect.collidepoint((mx2, my2)):
                                selected_ship_id = ship_selection_screen()
                                if selected_ship_id:
                                    game(selected_ship_id=selected_ship_id)
                                return
                    clock.tick(60)
        else:
            play_mouse_hover_bool = False
            retry_surf = font.render(f"RETRY", True, (255,255,255))
        
        if quit_rect.collidepoint((mx, my)):
            if not credits_mouse_hover_bool:
                mouse_hover.play()
                credits_mouse_hover_bool = True
            display_surface.blit(scaled_brush_stroke, quit_brush_stroke_rect)
            quit_surf = font.render("quit", True, (0,0,0))
            display_surface.blit(quit_surf, quit_rect)
            if pygame.mouse.get_pressed()[0]:
                click.play()
                pygame.quit()
                sys.exit()
        else:
            credits_mouse_hover_bool = False
            quit_surf = font.render(f"RETRY", True, (255,255,255))


        clock.tick(60)
        pygame.display.update()

def credits():
    credits_display = True
    while credits_display:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    credits_display = False
            
        display_surface.fill('black')

        mx, my = pygame.mouse.get_pos()

        if  WINDOW_WIDTH // 2 <= mx:
            display_surface.blit(dd_effect, (0,0))
        else:
            display_surface.blit(dd_normal, (0,0))      

        clock.tick(60)
        pygame.display.update()

def main_menu(play_text_surf, version_surf, credits_text_surf):
    menu_bg_music.play(-1)
    credits_mouse_hover_bool = True
    app = App(mode="main")  # Create an instance of App for the starfield background
    global save_data
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        app.update(mode="main")  # Update the starfield
        
        display_surface.fill((0, 0, 0))  # Fill with black
        app.draw(display_surface, mode="main")  # Draw the starfield
        
        mx, my = pygame.mouse.get_pos()

        display_surface.blit(logo, logo_rect)
        display_surface.blit(version_surf, version_rect)


        display_surface.blit(play_text_surf, play_text_rect)
        display_surface.blit(credits_text_surf, credits_text_rect)

        if play_text_rect.collidepoint((mx, my)):
            if not play_mouse_hover_bool:
                mouse_hover.play()
                play_mouse_hover_bool = True
            display_surface.blit(scaled_brush_stroke, play_brush_stroke_rect)
            play_text_surf = font.render(play_text, True, (0,0,0))
            display_surface.blit(play_text_surf, play_text_rect)
            if pygame.mouse.get_pressed()[0]:
                click.play()
                menu_bg_music.set_volume(0)
                # Ship selection before game
                selected_ship_id = ship_selection_screen()
                if selected_ship_id:
                    game(selected_ship_id=selected_ship_id)
        else:
            menu_bg_music.set_volume(100)
            play_mouse_hover_bool = False
            play_text_surf = font.render(play_text, True, (255,255,255))
        
        if credits_text_rect.collidepoint((mx, my)):
            if not credits_mouse_hover_bool:
                mouse_hover.play()
                credits_mouse_hover_bool = True
            display_surface.blit(credits_scaled_brush_stroke, credits_brush_stroke_rect)
            credits_text_surf = font.render(credits_text, True, (0,0,0))
            display_surface.blit(credits_text_surf, credits_text_rect)
            if pygame.mouse.get_pressed()[0]:
                click.play()
                credits()
        else:
            credits_mouse_hover_bool = False 
            credits_text_surf = font.render(credits_text, True, (255,255,255))

        clock.tick(60)
        pygame.display.update()

def game(selected_ship_id=None): 
    # game loop

    global save_data

    # sprite creation 
    if selected_ship_id is None:
        selected_ship_id = save_data.get('last_selected_ship', 'default')
    selected_ship = get_ship_by_id(selected_ship_id)
    save_data['last_selected_ship'] = selected_ship_id
    save_save_data(save_data)
    
    ship = Ship(spaceship_group, image_path=selected_ship['image'])

    # timer 
    meteor_timer = pygame.event.custom_type()
    stone_meteor_timer = pygame.event.custom_type()

    pygame.time.set_timer(meteor_timer, 300)
    pygame.time.set_timer(stone_meteor_timer, 500)

    score = Score()
    score.score_start()
    
    menu_bg_music.set_volume(0)
    game_bg_music.play(-1)
    game_bg_music.set_volume(100)
    game_loop = True
    last_credit_time = pygame.time.get_ticks()
    while game_loop and ship.game_eval:
        # event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_bg_music.set_volume(0)
                    game_loop = False

            if event.type == meteor_timer:
                meteor_y_pos = randint(-150, -50)
                meteor_x_pos = randint(-100, WINDOW_WIDTH + 100)
                Meteor((meteor_x_pos, meteor_y_pos), groups=meteor_group)
            
            if event.type == stone_meteor_timer:
                stone_meteor_y_pos = randint(-150, -50)
                stone_meteor_x_pos = randint(-100, WINDOW_WIDTH + 100)
                Stone_Meteor((stone_meteor_x_pos, stone_meteor_y_pos), groups=stone_meteor_group)
        
        # delta time 
        dt = clock.tick() / 1000

        # background 
        display_surface.blit(background_surf, (0, 0))

        # update
        spaceship_group.update()
        laser_group.update(dt)
        meteor_group.update(dt)
        shield_group.update()
        stone_meteor_group.update(dt)
        damageoverlay_group.update()
        shield_power_up_group.update(dt)

        # score
        score.display()

        # credits logic: 1 credit per 10 seconds survived
        current_time = pygame.time.get_ticks()
        if (current_time - last_credit_time) >= 10000:
            save_data['credits'] += 1
            last_credit_time = current_time
            save_save_data(save_data)

        # graphics 
        spaceship_group.draw(display_surface)
        laser_group.draw(display_surface)
        meteor_group.draw(display_surface)
        shield_group.draw(display_surface)
        stone_meteor_group.draw(display_surface)
        damageoverlay_group.draw(display_surface)
        shield_power_up_group.draw(display_surface)

        # draw the frame 
        pygame.display.update()
    
    game_bg_music.set_volume(0)
    save_save_data(save_data)
    retry_screen(highscore = score.ref_score)

def ship_selection_screen():
    global save_data
    running = True
    selected_ship_id = save_data.get('last_selected_ship', 'default')
    unlock_dialog = None  # (ship_id, ship_name, price) if showing dialog
    error_dialog = None  # error message if not enough credits
    double_click_timer = 0
    last_clicked_ship = None
    
    # Add starfield background for ship selection
    app = App(mode="ship_selection")
    grid_cols = 4
    grid_margin = 100
    ship_size = 160
    highlight_scale = 1.15
    hover_scale = 1.3
    slide_distance = 20
    # Standardized fonts for consistency
    name_font = pygame.font.Font('assets/main_menu/LEMONMILK-BoldItalic.otf', 24)
    button_font = pygame.font.Font('assets/main_menu/LEMONMILK-BoldItalic.otf', 36)
    price_font = pygame.font.Font('assets/main_menu/LEMONMILK-BoldItalic.otf', 20)
    dialog_font = pygame.font.Font('assets/main_menu/LEMONMILK-BoldItalic.otf', 32)
    dialog_button_font = pygame.font.Font('assets/main_menu/LEMONMILK-BoldItalic.otf', 30)
    back_button_rect = pygame.Rect(60, WINDOW_HEIGHT - 100, 220, 70)
    back_button_surf = button_font.render('Back', True, (255,255,255))
    back_brush_stroke = pygame.transform.scale(brush_stroke, (250, 90))
    back_brush_rect = back_brush_stroke.get_rect(center=back_button_rect.center)
    
    # Preload ship images
    ship_imgs = {}
    for ship in SHIPS:
        img = pygame.image.load(ship['image']).convert_alpha()
        ship_imgs[ship['id']] = img
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                current_time = pygame.time.get_ticks()
                
                # Back button
                if back_button_rect.collidepoint((mx, my)) and not unlock_dialog and not error_dialog:
                    return None
                # Dialogs
                if unlock_dialog:
                    # Confirm or cancel
                    confirm_rect = pygame.Rect(WINDOW_WIDTH//2-140, WINDOW_HEIGHT//2+50, 120, 50)
                    cancel_rect = pygame.Rect(WINDOW_WIDTH//2+20, WINDOW_HEIGHT//2+50, 120, 50)
                    if confirm_rect.collidepoint((mx, my)):
                        # Buy ship
                        ship_id, ship_name, price = unlock_dialog
                        if save_data['credits'] >= price:
                            save_data['credits'] -= price
                            save_data['unlocked_ships'].append(ship_id)
                            save_save_data(save_data)
                            unlock_dialog = None
                        else:
                            error_dialog = 'Not enough credits!'
                            unlock_dialog = None
                    elif cancel_rect.collidepoint((mx, my)):
                        unlock_dialog = None
                elif error_dialog:
                    ok_rect = pygame.Rect(WINDOW_WIDTH//2-60, WINDOW_HEIGHT//2+40, 120, 50)
                    if ok_rect.collidepoint((mx, my)):
                        error_dialog = None
                else:
                    # Ship grid - double click logic
                    for idx, ship in enumerate(SHIPS):
                        col = idx % grid_cols
                        row = idx // grid_cols
                        grid_w = grid_cols * (ship_size + grid_margin) - grid_margin
                        grid_x = (WINDOW_WIDTH - grid_w) // 2
                        grid_y = 160
                        x = grid_x + col * (ship_size + grid_margin)
                        y = grid_y + row * (ship_size + grid_margin + 60)
                        rect = pygame.Rect(x, y, ship_size, ship_size)
                        if rect.collidepoint((mx, my)):
                            if ship['id'] in save_data['unlocked_ships']:
                                # Double click detection
                                if (last_clicked_ship == ship['id'] and 
                                    current_time - double_click_timer < 500):
                                    # Double click detected - start game
                                    save_data['last_selected_ship'] = ship['id']
                                    save_save_data(save_data)
                                    return ship['id']
                                else:
                                    # Single click - just select
                                    selected_ship_id = ship['id']
                                    last_clicked_ship = ship['id']
                                    double_click_timer = current_time
                            else:
                                unlock_dialog = (ship['id'], ship['name'], ship['price'])
        # Draw
        app.update(mode="ship_selection")
        display_surface.fill((0,0,0))
        app.draw(display_surface, mode="ship_selection")
        # Title
        title_font = pygame.font.Font('assets/main_menu/LEMONMILK-BoldItalic.otf', 52)
        title_surf = title_font.render('Select Your Ship', True, (255,255,255))
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH//2, 70))
        display_surface.blit(title_surf, title_rect)
        
        # Show credits in ship selection screen
        credits_display_font = pygame.font.Font('assets/main_menu/LEMONMILK-BoldItalic.otf', 28)
        credits_surf = credits_display_font.render(f'Credits: {save_data["credits"]}', True, (255, 255, 80))
        credits_rect = credits_surf.get_rect(topright=(WINDOW_WIDTH - 60, 40))
        display_surface.blit(credits_surf, credits_rect)
        # Ship grid with hover animations
        mx, my = pygame.mouse.get_pos()
        hovered_ship_idx = None
        
        # Find which ship is hovered
        for idx, ship in enumerate(SHIPS):
            col = idx % grid_cols
            row = idx // grid_cols
            grid_w = grid_cols * (ship_size + grid_margin) - grid_margin
            grid_x = (WINDOW_WIDTH - grid_w) // 2
            grid_y = 160
            x = grid_x + col * (ship_size + grid_margin)
            y = grid_y + row * (ship_size + grid_margin + 60)
            rect = pygame.Rect(x, y, ship_size, ship_size)
            if rect.collidepoint((mx, my)) and ship['id'] in save_data['unlocked_ships']:
                hovered_ship_idx = idx
                break
        
        for idx, ship in enumerate(SHIPS):
            col = idx % grid_cols
            row = idx // grid_cols
            grid_w = grid_cols * (ship_size + grid_margin) - grid_margin
            grid_x = (WINDOW_WIDTH - grid_w) // 2
            grid_y = 160
            x = grid_x + col * (ship_size + grid_margin)
            y = grid_y + row * (ship_size + grid_margin + 60)
            rect = pygame.Rect(x, y, ship_size, ship_size)
            is_selected = (ship['id'] == selected_ship_id)
            mouse_over = (idx == hovered_ship_idx)
            
            # Calculate position offset and scale based on hover state
            offset_x = 0
            scale = 1.0
            
            if ship['id'] in save_data['unlocked_ships']:
                if mouse_over:
                    scale = hover_scale
                elif hovered_ship_idx is not None:
                    # Adjacent ships slide away
                    if abs(idx - hovered_ship_idx) == 1 and row == (hovered_ship_idx // grid_cols):
                        # Same row, adjacent ship
                        if idx < hovered_ship_idx:
                            offset_x = -slide_distance
                        else:
                            offset_x = slide_distance
                
                if is_selected and not mouse_over:
                    scale = highlight_scale
            
            # Draw ship with transformations
            img = ship_imgs[ship['id']]
            img_scaled = pygame.transform.smoothscale(img, (int(ship_size*scale), int(ship_size*scale)))
            img_rect = img_scaled.get_rect(center=(rect.centerx + offset_x, rect.centery))
            
            # Darken locked ships instead of overlay
            if ship['id'] not in save_data['unlocked_ships']:
                # Create darkened version
                dark_img = img_scaled.copy()
                dark_overlay = pygame.Surface(img_scaled.get_size(), pygame.SRCALPHA)
                dark_overlay.fill((0, 0, 0, 150))
                dark_img.blit(dark_overlay, (0, 0))
                display_surface.blit(dark_img, img_rect)
                
                # Simple lock icon without heavy overlay
                lock_center = img_rect.centerx, img_rect.centery + 10
                pygame.draw.circle(display_surface, (200, 200, 200), (lock_center[0], lock_center[1]-8), 12, 3)
                pygame.draw.rect(display_surface, (200, 200, 200), (lock_center[0]-10, lock_center[1]-2, 20, 18), border_radius=4)
            else:
                display_surface.blit(img_scaled, img_rect)
            
            # Ship name
            name_surf = name_font.render(ship['name'], True, (255,255,255))
            name_rect = name_surf.get_rect(center=(rect.centerx + offset_x, rect.bottom+25))
            display_surface.blit(name_surf, name_rect)
            
            # Price (if locked)
            if ship['id'] not in save_data['unlocked_ships']:
                price_surf = price_font.render(f'{ship["price"]} credits', True, (255,220,80))
                price_rect = price_surf.get_rect(center=(rect.centerx + offset_x, rect.bottom+55))
                display_surface.blit(price_surf, price_rect)
            
        # Back button with brush overlay on hover
        mx, my = pygame.mouse.get_pos()
        if back_button_rect.collidepoint((mx, my)):
            display_surface.blit(back_brush_stroke, back_brush_rect)
            back_button_surf = button_font.render('Back', True, (0,0,0))
        else:
            back_button_surf = button_font.render('Back', True, (255,255,255))
        
        display_surface.blit(back_button_surf, back_button_rect.move(30,10))
        
        # Draw dialogs LAST to ensure they appear on top
        if unlock_dialog:
            # Semi-transparent overlay to dim background
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            display_surface.blit(overlay, (0, 0))
            
            ship_id, ship_name, price = unlock_dialog
            dialog_surf = pygame.Surface((550, 280), pygame.SRCALPHA)
            dialog_surf.fill((25, 25, 25, 250))
            dialog_rect = dialog_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            
            # Draw dialog border
            pygame.draw.rect(display_surface, (100, 100, 100), dialog_rect, 3, border_radius=15)
            display_surface.blit(dialog_surf, dialog_rect)
            
            msg1 = dialog_font.render(f'Unlock {ship_name}?', True, (255,255,255))
            msg2 = dialog_font.render(f'Cost: {price} credits', True, (255,220,80))
            msg1_rect = msg1.get_rect(center=(dialog_rect.centerx, dialog_rect.top + 70))
            msg2_rect = msg2.get_rect(center=(dialog_rect.centerx, dialog_rect.top + 120))
            display_surface.blit(msg1, msg1_rect)
            display_surface.blit(msg2, msg2_rect)
            
            # Confirm/cancel buttons without overlays, moved higher with spacing
            confirm_rect = pygame.Rect(WINDOW_WIDTH//2-140, WINDOW_HEIGHT//2+50, 120, 50)
            cancel_rect = pygame.Rect(WINDOW_WIDTH//2+20, WINDOW_HEIGHT//2+50, 120, 50)
            
            # Simple colored backgrounds
            pygame.draw.rect(display_surface, (60,180,60), confirm_rect, border_radius=8)
            pygame.draw.rect(display_surface, (180,60,60), cancel_rect, border_radius=8)
            
            conf_surf = dialog_button_font.render('Buy', True, (255,255,255))
            canc_surf = dialog_button_font.render('Back', True, (255,255,255))
            conf_rect = conf_surf.get_rect(center=confirm_rect.center)
            canc_rect = canc_surf.get_rect(center=cancel_rect.center)
            display_surface.blit(conf_surf, conf_rect)
            display_surface.blit(canc_surf, canc_rect)
        if error_dialog:
            # Semi-transparent overlay to dim background
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            display_surface.blit(overlay, (0, 0))
            
            dialog_surf = pygame.Surface((500, 220), pygame.SRCALPHA)
            dialog_surf.fill((25, 25, 25, 250))
            dialog_rect = dialog_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            
            # Draw dialog border
            pygame.draw.rect(display_surface, (100, 100, 100), dialog_rect, 3, border_radius=15)
            display_surface.blit(dialog_surf, dialog_rect)
            
            msg = dialog_font.render(error_dialog, True, (255,100,100))
            msg_rect = msg.get_rect(center=(dialog_rect.centerx, dialog_rect.top + 80))
            display_surface.blit(msg, msg_rect)
            
            ok_rect = pygame.Rect(WINDOW_WIDTH//2-60, WINDOW_HEIGHT//2+40, 120, 50)
            
            # Simple colored background
            pygame.draw.rect(display_surface, (80,80,200), ok_rect, border_radius=8)
            
            ok_surf = dialog_button_font.render('OK', True, (255,255,255))
            ok_surf_rect = ok_surf.get_rect(center=ok_rect.center)
            display_surface.blit(ok_surf, ok_surf_rect)
        pygame.display.update()
        clock.tick(60)
    save_data['last_selected_ship'] = selected_ship_id
    save_save_data(save_data)
    return selected_ship_id

main_menu(play_text_surf, version_surf, credits_text_surf)