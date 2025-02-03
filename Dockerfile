FROM python:3.10.15-bullseye

RUN apt-get update && \
  apt-get install -y \
  # General dependencies
  locales \
  locales-all && \
  # Clean local repository of package files since they won't be needed anymore.
  # Make sure this line is called after all apt-get update/install commands have
  # run.
  apt-get clean && \
  # Also delete the index files which we also don't need anymore.
  rm -rf /var/lib/apt/lists/*

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user

# Switch to the "user" user
USER user

# Set home to the user's home directory
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

# Set the working directory to the user's home directory
WORKDIR $HOME/app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Add app code here
COPY --chown=user . $HOME/app
# Set the working directory to the user's home directory
WORKDIR $HOME/app

# Run Mesop through gunicorn. Should be available at localhost:7860
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "main:me"]