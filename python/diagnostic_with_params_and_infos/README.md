# Diagnostic Service with Parameters and Infos Messages

A Python service that simulates diagnostic data for devices, publishing metrics, parameters, and device information through NATS.

## Requirements

- Python 3.11 or higher
- NATS server running locally or accessible
- `uv` (recommended) or pip

## Running the Service

### Using uv (Recommended)

The simplest way to run the service is using `uv`:

```bash
uv run main.py
```

### Alternative: Using Traditional Python Setup

If you prefer using traditional Python setup:

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the service:

```bash
python main.py
```

### Environment Variables

The service can be customized using the following environment variables:

- `DEVICE_SERIAL_NUMBER`: Device serial number (default: "1122334455")
- `LOG_LEVEL`: Logging level (default: "INFO"). Possible values: "DEBUG", "INFO", "WARNING", "ERROR"

Example:

```bash
DEVICE_SERIAL_NUMBER=ABCD123456 LOG_LEVEL=DEBUG python main.py
```
