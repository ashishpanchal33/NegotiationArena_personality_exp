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

from negotiationarena.constants import PLAYER_ANSWER_TAG , PROPOSED_TRADE_TAG, RESOURCES_TAG, ACCEPTING_TAG, MESSAGE_TAG , REJECTION_TAG

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
        client_timeout_cushion_seconds: int = 15
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

        print(self.is_agent_one )
        
        # True means: the next chat() should wait for the human (because we just submitted)
        self.expecting_human_next = False

        # Timeout coordination
        self.server_wait_timeout_seconds = server_wait_timeout_seconds
        self.client_timeout_seconds = server_wait_timeout_seconds + client_timeout_cushion_seconds


        # Track last assistant content (for convenience/logging)
        self._last_assistant_content = ""

        
        
        self.add_config =  {"player_initial_resources":   "X: 1",
                            "player_goal":"Sell resources for ZUP. You might want to maximize profit. It costed X: 40 ZUP to produce the resources"} 
        

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


    def fetch_last_message(self):

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
        if answer_ == 'PROPOSAL':
        
            price = re.search(r'\d+$', trade_).group(0)
        else:
            (answer_old, trade_old) = extract_multiple_tags(self.conversation[-1]['content'],
                                                           PLAYER_ANSWER_TAG, 
                                                           PROPOSED_TRADE_TAG
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
            "seed": self.seed,
        }

        return payload


    def get_payload(self):
        # if the human is agent two then the ai would have saved something
        if ( self.sys_ and self.agent_name == AGENT_TWO) or (not self.sys_):
            payload = self.fetch_last_message()
        else:
            payload = self.base_payload()
        self.sys_ = False
        
        return payload


    def _post_submit(self, payload: dict) -> dict:
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
            
        self.update_conversation_tracking("assistant", content)
        return content or "[No content returned by API]"





    # offer, text,
    # acceptance, # i can fetch offer from the past message
    # rejection   #i can fetch offer  from past message

    def structure_internal_message(self,json_):

        ret_ = ""
        # normal offer messages


        
        print(json_)
        
        if json_['human_move']['offer']:
            if json_['human_move']['offer']['type'] == 'offer':
                ret_ = f"""<proposal count> 1 </proposal count>
        <my resources> {self.add_config['player_initial_resources']}</my resources>
        <my goals> {self.add_config['player_goal']} </my goals>
        <reason> __human_response_ </reason>
        <player answer> PROPOSAL </player answer>
        <newly proposed trade> Player RED Gives X: 1 | Player BLUE Gives ZUP: {int(float(json_['human_move']['offer']['offer']['amount']))} </newly proposed trade>
        <message> { json_['human_move']['chat_message']['message']['content']} </message>"""
        # accept and reject messages
        elif json_['human_move']['offer']['type'] == 'offer_response':

            type_ = json_['human_move']['offer']['offer']['final_result']

            if type_ == 'appected':
                ret_ = f"""<proposal count> 1 </proposal count>
        <my resources> {self.add_config['player_initial_resources']}</my resources>
        <my goals> {self.add_config['player_goal']} </my goals>
        <reason> __human_response_ </reason>
        <player answer> {ACCEPTING_TAG} </player answer>
        <newly proposed trade> Player RED Gives X: 1 | Player BLUE Gives ZUP: {int(float(json_['human_move']['offer']['offer']['amount']))} </newly proposed trade>
        <message> { json_['human_move']['chat_message']['message']['content']} </message>"""

            elif type_== 'rejected':
                
                ret_ = f"""<proposal count> 1 </proposal count>
        <my resources> {self.add_config['player_initial_resources']} </my resources>
        <my goals> {self.add_config['player_goal']} </my goals>
        <reason> __human_response_ </reason>
        <player answer> {REJECTION_TAG} </player answer>
        <newly proposed trade> Player RED Gives X: 1 | Player BLUE Gives ZUP: {int(float(json_['human_move']['offer']['offer']['amount']))} </newly proposed trade>
        <message> { json_['human_move']['chat_message']['message']['content']} </message>"""
                        
        return ret_

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
                if not data.get("success"):
                    # Server says it's not our turn; fallback to wait
                    data = self._post_wait(payload)
                    # After waiting, next turn should be our submit
                    self.expecting_human_next = False
                else:
                    # We submitted; next time expect human to speak
                    self.expecting_human_next = True
            else:
                # Agent two must wait first
                print(2)
                data = self._post_wait(payload)
                # After we waited (human spoke), we should submit next
                self.expecting_human_next = False
            self.first_turn_done = True

            print('data---'*5)
            print(data)
            
            return self._consume_content(data)

        
        # Subsequent turns:
        if self.expecting_human_next:
            data = self._post_wait(payload)
            # After we waited, it's our turn to submit next
            self.expecting_human_next = False
        else:
            data = self._post_submit(payload)
            if not data.get("success") and data.get("reason") == "not_turn":
                # Server disagrees; we should wait now
                data = self._post_wait(payload)
                # After waiting, we submit next
                self.expecting_human_next = False
            else:
                # We successfully submitted; next we should wait for human
                self.expecting_human_next = True

        return self._consume_content(data)






















