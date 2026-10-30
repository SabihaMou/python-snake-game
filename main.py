"""Snake Game: a beginner-friendly Pygame project.

Run with: python main.py
Controls:
  Menu: Up/Down to choose difficulty, Enter to start, Esc to quit
  Game: Arrow keys or WASD to move, P to pause, Esc to return to menu
  Game over: Enter to play again, M for menu, Esc to quit
"""

import pygame

from game_logic import (
    DIRECTIONS,
    GRID_HEIGHT,
    GRID_WIDTH,
    create_initial_snake,
    get_next_head,
    is_collision,
    place_food,
    load_high_score,
    save_high_score,
)

CELL_SIZE = 24
WIDTH = GRID_WIDTH * CELL_SIZE
HEIGHT = GRID_HEIGHT * CELL_SIZE
FPS_BY_DIFFICULTY = {"Easy": 7, "Normal": 11, "Hard": 16}

BACKGROUND = (18, 22, 30)
GRID_LINE = (29, 35, 45)
SNAKE_HEAD = (104, 230, 150)
SNAKE_BODY = (47, 175, 105)
FOOD_COLOR = (245, 95, 95)
TEXT = (240, 244, 248)
MUTED = (165, 175, 190)
PANEL = (31, 39, 52)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Quest")
clock = pygame.time.Clock()
title_font = pygame.font.Font(None, 68)
large_font = pygame.font.Font(None, 48)
font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)


def draw_text(text, font_obj, color, center):
    """Render text centered at a position."""
    surface = font_obj.render(text, True, color)
    screen.blit(surface, surface.get_rect(center=center))


def draw_board():
    """Draw subtle grid lines to make movement cells clear."""
    screen.fill(BACKGROUND)
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRID_LINE, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRID_LINE, (0, y), (WIDTH, y), 1)


def draw_snake(snake):
    for index, (x, y) in enumerate(snake):
        rect = pygame.Rect(
            x * CELL_SIZE + 2,
            y * CELL_SIZE + 2,
            CELL_SIZE - 4,
            CELL_SIZE - 4,
        )
        pygame.draw.rect(
            screen,
            SNAKE_HEAD if index == 0 else SNAKE_BODY,
            rect,
            border_radius=6,
        )


