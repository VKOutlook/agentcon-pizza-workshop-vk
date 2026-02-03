# Integrando MCP (Model Context Protocol)

Nos capítulos anteriores, seu agente aprendeu a seguir instruções, se fundamentar em seus próprios dados usando **File Search (RAG)** e chamar **ferramentas** personalizadas.  

Neste capítulo final, vamos conectar seu agente a um **servidor MCP** ao vivo — dando a ele acesso a **capacidades externas** como menus ao vivo, coberturas e gerenciamento de pedidos através de um protocolo padrão e seguro.


## O Que É MCP e Por Que Usá-lo?

**MCP (Model Context Protocol)** é um padrão aberto para conectar agentes de IA a ferramentas externas, fontes de dados e serviços através de **servidores MCP** interoperáveis.  
Em vez de integrar com APIs individuais, você conecta uma vez a um servidor MCP e automaticamente ganha acesso a todas as ferramentas que esse servidor expõe.

### Benefícios do MCP

- 🧩 **Interoperabilidade:** uma forma universal de expor ferramentas de qualquer serviço para qualquer agente compatível com MCP.  
- 🔐 **Segurança e governança:** gerencie centralmente acesso e permissões de ferramentas.  
- ⚙️ **Escalabilidade:** adicione ou atualize ferramentas do servidor sem mudar o código do seu agente.  
- 🧠 **Simplicidade:** mantenha integrações e lógica de negócio no servidor; mantenha seu agente focado em raciocínio.


## Atualizar Seus Imports

Atualize seus imports no `agent.py` para incluir `MCPTool`:

```python
import json
import os
import glob
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, FileSearchTool, FunctionTool, MCPTool, Tool
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam
```


## O Servidor MCP da Contoso Pizza

Para a Contoso Pizza, o servidor MCP expõe APIs para:
- 🧀 **Pizzas:** itens de menu disponíveis e preços  
- 🍅 **Coberturas:** categorias, disponibilidade e detalhes  
- 📦 **Pedidos:** criar, visualizar e cancelar pedidos de clientes  

Você conectará seu agente a este servidor e dará acesso para usar as ferramentas dessas operações.


## Adicionar a Ferramenta MCP

Adicione este código após sua seção de Ferramenta de Chamada de Função e antes de criar o toolset:

```python
## -- MCP -- ##
mcpTool = MCPTool(
    server_label="contoso-pizza-mcp",
    server_url="<!--@include: ./variables/mcp-url.md-->",
    require_approval="never"
)
## -- MCP -- ##
```

### Parâmetros Explicados

| Parâmetro | Descrição |
| -- | -- |
| **server_label** | Um nome legível para logs e depuração. |
| **server_url** | O endpoint do servidor MCP. |
| **require_approval** | Define se chamadas requerem aprovação manual (`"never"` desabilita prompts). |

::: tip
💡 Em produção, use modos de aprovação mais restritivos para operações sensíveis.
::: 


## Atualizar o Toolset

Adicione a ferramenta MCP ao seu toolset:

```python
## Definir o toolset para o agente
toolset: list[Tool] = []
toolset.append(FileSearchTool(vector_store_ids=[vector_store.id]))
toolset.append(func_tool)
toolset.append(mcpTool)
```


## Adicionar um ID de Usuário

Para fazer pedidos, o agente deve identificar o cliente.

1. **Obtenha seu ID de Usuário**  
   Visite esta URL para registrar um cliente:  
   [<!--@include: ../variables/customer-registration.md-->](<!--@include: ../variables/customer-registration.md-->)  

2. **Atualize seu `instrucoes.txt`** com seus detalhes de usuário ou passe o GUID no chat.

```txt
## Detalhes do usuário:
Nome: <SEU NOME>
UserId: <SEU GUID DE USUÁRIO>
```

3. (Opcional) Visualize seu painel de pedidos:  
   [<!--@include: ../variables/pizza-dashboard.md-->](<!--@include: ../variables/pizza-dashboard.md-->)



## Experimentando

Agora é hora de testar seu agente conectado!  
Execute o agente e experimente estes prompts:

```
Mostre-me as pizzas disponíveis.
```

```
Qual é o preço de uma pizza havaiana?
```

```
Quero pedir uma pizza margherita.
```



## Resumo

Neste capítulo, você:
- Aprendeu o que é **MCP (Model Context Protocol)** e por que é útil  
- Adicionou uma **MCPTool** ao seu toolset  
- Conectou seu agente a um **servidor MCP externo**  
- Testou o agente de ponta a ponta com menus ao vivo e pedidos



## Amostra de código final

```python 
<!--@include: ../codesamples/pt/agent_6_mcp.py-->
```

*Traduzido usando GitHub Copilot.*
