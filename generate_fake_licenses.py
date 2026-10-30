"""
Generate a fake Microsoft 365 license report for the License Auditor project.

Usage:
    pip install faker
    python generate_fake_licenses.py

Output: data/m365_licenses.csv
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

fake = Faker()
Faker.seed(42)   # same "random" data every run -> reproducible
random.seed(42)

N_USERS = 80
TODAY = date(2026, 11, 1)

# Approximate monthly prices per plan (USD)
PLANS = {
    "Microsoft 365 Business Basic": 6.00,
    "Microsoft 365 Business Standard": 12.50,
    "Microsoft 365 E3": 36.00,
    "Microsoft 365 E5": 57.00,
}

DEPARTMENTS = ["Sales", "Finance", "HR", "IT", "Marketing", "Operations"]


def make_user(i: int) -> dict:
    name = fake.name()
    email = name.lower().replace(" ", ".") + "@contoso-demo.com"

    # Decide which "problem" (if any) this user has
    scenario = random.choices(
        ["normal", "inactive", "disabled_with_license", "overlicensed"],
        weights=[70, 12, 8, 10],
    )[0]

    plan = random.choice(list(PLANS))
    enabled = True
    last_login = TODAY - timedelta(days=random.randint(0, 20))

    if scenario == "inactive":
        last_login = TODAY - timedelta(days=random.randint(91, 300))
    elif scenario == "disabled_with_license":
        enabled = False  # left the company but still has a paid license
        last_login = TODAY - timedelta(days=random.randint(30, 200))
    elif scenario == "overlicensed":
        plan = "Microsoft 365 E5"  # most expensive plan, barely used
        last_login = TODAY - timedelta(days=random.randint(40, 90))

    return {
        "user_id": f"U{i:04d}",
        "name": name,
        "email": email,
        "department": random.choice(DEPARTMENTS),
        "license_plan": plan,
        "monthly_cost_usd": PLANS[plan],
        "last_login_date": last_login.isoformat(),
        "account_enabled": enabled,
    }


def main() -> None:
    users = [make_user(i) for i in range(1, N_USERS + 1)]

    out = Path("data/m365_licenses.csv")
    out.parent.mkdir(exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=users[0].keys())
        writer.writeheader()
        writer.writerows(users)

    print(f"Wrote {len(users)} users to {out}")


if __name__ == "__main__":
    main()
