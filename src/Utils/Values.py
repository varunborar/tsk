from DataHandlers.Config import Config

def available_categories():
    c = Config()
    return c.get_categories()