"""Game rules separated from Pygame so they can be tested independently."""

import json
import random
from pathlib import Path

GRID_WIDTH = 30
GRID_HEIGHT = 22
DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}
HIGH_SCORE_FILE = Path(__file__).with_name("high_score.json")


def create_initial_snake():
    """Return a three-cell snake near the center of the board."""
    center_x = GRID_WIDTH // 2
    center_y = GRID_HEIGHT // 2
    return [(center_x, center_y), (center_x - 1, center_y), (center_x - 2, center_y)]


def get_next_head(head, direction):
    """Calculate the next head coordinate without changing the snake."""
    return (head[0] + direction[0], head[1] + direction[1])


def is_collision(new_head, snake, eating=False):
    """Return True for wall collisions or collisions with the body.

    If the snake is not eating, its tail moves away during this update,
    so moving into the current tail cell is allowed.
    """
    x, y = new_head
    if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
        return True

    body_to_check = snake if eating else snake[:-1]
    return new_head in body_to_check


def place_food(snake, rng=None):
    """Choose an unoccupied cell. Return None if the board is full."""
    rng = rng or random
    occupied = set(snake)
    empty_cells = [
        (x, y)
        for x in range(GRID_WIDTH)
        for y in range(GRID_HEIGHT)
        if (x, y) not in occupied
    ]
    return rng.choice(empty_cells) if empty_cells else None


def load_high_score(path=HIGH_SCORE_FILE):
    """Load the saved best score; return zero if no valid file exists."""
    try:
        with open(path, "r", encoding="utf-8") as score_file:
            data = json.load(score_file)
        score = data.get("high_score", 0)
        return score if type(score) is int and score >= 0 else 0
    except (OSError, json.JSONDecodeError, AttributeError, TypeError):
        return 0


def save_high_score(score, path=HIGH_SCORE_FILE):
    """Save a non-negative high score as JSON."""
    if type(score) is not int or score < 0:
        raise ValueError("Score must be a non-negative integer.")

    with open(path, "w", encoding="utf-8") as score_file:
        json.dump({"high_score": score}, score_file, indent=2)
