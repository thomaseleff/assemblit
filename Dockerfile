# Setup environment
FROM python:3.10-slim

# Developer configuration settings
ENV ENV PROD
ENV VERSION "v0.1.0"
ENV DEBUG false

# Web-app configuration settings
ENV NAME "getstreamy"
ENV HOME_PAGE_NAME "Home"
ENV GITHUB_REPOSITORY_URL "https://github.com/thomaseleff/Getstreamy"
ENV GITHUB_BRANCH_NAME "v0.1.0"

# Network configuration settings
ENV PORT 8501

# Database configuration settings
ENV DIR "/$NAME"

# Authentication settings
ENV REQUIRE_AUTHENTICATION true

# Users db settings
ENV USERS_DB_NAME "users"
ENV USERS_DB_QUERY_INDEX "user_id"

# Sessions db settings
ENV SESSIONS_DB_NAME "studies"
ENV SESSIONS_DB_QUERY_INDEX "study_id"

# Data db settings
ENV DATA_DB_NAME "data"
ENV DATA_DB_QUERY_INDEX "dataset_id"

# Set the working directory (cannot be the root directory for Streamlit)
WORKDIR "/$NAME"

# Update and install
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    nano \
    git --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*
RUN pip3 install --upgrade pip

# Clone from Github
RUN git clone --branch $GITHUB_BRANCH_NAME "$GITHUB_REPOSITORY_URL.git" .

# Install Python requirements
RUN pip3 install -r requirements.txt --no-cache-dir

# Expose the network port
EXPOSE $PORT

# Run
CMD streamlit run $HOME_PAGE_NAME.py --server.port=$PORT --server.headless=true
