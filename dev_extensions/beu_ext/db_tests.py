from api.command.context.mrvn_command_context import MrvnCommandContext
from api.models import GuildSetting, GlobalSetting, Setting
from impl import runtime
from dev_extensions.beu_ext.models import GuildSettingTest


@runtime.bot.command()
async def all_settings(ctx: MrvnCommandContext):
    guild_settings = []
    global_settings = []

    for setting in GuildSetting.__subclasses__() + GlobalSetting.__subclasses__():
        model: Setting

        if issubclass(setting, GuildSetting):
            model = (await setting.get_or_create(guild_id=ctx.guild_id))[0]
            l = guild_settings
        else:
            model = (await setting.get_or_create())[0]
            l = global_settings

        l.append(f"{setting.category.name}: {setting.title} - {setting.description}: {model.value}")

    desc = "All global settings:\n" + "\n".join(global_settings) + "\nAll guild settings:\n" + "\n".join(guild_settings)

    await ctx.respond(f"```\n{desc}```")


