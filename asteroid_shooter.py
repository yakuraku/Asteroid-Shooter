import pygame, sys
from random import randint, uniform

class Ship(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        
        self.image = pygame.image.load('assets/ship/ship.png').convert_alpha()
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

    def update(self, dt):
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
highscore_font = pygame.font.Font('assets/main_menu/LEMONMILK-BoldItalic.otf', 80)
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

version_surf = version_font.render("V1.5.1 - UNSTABLE", True, (255,255,255))
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


def retry_screen(highscore):

    menu_bg_music.set_volume(100)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        display_surface.fill('black')

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
                game()
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
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            
        display_surface.blit(scaled_mm_bg_image, (0,0))
        
        mx, my = pygame.mouse.get_pos()

        display_surface.blit(logo, logo_rect)
        display_surface.blit(version_surf, version_rect)

        # button_1 = pygame.Rect(50, 100, 200, 50)
        display_surface.blit(play_text_surf, play_text_rect)
        display_surface.blit(credits_text_surf, credits_text_rect)
    

        # pygame.draw.rect(display_surface, (255,0,0), button_1)

        if play_text_rect.collidepoint((mx, my)):
            # mouse_hover.play(1)
            if not play_mouse_hover_bool:
                mouse_hover.play()
                play_mouse_hover_bool = True
            display_surface.blit(scaled_brush_stroke, play_brush_stroke_rect)
            play_text_surf = font.render(play_text, True, (0,0,0))
            display_surface.blit(play_text_surf, play_text_rect)
            if pygame.mouse.get_pressed()[0]:
                click.play()
                menu_bg_music.set_volume(0)
                game()
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

def game(): 
    # game loop

    # sprite creation 
    ship = Ship(spaceship_group)

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
    retry_screen(highscore = score.ref_score)

main_menu(play_text_surf, version_surf, credits_text_surf)