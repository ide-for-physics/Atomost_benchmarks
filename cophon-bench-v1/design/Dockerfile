# cophon-bench v1 whiteboard sandbox (2026-10-15). The whiteboard model runs `claude -p` INSIDE this container: it sees only
# its own work folder, a read-only ssh identity for the cluster, a read-only copy of the pseudopotential table, and the network
# (Anthropic API, the cluster). Nothing of the project tree, the home directory or the other arms is mounted.
# The `claude` binary is bind-mounted read-only at run time (host: ~/.local/share/claude/versions/<v>), so the image holds no secrets.
FROM node:22-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
      openssh-client rsync python3 python3-numpy poppler-utils jq ripgrep less procps ca-certificates git \
    && rm -rf /var/lib/apt/lists/*
# the same uid as the host user, so bind mounts are writable and ssh finds a passwd entry
RUN userdel -r node 2>/dev/null || true; useradd -u 1002 -m -s /bin/bash wb
USER wb
WORKDIR /home/wb/work
ENV HOME=/home/wb PATH=/usr/local/bin:/usr/bin:/bin
