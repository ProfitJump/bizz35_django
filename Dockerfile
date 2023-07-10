# Pull base image
FROM python:3.11-alpine3.18

# Set work directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app
RUN pip install -r requirements.txt

# Copy project
COPY . /usr/src/app

# Run and expose project
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
