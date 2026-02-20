import os
# What should I import to use wildcard search for files in a directory
import glob
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
# What is the import to use Azure foundry project
from azure.ai.projects import AIProjectClient

# what should I import to use Azure foundry tools like file search and web search
# What is the import to use Azure foundry model
# what is the import to use Azure foundry agent function and mcp calls?
from azure.ai.projects.models import PromptAgentDefinition, FileSearchTool, Tool, FunctionTool, MCPTool
# What is the import to use Azure foundry conversations and responses
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam

import json

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


# How do I create a function calling tool for the agent to use and how do I 
#   define the function that the tool will call?
## -- Function Calling Tool -- ##
func_tool = FunctionTool(
    name="get_pizza_quantity",
    parameters={
        "type": "object",
        "properties": {
            "people": {
                "type": "integer",
                "description": "The number of people to order pizza for",
            },
        },
        "required": ["people"],
        "additionalProperties": False,
    },
    description="Get the quantity of pizza to order based on the number of people.",
    strict=True,
)

# how do I define the function that the tool will call?
def get_pizza_quantity(people: int) -> str:
    """Calculate the number of pizzas to order based on the number of people.
        Assumes each pizza can feed 2 people.
    Args:
        people (int): The number of people to order pizza for.
    Returns:
        str: A message indicating the number of pizzas to order.
    """
    print(f"[FUNCTION CALL:get_pizza_quantity] Calculating pizza quantity for {people} people.")
    return f"For {people} you need to order {people // 2 + people % 2} pizzas."
## -- Function Calling Tool -- ##

# how do I create an MCP tool for the agent to use and what is the significance of the parameters in the MCP tool?
# Parameters Explained
# --------------------
# Parameter	Description
# server_label	A human-readable name for logs and debugging.
# server_url	The MCP server endpoint.
# require_approval	Defines whether calls require manual approval ("never" disables prompts).
## -- MCP -- ##
mcpTool = MCPTool(
    server_label="contoso-pizza-mcp",
    server_url="https://ca-pizza-mcp-sc6u2typoxngc.graypond-9d6dd29c.eastus2.azurecontainerapps.io/mcp",
    require_approval="never"
)
## -- MCP -- ##



## Define the toolset for the agent
toolset: list[Tool] = [] # How do I create a list of type Tool and initializing it to an empty list?
toolset.append(FileSearchTool(vector_store_ids=[vector_store.id]))
# what is the method to add a function calling tool to the toolset list?
# How does the agent know which function to call when the function tool is invoked?
toolset.append(func_tool)
toolset.append(mcpTool)



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
        instructions=open("./workshop/instructions.txt").read(),
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

    # Handle function calls in the response
    # how do I check if the response contains a function call and how do I execute the 
    #   function and provide the results back to the model?
    input_list: ResponseInputParam = []
    function_call_count = sum(1 for item in response.output if item.type == "function_call")
    
    for item in response.output:
        if item.type == "function_call":
            if item.name == "get_pizza_quantity":
                # Execute the function logic for get_pizza_quantity
                # how do I send arguments to a funciton using **args or **kwargs?
                pizza_quantity = get_pizza_quantity(**json.loads(item.arguments))
                # Provide function call results to the model
                input_list.append(
                    FunctionCallOutput(
                        type="function_call_output",
                        call_id=item.call_id,
                        output=json.dumps({"pizza_quantity": pizza_quantity}),
                    )
                )

    # Only send response if we handled all function calls
    if input_list and len(input_list) == function_call_count:
        # how do I send the function output back to the model and get a new 
        #   response based on the function output?
        response = openai_client.responses.create(
            previous_response_id=response.id,
            input=input_list,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )    

    # Print the agent response
    # what is the method to get the text response from the agent response object?
    print(f"Assistant: {response.output_text}")