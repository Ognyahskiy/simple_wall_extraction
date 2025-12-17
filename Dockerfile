FROM python:3.10.13
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENTRYPOINT ["python", "plan.py"]

