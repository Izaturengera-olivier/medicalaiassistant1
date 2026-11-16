"""Load Rwanda's official administrative hierarchy into the database.

Source: "rwanda-locations-json" by Jean Bosco Ndayizeye (MIT licence),
https://github.com/jnkindi/rwanda-locations-json — one flat record per village,
carrying the government code and name of every level above it. The file is
committed rather than downloaded at runtime so an offline deploy still answers
"which hospital is near me" for a village nobody typed into a config.
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from knowledge.models import AdminPlace

DEFAULT_FILE = (
    Path(__file__).resolve().parents[2] / "data" / "rwanda_admin_locations.json"
)

# The dataset files each province under a statistical short name. Keep it: it is
# what a patient types ("Kigali", not "Kigali City"), and the facility register's
# longer spelling is applied when a place is used as a filter.
PROVINCE_NAMES = {
    "KIGALI": "Kigali",
    "NORTH": "North",
    "SOUTH": "South",
    "EAST": "East",
    "WEST": "West",
}


def units(records):
    """De-duplicate the flat village records into one row per administrative unit.

    Each row stores its own name and code plus the ancestors above it, so resolving
    a village needs no recursive query. A level's own field stays empty - "which
    district is this?" is answered by `level` and `name`, not by guessing.
    """
    seen = set()
    for record in records:
        province = PROVINCE_NAMES.get(
            str(record.get("province_name") or "").strip().upper(),
            str(record.get("province_name") or "").strip().title(),
        )
        district = str(record.get("district_name") or "").strip()
        sector = str(record.get("sector_name") or "").strip()
        cell = str(record.get("cell_name") or "").strip()
        village = str(record.get("village_name") or "").strip()

        levels = [
            ("province", province, record.get("province_code"), {}),
            ("district", district, record.get("district_code"), {"province": province}),
            (
                "sector",
                sector,
                record.get("sector_code"),
                {"province": province, "district": district},
            ),
            (
                "cell",
                cell,
                record.get("cell_code"),
                {"province": province, "district": district, "sector": sector},
            ),
            (
                "village",
                village,
                record.get("village_code"),
                {
                    "province": province,
                    "district": district,
                    "sector": sector,
                    "cell": cell,
                },
            ),
        ]
        for level, name, code, ancestors in levels:
            if not name or code in (None, ""):
                continue
            key = (level, str(code))
            if key in seen:
                continue
            seen.add(key)
            yield AdminPlace(
                level=level,
                name=name,
                # bulk_create never calls save(), so the match key is set here.
                name_key=AdminPlace.key_for(name),
                code=str(code),
                province=ancestors.get("province", ""),
                district=ancestors.get("district", ""),
                sector=ancestors.get("sector", ""),
                cell=ancestors.get("cell", ""),
            )


class Command(BaseCommand):
    help = "Create AdminPlace rows from the bundled official hierarchy dataset."

    def add_arguments(self, parser):
        parser.add_argument("--file", help="JSON path (default: bundled dataset)")
        parser.add_argument(
            "--if-empty",
            action="store_true",
            help="Exit without touching anything once places already exist, so a "
            "redeploy cannot undo the corrections an admin made in the panel.",
        )

    def handle(self, *args, **options):
        path = Path(options["file"]) if options["file"] else DEFAULT_FILE
        if not path.exists():
            raise CommandError(f"Dataset not found at {path}")

        if options["if_empty"] and AdminPlace.objects.exists():
            self.stdout.write(
                f"Places already present ({AdminPlace.objects.count()} rows); "
                "leaving them and the admin's edits alone."
            )
            return

        with path.open(encoding="utf-8") as handle:
            records = json.load(handle)

        rows = list(units(records))
        with transaction.atomic():
            # Idempotent without a delete: an admin's deactivation of a wrong row
            # survives a re-seed, because conflicting rows are left as they are.
            AdminPlace.objects.bulk_create(rows, ignore_conflicts=True, batch_size=1000)

        counts = {
            level: AdminPlace.objects.filter(level=level).count()
            for level, _ in AdminPlace.LEVEL
        }
        self.stdout.write(
            self.style.SUCCESS(
                f"Places: {len(rows)} read, "
                + ", ".join(f"{count} {level}" for level, count in counts.items())
                + f"; {AdminPlace.objects.count()} total."
            )
        )
