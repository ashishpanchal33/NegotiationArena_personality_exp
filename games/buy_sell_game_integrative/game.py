from negotiationarena.alternating_game import AlternatingGameEndsOnTag
from negotiationarena.game_objects.resource import Resources
from negotiationarena.constants import (
    REASONING_TAG,
    PLAYER_ANSWER_TAG,
    MESSAGE_TAG,
    PROPOSAL_COUNT_TAG,
    PROPOSED_TRADE_TAG,
    RESOURCES_TAG,
    GOALS_TAG,
    ACCEPTING_TAG,
    REFUSING_OR_WAIT_TAG,
    REJECTION_TAG,
AGENT_ONE,
AGENT_TWO,PROFIT_TAG
)

from negotiationarena.utils import extract_multiple_tags
from games.buy_sell_game_integrative.prompt import buy_sell_prompt
from negotiationarena.parser import ExchangeGameDefaultParser
from negotiationarena.agent_message import AgentMessage
from negotiationarena.game_objects.trade import TradeIntegrative

from negotiationarena.utils import *

class BuySellGameDefaultParser(ExchangeGameDefaultParser):
    def __init__(self):
        super().__init__()

    def instantiate_prompt(
        self,
        resources_available_in_game,
        starting_initial_resources,
        player_goal,
        maximum_number_of_proposals,
        player_social_behaviour,
    ):
        return buy_sell_prompt(
            resources_available_in_game,
            starting_initial_resources,
            player_goal,
            maximum_number_of_proposals,
            player_social_behaviour,
        )
    #player_public_info_dict
    #player_private_info_dict
    def parse(self, response):
        """
        Parse the response from the player. We are going to extract multiple lines of text from
        different tags.

        For example, we extrac <REASONING_TAG> reasoning from the model. </REASONING_TAG>

        :param response:
        :return:
        """
        (
            profit,
            goal,
            reasoning,
            answer,
            message,
            proposal_count,
            trade,
        ) = extract_multiple_tags(
            response,
            [
                PROFIT_TAG,
                GOALS_TAG,
                REASONING_TAG,
                PLAYER_ANSWER_TAG,
                MESSAGE_TAG,
                PROPOSAL_COUNT_TAG,
                PROPOSED_TRADE_TAG,
            ],
        )
        #try:
        #    resources = Resources.from_string(resources)
        #except Exception as e:
        #    print(e)
        #    print(resources)
        #    a()
        trade = self.parse_trade(response, PROPOSED_TRADE_TAG)

        # create the message, we are going to split between public messages and secret messages.

        ms = AgentMessage()

        for tag, content in zip(
            [MESSAGE_TAG, PLAYER_ANSWER_TAG, PROPOSED_TRADE_TAG],
            [message, answer, trade],
        ):
            ms.add_public(tag, content)


        for tag, content in zip(
            [#RESOURCES_TAG, 
             PROFIT_TAG,GOALS_TAG, REASONING_TAG, PROPOSAL_COUNT_TAG],
            [#resources, 
             profit, goal, reasoning, proposal_count],
        ):
            ms.add_secret(tag, content)

        return ms

    def parse_proposed_trade(self, s):
        """
        :param s:
        :return:
        """
        trade = {}
        
        c = s.strip().replace("\n", " ")#.split("")
        print(c)
        parse_resources = {"delivery_time" : c[0], "discount_terms" : c[1], "financial_terms" : c[2]}
        trade[AGENT_ONE] = parse_resources
        trade[AGENT_TWO] = parse_resources

        return trade
    def parse_trade(self, response, interest_tag):
        contents = get_tag_contents(response, interest_tag).lstrip().rstrip()
        if contents == REFUSING_OR_WAIT_TAG:
            return contents
        return TradeIntegrative(self.parse_proposed_trade(contents))





