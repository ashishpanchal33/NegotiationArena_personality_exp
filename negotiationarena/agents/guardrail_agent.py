from __future__ import annotations

import re
from typing import Optional, Callable


from negotiationarena.agents.chatgpt import ChatGPTAgent

from negotiationarena.agents.ai_agent import IndianEnglishConverterClient as ConverterAgent

from negotiationarena.guardrails import GUARD_PROMPTS
from negotiationarena.utils import extract_multiple_tags
from negotiationarena.constants import ACCEPTING_TAG ,PROPOSAL_COUNT_TAG ,RESOURCES_TAG ,GOALS_TAG ,REASONING_TAG ,PLAYER_ANSWER_TAG ,REJECTION_TAG ,PROPOSED_TRADE_TAG ,MESSAGE_TAG




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

from negotiationarena.utils import extract_multiple_tags

from negotiationarena.proficiency.Indianize import PROFICIENCY_SYSTEM_PROMPTS
from typing import Any, Dict, Optional, Literal
from dataclasses import dataclass, field
import json


import requests







class GuardAgent(ConverterAgent):
    def __init__(

        self,
        #agent_name: str,
        model="gpt-4-1106-preview",
        temperature=0.7,
        max_tokens=400,
        seed=None,
        proficiency = 'low',
        prompt_library: Optional[Dict[str, str]] = GUARD_PROMPTS,
        **kwargs
        
        ):
        super().__init__(model ,temperature ,max_tokens ,seed ,proficiency ,prompt_library ,**kwargs)

    def extract_all_tags(self,text,outgoing):

        if outgoing:
        
            (
                    resources,
                    goal,
                    reasoning,
                    answer,
                    message,
                    proposal_count,
                    trade,
                ) = extract_multiple_tags(
                    text,
                    [
                        RESOURCES_TAG,
                        GOALS_TAG,
                        REASONING_TAG,
                        PLAYER_ANSWER_TAG,
                        MESSAGE_TAG,
                        PROPOSAL_COUNT_TAG,
                        PROPOSED_TRADE_TAG,
                    ],
                )
        else:
        
            (
                    answer,
                    message,
                    trade,
                ) = extract_multiple_tags(
                    text,
                    [PLAYER_ANSWER_TAG,
                        MESSAGE_TAG,
                        PROPOSED_TRADE_TAG,
                    ],
                )
            resources      = None
            goal      = None
            reasoning      = None
            proposal_count       = None


            



        
        
        return { "resources":resources, "goal":goal, "reasoning":reasoning, "answer":answer, "message":message, "proposal_count":proposal_count, "trade":trade }

    def build_to_go_message(self, param_dict= None, new_message_text='', outgoing=True):
        if outgoing:

            
            ret_ = f"""<{PROPOSAL_COUNT_TAG}> { str(int( param_dict['proposal_count']  if param_dict['proposal_count'] else 0  )+1 ) } </{PROPOSAL_COUNT_TAG}>
                        <{RESOURCES_TAG}> {param_dict['resources']} </{RESOURCES_TAG}>
                        <{GOALS_TAG}> {param_dict['goal']} </{GOALS_TAG}>
                        <{REASONING_TAG}> {param_dict['reasoning']}  </{REASONING_TAG}>
                        <{PLAYER_ANSWER_TAG}> {param_dict['answer']} </{PLAYER_ANSWER_TAG}>
                        <{PROPOSED_TRADE_TAG}> {param_dict['trade']} </{PROPOSED_TRADE_TAG}>
                        <{MESSAGE_TAG}> {new_message_text} </{MESSAGE_TAG}>"""
        else:
            ret_ = f"""<{PLAYER_ANSWER_TAG}> {param_dict['answer']} </{PLAYER_ANSWER_TAG}>
                        <{PROPOSED_TRADE_TAG}> {param_dict['trade']} </{PROPOSED_TRADE_TAG}>
                        <{MESSAGE_TAG}> {new_message_text} </{MESSAGE_TAG}>"""
            

        return ret_
        


    def remake_message(self,text, param_dict= None, agent_function=None , outgoing =False):
        try:

            if param_dict and (agent_function):
                
                if "PROPOSAL" in param_dict['answer']:      
                    new_message_text = agent_function(param_dict)
                    print('---------------new message', new_message_text,'-------')
                    ret_ = self.build_to_go_message(param_dict,new_message_text,outgoing)
                else:
                    ret_ = text
    
            else:
                ret_ = text
                
            
            return ret_
        except Exception as e:
            print(f'[remake_message], error : {e}, message: {text}'    )
            return text        
        

    def CanonicalizationAgent(self, param_dict= None ): # this works

        try:

            price = re.search(r'\d+$', param_dict['trade']).group(0)
            
            new_message_text = f"You are offered {str(price)} ZUP for 1 X"
                    
            return new_message_text
        except Exception as e:
            print(f"[Canonicalization], error : {e}, message: {param_dict['message']}"    )
            return param_dict['message']

    
    def ObjectiveToneAgent(self,param_dict=None) -> str:

        try:
            system_prompt = self.prompt_library['ObjectiveTone']
            response = self.call_model( system_prompt,param_dict['message'])
            if len(response.output_text) == 0:
                a()
                
            return response.output_text
        except Exception as e:
            print(f"[ObjectiveToneAgent] conversion failed; falling back to original text., error : {e}, message: {param_dict['message']}")
            return param_dict['message']


    def DE_manipulative_persuasive_threatening(self,param_dict=None) -> str:

        try:
            system_prompt = self.prompt_library['DE_manipulative_persuasive_threatening']
            response = self.call_model( system_prompt,param_dict['message'])
            if len(response.output_text) == 0:
                a()
                
            return response.output_text
        except Exception as e:
            print(f"[DE_manipulative_persuasive_threatening] conversion failed; falling back to original text., error : {e}, message: {param_dict['message']}")
            return param_dict['message']

    def ToxicityFilter(self,param_dict=None) -> str:

        try:
            system_prompt = self.prompt_library['ToxicityFilter']
            response = self.call_model( system_prompt,param_dict['message'])
            if len(response.output_text) == 0:
                a()
                
            return response.output_text
        except Exception as e:
            print(f"[ToxicityFilter] conversion failed; falling back to original text., error : {e}, message: {param_dict['message']}")
            return param_dict['message']


            
    def call_model(self,system_prompt, message):

        if self.model == "gpt-5":
            return self.client.responses.create(
                model=self.model,
                store=True,                    # Enables caching for repeated context
                instructions=system_prompt,  # Send system only once
                input= message,
                max_output_tokens=self.max_tokens,
                reasoning={ "effort": "minimal" }, #{ "effort": "low" }, # this can be set ... but
                temperature=1,
                #response_format={"type": "text"},
    
            )
        else:
            return self.client.responses.create(
                model=self.model,
                store=True,                    # Enables caching for repeated context
                instructions=system_prompt,  # Send system only once
                input= message ,
                max_output_tokens=self.max_tokens,
                temperature=self.temperature,
    
            )
            
    


    def ComplianceFilter(self,param_dict= None):


        try:
            system_prompt = self.prompt_library['ComplianceFilter']
            response = self.call_model( system_prompt,param_dict['message'])
            if len(response.output_text) == 0:
                a()
                
            return response.output_text
        except Exception as e:
            print(f"[ComplianceFilter] conversion failed; falling back to original text., , error : {e}, message: {param_dict['message']}")
            return param_dict['message']



    def PrivacyFilter(self,param_dict=None) -> str:

        try:
            system_prompt = self.prompt_library['PrivacyFilter']
            response = self.call_model( system_prompt,param_dict['message'])
            if len(response.output_text) == 0:
                a()
                
            return response.output_text
        except Exception as e:
            print(f"[PrivacyFilter] conversion failed; falling back to original text., error : {e}, message: {param_dict['message']}")
            return param_dict['message']
            

    def convert(self, text:str,  what=None):



            
        if not what:
            return text


        if text:
    
            
            param_dict = self.extract_all_tags(text, (what in [ 'ObjectiveTone_outgoing', 'ComplianceFilter','PrivacyFilter']))
                    
            if what == 'Canonicalization':
                
                return self.remake_message(text, param_dict= param_dict, agent_function=self.CanonicalizationAgent, outgoing =False )
                
    
            elif what == 'ObjectiveTone_incoming':

                return self.remake_message(text, param_dict= param_dict, agent_function=self.ObjectiveToneAgent ,outgoing =False )


            elif what == 'DE_manipulative_persuasive_threatening':

                return self.remake_message(text, param_dict= param_dict, agent_function=self.DE_manipulative_persuasive_threatening ,outgoing =False )


            elif what == 'ToxicityFilter':

                return self.remake_message(text, param_dict= param_dict, agent_function=self.ToxicityFilter ,outgoing =False )
            
            elif what == 'ObjectiveTone_outgoing':


                return self.remake_message(text, param_dict= param_dict, agent_function=self.ObjectiveToneAgent,outgoing =True )

            elif what == "ComplianceFilter":

                return self.remake_message(text, param_dict= param_dict, agent_function=self.ComplianceFilter,outgoing =True )


            elif what == 'PrivacyFilter':

                return self.remake_message(text, param_dict= param_dict, agent_function=self.PrivacyFilter,outgoing =True )

            
                

                
            
        
            
            






