# Setup environment
FROM python:3.10-slim

# Developer configuration settings
ENV ENV "PROD"
ENV VERSION "v0.1.0"
ENV DEBUG False

# Web-app configuration settings
ENV NAME "assemblit"
ENV HOME_PAGE_NAME "app"
ENV GITHUB_REPOSITORY_URL "https://github.com/thomaseleff/assemblit"
ENV GITHUB_BRANCH_NAME "v0.1.0"

# Streamlit configuration settings
ENV CLIENT_PORT 8501
ENV PORT ${CLIENT_PORT}

# Orchestration server configuration settings
ENV SERVER_TYPE "prefect"
ENV SERVER_PORT 4200
ENV SERVER_JOB_NAME ""
ENV SERVER_JOB_ENTRYPOINT ""
ENV SERVER_DEPLOYMENT_NAME ""

# Database configuration settings
ENV DIR "/$NAME"

# Authentication settings
ENV REQUIRE_AUTHENTICATION False

# Users db settings
ENV USERS_DB_NAME "users"
ENV USERS_DB_QUERY_INDEX "user_id"

# Sessions db settings
ENV SESSIONS_DB_NAME "sessions"
ENV SESSIONS_DB_QUERY_INDEX "session_id"

# Data db settings
ENV DATA_DB_NAME "data"
ENV DATA_DB_QUERY_INDEX "dataset_id"

# Analysis db settings
ENV ANALYSIS_DB_NAME "analysis"
ENV ANALYSIS_DB_QUERY_INDEX "run_id"

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
RUN git clone --branch ${GITHUB_BRANCH_NAME} "${GITHUB_REPOSITORY_URL}.git" .

# Install Python requirements
RUN pip3 install -r requirements.txt --no-cache-dir

# Expose the network port(s)
EXPOSE $CLIENT_PORT
# EXPOSE $SERVER_PORT

# Run
CMD streamlit run ${HOME_PAGE_NAME}.py --server.port=${CLIENT_PORT} --server.headless=true
