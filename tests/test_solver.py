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
    """Enumerasi independen atas seluruh penempatan, termasuk posisi kosong."""
    ordered = sorted(positions, key=lambda p: p.id)
    best = None
    for choice in itertools.product([*volunteers, None], repeat=len(ordered)):
        taken = [(p, v) for p, v in zip(ordered, choice) if v is not None]
        if any(p.slot not in v.available_slots or p.role not in v.roles for p, v in taken):
            continue
        if len({(p.slot, v.id) for p, v in taken}) != len(taken):
            continue
        if any(choice.count(v) > v.max_tasks for v in volunteers):
            continue
        peak = max((choice.count(v) for v in volunteers), default=0)
        # Indeks relawan mengikuti urutan ID. Indeks terakhir berarti kosong.
        ids = sorted(v.id for v in volunteers)
        indices = tuple(len(ids) if v is None else ids.index(v.id) for v in choice)
        rank = (-len(taken), peak, indices)
        if best is None or rank < best:
            best = rank
            assignment = {p.id: (v.id if v else None) for p, v in zip(ordered, choice)}
    return -best[0], best[1], assignment


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

    def test_unicode_id_precedes_a_vacancy(self):
        volunteers = [Volunteer("😀", "Ayu", frozenset({"R"}), frozenset({"S"}), 1)]
        positions = [Position(pid, "S", "R", "Pos") for pid in ("P2", "P1")]
        result = solve_schedule(volunteers, positions)
        self.assertEqual(result.assignment, {"P1": "😀", "P2": None})

    def test_deep_search(self):
        positions = [Position(str(i), "S", "R", "Pos") for i in range(1100)]
        result = solve_schedule([], positions)
        self.assertTrue(result.is_optimal)
        self.assertEqual(result.assignment, dict.fromkeys(p.id for p in positions))

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
            self.assertEqual((result.coverage, result.max_load, result.assignment), score)
            self.assertEqual(verify_schedule(people, positions, result.assignment), [])


if __name__ == "__main__":
    unittest.main()
