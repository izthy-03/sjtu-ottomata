import click
import time
import logging

from sjtu_sports.internel.credential import login
from sjtu_sports.utils.logger import get_logger
from sjtu_sports.worker import OttoTask
from sjtu_sports.worker.worker import WorkerImpl


# TODO: User CLI


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
def cli():
    pass

def test():
    session = login()
    print(11)
    logger = get_logger("worker1", console_level=logging.DEBUG, log_file_path="./log")
    worker = WorkerImpl(session, logger)
    task = OttoTask(
        "3b10ff47-7e83-4c21-816c-5edc257168c1",
        "羽毛球",
        "2024-11-02"
        # force=True
    )

    print(task)
    worker.add_task(task) 
    time.sleep(10000)

if __name__ == '__main__':
    print('Hello, Otto!')
    test()