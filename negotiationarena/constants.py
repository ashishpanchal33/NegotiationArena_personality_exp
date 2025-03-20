MONEY_TOKEN = "ZUP"

RESOURCES_TAG = "my resources"
GOALS_TAG = "my goals"
REASONING_TAG = "reason"
PLAYER_ANSWER_TAG = "player answer"
PROPOSED_TRADE_TAG = "newly proposed trade"
SPLIT_TAG = "split"
MESSAGE_TAG = "message"
VALUATION_TAG = "my valuation"
REFUSING_OR_WAIT_TAG = "NONE"
ACCEPTING_TAG = "ACCEPT"
REJECTION_TAG = "REJECT"
TURN_OR_MOVE_TAG = "move"
PROPOSAL_COUNT_TAG = "proposal count"
MY_NAME_TAG = "my name"

OTHER_PLAYER_PROPOSED_TRADE = "other player proposed trade"
OTHER_PLAYER_ANSWER = "other player answer"
OTHER_PLAYER_MESSAGE = "other player message"

AGENT_ONE = "Player RED"
AGENT_TWO = "Player BLUE"

PROFIT_TAG = "My profit"


buyer_init = {'delivery_time': 'A', 'discount_terms': 'A', 'financial_terms': 'A'}
seller_init = {'delivery_time': 'I', 'discount_terms': 'I', 'financial_terms': 'I'}

Buyer_profit_schedule = {'delivery_time': {'A': '60-days',
  'B': '55-days',
  'C': '50-days',
  'D': '45-days',
  'E': '40-days',
  'F': '35-days',
  'G': '30-days',
  'H': '25-days',
  'I': '20-days'},
 'delivery_time(Profit)': {'A': 0,
  'B': 200,
  'C': 400,
  'D': 600,
  'E': 800,
  'F': 1000,
  'G': 1200,
  'H': 1400,
  'I': 1600},
 'discount_terms': {'A': 0,
  'B': 1,
  'C': 2,
  'D': 3,
  'E': 4,
  'F': 5,
  'G': 6,
  'H': 7,
  'I': 8},
 'discount_terms(Profit)': {'A': 0,
  'B': 300,
  'C': 600,
  'D': 900,
  'E': 1200,
  'F': 1500,
  'G': 1800,
  'H': 2100,
  'I': 2400},
 'financial_terms': {'A': 'Cash',
  'B': '2-payments',
  'C': '3-payments',
  'D': '4-payments',
  'E': '5-payments',
  'F': '6-payments',
  'G': '7-payments',
  'H': '8-payments',
  'I': '9-payments'},
 'financial_terms(Profit)': {'A': 0,
  'B': 500,
  'C': 1000,
  'D': 1500,
  'E': 2000,
  'F': 2500,
  'G': 3000,
  'H': 3500,
  'I': 4000}}


Seller_profit_schedule = {'delivery_time': {'A': '60-days',
  'B': '55-days',
  'C': '50-days',
  'D': '45-days',
  'E': '40-days',
  'F': '35-days',
  'G': '30-days',
  'H': '25-days',
  'I': '20-days'},
 'delivery_time(Profit)': {'A': 4000,
  'B': 3500,
  'C': 3000,
  'D': 2500,
  'E': 2000,
  'F': 1500,
  'G': 1000,
  'H': 500,
  'I': 0},
 'discount_terms': {'A': 0,
  'B': 1,
  'C': 2,
  'D': 3,
  'E': 4,
  'F': 5,
  'G': 6,
  'H': 7,
  'I': 8},
 'discount_terms(Profit)': {'A': 2400,
  'B': 2100,
  'C': 1800,
  'D': 1500,
  'E': 1200,
  'F': 900,
  'G': 600,
  'H': 300,
  'I': 0},
 'financial_terms': {'A': 'Cash',
  'B': '2-payments',
  'C': '3-payments',
  'D': '4-payments',
  'E': '5-payments',
  'F': '6-payments',
  'G': '7-payments',
  'H': '8-payments',
  'I': '9-payments'},
 'financial_terms(Profit)': {'A': 1600,
  'B': 1400,
  'C': 1200,
  'D': 1000,
  'E': 800,
  'F': 600,
  'G': 400,
  'H': 200,
  'I': 0}}