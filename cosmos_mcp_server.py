from mcp.server.fastmcp import FastMCP
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from starlette.responses import JSONResponse
import os


mcp = FastMCP("cosmos-mcp", stateless_http=True)

COSMOS_ENDPOINT = os.environ["COSMOS_ENDPOINT"]
DATABASE_NAME = os.getenv("COSMOS_DATABASE", "iso20022-db")
CONTAINER_NAME = os.getenv("COSMOS_CONTAINER", "messages")

credential = DefaultAzureCredential()
client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

@mcp.tool()
def count_messages_by_business_area(business_area: str) -> int:
    q = "SELECT VALUE COUNT(1) FROM c WHERE c.business_area = @ba"
    params = [{"name": "@ba", "value": business_area}]
    rows = list(container.query_items(
        query=q,
        parameters=params,
        enable_cross_partition_query=True
    ))
    return int(rows[0]) if rows else 0

@mcp.tool()
def list_business_areas() -> list[str]:
    q = "SELECT DISTINCT VALUE c.business_area FROM c"
    return list(container.query_items(query=q, enable_cross_partition_query=True))

@mcp.tool()
def get_messages(limit: int = 5) -> list[dict]:
    safe_limit = max(1, min(int(limit), 50))
    q = f"SELECT TOP {safe_limit} c.id, c.message_name, c.business_area FROM c"
    return list(container.query_items(query=q, enable_cross_partition_query=True))

@mcp.custom_route("/health", methods=["GET"])
async def health(_request):
    return JSONResponse({"status": "ok"})

app = mcp.http_app(path="/mcp", stateless_http=True)
