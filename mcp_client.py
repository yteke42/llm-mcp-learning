import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:

    def __init__(self, server_script: str):

        self.server_script = server_script

        self.server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_script]
        )

        self.session = None
        self._stdio = None
        self._read = None
        self._write = None

    async def connect(self):

        self._stdio = stdio_client(
            self.server_params
        )

        self._read, self._write = (
            await self._stdio.__aenter__()
        )

        self.session = ClientSession(
            self._read,
            self._write
        )

        await self.session.__aenter__()

        await self.session.initialize()

    async def list_tools(self):

        result = await self.session.list_tools()

        return result.tools

    async def call_tool(
        self,
        name: str,
        arguments: dict
    ):

        return await self.session.call_tool(
            name,
            arguments
        )

    async def close(self):

        if self.session is not None:
            await self.session.__aexit__(
                None,
                None,
                None
            )

            self.session = None

        if self._stdio is not None:
            await self._stdio.__aexit__(
                None,
                None,
                None
            )

            self._stdio = None