FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000 5000 5001 5002 5003 5004 5005
CMD ["uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
