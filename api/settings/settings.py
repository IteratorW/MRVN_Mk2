from api.settings.settings_category import SettingsCategory

categories: list[SettingsCategory] = []


def add_category(category: SettingsCategory):
    categories.append(category)

    return category
