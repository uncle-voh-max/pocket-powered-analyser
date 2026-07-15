from __future__ import annotations

import asyncio

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from rich import print

from pocket_powered_analyser.graph.builder import build_graph


async def main() -> None:
    load_dotenv()

    graph = build_graph()

    result = await graph.ainvoke(
        {"messages": [HumanMessage(content="Analyse the key trends in AI agents for 2026.")]},
    )

    for msg in result["messages"]:
        print(f"[bold]{msg.type}[/bold]: {msg.content}")


if __name__ == "__main__":
    asyncio.run(main())
