import datetime

from tortoise import Model, fields

from api.settings import settings
from api.settings.setting import GuildSetting
from api.settings.settings_category import SettingsCategory
from api.translation.translatable import Translatable


stats_category = settings.add_category(SettingsCategory("stats", Translatable("stats_settings_category_name")))


class IncrementableGuildValueModel(Model):
    guild_id = fields.BigIntField()
    count = fields.IntField(default=0)

    def increment(self):
        self.count += 1


class StatsCommandEntry(IncrementableGuildValueModel):
    command_name = fields.CharField(max_length=32)

    class Meta:
        unique_together = (("command_name", "guild_id"), )


class StatsUserCommandsEntry(IncrementableGuildValueModel):
    user_id = fields.BigIntField()

    class Meta:
        unique_together = (("user_id", "guild_id"), )


class StatsChannelMessageTimestamp(Model):
    guild_id = fields.BigIntField()
    channel_id = fields.BigIntField()
    user_id = fields.BigIntField(default=-1)
    text = fields.TextField(default="")
    embeds = fields.JSONField(default=[])

    timestamp = fields.DatetimeField(index=True)


class StatsEventEntry(Model):
    guild_id = fields.BigIntField()
    event_date = fields.DateField()
    text = fields.TextField()


class SettingChannelStatsAutopostEnable(GuildSetting):
    key = "stats_autopost_enable"
    description = Translatable("stats_autopost_enable")
    category = stats_category

    value_field = fields.BooleanField(default=False)

