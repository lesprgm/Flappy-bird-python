import pygame, random, time
from pygame.locals import *
import sqlite3


SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Speed increases after every 100 point interval
SPEED = 20
GRAVITY = 2.5
GAME_SPEED = 15
SPEED_INCREMENT = 4
speed_increase_interval = 100
next_speed_increase = speed_increase_interval

GROUND_WIDTH = 2 * SCREEN_WIDTH
GROUND_HEIGHT = 100

PIPE_WIDTH = 80
PIPE_HEIGHT = 500

PIPE_GAP = 150
score = 0

pygame.font.init()

def create_database():
    # Connect to SQLite database (or create it if it doesn't exist)
    connection = sqlite3.connect("highscore.db")
    cursor = connection.cursor()
      
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Highscore (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM Highscore")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO Highscore (score) VALUES (0)")
    
    connection.commit()
    connection.close()

def get_highscore():
    connection = sqlite3.connect("highscore.db")
    cursor = connection.cursor()
    
    cursor.execute("SELECT score FROM Highscore WHERE id = 1")
    highscore = cursor.fetchone()[0]
    
    connection.close()
    return highscore

def update_highscore(new_score):
    connection = sqlite3.connect("highscore.db")
    cursor = connection.cursor()
    
    current_highscore = get_highscore()
    if new_score > current_highscore:
        cursor.execute("UPDATE Highscore SET score = ? WHERE id = 1", (new_score,))
    
    connection.commit()
    connection.close()

class Bird(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = [pygame.image.load('bluebird-upflap.png').convert_alpha(),
                       pygame.image.load('bluebird-midflap.png').convert_alpha(),
                       pygame.image.load('bluebird-downflap.png').convert_alpha()]

        self.speed = SPEED

        self.current_image = 0
        self.image = pygame.image.load('bluebird-upflap.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDTH / 6
        self.rect[1] = SCREEN_HEIGHT / 2
        
    def update(self):
        global score
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.speed += GRAVITY

        self.rect[1] += self.speed
        

        for pipe in pipe_group:
            if pygame.sprite.collide_mask(self, pipe):
  
                score = 0
            elif pipe.rect[0] + pipe.rect[2] < self.rect[0] and not pipe.passed:
 
                score += 5
                pipe.passed = True
        
 
    def bump(self):
        self.speed = -SPEED


    def begin(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]


class Pipe(pygame.sprite.Sprite):
    def __init__(self, inverted, xpos, ysize):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load('pipe-green.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDTH, PIPE_HEIGHT))

        self.rect = self.image.get_rect()
        self.rect[0] = xpos

        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = - (self.rect[3] - ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize

        self.mask = pygame.mask.from_surface(self.image)
        
        self.passed = False  

 
    def update(self):
        self.rect[0] -= GAME_SPEED
        


class Ground(pygame.sprite.Sprite):
    
    def __init__(self, xpos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDTH, GROUND_HEIGHT))

        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT
 
    def update(self):
        self.rect[0] -= GAME_SPEED
        

def is_off_screen(sprite):
    return sprite.rect[0] < -(sprite.rect[2])


def get_random_pipes(xpos):
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return pipe, pipe_inverted


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')

BACKGROUND_DAY = pygame.image.load('background-day.png')
BACKGROUND_DAY = pygame.transform.scale(BACKGROUND_DAY, (SCREEN_WIDTH, SCREEN_HEIGHT))
BACKGROUND_NIGHT = pygame.image.load('background-night.png')
BACKGROUND_NIGHT = pygame.transform.scale(BACKGROUND_NIGHT, (SCREEN_WIDTH, SCREEN_HEIGHT))
BEGIN_IMAGE = pygame.image.load('message.png').convert_alpha()
#CLOSE_IMAGE = pygame.image.load().convert_alpha()


bird_group = pygame.sprite.Group()
bird = Bird()
bird_group.add(bird)

ground_group = pygame.sprite.Group()
for i in range(2):
    ground = Ground(GROUND_WIDTH * i)
    ground_group.add(ground)

pipe_group = pygame.sprite.Group()
for i in range(2):
    pipes = get_random_pipes(SCREEN_WIDTH * i + 800)
    pipe_group.add(pipes[0])
    pipe_group.add(pipes[1])


clock = pygame.time.Clock()

begin = True

create_database()


while begin:

    clock.tick(15)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE or event.key == K_UP:
                bird.bump()
                begin = False

    screen.blit(BACKGROUND_DAY, (0, 0))
    screen.blit(BEGIN_IMAGE, (120, 150))


    if is_off_screen(ground_group.sprites()[0]):
        ground_group.remove(ground_group.sprites()[0])

        new_ground = Ground(GROUND_WIDTH - 20)
        ground_group.add(new_ground)


    bird.begin()
    ground_group.update()

    bird_group.draw(screen)
    ground_group.draw(screen)

    pygame.display.update()


# Main game loop
while True:

    clock.tick(15)
    font = pygame.font.Font(None, 36)

    if (score // 100) % 2 == 1:
        background = BACKGROUND_NIGHT
    else:
        background = BACKGROUND_DAY

    if score >= next_speed_increase:
        GAME_SPEED += SPEED_INCREMENT
        next_speed_increase += speed_increase_interval

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE or event.key == K_UP:
                bird.bump()
    screen.blit(background, (0, 0))

  
    if is_off_screen(ground_group.sprites()[0]):
        ground_group.remove(ground_group.sprites()[0])

        new_ground = Ground(GROUND_WIDTH - 20)
        ground_group.add(new_ground)

  
    if is_off_screen(pipe_group.sprites()[0]):
        pipe_group.remove(pipe_group.sprites()[0])
        pipe_group.remove(pipe_group.sprites()[0])

        pipes = get_random_pipes(SCREEN_WIDTH * 2)

        pipe_group.add(pipes[0])
        pipe_group.add(pipes[1])

 
    bird_group.update()
    ground_group.update()
    pipe_group.update()


    bird_group.draw(screen)
    pipe_group.draw(screen)
    ground_group.draw(screen)
    
 
    score_text = font.render(f'Score: {score}', True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    

    highscore = get_highscore()
    highscore_text = font.render(f'High Score: {highscore}', True, (255, 255, 255))
    screen.blit(highscore_text, (10, 50))

    pygame.display.update()

    if (pygame.sprite.groupcollide(bird_group, ground_group, False, False, pygame.sprite.collide_mask) or
            pygame.sprite.groupcollide(bird_group, pipe_group, False, False, pygame.sprite.collide_mask)):
        time.sleep(1)
        
    
        update_highscore(score)
        
        game_over_image = pygame.image.load('gameover.png').convert_alpha()
        game_over_image = pygame.transform.scale(game_over_image, (int(game_over_image.get_width() * 0.3), int(game_over_image.get_height() * 0.3)))
        screen.blit(game_over_image, (SCREEN_WIDTH / 2 - game_over_image.get_width() / 2, SCREEN_HEIGHT / 2 - game_over_image.get_height() / 2))
        
 
        score_text = font.render(f'Your Score: {score}', True, (255, 255, 255))
        screen.blit(score_text, (SCREEN_WIDTH / 2 - score_text.get_width() / 2, SCREEN_HEIGHT / 2 + game_over_image.get_height() / 2 + 10))
        
     
        highscore = get_highscore()
        highscore_text = font.render(f'High Score: {highscore}', True, (255, 255, 255))
        screen.blit(highscore_text, (SCREEN_WIDTH / 2 - highscore_text.get_width() / 2, SCREEN_HEIGHT / 2 + game_over_image.get_height() / 2 + 50))

     
        pygame.display.update()
        
        wait_for_key = True
        while wait_for_key:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                if event.type == KEYDOWN:
                    if event.key == K_SPACE or event.key == K_UP:
                        bird.rect[1] = SCREEN_HEIGHT / 2
                        bird.speed = 0
                        pipe_group.empty()
                        ground_group.empty()
                        score = 0
                        for i in range(2):
                            ground = Ground(GROUND_WIDTH * i)
                            ground_group.add(ground)
                        for i in range(2):
                            pipes = get_random_pipes(SCREEN_WIDTH * i + 800)
                            pipe_group.add(pipes[0])
                            pipe_group.add(pipes[1])
                        wait_for_key = False
                        game_over = False 

    pygame.display.update()
