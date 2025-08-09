import unittest
from scheduler import Scheduler


class TestScheduler(unittest.TestCase):
    """Тестирование работы с занятостью работника."""

    def setUp(self):
        self.scheduler = Scheduler(
            url="https://ofc-test-01.tspb.su/test-task/"
        )

    def test_get_busy_slots(self):
        """Проверка получения занятых слотов."""

        result = self.scheduler.get_busy_slots("2025-02-15")
        self.assertEqual(result, [("09:00", "12:00"), ("17:30", "20:00")])

        result = self.scheduler.get_busy_slots("2024-10-12")
        self.assertEqual(result, [])
    
    def test_get_free_slots(self):
        """Проверка получения свободных слотов."""
        result = self.scheduler.get_free_slots("2025-02-15")
        self.assertEqual(result, [("12:00", "17:30"), ("20:00", "21:00")])

        result = self.scheduler.get_free_slots("2024-10-12")
        self.assertEqual(result, [])
