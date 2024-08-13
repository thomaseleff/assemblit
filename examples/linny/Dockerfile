# Setup environment
FROM python:3.10-slim

# Developer configuration settings
ENV ASSEMBLIT_ENV "PROD"
ENV ASSEMBLIT_VERSION "v0.1.0"
ENV ASSEMBLIT_DEBUG False

# Web-app configuration settings
ENV ASSEMBLIT_NAME "linny"
ENV ASSEMBLIT_HOME_PAGE_NAME "Home"
ENV ASSEMBLIT_GITHUB_REPOSITORY_URL "https://github.com/thomaseleff/assemblit"
ENV ASSEMBLIT_GITHUB_BRANCH_NAME "v0.1.0"

# Streamlit configuration settings
ENV ASSEMBLIT_CLIENT_PORT 8501

# Orchestration server configuration settings
ENV ASSEMBLIT_SERVER_TYPE "prefect"
ENV ASSEMBLIT_SERVER_JOB_NAME "linear-regression-flow"
ENV ASSEMBLIT_SERVER_JOB_ENTRYPOINT "/examples/${ASSEMBLIT_NAME}/flow.py"
ENV ASSEMBLIT_SERVER_DEPLOYMENT_NAME "v0_1_0"
ENV ASSEMBLIT_SERVER_PORT 4200

# Database configuration settings
ENV ASSEMBLIT_DIR "/examples/${ASSEMBLIT_NAME}"

# Authentication settings
ENV ASSEMBLIT_REQUIRE_AUTHENTICATION True

# Users db settings
ENV ASSEMBLIT_USERS_DB_NAME "users"
ENV ASSEMBLIT_USERS_DB_QUERY_INDEX "user_id"

# Sessions db settings
ENV ASSEMBLIT_SESSIONS_DB_NAME "studies"
ENV ASSEMBLIT_SESSIONS_DB_QUERY_INDEX "study_id"

# Data db settings
ENV ASSEMBLIT_DATA_DB_NAME "data"
ENV ASSEMBLIT_DATA_DB_QUERY_INDEX "dataset_id"

# Analysis db settings
ENV ASSEMBLIT_ANALYSIS_DB_NAME "analysis"
ENV ASSEMBLIT_ANALYSIS_DB_QUERY_INDEX "run_id"

# Set the working directory (cannot be the root directory for Streamlit)
WORKDIR "/${ASSEMBLIT_NAME}"

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
RUN git clone --branch ${ASSEMBLIT_GITHUB_BRANCH_NAME} "${ASSEMBLIT_GITHUB_REPOSITORY_URL}.git" .

# Install Python requirements
RUN pip3 install -r requirements.txt --no-cache-dir

# Expose the network port(s)
EXPOSE ${ASSEMBLIT_CLIENT_PORT}
EXPOSE ${ASSEMBLIT_SERVER_PORT}

# Run
CMD assemblit run ${ASSEMBLIT_HOME_PAGE_NAME}.py && orchestrator start -N ${ASSEMBLIT_NAME} -T ${ASSEMBLIT_SERVER_TYPE} -P ${ASSEMBLIT_SERVER_PORT} -D "/examples/${ASSEMBLIT_NAME}/db" -E ${ASSEMBLIT_SERVER_JOB_ENTRYPOINT}
