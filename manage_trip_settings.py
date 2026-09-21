"""Safely update PTIS user_config.json from a guided workflow form."""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from config import KST
from focus import FocusConfigError, parse_focus_config
from route_watch import (
    RouteWatchConfigError,
    parse_route_watch_config,
    parse_route_watch_configs,
)

USER_CONFIG_FILE = Path("user_config.json")
OPERATIONS = {"exact_add", "exact_replace", "focus_set", "pause_all"}


class SettingsError(ValueError):
    pass


def _load(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SettingsError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SettingsError("user_config.json must contain a JSON object")
    return payload


def _positive_optional(value: str, name: str) -> Optional[int]:
    value = value.strip()
    if not value or value == "0":
        return None
    try:
        parsed = int(value)
    except ValueError as exc:
        raise SettingsError(f"{name} must be a positive whole number") from exc
    if parsed <= 0:
        raise SettingsError(f"{name} must be a positive whole number")
    return parsed


def _required(value: str, name: str) -> str:
    value = value.strip()
    if not value:
        raise SettingsError(f"{name} is required for this operation")
    return value


def _validate(payload: Dict[str, Any], now: Optional[datetime]) -> None:
    try:
        parse_focus_config(payload, now=now)
        parse_route_watch_configs(payload, now=now)
    except (FocusConfigError, RouteWatchConfigError) as exc:
        raise SettingsError(str(exc)) from exc


def update_settings(
    payload: Dict[str, Any],
    operation: str,
    name: str = "",
    origin: str = "",
    destination_or_region: str = "",
    outbound_from: str = "",
    outbound_to: str = "",
    stay_min: str = "",
    stay_max: str = "",
    max_price: str = "",
    nonstop_only: bool = False,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    if operation not in OPERATIONS:
        raise SettingsError(f"Unknown operation: {operation}")
    result = json.loads(json.dumps(payload))
    result.setdefault("focus_slot", {"mode": "alternate"})
    result.setdefault("focus_search", {"enabled": False})
    result.setdefault("route_watch", {"enabled": False})
    result.setdefault("route_watches", [])

    if operation == "pause_all":
        result["focus_search"] = {"enabled": False}
        result["route_watch"] = {"enabled": False}
        routes = result.get("route_watches", [])
        if not isinstance(routes, list):
            routes = []
        result["route_watches"] = [
            {**route, "enabled": False} if isinstance(route, dict) else route
            for route in routes
        ]
        _validate(result, now)
        return result

    origin = _required(origin, "origin").upper()
    destination_or_region = _required(
        destination_or_region, "destination or region"
    )
    outbound_from = _required(outbound_from, "first date")
    outbound_to = _required(outbound_to, "second date")
    price = _positive_optional(max_price, "max price")

    if operation == "focus_set":
        minimum = _positive_optional(stay_min, "minimum stay")
        maximum = _positive_optional(stay_max, "maximum stay")
        if minimum is None or maximum is None:
            raise SettingsError("minimum and maximum stay are required")
        focus = {
            "enabled": True,
            "origin": origin,
            "region": destination_or_region,
            "outbound_from": outbound_from,
            "outbound_to": outbound_to,
            "stay_min": minimum,
            "stay_max": maximum,
        }
        if price is not None:
            focus["max_price"] = price
        result["focus_search"] = focus
    else:
        route = {
            "name": name.strip(),
            "enabled": True,
            "origin": origin,
            "destination": destination_or_region.upper(),
            "outbound_date": outbound_from,
            "return_date": outbound_to,
            "nonstop_only": bool(nonstop_only),
        }
        if price is not None:
            route["max_price"] = price
        try:
            parse_route_watch_config({"route_watch": route}, now=now)
        except RouteWatchConfigError as exc:
            raise SettingsError(str(exc)) from exc
        if operation == "exact_replace":
            result["route_watch"] = {"enabled": False}
            result["route_watches"] = [route]
        else:
            routes = result.get("route_watches", [])
            if not isinstance(routes, list):
                raise SettingsError("route_watches must be a JSON array")
            result["route_watches"] = routes + [route]

    _validate(result, now)
    return result


def save_settings(path: Path, payload: Dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _operation(value: str) -> str:
    value = value.strip()
    mapping = {
        "1": "exact_add",
        "2": "exact_replace",
        "3": "focus_set",
        "4": "pause_all",
    }
    key = value.split(".", 1)[0]
    return mapping.get(key, value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=USER_CONFIG_FILE)
    parser.add_argument("--operation", required=True)
    parser.add_argument("--name", default="")
    parser.add_argument("--origin", default="")
    parser.add_argument("--destination-or-region", default="")
    parser.add_argument("--outbound-from", default="")
    parser.add_argument("--outbound-to", default="")
    parser.add_argument("--stay-min", default="")
    parser.add_argument("--stay-max", default="")
    parser.add_argument("--max-price", default="")
    parser.add_argument("--nonstop-only", action="store_true")
    args = parser.parse_args()
    try:
        payload = update_settings(
            _load(args.config), _operation(args.operation), args.name, args.origin,
            args.destination_or_region, args.outbound_from, args.outbound_to,
            args.stay_min, args.stay_max, args.max_price, args.nonstop_only,
            now=datetime.now(KST),
        )
        save_settings(args.config, payload)
    except SettingsError as exc:
        parser.error(str(exc))
    print(f"Saved {args.config} for {_operation(args.operation)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
