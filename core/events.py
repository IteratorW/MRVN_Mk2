from collections import defaultdict

callbacks = defaultdict(list)



def event(cb: callable):
    """
    Зарегистрировать колбек в системе ивентов
    """
    callbacks[cb.__name__].append(cb)
    return cb