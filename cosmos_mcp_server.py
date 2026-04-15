from mcp.server.fastmcp import FastMCP
from azure.cosmos import CosmosClient
import os

mcp = FastMCP("cosmos-mcp", stateless_http=True)

COSMOS_ENDPOINT = os.environ["COSMOS_ENDPOINT"]
COSMOS_KEY = os.environ["COSMOS_KEY"]
DATABASE_NAME = os.getenv("COSMOS_DATABASE", "iso20022-db")
CONTAINER_NAME = os.getenv("COSMOS_CONTAINER", "messages")

client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

@mcp.tool()
def count_messages_by_business_area(business_area: str) -> int:
    """Count ISO 20022 messages in a business area."""
    q = "SELECT VALUE COUNT(1) FROM c WHERE c.business_area = @ba"
    params = [{"name": "@ba", "value": business_area}]
    rows = list(container.query_items(
        query=q,
        parameters=params,
        enable_cross_partition_query=True
    ))
    return rows[0] if rows else 0

@mcp.tool()
def list_business_areas() -> list[str]:
    """List business areas in the ISO 20022 knowledge base."""
    q = "SELECT DISTINCT VALUE c.business_area FROM c"
    return list(container.query_items(query=q, enable_cross_partition_query=True))

@mcp.tool()
def get_messages(limit: int = 5) -> list[dict]:
    """Return sample message records."""
    q = f"SELECT TOP {int(limit)} c.id, c.message_name, c.business_area FROM c"
    return list(container.query_items(query=q, enable_cross_partition_query=True))

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=80)
