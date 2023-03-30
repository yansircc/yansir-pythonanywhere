from flask import session
import openai
import os

openai_api_key = os.getenv("OPENAI_API_KEY")

class Golem:
    
    def __init__(self, api_key, sys_prompt="", sys_prompt_prefix="", sys_prompt_suffix="", user_input_prefix="", user_input_suffix="", max_tokens=3000, temperature=0.7, memory=False):
        self.__model = "gpt-3.5-turbo"
        self.__openai_api_key = api_key
        self.__user_input_prefix = user_input_prefix
        self.__user_input_suffix = user_input_suffix
        self.__max_tokens = max_tokens
        self.__temperature = temperature
        self.__memory = memory
        self.__init_sys_prompt = [{'role':'system', 'content':sys_prompt_prefix + sys_prompt + sys_prompt_suffix}]

    def response(self, user_input):
        transcript_history = session.get('transcript_history', self.__init_sys_prompt)
        if not self.__memory:
            transcript_history = self.__init_sys_prompt
        transcript_history += [{'role':'user', 'content':self.__user_input_prefix + user_input + self.__user_input_suffix}]
        openai.api_key = self.__openai_api_key
        response = openai.ChatCompletion.create(
            model=self.__model,
            messages=transcript_history,
            max_tokens=self.__max_tokens,
            temperature=self.__temperature
        )
        response_string = response.choices[0].message['content']
        transcript_history += ([{'role':'assistant', 'content':response_string}])
        session['transcript_history'] = transcript_history
        return response_string
    
    def clear(self):
        session.pop('transcript_history', None)
        return