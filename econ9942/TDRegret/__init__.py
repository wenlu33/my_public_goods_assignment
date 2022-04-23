from otree.api import *


doc = """
This is TDRegret
"""


class C(BaseConstants):
    NAME_IN_URL = 'TDRegret'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 10
    INSTRUCTIONS_TEMPLATE = 'TDRegret/instructions.html'
    # Player's reward for the lowest claim"""
    ADJUSTMENT_ABS = cu(40)
    # Player's deduction for the higher claim
    # The maximum claim to be requested
    MAX_AMOUNT = cu(200)
    # The minimum claim to be requested
    MIN_AMOUNT = cu(40)
    timeout_seconds = 60



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    lower_claim = models.CurrencyField()


class Player(BasePlayer):
    q1 = models.StringField(
        choices=[['False', 'A. $ED20'], ['False', 'B. $ED30'], ['True', 'C. $ED40'],['False', 'D. $ED50']],
        label='1. The minimum amount you can choose is:',
        widget=widgets.RadioSelect,
    )
    q2 = models.StringField(
        choices=[['False', 'A. $ED100'], ['B. $ED200', 'B. $ED200'], ['False', 'C. $ED300'],['False', 'D. $ED400']],
        label='2. The maximum amount you can choose is:',
        widget=widgets.RadioSelect,
    )
    q3 = models.StringField(
        choices=[['False', 'A. There is no penalty / reward'], ['False', 'B. $ED10'], ['False', 'C. $ED20'], ['False', 'D. $ED30'],['True', 'E. $ED40']],
        label='3. What is the penalty / reward if I choose differently than the person I matched with?',
        widget=widgets.RadioSelect,
    )
    q4 = models.StringField(
        choices=[['True', 'A. $ED M'], ['B. False', 'B. $ED (M – penalty)'], ['False', 'C. $ED (M + reward)']],
        label='4. M represent the value chosen. '
              'If I and the person matched with me both choose M, how much will I get?',
        widget=widgets.RadioSelect,
    )
    q5 = models.StringField(
        choices=[['False', 'A. $ED M'], ['False', 'B. $ED m'], ['False', 'C. $ED (M – penalty)'], ['False', 'D. $ED (M + reward)'], ['True', 'E. $ED (m - penalty)'], ['False', 'F. $ED (m + reward)']],
        label='5. M and m represent the value chosen and M is larger than m. If I choose M and the person matched with me chooses m, how much will I get?',
        widget=widgets.RadioSelect,
    )
    q6 = models.StringField(
        choices=[['False', 'A. $ED M'], ['False', 'B. $ED m'], ['False', 'C. $ED (M – penalty)'], ['False', 'D. $ED (M + reward)'], ['False', 'E. $ED (m - penalty)'], ['True', 'F. $ED (m + reward)']],
        label='6. M and m represent the value chosen and M is larger than m. If I choose m and the person matched with me chooses M, how much will I get?',
        widget=widgets.RadioSelect,
    )
    ## how to make people not move to next step unless they answer correctly?
    ## how to make instructions side by side with the assessment?
    ## if i want to pay them with number of questions they answered correctly (to motivate them to answer correctly), how should i do it?

    claim = models.CurrencyField(
        min=C.MIN_AMOUNT,
        max=C.MAX_AMOUNT,
        label='What value are you submitting for this round?',
        doc="""
        Each player's claim
        """,
    )
    guess = models.CurrencyField(
        min=C.MIN_AMOUNT,
        max=C.MAX_AMOUNT,
        label='What value do you think your match will submit?',
        doc="""
            Each player's guess
            """,
    )
    adjustment = models.CurrencyField()

class Message(ExtraModel):
    group = models.Link(Group)
    sender = models.Link(Player)
    text = models.StringField()
def to_dict(msg: Message):
    return dict(sender=msg.sender.id_in_group, text=msg.text)

# FUNCTIONS
def set_payoffs(group: Group):
    p1, p2 = group.get_players()
    if p1.claim == p2.claim:
        group.lower_claim = p1.claim
        for p in [p1, p2]:
            p.payoff = group.lower_claim
            p.adjustment = cu(0)
    else:
        if p1.claim < p2.claim:
            winner = p1
            loser = p2
        else:
            winner = p2
            loser = p1
        group.lower_claim = winner.claim
        winner.adjustment = C.ADJUSTMENT_ABS
        loser.adjustment = -C.ADJUSTMENT_ABS
        winner.payoff = group.lower_claim + winner.adjustment
        loser.payoff = group.lower_claim + loser.adjustment
    # group.potential_max_payoff = group.lower_claim - 1 + winner.adjustment
    # group.potential_optimal_claim = group.lower_claim - 1
        ## How to get this value and show it in result page???


def other_player(player: Player):
    return player.get_others_in_group()[0]

def creating_session(subsession):
    subsession.group_randomly()

# PAGES
class Introduction(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

class Assessment(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6']
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Claim(Page):
    form_model = 'player'
    form_fields = ['guess', 'claim']


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

class chat(Page):
    def get_timeout_seconds(player):
        return C.timeout_seconds  # in seconds

class aMyWaitPage(WaitPage):
    template_name = 'TDRegret/aMyWaitPage.html'


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(other_player_claim=other_player(player).claim)


page_sequence = [Introduction, Assessment, aMyWaitPage, chat, Claim, ResultsWaitPage, Results, ResultsWaitPage]
