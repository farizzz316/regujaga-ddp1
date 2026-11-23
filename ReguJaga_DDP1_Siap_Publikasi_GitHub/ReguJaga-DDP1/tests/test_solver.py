"""Pengujian skenario utama dan oracle exhaustive yang independen dari solver."""
import itertools
import random
import unittest
from _setup import *  # noqa: F403
from regujaga.baseline import greedy_schedule
from regujaga.models import Position, Volunteer
from regujaga.rules import verify_schedule
from regujaga.solver import solve_schedule


def make_trap():
    people = [Volunteer("N", "Nara", frozenset({"R", "D"}), frozenset({"S1"}), 1),
              Volunteer("B", "Bima", frozenset({"R"}), frozenset({"S1"}), 1)]
    positions = [Position("P1", "S1", "R", "Meja"), Position("P2", "S1", "D", "Panggung")]
    return people, positions


def brute_score(volunteers, positions):
    """Oracle kecil: enumerasi semua assignment dan gunakan verifier, bukan fungsi solver."""
    best = (-1, float("inf"))
    ids = [None] + [v.id for v in volunteers]
    for choice in itertools.product(ids, repeat=len(positions)):
        assignment = dict(zip((p.id for p in positions), choice))
        if verify_schedule(volunteers, positions, assignment):
            continue
        coverage = sum(x is not None for x in choice)
        load = max((choice.count(v.id) for v in volunteers), default=0)
        if coverage > best[0] or (coverage == best[0] and load < best[1]):
            best = (coverage, load)
    return best


class SolverTest(unittest.TestCase):
    def test_greedy_trap(self):
        volunteers, positions = make_trap()
        greedy = greedy_schedule(volunteers, positions)
        optimal = solve_schedule(volunteers, positions)
        self.assertEqual(greedy.coverage, 1)
        self.assertEqual(optimal.coverage, 2)
        self.assertEqual(optimal.assignment, {"P1": "B", "P2": "N"})
        self.assertTrue(optimal.is_optimal)

    def test_cancel_bima(self):
        volunteers, positions = make_trap()
        result = solve_schedule([volunteers[0]], positions)
        self.assertEqual(result.coverage, 1)
        self.assertFalse(verify_schedule([volunteers[0]], positions, result.assignment))

    def test_node_limit_zero(self):
        volunteers, positions = make_trap()
        result = solve_schedule(volunteers, positions, max_nodes=0)
        self.assertFalse(result.is_optimal)
        self.assertEqual(result.nodes_explored, 0)
        self.assertEqual(result.coverage, 1)

    def test_node_limit_one(self):
        volunteers, positions = make_trap()
        result = solve_schedule(volunteers, positions, max_nodes=1)
        self.assertFalse(result.is_optimal)
        self.assertLessEqual(result.nodes_explored, 1)
        self.assertEqual(verify_schedule(volunteers, positions, result.assignment), [])

    def test_all_positions_unfillable(self):
        result = solve_schedule([], [Position("P", "S1", "R", "Gerbang")])
        self.assertEqual(result.coverage, 0)
        self.assertEqual(result.assignment["P"], None)
        self.assertTrue(result.is_optimal)

    def test_empty_positions(self):
        result = solve_schedule([], [])
        self.assertEqual(result.coverage, 0)
        self.assertEqual(result.percentage, 100.0)
        self.assertTrue(result.is_optimal)

    def test_balanced_peak(self):
        volunteers = [Volunteer("A", "A", frozenset({"R"}), frozenset({"S1", "S2"}), 2),
                      Volunteer("B", "B", frozenset({"R"}), frozenset({"S1", "S2"}), 2)]
        positions = [Position("P1", "S1", "R", "X"), Position("P2", "S2", "R", "Y")]
        result = solve_schedule(volunteers, positions)
        self.assertEqual((result.coverage, result.max_load), (2, 1))

    def test_deterministic(self):
        volunteers, positions = make_trap()
        self.assertEqual(solve_schedule(volunteers, positions), solve_schedule(volunteers, positions))

    def test_bad_node_limit(self):
        volunteers, positions = make_trap()
        with self.assertRaises(ValueError):
            solve_schedule(volunteers, positions, -1)

    def test_random_small_vs_independent_brute_force(self):
        rng = random.Random(20261123)
        for _ in range(35):
            people = []
            positions = []
            for i in range(rng.randint(0, 3)):
                people.append(Volunteer(f"V{i}", f"Nama {i}", frozenset(rng.sample(["R", "D"], rng.randint(1, 2))),
                                        frozenset(rng.sample(["S1", "S2"], rng.randint(1, 2))),
                                        rng.randint(0, 2)))
            for j in range(rng.randint(0, 4)):
                positions.append(Position(f"P{j}", rng.choice(["S1", "S2"]),
                                          rng.choice(["R", "D"]), "Pos"))
            result = solve_schedule(people, positions, max_nodes=50000)
            score = brute_score(people, positions)
            self.assertTrue(result.is_optimal)
            self.assertEqual((result.coverage, result.max_load), score)
            self.assertEqual(verify_schedule(people, positions, result.assignment), [])


if __name__ == "__main__":
    unittest.main()
