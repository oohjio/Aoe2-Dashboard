#  Copyright (C)  2021 oohjio, https://github.com/oohjio
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License v3 as published by the Free Software Foundation.

from PySide6.QtCore import QSettings, Signal

import keys


class SettingsHandler:

    @staticmethod
    def save_profile_id_to_settings(profile_id: int, feedback_signal: Signal):
        try:
            settings = QSettings()
        except:
            return_value = (2, True)
            feedback_signal.emit(return_value)
        else:
            settings.setValue(keys.k_profile_id_key, profile_id)
            return_value = (2, True)
            feedback_signal.emit(return_value)

    @staticmethod
    def get_saved_locale_from_settings():
        settings = QSettings()
        if settings.contains(keys.k_opt_api_locale):
            return int(settings.value(keys.k_opt_api_locale))
        else:
            return 0

    @staticmethod
    def save_player_locale_to_settings(locale: int):
        settings = QSettings()
        settings.setValue(keys.k_opt_api_locale, locale)

    @staticmethod
    def get_saved_option_for_humanized_time() -> bool:
        settings = QSettings()
        if settings.contains(keys.k_opt_humanized_time):
            checked = settings.value(keys.k_opt_humanized_time)
            if checked == "false" or checked is False:
                return False
            else:
                return True
        else:
            return True

    @staticmethod
    def set_option_humanized_time_in_settings(checked: bool):
        settings = QSettings()
        settings.setValue(keys.k_opt_humanized_time, checked)

    @staticmethod
    def get_profile_id_from_settings() -> int:
        """This is returning the profile_id saved via QSettings"""
        settings = QSettings()
        if settings.contains(keys.k_profile_id_key):
            profile_id = int(settings.value(keys.k_profile_id_key))
            return profile_id
        else:
            return 0

    @staticmethod
    def get_1v1_RM_display_option_from_settings() -> bool:
        settings = QSettings()
        if settings.contains(keys.k_1v1_RM_display_option):
            checked = settings.value(keys.k_1v1_RM_display_option)
            if checked == "false" or checked is False:
                return False
            else:
                return True
        else:
            return True

    @staticmethod
    def get_1v1_EW_display_option_from_settings() -> bool:
        settings = QSettings()
        if settings.contains(keys.k_1v1_EW_display_option):
            checked = settings.value(keys.k_1v1_EW_display_option)
            if checked == "false" or checked is False:
                return False
            else:
                return True
        else:
            return True

    @staticmethod
    def get_team_RM_display_option_from_settings() -> bool:
        settings = QSettings()
        if settings.contains(keys.k_team_RM_display_option):
            checked = settings.value(keys.k_team_RM_display_option)
            if checked == "false" or checked is False:
                return False
            else:
                return True
        else:
            return True

    @staticmethod
    def get_team_EW_display_option_from_settings() -> bool:
        settings = QSettings()
        if settings.contains(keys.k_team_EW_display_option):
            checked = settings.value(keys.k_team_EW_display_option)
            if checked == "false" or checked is False:
                return False
            else:
                return True
        else:
            return True

    @staticmethod
    def set_1v1_RM_display_option_in_settings(checked: bool):
        settings = QSettings()
        settings.setValue(keys.k_1v1_RM_display_option, checked)

    @staticmethod
    def set_1v1_EW_display_option_in_settings(checked: bool):
        settings = QSettings()
        settings.setValue(keys.k_1v1_EW_display_option, checked)

    @staticmethod
    def set_team_RM_display_option_in_settings(checked: bool):
        settings = QSettings()
        settings.setValue(keys.k_team_RM_display_option, checked)

    @staticmethod
    def set_team_EW_display_option_in_settings(checked: bool):
        settings = QSettings()
        settings.setValue(keys.k_team_EW_display_option, checked)
