import datetime
import io
from collections import defaultdict

# noinspection PyPackageRequirements
import matplotlib.pyplot as plt
# noinspection PyPackageRequirements
import numpy as np
# noinspection PyPackageRequirements
from discord import File
# noinspection PyPackageRequirements
from scipy.stats import gaussian_kde

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.translation.translatable import Translatable
from extensions.statistics.commands import stats
from extensions.statistics.models import StatsChannelMessageTimestamp

PLOT_DAYS_COUNT = 30

async def get_kde(guild_id: int):
    res: list[StatsChannelMessageTimestamp] = await StatsChannelMessageTimestamp.filter(guild_id=guild_id,
                                                                                        timestamp_gte=(
                                                                                                datetime.datetime.now() - datetime.timedelta(
                                                                                            days=PLOT_DAYS_COUNT)))

    # False alarm, PyCharm can't infer type
    # noinspection PyTypeChecker
    by_channel: dict[int, list[StatsChannelMessageTimestamp]] = defaultdict(default_factory=list)

    for item in res:
        by_channel[item.channel_id].append(item)

    # False alarm again, now it thinks that key return type is the type parameter of returned list
    # noinspection PyTypeChecker,PyArgumentList
    by_channel = dict(sorted(by_channel.items(), lambda item: len(item[1]))[:5])

    event: StatsChannelMessageTimestamp
    kde_by_channel = {
        channel_id: gaussian_kde([event.timestamp.timestamp() for event in events]) for channel_id, events in by_channel
    }

    return kde_by_channel


@stats.stats_group.command(description=Translatable("statistics_command_messages_desc"), name="messages_gaussian")
async def messages_command(ctx: MrvnCommandContext):
    await ctx.defer()

    kde_by_channel = await get_kde(ctx.guild_id)

    legend_text = ctx.format("statistics_command_messages_legend", ctx.guild.name)
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.linspace(
        (datetime.datetime.now() - datetime.timedelta(days=PLOT_DAYS_COUNT)).timestamp(),
        datetime.datetime.now().timestamp(), 1000)

    for channel, kde in kde_by_channel:
        ax.plot(x, kde(x))

    plt.xticks(rotation=45)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)

    await ctx.respond(file=File(buf, filename="Chart.png"))
