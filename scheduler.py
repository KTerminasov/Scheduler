import requests


class Scheduler:
    """Класс, реализующий работу с занятостью работника."""

    def __init__(self, url):
        """Инициализация класса."""
        self.url = url
        self.data = self._get_data()
        self.days = {day['date']: day for day in self.data['days']}
        self.timeslots = self._parse_timeslots()

    def _convert_to_minutes(self, time):
        """Преобразование часов в минуты."""
        hours, minutes = map(int, time.split(':'))
        return hours * 60 + minutes
    
    def _convert_to_hours(self, minutes):
        """Преобразование минут в часы."""
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours:02}:{minutes:02}"

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

    def is_available(self, date, start_time, end_time):
        """Проверка доступности работника в указанное время."""

        if date not in self.days:
            return False

        day = self.days[date]
        day_start = day['start']
        day_end = day['end']

        if (start_time < day_start or end_time > day_end or
                day_start >= day_end):
            return False

        busy_slots = self.get_busy_slots(date)
        if not busy_slots:
            return True

        for busy_start, busy_end in busy_slots:
            if ((start_time < busy_start and end_time > busy_start) or
                    (start_time < busy_end and end_time > busy_end) or
                    (start_time >= busy_start and end_time <= busy_end)):
                return False

        return True

    def find_slot_for_duration(self, duration_in_minutes):
        """Нахождение свободного слота для указанной продолжительности."""
        for date, slots in self.timeslots.items():
            free_slots = self.get_free_slots(date)  
            
            for start, end in free_slots:
                start_time = self._convert_to_minutes(start)
                end_time = self._convert_to_minutes(end)
       
                if end_time - start_time >= duration_in_minutes:
                    return (
                        date, start, 
                        self._convert_to_hours(
                            start_time + duration_in_minutes
                        )
                    )

        return ()
