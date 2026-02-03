
# Servidor MCP de Pizza

Para este taller usamos el ejemplo de código abierto [Pizza MCP Agent](https://github.com/Azure-Samples/pizza-mcp-agents).

::: danger
Esto solo es relevante si llegas al capítulo 6 del taller.
:::

Este proyecto demuestra cómo construir agentes de IA que pueden interactuar con APIs del mundo real utilizando el Model Context Protocol (MCP). Presenta un sistema completo de pedidos de pizza con una API sin servidor, interfaces web y un servidor MCP que permite a los agentes de IA explorar menús, realizar pedidos y rastrear el estado de los pedidos.

El sistema consiste en múltiples servicios interconectados:
- **Servidor MCP de Pizza:** Servidor MCP que permite interacciones con agentes de IA
- **Aplicación web de Pizza:** Panel de pedidos en vivo, mostrando el estado de pedidos de pizza en tiempo real
- **Sistema de registro:** Registro de usuarios para acceder al sistema de pedidos de pizza

|  Nombre | Descripción |
|-----------|-------------|
| Servidor MCP de Pizza | [<!--@include: ../variables/mcp-url.md-->](<!--@include: ./variables/mcp-url.md-->)|
| Aplicación web de Pizza | [<!--@include: ../variables/pizza-dashboard.md-->](<!--@include: ./variables/pizza-dashboard.md-->)|
| Sistema de registro | [<!--@include: ../variables/customer-registration.md-->](<!--@include: ./variables/customer-registration.md-->) |


## Descripción General

Este es el servidor MCP de Pizza, que expone la API de Pizza como un servidor Model Context Protocol (MCP). El servidor MCP permite a los LLMs interactuar con el proceso de pedidos de pizza a través de herramientas MCP.

Este servidor admite los siguientes tipos de transporte:
- **HTTP transmisible**
- **SSE** (heredado, no recomendado para nuevas aplicaciones)

## Herramientas MCP

El servidor MCP de Pizza proporciona las siguientes herramientas:

| Nombre de la Herramienta | Descripción |
|-----------|-------------|
| get_pizzas | Obtener una lista de todas las pizzas en el menú |
| get_pizza_by_id | Obtener una pizza específica por su ID |
| get_toppings | Obtener una lista de todos los ingredientes en el menú |
| get_topping_by_id | Obtener un ingrediente específico por su ID |
| get_topping_categories | Obtener una lista de todas las categorías de ingredientes |
| get_orders | Obtener una lista de todos los pedidos en el sistema |
| get_order_by_id | Obtener un pedido específico por su ID |
| place_order | Realizar un nuevo pedido con pizzas (requiere `userId`) |
| delete_order_by_id | Cancelar un pedido si aún no ha comenzado (el estado debe ser `pending`, requiere `userId`) |

## Probar con MCP inspector

Primero, necesitas iniciar la API de Pizza y el servidor MCP de Pizza localmente.

1. En una ventana de terminal, inicia MCP Inspector:
    ```bash
    npx -y @modelcontextprotocol/inspector
    ```
2. Ctrl+clic para cargar la aplicación web MCP Inspector desde la URL mostrada por la aplicación (por ejemplo, http://127.0.0.1:6274)
3. En MCP Inspector, establece el tipo de transporte en **SSE** y 
3. Pon `<!--@include: ./variables/mcp-url.md-->` en el campo URL y haz clic en el botón **Connect**.
4. En la pestaña **Tools**, selecciona **List Tools**. Haz clic en una herramienta y selecciona **Run Tool**.

> [!NOTE]
> Esta aplicación también proporciona un punto final SSE si usas `/sse` en lugar de `/mcp` en el campo URL. 

*Traducido usando GitHub Copilot.*
