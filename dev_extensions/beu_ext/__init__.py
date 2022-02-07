import asyncio
import logging

from discord import User, Role, Option, OptionChoice, Member
from discord.abc import Mentionable, GuildChannel
from discord.commands import permissions
from discord.enums import SlashCommandOptionType

from api.command import categories
from api.command.command_category import CommandCategory
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.command.option.parse_until_ends import ParseUntilEndsOption
from api.command.permission.decorators import mrvn_owners_only
from api.embed.style import Style
from api.event_handler.decorators import event_handler
from api.translation.translatable import Translatable
from impl import runtime

from . import components_test
from . import pages_test
from . import view_test2

test_category = categories.add_category(CommandCategory(Translatable("beu_ext_category_name"), "test_category"))


@event_handler()
async def on_startup():
    logging.info("Beu startup!")


@runtime.bot.slash_command(category=categories.debug)
@mrvn_owners_only()
async def test(ctx: MrvnCommandContext, arg_1: str, arg_2: str):
    """Test command"""

    await ctx.respond_embed(Style.INFO, desc=f"arg_1: {arg_1}\narg_2: {arg_2}")


@runtime.bot.slash_command(category=categories.debug)
async def test_int(ctx: MrvnCommandContext, test_arg: int):
    """Test command with int arg"""

    await ctx.respond_embed(Style.INFO, str(test_arg))


@runtime.bot.slash_command(category=categories.debug)
async def multi_arg(ctx: MrvnCommandContext, string: str, integer: int, boolean: bool, user: User,
                    channel: GuildChannel, role: Role, mentionable: Mentionable, number: float):
    await ctx.respond_embed(Style.INFO, f"""
String: `{string}`
Integer: `{integer}`
Boolean: `{boolean}`
User: `{user}`
Channel: `{channel}`
Role: `{role}`
Mentionable: `{mentionable}`
Number: `{number}`
""")


@runtime.bot.slash_command(category=categories.debug)
async def optional_arg(ctx, optional: int = 0):
    await ctx.respond_embed(Style.INFO, str(optional))


group = runtime.bot.create_group("group", "A group", category=categories.debug)
sub_group = group.create_subgroup("subgroup", "A subgroup")


@group.command()
async def group_command(ctx):
    await ctx.respond_embed(Style.INFO, "Group test")


@sub_group.command()
async def sub_group_command(ctx):
    await ctx.respond_embed(Style.INFO, "Subgroup test!")


@sub_group.command()
async def sub_group_command2(ctx, test_arg: int):
    await ctx.respond_embed(Style.INFO, f"Argument: {test_arg}")


@runtime.bot.slash_command(category=categories.debug)
async def until_ends(ctx, query: ParseUntilEndsOption(str)):
    await ctx.respond_embed(Style.INFO, f"Query: `{query}`")


@runtime.bot.slash_command(category=categories.debug)
async def choices(ctx, choice_str: Option(str, choices=[OptionChoice("Choice 1", "Anus"),
                                                        OptionChoice("Choice 2", "Amogus"),
                                                        OptionChoice("Choice 3", "Test")])):
    await ctx.respond_embed(Style.INFO, f"{choice_str}")


@runtime.bot.slash_command(category=categories.debug)
async def attach(ctx, attachment: Option(SlashCommandOptionType.attachment)):
    await ctx.respond_embed(Style.OK, attachment.url)


@runtime.bot.user_command()
async def pidor(ctx, member: Member):
    await ctx.respond_embed(Style.INFO, f"{member.mention} пидор!")


@runtime.bot.slash_command(category=categories.debug)
async def deferred(ctx: MrvnCommandContext, ephemeral: bool):
    await ctx.defer(ephemeral=ephemeral)

    await asyncio.sleep(3)

    await ctx.respond_embed(Style.OK, "Deferred message test!")


@runtime.bot.slash_command(category=categories.debug)
async def trans(ctx: MrvnCommandContext):
    await ctx.respond_embed(Style.INFO, ctx.translate("test"))


@runtime.bot.slash_command(category=test_category)
async def cat(ctx: MrvnCommandContext):
    desc = []

    cats = sorted(categories.categories, key=lambda it: len(it.items), reverse=True)

    for category in cats:
        desc.append(f"{category.name}: {len(category.items)}")

    await ctx.respond_embed(Style.INFO, "\n".join(desc))


@runtime.bot.slash_command()
@mrvn_owners_only()
async def owner_only(ctx: MrvnCommandContext):
    await ctx.respond_embed(Style.OK, "You are the owner!")


@runtime.bot.slash_command()
async def exception(ctx: MrvnCommandContext):
    a = 5 / 0

    await ctx.respond_embed(Style.OK, "No exception!")
