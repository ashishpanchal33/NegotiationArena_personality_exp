import copy
from openai import OpenAI
import os

import os
import random
from negotiationarena.agents.agents import Agent
import time
from negotiationarena.constants import AGENT_TWO, AGENT_ONE
from negotiationarena.agents.agent_behaviours import SelfCheckingAgent
from copy import deepcopy
import time 


class ChatGPTAgent(Agent):
    def __init__(
        self,
        #agent_name: str,
        model="gpt-4-1106-preview",
        temperature=0.7,
        max_tokens=400,
        seed=None,
        previous_response_id = None,
        wait = 0.3
        **kwargs
    ):
        super().__init__(**kwargs)
        self.run_epoch_time_ms = str(round(time.time() * 1000))
        self.model = model
        self.conversation = []
        self.previous_response_id = previous_response_id
        if model[:2] =="o1":
            self.prompt_entity_initializer = "assistant"
        else:
            self.prompt_entity_initializer = "system"
        self.seed = (
            int(self.run_epoch_time_ms) + random.randint(0, 2**16)
            if seed is None
            else seed
        )
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.sys_ = True
        self.wait = wait

    def init_agent(self, system_prompt, role):
        self.system_prompt = system_prompt
        if AGENT_ONE in self.agent_name:
            # we use the user role to tell the assistant that it has to start.

            self.update_conversation_tracking(
                self.prompt_entity_initializer, system_prompt
            )
            self.update_conversation_tracking("user", "start "+role)
        elif AGENT_TWO in self.agent_name:
            system_prompt = system_prompt + role
            self.update_conversation_tracking(
                self.prompt_entity_initializer, system_prompt
            )
        else:
            raise "No Player 1 or Player 2 in role"

    def __deepcopy__(self, memo):
        """
        Deepcopy is needed because we cannot pickle the llama object.
        :param memo:
        :return:
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == "client" and not isinstance(v, str):
                v = v.__class__.__name__
            setattr(result, k, deepcopy(v, memo))
        return result

    def chat(self):

        

        if self.sys_ :
            response = self.client.responses.create(
                model=self.model,
                store=True,                    # Enables caching for repeated context
                instructions=self.system_prompt,  # Send system only once
                input= self.conversation[-1]['content'] ,
                max_output_tokens=self.max_tokens,
                temperature=self.temperature,
    
            )
            self.sys_ = False # only 1 time init
        else:
            response = self.client.responses.create(
                model=self.model,
                store=True,                    # Enables caching for repeated context
                input= self.conversation[-1]['content'],
                max_output_tokens=self.max_tokens,
                temperature=self.temperature,
                previous_response_id=self.previous_response_id,
    
            )

        #print('**'*10)
        #print(len(self.conversation[-1]['content']))
        #print(self.conversation[-1]['content'])

        #print('**'*10)
        
        
        self.previous_response_id = response.id



        if len(response.output_text) == 0:
            a()
            
        if self.wait:
            time.sleep(len(response.output_text)*self.wait)
        
        return response.output_text

    def update_conversation_tracking(self, role, message):
        self.conversation.append({"role": role, 
                                  "content": message})


class SelfCheckingChatGPTAgent(ChatGPTAgent, SelfCheckingAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
