# Air-Gapped Evaluation Sandbox (project brief, section 2.2)
#
# The ephemeral execution engine for compiling code, running tests, and
# running static analysis. Instantiated by AutoGen via
# DockerCommandLineCodeExecutor.
#
# SECURITY: this image is built and run WITHOUT the host's environment.
# No Azure keys and no GitHub PATs are ever injected here. Do not add ARG or
# ENV entries that accept credentials -- doing so would defeat the Indirect
# Prompt Injection (IPI) exfiltration mitigation this sandbox exists to
# provide.

FROM python:3.11-slim

# Pinned toolchain versions. Pinning keeps grading reproducible across runs:
# an unpinned linter that changes its default rules would silently shift Q
# scores between benchmarks.
ARG TRUFFLEHOG_VERSION=3.97.5
ARG SCC_VERSION=4.1.0

# TARGETARCH is supplied automatically by BuildKit ("arm64" or "amd64").
# Both tools ship native builds for each, so the sandbox runs without
# emulation on Apple Silicon and on x86 CI runners alike.
ARG TARGETARCH

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# git is required by the Security grader: trufflehog scans the workspace as a
# git repository (`trufflehog git file:///workspace`) so it can walk history.
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        curl \
    && rm -rf /var/lib/apt/lists/*

# --- Python grading toolchain ------------------------------------------------
# pytest-json-report backs the Functionality grader's --json-report output.
RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0 \
        complexipy==3.0.0

# --- trufflehog (Security / S) ------------------------------------------------
RUN set -eux; \
    case "${TARGETARCH}" in \
        arm64) TH_ARCH=arm64 ;; \
        amd64) TH_ARCH=amd64 ;; \
        *) echo "Unsupported TARGETARCH: ${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    curl -sSfL \
        "https://github.com/trufflesecurity/trufflehog/releases/download/v${TRUFFLEHOG_VERSION}/trufflehog_${TRUFFLEHOG_VERSION}_linux_${TH_ARCH}.tar.gz" \
        -o /tmp/trufflehog.tar.gz; \
    tar -xzf /tmp/trufflehog.tar.gz -C /usr/local/bin trufflehog; \
    rm /tmp/trufflehog.tar.gz; \
    chmod +x /usr/local/bin/trufflehog

# --- scc (Code Quality / Q) ---------------------------------------------------
RUN set -eux; \
    case "${TARGETARCH}" in \
        arm64) SCC_ARCH=arm64 ;; \
        amd64) SCC_ARCH=x86_64 ;; \
        *) echo "Unsupported TARGETARCH: ${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    curl -sSfL \
        "https://github.com/boyter/scc/releases/download/v${SCC_VERSION}/scc_Linux_${SCC_ARCH}.tar.gz" \
        -o /tmp/scc.tar.gz; \
    tar -xzf /tmp/scc.tar.gz -C /usr/local/bin scc; \
    rm /tmp/scc.tar.gz; \
    chmod +x /usr/local/bin/scc

# trufflehog refuses to scan a repo owned by a different uid than the caller;
# the bind-mounted workspace comes from the macOS host, so mark it safe.
RUN git config --system --add safe.directory /workspace \
    && git config --system --add safe.directory '*'

WORKDIR /workspace

CMD ["/bin/bash"]
