# 1. Base Image: Ubuntu 24.04
FROM ubuntu:24.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# 2. Install System Dependencies
# FIXED: Added space after 'lcov' and removed empty lines to prevent syntax errors
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    cmake \
    python3 \
    python3-pip \
    python3-venv \
    software-properties-common \
    ca-certificates \
    lcov \
    libboost-system-dev \
    libgmp-dev \
    libarmadillo-dev \
    nlohmann-json3-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    zlib1g-dev \
    libnghttp2-dev \
    libkrb5-dev \
    libldap2-dev \
    libidn2-dev \
    libpsl-dev \
    libbrotli-dev \
    libzstd-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Install Z3 4.8.17 from Source
RUN git clone https://github.com/Z3Prover/z3.git --branch z3-4.8.17 && \
    cd z3 && \
    python3 scripts/mk_make.py && \
    cd build && \
    make -j$(nproc) && \
    make install && \
    cd ../.. && rm -rf z3

# 4. Install Foundry (FROM GITHUB DIRECTLY)
# This link is rarely blocked by OpenDNS
RUN curl -L https://github.com/foundry-rs/foundry/releases/download/nightly/foundry_nightly_linux_amd64.tar.gz -o foundry.tar.gz && \
    tar -xzf foundry.tar.gz -C /usr/local/bin && \
    rm foundry.tar.gz && \
    chmod +x /usr/local/bin/forge /usr/local/bin/cast

# Add Foundry to PATH
ENV PATH="/root/.foundry/bin:$PATH"

# 5. Install Solc (Solidity Compiler 0.8.21)
RUN curl -fsSL -k https://github.com/ethereum/solidity/releases/download/v0.8.21/solc-static-linux -o /usr/local/bin/solc && \
    chmod +x /usr/local/bin/solc

# 6. Copy Your Project Files
COPY . /app

# 7. Install Your Python Package
RUN python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install .

# 8. Setup Environment Variables
ENV PATH="/venv/bin:$PATH"

# 9. Entry Point
ENTRYPOINT ["neurosolidtg"]