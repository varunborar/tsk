import json 
import os

from Utils.Enums import SystemMode, StatusType

class Config:
    def __init__(self):
        self._config_file = os.path.join(os.path.expanduser('~'), '.tskrc')
        self._config = {}
        self._app_config = json.load(open('./app.json', 'r'))

        if not os.path.exists(self._config_file):
            self.init()
        else:
            self.load()
            self.update_system_params()
    
    def init(self):
        self._config = {
            'system' : {
                'version': self._app_config.get('version'),
                'mode': SystemMode.FILE.value,
                'file': {
                    'dataDirectory': os.path.join(os.path.expanduser('~'), '.tskdata')
                }
            },
            'categories': ['default'],
            'defaultCategory': 'default',
            'properties': {
                'default': {
                    'statusMode': StatusType.BOOL.value
                }
            },
            "preferences": {
                'default': {}
            }
        }
        self.save()
    
    def load(self):
        with open(self._config_file, 'r') as f:
            self._config = json.load(f)
    
    def save(self):
        with open(self._config_file, 'w') as f:
            json.dump(self._config, f, indent=4)
    
    def get(self, key, config=None):
        if config is None:
            config = self._config
        keys = key.split('.')
        if len(keys) == 1:
            if keys[0] not in config:
                raise KeyError(f'Key {key} not found in config')
            return config.get(keys[0])
        return self.get('.'.join(keys[1:]), config.get(keys[0]))
    
    def set(self, key, value, config=None):
        if config is None:
            config = self._config
        keys = key.split('.')
        if len(keys) == 1:
            config[keys[0]] = value
            self.save()
            return
        self.set('.'.join(keys[1:]), value, config.get(keys[0]))
    
    def remove(self, key, config=None):
        if config is None:
            config = self._config
        keys = key.split('.')
        if len(keys) == 1:
            if keys[0] not in config:
                raise KeyError(f'Key {key} not found in config')
            del config[keys[0]]
            self.save()
            return
        self.remove('.'.join(keys[1:]), config.get(keys[0]))

    def update_system_params(self):
        self._config['system']['version'] = self._app_config.get('version')
        self.save()

    def get_mode(self):
        return self.get('system.mode')
    
    def set_mode(self, mode):
        self.set('system.mode', mode)

    def get_data_dir(self):
        return self.get('system.file.dataDirectory')
    
    def set_data_dir(self, data_dir):
        self.set('system.file.dataDirectory', data_dir)
    
    def get_categories(self):
        return self.get('categories')
    
    def add_category(self, category):
        categories = self.get_categories()
        categories.append(category)
        self.set('categories', categories)
    
    def get_default_category(self):
        return self.get('defaultCategory')
    
    def set_default_category(self, category):
        if category not in self.get_categories():
            self.add_category(category)
        self.set('defaultCategory', category)

    def get_preference(self, category, key):
        preferences = self.get('preferences')
        if category not in preferences:
            return None
        if not key:
            return preferences[category]
        return preferences[category].get(key)    
    
    def set_preference(self, category, key, value):
        preferences = self.get('preferences')
        if category not in preferences:
            preferences[category] = {}
        preferences[category][key] = value
        self.set('preferences', preferences)
    
    def clean_preferences(self):
        self.set('preferences', {})

    def remove_preference(self, category, key):
        preferences = self.get('preferences')
        if category not in preferences:
            return
        if key in preferences[category]:
            del preferences[category][key]
        self.set('preferences', preferences)