def draw_food(food):
    if food is not None:
        x, y = food
        center = (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2)
        pygame.draw.circle(screen, FOOD_COLOR, center, CELL_SIZE // 2 - 3)


def draw_menu(selected, high_score):
    screen.fill(BACKGROUND)
    draw_text("SNAKE QUEST", title_font, SNAKE_HEAD, (WIDTH // 2, 145))
    draw_text("Choose your difficulty", font, TEXT, (WIDTH // 2, 225))

    options = list(FPS_BY_DIFFICULTY)
    for index, option in enumerate(options):
        color = SNAKE_HEAD if index == selected else MUTED
        prefix = "> " if index == selected else "  "
        draw_text(prefix + option, large_font, color, (WIDTH // 2, 295 + index * 58))

    draw_text(f"Best score: {high_score}", font, TEXT, (WIDTH // 2, 500))
    draw_text("UP/DOWN: select     ENTER: start     ESC: quit",
              small_font, MUTED, (WIDTH // 2, 480))


def draw_game(snake, food, score, high_score, difficulty, paused=False):
    draw_board()
    draw_food(food)
    draw_snake(snake)

    pygame.draw.rect(screen, PANEL, (0, 0, WIDTH, 42))
    draw_text(
        f"Score: {score}     Best: {high_score}     {difficulty}",
        small_font,
        TEXT,
        (WIDTH // 2, 21),
    )

    if paused:
        pygame.draw.rect(screen, PANEL, (WIDTH // 2 - 180, HEIGHT // 2 - 65, 360, 130),
                         border_radius=12)
        draw_text("PAUSED", large_font, SNAKE_HEAD, (WIDTH // 2, HEIGHT // 2 - 12))
        draw_text("Press P to continue", small_font, MUTED, (WIDTH // 2, HEIGHT // 2 + 28))


def draw_game_over(score, high_score):
    draw_board()
    pygame.draw.rect(screen, PANEL, (WIDTH // 2 - 220, HEIGHT // 2 - 125, 440, 250),
                     border_radius=16)
    draw_text("GAME OVER", large_font, FOOD_COLOR, (WIDTH // 2, HEIGHT // 2 - 75))
    draw_text(f"Score: {score}     Best: {high_score}", font, TEXT,
              (WIDTH // 2, HEIGHT // 2 - 20))
    draw_text("ENTER: play again", small_font, SNAKE_HEAD,
              (WIDTH // 2, HEIGHT // 2 + 35))
    draw_text("M: menu     ESC: quit", small_font, MUTED,
              (WIDTH // 2, HEIGHT // 2 + 72))


def start_new_game():
    snake = create_initial_snake()
    direction = DIRECTIONS["RIGHT"]
    food = place_food(snake)
    return snake, direction, direction, food, 0


def main():
    high_score = load_high_score()
    selected_difficulty = 1
    state = "menu"

    snake, direction, queued_direction, food, score = start_new_game()
    running = True
    turn_queued = False

    while running:
        # Process input events once per frame.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if state == "menu":
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        selected_difficulty = (selected_difficulty - 1) % 3
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        selected_difficulty = (selected_difficulty + 1) % 3
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        snake, direction, queued_direction, food, score = start_new_game()
                        state = "playing"
                        turn_queued = False

                elif state == "playing":
                    if event.key == pygame.K_ESCAPE:
                        state = "menu"
                    elif event.key == pygame.K_p:
                        state = "paused" if state == "playing" else "playing"
                    else:
                        key_to_direction = {
                            pygame.K_UP: DIRECTIONS["UP"],
                            pygame.K_w: DIRECTIONS["UP"],
                            pygame.K_DOWN: DIRECTIONS["DOWN"],
                            pygame.K_s: DIRECTIONS["DOWN"],
                            pygame.K_LEFT: DIRECTIONS["LEFT"],
                            pygame.K_a: DIRECTIONS["LEFT"],
                            pygame.K_RIGHT: DIRECTIONS["RIGHT"],
                            pygame.K_d: DIRECTIONS["RIGHT"],
                        }
                        candidate = key_to_direction.get(event.key)
                        if (candidate and not turn_queued
                                and candidate != (-direction[0], -direction[1])):
                            queued_direction = candidate
                            turn_queued = True

                elif state == "paused":
                    if event.key == pygame.K_p:
                        state = "playing"
                        turn_queued = False
                    elif event.key == pygame.K_ESCAPE:
                        state = "menu"

                elif state == "game_over":
                    if event.key == pygame.K_RETURN:
                        snake, direction, queued_direction, food, score = start_new_game()
                        state = "playing"
                        turn_queued = False
                    elif event.key == pygame.K_m:
                        state = "menu"
                    elif event.key == pygame.K_ESCAPE:
                        running = False

        if state == "playing":
            direction = queued_direction
            turn_queued = False
            new_head = get_next_head(snake[0], direction)
            eating = new_head == food

            if is_collision(new_head, snake, eating):
                state = "game_over"
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
            else:
                snake.insert(0, new_head)
                if eating:
                    score += 1
                    food = place_food(snake)
                    if food is None:  # The player filled every cell.
                        state = "game_over"
                        if score > high_score:
                            high_score = score
                            save_high_score(high_score)
                else:
                    snake.pop()

        if state == "menu":
            draw_menu(selected_difficulty, high_score)
        elif state in ("playing", "paused"):
            difficulty = list(FPS_BY_DIFFICULTY)[selected_difficulty]
            draw_game(snake, food, score, high_score, difficulty, state == "paused")
        elif state == "game_over":
            draw_game_over(score, high_score)

        pygame.display.flip()
        current_fps = FPS_BY_DIFFICULTY[list(FPS_BY_DIFFICULTY)[selected_difficulty]]
        clock.tick(current_fps if state == "playing" else 30)

    pygame.quit()


if __name__ == "__main__":
    main()
