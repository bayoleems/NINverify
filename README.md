# Nigerian National Identification Number (NIN) Validation API

A FastAPI service that validates Nigerian National Identification Numbers (NIN) by automating the passport immigration portal and using Google Gemini to solve captchas.

## Prerequisites

- Python 3.11+
- [Google AI Studio](https://aistudio.google.com/) API key (free tier available)
- Google Chrome (recommended on macOS for local Playwright runs)

## Quick start

### 1. Get a Gemini API key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Create an API key from the dashboard

### 2. Configure environment variables

Copy the sample env file and add your key:

```bash
cp .env.example .env
```

Edit `.env`:

```env
GEMINI_API_KEY=your_api_key_here
```

### 3. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

On macOS, install Google Chrome if you have not already — Playwright uses it locally for better stability.

### 4. Run the API

```bash
python app.py
```

The server starts at `http://localhost:8000`.

Interactive docs: `http://localhost:8000/docs`

## Docker

Build and run with your API key:

```bash
docker build -t ninverify .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_api_key_here ninverify
```

Or use an env file:

```bash
docker run -p 8000:8000 --env-file .env ninverify
```

## Endpoints

### Health check

- **URL:** `/`
- **Method:** `GET`

### Validate NIN (async)

- **URL:** `/get_validation/`
- **Method:** `POST`

### Validate NIN (sync)

- **URL:** `/get_validation_sync/`
- **Method:** `POST`

### Request body

| Field   | Type   | Description                                      |
|---------|--------|--------------------------------------------------|
| `nin`   | string | 11-digit NIN                                     |
| `day`   | string | Day of birth, e.g. `06`                          |
| `month` | string | Month abbreviation, e.g. `Jan`, `Feb`, `Oct`     |
| `year`  | string | Year of birth, e.g. `2015`                       |

### Example request

```json
{
  "nin": "12345678901",
  "day": "06",
  "month": "Oct",
  "year": "2015"
}
```

### Example response

```json
{
  "First Name": "JOHN",
  "Middle Name": "SINCLAIR",
  "Last Name": "DOE",
  "Date of Birth": "06-10-2015",
  "Gender": "MALE",
  "Marital Status": "SINGLE",
  "Place of Birth": "Akure Ondo",
  "Maiden Name": ""
}
```

## Validation rules

- NIN must be exactly 11 digits
- NIN must contain only numeric characters
- Month must use three-letter abbreviations: `Jan`, `Feb`, `Mar`, `Apr`, `May`, `Jun`, `Jul`, `Aug`, `Sep`, `Oct`, `Nov`, `Dec`

## Environment variables

| Variable         | Required | Description |
|------------------|----------|-------------|
| `GEMINI_API_KEY` | Yes      | API key from [Google AI Studio](https://aistudio.google.com/) |
| `GEMINI_MODEL`   | No       | Optional model override, e.g. `gemini-2.5-flash-lite` |

See `.env.example` for a starter template.

## Contributing

Contributions are welcome. Please open a pull request and follow the existing code style.

## Contact

Saleem Adebayo — bayoleeems@gmail.com
