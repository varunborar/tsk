
class AbstractTaskHandler:

    def add_task(self, task):
        raise NotImplementedError('Method add_task not implemented')
    
    def get_task(self, task_key):
        raise NotImplementedError('Method get_task not implemented')
    
    def get_tasks(self):
        raise NotImplementedError('Method get_tasks not implemented')
    
    def update_task(self, task_key, task):
        raise NotImplementedError('Method update_task not implemented')
    
    def delete_task(self, task_key):
        raise NotImplementedError('Method delete_task not implemented')
    