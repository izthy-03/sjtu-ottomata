import threading
import time
from sjtu_sports.worker import WorkerInterface
from sjtu_sports.internel.request import get_field_info, confirm_order
from sjtu_sports.internel.credential import get_session
from sjtu_sports.utils.error import *

class WorkerImpl(WorkerInterface):
    def __init__(self, session) -> None:
        self.session = session
        self.tasks = []
        self.task_threads = []
        self._task_id_counter = 0
        self.mux = threading.Lock()

        # Start session update daemon
        update_thread = threading.Thread(target=self.__update_session)
        update_thread.setDaemon(True)

    def __start_task(self, task):
        task._mux.acquire()
        task._status = "Running"
        task._mux.release()

        while True:
            # 1. Query field info
            try: 
                fields, err = get_field_info(self.session, task.field_type, task.date, task.venue_id) 
            except OttoError as err:
                if err.error_code == ErrorCode_kLoginExpired:
                   time.sleep(1)
                   continue 
                else:
                    task._mux.acquire()
                    task._status = ErrorCode_name[err.error_code]
                    print(f"Task {task._id} failed: {err}")
                    task._mux.release()
                    break
            # 2. Check field availability
            available_fields = []
            for field in fields:
                for time in task.start_time:
                    if time < 7:
                        continue
                    price_list = field['priceList'][time-7]
                    if price_list['count'] > 0:
                        available_fields.append((field, price_list))

            if len(available_fields) == 0:
               time.sleep(1)
               continue 

            # 3. Confirm order
            for i in range(task.num):
                field, price_list = available_fields[i]
                data = {
                    'fieldId': field['fieldId'],
                    'fieldType': field['fieldType'],
                    'venueId': field['venueId'],
                    'date': task.date,
                    'startTime': field['startTime'],
                    'endTime': field['endTime'],
                    'price': price_list['price'],
                    'priceId': price_list['priceId'],
                    'count': 1
                }
                try:
                    confirm_order(self.session, data)
                except OttoError as err:
                    task._mux.acquire()
                    task._status = ErrorCode_name[err.error_code]
                    print(f"Task {task._id} failed: {err}")
                    task._mux.release()
                    break
            
    
    def __update_session(self):
        """
        Daemon thread to check session status periodically.
        """
        self.mux.acquire()

        self.mux.release()


    def add_task(self, task):
        self.mux.acquire()
        print('add task')
        task._id = self._task_id_counter
        task._status = "Pending" 

        task_thread = threading.Thread(target=self.__start_task, args=(task,))
        self.tasks.append(task)
        self.task_threads.append(task_thread)
        self._task_id_counter += 1
             
        task_thread.setDaemon(True)
        task_thread.start()

        self.mux.release()
    
    def delete_task(self, task_id):
        print('delete task')
    
    def list_task(self):
        print('list task')
    