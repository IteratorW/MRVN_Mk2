import asyncio
from collections import defaultdict

callbacks = defaultdict(list)



def event(cb: callable):
    if not asyncio.iscoroutinefunction(cb):
        raise TypeError('event registered must be a coroutine function')
    """
    Зарегистрировать колбек в системе ивентов
    """
    callbacks[cb.__name__].append(cb)
    return cb