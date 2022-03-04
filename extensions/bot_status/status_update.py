import asyncio
import time

from discord import Status, Activity, ActivityType

from api.event_handler.decorators import event_handler
from extensions.bot_status.models import BotStatusEntry
from impl import runtime

task = None


def get_uptime():
    uptime = time.time() - runtime.start_time

    days = round(uptime // 86400)
    hours = round((uptime - days * 86400) // 3600)
    minutes = round((uptime - days * 86400 - hours * 3600) // 60)

    formatted = ":".join([str(x) for x in [days, hours, minutes]])

    return formatted


def get_activity_and_status(entry: BotStatusEntry):
    text = entry.text.replace("{uptime}", get_uptime())

    status = Status[entry.status]
    activity = Activity(type=ActivityType[entry.activity], name=text,
                        url="https://twitch.tv/dreamfinity" if entry.activity == "streaming" else None)

    return activity, status


def start_task():
    global task

    if task is not None and not task.done():
        task.cancel()

    task = asyncio.create_task(status_update_task())


async def status_update_task():
    entries = await BotStatusEntry.filter()

    if not len(entries):
        await runtime.bot.change_presence(status=Status.online)

        return

    index = 0

    while True:
        entry = entries[index]
        index = 0 if index == len(entries) - 1 else index + 1

        activity, status = get_activity_and_status(entry)

        await runtime.bot.change_presence(activity=activity, status=status)

        await asyncio.sleep(30)


@event_handler()
async def on_startup():
    start_task()
