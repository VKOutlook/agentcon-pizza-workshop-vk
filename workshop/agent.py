import os
import glob
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, FileSearchTool, Tool

load_dotenv()


project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
openai_client = project_client.get_openai_client()

vector_store_id = ""  # Set to your vector store ID if you already have one

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
toolset: list[Tool] = []
toolset.append(FileSearchTool(vector_store_ids=[vector_store.id]))


agent = project_client.agents.create_version(
    agent_name="hello-world-agent",
    definition=PromptAgentDefinition(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        instructions=open("instructions.txt").read(),
        tools=toolset,
      ),
)
print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

conversation = openai_client.conversations.create()
print(f"Created conversation (id: {conversation.id})")

while True:
    # Get the user input
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Exiting the chat.")
        break

    # Get the agent response
    response = openai_client.responses.create(
        conversation=conversation.id,
        input=user_input,
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )

    # Print the agent response
    print(f"Assistant: {response.output_text}")