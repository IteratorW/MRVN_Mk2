import logging
import re
import traceback
from typing import List

from discord.enums import SlashCommandOptionType

from api.command.args.arguments import PreparedArguments
from api.command.args.parser import ParserElement
from api.command.mrvn_message_context import MrvnMessageContext
from api.exc import ArgumentParseException


# TODO shitty regex, ask Herobrine for a better version
MENTION_PATTERN = re.compile(r"(@everyone)|(<((#)|(@&)|(@!|@))([0-9]{18})>)")


class SingleStringParserElement(ParserElement):
    option = SlashCommandOptionType.string

    @classmethod
    def parse_value(cls, ctx: MrvnMessageContext, args: PreparedArguments) -> any:
        return args.next().value


class IntegerParserElement(ParserElement):
    option = SlashCommandOptionType.integer

    @classmethod
    def parse_value(cls, ctx: MrvnMessageContext, args: PreparedArguments) -> any:
        try:
            return int(args.next().value)
        except ValueError:
            raise ArgumentParseException.with_pointer(
                "This is not an integer.", args)


class BoolParserElement(ParserElement):
    option = SlashCommandOptionType.boolean

    @classmethod
    def parse_value(cls, ctx: MrvnMessageContext, args: PreparedArguments) -> any:
        value = args.next().value.lower()

        if value in ["yes", "yeah", "true", "da", "+"]:
            return True
        elif value in ["no", "false", "nah", "net", "-"]:
            return False
        else:
            raise ArgumentParseException.with_pointer("This is not a boolean. Specify either True or False.", args)


class MentionableParserElement(ParserElement):  # TODO refactor this
    option = SlashCommandOptionType.mentionable

    @classmethod
    def parse_value(cls, ctx: MrvnMessageContext, args: PreparedArguments) -> any:
        value = args.next().value.lower()

        try:
            search = MENTION_PATTERN.search(value)

            if not search:
                raise ArgumentParseException.with_pointer("This is not a mention.", args)

            snowflake = int(search.group(7)) if value != "@everyone" else None

            if (search.group(5) and (cls.option == SlashCommandOptionType.role or cls.option == SlashCommandOptionType.mentionable)) or value == "@everyone":
                if value == "@everyone":
                    return ctx.guild.roles[0]
                else:
                    return ctx.guild.get_role(snowflake)
            elif search.group(6) and (cls.option == SlashCommandOptionType.user or cls.option == SlashCommandOptionType.mentionable):
                if ctx.guild:
                    return ctx.guild.get_member(snowflake)
                else:
                    return ctx.bot.get_user(snowflake)
            elif search.group(4) and (cls.option == SlashCommandOptionType.channel or cls.option == SlashCommandOptionType.mentionable):
                return ctx.guild.get_channel(snowflake)
            else:
                raise ArgumentParseException.with_pointer("Invalid mention.", args)
        except IndexError:
            logging.error(traceback.format_exc())

            raise ArgumentParseException.with_pointer("Can't parse this.", args)


class UserParserElement(MentionableParserElement):
    option = SlashCommandOptionType.user


class RoleParserElement(MentionableParserElement):
    option = SlashCommandOptionType.role


class ChannelParserElement(MentionableParserElement):
    option = SlashCommandOptionType.channel


class NumberParserElement(ParserElement):
    option = SlashCommandOptionType.number

    @classmethod
    def parse_value(cls, ctx: MrvnMessageContext, args: PreparedArguments) -> any:
        try:
            return float(args.next().value)
        except ValueError:
            raise ArgumentParseException.with_pointer(
                "This is not a number.", args)


parsers = {elem.option: elem for elem in [SingleStringParserElement,
                                          IntegerParserElement,
                                          BoolParserElement,
                                          MentionableParserElement,
                                          UserParserElement,
                                          RoleParserElement,
                                          ChannelParserElement,
                                          NumberParserElement] if elem.option}
