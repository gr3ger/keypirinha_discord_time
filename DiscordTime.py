import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import arrow

import keypirinha as kp
import keypirinha_util as kpu
import keypirinha_net as kpnet
import re



class DiscordTime(kp.Plugin):
    DEFAULT_ITEM_LABEL = 'DiscordTime:'
    DEFAULT_KEYWORD = "dtime"
    ITEMCAT_VAR = kp.ItemCategory.USER_BASE + 1
    ITEMCAT_ERR = kp.ItemCategory.USER_BASE + 2
    TIME_ONLY_PATTERN = re.compile(r"^(\d{2}):(\d{2})$")
    DATE_AND_TIME_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})[ T](\d{2}):(\d{2})(:\d{2})?([Z]|[+-]\d{2}:\d{2})?$")

    def __init__(self):
        super().__init__()

    def on_start(self):
        pass

    def on_activated(self):
        pass

    def on_deactivated(self):
        pass

    def on_events(self, flags):
        pass

    def on_catalog(self):
        self.set_catalog([
            self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label=self.DEFAULT_ITEM_LABEL,
                short_desc="Generate discord timestamp",
                target=self.DEFAULT_KEYWORD,
                args_hint=kp.ItemArgsHint.REQUIRED,
                hit_hint=kp.ItemHitHint.KEEPALL)])

    def on_suggest(self, user_input, items_chain):
        if not user_input:
            return

        stripped_input = user_input.strip()

        if not items_chain or len(items_chain) == 0:
            return

        if items_chain[0].category() != kp.ItemCategory.KEYWORD or items_chain[0].target() != self.DEFAULT_KEYWORD:
            return

        result_datetime = arrow.now()
        success = False
        suggestions = []

        if self.DATE_AND_TIME_PATTERN.match(stripped_input):
            # Arrow can handle this format, no need to mess with it
            try:
                result_datetime = arrow.get(stripped_input)
                success = True
            except ValueError as e:
                self.err(f"Failed to parse date and time: {e}")
                suggestions.append(self.create_item(
                    category=self.ITEMCAT_ERR,
                    label="Parse error",
                    short_desc=str(e),
                    target=str(e),
                    args_hint=kp.ItemArgsHint.FORBIDDEN,
                    hit_hint=kp.ItemHitHint.NOARGS
                ))
                success = False
        elif self.TIME_ONLY_PATTERN.match(stripped_input): # Only time, apply to current date
            time_result = self.TIME_ONLY_PATTERN.search(stripped_input)
            try:
                result_datetime = result_datetime.replace(hour=int(time_result.group(1)), minute=int(time_result.group(2)))
                success = True
            except ValueError as e:
                self.err(f"Failed to parse date and time: {e}")
                suggestions.append(self.create_item(
                    category=self.ITEMCAT_ERR,
                    label="Parse error",
                    short_desc=str(e),
                    target=str(e),
                    args_hint=kp.ItemArgsHint.FORBIDDEN,
                    hit_hint=kp.ItemHitHint.NOARGS
                ))
        else:
            suggestions.append(self.create_item(
                category=self.ITEMCAT_ERR,
                label="Invalid input",
                short_desc="Please use a date format like '2023-12-30', '13:00', or '2023-12-30 13:00'",
                target="Invalid input",
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.NOARGS
            ))

        if success:
            relative_time_desc = result_datetime.humanize()
            short_time_desc = result_datetime.format('HH:mm')
            short_date_desc = result_datetime.format('DD/MM/YY')
            long_date_desc = result_datetime.format('MMMM DD, YYYY')
            long_date_short_time_desc = long_date_desc + " at " + short_time_desc
            day_of_week_desc = result_datetime.format('dddd')
            long_date_short_time_day_of_week_desc = day_of_week_desc + ", " + long_date_short_time_desc

            unix_timestamp = int(result_datetime.timestamp())
            suggestions.append(self.create_item(
                category=self.ITEMCAT_VAR,
                label="Relative timestamp",
                short_desc=relative_time_desc,
                target=f"<t:{unix_timestamp}:R>",
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.NOARGS
            ))
            suggestions.append(self.create_item(
                category=self.ITEMCAT_VAR,
                label="Short time",
                short_desc=short_time_desc,
                target=f"<t:{unix_timestamp}:t>",
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.NOARGS
            ))
            suggestions.append(self.create_item(
                category=self.ITEMCAT_VAR,
                label="Short date",
                short_desc=short_date_desc,
                target=f"<t:{unix_timestamp}:d>",
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.NOARGS
            ))
            suggestions.append(self.create_item(
                category=self.ITEMCAT_VAR,
                label="Long date",
                short_desc=long_date_desc,
                target=f"<t:{unix_timestamp}:D>",
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.NOARGS
            ))
            suggestions.append(self.create_item(
                category=self.ITEMCAT_VAR,
                label="Long date, short time",
                short_desc=long_date_short_time_desc,
                target=f"<t:{unix_timestamp}:f>",
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.NOARGS
            ))
            suggestions.append(self.create_item(
                category=self.ITEMCAT_VAR,
                label="Long date, day of week, short time",
                short_desc= long_date_short_time_day_of_week_desc,
                target=f"<t:{unix_timestamp}:F>",
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.NOARGS
            ))

        self.set_suggestions(suggestions, kp.Match.ANY, kp.Sort.NONE)


    def on_execute(self, item, action):
        # Handle execution: copy result to clipboard or show a notification
        if item.category() == self.ITEMCAT_VAR:
            try:
                kpu.set_clipboard(item.target())
                self.info(f"Copied to clipboard: {item.target()}")
            except Exception as e:
                self.err(f"Failed to execute: {e}")

