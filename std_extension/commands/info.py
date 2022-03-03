import git
from git import InvalidGitRepositoryError

from api.command import categories
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.embed.style import Style
from api.extension import extension_manager
from api.translation.translatable import Translatable
from impl import runtime


def get_version():
    try:
        repo = git.Repo(search_parent_directories=True)
    except InvalidGitRepositoryError:
        return None

    version = next((tag for tag in repo.tags if tag.commit == repo.head.commit), None)

    if version is None:
        version = repo.git.rev_parse(repo.head.commit.hexsha, short=7)

    del repo

    return version


current_version = get_version()


@runtime.bot.slash_command(category=categories.info, description=Translatable("std_command_info_desc"))
async def info(ctx: MrvnCommandContext):
    embed = ctx.get_embed(Style.INFO, title=ctx.translate("std_command_info_title"))

    embed.add_field(name=ctx.translate("std_command_info_version"), value=f"`{current_version}`", inline=False)
    embed.add_field(name=ctx.translate("std_command_info_extensions"), value=", ".join([f"**{x}**" for x in extension_manager.extensions.keys()]), inline=False)
    embed.add_field(name=ctx.translate("std_command_info_commands"), value=f"**{len(runtime.bot.unique_app_commands)}**", inline=False)
    # Still hardcoding author names in 2022 kek
    embed.add_field(name=ctx.translate("std_command_info_authors"), value="**Iterator, HeroBrine1st**", inline=False)

    await ctx.respond(embed=embed)

