import time

import pytest

from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.llms.fake import FakeListLLM

from panel.chat import ChatFeed, ChatInterface
from panel.chat.langchain import PanelCallbackHandler


@pytest.importorskip("langchain")
@pytest.mark.parametrize("instance_type", [ChatFeed, ChatInterface])
def test_panel_callback_handler(instance_type):
    def callback(contents, user, instance):
        return agent.run(contents)

    instance = instance_type(callback=callback, callback_user="Langchain")
    callback_handler = PanelCallbackHandler(instance)
    tools = load_tools(["python_repl"])
    responses = ["Action: Python REPL\nAction Input: print(2 + 2)", "Final Answer: 4"]
    llm = FakeListLLM(responses=responses, callbacks=[callback_handler])
    agent = initialize_agent(
        tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, callbacks=[callback_handler]
    )
    instance.send("2 + 2")
    time.sleep(1)
    assert len(instance.value) == 2
    assert instance.value[0].value == "Final Answer: 4"
