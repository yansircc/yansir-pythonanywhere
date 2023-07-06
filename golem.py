from flask import Response
import openai
import os
import json
from transcripts_db import TranscriptsDB
from count_tokens import Counter

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_4_api_key = os.getenv("GPT4_API_KEY")
api_base = os.getenv("API_BASE")

class Golem:

    def __init__(self, api_key, session_id, sys_prompt="", sys_prompt_prefix="", sys_prompt_suffix="", user_input_prefix="", user_input_suffix="", max_tokens=None, temperature=0.7, memory=False, is_stream=True, table_name="", column_name="", api_base=None):
        self.__model = "gpt-4" if api_base else "gpt-3.5-turbo"
        self.__openai_api_key = api_key
        self.__session_id = session_id
        self.__user_input_prefix = user_input_prefix
        self.__user_input_suffix = user_input_suffix
        self.__max_tokens = max_tokens
        self.__temperature = temperature
        self.__memory = memory
        self.__api_base = api_base
        self.__init_sys_prompt = [
            {'role': 'system', 'content': sys_prompt_prefix + sys_prompt + sys_prompt_suffix}]
        self.__is_stream = is_stream
        self.__table_name = table_name
        self.__column_name = column_name

        if self.__memory:
            self.__transcripts_db = TranscriptsDB()
            with self.__transcripts_db as db:
                db.create_table(self.__table_name, self.__column_name)
                transcript_history = db.retrieve_data(
                    self.__table_name, self.__session_id, self.__column_name)
            self.__transcript_history = transcript_history if transcript_history else self.__init_sys_prompt
        else:
            self.__transcript_history = self.__init_sys_prompt

    def response(self, user_input, callback=None, no_stop=False):
        
        token_counter = Counter()
        if isinstance(user_input, list):
            self.__transcript_history = user_input
            # 循环统计token数量，如果大于4096，则删除最早一条消息，直到token数量小于4096
            while token_counter.num_tokens_from_messages(self.__transcript_history) > 4096:
                if len(self.__transcript_history) == 1:
                    yield f"data: {json.dumps({'exceed': True})}\n\n"
                self.__transcript_history = self.__transcript_history[2:]
        else:
            # 统计token数量，如果大于4096，则返回exceed事件
            if token_counter.num_tokens_from_string(user_input) > 4096:
                yield f"data: {json.dumps({'exceed': True})}\n\n"
            self.__transcript_history += [{'role': 'user',
                                           'content': self.__user_input_prefix + user_input + self.__user_input_suffix}]
        print("API base", self.__api_base)
        print("API key", self.__openai_api_key)
        openai.api_key = self.__openai_api_key
        if self.__api_base:
            openai.api_base = self.__api_base
        response = openai.ChatCompletion.create(
            model=self.__model,
            messages=self.__transcript_history,
            max_tokens=self.__max_tokens,
            temperature=self.__temperature,
            stream=self.__is_stream,
        )

        if self.__is_stream:
            self.__collected_messages = []
            self.__full_reply_content = ""
            for chunk in response:
                chunk_message = chunk["choices"][0]["delta"]
                self.__collected_messages.append(chunk_message)

                if not chunk_message:
                    if not chunk_message:
                        print(no_stop)
                        if no_stop:
                            yield f"data: {json.dumps({'keyword_done': True})}\n\n"
                        else:
                            yield f"data: {json.dumps({'done': True})}\n\n"
                    self.__full_reply_content = ''.join(
                        [m.get('content', '') for m in self.__collected_messages])
                    self.__transcript_history += [{'role': 'assistant',
                                                   'content': self.__full_reply_content}]
                    if self.__memory:
                        with self.__transcripts_db as db:
                            db.store_data(self.__table_name, self.__session_id,
                                          self.__column_name, self.__transcript_history)
                    if callback:
                        callback(self.__full_reply_content)
                    break
                elif chunk_message.get('content'):
                    yield f"data: {json.dumps({'response': chunk_message['content']})}\n\n"

        else:
            golem_response = response['choices'][0]['message']['content']
            self.__transcript_history += [{'role': 'assistant',
                                           'content': golem_response}]
            if self.__memory:
                with self.__transcripts_db as db:
                    db.store_data(self.__table_name, self.__session_id,
                                  self.__column_name, self.__transcript_history)
            if callback:
                callback(golem_response)
            yield golem_response

    def update_sys_prompt(self, sys_prompt):
            self.__init_sys_prompt = [{'role': 'system', 'content': sys_prompt}]