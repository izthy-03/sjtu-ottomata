import threading
import datetime 
from abc import ABC, abstractmethod


class OttoTask():
    def __init__(self, venue_id, field_type, date, start_time, num=1, strategy="continuous") -> None:
        """
        Args:
            venue_id: string, venue id.
            field_type: string, field type.
            date: string, date.
            start_time: list of int, start times. Blank means any time.
            num: int, number of fields. Default is 1.
            strategy: string, strategy, continuous or any. Default is continuous.
        """
        self.venue_id = venue_id
        self.field_type = field_type
        self.date = date
        self.start_time = start_time
        self.num = num
        self.strategy = strategy

        self.venue_type_id = None

        self.id = -1
        self.status = "Undefined"
        self.mux = threading.Lock()

        # process start times
        if self.start_time == "any":
            self.start_time = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
        self.start_time.sort()
        # delete start time out of 7~22
        self.start_time = [time for time in self.start_time if time >= 7 and time <= 22]

        # calculate week
        week = datetime.datetime.strptime(date, "%Y-%m-%d").weekday()
        self.week = (week+1) % 7

    def update_status(self, status):
        self.mux.acquire()
        self.status = status
        self.mux.release()


class WorkerInterface(ABC):
    @abstractmethod
    def add_task(self, task: OttoTask):
        pass

    @abstractmethod
    def delete_task(self, task_id: int):
        pass

    @abstractmethod
    def list_task(self):
        pass
