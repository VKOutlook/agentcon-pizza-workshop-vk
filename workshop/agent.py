import os
# What should I import to use wildcard search for files in a directory
import glob
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
# What is the import to use Azure foundry project
from azure.ai.projects import AIProjectClient

# what should I import to use Azure foundry tools like file search and web search
# What is the import to use Azure foundry model
from azure.ai.projects.models import PromptAgentDefinition, FileSearchTool, Tool



load_dotenv()

# How to initialize foundry project client
'''This client connects your script to the Microsoft Foundry 
service using the endpoint and your Azure credentials.'''

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# how to get the OpenAI client 
openai_client = project_client.get_openai_client()



# I have a bunch of files that I want the agent look in the files to search for information?
#   How do I make the agent search it. What are the steps?

# 1. Create a vector store that will store the files in embeddings
# 2. upload the files into the vector store
# 3. add fileSearchTool(vector store id) as a tool to the agent 

vector_store_id = "vs_02gkhuBcAbrqhvZzgkSG3qHq"  # Set to your vector store ID if you already have one

## -- FILE SEARCH -- ##

if vector_store_id:
    vector_store = openai_client.vector_stores.retrieve(vector_store_id)
    print(f"Using existing vector store (id: {vector_store.id})")
else:
    # Create vector store for file search
    vector_store = openai_client.vector_stores.create(name="ContosoPizzaStores")
    print(f"Vector store created (id: {vector_store.id})")

    # Upload file to vector store
    for file_path in glob.glob("documents/*.md"):
        file = openai_client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id, file=open(file_path, "rb")
        )
        print(f"File uploaded to vector store (id: {file.id})")
## -- FILE SEARCH -- ##

## Define the toolset for the agent
toolset: list[Tool] = [] # How do I create a list of type Tool and initializing it to an empty list?
toolset.append(FileSearchTool(vector_store_ids=[vector_store.id]))





# how to create a foundry agent
'''Create the Agent
Now, let's create the agent itself. We'll use create_version to create a 
Foundry Agent with a PromptAgentDefinition.'''

# What other options do I have other than having the 
# Instructions inline?
agent = project_client.agents.create_version(
    agent_name="hello-world-agent",
    definition=PromptAgentDefinition(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        instructions=open("instructions.txt").read(),
        tools=toolset,
      ),
)


print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")




# How are messages stored for Azure Foundry Agent
'''Create a Conversation
Agents interact within conversations. A conversation is like a container that stores 
all messages exchanged between the user and the agent.'''

conversation = openai_client.conversations.create()
print(f"Created conversation (id: {conversation.id})")



while True:
    # Get the user input
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Exiting the chat.")
        break

    # How to invoke the responses and what is the significance of the conversation
    # Get the agent response
    response = openai_client.responses.create(
        conversation=conversation.id,
        input=user_input,
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )

    # Print the agent response
    print(f"Assistant: {response.output_text}")