from typing import Any

from inspect_ai._util.error import exception_message
from inspect_ai._util.registry import (
    registry_info,
)
from inspect_ai.model import (
    ChatMessageTool,
    GenerateConfig,
    Model,
    ToolCall,
    ToolFunction,
    ToolInfo,
)
from inspect_ai.solver import TaskState, Tool
from inspect_ai.solver._tool.tool import TOOL_PARAMS
from inspect_ai.solver._tool.tool_def import ToolDef, tool_defs

from .util import has_max_messages


async def task_generate(
    model: Model,
    state: TaskState,
    config: GenerateConfig,
    max_messages: int | None,
) -> TaskState:
    # track tool_choice (revert to "none" after first forced call of a tool)
    tool_choice = state.tool_choice

    while True:
        # call the model
        output = await model.generate(
            state.messages,
            tools_info(state.tools),
            tool_choice,
            config,
        )

        # append the assistant message
        message = output.choices[0].message
        state.messages.append(message)

        # check for max messages
        if has_max_messages(state, max_messages):
            state.output = output
            return state

        # resolve tool calls if necessary
        tdefs = tool_defs(state.tools)
        if message.tool_calls and len(message.tool_calls) > 0:
            for tool_call in message.tool_calls:
                tool_error: str | None = None
                try:
                    result = await call_tool(tdefs, tool_call, state.metadata)
                except Exception as ex:
                    result = ""
                    tool_error = str(ex)

                if isinstance(result, tuple):
                    result, metadata = result
                    state.metadata.update(metadata)

                state.messages.append(
                    ChatMessageTool(
                        content=result if isinstance(result, list) else str(result),
                        tool_error=tool_error,
                        tool_call_id=tool_call.id,
                    )
                )

                # check for max messages
                if has_max_messages(state, max_messages):
                    state.output = output
                    return state

                # if a tool_call was forced set tool_choice to 'none'
                # (otherwise it will get forced over and over again)
                if isinstance(tool_choice, ToolFunction):
                    tool_choice = "none"

        # no tool calls, we are done!
        else:
            state.output = output
            return state


def tools_info(tools: list[Tool]) -> list[ToolInfo]:
    tdefs = tool_defs(tools)
    return [
        ToolInfo(name=tool.name, description=tool.description, params=tool.params)
        for tool in tdefs
    ]


async def call_tool(
    tools: list[ToolDef], call: ToolCall, metadata: dict[str, Any]
) -> Any:
    # if there was an error parsing the ToolCall, raise that
    if call.parse_error:
        raise ValueError(call.parse_error)

    # find the tool
    tool_def = next((tool for tool in tools if tool.name == call.function), None)
    if tool_def is None:
        return f"Tool {call.function} not found"

    # resolve metadata params and prepend to arguments
    tool_params: dict[str, str] = registry_info(tool_def.tool).metadata.get(
        TOOL_PARAMS, {}
    )
    resolved_params: dict[str, Any] = {}
    for name, value in tool_params.items():
        key = value.removeprefix("metadata.")
        resolved = metadata.get(key, None)
        if resolved is None:
            raise ValueError(f"Metadata value '{key}' not found for tool parameter")
        resolved_params[name] = resolved
    arguments = resolved_params | call.arguments

    # call the tool
    try:
        return await tool_def.tool(**arguments)
    except Exception as e:
        return f"Error: {exception_message(e)}"
