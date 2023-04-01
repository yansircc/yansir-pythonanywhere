from flask import Response
import openai
import os
import json
from transcripts_db import TranscriptsDB

openai_api_key = os.getenv("OPENAI_API_KEY")

class Golem:
    
    def __init__(self, api_key, session_id, sys_prompt="", sys_prompt_prefix="", sys_prompt_suffix="", user_input_prefix="", user_input_suffix="", max_tokens=None, temperature=0.7, memory=False):
        self.__model = "gpt-3.5-turbo"
        self.__openai_api_key = api_key
        self.__session_id = session_id
        self.__user_input_prefix = user_input_prefix
        self.__user_input_suffix = user_input_suffix
        self.__max_tokens = max_tokens
        self.__temperature = temperature
        self.__memory = memory
        self.__init_sys_prompt = [{'role':'system', 'content':sys_prompt_prefix + sys_prompt + sys_prompt_suffix}]
        
        if self.__memory:
            host = os.getenv("DB_HOST")
            user = os.getenv("DB_USER")
            password = os.getenv("DB_PASSWORD")
            database = os.getenv("DB_NAME")
            
            self.__transcripts_db = TranscriptsDB(host, user, password, database)
            with self.__transcripts_db as db:
                db.create_table()

            with self.__transcripts_db as db:
                transcript_history = db.retrieve_transcript_history(self.__session_id)
            self.__transcript_history = transcript_history if transcript_history else self.__init_sys_prompt

    def __generate_response(self, user_input):
        
        self.__transcript_history += [{'role':'user', 'content':self.__user_input_prefix + user_input + self.__user_input_suffix}]
        
        openai.api_key = self.__openai_api_key
        response = openai.ChatCompletion.create(
            model=self.__model,
            messages=self.__transcript_history,
            max_tokens=self.__max_tokens,
            temperature=self.__temperature,
            stream=True
        )
        
        self.__collected_messages = []
        for chunk in response:
            chunk_message = chunk["choices"][0]["delta"]
            self.__collected_messages.append(chunk_message)

            if not chunk_message:
                yield f"data: {json.dumps({'done': True})}\n\n"
                break
            elif chunk_message.get('content'):
                yield f"data: {json.dumps({'response': chunk_message['content']})}\n\n"

        full_reply_content = ''.join([m.get('content', '') for m in self.__collected_messages])
        self.__transcript_history += [{'role':'assistant', 'content':full_reply_content}]
        with self.__transcripts_db as db:
            db.store_transcript_history(self.__session_id, self.__transcript_history)
    
    def response(self, user_input):
        return Response(self.__generate_response(user_input), content_type='text/event-stream')
