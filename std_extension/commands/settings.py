import math
from typing import Union

from discord import Interaction, ButtonStyle, Embed, Option
from discord.ui import Item, Button

from api.command import categories
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.embed.style import Style
from api.event_handler.decorators import event_handler
from api.settings import settings
from api.settings.exc import SettingsValueWriteError
from api.settings.setting import GuildSetting, GlobalSetting
from api.translation.translator import Translator
from api.view.mrvn_paginator import MrvnPaginator
from api.view.mrvn_view import MrvnView
from impl import runtime

PAGE_SIZE = 5

autocomplete_guild = None
autocomplete_global = None

settings_group = runtime.bot.create_group("settings", "Edit and list settings.", category=categories.bot_management,
                                          discord_permissions=["administrator"])
global_settings_group = runtime.bot.create_group("global_settings", "Edit and list global settings.",
                                                 category=categories.owners_only, owners_only=True)


class CategoryView(MrvnView):
    def __init__(self, tr: Translator, items: list[Item], **kwargs):
        super().__init__(tr, *items, **kwargs)

        self.category_len = None

    async def callback(self, item: Item, interaction: Interaction):
        self.category_len = self.children.index(item)

        self.stop()


class CmdsPaginator(MrvnPaginator):
    def __init__(self, ctx: MrvnCommandContext, settings_list: list[tuple[str, str]], category_name: str,
                 is_global: bool, **kwargs):
        super().__init__(ctx, **kwargs)

        self.settings_list = settings_list
        self.category_name = category_name
        self.is_global = is_global

    async def get_page_contents(self) -> Union[str, Embed]:
        embed = self.ctx.get_embed(Style.INFO,
                                   title=f"{self.category_name} ({self.ctx.translate('std_command_settings_list_' + ('global' if self.is_global else 'guild'))})")
        page_settings = self.settings_list[(self.page_index * PAGE_SIZE):][:PAGE_SIZE]

        for setting in page_settings:
            embed.add_field(name=setting[0], value=setting[1],
                            inline=False)

        return embed


@event_handler
async def on_startup():
    global autocomplete_global
    global autocomplete_guild

    autocomplete_global = [x.key for x in GlobalSetting.__subclasses__()]
    autocomplete_guild = [x.key for x in GuildSetting.__subclasses__()]


async def edit_(ctx: MrvnCommandContext, key: str, value: str, global_setting: bool):
    cls = GlobalSetting if global_setting else GuildSetting

    try:
        setting = next(filter(lambda it: it.key == key, cls.__subclasses__()))
    except StopIteration:
        await ctx.respond_embed(Style.ERROR, ctx.translate("std_command_settings_edit_invalid_key"))
        return

    model = (await setting.get_or_create(guild_id=ctx.guild_id))[0]

    value_type = type(model.value_field)

    if value_type == bool:
        value = value.lower() == "true"

    try:
        model.value = value
    except SettingsValueWriteError as e:
        await ctx.respond_embed(Style.ERROR, ctx.translate(e.message),
                                ctx.translate("std_command_settings_edit_invalid_value"))
        return

    try:
        await model.save()
    except ValueError:
        await ctx.respond_embed(Style.ERROR,
                                ctx.format("std_command_settings_edit_invalid_value_for_type", value_type.__name__))
        return

    await ctx.respond_embed(Style.OK, ctx.translate("std_command_settings_edit_value_set"))


async def list_(ctx: MrvnCommandContext, global_setting: bool):
    items = []

    for cat in settings.categories:
        cat_settings = cat.get_settings(global_setting)

        items.append(
            Button(label=ctx.translate(cat.name), style=ButtonStyle.blurple if len(cat_settings) else ButtonStyle.gray,
                   disabled=not len(cat_settings)))

    view = CategoryView(ctx, items, author=ctx.author, timeout=10)

    message = await ctx.respond(ctx.translate("std_command_help_choose_category"), view=view)

    await view.wait()

    if view.category_len is None:
        return

    category = settings.categories[view.category_len]
    category_settings = category.get_settings(global_setting)

    count = len(category_settings)

    num_pages = math.ceil(count / PAGE_SIZE) if count > PAGE_SIZE else 1

    settings_list = []

    for setting in category_settings:
        if global_setting:
            value = (await setting.get_or_create())[0].value
        else:
            value = (await setting.get_or_create(guild_id=ctx.guild_id))[0].value

        settings_list.append((f"{setting.key} [{value}]", ctx.translate(setting.description)))

    paginator = CmdsPaginator(ctx, settings_list, ctx.translate(category.name), is_global=global_setting,
                              num_pages=num_pages,
                              timeout=30)

    await paginator.attach(message)


@settings_group.command(name="list")
async def list_cmd(ctx: MrvnCommandContext):
    await list_(ctx, False)


@settings_group.command()
async def edit(ctx: MrvnCommandContext, key: Option(str),
               value: str):
    await edit_(ctx, key, value, False)


@global_settings_group.command(name="list")
async def list_cmd(ctx: MrvnCommandContext):
    await list_(ctx, True)


@global_settings_group.command()
async def edit(ctx: MrvnCommandContext, key: Option(str),
               value: str):
    await edit_(ctx, key, value, True)
