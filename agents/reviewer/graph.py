import json
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages
from langchain_core.messages import ToolMessage
from langgraph.graph import StateGraph, START, END

from agents.reviewer.tools.review_file_changes import review_file_changes, create_fetch_file
from llms.openai import initialize_llm


class Description:
    def __init__(self, text: str):
        self.text = text

class State(TypedDict):
    messages: Annotated[list, add_messages]


class BasicToolNode:
    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")

        outputs = []
        internal_values = {}

        for tool_call in message.tool_calls:
            args = tool_call["args"]

            result = self.tools_by_name[tool_call["name"]].invoke(args)

            outputs.append(
                ToolMessage(
                    content=json.dumps(result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )

        return {
            "messages": outputs,
            "internal": internal_values
        }


def route_tools(
    state: State,
):
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END


def initialize_graph(info):
    fetch_file_changes_tool = create_fetch_file(info=info)
    tools = [review_file_changes, fetch_file_changes_tool]
    graph_builder = StateGraph(State)
    llm = initialize_llm(json_mode=False)

    llm_with_tools = llm.bind_tools(tools)

    tool_node = BasicToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)

    def chatbot(state: State):
        schema_message = f"""You are a senior developer who reviews PR file changes."""

        new_messages = [
           {"type": "system", "content": schema_message}
        ] + state["messages"]

        return {"messages": [llm_with_tools.invoke(new_messages)]}

    graph_builder.add_node("chatbot", chatbot)

    graph_builder.add_conditional_edges(
        "chatbot",
        route_tools,
        {"tools": "tools", END: END},
    )

    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    graph = graph_builder.compile()
    return graph
