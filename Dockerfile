# syntax=docker/dockerfile:1
FROM python:3.10-slim-buster
WORKDIR /app

# Put the requirements file into the workdir
COPY requirements.txt requirements.txt
# Install module from requirements file into the image
RUN pip3 install -r requirements.txt

# Add source code to the image
COPY . .

# Command we want to run when our image is executed inside a container
ENTRYPOINT [ "streamlit", "run" , "ECHECProject_StreamlitAPI.py", "--server.port=8501", "--server.address=0.0.0.0"]

EXPOSE 8501