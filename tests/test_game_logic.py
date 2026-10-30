"""Unit tests for the display-independent game rules."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import game_logic as game


class GameLogicTests(unittest.TestCase):
    def test_initial_snake(self):
        snake = game.create_initial_snake()
        self.assertEqual(len(snake), 3)
        self.assertEqual(len(set(snake)), 3)
        self.assertTrue(all(0 <= x < game.GRID_WIDTH and 0 <= y < game.GRID_HEIGHT for x, y in snake))

    def test_next_head(self):
        self.assertEqual(game.get_next_head((5, 5), game.DIRECTIONS["UP"]), (5, 4))

    def test_wall_collision(self):
        snake = [(5, 5)]
        for point in [(-1, 5), (game.GRID_WIDTH, 5), (5, -1), (5, game.GRID_HEIGHT)]:
            with self.subTest(point=point):
                self.assertTrue(game.is_collision(point, snake))

    def test_self_collision_and_tail_exception(self):
        snake = [(3, 3), (3, 4), (2, 4), (2, 3)]
        self.assertTrue(game.is_collision((3, 4), snake))
        self.assertFalse(game.is_collision((2, 3), snake, eating=False))
        self.assertTrue(game.is_collision((2, 3), snake, eating=True))
        self.assertFalse(game.is_collision((4, 3), snake))

    def test_food_avoids_snake(self):
        snake = [(0, 0), (1, 0)]
        for _ in range(20):
            food = game.place_food(snake)
            self.assertNotIn(food, snake)
            self.assertIsNotNone(food)

    def test_full_board_has_no_food(self):
        snake = [(x, y) for x in range(game.GRID_WIDTH) for y in range(game.GRID_HEIGHT)]
        self.assertIsNone(game.place_food(snake))

    def test_only_remaining_cell_selected(self):
        snake = [(x, y) for x in range(game.GRID_WIDTH) for y in range(game.GRID_HEIGHT) if (x, y) != (0, 0)]
        self.assertEqual(game.place_food(snake), (0, 0))

    def test_high_score_roundtrip_and_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "score.json"
            self.assertEqual(game.load_high_score(path), 0)
            game.save_high_score(16, path)
            self.assertEqual(game.load_high_score(path), 16)
            self.assertEqual(json.loads(path.read_text()), {"high_score": 16})

    def test_invalid_high_score(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "score.json"
            for value in ['not json', '{"high_score": -1}', '{"high_score": true}', '{"high_score": "16"}']:
                path.write_text(value)
                self.assertEqual(game.load_high_score(path), 0)
            for value in [-1, True, 1.5]:
                with self.assertRaises(ValueError):
                    game.save_high_score(value, path)


if __name__ == "__main__":
    unittest.main()
