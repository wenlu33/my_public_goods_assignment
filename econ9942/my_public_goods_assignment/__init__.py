from otree.api import *


doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'my_public_goods_assignment'
    players_per_group = 2
    num_rounds = 2
    MPCR1 = 0.4
    MPCR2 = 0.6
    endowment = 100


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    MPCR = models.FloatField


class Player(BasePlayer):
    earnings = models.IntegerField()
    total_earnings = models.IntegerField()

# FUNCTIONS


# PAGES
class MyPage(Page):
    pass


class ResultsWaitPage(WaitPage):
    pass

class Results(Page):
    pass


page_sequence = [MyPage, ResultsWaitPage, Results]
