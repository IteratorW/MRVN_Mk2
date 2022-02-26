import datetime

from tortoise import Model, fields


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


class StatsDailyGuildMessages(IncrementableGuildValueModel):
    date = fields.DateField()

    class Meta:
        unique_together = (("date", "guild_id"), )

    @classmethod
    async def get_for_now(cls, guild_id: int) -> "StatsDailyGuildMessages":
        return await cls.get_for_datetime(datetime.datetime.now(), guild_id)

    @classmethod
    async def get_for_datetime(cls, date: datetime.datetime, guild_id: int) -> "StatsDailyGuildMessages":
        return (await cls.get_or_create(date=date.date(), guild_id=guild_id))[0]
