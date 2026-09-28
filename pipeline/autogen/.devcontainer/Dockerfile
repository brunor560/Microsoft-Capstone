# Air-Gapped Evaluation Sandbox (project brief, section 2.2)
#
# This image is the isolated execution environment used by AutoGen to:
#   - execute agent-generated commands,
#   - run application tests,
#   - perform static/code-quality analysis,
#   - and run security scans.
#
# SECURITY:
# This image must not receive credentials from the host environment.
# Do not add Azure keys, GitHub PATs, API keys, .env files, or Docker build
# ARG/ENV entries that contain secrets. Keeping credentials outside the
# sandbox helps prevent prompt-injection-based secret exfiltration.

FROM python:3.11-slim


# ---------------------------------------------------------------------------
# Reproducible tool versions
# ---------------------------------------------------------------------------
#
# Pin external tools so benchmark results do not change simply because a
# newer scanner or analyzer changes its behavior between evaluation runs.

ARG TRUFFLEHOG_VERSION=3.97.5
ARG SCC_VERSION=4.1.0
ARG NODE_MAJOR=22

# TARGETARCH is automatically supplied by Docker BuildKit.
# Expected values are typically "amd64" or "arm64".
ARG TARGETARCH


# ---------------------------------------------------------------------------
# Base environment
# ---------------------------------------------------------------------------

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1


# ---------------------------------------------------------------------------
# Base operating-system tools
# ---------------------------------------------------------------------------
#
# git:
#   Required by the security grader so TruffleHog can inspect repository
#   history in addition to the current working tree.
#
# curl / ca-certificates:
#   Used only while BUILDING the image to download pinned tools.
#   Runtime network access can still be disabled with Docker --network none.
#
# gnupg:
#   Used to install the NodeSource signing key securely.

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        curl \
        gnupg \
    && rm -rf /var/lib/apt/lists/*


# ---------------------------------------------------------------------------
# Node.js application/test toolchain
# ---------------------------------------------------------------------------
#
# The current benchmark target is a Node/Express application. The sandbox
# therefore needs Node.js and npm so agent-generated changes can be executed
# and validated with commands such as:
#
#     npm test
#     node --test test.js
#
# Node is installed inside the sandbox rather than inherited from the host,
# ensuring that every benchmark run uses the same runtime version.

RUN set -eux; \
    mkdir -p /etc/apt/keyrings; \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
        | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg; \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_MAJOR}.x nodistro main" \
        > /etc/apt/sources.list.d/nodesource.list; \
    apt-get update; \
    apt-get install -y --no-install-recommends nodejs; \
    rm -rf /var/lib/apt/lists/*; \
    node --version; \
    npm --version


# ---------------------------------------------------------------------------
# Python grading toolchain
# ---------------------------------------------------------------------------
#
# pytest-json-report:
#   Produces machine-readable test results for Python-based evaluation.
#
# complexipy:
#   Existing complexity analysis tool used by the quality grader.
#
# Even though the current baseline is Node-based, the Python tooling remains
# because the benchmark harness and future target repositories may use Python.

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0 \
        complexipy==3.0.0


# ---------------------------------------------------------------------------
# TruffleHog - Security grader
# ---------------------------------------------------------------------------
#
# TruffleHog scans the working tree and Git history for potential secrets.
# Architecture-specific binaries are selected so the image can run on both
# x86 GitHub runners and ARM-based development machines.

RUN set -eux; \
    case "${TARGETARCH}" in \
        arm64) TH_ARCH=arm64 ;; \
        amd64) TH_ARCH=amd64 ;; \
        *) echo "Unsupported TARGETARCH: ${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    curl -sSfL \
        "https://github.com/trufflesecurity/trufflehog/releases/download/v${TRUFFLEHOG_VERSION}/trufflehog_${TRUFFLEHOG_VERSION}_linux_${TH_ARCH}.tar.gz" \
        -o /tmp/trufflehog.tar.gz; \
    tar -xzf /tmp/trufflehog.tar.gz \
        -C /usr/local/bin \
        trufflehog; \
    rm /tmp/trufflehog.tar.gz; \
    chmod +x /usr/local/bin/trufflehog


# ---------------------------------------------------------------------------
# SCC - Code quality / source metrics
# ---------------------------------------------------------------------------
#
# SCC provides language-aware source-code statistics and supports multiple
# languages, which makes it more useful than a Python-only metric for future
# benchmark codebases.

RUN set -eux; \
    case "${TARGETARCH}" in \
        arm64) SCC_ARCH=arm64 ;; \
        amd64) SCC_ARCH=x86_64 ;; \
        *) echo "Unsupported TARGETARCH: ${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    curl -sSfL \
        "https://github.com/boyter/scc/releases/download/v${SCC_VERSION}/scc_Linux_${SCC_ARCH}.tar.gz" \
        -o /tmp/scc.tar.gz; \
    tar -xzf /tmp/scc.tar.gz \
        -C /usr/local/bin \
        scc; \
    rm /tmp/scc.tar.gz; \
    chmod +x /usr/local/bin/scc


# ---------------------------------------------------------------------------
# Git workspace configuration
# ---------------------------------------------------------------------------
#
# Benchmark workspaces are bind-mounted from the host and may have a
# different UID than the container user. Marking /workspace as safe prevents
# Git and TruffleHog from refusing to inspect the staged repository.

RUN git config --system --add safe.directory /workspace \
    && git config --system --add safe.directory '*'


# ---------------------------------------------------------------------------
# Final sandbox configuration
# ---------------------------------------------------------------------------

WORKDIR /workspace

CMD ["/bin/bash"]
