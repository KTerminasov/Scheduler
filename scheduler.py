import requests


class Scheduler:
    """Класс, реализующий работу с занятостью работника."""

    def __init__(self, url):
        """Инициализация класса."""
        self.url = url
        self.data = self._get_data()
        self.days = {day['date']: day for day in self.data['days']}
        self.timeslots = self._parse_timeslots()

    def _get_data(self):
        """Получение данных с помощью GET-запроса."""
        response = requests.get(self.url, timeout=10)
        return response.json()

    def _parse_timeslots(self):
        """Парсинг временных слотов и привязка их к датам."""
        timeslots = {}

        for day in self.data['days']:
            date = day['date']
            timeslots[date] = []

        for timeslot in self.data['timeslots']:
            day_id = timeslot['day_id']
            day = next(
                (d for d in self.data['days'] if d['id'] == day_id),
                None
            )
            if day:
                date = day['date']
                timeslots[date].append((timeslot['start'], timeslot['end']))

        for date, slots in timeslots.items():
            slots.sort(key=lambda x: x[0])

        return timeslots

    def get_busy_slots(self, date):
        """Получение всех занятых промежутков для указанной даты."""

        if date not in self.days or not self.timeslots[date]:
            return []

        return self.timeslots[date]

    def get_free_slots(self, date):
        """Получение всех свободных промежутков для указанной даты."""

        if date not in self.days:
            return []

        day = self.days[date]
        start_time = day['start']
        end_time = day['end']

        busy_slots = self.get_busy_slots(date)
        if not busy_slots:
            return [(start_time, end_time)]

        free_slots = []
        last_end = start_time

        for start, end in busy_slots:
            if last_end < start:
                free_slots.append((last_end, start))
            last_end = end

        if last_end < end_time:
            free_slots.append((last_end, end_time))

        return free_slots

