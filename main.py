import os
import sys
import random
import pygame


# Конфигурация места исполнения
os.chdir(os.path.dirname(__file__))

# Инициализация Pygame
pygame.init()

# Инициализация музыкального плеера
pygame.mixer.init()
pygame.mixer.music.set_volume(0.01)
# Список композиций
playlist = ["music/" + file for file in os.listdir("music") if file.endswith(".mp3")]
random.shuffle(playlist)
# Запуск фоновой музыки
playlist_index = 0
pygame.mixer.music.load(playlist[playlist_index])
pygame.mixer.music.play()
playlist_index += 1

# Параметры игры
WIDTH, HEIGHT = 800, 600  # Размеры окна
FPS = 60  # Кадры в секунду
PLAYER_WIDTH, PLAYER_HEIGHT = 80, 40  # Размеры машин игроков
ENEMY_WIDTH, ENEMY_HEIGHT = 80, 40  # Размеры остальных машин
ROAD_WIDTH = WIDTH // 2  # Ширина дороги каждого
CAR_SPEED = 5
FINISH = 1_000

# Настройки экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Гонки для двух игроков")


# Класс игрока
class Player:
    count = 0

    def __init__(self, x, name=None, second_player=False):
        # Считаем кол-во объектов класса
        Player.count = 1 + (Player.count % 2)
        # Список возможных картинок машин
        enemy_images = ["images/" + file for file in os.listdir("images") if file.endswith(".png") and "cropped" in file]
        # Выбор случайной картинки
        image_path = random.choice(enemy_images)
        # Установка картинки
        self.image = pygame.image.load(image_path)
        # Масштабирование картинки под нужный размер
        self.image = pygame.transform.scale(self.image, (PLAYER_HEIGHT, PLAYER_WIDTH))
        # Установка границ машины игрока
        self.rect = self.image.get_rect(center=(x, HEIGHT - PLAYER_HEIGHT))
        # Имя
        self.name = f"Игрок {Player.count}" if not name else name
        # Счёт
        self.score = 0
        self.score_font = pygame.font.Font(None, 36)
        # Статус
        self.alive = True
        # Установка флага второго игрока
        self.second_player = second_player

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

        # Ограничение движения игрока в пределах его дороги
        # Ограничения по горизонтали
        if not self.second_player:  # Проверка на второго игрока
            # Ограничения для первого игрока
            if self.rect.x < 0:
                self.rect.x = 0
            elif self.rect.x > ROAD_WIDTH - PLAYER_HEIGHT - 50:
                self.rect.x = ROAD_WIDTH - PLAYER_HEIGHT - 50
        else:
            # Ограничения для второго игрока
            if self.rect.x < ROAD_WIDTH + 50:
                self.rect.x = ROAD_WIDTH + 50
            elif self.rect.x > ROAD_WIDTH * 2 - PLAYER_HEIGHT:
                self.rect.x = ROAD_WIDTH * 2 - PLAYER_HEIGHT
        # Ограничения по вертикали (у обоих игроков одинаковые)
        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.y > HEIGHT - PLAYER_WIDTH:
            self.rect.y = HEIGHT - PLAYER_WIDTH

    def update(self):
        self.score += 3 * (1 - self.rect.y / HEIGHT)

    def draw(self):
        screen.blit(self.image, self.rect)
        score = self.score_font.render(str(int(self.score)), True, (255, 255, 255))
        screen.blit(score, (10 + (self.rect.x > WIDTH / 2) * (WIDTH / 2 + 50), 10))


