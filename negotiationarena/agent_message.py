from abc import ABC, abstractmethod
from negotiationarena.utils import from_name_and_tag_to_message


class AgentMessage:
    """
    Structured format for agent messages.
    Should define what agents can see of each other messages.

    Note that for public messages, order in the dict is important.
    """

    def __init__(self):
        self.public = {}
        self.secret = {}

    def add_public(self, key, message):
        """

        :param key:
        :param message:
        :return:
        """

        self.public[key] = message

    def add_secret(self, key, message):
        self.secret[key] = message

    def message_to_other_player(self):
        response = []
        for key, value in self.public.items():
            #response.append(from_name_and_tag_to_message(key, value)) # original  key is the tag name and value is contect
            #however from_name_and_tag_to_message follows the signature : (name, tag), and returns f"<{tag}> {name} </{tag}>"
            # there key (the actual tag) is mapped to name and value (the actual content) is mapped to tag resulting in <{content}> {tag} </{content}> 
            # this resulting in 2x prompt size when passing the message history at each turn, resulting in high token count and cost
            #FIX: 
            response.append(from_name_and_tag_to_message(value, key)) #swap key with value now returns <{tag}> {content} </{tag}>

        r = "\n".join(response)

        return r
