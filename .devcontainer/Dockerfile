FROM ubuntu:24.04

# Install dependencies
RUN apt-get -y update && \
    apt-get install -y build-essential git cmake libssl-dev python3.12 python3.12-venv python3.12-dev python3-pip coreutils bash curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Rust (required for modern Python package builds like pydantic-core)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    . $HOME/.cargo/env

ENV PATH="/root/.cargo/bin:${PATH}"

# Get liboqs
WORKDIR /root
RUN git clone --depth 1 --branch main https://github.com/open-quantum-safe/liboqs

# Install liboqs with stateful-signature algorithms enabled
RUN cmake -S liboqs -B liboqs/build \
        -DBUILD_SHARED_LIBS=ON \
        -DOQS_ENABLE_SIG_STFL_LMS=ON \
        -DOQS_ENABLE_SIG_STFL_XMSS=ON \
        -DOQS_ENABLE_SIG_STFL_KEY_SIG_GEN=ON && \
    cmake --build liboqs/build --parallel 4 && \
    cmake --install liboqs/build

# Enable a normal user with sudo capabilities (needed for later installs)
RUN useradd -m -c "Open Quantum Safe" -s /bin/bash oqs && \
    apt-get update && apt-get install -y sudo && \
    echo "oqs ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

USER oqs
WORKDIR /home/oqs

# Create a Python 3 virtual environment
RUN python3.12 -m venv venv

# Get liboqs-python
RUN git clone --depth 1 --branch main https://github.com/open-quantum-safe/liboqs-python.git

# Install liboqs-python
# Possible conflict where the container tries to load a system library instead of one in your venv
ENV LD_LIBRARY_PATH=/usr/local/lib
ENV PYTHONPATH=/home/oqs/liboqs-python
RUN . venv/bin/activate && \
    cd liboqs-python && \
    pip install --upgrade pip setuptools wheel && \
    pip install . && \
    cd /home/oqs
