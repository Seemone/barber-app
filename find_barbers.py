#!/usr/bin/env python3
import argparse

import geocoder

from barberapp_client import search_nearby


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Trova barbieri nelle vicinanze usando BarberApp."
    )
    parser.add_argument("--lat", type=float, help="Latitudine da usare per la ricerca")
    parser.add_argument("--lon", type=float, help="Longitudine da usare per la ricerca")
    parser.add_argument(
        "--radius",
        type=int,
        default=6000,
        help="Raggio di ricerca in metri (default 6000)",
    )

    args = parser.parse_args()
    if (args.lat is None) ^ (args.lon is None):
        parser.error("--lat e --lon devono essere usati insieme")
    return args


def main():
    args = parse_args()

    if args.lat is not None:
        lat, lon = args.lat, args.lon
        print("📍 Posizione fornita tramite argomenti CLI.\n")
    else:
        g = geocoder.ip("me")
        lat, lon = g.latlng
        print(f"📍 Posizione rilevata: {lat}, {lon}\n")

    results = search_nearby(lat=lat, lon=lon, radius=args.radius)

    for shop in results:
        nome = shop.get("Nome", "N/A")
        key = shop.get("Key", "N/A")
        indirizzo = shop.get("Indirizzo", "N/A")
        telefono = shop.get("Telefono", "N/A")
        distanza = shop.get("Distanza")
        if distanza is not None:
            distanza_str = f"{distanza}m"
        else:
            distanza_str = "N/A"
        print(f"{nome} - ID: {key}")
        print(f"  Indirizzo: {indirizzo}")
        print(f"  Tel: {telefono}")
        print(f"  Distanza: {distanza_str}")


if __name__ == "__main__":
    main()