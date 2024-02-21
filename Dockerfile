# Setup environment
FROM python:3.10-slim

# Developer mode
ENV DEV = false

# Web-app configuration settings
ENV NAME = "getstreamy"
ENV HOME_PAGE_NAME = "Home"
ENV GITHUB_REPOSITORY_URL = ""

# Database configuration settings
ENV DIR = "/${WORKDIR}"

# Authentication settings
ENV REQUIRE_AUTHENTICATION = true

# Users db settings
ENV USERS_DB_NAME = "users"
ENV USERS_DB_QUERY_INDEX = "user_id"

# Sessions db settings
ENV SESSIONS_DB_NAME = "studies"
ENV SESSIONS_DB_QUERY_INDEX = "study_id"

# Data db settings
ENV DATA_DB_NAME = "data"
ENV DATA_DB_QUERY_INDEX = "dataset_id"

# Set the working directory (cannot be the root directory for Streamlit)
WORKDIR /${NAME}

# Update and install
RUN apt-get update
RUN apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git
RUN rm -rf /var/lib/apt/lists/*

# Clone from Github
RUN git clone "${GITHUB_REPOSITORY_URL}.git" "/${WORKDIR}"

# Install Python requirements
RUN pip3 install -r requirements.txt

# Expose the network port
ARG PORT=8501
EXPOSE ${PORT}

# Monitor the health of the container
HEALTHCHECK CMD curl --fail "http://localhost:${PORT}/_stcore/health"

# Run
ENTRYPOINT [ \
    "streamlit", \
    "run", \
    "${HOME_PAGE_NAME}.py", \
    "--server.port=${PORT}", \
    # "--server.address=0.0.0.0" \
    "--server.headless=true" \
]
