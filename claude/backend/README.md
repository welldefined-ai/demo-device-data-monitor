# DDMS Backend

FastAPI backend for the Distributed Device Monitoring System.

## Development

```bash
pip install uv
uv pip install -e ".[dev]"
uvicorn ddms.main:app --reload
```

## Testing

```bash
pytest
```