# Класс встречных машин
class Enemy:
    def __init__(self, x):
        # Список возможных картинок машин
        enemy_images = ["images/" + file for file in os.listdir("images") if file.endswith(".png") and "cropped" in file]
        # Выбор случайной картинки
        image_path = random.choice(enemy_images)
        # Установка картинки
        self.image = pygame.image.load(image_path)
        # Поворот картинки
        self.image = pygame.transform.rotate(self.image, -180)
        # Масштабирование картинки под нужный размер
        self.image = pygame.transform.scale(self.image, (ENEMY_HEIGHT, ENEMY_WIDTH))
        # Установка границ машины
        self.rect = self.image.get_rect(center=(x + ENEMY_WIDTH // 2, -ENEMY_HEIGHT))
        # Установка скорости
        self.speed = random.randint(6, 12)

    def move(self):
        self.rect.y += self.speed

    def draw(self):
        screen.blit(self.image, self.rect)


# Функция для генерации позиции встречной машины
def generate_enemy_position(occupied_positions):
    # Позиции X для возможного появления машины (каждые 50 пикселей)
    # Первый список для первой дороги, а второй для второй дороги
    spawn_points_x = [i - 12 for i in range(0, 350, 50)] + [i - 12 for i in range(450, 800, 50)]
    # Цикл генерации позиции
    while True:
        # Генерация случайной позиции на дороге
        x = random.choice(spawn_points_x)
        # Проверка свободна ли позиция
        if x not in occupied_positions:
            # Если свободна, добавляем в список занятых позиций
            occupied_positions.add(x)
            # И выходим из функции (и цикла)
            return x
        # Если нет, цикл повторяет генерацию новой случайной позиции, пока не найдёт свободную


# Функция для отображения сообщения о проигрыше
def display_message(text):
    screen.fill((255, 255, 255))  # Белый фон
    message_surface = pygame.font.Font(None, 64).render(text, True, (0, 0, 0))
    message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(message_surface, message_rect)
    pygame.display.flip()
    pygame.time.delay(2000)  # Задержка на 2 секунды


# Основная функция игры
def main():
    global playlist_index
    clock = pygame.time.Clock()

    player1 = Player(0 + PLAYER_HEIGHT // 2)  # Игрок 1
    player2 = Player(ROAD_WIDTH + 50 + PLAYER_HEIGHT // 2, second_player=True)  # Игрок 2

    enemies = []
    occupied_positions = set()  # Занятые позиции для врагов

    # Переменная для смешения текстур при симуляции движения
    texture_y = 0
    # Загрузка текстуры дороги
    road_texture = pygame.image.load("images/road.jpg")
    road_texture = pygame.transform.scale(road_texture, (50, 50))  # Масштабируем текстуру до нужного размера
    # Загрузка текстуры границы
    border_texture = pygame.image.load("images/border.jpg")
    border_texture = pygame.transform.scale(border_texture, (50, 50))  # Масштабируем текстуру до нужного размера

    # Игровой цикл
    while True:
        # Поддержание заданной частоты кадров
        clock.tick(FPS)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        # Проверка на включение следующей песни, когда закончилась прошлая
        if not pygame.mixer.music.get_busy():
            playlist_index += 1
            playlist_index %= len(playlist)
            pygame.mixer.music.load(playlist[playlist_index])
            pygame.mixer.music.play()

        # Заполнение игрового окна текстурами дороги
        texture_y += 5
        for y in range(-50, HEIGHT, 50):
            for x in range(0, WIDTH, 50):
                if x != 350 and x != 400:
                    screen.blit(road_texture, (x, y + texture_y))
                else:
                    screen.blit(border_texture, (x, y + texture_y))
        if texture_y == 50:
            texture_y = 0

        # Генерация врагов
        if random.randint(1, FPS) <= 2:  # Примерная частота появления врагов (2 врага/сек)
            enemy_position = generate_enemy_position(occupied_positions)
            enemies.append(Enemy(enemy_position))

        # Движение врагов и проверка на столкновение
        for enemy in enemies[:]:
            enemy.move()
            if enemy.rect.y > HEIGHT:
                enemies.remove(enemy)
                occupied_positions.remove(enemy.rect.x - ENEMY_HEIGHT // 2)  # Освобождаем позицию
            
            if enemy.rect.colliderect(player1.rect):
                display_message(f"{player1.name} проиграл!")
                return 0 # Завершение текущей игры и выход из функции
            elif enemy.rect.colliderect(player2.rect):
                display_message(f"{player2.name} проиграл!")
                return 0 # Завершение текущей игры и выход из функции

            enemy.draw()

        # Управление игроками
        pressed_keys = pygame.key.get_pressed()
        directions = [(0, -CAR_SPEED), (-CAR_SPEED, 0), (0, CAR_SPEED), (CAR_SPEED, 0)]
        players_keys = [
            (player1, [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]),
            (player2, [pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT])
        ]
        for player, keys in players_keys:
            for i in range(len(keys)):
                if pressed_keys[keys[i]]:
                    player.move(*directions[i])

        # Отображение игроков
        player1.update()
        player2.update()
        player1.draw()
        player2.draw()

        # Обновление экрана
        pygame.display.flip()


if __name__ == "__main__":
    while True:
        main()