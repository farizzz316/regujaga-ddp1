import unittest
from _setup import *  # noqa: F403 - masukkan src ke sys.path
from regujaga.models import Volunteer, Position
from regujaga.rules import is_eligible, can_assign, validate_data, verify_schedule, describe_vacancy


class RulesTest(unittest.TestCase):
    def setUp(self):
        self.v = [
            Volunteer("A", "Andi", frozenset({"R"}), frozenset({"S1", "S2"}), 1),
            Volunteer("B", "Budi", frozenset({"D"}), frozenset({"S1"}), 2),
        ]
        self.p = [Position("P1", "S1", "R", "Depan"),
                  Position("P2", "S1", "R", "Belakang"),
                  Position("P3", "S2", "R", "Atas")]

    def test_role_and_availability(self):
        self.assertTrue(is_eligible(self.v[0], self.p[0]))
        self.assertFalse(is_eligible(self.v[1], self.p[0]))

    def test_reject_duplicate_volunteer_id(self):
        with self.assertRaisesRegex(ValueError, "duplikat"):
            validate_data([self.v[0], self.v[0]], self.p)

    def test_reject_duplicate_position_id(self):
        with self.assertRaisesRegex(ValueError, "duplikat"):
            validate_data(self.v, [self.p[0], self.p[0]])

    def test_reject_negative_capacity(self):
        x = Volunteer("C", "C", frozenset({"R"}), frozenset({"S1"}), -1)
        with self.assertRaises(ValueError):
            validate_data([x], self.p)

    def test_reject_empty_role(self):
        x = Volunteer("C", "C", frozenset(), frozenset({"S1"}), 1)
        with self.assertRaises(ValueError):
            validate_data([x], self.p)

    def test_detect_double_booking(self):
        schedule = {"P1": "A", "P2": "A", "P3": None}
        errors = verify_schedule(self.v, self.p, schedule)
        self.assertTrue(any("dua kali" in item for item in errors))

    def test_detect_task_limit(self):
        schedule = {"P1": "A", "P2": None, "P3": "A"}
        errors = verify_schedule(self.v, self.p, schedule)
        self.assertTrue(any("melebihi batas" in item for item in errors))

    def test_detect_unknown_volunteer(self):
        errors = verify_schedule(self.v, self.p, {"P1": "Z", "P2": None, "P3": None})
        self.assertTrue(any("tak dikenal" in item for item in errors))

    def test_detect_missing_position(self):
        errors = verify_schedule(self.v, self.p, {"P1": None})
        self.assertTrue(any("Kunci hasil" in item for item in errors))

    def test_can_assign_obeys_capacity(self):
        mapping = {"P1": "A", "P2": None, "P3": None}
        pmap = {p.id: p for p in self.p}
        self.assertFalse(can_assign(self.v[0], self.p[2], mapping, pmap))

    def test_vacancy_explanation(self):
        vacancy = Position("P9", "S3", "Keamanan", "Gerbang")
        text = describe_vacancy(vacancy, self.v, {"P9": None}, [vacancy])
        self.assertIn("Tidak ada relawan", text)


if __name__ == "__main__":
    unittest.main()
