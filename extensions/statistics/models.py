import datetime

from tortoise import Model, fields

from api.settings import settings
from api.settings.setting import GuildSetting
from api.settings.settings_category import SettingsCategory
from api.translation.translatable import Translatable


stats_category = settings.add_category(SettingsCategory("stats", Translatable("stats_settings_category_name")))


class IncrementableGuildValueModel(Model):
    guild_id = fields.IntField()
    count = fields.IntField(default=0)

    def increment(self):
        self.count += 1


class StatsCommandEntry(IncrementableGuildValueModel):
    command_name = fields.CharField(max_length=32)

    class Meta:
        unique_together = (("command_name", "guild_id"), )


class StatsUserCommandsEntry(IncrementableGuildValueModel):
    user_id = fields.IntField()

    class Meta:
        unique_together = (("user_id", "guild_id"), )


class StatsDailyGuildChannelMessages(IncrementableGuildValueModel):
    date = fields.DateField()
    channel_id = fields.IntField()

    class Meta:
        unique_together = (("date", "guild_id", "channel_id"), )

    @classmethod
    async def get_for_now(cls, guild_id: int, channel_id: int) -> "StatsDailyGuildChannelMessages":
        return await cls.get_for_datetime(datetime.datetime.now(), guild_id, channel_id)

    @classmethod
    async def get_for_datetime(cls, date: datetime.datetime, guild_id: int, channel_id: int) -> "StatsDailyGuildChannelMessages":
        return (await cls.get_or_create(date=date.date(), guild_id=guild_id, channel_id=channel_id))[0]


class SettingChannelStatsAutopostEnable(GuildSetting):
    key = "stats_autopost_enable"
    description = Translatable("stats_autopost_enable")
    category = stats_category

    value_field = fields.BooleanField(default=False)