class LLMPreprocessingAgentBase(ChatGPTAgent):
    """
    A ChatGptAgent wrapper that:
      - Tracks original conversation in self.conversation_original
      - Uses the model to transform only the inner text of <message>...</message> tags
      - Appends the transformed text to self.conversation for downstream use

    Subclasses must implement:
      - task_system_prompt(self) -> str
      - task_user_instruction(self) -> str

    Notes on persistence:
      - If your game_state persistence stores arbitrary attributes (like __dict__), conversation_original will be saved.
      - If persistence is selective, also include conversation_original in your to_dict()/from_dict() or equivalent.
    """

    def __init__(
        self,
        #agent_name: str,
        model="gpt-4-1106-preview",
        temperature=0.7,
        max_tokens=400,
        seed=None,
        gaurding: Optional[Dict[str, bool]] = {
                    'Canonicalization':False,
                    'ObjectiveTone_incoming':False,
                    'ObjectiveTone_outgoing':False,
                    'ComplianceFilter':False,
                    'DE_manipulative_persuasive_threatening':False,
                    'ToxicityFilter':False,
                    'PrivacyFilter':False
                    },

        
        **kwargs
    ):
        super().__init__(        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        seed=seed, **kwargs)


        self.converter = GuardAgent(model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        seed=seed,
                        proficiency = 'low',
                        prompt_library = GUARD_PROMPTS,
                        **kwargs)

        self.gaurding = gaurding

        self.conversation_original = []


        if sum([self.gaurding[i] for i in  ['Canonicalization','ObjectiveTone_incoming','DE_manipulative_persuasive_threatening','ToxicityFilter']]    ) >1:
            raise Exception(f"[LLMPreprocessingAgentBase] more than one ingoing guards active {self.gaurding}")
        if sum([self.gaurding[i] for i in  ['ObjectiveTone_outgoing','ComplianceFilter','PrivacyFilter'] ]   ) >1:
            raise Exception(f"[LLMPreprocessingAgentBase] more than one outgoing guards active {self.gaurding}")



    def init_agent(self, system_prompt, role):
        self.system_prompt = system_prompt
        if AGENT_ONE in self.agent_name:
            # we use the user role to tell the assistant that it has to start.

            self.update_conversation_tracking(
                self.prompt_entity_initializer, system_prompt,init=True
            )
            self.update_conversation_tracking("user", role, init=True)
        elif AGENT_TWO in self.agent_name:
            system_prompt = system_prompt + role
            self.update_conversation_tracking(
                self.prompt_entity_initializer, system_prompt, init=True
            )
        else:
            raise "No Player 1 or Player 2 in role"

    def get_transformed(self, role: str, message: str):
        transformed = message
        if role == 'user':
            
            if any([self.gaurding[i] for i in  ['Canonicalization','ObjectiveTone_incoming','DE_manipulative_persuasive_threatening','ToxicityFilter']]):
                
                if self.gaurding['Canonicalization']: # for incoming
                    transformed = self.converter.convert( message,  what='Canonicalization')
                elif self.gaurding['ObjectiveTone_incoming']: #for incoming
                    transformed = self.converter.convert( message,  what='ObjectiveTone_incoming')
                elif self.gaurding['DE_manipulative_persuasive_threatening']: #for incoming
                    transformed = self.converter.convert( message,  what='DE_manipulative_persuasive_threatening')
                elif self.gaurding['ToxicityFilter']: #for incoming
                    transformed = self.converter.convert( message,  what='ToxicityFilter')




                    

                print('\n ----------------')
                print('others transformed:', transformed)
                print('\n ----------------')

        else:
            if any([self.gaurding[i] for i in  ['ComplianceFilter','ObjectiveTone_outgoing','PrivacyFilter']] ):
                
                if self.gaurding['ComplianceFilter']: # for incoming
                    transformed = self.converter.convert( message,  what='ComplianceFilter')
                elif self.gaurding['ObjectiveTone_outgoing']: #for incoming
                    transformed = self.converter.convert( message,  what='ObjectiveTone_outgoing')
                elif self.gaurding['PrivacyFilter']: #for incoming
                    transformed = self.converter.convert( message,  what='PrivacyFilter')


        return transformed
            
            
    # ----- Public override -----
    def update_conversation_tracking(self, role: str, message: str, init=False,transformed=''):



        print('\n-------...........ROLE.....--------', role, init)

        if init:
            self.conversation_original.append({"role": role, "content": message})
            self.conversation.append({"role": role, "content": message})

        else:
            if role == 'user':
                transformed = self.get_transformed(role, message)

                self.conversation_original.append({"role": role, "content": message})
                self.conversation.append({"role": role, "content": transformed})

            else: #this is handled in chat
                if transformed:
                    pass
                else:
                    transformed = message

                self.conversation.append({"role": role, "content": transformed})
            


    def chat(self):

        if self.model[:2] == "o1":
            chat = self.client.chat.completions.create(
            model=self.model,
            messages=self.conversation,
            seed=self.seed,
            )
        elif "gpt-5" in self.model:
            chat = self.client.chat.completions.create(
            model=self.model,
            messages=self.conversation,
            temperature= 1, #self.temperature,
            #max_completion_tokens=self.max_tokens,
            seed=self.seed,
            response_format={"type": "text"},
            reasoning_effort = 'low'
            )
        else:
            chat = self.client.chat.completions.create(
            model=self.model,
            messages=self.conversation,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            seed=self.seed,
        )


        print('\n ----------------')
        print('my message:', chat.choices[0].message.content)
        print('\n ----------------')

        transformed = self.get_transformed(role = "assistant", message = chat.choices[0].message.content)

        if any([self.gaurding[i] for i in  ['ComplianceFilter','ObjectiveTone_outgoing','PrivacyFilter']] ):
            print('\n ----------------')
            print('my message transformed:', transformed)
            print('\n ----------------')
        
        self.conversation_original.append({"role": "assistant", "content": chat.choices[0].message.content})


        return transformed #chat.choices[0].message.content


        










