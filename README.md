# AFU Global Network Dashboard

A Plotly Dash web application displaying global and regional metrics for the AFU Global Network.

## Running Locally

`ash
pip install -r requirements.txt
python app.py
`

## Deployment on Render

This repository is configured for deployment on [Render](https://render.com).

* **Build Command:** pip install -r requirements.txt
* **Start Command:** gunicorn app:server --bind 0.0.0.0:

