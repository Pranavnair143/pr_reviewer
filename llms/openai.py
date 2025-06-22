from langchain_openai import ChatOpenAI


def initialize_llm(model="gpt-4o",temperature=0,json_mode=True):
    model_kwargs = {}
    if json_mode:
        model_kwargs.update({"response_format": {"type": "json_object"}})
    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        model_kwargs=model_kwargs
    )
    return llm