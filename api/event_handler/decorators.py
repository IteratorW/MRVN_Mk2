from api.event_handler import handler_manager


def event_handler(event_name: str = None):
    def decorator(func):
        handler_manager.add_handler((func.__name__[3:] if func.__name__.startswith("on_") else func.__name__) if
                                    event_name is None else event_name, func)

        return func

    return decorator
