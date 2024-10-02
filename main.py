from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain.memory import ConversationBufferWindowMemory, FileChatMessageHistory
import os
from dotenv import load_dotenv
from langchain_together import ChatTogether
from langchain_together import Together
from basic_tools import DateTool, TimeTool, OpenWeatherTool
from langchain.chat_models.openai import ChatOpenAI
from prompts import structured_chat_prompt2


load_dotenv()


# llm = ChatTogether(
#     together_api_key=os.getenv("TOGETHER_AI_API_KEY"),
#     # model="meta-llama/Llama-Vision-Free",
#     model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
# )
llm = ChatOpenAI(model="llama3.2", streaming=True, temperature=0, base_url=os.getenv('OLLAMA_API_URL'), api_key="lm")

mind = FileChatMessageHistory(file_path="data/memory.json")
memory = ConversationBufferWindowMemory(
    chat_memory=mind,
    memory_key="chat_history",
    k=20,
    return_messages=True
)
del_memory = input("Delete Memory (y/n): ")
if del_memory and del_memory.lower() == 'y':
    mind.clear()



class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


tools = [DateTool(), TimeTool(), OpenWeatherTool()]

structured_chat_agent = create_structured_chat_agent(llm, tools, structured_chat_prompt2)
agent = AgentExecutor(agent=structured_chat_agent, tools=tools, memory=memory, verbose=True,
                      handle_parsing_errors="Check your output and make sure it conforms, use the Action/Action Input syntax, if it doesn't call a tool, output only the action_input.",
                      max_iterations=2, )


# You're being opened for the first time, greet the user properly in the style of Jarvis

def boot(message: str = "You're being opened for the first time, Always address the user as 'Sir'"):
    try:
        response = agent.invoke({"input": message, "chat_history": memory.buffer_as_messages})
        print(f"MegaMind's Response: {response}")

        while True:
            text = input("Enter your query here >>>> ")
            print(bcolors.BOLD + " " + bcolors.OKCYAN + " You: " + text)
            response = agent.invoke({"input": text, "chat_history": memory.buffer_as_messages})
            print(f"MegaMind's Response: {response}")
    except KeyboardInterrupt:
        return False
    except BaseException as e:
        boot("Your system just recovered from a crash. You encountered an error. Answer my last question, use the appropriate tools if you have to.")


if "__main__":
    boot()