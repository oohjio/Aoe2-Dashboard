#  Copyright (C)  2021 oohjio, https://github.com/oohjio
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License v3 as published by the Free Software Foundation.

class APIStringGenerator:
    """Basic class that can generate API Strings consistently"""

    @staticmethod
    def get_AoE2_net_link_for_profile_id(profile_id):
        return f"https://aoe2.net/#profile-{profile_id}"

    @staticmethod
    def get_API_string_for_last_match(profile_id):
        return f"https://aoe2.net/api/player/lastmatch?game=aoe2de&profile_id={profile_id}"

    @staticmethod
    def get_API_string_for_match_history(profile_id, count, start):
        return f"https://aoe2.net/api/player/matches?game=aoe2de&profile_id={profile_id}&count={count}&start={start}"

    @staticmethod
    def get_API_string_for_rating_history(leaderboard_id, profile_id, count):
        return f"https://aoe2.net/api/player/ratinghistory?game=aoe2de&leaderboard_id={str(leaderboard_id)}&profile_id={str(profile_id)}&count={str(count)}"

    @staticmethod
    def get_API_string_for_string_list(locale):
        return f"https://aoe2.net/api/strings?game=aoe2de&language={locale}"
