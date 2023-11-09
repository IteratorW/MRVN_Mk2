import datetime

from discord import SelectOption, Interaction
from discord.ui import Select

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.command.option.parse_until_ends import ParseUntilEndsOption
from api.embed.style import Style
from api.translation.translatable import Translatable
from api.view.mrvn_view import MrvnView
from extensions.statistics.commands.stats_group import stats_group
from extensions.statistics.models import StatsEventEntry

event_group = stats_group.create_subgroup("event", "Events")


class Dropdown(Select):
    def __init__(self, events: list[StatsEventEntry]):
        options = [SelectOption(label=f"{x.event_date.strftime('%d.%m')} - {x.text}", emoji="❌") for x in events]

        super().__init__(
            placeholder=Translatable("statistics_command_daily_event_remove_select_placeholder"),
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: Interaction):
        selected_name = self.values[0]

        await interaction.response.defer(ephemeral=True)

        entry = await StatsEventEntry.get_or_none(guild_id=interaction.guild_id,
                                                  event_date=datetime.datetime.strptime(selected_name.split(" - ")[0],
                                                                                        "%d.%m").date())

        if entry is not None:
            await entry.delete()

        self.options = list(filter(lambda x: x.label != selected_name, self.options))

        if len(self.options) == 0:
            await interaction.message.edit(content=self.view.tr.translate("statistics_command_daily_event_all_removed"),
                                           view=None)
        else:
            await interaction.message.edit(view=self.view)

        await interaction.followup.send(self.view.tr.format("statistics_command_daily_event_remove_done",
                                                                    self.values[0]))


class DropdownView(MrvnView):
    def __init__(self, events: list[StatsEventEntry], **kwargs):
        super().__init__(timeout=10, **kwargs)
        self.add_item(Dropdown(events))


@event_group.command(description=Translatable("statistics_command_daily_event_add_desc"))
async def add(ctx: MrvnCommandContext, date: str, text: ParseUntilEndsOption(str)):
    try:
        date = datetime.datetime.strptime(date, "%d.%m")
    except ValueError:
        await ctx.respond_embed(Style.ERROR, ctx.translate("statistics_date_validation_invalid"))
        return

    if len(text) > 60:
        await ctx.respond_embed(Style.ERROR, ctx.translate("statistics_command_daily_event_add_error_text_too_long"))
        return

    await ctx.defer()

    await StatsEventEntry.update_or_create(guild_id=ctx.guild_id, event_date=date.date(),
                                           defaults={"text": text})

    await ctx.respond(ctx.translate("statistics_command_daily_event_add_ok"))


@event_group.command(description=Translatable("statistics_command_daily_event_list_desc"), name="list")
async def list_command(ctx: MrvnCommandContext):
    await ctx.defer()

    events: list[StatsEventEntry] = await StatsEventEntry.filter(guild_id=ctx.guild_id).order_by("event_date",
                                                                                                 "event_date")

    await ctx.respond_embed(Style.INFO,
                            "\n".join([f"📅 **{x.event_date.strftime('%d.%m')}** - {x.text}" for x in events]),
                            ctx.format("statistics_command_daily_event_list_desc_title", len(events)))


@event_group.command(description=Translatable("statistics_command_daily_event_remove_desc"))
async def remove(ctx: MrvnCommandContext):
    await ctx.defer()

    events: list[StatsEventEntry] = await StatsEventEntry.filter(guild_id=ctx.guild_id).order_by("event_date",
                                                                                                 "event_date")

    if len(events) == 0:
        await ctx.respond_embed(Style.ERROR, ctx.translate("statistics_command_daily_event_no_events"))
        return

    await ctx.respond(ctx.translate("statistics_command_daily_event_remove_choose_an_event"),
                      view=DropdownView(events, tr=ctx, author=ctx.author))
