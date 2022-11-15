from threading import Thread

'''
    Could I have passed an is_daemon param to the decorator? Yes. 
    Would that have made things less clear? imo, also yes.
    Functions are duplicates with daemon set to True in threaded_user 
    and False in threaded_daemon.
'''

def threaded_daemon(fn):
    """
    Program will exit when only daemon threads are left. 
    Decorator sets daemonto True; 
    Main *will not* wait on decorated function thread completion beforing finishing.
    """
    def wrapper(*args, **kwargs):
        thread = Thread(name=fn.__name__, target=fn, daemon=True, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


def threaded_user(fn):
    """
    Non-daemon threads are "user" threads. 
    Decorator sets daemon to False; 
    Main *will* wait on decorated function thread completion before finishing.
    """
    def wrapper(*args, **kwargs):
        thread = Thread(name=fn.__name__, target=fn, daemon=False, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper
    