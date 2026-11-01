# Stock Prediction Platform

A full-stack platform for STAR Market stock analysis, five-trading-day trend prediction, research-report sentiment analysis, and strategy backtesting.

## Features

- Company profiles, daily and real-time market data, financial reports, and technical indicators.
- Interactive charts and locally supplied research-report PDF previews.
- LightGBM, LSTM, and configurable multi-relational GNN inference through a Flask API.
- Chinese FinBERT sentiment analysis on research-report titles and abstracts.
- Walk-forward evaluation across 21 stocks and backtesting with fees and slippage.

## Architecture

```text
Vue 2 + Element UI + ECharts
  |-- REST --> Spring Boot :9090 --> MySQL / Wind API
  |-- REST --> Flask       :8083 --> MySQL features / model artifacts / FinBERT

Private Excel datasets --> feature engineering --> training --> evaluation/backtest
                                                    |--> exported model artifacts
```

```text
frontend/             Vue application
backend/              Spring Boot business API and Wind integration
prediction-service/   Flask inference, feature construction, sentiment analysis
model/                Training, model export, evaluation and backtesting
database/             Schema-only SQL; no user or market records
.env.example          Local configuration template
.gitignore            Excludes private data, model weights, binaries and builds
```

## Research models

The thesis compares nine models. This source snapshot includes LightGBM, LSTM and a configurable GNN implementation; the full nine-experiment configuration/results collection is not included.

| ID | Model | Source coverage |
|---|---|---|
| M1 | LightGBM | Training, export and inference |
| M2 | LSTM | Training, export and inference |
| M3 | GNN Best | Fixed relation weighting and ranking-loss mechanisms |
| M4 | GNN-Baseline | Industry-only relation configuration supported |
| M5 | GNN-MultiRel-Equal | Equal relation weighting supported |
| M6 | GNN-MultiRel-Gate | Market-context relation gating supported |
| M7 | GNN-MLP-Head | Configurable MLP prediction head supported |
| M8 | GNN-RelAttn | Thesis experiment; implementation not located in this snapshot |
| M9 | LSTM-GNN | Thesis experiment; implementation not located in this snapshot |

The thesis reports 58.15% classification accuracy for GNN Best and a Sharpe ratio of 1.108 for LSTM-GNN. These are thesis-reported historical experiment results, not newly reproduced results from this repository. FinBERT is a separate sentiment model.

## Prerequisites

- Python 3.10+ and a compatible PyTorch / LightGBM environment.
- Node.js 18 for the legacy Vue CLI 3 frontend; a clean build on other Node versions is not verified.
- Java 8-compatible JDK, Maven and MySQL. Original schema was exported from MySQL 5.7.
- Licensed Wind Java SDK, Windows native DLL and authenticated Wind terminal for Wind integration. The backend currently has a Maven system dependency on `backend/lib/WindJavaAPI_JNA-1.0-SNAPSHOT.jar`; obtain this privately from your licensed installation. Native loading uses `backend/native/WindJava.dll`. These binaries are intentionally excluded, and the backend build requires the SDK JAR.

## Local setup

Run from the repository root. Create your local configuration and replace the example password:

```bash
cp .env.example .env
# Edit .env, then export its values into the current shell:
set -a
source .env
set +a
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r model/requirements.txt -r prediction-service/requirements.txt
```

The applications read environment variables; `.env` is not loaded automatically. Source it in each new terminal. Use shell quoting for passwords containing special characters.

### Database

Create an empty UTF-8 database named `stock`, then import the four SQL files in numbered order, using the MySQL client and your local account:

```bash
mysql -u root -p -e 'CREATE DATABASE IF NOT EXISTS stock CHARACTER SET utf8mb4;'
mysql -u root -p stock < database/01_stock_schema.sql
mysql -u root -p stock < database/02_kcb_close_daily.sql
mysql -u root -p stock < database/03_model_input_features.sql
mysql -u root -p stock < database/04_report_sentiment.sql
```

The schemas contain no seed data. Populate company profiles and historical market tables from your own licensed sources before constructing features. The last schema supplies the sentiment cache table required by the service.

### Model training and export

Create a local `data/` directory containing:

- `688001_with_indicators.xlsx` and the other stock files matching `*_with_indicators.xlsx`.
- `21公司行业分类.xlsx`.
- `科创板收盘价.xlsx`.

Use your own authorized datasets. They are not distributed here.

```bash
cd model
python run_pipeline.py --all-models --config config.yaml
python export_artifact.py --model all --config config_prod.yaml
```

Outputs are written to `model/outputs/`, and inference artifacts to `model/outputs/artifacts/`. `--all-models` runs three model families, not all nine thesis experiments. Different GNN configurations use the same output names; preserve results separately before running another variant.

### Services

Start each component in a separate terminal after loading environment variables and activating Python as needed:

```bash
# Business API (requires the privately supplied Wind SDK JAR)
cd backend
mvn spring-boot:run
```

```bash
# Build database features, then serve predictions
cd prediction-service
python build_features.py
python app.py
```

```bash
# Frontend
cd frontend
npm ci
npm run serve
```

Open the frontend URL printed by Vue CLI. It calls local business APIs on port 9090 and prediction APIs on port 8083. Private PDFs and their contents are excluded; regenerate manifests after supplying local documents.

## Prediction API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/ml/health` | Service liveness; does not validate database/models |
| GET | `/api/ml/predict?stockCode=688001.SH&model=lgbm` | Prediction; model is `lgbm`, `lstm`, or `gnn` |
| GET | `/api/ml/sentiment?stockCode=688001.SH` | Report sentiment and cached results |
| POST | `/api/ml/build-features` | Build features; optional JSON `{"stockCode":"688001.SH"}` |

FinBERT downloads `yiyanghkust/finbert-tone-chinese` on first use and requires network access or a populated local model cache.

## Reproducibility notes

- Offline evaluation standardizes LSTM/GNN features; the current export path does not preserve that same preprocessing. The GNN export training loop also omits the evaluation training loop's ranking loss.
- Online GNN labels and displayed scores use graph-relative percentile ranking rather than the offline probability-threshold rule. Those scores are not calibrated probabilities.
- Some online feature fallbacks differ from offline feature definitions. Current report sentiment aggregation is a simple mean, not time-decay aggregation.
- Full-sample backward filling, winsorization and forward-label split boundaries need review before making strict leakage-free evaluation claims.
- This is an academic prototype. Login currently compares stored passwords directly, and production authentication/authorization is not implemented.

No raw datasets, trained weights, user records, proprietary SDKs, report PDFs or local credentials are included. Source organization and static checks do not constitute a successful end-to-end run or a reproduction of thesis results.
