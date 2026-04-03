# Create Your First Agent  

In this chapter, we'll walk through the process of creating your very first AI agent using the **Foundry Agent Service**.  
By the end, you'll have a simple agent running locally that you can interact with in real time.  

First switch back to the Github codespace environment you created earlier. Make sure the terminal pane is still opened on the **workshop** folder.


## Login to Azure  

Before you can use the Foundry Agent Service, you need to sign in to your Azure subscription.  

Run the following command and follow the on-screen instructions. Use credentials that have access to your Microsoft Foundry resource:  

```shell
az login --use-device-code
```





### Create a `.env` File  

We'll store secrets (such as your project endpoint) in an environment file for security and flexibility.  

1. **Create a file named `.env` in the root of your project directory.**

2. **Add the following lines to the file:**

    ```env
    PROJECT_ENDPOINT="https://<your-foundry-resource>.services.ai.azure.com/api/projects/<your-project-name>"
    MODEL_DEPLOYMENT_NAME="gpt-4o"
    ```

Replace `https://<your-foundry-resource>.services.ai.azure.com/api/projects/<your-project-name>` with the actual values from your Microsoft Foundry project. 

![](/public/foundry/foundry-project-string.png)  


3. **Where to find your endpoint:**

   - Go to the **Microsoft Foundry portal**
   - Navigate to your project
   - Click on **Overview**
   - The endpoint will be displayed on the homepage of your project



### 📝 Notes

- Make sure there are **no spaces** around the `=` sign in the `.env` file.



## Create a Basic Agent  

We'll now create a basic Python script that defines and runs an agent.  

- Start by creating a new file called: **`agent.py`** in the **workshop** folder



### Add Imports to `agent.py`  

These imports bring in the Azure SDK, environment handling, and helper classes:  

```python
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
```

### Load the `.env` File  

Load environment variables into your script by adding this line to `agent.py`:  

```python
load_dotenv()
```



### Create the Project Client  

This client connects your script to the Microsoft Foundry service using the endpoint and your Azure credentials.  

```python
project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
openai_client = project_client.get_openai_client()
```



### Create the Agent  

Now, let's create the agent itself. We'll use `create_version` to create a Foundry Agent with a `PromptAgentDefinition`.  

```python
agent = project_client.agents.create_version(
    agent_name="hello-world-agent",
    definition=PromptAgentDefinition(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
    ),
)
print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")
```



### Create a Conversation  

Agents interact within conversations. A conversation is like a container that stores all messages exchanged between the user and the agent.  

```python
conversation = openai_client.conversations.create()
print(f"Created conversation (id: {conversation.id})")
```



### Chat with the Agent  

This loop lets you send messages to the agent. Type into the terminal, and the message will be sent to the agent.  

```python
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
```



## Run the Agent  

Finally, run the Python script:  

```shell
python agent.py
```

You can now chat with your agent directly in the terminal. Type `exit` or `quit` to stop the conversation.  

## Debugging 

If you get an error (the principal `*****-****-***-****-*****`) does **not have permission** to create assistants in your Microsoft Foundry project. Specifically, it's missing the **`Microsoft.CognitiveServices/accounts/AIServices/agents/write`** data action.

Here's how to fix it:

1. **Go to the Azure Portal**: [https://portal.azure.com](https://portal.azure.com)

2. **Navigate to your Microsoft Foundry resource**:
   - You can find it by searching for the name of your Foundry resource (e.g., `my-foundry-name`).

3. **Open the "Access Control (IAM)" panel**:
   - In the left-hand menu of the resource, click **Access Control (IAM)**.

4. **Click "Add role assignment"**:
   - Choose **Add → Add role assignment**
   - Select a role that includes the required data action:
     - Recommended: **Cognitive Services Contributor** or a **custom role** that includes `Microsoft.CognitiveServices/accounts/AIServices/agents/write`

5. **Assign the role to your principal**:
   - Use the Object ID or name of the principal: `******-****-***-********`
   - This might be a service principal, user, or managed identity depending on your setup.

6. **Save and confirm**:
   - Once assigned, wait a few minutes for the permission to propagate.
   - Retry the operation to create the assistant.



## Recap  

In this chapter, you have:  

- Logged in to Azure  
- Retrieved a project endpoint  
- Separated secrets from code using `.env`  
- Created a basic agent with the Foundry Agent Service  
- Started a conversation with the agent  


## Final code sample

```python 
<!--@include: ./codesamples/agent_2.py-->
```
