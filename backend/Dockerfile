# Use official Python 3.12 slim image as base
FROM python:3.12-slim

# Install LaTeX and dependencies with apt
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    dvipng \
    cm-super \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy requirements file and install Python deps
COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copy your entire project code into the container
COPY . .

# Command to run your app (change if your main file or command differs)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
