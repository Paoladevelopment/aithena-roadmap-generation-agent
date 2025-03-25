import json
from langchain_core.messages import ToolMessage

class BasicToolNode:
    """A node that runs the tools requested in the last AI message."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}
        print("[ToolNode] Tools registered:", list(self.tools_by_name.keys()))

    def __call__(self, inputs: dict):
        print("[ToolNode] Inputs received:", inputs)

        if messages := inputs.get("messages", []):
            message = messages[-1]
            print("[ToolNode] Last message:", message)
        else:
            raise ValueError("No message found in input")

        outputs = []
        for tool_call in getattr(message, "tool_calls", []):
            tool_name = tool_call["name"]
            print(f"[ToolNode] Invoking tool: {tool_name} with args: {tool_call['args']}")

            try:
                tool_result = self.tools_by_name[tool_name].invoke(tool_call["args"])
                # Aseguramos que es serializable
                tool_content = json.dumps(tool_result)
            except Exception as e:
                print(f"[ToolNode] Error in tool '{tool_name}': {e}")
                tool_content = json.dumps({"error": str(e)})

            outputs.append(
                ToolMessage(
                    content=tool_content,
                    name=tool_name,
                    tool_call_id=tool_call["id"],
                )
            )

        print("[ToolNode] Tool outputs:", outputs)
        return {"messages": outputs}

