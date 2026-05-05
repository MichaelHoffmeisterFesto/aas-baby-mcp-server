# aas-baby-mcp-server
This is a sandbox MCP server in python trying out to play with AAS.

## Credits
The initial scripts were taken from https://github.com/kirillsaidov/ollama-mcp-example

Thanks for providing this nice starting point!

## Important command lines

Start Ollama with specific model

```
ollama run qwen3:4b-instruct
```

Start Server

```
python3.exe .\mcp_server.py
```

Start Client

```
python3.exe .\mcp_client.py
```

## Naming conventions of tools

According ChatGPT:

Encode the operation type explicitly

You want a small, consistent verb taxonomy. For MCP agents, these usually work best:

* fetch_ → direct retrieval by ID (deterministic)
* list_ → enumerate collections
* search_ → fuzzy or filtered lookup
* resolve_ → indirect lookup (e.g., asset → AAS)
* traverse_ → navigate hierarchical structures

