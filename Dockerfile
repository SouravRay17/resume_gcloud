# Use the official Python image with the desired version
FROM python:3.11

# Make the port provided by the $PORT variable available to the world outside this container
EXPOSE 8080

# Set the working directory in the container
WORKDIR /app


# Copy the current directory contents into the container at /resume-analysis-app-main
COPY . ./

# Install any dependencies specified in requirements.txt
RUN pip3 install -r requirements.txt

# Define the command to run your app using Streamlit
ENTRYPOINT ["streamlit", "run", "app.py" "--server.port=8080", "--server.address=0.0.0.0"] 
