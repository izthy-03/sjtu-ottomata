import click
from click import echo, secho
import time

from sjtu_sports.internel.credential import login
from sjtu_sports.worker import OttoTask
from sjtu_sports.worker.worker import WorkerImpl


# TODO: User CLI


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
def cli():
    pass

def test():
    session = login()
    worker = WorkerImpl(session)
    task = OttoTask(
        "3b10ff47-7e83-4c21-816c-5edc257168c1",
        "篮球",
        "2024-9-25",
        "any"
    )
    worker.add_task(task) 
    time.sleep(10000)

if __name__ == '__main__':
    print('Hello, Otto!')
    test()