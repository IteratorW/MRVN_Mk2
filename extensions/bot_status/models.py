from tortoise import Model, fields


class BotStatusEntry(Model):
    text = fields.CharField(max_length=50)
    status = fields.CharField(max_length=10)
    activity = fields.CharField(max_length=15)
