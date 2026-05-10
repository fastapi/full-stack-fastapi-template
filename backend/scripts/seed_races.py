#!/usr/bin/env python3
"""Seed the database with real Vietnamese race events.

Usage (from src/backend/):
    uv run python scripts/seed_races.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date
from sqlmodel import Session, select

from app.core.db import engine
from app.models import (
    Race,
    RaceCategoryCreate,
    RaceCreate,
    User,
)
from app import crud

RACES: list[dict] = [
    {
        "name": "Vietnam Mountain Marathon",
        "description": "The iconic trail race through the misty peaks of Sa Pa, Lào Cai. One of Southeast Asia's most spectacular mountain races with breathtaking views of terraced rice fields.",
        "location": "Sa Pa, Lào Cai",
        "city": "Sa Pa",
        "country": "Vietnam",
        "latitude": 22.3364,
        "longitude": 103.8438,
        "terrain_type": "trail",
        "difficulty_level": "extreme",
        "elevation_gain_m": 4200,
        "is_certified": True,
        "website_url": "https://vietnammountainmarathon.com",
        "event_start_date": date(2026, 8, 15),
        "event_end_date": date(2026, 8, 16),
        "base_price": 1_500_000,
        "status": "published",
        "categories": [
            {"name": "70K Ultra", "distance_km": 70, "price": 2_000_000, "cutoff_time_minutes": 1800},
            {"name": "42K Marathon", "distance_km": 42, "price": 1_500_000, "cutoff_time_minutes": 960},
            {"name": "21K Half", "distance_km": 21, "price": 900_000, "cutoff_time_minutes": 480},
        ],
    },
    {
        "name": "Dalat Ultra Trail",
        "description": "Running through the pine forests and waterfalls of the Central Highlands, this race showcases Da Lat's stunning cool-climate scenery.",
        "location": "Đà Lạt, Lâm Đồng",
        "city": "Đà Lạt",
        "country": "Vietnam",
        "latitude": 11.9404,
        "longitude": 108.4583,
        "terrain_type": "trail",
        "difficulty_level": "hard",
        "elevation_gain_m": 2800,
        "is_certified": False,
        "website_url": None,
        "event_start_date": date(2026, 5, 20),
        "base_price": 800_000,
        "status": "registration_open",
        "categories": [
            {"name": "100K Ultra", "distance_km": 100, "price": 1_800_000, "cutoff_time_minutes": 2400},
            {"name": "50K", "distance_km": 50, "price": 1_200_000, "cutoff_time_minutes": 1200},
            {"name": "25K", "distance_km": 25, "price": 700_000, "cutoff_time_minutes": 600},
        ],
    },
    {
        "name": "Hà Nội International Marathon",
        "description": "Run through the historic streets of Vietnam's capital city, passing Hoan Kiem Lake and the Old Quarter.",
        "location": "Hà Nội",
        "city": "Hà Nội",
        "country": "Vietnam",
        "latitude": 21.0285,
        "longitude": 105.8542,
        "terrain_type": "road",
        "difficulty_level": "moderate",
        "elevation_gain_m": 120,
        "is_certified": True,
        "website_url": None,
        "event_start_date": date(2026, 11, 8),
        "base_price": 600_000,
        "status": "published",
        "categories": [
            {"name": "42K Full Marathon", "distance_km": 42.195, "price": 900_000, "cutoff_time_minutes": 360},
            {"name": "21K Half Marathon", "distance_km": 21.1, "price": 600_000, "cutoff_time_minutes": 210},
            {"name": "10K", "distance_km": 10, "price": 350_000, "cutoff_time_minutes": 120},
            {"name": "5K Fun Run", "distance_km": 5, "price": 200_000, "cutoff_time_minutes": 90},
        ],
    },
    {
        "name": "Ho Chi Minh City Marathon",
        "description": "The biggest road race in southern Vietnam, starting at the iconic City Hall and winding through District 1's wide boulevards.",
        "location": "Hồ Chí Minh City",
        "city": "Hồ Chí Minh City",
        "country": "Vietnam",
        "latitude": 10.7769,
        "longitude": 106.7009,
        "terrain_type": "road",
        "difficulty_level": "moderate",
        "elevation_gain_m": 60,
        "is_certified": True,
        "event_start_date": date(2026, 10, 11),
        "base_price": 700_000,
        "status": "published",
        "categories": [
            {"name": "42K", "distance_km": 42.195, "price": 1_000_000, "cutoff_time_minutes": 360},
            {"name": "21K", "distance_km": 21.1, "price": 650_000, "cutoff_time_minutes": 210},
            {"name": "10K", "distance_km": 10, "price": 400_000, "cutoff_time_minutes": 120},
        ],
    },
    {
        "name": "Mù Cang Chải Skyrace",
        "description": "One of Vietnam's most technical skyrunning routes, traversing the dramatic Mù Cang Chải terraced landscape at altitudes above 2000m.",
        "location": "Mù Cang Chải, Yên Bái",
        "city": "Mù Cang Chải",
        "country": "Vietnam",
        "latitude": 21.8167,
        "longitude": 104.0833,
        "terrain_type": "trail",
        "difficulty_level": "extreme",
        "elevation_gain_m": 5500,
        "is_certified": False,
        "event_start_date": date(2026, 9, 27),
        "base_price": 1_200_000,
        "status": "published",
        "categories": [
            {"name": "VK (Vertical Kilometer)", "distance_km": 8, "price": 800_000, "cutoff_time_minutes": 180},
            {"name": "Skyrace 28K", "distance_km": 28, "price": 1_200_000, "cutoff_time_minutes": 600},
        ],
    },
    {
        "name": "Hội An Ancient Town Night Run",
        "description": "A unique evening run through the UNESCO World Heritage streets of Hội An, lit by hundreds of lanterns.",
        "location": "Hội An, Quảng Nam",
        "city": "Hội An",
        "country": "Vietnam",
        "latitude": 15.8801,
        "longitude": 108.3380,
        "terrain_type": "road",
        "difficulty_level": "easy",
        "elevation_gain_m": 10,
        "is_certified": False,
        "event_start_date": date(2026, 4, 4),
        "base_price": 300_000,
        "status": "registration_open",
        "categories": [
            {"name": "10K Night Run", "distance_km": 10, "price": 350_000, "cutoff_time_minutes": 120},
            {"name": "5K Fun Run", "distance_km": 5, "price": 200_000, "cutoff_time_minutes": 90},
        ],
    },
    {
        "name": "Nha Trang Bay Run",
        "description": "A scenic coastal run along Nha Trang's famous beachfront with views of islands and turquoise water.",
        "location": "Nha Trang, Khánh Hòa",
        "city": "Nha Trang",
        "country": "Vietnam",
        "latitude": 12.2388,
        "longitude": 109.1967,
        "terrain_type": "road",
        "difficulty_level": "easy",
        "elevation_gain_m": 40,
        "is_certified": True,
        "event_start_date": date(2026, 6, 7),
        "base_price": 450_000,
        "status": "published",
        "categories": [
            {"name": "21K", "distance_km": 21.1, "price": 600_000, "cutoff_time_minutes": 240},
            {"name": "10K", "distance_km": 10, "price": 400_000, "cutoff_time_minutes": 120},
        ],
    },
    {
        "name": "Phong Nha Cave Trail",
        "description": "Run through the UNESCO World Heritage karst landscape of Phong Nha-Kẻ Bàng National Park.",
        "location": "Phong Nha, Quảng Bình",
        "city": "Phong Nha",
        "country": "Vietnam",
        "latitude": 17.5920,
        "longitude": 106.2853,
        "terrain_type": "trail",
        "difficulty_level": "hard",
        "elevation_gain_m": 1800,
        "is_certified": False,
        "event_start_date": date(2026, 7, 18),
        "base_price": 700_000,
        "status": "published",
        "categories": [
            {"name": "50K", "distance_km": 50, "price": 1_000_000, "cutoff_time_minutes": 1200},
            {"name": "25K", "distance_km": 25, "price": 700_000, "cutoff_time_minutes": 600},
        ],
    },
    {
        "name": "Fansipan Vertical Race",
        "description": "Climb Indochina's highest peak (3143m) in this vertical race from Sa Pa town to the summit of Fansipan.",
        "location": "Sa Pa, Lào Cai",
        "city": "Sa Pa",
        "country": "Vietnam",
        "latitude": 22.3033,
        "longitude": 103.7756,
        "terrain_type": "trail",
        "difficulty_level": "extreme",
        "elevation_gain_m": 2800,
        "is_certified": False,
        "event_start_date": date(2026, 5, 30),
        "base_price": 1_500_000,
        "status": "published",
        "categories": [
            {"name": "Summit Attempt", "distance_km": 19, "price": 1_500_000, "cutoff_time_minutes": 480},
        ],
    },
    {
        "name": "Đà Nẵng International Marathon",
        "description": "Run along the iconic Dragon Bridge and Han River waterfront in Vietnam's most livable city.",
        "location": "Đà Nẵng",
        "city": "Đà Nẵng",
        "country": "Vietnam",
        "latitude": 16.0544,
        "longitude": 108.2022,
        "terrain_type": "road",
        "difficulty_level": "moderate",
        "elevation_gain_m": 80,
        "is_certified": True,
        "event_start_date": date(2026, 8, 2),
        "base_price": 600_000,
        "status": "registration_open",
        "categories": [
            {"name": "42K", "distance_km": 42.195, "price": 900_000, "cutoff_time_minutes": 360},
            {"name": "21K", "distance_km": 21.1, "price": 600_000, "cutoff_time_minutes": 210},
            {"name": "10K", "distance_km": 10, "price": 350_000, "cutoff_time_minutes": 120},
        ],
    },
    {
        "name": "Mekong Delta River Run",
        "description": "A flat, scenic run through the lush Mekong Delta, crossing ancient bridges and passing floating markets.",
        "location": "Cần Thơ, Cần Thơ",
        "city": "Cần Thơ",
        "country": "Vietnam",
        "latitude": 10.0452,
        "longitude": 105.7469,
        "terrain_type": "road",
        "difficulty_level": "easy",
        "elevation_gain_m": 15,
        "is_certified": False,
        "event_start_date": date(2026, 12, 13),
        "base_price": 300_000,
        "status": "published",
        "categories": [
            {"name": "21K", "distance_km": 21.1, "price": 500_000, "cutoff_time_minutes": 240},
            {"name": "10K", "distance_km": 10, "price": 300_000, "cutoff_time_minutes": 120},
        ],
    },
    {
        "name": "Hà Giang Loop Trail",
        "description": "Explore the rugged, remote northern highlands on this multi-day ultra trail through the Đồng Văn Karst Plateau Geopark.",
        "location": "Đồng Văn, Hà Giang",
        "city": "Đồng Văn",
        "country": "Vietnam",
        "latitude": 23.2744,
        "longitude": 105.3592,
        "terrain_type": "trail",
        "difficulty_level": "extreme",
        "elevation_gain_m": 6000,
        "is_certified": False,
        "event_start_date": date(2026, 10, 24),
        "base_price": 2_000_000,
        "status": "published",
        "categories": [
            {"name": "150K Ultra", "distance_km": 150, "price": 3_000_000, "cutoff_time_minutes": 4800},
            {"name": "70K", "distance_km": 70, "price": 2_000_000, "cutoff_time_minutes": 2000},
        ],
    },
    {
        "name": "Huế Imperial City Run",
        "description": "A heritage run through the ancient imperial capital, starting at the Citadel walls and weaving through royal gardens.",
        "location": "Huế, Thừa Thiên Huế",
        "city": "Huế",
        "country": "Vietnam",
        "latitude": 16.4637,
        "longitude": 107.5909,
        "terrain_type": "road",
        "difficulty_level": "easy",
        "elevation_gain_m": 25,
        "is_certified": False,
        "event_start_date": date(2026, 3, 22),
        "base_price": 250_000,
        "status": "registration_open",
        "categories": [
            {"name": "10K", "distance_km": 10, "price": 300_000, "cutoff_time_minutes": 120},
            {"name": "5K Heritage Walk/Run", "distance_km": 5, "price": 150_000, "cutoff_time_minutes": 90},
        ],
    },
    {
        "name": "Bidoup Núi Bà Trail Race",
        "description": "Technical trail race through Bidoup-Núi Bà National Park, home to rare wildlife and towering primeval forests.",
        "location": "Đà Lạt, Lâm Đồng",
        "city": "Đà Lạt",
        "country": "Vietnam",
        "latitude": 12.1667,
        "longitude": 108.7000,
        "terrain_type": "trail",
        "difficulty_level": "hard",
        "elevation_gain_m": 2200,
        "is_certified": False,
        "event_start_date": date(2026, 6, 27),
        "base_price": 700_000,
        "status": "published",
        "categories": [
            {"name": "50K", "distance_km": 50, "price": 1_100_000, "cutoff_time_minutes": 1200},
            {"name": "25K", "distance_km": 25, "price": 700_000, "cutoff_time_minutes": 600},
            {"name": "12K", "distance_km": 12, "price": 400_000, "cutoff_time_minutes": 240},
        ],
    },
    {
        "name": "Long Biên Half Marathon",
        "description": "A fast, flat race across the iconic Long Biên Bridge spanning the Red River in Hà Nội.",
        "location": "Hà Nội",
        "city": "Hà Nội",
        "country": "Vietnam",
        "latitude": 21.0459,
        "longitude": 105.8671,
        "terrain_type": "road",
        "difficulty_level": "moderate",
        "elevation_gain_m": 30,
        "is_certified": False,
        "event_start_date": date(2026, 3, 8),
        "base_price": 400_000,
        "status": "registration_open",
        "categories": [
            {"name": "21K", "distance_km": 21.1, "price": 500_000, "cutoff_time_minutes": 240},
            {"name": "10K", "distance_km": 10, "price": 350_000, "cutoff_time_minutes": 120},
        ],
    },
    {
        "name": "Bà Nà Hills Trail Challenge",
        "description": "Run on the trails surrounding the famous Bà Nà Hills resort area with its legendary Golden Bridge and French village.",
        "location": "Đà Nẵng",
        "city": "Đà Nẵng",
        "country": "Vietnam",
        "latitude": 15.9978,
        "longitude": 107.9877,
        "terrain_type": "trail",
        "difficulty_level": "hard",
        "elevation_gain_m": 1500,
        "is_certified": False,
        "event_start_date": date(2026, 4, 18),
        "base_price": 800_000,
        "status": "published",
        "categories": [
            {"name": "30K", "distance_km": 30, "price": 900_000, "cutoff_time_minutes": 720},
            {"name": "15K", "distance_km": 15, "price": 600_000, "cutoff_time_minutes": 360},
        ],
    },
    {
        "name": "Côn Đảo Island Race",
        "description": "A rare racing experience on the remote Côn Đảo archipelago, known for its pristine beaches and historical significance.",
        "location": "Côn Đảo, Bà Rịa-Vũng Tàu",
        "city": "Côn Đảo",
        "country": "Vietnam",
        "latitude": 8.6833,
        "longitude": 106.6000,
        "terrain_type": "mixed",
        "difficulty_level": "moderate",
        "elevation_gain_m": 400,
        "is_certified": False,
        "event_start_date": date(2026, 11, 28),
        "base_price": 1_200_000,
        "status": "published",
        "categories": [
            {"name": "21K", "distance_km": 21.1, "price": 1_200_000, "cutoff_time_minutes": 300},
            {"name": "10K", "distance_km": 10, "price": 800_000, "cutoff_time_minutes": 150},
        ],
    },
    {
        "name": "Tam Đảo Mountain Climb",
        "description": "A classic mountain run from Tam Đảo town up the cloud forest ridge above Vĩnh Phúc province.",
        "location": "Tam Đảo, Vĩnh Phúc",
        "city": "Tam Đảo",
        "country": "Vietnam",
        "latitude": 21.4667,
        "longitude": 105.6500,
        "terrain_type": "trail",
        "difficulty_level": "hard",
        "elevation_gain_m": 900,
        "is_certified": False,
        "event_start_date": date(2026, 9, 6),
        "base_price": 500_000,
        "status": "published",
        "categories": [
            {"name": "22K Trail", "distance_km": 22, "price": 650_000, "cutoff_time_minutes": 480},
            {"name": "11K Trail", "distance_km": 11, "price": 400_000, "cutoff_time_minutes": 240},
        ],
    },
    {
        "name": "Phan Thiết Beach Race",
        "description": "Race along the sandy beaches and red sand dunes of Phan Thiết, Vietnam's kite-surfing capital.",
        "location": "Phan Thiết, Bình Thuận",
        "city": "Phan Thiết",
        "country": "Vietnam",
        "latitude": 10.9281,
        "longitude": 108.1030,
        "terrain_type": "mixed",
        "difficulty_level": "moderate",
        "elevation_gain_m": 50,
        "is_certified": False,
        "event_start_date": date(2026, 7, 4),
        "base_price": 400_000,
        "status": "published",
        "categories": [
            {"name": "21K", "distance_km": 21.1, "price": 550_000, "cutoff_time_minutes": 270},
            {"name": "10K", "distance_km": 10, "price": 350_000, "cutoff_time_minutes": 130},
        ],
    },
    {
        "name": "Sóc Sơn Forest Trail",
        "description": "A beginner-friendly forest trail race in the green lung north of Hà Nội, perfect for runners new to trail running.",
        "location": "Sóc Sơn, Hà Nội",
        "city": "Sóc Sơn",
        "country": "Vietnam",
        "latitude": 21.2378,
        "longitude": 105.8481,
        "terrain_type": "trail",
        "difficulty_level": "easy",
        "elevation_gain_m": 200,
        "is_certified": False,
        "event_start_date": date(2026, 4, 11),
        "base_price": 250_000,
        "status": "registration_open",
        "categories": [
            {"name": "12K Intro Trail", "distance_km": 12, "price": 300_000, "cutoff_time_minutes": 240},
            {"name": "6K Walk/Run", "distance_km": 6, "price": 150_000, "cutoff_time_minutes": 120},
        ],
    },
]


def main() -> None:
    with Session(engine) as session:
        # Get or create organizer user
        organizer = session.exec(select(User).where(User.is_superuser)).first()
        if organizer is None:
            print("ERROR: No superuser found. Run the app first to create the initial superuser.")
            sys.exit(1)

        created = 0
        skipped = 0
        for race_data in RACES:
            # Check if race already exists by name
            existing = session.exec(
                select(Race).where(Race.name == race_data["name"])
            ).first()
            if existing:
                skipped += 1
                continue

            categories_data = race_data.pop("categories", [])

            race_in = RaceCreate(
                name=race_data["name"],
                description=race_data.get("description"),
                location=race_data["location"],
                city=race_data.get("city"),
                country=race_data.get("country", "Vietnam"),
                latitude=race_data.get("latitude"),
                longitude=race_data.get("longitude"),
                terrain_type=race_data.get("terrain_type"),
                difficulty_level=race_data.get("difficulty_level"),
                elevation_gain_m=race_data.get("elevation_gain_m"),
                is_certified=race_data.get("is_certified", False),
                website_url=race_data.get("website_url"),
                event_start_date=race_data["event_start_date"],
                event_end_date=race_data.get("event_end_date"),
                base_price=race_data.get("base_price"),
                status=race_data.get("status", "published"),
            )

            race = crud.create_race(
                session=session,
                race_in=race_in,
                organizer_id=organizer.id,
            )

            for cat_data in categories_data:
                cat_in = RaceCategoryCreate(
                    name=cat_data["name"],
                    distance_km=cat_data.get("distance_km"),
                    price=cat_data.get("price"),
                    cutoff_time_minutes=cat_data.get("cutoff_time_minutes"),
                    race_id=race.id,
                )
                crud.create_race_category(session=session, category_in=cat_in)

            created += 1
            print(f"  Created: {race.name}")

        print(f"\nDone — {created} races created, {skipped} already existed.")


if __name__ == "__main__":
    main()
