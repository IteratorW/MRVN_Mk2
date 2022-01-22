from api.event_handler import handler_manager


def event_handler(event_name: str):
    def decorator(func):
        handler_manager.add_handler(event_name, func)

        return func

    return decorator
