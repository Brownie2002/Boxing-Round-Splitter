############################################
# STAGE 1 — Image de production
############################################
FROM python:3.12-slim AS prod

# Éviter Python qui bavarde trop
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Dépendances (si requirements.txt existe)
RUN pip install --no-cache-dir librosa numpy scipy matplotlib


# Arguments pour l'utilisateur VS Code
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=1000

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=fr_FR.UTF-8 \
    LC_ALL=fr_FR.UTF-8

# Outils de base + git + locales + couleur
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    locales \
    less \
    nano \
    bash-completion \
    && sed -i '/fr_FR.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen \
    && rm -rf /var/lib/apt/lists/*

# Création du groupe et user non-root
RUN groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} \
       --create-home --shell /bin/bash ${USERNAME}

# Git un peu plus humain
RUN git config --system color.ui auto

WORKDIR /workspace

# Bash agréable pour VS Code
RUN echo "force_color_prompt=yes" >> /home/${USERNAME}/.bashrc

USER ${USERNAME}

RUN curl -LsSf https://mistral.ai/vibe/install.sh | bash


# VS Code aime quand le container ne meurt pas
CMD ["sleep", "infinity"]