class BuySellGame_integrate(AlternatingGameEndsOnTag):
    def __init__(
        self,
        player_goals,
        player_starting_resources,
        player_social_behaviour,
        player_conversation_roles,
        game_interface=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        # we compute the set of resources available in game.
        # this is done just to "inform" the agents of the resources available in the game.
        resources_support_set = {}

        self.game_development = dict(price=[],p1_val = [],p2_val =[], action=[],turn=[], expected_profit =[])

        #if len(player_starting_resources[0].resource_dict) > 1:
        #    raise ValueError(
        #        "Only one resource is supported due to rendering in the prompt. Update the prompt to support more resources"
        #    )

        for resource in player_starting_resources[0].resource_dict:
            resources_support_set[resource] = 0

        resources_support_set = Resources(resources_support_set)

        self.game_state = [
            {
                "current_iteration": "START",
                "turn": "None",
                "settings": dict(
                    resources_support_set=resources_support_set,
                    player_goals=player_goals,
                    player_initial_resources=player_starting_resources,
                    player_social_behaviour=player_social_behaviour,
                    player_roles=player_conversation_roles,
                    player_valuation=[g.get_valuation() for g in player_goals],
                ),
            }
        ]

        # we are going to set all the parameter we might need later
        self.resources_support_set = resources_support_set
        self.player_goals = player_goals
        self.player_starting_resources = player_starting_resources
        self.player_social_behaviour = player_social_behaviour
        self.player_conversation_roles = player_conversation_roles

        self.game_interface = (
            BuySellGameDefaultParser()
            if game_interface is None
            else game_interface
        )

        # init players
        self.init_players()

    def init_players(self):
        settings = self.game_state[0]["settings"]
        for idx, player in enumerate(self.players):
            game_prompt = self.game_interface.instantiate_prompt(
                resources_available_in_game=settings[
                    "resources_support_set"
                ].only_keys(),
                starting_initial_resources=settings[
                    "player_initial_resources"
                ][idx],
                player_goal=settings["player_goals"][idx],
                maximum_number_of_proposals=self.iterations // 2 - 1,
                player_social_behaviour=settings["player_social_behaviour"][
                    idx
                ],
            )

            player.init_agent(game_prompt, settings["player_roles"][idx])
    def write_game_state(
        self,
        players,
        response,
    ):
        try:
            agent_message = self.game_interface.parse(response)
        except Exception as e:
            print("response : {}".format(response))
            raise e

        datum = dict(
            current_iteration=self.current_iteration,
            turn=self.turn,
            player_public_answer_string=agent_message.message_to_other_player(),
            player_public_info_dict=agent_message.public,
            player_private_info_dict=agent_message.secret,
            player_complete_answer=response,
            player_state=[player.get_state() for player in players],
        )
        
        print("____")
        #try:
        #print(dir(agent_message.public[PROPOSED_TRADE_TAG]))
        #    print(str(agent_message.public[PROPOSED_TRADE_TAG].resources_from_first_agent),str(agent_message.public[PROPOSED_TRADE_TAG].resources_from_second_agent))
        #except:
        #    print(agent_message.public[PROPOSED_TRADE_TAG])
        
        #print((self.player_goals[0]).json())
        #print((self.player_goals[1]).json(), RESOURCES_TAG)
        #print(dir(self.player_starting_resources[1]), self.player_starting_resources[1].value() )
        #a()

        #print(agent_message.public[PLAYER_ANSWER_TAG])

        player_valuation = self.game_state[0]["settings"][
                "player_valuation"
            ]
        
        if agent_message.public[PLAYER_ANSWER_TAG] not in [ACCEPTING_TAG, REJECTION_TAG]:
            pri = agent_message.public[PROPOSED_TRADE_TAG]
            #int(agent_message.public[PROPOSED_TRADE_TAG].resources_from_second_agent.value())/int(agent_message.public[PROPOSED_TRADE_TAG].resources_from_first_agent.value())
            self.game_development['p1_val'].append(player_valuation[0].value(agent_message.public[PROPOSED_TRADE_TAG].resources_from_first_agent))
            self.game_development['p2_val'].append(player_valuation[1].value(agent_message.public[PROPOSED_TRADE_TAG].resources_from_second_agent))
            

            
            
        else:
            pri = self.game_development['price'][-1]
            self.game_development['last_price'] = pri
            self.game_development['reject'] = (agent_message.public[PLAYER_ANSWER_TAG] == REJECTION_TAG)
            

        print(pri, '---')
        print('p1_val',self.game_development['p1_val'])
        print('p2_val',self.game_development['p2_val'])


        
        
        
        self.game_development['expected_profit'].append((self.turn,agent_message.secret[PROFIT_TAG]))
        self.game_development['price'].append(pri)
        self.game_development['action'].append(agent_message.public[PLAYER_ANSWER_TAG])
        self.game_development['turn'].append(self.turn)
        #if agent_message.public[PLAYER_ANSWER_TAG] in []:
        #    self.game_development['last_price']
        
        

        self.game_state.append(datum)
    def after_game_ends(self):
        """
        This method is called after the game ends. For example
        the agent has accepted.

        This method can be much simpler if you don't want to compute the outcome of the game.

        :return:
        """
        end_state = self.game_state[-1]

        # if there is only one iteration, we are going to set the game state to END
        if int(end_state["current_iteration"]) <= 1:
            datum = dict(
                current_iteration="END",
                turn="None",
            )
            self.game_state.append(datum)
        else:
            # we compute the outcome of the game

            player_response = end_state["player_public_info_dict"][
                PLAYER_ANSWER_TAG
            ]
            initial_resources = self.game_state[0]["settings"][
                "player_initial_resources"
            ]
            player_valuation = self.game_state[0]["settings"][
                "player_valuation"
            ]
            player_goals = self.game_state[0]["settings"]["player_goals"]
            proposed_trade = self.game_state[-2]["player_public_info_dict"][
                PROPOSED_TRADE_TAG
            ]

            if player_response == ACCEPTING_TAG:
                # get proposed trade
                final_resources = proposed_trade #[
                    #proposed_trade.execute_trade(res, idx)
            #        for idx, res in enumerate(initial_resources)
            #    ]
            #else:
            #    final_resources = initial_resources

            outcome = [self.game_development['p1_val'][-1], self.game_development['p2_val'][-1]]
            #outcome = [
            #    v.value(final - initial)
            #    for v, initial, final in zip(
            #        player_valuation, initial_resources, final_resources
            #    )
            #]

            datum = dict(
                current_iteration="END",
                turn="None",
                summary=dict(
                    player_goals=player_goals,
                    player_initial_resources=initial_resources,
                    proposed_trade=proposed_trade,
                    player_valuation=player_valuation,
                    final_response=player_response,  # ACCEPT / REJECT / NONE
                    #final_resources=final_resources,
                    player_outcome=outcome,
                ),
            )

            self.game_state.append(datum)
