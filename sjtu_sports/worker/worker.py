import threading
import logging
import requests
import time

from sjtu_sports.utils.error import *
from sjtu_sports.utils.logger import get_logger
from sjtu_sports.worker import WorkerInterface, OttoTask
from sjtu_sports.internel.credential import get_session
from sjtu_sports.internel.request import (
    get_field_info, confirm_order, get_field_type_id
)

from sjtu_sports.resources import tensity_list 

class WorkerImpl(WorkerInterface):
    def __init__(self, session: requests.Session, logger: logging.Logger) -> None:
        self.session = session
        self.tasks = []
        self.task_threads = []
        self.task_id_counter = 0
        self.mux = threading.Lock()

        # Start session update daemon
        update_thread = threading.Thread(target=self.__update_session)
        update_thread.setDaemon(True)

        # Logger
        self.logger = logger


    def __start_task(self, task: OttoTask, logger: logging.Logger):

        task.update_status("Initializing")
        
        # Get venTypeId by venueId and fieldType
        while not task.is_killed():
            try:
                task.field_type_id = get_field_type_id(self.session, task.venue_id, task.field_type_name)
                break

            except OttoError as err:
                logger.warning(f"Failed on getting venue type id list: {err}")
                time.sleep(1)
                continue
            except Exception as err:
                logger.error(f"Failed on getting venue type id list: {err}")
                task.update_status("InitErr:" + str(err))
                return
            
        task.update_status("RUNNING")

        while not task.is_killed():
            # 1. Query field info
            try: 
                fields = get_field_info(self.session, task.field_type_id, task.date, task.venue_id) 

            except OttoError as err:
                logger.warning(f"Failed on getting field info: {err}")
                time.sleep(1)
                continue

            except Exception as err:
                logger.error(f"Failed on getting field info: {err}")
                task.update_status("GetFieldInfoErr:" + str(err))
                return 

            # 2. Check field availability
            available_fields = []
            for field in fields:
                for start_time in task.start_time:
                    if start_time < 7 or start_time > len(field['priceList']):
                        continue
                    sub_field = field['priceList'][start_time-7]
                    if int(sub_field['count']) > 0:
                        available_fields.append((field, sub_field, start_time))

            if len(available_fields) == 0:
                logger.debug("No available field found, retrying...")
                time.sleep(1)
                continue 

            # 3. Confirm order
            format_time = lambda x: f"{x}:00-{x+1}:00"
            spaces = [] 
            for i in range(task.num):
                field, sub_field, start_time = available_fields[i]
                spaces.append({
                    "count": 1,
                    "venuePrice": sub_field['price'],
                    "status": 1,
                    "scheduleTime": format_time(start_time),
                    "subSitename": field['fieldName'],
                    "subSiteId": field['fieldId'],
                    "tensity": field['fieldDetailStatus'],
                    "venueNum": 1
                }) 

            data = {
                "venTypeId": task.field_type_id,
                "venueId": task.venue_id,
                "fieldType": task.field_type_name,
                "returnUrl": "https://sports.sjtu.edu.cn/#/paymentResult/1",
                "scheduleDate": task.date,
                "week": task.week,
                "spaces": spaces,
                "tenSity": tensity_list[int(field['fieldDetailStatus'])],
            }  

            try:
                confirm_order(self.session, data)
            except OttoError as err:
                print(f"Failed on confirming order: {err}")
                time.sleep(1)
                continue

            # 4. Task finished
            logger.info("Task finished.")
            task.update_status("Finished")
            return

    
    def __update_session(self):
        """
        Daemon thread to check session status periodically.
        """
        self.mux.acquire()

        self.mux.release()


    def add_task(self, task):
        self.mux.acquire()
        print('add task')
        task.id = self.task_id_counter
        task_logger = self.logger.getChild(f"t{task.id}")
        
        task.update_status("Pending")
        task_thread = threading.Thread(target=self.__start_task, args=(task, task_logger))

        self.tasks.append(task)
        self.task_threads.append(task_thread)
        self.task_id_counter += 1
             
        task_thread.setDaemon(True)
        task_thread.start()

        self.mux.release()
    
    def delete_task(self, task_id):
        print('delete task')
        self.mux.acquire()
        for task in self.tasks:
            if task.id == task_id:
                task.kill()
                return
        self.mux.release()
    
    def list_task(self):
        print('list task')
    