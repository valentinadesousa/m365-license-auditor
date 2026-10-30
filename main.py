import csv
import io
from datetime import date, datetime

from fastapi import FastAPI, File, UploadFile

app = FastAPI(title="M365 License Auditor")

INACTIVE_DAYS = 90


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/audit")
async def audit(file: UploadFile = File(...)):
    content = await file.read()
    rows = list(csv.DictReader(io.StringIO(content.decode("utf-8"))))

    today = date.today()
    total_cost = 0.0
    inactive = []
    disabled_with_license = []

    for row in rows:
        cost = float(row["monthly_cost_usd"])
        total_cost += cost
        last_login = datetime.strptime(row["last_login_date"], "%Y-%m-%d").date()

        if row["account_enabled"] == "False":
            disabled_with_license.append(row["email"])
        elif (today - last_login).days > INACTIVE_DAYS:
            inactive.append(row["email"])

    return {
        "total_users": len(rows),
        "total_monthly_cost_usd": round(total_cost, 2),
        "inactive_users": inactive,
        "disabled_with_license": disabled_with_license,
    }