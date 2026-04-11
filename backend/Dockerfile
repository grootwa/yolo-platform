# Step 1: Start with a base that already has Python and YOLO requirements
FROM ultralytics/ultralytics:latest

# Step 2: Set the "Home" folder inside the container
WORKDIR /app

# Step 3: Copy our shopping list into the container
COPY requirements.txt .

# Step 4: Tell the container to install everything on the list
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy all our code from the local 'backend' folder into the container
COPY . .

# Step 6: The command to start our backend server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]