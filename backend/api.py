import logging
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

from app.services.pipeline import run_pipeline
from app.services.storage import load_clean, load_stats as load_stats_df
from app.utils.logger import setup_logger

app = Flask(__name__)
CORS(app)

setup_logger()


# GET /data 
@app.route("/data", methods=["GET"])
def get_data():
    df = load_clean()
    df["period"] = pd.to_datetime(df["period"])

    if df.empty:
        return jsonify({
            "status":  "ok",
            "message": "No hay datos disponibles. Ejecuta /refresh primero.",
            "total":   0,
            "page":    1,
            "pages":   0,
            "data":    []
        }), 200

    # Filtros
    date_from  = request.args.get("date_from")
    date_to    = request.args.get("date_to")
    min_outage = request.args.get("min_outage", type=float)

    if date_from:
        df = df[df["period"] >= pd.to_datetime(date_from)]
    if date_to:
        df = df[df["period"] <= pd.to_datetime(date_to)]
    if min_outage is not None:
        df = df[df["outage"] >= min_outage]

    # Paginación
    page  = max(1, request.args.get("page",  default=1,  type=int))
    limit = min(500, max(1, request.args.get("limit", default=50, type=int)))

    total  = len(df)
    pages  = (total + limit - 1) // limit
    start  = (page - 1) * limit
    end    = start + limit

    df_page = df.sort_values("period", ascending=False).iloc[start:end]
    records = df_page.copy()
    records["period"] = records["period"].dt.strftime("%Y-%m-%d")

    return jsonify({
        "status": "ok",
        "total":  total,
        "page":   page,
        "pages":  pages,
        "limit":  limit,
        "data":   records.to_dict(orient="records")
    }), 200


# POST /refresh 
# Dispara el pipeline de extracción y retorna el resultado.
@app.route("/refresh", methods=["POST"])
def refresh():
    logging.info("Refresh solicitado via API")

    try:
        result = run_pipeline()
        return jsonify({"status": "ok", "pipeline": result}), 200

    except Exception as e:
        logging.error(f"Error en /refresh: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# GET /stats 
# Devuelve las estadísticas anuales.
@app.route("/stats", methods=["GET"])
def get_stats():
    df = load_stats_df()

    if df.empty:
        return jsonify({
            "status":  "ok",
            "message": "No hay estadísticas disponibles. Ejecuta /refresh primero.",
            "data":    []
        }), 200

    return jsonify({
        "status": "ok",
        "data":   df.to_dict(orient="records")
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
