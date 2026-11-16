"""Load Rwanda's health facilities into the database from the bundled dataset.

Source: "Health Facilities of Rwanda", Humanitarian Open Data Team (OSM export,
ODbL licence), https://data.humdata.org/dataset/hotosm_rwa_health_facilities —
which is why every row keeps an `origin` note.
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from knowledge.models import HealthFacility
from knowledge.services.facility_service import NOT_A_FACILITY

DEFAULT_FILE = (
    Path(__file__).resolve().parents[2] / "data" / "rwanda_health_facilities.geojson"
)


def facility_type(properties: dict) -> str:
    """Map OSM tags onto our own vocabulary.

    The dataset tags a district health centre, a polyclinic and even a primary
    school as amenity=hospital, so the name decides first: an "is hospital"
    answer built on the tag alone would claim all of them are hospitals.
    """
    name = " ".join(
        str(properties.get(key) or "")
        for key in ("name", "name_en", "name_rw", "name_fr")
    ).lower()
    amenity = str(properties.get("amenity") or "").lower()
    healthcare = str(properties.get("healthcare") or "").lower()

    # amenity=hospital on a school, church hall or stadium is a mapping error,
    # and telling a patient it is a hospital is worse than saying nothing.
    if NOT_A_FACILITY.search(name):
        return "other"
    if "health post" in name or "poste" in name:
        return "health_post"
    if "health centre" in name or "health center" in name or "ivuriro" in name:
        return "health_center"
    if amenity in ("pharmacy", "drugstore") or healthcare == "pharmacy" or "pharmac" in name or "farumasi" in name:
        return "pharmacy"
    if "hospital" in name or "ibitaro" in name:
        return "hospital"
    if "clinic" in name or "kliniki" in name:
        return "clinic"
    if amenity == "hospital":
        return "hospital"
    if amenity == "clinic" or healthcare in ("clinic", "doctor", "centre"):
        return "clinic"
    return "other"


def coordinates(geometry: dict):
    """Return (lat, lng); building outlines use the centroid of their outer ring."""
    if not geometry:
        return None, None
    kind = geometry.get("type")
    if kind == "Point":
        point = geometry.get("coordinates") or []
        if len(point) >= 2:
            return float(point[1]), float(point[0])
        return None, None
    if kind == "Polygon":
        rings = geometry.get("coordinates") or []
        ring = rings[0] if rings else []
        if not ring:
            return None, None
        lng = sum(vertex[0] for vertex in ring) / len(ring)
        lat = sum(vertex[1] for vertex in ring) / len(ring)
        return lat, lng
    return None, None


class Command(BaseCommand):
    help = "Create or update HealthFacility rows from the bundled Rwanda dataset."

    def add_arguments(self, parser):
        parser.add_argument("--file", help="GeoJSON path (default: bundled dataset)")
        parser.add_argument(
            "--limit", type=int, help="Import only the first N features (for testing)"
        )
        parser.add_argument(
            "--if-empty",
            action="store_true",
            help="Exit without touching anything once facilities already exist, so a "
            "redeploy cannot undo the corrections an admin made in the panel.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        path = Path(options["file"]) if options["file"] else DEFAULT_FILE
        if not path.exists():
            raise CommandError(f"Dataset not found at {path}")

        if options["if_empty"] and HealthFacility.objects.exists():
            self.stdout.write(
                f"Facilities already present ({HealthFacility.objects.count()} rows); "
                "leaving them and the admin's edits alone."
            )
            return

        with path.open(encoding="utf-8") as handle:
            features = json.load(handle).get("features", [])
        if options["limit"]:
            features = features[: options["limit"]]

        created = updated = skipped = 0
        for feature in features:
            properties = feature.get("properties") or {}
            external_id = str(properties.get("id") or "").strip()
            name = str(properties.get("name") or properties.get("name_en") or "").strip()
            if not external_id or not name:
                skipped += 1
                continue

            lat, lng = coordinates(feature.get("geometry"))
            _, was_created = HealthFacility.objects.update_or_create(
                external_id=external_id,
                defaults={
                    "name": name[:300],
                    "name_en": str(properties.get("name_en") or "")[:300],
                    "facility_type": facility_type(properties),
                    "province": str(properties.get("adm1_name") or "")[:60],
                    "district": str(properties.get("adm2_name") or "")[:60],
                    "sector": str(properties.get("adm3_name") or "")[:60],
                    "latitude": lat,
                    "longitude": lng,
                },
            )
            created += was_created
            updated += not was_created

        self.stdout.write(
            self.style.SUCCESS(
                f"Facilities: {created} created, {updated} updated, "
                f"{skipped} skipped (no id or name); {HealthFacility.objects.count()} total."
            )
        )
