import json

from DataHandlers.Task.AbstractTaskHandler import AbstractTaskHandler
from DataHandlers.Task.Model import Task


class JsonTaskHandler(AbstractTaskHandler):

    def __init__(self, handler_config):
        self.handler_config = handler_config
        self.tasks = []

    def add_task(self, task):
        pass

    def get_task(self, task_key):
        pass

    def get_tasks(self):
        pass

    def update_task(self, task_key, task):
        pass

    def delete_task(self, task_key):
        pass