from flask import session
import openai

class Golem:
    
    def __init__(self, api_key, sys_prompt="", sys_prompt_prefix="", sys_prompt_suffix="", user_input_prefix="", user_input_suffix="", max_tokens=3000, temperature=0.7, memory=False):
        self.__model = "gpt-3.5-turbo"
        self.__openai_api_key = api_key
        self.__user_input_prefix = user_input_prefix
        self.__user_input_suffix = user_input_suffix
        self.__transcript_history = [{'role':'system', 'content':sys_prompt_prefix + sys_prompt + sys_prompt_suffix}]
        self.__max_tokens = max_tokens
        self.__temperature = temperature
        self.__memory = memory
        self.__init_sys_prompt = self.__transcript_history.copy()

    def response(self, user_input):
        if not self.__memory:
            self.clear()
        self.__transcript_history += [{'role':'user', 'content':self.__user_input_prefix + user_input + self.__user_input_suffix}]
        openai.api_key = self.__openai_api_key
        response = openai.ChatCompletion.create(
            model=self.__model,
            messages=self.__transcript_history,
            max_tokens=self.__max_tokens,
            temperature=self.__temperature
        )
        response_string = response.choices[0].message['content']
        self.__transcript_history += ([{'role':'assistant', 'content':response_string}])
        return response_string
    
    def clear(self):
        self.__transcript_history = self.__init_sys_prompt
        return
