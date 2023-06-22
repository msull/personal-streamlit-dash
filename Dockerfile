# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container to /app
WORKDIR /app

# Add a system user to run our application so it doesn't run as root
RUN useradd -m myuser
# Copy the requirements file into the container at /app
COPY --chown=myuser:myuser requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY --chown=myuser:myuser shared-src /app/lib
COPY --chown=myuser:myuser src/ /app

RUN mkdir /app/data
RUN chown myuser:myuser /app/data

# Switch to the new user
USER myuser
EXPOSE 8501
#HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENV PYTHONPATH=/app/lib
ENTRYPOINT ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
