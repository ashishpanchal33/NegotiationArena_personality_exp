import copy
from openai import OpenAI
import os
import re
import os
import random
from negotiationarena.agents.agents import Agent
import time
from negotiationarena.constants import AGENT_TWO, AGENT_ONE
from negotiationarena.agents.agent_behaviours import SelfCheckingAgent
from copy import deepcopy

from negotiationarena.constants import ACCEPTING_TAG ,PROPOSAL_COUNT_TAG ,RESOURCES_TAG ,GOALS_TAG ,REASONING_TAG ,PLAYER_ANSWER_TAG ,REJECTION_TAG ,PROPOSED_TRADE_TAG ,MESSAGE_TAG

from negotiationarena.utils import extract_multiple_tags


import requests


class AIProxyClientAgent(Agent):
    """
    Drop-in replacement for ChatGPTAgent that proxies conversation turns
    to your Django app's API (views_proxy.py). It adheres to the same
    surface API used by NegotiationArena:
      - init_agent(system_prompt, role)
      - chat() -> str
      - update_conversation_tracking(role, message)

    How it works (suggested flow):
      - The game sets up the conversation via init_agent and update_conversation_tracking.
      - When chat() is called, this agent POSTS its current conversation to your
        Django API. Your API decides whether this should:
          * block/wait for the human's turn (if it is not our turn), or
          * persist/broadcast an AI message/offer and then wait for the human response.
      - The API returns the next text content to speak; we return that to the game.

    You can wire two endpoints:
      - wait_endpoint: blocks until a human message/offer is available for this session
      - submit_endpoint: persists an AI turn (message/offer/etc.) and returns the human response

    Your views_proxy.py should map these appropriately.
    """

    def __init__(
        self,
        agent_name: str,
        session_id: str,
        participant_id: str,
        submit_endpoint: str = "submit_ai_move",
        wait_endpoint: str = "wait_for_human",
        api_base_url: str = "http://172.16.68.4:8081/api/ai_proxy/",
        temperature: float = 0.7,
        max_tokens: int = 400,
        seed: int = None,
        role: str = "buyer",
        server_wait_timeout_seconds: int = 60,
        client_timeout_cushion_seconds: int = 15,
        wait = 0.2
    ):
        super().__init__(agent_name)
        self.session_id = session_id
        self.participant_id = participant_id
        self.api_base_url = api_base_url.rstrip("/")
        self.submit_url = f"{self.api_base_url}/{session_id}/{submit_endpoint}/"
        self.wait_url = f"{self.api_base_url}/{session_id}/{wait_endpoint}/"

        self.run_epoch_time_ms = str(round(time.time() * 1000))
        self.conversation = []
        self.prompt_entity_initializer = "system"
        self.seed = int(self.run_epoch_time_ms) + random.randint(0, 2**16) if seed is None else seed
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.role = role
        self.sys_ = True  # not first_turn_done
        self.first_turn_done = False
        self.is_agent_one = (AGENT_ONE in self.agent_name)
        self.wait = wait


        print(self.is_agent_one )
        
        # True means: the next chat() should wait for the human (because we just submitted)
        self.expecting_human_next = False

        # Timeout coordination
        self.server_wait_timeout_seconds = server_wait_timeout_seconds
        self.client_timeout_seconds = server_wait_timeout_seconds + client_timeout_cushion_seconds


        # Track last assistant content (for convenience/logging)
        self._last_assistant_content = ""

        self._last_reponse = {}


        if role =='seller':
            self.add_config =  {"player_initial_resources":   "X: 1",
                            "player_goal":"Sell resources for ZUP. You might want to maximize profit. It costed X: 40 ZUP to produce the resources"} 
        else:
            self.add_config =  {"player_initial_resources":   "ZUP: 60",
                            "player_goal":"Buy resources with ZUP. You might want to maximize profit. You think you can resell the product at X: 60 ZUP for the resources."}            


    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def init_agent(self, system_prompt, role):
        if AGENT_ONE in self.agent_name:
            # Player 1: system + user to indicate it starts
            self.update_conversation_tracking(self.prompt_entity_initializer, system_prompt)
            
            # so the ws connection is done in the negotiation web app ... we dont have to do anything here
            # basically we are saying that this guy is AI 
            #self.update_conversation_tracking("user",  "start "+role)
        elif AGENT_TWO in self.agent_name:
            # Player 2: system prompt includes role suffix
            system_prompt = system_prompt + role
            self.update_conversation_tracking(self.prompt_entity_initializer, system_prompt)
        else:
            raise ValueError("Agent name must include AGENT_ONE or AGENT_TWO")

    def update_conversation_tracking(self, role, message):
        self.conversation.append({"role": role, "content": message})
    
    def base_payload(self):
        
        payload = {
                "session_id": self.session_id,
                "participant_id": self.participant_id,
                "agent_name": self.agent_name,
                "role" : self.role,
                "role_display" : self.role,
                # Optional knobs your API may use:
                "type": 'offer', # this will not be read
                "message": " ", # this will not be read
                "amount" : 40, # this will not be read
                "seed": self.seed,
            }
        return payload


    def fetch_last_message(self,message_=None):


        if message_:
            pass
        else:
            message_ = self.conversation[-1]['content']

        if type(message_) == str:
                (
                    answer_,
                    message_to_pass,
                    trade_,
                ) = extract_multiple_tags(
                    message_,
                    [
                
                        PLAYER_ANSWER_TAG,
                        MESSAGE_TAG,
                        PROPOSED_TRADE_TAG,
                    ],
                )


        print("answer_:", answer_, "message_to_pass:", message_to_pass, "trade_:", trade_)
        if answer_ == 'PROPOSAL':
        
            price = re.search(r'\d+$', trade_).group(0)
        else:
            (answer_old, trade_old) = extract_multiple_tags(self.conversation[-1]['content'],
                                                           [PLAYER_ANSWER_TAG, 
                                                           PROPOSED_TRADE_TAG]
                                                           )
            
            price = re.search(r'\d+$', trade_old).group(0)
        
        payload = {
            "session_id": self.session_id,
            "participant_id": self.participant_id,
            "agent_name": self.agent_name,
            "role" : self.role,
            "role_display" : self.role,
            # Optional knobs your API may use:
            "type": ( 'offer' if answer_=='PROPOSAL' else ('reject' if answer_ == REJECTION_TAG else 'accept')),
            "message": message_to_pass,
            "amount" : price,
            "seed": self.seed,}


        
        
        if answer_ == REJECTION_TAG:

            print('last_offer_id---------',self._last_reponse )
            
            payload = payload | {"rejected_offer_id":self._last_reponse , "no_wait": True}

        elif answer_ == ACCEPTING_TAG:

            print('last_offer_id---------',self._last_reponse )
    
            payload = payload | {"accepted_offer_id":self._last_reponse , "no_wait": True}


        
        return payload


    def get_payload(self,message_=None):
        # if the human is agent two then the ai would have saved something
        if ( self.sys_ and self.agent_name == AGENT_TWO) or (not self.sys_):
            payload = self.fetch_last_message(message_)
        else:
            payload = self.base_payload()
        self.sys_ = False
        
        return payload


    def _post_submit(self, payload: dict, return_code=False) -> dict:
        # After submit, we expect the next thing to be a human response
        try:
            resp = requests.post(self.submit_url, json=payload, timeout=self.client_timeout_seconds)
            resp.raise_for_status()  # i have to think about this... 
            return resp.json()
        except Exception as e:

            return {"success": False, "error": f"submit error: {e}"}

    def _post_wait(self, payload: dict) -> dict:
        # NOTE: We intentionally set the client timeout a little larger than the server's wait
        # so that the server decides if/when to time out the wait.
        try:
            wait_resp = requests.post(self.wait_url, json=payload, timeout=self.client_timeout_seconds)
            wait_resp.raise_for_status()  # i have to think about this... 
            return wait_resp.json()
        except Exception as e:
            return {"success": False, "error": f"wait error: {e}"}



    def _wait_until_response(self, payload: dict, max_minutes: float | None = None, retry_base_delay: float = 1.0) -> dict:
        """
        Indefinite (or capped) long-poll loop: keeps calling wait until we get a success with a human_move.
        Returns the first successful response. Logs and retries on timeouts/transient errors.
        If max_minutes is None, loops forever.
        """
        start = time.monotonic()
        attempt = 0
        while True:
            data = self._post_wait(payload)
            # Success and human_move present -> return
            if data.get("success") and data.get("human_move"):
                return data
            # If server returns success True but no human_move (shouldn't happen), keep looping
            # If timeout/error, also keep looping
            attempt += 1

            #{'success': False, 'human_move': None, 'timeout': True, 'next_poll_seconds': 2}
            # Optional cap
            if max_minutes is not None:
                if (time.monotonic() - start) >= max_minutes * 60:
                    return data  # return whatever we have (caller should handle gracefully)
            # Backoff a bit before next poll to avoid tight loop
            time.sleep(min(retry_base_delay + attempt * 0.25, 3.0))






            

    def _consume_content(self, data: dict) -> str:
        # Standardize the returned content field
        content = self.structure_internal_message(data)
        # Track as assistant output for the game’s transcript
        if content:
            self._last_assistant_content = content

            # i need a function that actually converts the json into a message text

            # graceful fallback
        else:
            content = "[No content returned by API]"

        print('---content----',content)
            
        self.update_conversation_tracking("assistant", content)

        return content





    # offer, text,
    # acceptance, # i can fetch offer from the past message
    # rejection   #i can fetch offer  from past message

    def structure_internal_message(self,json_):

        

        ret_ = ""
        # normal offer messages


        print('here------') 
        print(json_)



       
        hm = json_.get('human_move') or {}
        # Handle explicit final (e.g., session_ended) early to end the game
        if hm.get('final'):
            # Map session end to a terminal rejection to let the game stop


            if hm.get('final').get("type") == 'session_ended':

    
    
                print('rejected------')   

                






                
                ret_ = f"""<{PROPOSAL_COUNT_TAG}> 1 </{PROPOSAL_COUNT_TAG}>
                        <{RESOURCES_TAG}> {self.add_config['player_initial_resources']} </{RESOURCES_TAG}>
                        <{GOALS_TAG}> {self.add_config['player_goal']} </{GOALS_TAG}>
                        <{REASONING_TAG}> session ended  </{REASONING_TAG}>
                        <{PLAYER_ANSWER_TAG}> {REJECTION_TAG} </{PLAYER_ANSWER_TAG}>
                        <{PROPOSED_TRADE_TAG}> NONE</{PROPOSED_TRADE_TAG}>
                        <{MESSAGE_TAG}> session_ended </{MESSAGE_TAG}>"""


                #print(ret_)
                return ret_




        try:
            
            if json_['human_move']['offer']:
                print('here------1')
                if json_['human_move']['offer']['type'] == 'offer':
                    print('here------1_1')
                    self._last_reponse = json_['human_move']['offer']['offer']['id']
                    
                    ret_ = f"""<{PROPOSAL_COUNT_TAG}> 1 </{PROPOSAL_COUNT_TAG}>
                    <{RESOURCES_TAG}> {self.add_config['player_initial_resources']}</{RESOURCES_TAG}>
                    <{GOALS_TAG}> {self.add_config['player_goal']} </{GOALS_TAG}>
                    <{REASONING_TAG}> __human_response_ </{REASONING_TAG}>
                    <{PLAYER_ANSWER_TAG}> PROPOSAL </{PLAYER_ANSWER_TAG}>
                    <{PROPOSED_TRADE_TAG}> Player RED Gives X: 1 | Player BLUE Gives ZUP: {int(float(json_['human_move']['offer']['offer']['amount']))} </{PROPOSED_TRADE_TAG}>
                    <{MESSAGE_TAG}> { json_['human_move']['chat_message']['message']['content']} </{MESSAGE_TAG}>"""
                # accept and reject messages
                elif json_['human_move']['offer']['type'] == 'offer_response':
    
                    #print('here------2')
        
                    type_ = json_['human_move']['offer']['final_result']
    
                    print('here------2', type_)
        
                    if type_ == 'accepted':
    

                        if not json_['human_move']['chat_message']:
                            chat_m ='Deal'
                        else:
                            chat_m = json_['human_move']['chat_message']['message']['content']
                            

                        
                        ret_ = f"""<{PROPOSAL_COUNT_TAG}> 1 </{PROPOSAL_COUNT_TAG}>
                        <{RESOURCES_TAG}> {self.add_config['player_initial_resources']}</{RESOURCES_TAG}>
                        <{GOALS_TAG}> {self.add_config['player_goal']} </{GOALS_TAG}>
                        <{REASONING_TAG}> __human_response_ </{REASONING_TAG}>
                        <{PLAYER_ANSWER_TAG}> {ACCEPTING_TAG} </{PLAYER_ANSWER_TAG}>
                        <{PROPOSED_TRADE_TAG}> NONE</{PROPOSED_TRADE_TAG}>
                        <{MESSAGE_TAG}> { chat_m} </{MESSAGE_TAG}>"""
                
                    elif type_== 'rejected':

                        
                        if not json_['human_move']['chat_message']:
                            chat_m ='No Deal'
                        else:
                            chat_m = json_['human_move']['chat_message']['message']['content']
                            
                        
                        ret_ = f"""<{PROPOSAL_COUNT_TAG}> 1 </{PROPOSAL_COUNT_TAG}>
                        <{RESOURCES_TAG}> {self.add_config['player_initial_resources']} </{RESOURCES_TAG}>
                        <{GOALS_TAG}> {self.add_config['player_goal']} </{GOALS_TAG}>
                        <{REASONING_TAG}> __human_response_ </{REASONING_TAG}>
                        <{PLAYER_ANSWER_TAG}> {REJECTION_TAG} </{PLAYER_ANSWER_TAG}>
                        <{PROPOSED_TRADE_TAG}> NONE </{PROPOSED_TRADE_TAG}>
                        <{MESSAGE_TAG}> { json_['human_move']['chat_message']['message']['content']} </{MESSAGE_TAG}>"""
                        
                print(f'ret_ {ret_}')

            #print(f'ret_ {type_}')#, no offer { (json_['human_move']['offer'] != None) }')
                
            return ret_
        except Exception as e:
            print('There was an exception',e,json_)


    
    def chat(self) -> str:
        """
        Called by the game loop to get this agent's next utterance.
        We send our full current conversation context to your API.

        Your server is responsible for:
          - Determining if it's this agent's turn -> persist + broadcast + wait for opponent
          - Or if it's the opponent's turn -> simply wait until human/opponent responds
          - Returning the next "content" text that this agent should emit in the game

        Expected server response JSON (example):
          { "success": true, "content": "proposed price is 42 with rationale ..." }
        """


        """
        Implements first-turn policy plus post-first-turn alternation:
          - First call:
              * agent_one -> submit
              * agent_two -> wait
          - Thereafter:
              * if expecting_human_next: wait
              * else: submit
        """

        # only when AI was the previous player and has spoken something
        payload = self.get_payload()
        
        # Strategy:
        # - If last speaker is this agent, then we've just spoken; the server should wait for the human
        # - Else it's our turn; the server should persist our move and then wait for human response
        # You can implement this routing server-side. Here we just POST to submit_url,
        # and your API can decide whether to block/wait or to process-and-wait based on turn state.

        #the logic has to change a bit.... 

        content = self.handle_conversation(payload)
        
        return content


    def handle_conversation(self,payload):

        
        if not self.first_turn_done: # if this guy is the agent one then we will just listen
            
            if not self.is_agent_one: 
                print(1)
                data = self._post_submit(payload)
                if (not data.get("success")) or data.get("next_poll_seconds") :
                    # Server says it's not our turn; fallback to wait
                    #data = self._post_wait(payload)
                    data = self._wait_until_response(payload)
                    # After waiting, next turn should be our submit
                    self.expecting_human_next = False
                else:
                    # We submitted; next time expect human to speak
                    self.expecting_human_next = True

                    
            else:
                # Agent two must wait first
                print(2)
                data = self._wait_until_response(payload)
                #data = self._post_wait(payload)
                # After we waited (human spoke), we should submit next
                self.expecting_human_next = False
            self.first_turn_done = True

            print('data---'*5)            
            print(data)

            ret__ = self._consume_content(data)

            if self.wait:
                print('message_length', len(ret__.split('<message>')[-1][:-11]))
                time.sleep(len(ret__.split('<message>')[-1][:-11])*self.wait)
                
                
            return ret__

        
        # Subsequent turns:
        if 0: #self.expecting_human_next:
            print(3)
            data = self._wait_until_response(payload)
            data = self._post_wait(payload)
            # After we waited, it's our turn to submit next
            self.expecting_human_next = False
        else:

            print(4)
            data = self._post_submit(payload)
            print('data',data)
            if ((not data.get("success") ) or data.get("next_poll_seconds")):# and data.get("reason") == "not_turn" :
                # Server disagrees; we should wait now
                data = self._wait_until_response(payload)
                #data = self._post_wait(payload)
                # After waiting, we submit next
                self.expecting_human_next = False
            else:
                # We successfully submitted; next we should wait for human
                self.expecting_human_next = True


        ret__ = self._consume_content(data)
                    
        if self.wait:
            print('message_length', len(ret__.split('<message>')[-1][:-11]))
            time.sleep(len(ret__.split('<message>')[-1][:-11])*self.wait)

        return ret__






















