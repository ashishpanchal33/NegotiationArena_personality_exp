from negotiationarena.constants import *


def buy_sell_prompt(
    resources_available_in_game,
    starting_initial_resources,
    player_goal,
    maximum_number_of_proposals,
    player_social_behaviour,
):


    #Integrative Bargaining in a Competitive Market 

    #Instructions that described the exercise as a simulation of a free market
    #between buyers (retail stores) and sellers (manufacturers of refrigerators)
    #were provided to all subjects.
    #Participants were told that product quality 
    #among all manufacturers was undifferentiable and that profits (or expenses) were affected by only three factors: delivery terms, discount
    #level, and financial terms. 
    #The information packet included a profit
    #schedule showing nine levels labeled “A” through “I” for each of the
    #factors (see Tables la and b for seller and buyer profit schedules). Subjects saw only the profit schedule for their role.
    #Buyers achieve their highest profits and sellers their lowest profits at
    #the “A” levels of delivery, discount, and financing, whereas sellers
    #achieve their highest profits and buyers their lowest profits at the “1”
    #levels. In addition, {"delivery time holds the highest profit potential and financing terms holds the lowest profit potential for buyers."

    #In addition, {"delivery time holds the highest profit potential and financing terms holds the lowest profit potential for buyers." if ('buyer' in player_goal.lower()) else
    #"delivery time holds the lowest profit potential and financing terms holds the highest profit potential for sellers."

    #}

    # In contrast,
    #delivery time holds the lowest profit potential and financing terms holds
    #the highest profit potential for sellers. Although an extremely unlikely
    #possibility, if either party were able to convince the other party to accept
    #his/her optimal terms (A-A-A for buyers, I-I-I for sellers), then his/
    #her profit for the transaction would be equal to $8000. The opponent
    #would receive $0. The simple compromise solution of E-E-E yields
    #$4000 to each party. However, if the parties are able to reach the fully 
    #integrative agreement of A-E-I, then each would receive a profit of
    #$5200.



    #The market methodology used in this study responds to the limitations
    #of field research on negotiation (e.g., inaccessibility of private negotiations, the difficulties of obtaining causal data, and the difficulty in obtaining data on the same variables across transactions). The market methodology also overcomes many of the limitations accepted by most social
    #psychological laboratory studies of negotiation (e.g., one-shot negotiations, external validity, and ignoring the existence of economic markets
    #that surround the transaction). This experiment uses a rich-context simulation (Greenhalgh and Neslin, 1983) that purists of both the laboratory
    #and field research traditions may find to be less than fully satisfactory.
    #However, the market experiments may provide the best joint optimization
    #of (1) the control necessary to understand the decision processes of negotiators and (2) the reduction of the inherent limitations of laboratory
    #studies.




    #Each subject was told that he/she was either a buyer or seller in a
    #market in which they could complete as many transactions as possible in
    #a fixed (30 min) amount of time. 
    #
    #
    #For example, a buyer could potentially
    #complete as many transactions as the number of sellers in the room. Since
    #an equal number of buyers and sellers existed in each market and the
    #simulation was perfectly symmetrical, all negotiators in a particular
    #market had identical profit potential. A buyer (seller) could complete only
    #one transaction with any one seller (buyer). The logistics of the market
    #required buyers and sellers to make contact at the front of the classroom
    #and then proceed to a “bargaining area” to engage in the actual negotiation. Once an agreement was reached, a “transaction form” was completed, which identified the buyer and seller and the delivery, discount,
    #and financing terms agreed upon. In addition, the time of the transaction
    #(0 to 30 min) was recorded by the experimenters for each transaction.
    #After jointly turning in the form, the buyer and seller were free to return
    #to the front of the classroom in order to make contact for another transaction. 
    #
    #This cyclical procedure continued until the end of the 30-min
    #market session.
    #The framing manipulation. Positively framed subjects were given the
    #role-specific profit tables (la and b) previously discussed. For the negatively framed condition, these tables were converted into “expenses”
    #that the subject would incur-that would be taken away from the $8000
    #gross profit that would be received for each completed transaction. This
    #transformation can be seen for buyers and sellers in Tables Ic and d.
    #Since net profit is defined to be equal to gross profit minus expenses,
    #Tables la and b are identical objectively to Tables lc and d. For example,
    #the seller’s profit for A-E-I is $5200, the sum of $0 + $1200 + $4000
    #
    #In Table Id, this same transaction would result in expenses of
    #$2800, the sum of $1600 + $1200 + $0. When $2800 is subtracted from
    #the $8000 gross profit, the same $5200 net profit is received. Thus both
    #forms of the schedules yield the same profit results, with the only difference being that the positively framed negotiators see the terms as net
    #profits, whereas the negatively framed negotiators see the same terms as
    #expenses. In addition, all further instructions were given in terms of
    #profits for positively framed negotiators and in terms of expenses for
    #negatively framed negotiators. However, all subjects were told to maximize their total profit during the 30-min market. 
    #
    #
    #Limit setting (constraints). Limit setting was manipulated by including
    #a “confidential memo” in the information packet of subjects in the “constrained” condition. The memo was not included in the packets of those
    #in the “unconstrained” condition.’ The memo was signed by the negotiator’s supervisor. This memo stated that it was against company policy
    #to accept any transaction that did not meet minimum requirements. For
    #example, subjects in the positive frame/constrained condition read:
    #do not under any circumstances make any deals which result in total profit of less
    #than $4,600. At this limit, the transaction is detrimental to the overall financial
    #welfare of the company. If you cannot reach this goal with a particular seller, you
    #should break off negotiations since there are other firms we can deal with.
    #In the negative frame/constrained level condition, subjects read the following:
    #do not under any circumstances make any deals which result in expenses of more
    #than $3,400. At this limit . . .
    #After they had taken a short quiz to ensure that the profit and expense
    #schedules were understood, subjects were given final instructions prior
    #to negotiations. For example, positively framed sellers were told:



    if 'buy' in player_goal.goal.lower():

        prompt = f""" You are playing a game where you are buying or selling an object. There is only one object for sale/purchase.

        {AGENT_ONE},(manufacturer of object) is going to sell one object. {AGENT_TWO},(as a retail store) buys the object.

        Your profits are affected by only three factors, which you negotiate over: 
            1. delivery time 
            2. discount terms
            3. financial terms

        Each factor has nine levels labeled “A” through “I”. Each level is associated with profit in {MONEY_TOKEN} currency. You achieve the highest profits at the “A” levels of delivery, discount, and financing, lowest profits at the “I” levels.

        Profit Schedule (confidential) : 
        ```
            - Level, 'delivery time', (profit in {MONEY_TOKEN})
            A,	60-days,	0
            B,	55-days,	200
            C,	50-days,	400
            D,	45-days,	600
            E,	40-days,	800
            F,	35-days,	1000
            G,	30-days,	1200
            H,	25-days,	1400
            I,	20-days,	1600

            - Level, 'discount terms % from seller', (profit in {MONEY_TOKEN})
            A,	0,	0
            B,	1,	300
            C,	2,	600
            D,	3,	900
            E,	4,	1200
            F,	5,	1500
            G,	6,	1800
            H,	7,	2100
            I,	8,	2400

            - Level, 'financial terms', (profit in {MONEY_TOKEN})
            A,	'Cash',	0
            B,	'2-payments',	500
            C,	'3-payments',	1000
            D,	'4-payments',	1500
            E,	'5-payments',	2000
            F,	'6-payments',	2500
            G,	'7-payments',	3000
            H,	'8-payments',	3500
            I,	'9-payments',	4000

        ```

        Talk to seller and make a deal which specify all three factors. That is you should propose three-letter deals in your negotiations ___ (without space).

            example 1. AAA: 
                - profit for deal : (delivery time = A, discount terms = A, financial terms = A) = 0 + 0 + 0 = 0 {MONEY_TOKEN}
            example 2. III: 
                - profit for deal : (delivery time = I, discount terms = I, financial terms = I) = 1600 + 2400 + 4000 = 8000 {MONEY_TOKEN}

        Assume that market conditions are such that seller's firm can produce all the refrigerators that can be sold.


        RULES:

        ```
        1. You must always respond with:

            A) Propose a trade with (Three-letter sequence, each letter from A to I, for `delivery time`,`discount terms`,`discount terms` respectively):
            <{PLAYER_ANSWER_TAG}> PROPOSAL </{PLAYER_ANSWER_TAG}>
            <{PROPOSED_TRADE_TAG}> `three-letter trade sequence`, i.e for `delivery time`,`discount terms`,`discount terms` respectively (do not include any other info here) </{PROPOSED_TRADE_TAG}>

            B) Accept the trade by saying:
            <{PLAYER_ANSWER_TAG}> {ACCEPTING_TAG} </{PLAYER_ANSWER_TAG}>
            <{PROPOSED_TRADE_TAG}> NONE </{PROPOSED_TRADE_TAG}>

            C) Reject and end the game:
            <{PLAYER_ANSWER_TAG}> {REJECTION_TAG} </{PLAYER_ANSWER_TAG}>
            <{PROPOSED_TRADE_TAG}> NONE </{PROPOSED_TRADE_TAG}>

            Note: The game will end if one of the players {ACCEPTING_TAG} OR {REJECTION_TAG}. This means that you have to be careful about both accepting, rejecting and proposing a trade.

        2. You are allowed at most {maximum_number_of_proposals} proposals of your own to complete the game, after which you can only reply with {ACCEPTING_TAG} or {REJECTION_TAG}.
        DO NOT propose a new trade after {maximum_number_of_proposals} proposals. Your limit for proposals is {maximum_number_of_proposals}.

        3. You can reason step by step on why you are A) proposing, B) rejecting and C) accepting a trade with:

        <{REASONING_TAG}> [add reasoning] </{REASONING_TAG}> add as much text as you want

        This information will not be sent to the other player. It is just for you to keep track of your reasoning.

        4.Calculate your total profit based on your new proposal from the profit schedule: 
        
        <{PROFIT_TAG}> delivery time profit at level _ : __ | discount terms profit at level _: __ | financial terms profit at level _: __ | total profit:__  </{PROFIT_TAG}> (add only integer number without decimal or comma for profits and level letter for levels)
        
        This information will not be sent to the other player. It is just for you to keep track of your reasoning.
        
        5. At each turn send messages to each other by using the following format:

        <{MESSAGE_TAG}>your message here (also mention three-letter trade sequence)</{MESSAGE_TAG}>

        You can decide if you want disclose your resources, goals, cost and willingness to pay in the message. However, you may not disclose details about your profit schedule, as they are confidential.
        ```

        Here is what you have access to:
        ```
        Issues that is being negotiated: {resources_available_in_game}
        <{GOALS_TAG}> {player_goal} </{GOALS_TAG}>,
        ```

        All the responses you send should contain the following and in this order:

        ```
        <{PROPOSAL_COUNT_TAG}> [add here (inclusive of current)] </{PROPOSAL_COUNT_TAG}>
        <{GOALS_TAG}> [add here] </{GOALS_TAG}>
        <{REASONING_TAG}> [add here] </{REASONING_TAG}>
        <{PLAYER_ANSWER_TAG}> [add here] </{PLAYER_ANSWER_TAG}>
        <{PROPOSED_TRADE_TAG}> [add here] </{PROPOSED_TRADE_TAG}>
        <{PROFIT_TAG}> [add here] </{PROFIT_TAG}>
        <{MESSAGE_TAG}> [add here] </{MESSAGE_TAG}>
        ```

        Please be sure to include all.

        {player_social_behaviour}
        """
    else:

        prompt = f""" You are playing a game where you are buying or selling an object. There is only one object for sale/purchase.

        {AGENT_ONE},(manufacturer of object) is going to sell one object. {AGENT_TWO},(as a retail store) buys the object.

        Your profits are affected by only three factors, which you negotiate over: 
            1. delivery time 
            2. discount terms
            3. financial terms

        Each factor has nine levels labeled “A” through “I”. Each level is associated with profit in {MONEY_TOKEN} currency. You achieve the lowest profits at the “A” levels of delivery, discount, and financing, higest profits at the “I” levels.

        Profit schedule (confidential) : 
        ```
            - Level, 'delivery time', (profit in {MONEY_TOKEN})
            A,	60-days,	4000
            B,	55-days,	3500
            C,	50-days,	3000
            D,	45-days,	2500
            E,	40-days,	2000
            F,	35-days,	1500
            G,	30-days,	1000
            H,	25-days,	500
            I,	20-days,	0

            - Level, 'discount terms % from seller', (profit in {MONEY_TOKEN})
            A,	0,	2400
            B,	1,	2100
            C,	2,	1800
            D,	3,	1500
            E,	4,	1200
            F,	5,	900
            G,	6,	600
            H,	7,	300
            I,	8,	0

            - Level, 'financial terms', (profit in {MONEY_TOKEN})
            A,	'Cash',	1600
            B,	'2-payments',	1400
            C,	'3-payments',	1200
            D,	'4-payments',	1000
            E,	'5-payments',	800
            F,	'6-payments',	600
            G,	'7-payments',	400
            H,	'8-payments',	200
            I,	'9-payments',	0

        ```

        Talk to buyer and make a deal which specify all three factors. That is you should propose three-letter deals in your negotiations _ _ _.

            example 1. AAA: (delivery time = A, discount terms = A, financial terms = A) = 4000 + 2400 + 1600 = 8000 {MONEY_TOKEN}
            example 2. III: (delivery time = I, discount terms = I, financial terms = I) = 0 + 0 + 0 = 0 {MONEY_TOKEN}

        Assume that market conditions are such that your firm can produce all the refrigerators that you can sell.


        RULES:

        ```
        1. You must always respond with:

            A) Propose a trade with (Three-letter sequence, each letter from A to I, for `delivery time`,`discount terms`,`discount terms` respectively):
            <{PLAYER_ANSWER_TAG}> PROPOSAL </{PLAYER_ANSWER_TAG}>
            <{PROPOSED_TRADE_TAG}> `three-letter trade sequence`, i.e for `delivery time`,`discount terms`,`discount terms` respectively (do not include any other info here) </{PROPOSED_TRADE_TAG}>

            B) Accept the trade by saying:
            <{PLAYER_ANSWER_TAG}> {ACCEPTING_TAG} </{PLAYER_ANSWER_TAG}>
            <{PROPOSED_TRADE_TAG}> NONE </{PROPOSED_TRADE_TAG}>

            C) Reject and end the game:
            <{PLAYER_ANSWER_TAG}> {REJECTION_TAG} </{PLAYER_ANSWER_TAG}>
            <{PROPOSED_TRADE_TAG}> NONE </{PROPOSED_TRADE_TAG}>

            Note: The game will end if one of the players {ACCEPTING_TAG} OR {REJECTION_TAG}. This means that you have to be careful about both accepting, rejecting and proposing a trade.

        2. You are allowed at most {maximum_number_of_proposals} proposals of your own to complete the game, after which you can only reply with {ACCEPTING_TAG} or {REJECTION_TAG}.
        DO NOT propose a new trade after {maximum_number_of_proposals} proposals. Your limit for proposals is {maximum_number_of_proposals}.

        3. You can reason step by step on why you are A) proposing, B) rejecting and C) accepting a trade with:

        <{REASONING_TAG}> [add reasoning] </{REASONING_TAG}> add as much text as you want

        This information will not be sent to the other player. It is just for you to keep track of your reasoning.
        
        4.Calculate your total profit based on your new proposal from the profit schedule:
        
        <{PROFIT_TAG}> delivery time profit at level _ : __ | discount terms profit at level _: __ | financial terms profit at level _: __ | total profit:__  </{PROFIT_TAG}> (add only integer number without decimal or comma for profits and level letter for levels)
        
        This information will not be sent to the other player. It is just for you to keep track of your reasoning.
        
        5. At each turn send messages to each other by using the following format:

        <{MESSAGE_TAG}>your message here (also mention three-letter trade sequence)</{MESSAGE_TAG}>

        You can decide if you want disclose your resources, goals, cost and willingness to pay in the message. However, you may not disclose details about your profit schedule, as they are confidential.
        ```

        Here is what you have access to:
        ```
         Issues that is being negotiated: {resources_available_in_game} 
        <{GOALS_TAG}> {player_goal} </{GOALS_TAG}>,
        ```

        All the responses you send should contain the following and in this order:

        ```
        <{PROPOSAL_COUNT_TAG}> [add here (inclusive of current)] </{PROPOSAL_COUNT_TAG}>
        <{GOALS_TAG}> [add here] </{GOALS_TAG}>
        <{REASONING_TAG}> [add here] </{REASONING_TAG}>
        <{PLAYER_ANSWER_TAG}> [add here] </{PLAYER_ANSWER_TAG}>
        <{PROPOSED_TRADE_TAG}> [add here] </{PROPOSED_TRADE_TAG}>
        <{PROFIT_TAG}> [add here] </{PROFIT_TAG}>
        <{MESSAGE_TAG}> [add here] </{MESSAGE_TAG}>
        ```

        Please be sure to include all.

        {player_social_behaviour}
        """
    
    
    return prompt