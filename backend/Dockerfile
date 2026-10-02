FROM python:3.12-slim

WORKDIR /app

# Install dependencies first so Docker can cache this layer as long as
# requirements.txt doesn't change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# The SQLite file is created inside the container on first run (and seeded
# with the demo admin/customer accounts and fleet, see app/main.py). It is
# not mounted on a volume, so it resets whenever the container is removed —
# fine for development/demo use, matching the project's SQLite-for-dev
# constraint (see docs/requirements.md, §5).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
