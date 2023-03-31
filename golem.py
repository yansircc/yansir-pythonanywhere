import openai
import os
#import mysql.connector

openai_api_key = os.getenv("OPENAI_API_KEY")

class Golem:
    
    def __init__(self, api_key, sys_prompt="", sys_prompt_prefix="", sys_prompt_suffix="", user_input_prefix="", user_input_suffix="", max_tokens=2000, temperature=0.7, memory=False):
        self.__model = "gpt-3.5-turbo"
        self.__openai_api_key = api_key
        self.__user_input_prefix = user_input_prefix
        self.__user_input_suffix = user_input_suffix
        self.__max_tokens = max_tokens
        self.__temperature = temperature
        self.__transcript_history = []
        self.__memory = memory
        self.__init_sys_prompt = [{'role':'system', 'content':sys_prompt_prefix + sys_prompt + sys_prompt_suffix}]

    def response(self, user_input, transcript_id=1):
        # if self.__memory and transcript_id in ['数据库的key列表']:
        #     transcript_history = mysql[transcript_id]
        # else:
        self.__transcript_history += self.__init_sys_prompt
        self.__transcript_history += [{'role':'user', 'content':self.__user_input_prefix + user_input + self.__user_input_suffix}]
        openai.api_key = self.__openai_api_key
        response = openai.ChatCompletion.create(
            model=self.__model,
            messages=self.__transcript_history,
            max_tokens=self.__max_tokens,
            temperature=self.__temperature
        )
        response_string = response.choices[0].message['content']
        # if self.__memory:
        #     transcript_history += ([{'role':'assistant', 'content':response_string}])
            # 将以上值存入数据库的transcript_id键中
        return response_string
    
    def clear(self):
        pass
        return