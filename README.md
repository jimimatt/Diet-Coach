# Diet Coach

AI-powered nutritionist assistant based on [this DataCamp tutorial](https://www.datacamp.com/de/tutorial/mistral-agents-api).

Changed frontend from gradio to streamlit and did some linting adaptions.

## Setup

```bash
uv sync
cp template.env .env
```

Copy your mistral api key to the `.env` file.

## Run

```bash
uv run streamlit run gui.py
```

Opens at http://localhost:8501
