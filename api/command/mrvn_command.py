from discord.ext.bridge import BridgeCommand, BridgeExtCommand, BridgeSlashCommand


class MrvnCommand(BridgeCommand):
    def __init__(self, callback, **kwargs):
        super().__init__(callback, **kwargs)

        self.slash_variant: MrvnSlashCommand = kwargs.pop(
            "slash_variant", None
        ) or MrvnSlashCommand(callback, **kwargs)
        self.ext_variant: MrvnPrefixCommand = kwargs.pop(
            "ext_variant", None
        ) or MrvnPrefixCommand(callback, **kwargs)


class MrvnPrefixCommand(BridgeExtCommand):
    pass


class MrvnSlashCommand(BridgeSlashCommand):
    pass
