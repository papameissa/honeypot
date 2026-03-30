from flask import Blueprint, Response
from ..utils.exporter import export_attacks_csv, export_attacks_json

export_bp = Blueprint("export", __name__, url_prefix="/export")


@export_bp.route("/csv")
def download_csv():
    csv_data = export_attacks_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=honeytrap_attacks.csv"},
    )


@export_bp.route("/json")
def download_json():
    json_data = export_attacks_json()
    return Response(
        json_data,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=honeytrap_attacks.json"},
    )
