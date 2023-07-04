import tiktoken


class Counter:

    def __init__(self, encoding_name: str = "cl100k_base", model: str = "gpt-3.5-turbo-0301", max_tokens: int = 4096):
        self.__encoding_name = encoding_name
        self.__model = model
        self.__max_tokens = max_tokens

    def num_tokens_from_string(self, string: str) -> int:
        encoding = tiktoken.get_encoding(self.__encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens
    
    def num_tokens_from_messages(self, messages) -> int:
        try:
            encoding = tiktoken.encoding_for_model(self.__model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if self.__model == "gpt-3.5-turbo":
            print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
            return self.num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
        elif self.__model == "gpt-4":
            print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-3.5-turbo.")
            return self.num_tokens_from_messages(messages, model="gpt-3.5-turbo")
        elif self.__model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif self.__model == "gpt-3.5-turbo":
            tokens_per_message = 3
            tokens_per_name = 1
        else:
            raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {self.__model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens
