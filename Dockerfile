FROM gcr.io/google.com/cloudsdktool/google-cloud-cli:429.0.0-slim

ENV PYTHONBUFFERED True

# Install requisite python package requirements
RUN pip3 install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy requisite code files into container
COPY src/ src/

CMD exec gunicorn --bind :$PORT --workers 2 --threads 1 --timeout 0 'src.app:create_app()'
