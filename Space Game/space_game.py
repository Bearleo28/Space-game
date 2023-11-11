import pygame
import os
import time
import random

pygame.init()
pygame.display.init()
pygame.font.init()
pygame.mixer.init()
#window
width, height = 1440, 1080
WIN = pygame.display.set_mode((width, height), pygame.RESIZABLE)

pygame.display.set_caption("SPACE!!!!!!!")



#Loading images
red_ship = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
green_ship = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
blue_ship = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

#main player ship
yellow_ship = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

#background
bg = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (width, height))

#Lasers
red_lazer = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
green_lazer = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
blue_lazer = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
yellow_laser = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

#sound effects and music
laser_sound = pygame.mixer.Sound(os.path.join("sounds", "laser.wav"))

bg_music = pygame.mixer.Sound(os.path.join("sounds", "enigma.mp3"))

main_music = pygame.mixer.music.load(os.path.join("sounds", "elevator_music.mp3"))

lost_music = pygame.mixer.Sound(os.path.join("sounds", "lobby_time.mp3"))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)
    
    def collision(self, obj):
        return collide(self, obj)



#ship class
class Ship():
    COOLDOWN = 20
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_donw_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_donw_counter >= self.COOLDOWN:
            self.cool_donw_counter = 0
        elif self.cool_donw_counter > 0:
            self.cool_donw_counter += 1

    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()
    
    def shoot(self):
        if self.cool_donw_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_donw_counter = 1
                    
#defines the players ship and attributes
class PLayer(Ship):
    

    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = yellow_ship
        self.laser_img = yellow_laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        count = 0
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)
                        count+=1
        return count
                        
                        
                        

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)


#enemy ship attributes
class Enemy(Ship):
    COLOR_MAP = {
                "red": (red_ship, red_lazer),
                "green": (green_ship, green_lazer),
                "blue": (blue_ship, blue_lazer),
                 }


    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_donw_counter == 0:
            laser = Laser(self.x-18, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_donw_counter = 1


    #defining the collision masks of the enemys versus the laser blasts
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

#main loop
def main():
    run = True
    FPS = 90
    clock = pygame.time.Clock()
    level = 0
    lives = 5
    bg_music.play(-1)
    bg_music.set_volume(0.3)
    
    score = 0
    main_font = pygame.font.SysFont("magneto", 40)
    lost_font = pygame.font.SysFont("showcard", 40)


    enemies = []
    wave_length = 5
    enemy_vel = 0.8
    laser_vel = 5
    playerLaserVel = 8
    lost = False
    lost_count = 0

    player_vel = 8

    player = PLayer(680, 680)
    #loads the player on to the window
    def redraw_window():
        WIN.blit(bg, (0,0))
        #text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level : {level}", 1, (255, 255, 255))
        score_label = main_font.render(f"Score : {score}", 1, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (width - level_label.get_width() - 10, 10))
        WIN.blit(score_label, (width/2 - score_label.get_width()/2, 10))

        for enemy in enemies:
            enemy.draw(WIN)
        
        

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("YOU LOST!!! TOO BAD BRUH!", 1, (255, 255, 255))
            WIN.blit(lost_label, (width/2 - lost_label.get_width()/2, 350))

        pygame.display.update()


    while run:
        
        clock.tick(FPS)
        redraw_window() 
        

        if lives <= 0 or player.health <= 0:
            pygame.mixer.Sound.stop(bg_music)
            pygame.mixer.Sound.play(lost_music)
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 5:
                run = False
                pygame.mixer.Sound.stop(lost_music)
                main_menu()
            else:
                continue
            
        
        if len(enemies) == 0:
            level += 1
            player.health = player.max_health
            if level > 1:
                lives += 1

            
            wave_length += 3
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, width-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                bg_music.stop()
                main_menu()

        
        #Getting the movements of the player:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: #makes ship go left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < width: #to the right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: #up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() < height: #down
            player.y += player_vel
        #shooting laser
        if keys[pygame.K_SPACE]:
            player.shoot()
            laser_sound.play()
            laser_sound.set_volume(0.3)
        if keys[pygame.K_m]:
            bg_music.stop()
        if keys[pygame.K_n]:
            bg_music.play()

        
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 4*60) == 1:
                enemy.shoot()

            

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
                
            elif enemy.y + enemy.get_height() > height:
                lives -= 1
                enemies.remove(enemy)
        
            
                
            

        enemiesHit = player.move_lasers(-playerLaserVel, enemies)
        score += enemiesHit * 100



def main_menu():
    title_font = pygame.font.SysFont("magneto", 30)
    main_font = pygame.font.SysFont("magneto", 70)
    run = True
    pygame.mixer.music.play(-1, 0, 3)
    while run:
        WIN.blit(bg, (0,0))
        title_label = title_font.render("Press Left Mouse Button to Start!", 1, (255, 255, 255))
        WIN.blit(title_label, (width/2 - title_label.get_width()/2, 550))

        main_title = main_font.render("WELCOME TO SPACE GAME!!!", 1, (255,255,255))
        WIN.blit(main_title, (width/2 - main_title.get_width()/2, 350))

        pygame.display.update()

       

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.mixer.music.stop()
                main()      
    pygame.quit()


main_menu()