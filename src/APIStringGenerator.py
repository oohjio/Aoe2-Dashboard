class APIStringGenerator:
    """Basic class that can generate API Strings consistently"""

    @staticmethod
    def get_AoE2_net_link_for_player_id(player_id):
        return "https://aoe2.net/#profile-" + str(player_id)

    @staticmethod
    def get_API_string_for_last_match(player_id):
        return "https://aoe2.net/api/player/lastmatch?game=aoe2de&profile_id=" + str(player_id)

    @staticmethod
    def get_API_string_for_rating_history(leaderboard_id, player_id, count):
        return "https://aoe2.net/api/player/ratinghistory?game=aoe2de&leaderboard_id={0}&profile_id={1}&count={2}" \
            .format(str(leaderboard_id), str(player_id), str(count))

    @staticmethod
    def get_API_string_for_string_list(locale):
        return "https://aoe2.net/api/strings?game=aoe2de&language={}".format(locale)