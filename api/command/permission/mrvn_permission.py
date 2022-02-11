class MrvnPermission:
    def __init__(self, discord_permissions: list[str] = None, owners_only: bool = False):
        if not discord_permissions and not owners_only:
            raise ValueError("Invalid permission. Specify either a list of permissions or owners_only = True")

        self.discord_permissions = discord_permissions
        self.owners_only = owners_only
