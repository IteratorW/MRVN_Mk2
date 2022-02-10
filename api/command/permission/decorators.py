from api.command.permission.mrvn_permission import MrvnPermission


def mrvn_guild_only():
    def decorator(func):
        func.__mrvn_guild_only__ = True

        return func

    return decorator


def mrvn_owners_only():
    def decorator(func):
        func.__mrvn_perm__ = MrvnPermission(owners_only=True)

        return func

    return decorator


def mrvn_discord_permissions(*discord_permissions: str):
    def decorator(func):
        func = mrvn_guild_only()(func)

        func.__mrvn_perm__ = MrvnPermission(*discord_permissions)

        return func

    return decorator
