FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY cosmos_mcp_server.py .

EXPOSE 80

CMD ["uvicorn", "cosmos_mcp_server:app", "--host", "0.0.0.0", "--port", "80"]
