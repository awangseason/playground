#!/usr/bin/env python3
"""Generate/package Scratch 3 .sb3 files for Solar System Guardian."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def md5_hex(content: str) -> str:
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def svg_rect(width: int, height: int, fill: str, label: str = "") -> str:
    text = ""
    if label:
        text = (
            f'<text x="{width/2}" y="{height/2}" '
            f'font-family="sans-serif" font-size="24" fill="#ffffff" '
            f'text-anchor="middle" dominant-baseline="middle">{label}</text>'
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="{fill}"/>{text}</svg>'
    )


# ── Planet SVGs (each 100×100, rotationCenter 50,50) ───────────────────────
def svg_planet_mercury() -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">'
        '<circle cx="50" cy="50" r="36" fill="#9e9e9e" stroke="#bdbdbd" stroke-width="2"/>'
        '<circle cx="34" cy="38" r="6" fill="#757575" opacity="0.7"/>'
        '<circle cx="61" cy="59" r="4" fill="#757575" opacity="0.6"/>'
        '<circle cx="44" cy="65" r="7" fill="#757575" opacity="0.5"/>'
        '<circle cx="63" cy="37" r="5" fill="#757575" opacity="0.6"/>'
        '</svg>'
    )

def svg_planet_venus() -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">'
        '<circle cx="50" cy="50" r="40" fill="#f9e04b" opacity="0.25"/>'
        '<circle cx="50" cy="50" r="36" fill="#f9a825" stroke="#fbc02d" stroke-width="2"/>'
        '<ellipse cx="44" cy="39" rx="18" ry="8" fill="#fbc02d" opacity="0.45"/>'
        '<ellipse cx="56" cy="63" rx="12" ry="5" fill="#e65100" opacity="0.3"/>'
        '</svg>'
    )

def svg_planet_earth() -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">'
        '<circle cx="50" cy="50" r="36" fill="#1565c0" stroke="#1976d2" stroke-width="2"/>'
        '<ellipse cx="40" cy="44" rx="14" ry="10" fill="#2e7d32" opacity="0.9"/>'
        '<ellipse cx="60" cy="55" rx="10" ry="8" fill="#2e7d32" opacity="0.9"/>'
        '<ellipse cx="34" cy="62" rx="8" ry="6" fill="#2e7d32" opacity="0.8"/>'
        '<ellipse cx="50" cy="17" rx="11" ry="4" fill="white" opacity="0.85"/>'
        '<ellipse cx="50" cy="83" rx="9" ry="3" fill="white" opacity="0.85"/>'
        '</svg>'
    )

def svg_planet_mars() -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">'
        '<circle cx="50" cy="50" r="36" fill="#c62828" stroke="#e53935" stroke-width="2"/>'
        '<ellipse cx="45" cy="56" rx="15" ry="9" fill="#b71c1c" opacity="0.5"/>'
        '<ellipse cx="50" cy="17" rx="10" ry="4" fill="white" opacity="0.9"/>'
        '</svg>'
    )

def svg_planet_jupiter() -> str:
    cid = "jc"
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">'
        f'<defs><clipPath id="{cid}"><circle cx="50" cy="50" r="38"/></clipPath></defs>'
        '<circle cx="50" cy="50" r="38" fill="#e65100"/>'
        f'<rect x="12" y="30" width="76" height="8" fill="#bf360c" opacity="0.65" clip-path="url(#{cid})"/>'
        f'<rect x="12" y="44" width="76" height="6" fill="#ffa726" opacity="0.5" clip-path="url(#{cid})"/>'
        f'<rect x="12" y="56" width="76" height="8" fill="#bf360c" opacity="0.65" clip-path="url(#{cid})"/>'
        f'<rect x="12" y="70" width="76" height="5" fill="#ffa726" opacity="0.4" clip-path="url(#{cid})"/>'
        f'<ellipse cx="60" cy="60" rx="8" ry="5" fill="#c62828" opacity="0.8" clip-path="url(#{cid})"/>'
        '<circle cx="50" cy="50" r="38" fill="none" stroke="#e64a19" stroke-width="2"/>'
        '</svg>'
    )

def svg_planet_saturn() -> str:
    cid = "sc"
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">'
        '<ellipse cx="50" cy="52" rx="44" ry="10" fill="none" stroke="#f9a825" stroke-width="6" opacity="0.55"/>'
        f'<defs><clipPath id="{cid}"><circle cx="50" cy="52" r="26"/></clipPath></defs>'
        '<circle cx="50" cy="52" r="26" fill="#f9a825" stroke="#fbc02d" stroke-width="2"/>'
        f'<rect x="24" y="47" width="52" height="5" fill="#e65100" opacity="0.35" clip-path="url(#{cid})"/>'
        f'<rect x="24" y="57" width="52" height="4" fill="#e65100" opacity="0.25" clip-path="url(#{cid})"/>'
        '<ellipse cx="50" cy="52" rx="44" ry="10" fill="none" stroke="#fbc02d" stroke-width="3" stroke-dasharray="138,138" stroke-dashoffset="69" opacity="0.75"/>'
        '</svg>'
    )

def svg_planet_uranus() -> str:
    cid = "uc"
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">'
        f'<defs><clipPath id="{cid}"><circle cx="50" cy="50" r="36"/></clipPath></defs>'
        '<circle cx="50" cy="50" r="36" fill="#80cbc4" stroke="#4db6ac" stroke-width="2"/>'
        f'<rect x="14" y="38" width="72" height="6" fill="#4db6ac" opacity="0.4" clip-path="url(#{cid})"/>'
        f'<rect x="14" y="56" width="72" height="5" fill="#4db6ac" opacity="0.3" clip-path="url(#{cid})"/>'
        '</svg>'
    )

def svg_planet_neptune() -> str:
    cid = "nc"
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">'
        f'<defs><clipPath id="{cid}"><circle cx="50" cy="50" r="36"/></clipPath></defs>'
        '<circle cx="50" cy="50" r="36" fill="#1565c0" stroke="#1976d2" stroke-width="2"/>'
        f'<ellipse cx="42" cy="55" rx="10" ry="6" fill="#0d47a1" opacity="0.8" clip-path="url(#{cid})"/>'
        f'<rect x="14" y="35" width="72" height="5" fill="#0d47a1" opacity="0.4" clip-path="url(#{cid})"/>'
        '</svg>'
    )

# ── Hero spaceship (50×28, rotationCenter 25,14) ────────────────────────────
def svg_hero_ship() -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="50" height="28" viewBox="0 0 50 28">'
        '<polygon points="2,14 40,4 40,24" fill="#78909c" stroke="#b0bec5" stroke-width="1.5"/>'
        '<circle cx="30" cy="14" r="6" fill="#e1f5fe" stroke="#81d4fa" stroke-width="1.5"/>'
        '<polygon points="40,9 50,12 50,16 40,19" fill="#ff7043" opacity="0.9"/>'
        '<polygon points="25,4 32,0 40,4" fill="#546e7a"/>'
        '<polygon points="25,24 32,28 40,24" fill="#546e7a"/>'
        '</svg>'
    )

# ── Trash SVGs (40×40) ───────────────────────────────────────────────────────
def svg_trash_rock() -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">'
        '<polygon points="20,5 35,12 38,28 25,38 10,35 5,20 12,8" fill="#78909c" stroke="#546e7a" stroke-width="1.5"/>'
        '<line x1="15" y1="12" x2="20" y2="22" stroke="#546e7a" stroke-width="1"/>'
        '<line x1="24" y1="15" x2="28" y2="28" stroke="#546e7a" stroke-width="1"/>'
        '</svg>'
    )

def svg_trash_can() -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">'
        '<rect x="10" y="12" width="20" height="24" rx="2" fill="#90a4ae" stroke="#607d8b" stroke-width="1.5"/>'
        '<rect x="7" y="8" width="26" height="6" rx="1" fill="#b0bec5" stroke="#607d8b" stroke-width="1"/>'
        '<rect x="16" y="3" width="8" height="6" rx="1" fill="#b0bec5" stroke="#607d8b" stroke-width="1"/>'
        '<line x1="17" y1="18" x2="17" y2="30" stroke="#607d8b" stroke-width="1.5"/>'
        '<line x1="23" y1="18" x2="23" y2="30" stroke="#607d8b" stroke-width="1.5"/>'
        '</svg>'
    )

def svg_trash_debris() -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">'
        '<polygon points="8,18 14,6 28,8 36,20 30,34 16,36 6,28" fill="#b0bec5" stroke="#78909c" stroke-width="1.5"/>'
        '<line x1="14" y1="14" x2="20" y2="20" stroke="#607d8b" stroke-width="1.5"/>'
        '<line x1="22" y1="12" x2="26" y2="24" stroke="#607d8b" stroke-width="1.5"/>'
        '<circle cx="20" cy="27" r="3" fill="#78909c"/>'
        '</svg>'
    )

# ── Full solar-system victory screen (480×360) ───────────────────────────────
def svg_full_solar_system() -> str:
    stars = ""
    pts = [(42,18),(91,44),(153,11),(210,67),(277,23),(332,55),(388,14),(441,78),
           (60,100),(118,130),(180,95),(245,140),(300,88),(360,120),(420,105),
           (30,160),(88,190),(145,172),(205,200),(265,175),(320,195),(378,165),
           (440,185),(55,230),(112,250),(170,235),(228,260),(285,240),(340,255),(397,232),(450,248),
           (20,290),(75,310),(133,295),(190,320),(248,300),(303,318),(358,295),(412,312),(465,296),
           (38,340),(95,352),(148,338),(200,355),(258,342),(315,356),(370,340),(425,350)]
    for x, y in pts:
        stars += f'<circle cx="{x}" cy="{y}" r="1.2" fill="white" opacity="0.7"/>'
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360" viewBox="0 0 480 360">'
        f'<rect width="480" height="360" fill="#030b1a"/>'
        f'{stars}'
        f'<text x="240" y="28" font-family="sans-serif" font-size="20" fill="#fff176" text-anchor="middle" font-weight="bold">Solar System Guardian</text>'
        f'<text x="240" y="50" font-family="sans-serif" font-size="13" fill="#b0bec5" text-anchor="middle">All 8 planets protected! \u2605</text>'
        f'<circle cx="28" cy="210" r="26" fill="#fdd835" opacity="0.3"/>'
        f'<circle cx="28" cy="210" r="22" fill="#fdd835"/>'
        f'<text x="28" y="244" font-family="sans-serif" font-size="8" fill="#fff9c4" text-anchor="middle">Sun</text>'
        f'<circle cx="80" cy="210" r="9" fill="#9e9e9e"/>'
        f'<text x="80" y="228" font-family="sans-serif" font-size="7" fill="#bdbdbd" text-anchor="middle">Mercury</text>'
        f'<circle cx="122" cy="210" r="13" fill="#f9a825"/>'
        f'<text x="122" y="232" font-family="sans-serif" font-size="7" fill="#fff9c4" text-anchor="middle">Venus</text>'
        f'<circle cx="168" cy="210" r="14" fill="#1565c0"/>'
        f'<ellipse cx="164" cy="206" rx="6" ry="4" fill="#2e7d32" opacity="0.9"/>'
        f'<text x="168" y="233" font-family="sans-serif" font-size="7" fill="#90caf9" text-anchor="middle">Earth</text>'
        f'<circle cx="212" cy="210" r="11" fill="#c62828"/>'
        f'<text x="212" y="230" font-family="sans-serif" font-size="7" fill="#ef9a9a" text-anchor="middle">Mars</text>'
        f'<circle cx="265" cy="210" r="22" fill="#e65100"/>'
        f'<rect x="243" y="205" width="44" height="5" fill="#bf360c" opacity="0.6"/>'
        f'<text x="265" y="242" font-family="sans-serif" font-size="7" fill="#ffccbc" text-anchor="middle">Jupiter</text>'
        f'<ellipse cx="328" cy="210" rx="30" ry="7" fill="none" stroke="#fbc02d" stroke-width="5" opacity="0.65"/>'
        f'<circle cx="328" cy="210" r="17" fill="#f9a825"/>'
        f'<ellipse cx="328" cy="210" rx="30" ry="7" fill="none" stroke="#fbc02d" stroke-width="3" stroke-dasharray="94,94" stroke-dashoffset="47" opacity="0.8"/>'
        f'<text x="328" y="236" font-family="sans-serif" font-size="7" fill="#fff9c4" text-anchor="middle">Saturn</text>'
        f'<circle cx="385" cy="210" r="13" fill="#80cbc4"/>'
        f'<text x="385" y="232" font-family="sans-serif" font-size="7" fill="#b2dfdb" text-anchor="middle">Uranus</text>'
        f'<circle cx="438" cy="210" r="12" fill="#1565c0"/>'
        f'<text x="438" y="231" font-family="sans-serif" font-size="7" fill="#90caf9" text-anchor="middle">Neptune</text>'
        f'</svg>'
    )


def write_assets(out_dir: Path) -> dict:
    assets = {
        "bg_space.svg": svg_rect(480, 360, "#030b1a", "Solar System Guardian"),
        "bg_full_solar_system.svg": svg_full_solar_system(),
        "hero.svg": svg_hero_ship(),
        "trash_1.svg": svg_trash_rock(),
        "trash_2.svg": svg_trash_can(),
        "trash_3.svg": svg_trash_debris(),
        "planet_mercury.svg": svg_planet_mercury(),
        "planet_venus.svg": svg_planet_venus(),
        "planet_earth.svg": svg_planet_earth(),
        "planet_mars.svg": svg_planet_mars(),
        "planet_jupiter.svg": svg_planet_jupiter(),
        "planet_saturn.svg": svg_planet_saturn(),
        "planet_uranus.svg": svg_planet_uranus(),
        "planet_neptune.svg": svg_planet_neptune(),
        "intro_board.svg": svg_rect(280, 90, "#1f2a44", ""),
    }
    asset_map = {}
    for name, content in assets.items():
        digest = md5_hex(content)
        new_name = f"{digest}.svg"
        write_text(out_dir / new_name, content)
        asset_map[name] = {
            "assetId": digest,
            "md5ext": new_name,
        }
    return asset_map


def normalize_project_assets(project: dict, asset_map: dict) -> None:
    for target in project.get("targets", []):
        for costume in target.get("costumes", []):
            old_md5ext = costume.get("md5ext", "")
            if old_md5ext in asset_map:
                costume["assetId"] = asset_map[old_md5ext]["assetId"]
                costume["md5ext"] = asset_map[old_md5ext]["md5ext"]


def make_template_project() -> dict:
    var_ids = {
        "Level": "var_level",
        "Blocked": "var_blocked",
        "Target": "var_target",
        "Remaining": "var_remaining",
        "PlanetHP": "var_hp",
        "Score": "var_score",
        "GameOn": "var_game_on",
        "SpawnGap": "var_spawn_gap",
        "TrashSpeed": "var_trash_speed",
    }
    list_ids = {
        "PlanetNames": "list_planet_names",
        "Targets": "list_targets",
        "Intros": "list_intros",
    }
    bc = {
        "bc_set_planet": "SetPlanet",
        "bc_show_intro": "ShowIntro",
        "bc_level_clear": "LevelClear",
        "bc_level_fail": "LevelFail",
        "bc_all_clear": "AllClear",
    }

    stage = {
        "isStage": True,
        "name": "Stage",
        "variables": {
            var_ids["Level"]: ["Level", 1],
            var_ids["Blocked"]: ["Blocked", 0],
            var_ids["Target"]: ["Target", 6],
            var_ids["Remaining"]: ["Remaining", 6],
            var_ids["PlanetHP"]: ["PlanetHP", 3],
            var_ids["Score"]: ["Score", 0],
            var_ids["GameOn"]: ["GameOn", 0],
            var_ids["SpawnGap"]: ["SpawnGap", 0.9],
            var_ids["TrashSpeed"]: ["TrashSpeed", 4],
        },
        "lists": {
            list_ids["PlanetNames"]: [
                "PlanetNames",
                ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"],
            ],
            list_ids["Targets"]: ["Targets", [6, 9, 12, 15, 18, 21, 24, 28]],
            list_ids["Intros"]: [
                "Intros",
                [
                    "The smallest planet and closest to the Sun.",
                    "The hottest planet with thick clouds.",
                    "Our blue world and home to life.",
                    "The red planet with giant volcanoes.",
                    "The largest planet with huge storms.",
                    "Famous for beautiful rings of ice and rock.",
                    "An icy giant that spins on its side.",
                    "The farthest planet, dark blue and windy.",
                ],
            ],
        },
        "broadcasts": bc,
        "blocks": {},
        "comments": {},
        "currentCostume": 0,
        "costumes": [
            {
                "assetId": "bg_space",
                "name": "Space",
                "md5ext": "bg_space.svg",
                "dataFormat": "svg",
                "rotationCenterX": 240,
                "rotationCenterY": 180,
            },
            {
                "assetId": "bg_full_solar_system",
                "name": "FullSolarSystem",
                "md5ext": "bg_full_solar_system.svg",
                "dataFormat": "svg",
                "rotationCenterX": 240,
                "rotationCenterY": 180,
            },
        ],
        "sounds": [],
        "volume": 100,
        "layerOrder": 0,
        "tempo": 60,
        "videoTransparency": 50,
        "videoState": "on",
        "textToSpeechLanguage": None,
    }

    hero = {
        "isStage": False,
        "name": "Hero",
        "variables": {},
        "lists": {},
        "broadcasts": {},
        "blocks": {},
        "comments": {},
        "currentCostume": 0,
        "costumes": [
            {
                "assetId": "hero",
                "name": "Hero",
                "md5ext": "hero.svg",
                "dataFormat": "svg",
                "rotationCenterX": 25,
                "rotationCenterY": 14,
            }
        ],
        "sounds": [],
        "volume": 100,
        "layerOrder": 1,
        "visible": True,
        "x": -120,
        "y": 0,
        "size": 100,
        "direction": 90,
        "draggable": False,
        "rotationStyle": "left-right",
    }

    trash = {
        "isStage": False,
        "name": "Trash",
        "variables": {},
        "lists": {},
        "broadcasts": {},
        "blocks": {},
        "comments": {},
        "currentCostume": 0,
        "costumes": [
            {
                "assetId": "trash_1",
                "name": "Bottle",
                "md5ext": "trash_1.svg",
                "dataFormat": "svg",
                "rotationCenterX": 24,
                "rotationCenterY": 24,
            },
            {
                "assetId": "trash_2",
                "name": "Can",
                "md5ext": "trash_2.svg",
                "dataFormat": "svg",
                "rotationCenterX": 24,
                "rotationCenterY": 24,
            },
            {
                "assetId": "trash_3",
                "name": "Bag",
                "md5ext": "trash_3.svg",
                "dataFormat": "svg",
                "rotationCenterX": 24,
                "rotationCenterY": 24,
            },
        ],
        "sounds": [],
        "volume": 100,
        "layerOrder": 2,
        "visible": False,
        "x": 240,
        "y": 0,
        "size": 100,
        "direction": -90,
        "draggable": False,
        "rotationStyle": "all around",
    }

    planet = {
        "isStage": False,
        "name": "Planet",
        "variables": {},
        "lists": {},
        "broadcasts": {},
        "blocks": {},
        "comments": {},
        "currentCostume": 0,
        "costumes": [
            {"assetId": "planet_mercury", "name": "Mercury", "md5ext": "planet_mercury.svg", "dataFormat": "svg", "rotationCenterX": 50, "rotationCenterY": 50},
            {"assetId": "planet_venus", "name": "Venus", "md5ext": "planet_venus.svg", "dataFormat": "svg", "rotationCenterX": 50, "rotationCenterY": 50},
            {"assetId": "planet_earth", "name": "Earth", "md5ext": "planet_earth.svg", "dataFormat": "svg", "rotationCenterX": 50, "rotationCenterY": 50},
            {"assetId": "planet_mars", "name": "Mars", "md5ext": "planet_mars.svg", "dataFormat": "svg", "rotationCenterX": 50, "rotationCenterY": 50},
            {"assetId": "planet_jupiter", "name": "Jupiter", "md5ext": "planet_jupiter.svg", "dataFormat": "svg", "rotationCenterX": 50, "rotationCenterY": 50},
            {"assetId": "planet_saturn", "name": "Saturn", "md5ext": "planet_saturn.svg", "dataFormat": "svg", "rotationCenterX": 50, "rotationCenterY": 50},
            {"assetId": "planet_uranus", "name": "Uranus", "md5ext": "planet_uranus.svg", "dataFormat": "svg", "rotationCenterX": 50, "rotationCenterY": 50},
            {"assetId": "planet_neptune", "name": "Neptune", "md5ext": "planet_neptune.svg", "dataFormat": "svg", "rotationCenterX": 50, "rotationCenterY": 50},
        ],
        "sounds": [],
        "volume": 100,
        "layerOrder": 3,
        "visible": True,
        "x": -200,
        "y": 0,
        "size": 100,
        "direction": 90,
        "draggable": False,
        "rotationStyle": "all around",
    }

    intro = {
        "isStage": False,
        "name": "IntroBoard",
        "variables": {},
        "lists": {},
        "broadcasts": {},
        "blocks": {},
        "comments": {},
        "currentCostume": 0,
        "costumes": [
            {
                "assetId": "intro_board",
                "name": "Intro",
                "md5ext": "intro_board.svg",
                "dataFormat": "svg",
                "rotationCenterX": 140,
                "rotationCenterY": 45,
            }
        ],
        "sounds": [],
        "volume": 100,
        "layerOrder": 4,
        "visible": False,
        "x": 155,
        "y": -140,
        "size": 100,
        "direction": 90,
        "draggable": False,
        "rotationStyle": "all around",
    }

    return {
        "targets": [stage, hero, trash, planet, intro],
        "monitors": [
            {"id": "var_level", "mode": "default", "opcode": "data_variable",
             "params": {"VARIABLE": "Level"}, "spriteName": None, "value": 1,
             "width": 0, "height": 0, "x": 5, "y": 5, "visible": True,
             "sliderMin": 0, "sliderMax": 10, "isDiscrete": True},
            {"id": "var_remaining", "mode": "default", "opcode": "data_variable",
             "params": {"VARIABLE": "Remaining"}, "spriteName": None, "value": 6,
             "width": 0, "height": 0, "x": 5, "y": 30, "visible": True,
             "sliderMin": 0, "sliderMax": 30, "isDiscrete": True},
            {"id": "var_score", "mode": "default", "opcode": "data_variable",
             "params": {"VARIABLE": "Score"}, "spriteName": None, "value": 0,
             "width": 0, "height": 0, "x": 5, "y": 55, "visible": True,
             "sliderMin": 0, "sliderMax": 200, "isDiscrete": True},
        ],
        "extensions": [],
        "meta": {"semver": "3.0.0", "vm": "0.2.0", "agent": "Python builder"},
    }


def make_playable_project() -> dict:
    project = make_template_project()

    # ── STAGE ────────────────────────────────────────────────────────────────
    # Flag → bg → score=0 → level=1 → repeat_until(Level>8):
    #   reset blocked/hp → set Target from list → set Remaining=Target
    #   → broadcast SetPlanet → broadcastandwait ShowIntro (waits for intro to finish)
    #   → GameOn=1 → wait 10s → GameOn=0 → Level++
    # → switch to FullSolarSystem → broadcast AllClear
    stage = project["targets"][0]
    sb = {}

    sb["s_top"] = {"opcode": "event_whenflagclicked", "next": "s_bg", "parent": None,
                   "inputs": {}, "fields": {}, "shadow": False, "topLevel": True, "x": 20, "y": 20}
    sb["s_bg"] = {"opcode": "looks_switchbackdropto", "next": "s_score", "parent": "s_top",
                  "inputs": {"BACKDROP": [1, [10, "Space"]]}, "fields": {}, "shadow": False, "topLevel": False}
    sb["s_score"] = {"opcode": "data_setvariableto", "next": "s_level", "parent": "s_bg",
                     "inputs": {"VALUE": [1, [4, "0"]]}, "fields": {"VARIABLE": ["Score", "var_score"]},
                     "shadow": False, "topLevel": False}
    sb["s_level"] = {"opcode": "data_setvariableto", "next": "s_loop", "parent": "s_score",
                     "inputs": {"VALUE": [1, [4, "1"]]}, "fields": {"VARIABLE": ["Level", "var_level"]},
                     "shadow": False, "topLevel": False}
    # repeat until (Level > 8)
    sb["s_loop"] = {"opcode": "control_repeat_until", "next": "s_full", "parent": "s_level",
                    "inputs": {"CONDITION": [2, "s_cond_gt"], "SUBSTACK": [2, "s_reset_blocked"]},
                    "fields": {}, "shadow": False, "topLevel": False}
    sb["s_cond_gt"] = {"opcode": "operator_gt", "next": None, "parent": "s_loop",
                       "inputs": {"OPERAND1": [3, "s_cond_var", [4, ""]], "OPERAND2": [1, [4, "8"]]},
                       "fields": {}, "shadow": False, "topLevel": False}
    sb["s_cond_var"] = {"opcode": "data_variable", "next": None, "parent": "s_cond_gt",
                        "inputs": {}, "fields": {"VARIABLE": ["Level", "var_level"]},
                        "shadow": False, "topLevel": False}
    # loop body
    sb["s_reset_blocked"] = {"opcode": "data_setvariableto", "next": "s_reset_hp", "parent": "s_loop",
                              "inputs": {"VALUE": [1, [4, "0"]]}, "fields": {"VARIABLE": ["Blocked", "var_blocked"]},
                              "shadow": False, "topLevel": False}
    sb["s_reset_hp"] = {"opcode": "data_setvariableto", "next": "s_target", "parent": "s_reset_blocked",
                        "inputs": {"VALUE": [1, [4, "3"]]}, "fields": {"VARIABLE": ["PlanetHP", "var_hp"]},
                        "shadow": False, "topLevel": False}
    # Target = item(Level) of Targets list → [6,9,12,15,18,21,24,28]
    sb["s_target"] = {"opcode": "data_setvariableto", "next": "s_remaining", "parent": "s_reset_hp",
                      "inputs": {"VALUE": [3, "s_target_item", [4, "6"]]},
                      "fields": {"VARIABLE": ["Target", "var_target"]},
                      "shadow": False, "topLevel": False}
    sb["s_target_item"] = {"opcode": "data_itemoflist", "next": None, "parent": "s_target",
                           "inputs": {"INDEX": [3, "s_lft", [4, "1"]]},
                           "fields": {"LIST": ["Targets", "list_targets"]},
                           "shadow": False, "topLevel": False}
    sb["s_lft"] = {"opcode": "data_variable", "next": None, "parent": "s_target_item",
                   "inputs": {}, "fields": {"VARIABLE": ["Level", "var_level"]},
                   "shadow": False, "topLevel": False}
    # set Remaining = Target
    sb["s_remaining"] = {"opcode": "data_setvariableto", "next": "s_spawn", "parent": "s_target",
                         "inputs": {"VALUE": [3, "s_tref", [4, "0"]]},
                         "fields": {"VARIABLE": ["Remaining", "var_remaining"]},
                         "shadow": False, "topLevel": False}
    sb["s_tref"] = {"opcode": "data_variable", "next": None, "parent": "s_remaining",
                    "inputs": {}, "fields": {"VARIABLE": ["Target", "var_target"]},
                    "shadow": False, "topLevel": False}
    sb["s_spawn"] = {"opcode": "data_setvariableto", "next": "s_speed", "parent": "s_remaining",
                     "inputs": {"VALUE": [1, [4, "0.6"]]}, "fields": {"VARIABLE": ["SpawnGap", "var_spawn_gap"]},
                     "shadow": False, "topLevel": False}
    sb["s_speed"] = {"opcode": "data_setvariableto", "next": "s_setplanet", "parent": "s_spawn",
                     "inputs": {"VALUE": [1, [4, "5"]]}, "fields": {"VARIABLE": ["TrashSpeed", "var_trash_speed"]},
                     "shadow": False, "topLevel": False}
    sb["s_setplanet"] = {"opcode": "event_broadcast", "next": "s_intro", "parent": "s_speed",
                         "inputs": {"BROADCAST_INPUT": [1, "s_setplanet_menu"]},
                         "fields": {}, "shadow": False, "topLevel": False}
    sb["s_setplanet_menu"] = {"opcode": "event_broadcast_menu", "next": None, "parent": "s_setplanet",
                               "inputs": {}, "fields": {"BROADCAST_OPTION": ["SetPlanet", "bc_set_planet"]},
                               "shadow": True, "topLevel": False}
    # broadcastandwait — stage waits until intro say-blocks finish before GameOn=1
    sb["s_intro"] = {"opcode": "event_broadcastandwait", "next": "s_game_on", "parent": "s_setplanet",
                     "inputs": {"BROADCAST_INPUT": [1, "s_intro_menu"]},
                     "fields": {}, "shadow": False, "topLevel": False}
    sb["s_intro_menu"] = {"opcode": "event_broadcast_menu", "next": None, "parent": "s_intro",
                           "inputs": {}, "fields": {"BROADCAST_OPTION": ["ShowIntro", "bc_show_intro"]},
                           "shadow": True, "topLevel": False}
    sb["s_game_on"] = {"opcode": "data_setvariableto", "next": "s_wait", "parent": "s_intro",
                       "inputs": {"VALUE": [1, [4, "1"]]}, "fields": {"VARIABLE": ["GameOn", "var_game_on"]},
                       "shadow": False, "topLevel": False}
    sb["s_wait"] = {"opcode": "control_wait", "next": "s_game_off", "parent": "s_game_on",
                    "inputs": {"DURATION": [1, [4, "8"]]}, "fields": {}, "shadow": False, "topLevel": False}
    sb["s_game_off"] = {"opcode": "data_setvariableto", "next": "s_levelup", "parent": "s_wait",
                        "inputs": {"VALUE": [1, [4, "0"]]}, "fields": {"VARIABLE": ["GameOn", "var_game_on"]},
                        "shadow": False, "topLevel": False}
    sb["s_levelup"] = {"opcode": "data_changevariableby", "next": None, "parent": "s_game_off",
                       "inputs": {"VALUE": [1, [4, "1"]]}, "fields": {"VARIABLE": ["Level", "var_level"]},
                       "shadow": False, "topLevel": False}
    # after loop → full solar system → AllClear
    sb["s_full"] = {"opcode": "looks_switchbackdropto", "next": "s_all", "parent": "s_loop",
                    "inputs": {"BACKDROP": [1, [10, "FullSolarSystem"]]}, "fields": {}, "shadow": False, "topLevel": False}
    sb["s_all"] = {"opcode": "event_broadcast", "next": None, "parent": "s_full",
                   "inputs": {"BROADCAST_INPUT": [1, "s_all_menu"]}, "fields": {}, "shadow": False, "topLevel": False}
    sb["s_all_menu"] = {"opcode": "event_broadcast_menu", "next": None, "parent": "s_all",
                        "inputs": {}, "fields": {"BROADCAST_OPTION": ["AllClear", "bc_all_clear"]},
                        "shadow": True, "topLevel": False}
    stage["blocks"] = sb

    # ── HERO ─────────────────────────────────────────────────────────────────
    # Flag → show → goto(-120,0) → forever [ if ↑ pressed: y+6 | if ↓ pressed: y-6 ]
    hero = project["targets"][1]
    hero["blocks"] = {
        "h_top": {"opcode": "event_whenflagclicked", "next": "h_show", "parent": None,
                  "inputs": {}, "fields": {}, "shadow": False, "topLevel": True, "x": 20, "y": 20},
        "h_show": {"opcode": "looks_show", "next": "h_goto", "parent": "h_top",
                   "inputs": {}, "fields": {}, "shadow": False, "topLevel": False},
        "h_goto": {"opcode": "motion_gotoxy", "next": "h_forever", "parent": "h_show",
                   "inputs": {"X": [1, [4, "-120"]], "Y": [1, [4, "0"]]},
                   "fields": {}, "shadow": False, "topLevel": False},
        "h_forever": {"opcode": "control_forever", "next": None, "parent": "h_goto",
                      "inputs": {"SUBSTACK": [2, "h_if_up"]},
                      "fields": {}, "shadow": False, "topLevel": False},
        # if up arrow pressed → change y by 6
        "h_if_up": {"opcode": "control_if", "next": "h_if_down", "parent": "h_forever",
                    "inputs": {"CONDITION": [2, "h_key_up"], "SUBSTACK": [2, "h_move_up"]},
                    "fields": {}, "shadow": False, "topLevel": False},
        "h_key_up": {"opcode": "sensing_keypressed", "next": None, "parent": "h_if_up",
                     "inputs": {"KEY_OPTION": [1, "h_key_up_menu"]},
                     "fields": {}, "shadow": False, "topLevel": False},
        "h_key_up_menu": {"opcode": "sensing_keyoptions", "next": None, "parent": "h_key_up",
                          "inputs": {}, "fields": {"KEY_OPTION": ["up arrow", None]},
                          "shadow": True, "topLevel": False},
        "h_move_up": {"opcode": "motion_changeyby", "next": None, "parent": "h_if_up",
                      "inputs": {"DY": [1, [4, "6"]]}, "fields": {}, "shadow": False, "topLevel": False},
        # if down arrow pressed → change y by -6
        "h_if_down": {"opcode": "control_if", "next": None, "parent": "h_if_up",
                      "inputs": {"CONDITION": [2, "h_key_down"], "SUBSTACK": [2, "h_move_down"]},
                      "fields": {}, "shadow": False, "topLevel": False},
        "h_key_down": {"opcode": "sensing_keypressed", "next": None, "parent": "h_if_down",
                       "inputs": {"KEY_OPTION": [1, "h_key_down_menu"]},
                       "fields": {}, "shadow": False, "topLevel": False},
        "h_key_down_menu": {"opcode": "sensing_keyoptions", "next": None, "parent": "h_key_down",
                            "inputs": {}, "fields": {"KEY_OPTION": ["down arrow", None]},
                            "shadow": True, "topLevel": False},
        "h_move_down": {"opcode": "motion_changeyby", "next": None, "parent": "h_if_down",
                        "inputs": {"DY": [1, [4, "-6"]]}, "fields": {}, "shadow": False, "topLevel": False},
    }

    # ── TRASH ────────────────────────────────────────────────────────────────
    # Flag → hide → forever [ if GameOn=1: wait(SpawnGap) → clone ]
    # Clone start → random costume(1-3) → goto(240, random Y -140..140)
    #            → repeat 70 [ move x-5 ] → delete clone
    trash = project["targets"][2]
    trash["blocks"] = {
        "t_top": {"opcode": "event_whenflagclicked", "next": "t_hide", "parent": None,
                  "inputs": {}, "fields": {}, "shadow": False, "topLevel": True, "x": 20, "y": 20},
        "t_hide": {"opcode": "looks_hide", "next": "t_forever", "parent": "t_top",
                   "inputs": {}, "fields": {}, "shadow": False, "topLevel": False},
        "t_forever": {"opcode": "control_forever", "next": None, "parent": "t_hide",
                      "inputs": {"SUBSTACK": [2, "t_if_on"]},
                      "fields": {}, "shadow": False, "topLevel": False},
        # if GameOn = 1
        "t_if_on": {"opcode": "control_if", "next": None, "parent": "t_forever",
                    "inputs": {"CONDITION": [2, "t_game_eq"], "SUBSTACK": [2, "t_wait"]},
                    "fields": {}, "shadow": False, "topLevel": False},
        "t_game_eq": {"opcode": "operator_equals", "next": None, "parent": "t_if_on",
                      "inputs": {"OPERAND1": [3, "t_game_var", [4, ""]], "OPERAND2": [1, [4, "1"]]},
                      "fields": {}, "shadow": False, "topLevel": False},
        "t_game_var": {"opcode": "data_variable", "next": None, "parent": "t_game_eq",
                       "inputs": {}, "fields": {"VARIABLE": ["GameOn", "var_game_on"]},
                       "shadow": False, "topLevel": False},
        "t_wait": {"opcode": "control_wait", "next": "t_clone", "parent": "t_if_on",
                   "inputs": {"DURATION": [3, "t_spawn_var", [4, "0.6"]]},
                   "fields": {}, "shadow": False, "topLevel": False},
        "t_spawn_var": {"opcode": "data_variable", "next": None, "parent": "t_wait",
                        "inputs": {}, "fields": {"VARIABLE": ["SpawnGap", "var_spawn_gap"]},
                        "shadow": False, "topLevel": False},
        "t_clone": {"opcode": "control_create_clone_of", "next": None, "parent": "t_wait",
                    "inputs": {"CLONE_OPTION": [1, "t_clone_menu"]},
                    "fields": {}, "shadow": False, "topLevel": False},
        "t_clone_menu": {"opcode": "control_create_clone_of_menu", "next": None, "parent": "t_clone",
                         "inputs": {}, "fields": {"CLONE_OPTION": ["_myself_", None]},
                         "shadow": True, "topLevel": False},
        # clone start
        "t_clone_start": {"opcode": "control_start_as_clone", "next": "t_costume", "parent": None,
                          "inputs": {}, "fields": {}, "shadow": False, "topLevel": True, "x": 20, "y": 260},
        # pick random costume 1–3
        "t_costume": {"opcode": "looks_switchcostumeto", "next": "t_show", "parent": "t_clone_start",
                      "inputs": {"COSTUME": [3, "t_costume_rand", [4, "1"]]},
                      "fields": {}, "shadow": False, "topLevel": False},
        "t_costume_rand": {"opcode": "operator_random", "next": None, "parent": "t_costume",
                           "inputs": {"FROM": [1, [4, "1"]], "TO": [1, [4, "3"]]},
                           "fields": {}, "shadow": False, "topLevel": False},
        "t_show": {"opcode": "looks_show", "next": "t_goto", "parent": "t_costume",
                   "inputs": {}, "fields": {}, "shadow": False, "topLevel": False},
        # goto X=240, Y=random -140..140
        "t_goto": {"opcode": "motion_gotoxy", "next": "t_repeat", "parent": "t_show",
                   "inputs": {"X": [1, [4, "240"]], "Y": [3, "t_rand_y", [4, "0"]]},
                   "fields": {}, "shadow": False, "topLevel": False},
        "t_rand_y": {"opcode": "operator_random", "next": None, "parent": "t_goto",
                     "inputs": {"FROM": [1, [4, "-140"]], "TO": [1, [4, "140"]]},
                     "fields": {}, "shadow": False, "topLevel": False},
        "t_repeat": {"opcode": "control_repeat", "next": "t_del", "parent": "t_goto",
                     "inputs": {"TIMES": [1, [4, "70"]], "SUBSTACK": [2, "t_move"]},
                     "fields": {}, "shadow": False, "topLevel": False},
        "t_move": {"opcode": "motion_changexby", "next": "t_check_hero", "parent": "t_repeat",
                   "inputs": {"DX": [1, [4, "-5"]]}, "fields": {}, "shadow": False, "topLevel": False},
        # Each step: check if touching Hero → score++, Blocked++, Remaining--, delete clone
        "t_check_hero": {"opcode": "control_if", "next": None, "parent": "t_move",
                         "inputs": {"CONDITION": [2, "t_touching_hero"], "SUBSTACK": [2, "t_add_score"]},
                         "fields": {}, "shadow": False, "topLevel": False},
        "t_touching_hero": {"opcode": "sensing_touchingobject", "next": None, "parent": "t_check_hero",
                            "inputs": {"TOUCHINGOBJECTMENU": [1, "t_touching_menu"]},
                            "fields": {}, "shadow": False, "topLevel": False},
        "t_touching_menu": {"opcode": "sensing_touchingobjectmenu", "next": None, "parent": "t_touching_hero",
                            "inputs": {}, "fields": {"TOUCHINGOBJECTMENU": ["Hero", None]},
                            "shadow": True, "topLevel": False},
        "t_add_score": {"opcode": "data_changevariableby", "next": "t_add_blocked", "parent": "t_check_hero",
                        "inputs": {"VALUE": [1, [4, "1"]]}, "fields": {"VARIABLE": ["Score", "var_score"]},
                        "shadow": False, "topLevel": False},
        "t_add_blocked": {"opcode": "data_changevariableby", "next": "t_dec_remaining", "parent": "t_add_score",
                          "inputs": {"VALUE": [1, [4, "1"]]}, "fields": {"VARIABLE": ["Blocked", "var_blocked"]},
                          "shadow": False, "topLevel": False},
        "t_dec_remaining": {"opcode": "data_changevariableby", "next": "t_delete_on_hit", "parent": "t_add_blocked",
                            "inputs": {"VALUE": [1, [4, "-1"]]}, "fields": {"VARIABLE": ["Remaining", "var_remaining"]},
                            "shadow": False, "topLevel": False},
        "t_delete_on_hit": {"opcode": "control_delete_this_clone", "next": None, "parent": "t_dec_remaining",
                            "inputs": {}, "fields": {}, "shadow": False, "topLevel": False},
        "t_del": {"opcode": "control_delete_this_clone", "next": None, "parent": "t_repeat",
                  "inputs": {}, "fields": {}, "shadow": False, "topLevel": False},
    }

    # ── PLANET ───────────────────────────────────────────────────────────────
    # Flag → show → goto(-200,0)
    # On SetPlanet → switch costume to item(Level) of PlanetNames  (Mercury/Venus/…)
    planet = project["targets"][3]
    planet["blocks"] = {
        "p_top": {"opcode": "event_whenflagclicked", "next": "p_show", "parent": None,
                  "inputs": {}, "fields": {}, "shadow": False, "topLevel": True, "x": 20, "y": 20},
        "p_show": {"opcode": "looks_show", "next": "p_goto", "parent": "p_top",
                   "inputs": {}, "fields": {}, "shadow": False, "topLevel": False},
        "p_goto": {"opcode": "motion_gotoxy", "next": None, "parent": "p_show",
                   "inputs": {"X": [1, [4, "-200"]], "Y": [1, [4, "0"]]},
                   "fields": {}, "shadow": False, "topLevel": False},
        # SetPlanet → switch costume to planet name from list
        "p_set_recv": {"opcode": "event_whenbroadcastreceived", "next": "p_set_costume", "parent": None,
                       "inputs": {}, "fields": {"BROADCAST_OPTION": ["SetPlanet", "bc_set_planet"]},
                       "shadow": False, "topLevel": True, "x": 20, "y": 220},
        "p_set_costume": {"opcode": "looks_switchcostumeto", "next": None, "parent": "p_set_recv",
                          "inputs": {"COSTUME": [3, "p_costume_name", [4, "1"]]},
                          "fields": {}, "shadow": False, "topLevel": False},
        # item (Level) of PlanetNames  → e.g. "Mercury" on level 1
        "p_costume_name": {"opcode": "data_itemoflist", "next": None, "parent": "p_set_costume",
                           "inputs": {"INDEX": [3, "p_level_var", [4, "1"]]},
                           "fields": {"LIST": ["PlanetNames", "list_planet_names"]},
                           "shadow": False, "topLevel": False},
        "p_level_var": {"opcode": "data_variable", "next": None, "parent": "p_costume_name",
                        "inputs": {}, "fields": {"VARIABLE": ["Level", "var_level"]},
                        "shadow": False, "topLevel": False},
        # AllClear → hide planet before full solar-system screen
        "p_all_recv": {"opcode": "event_whenbroadcastreceived", "next": "p_all_hide", "parent": None,
                       "inputs": {}, "fields": {"BROADCAST_OPTION": ["AllClear", "bc_all_clear"]},
                       "shadow": False, "topLevel": True, "x": 20, "y": 440},
        "p_all_hide": {"opcode": "looks_hide", "next": None, "parent": "p_all_recv",
                       "inputs": {}, "fields": {}, "shadow": False, "topLevel": False},
    }

    # ── INTRO BOARD ──────────────────────────────────────────────────────────
    intro = project["targets"][4]
    intro["blocks"] = {
        # Flag → hide board
        "i_top": {"opcode": "event_whenflagclicked", "next": "i_hide", "parent": None,
                  "inputs": {}, "fields": {}, "shadow": False, "topLevel": True, "x": 20, "y": 20},
        "i_hide": {"opcode": "looks_hide", "next": None, "parent": "i_top",
                   "inputs": {}, "fields": {}, "shadow": False, "topLevel": False},
        # ShowIntro → show board → persistent say("PlanetName: description") → wait 2.5s
        # broadcastandwait in Stage waits for this script to finish, then sets GameOn=1
        # The say bubble stays visible during gameplay (no hide at end)
        "i_recv": {"opcode": "event_whenbroadcastreceived", "next": "i_show", "parent": None,
                   "inputs": {}, "fields": {"BROADCAST_OPTION": ["ShowIntro", "bc_show_intro"]},
                   "shadow": False, "topLevel": True, "x": 20, "y": 150},
        "i_show": {"opcode": "looks_show", "next": "i_say_info", "parent": "i_recv",
                   "inputs": {}, "fields": {}, "shadow": False, "topLevel": False},
        # looks_say (no timer) → persistent bubble showing planet info all level
        "i_say_info": {"opcode": "looks_say", "next": "i_wait", "parent": "i_show",
                       "inputs": {"MESSAGE": [3, "i_join_full", [10, ""]]},
                       "fields": {}, "shadow": False, "topLevel": False},
        # join(planet_name, join(": ", description))
        "i_join_full": {"opcode": "operator_join", "next": None, "parent": "i_say_info",
                        "inputs": {"STRING1": [3, "i_name_item", [10, ""]], "STRING2": [3, "i_join_desc", [10, ""]]},
                        "fields": {}, "shadow": False, "topLevel": False},
        "i_join_desc": {"opcode": "operator_join", "next": None, "parent": "i_join_full",
                        "inputs": {"STRING1": [1, [10, ": "]], "STRING2": [3, "i_desc_item", [10, ""]]},
                        "fields": {}, "shadow": False, "topLevel": False},
        "i_name_item": {"opcode": "data_itemoflist", "next": None, "parent": "i_join_full",
                        "inputs": {"INDEX": [3, "i_lv1", [4, "1"]]},
                        "fields": {"LIST": ["PlanetNames", "list_planet_names"]},
                        "shadow": False, "topLevel": False},
        "i_lv1": {"opcode": "data_variable", "next": None, "parent": "i_name_item",
                  "inputs": {}, "fields": {"VARIABLE": ["Level", "var_level"]},
                  "shadow": False, "topLevel": False},
        "i_desc_item": {"opcode": "data_itemoflist", "next": None, "parent": "i_join_desc",
                        "inputs": {"INDEX": [3, "i_lv2", [4, "1"]]},
                        "fields": {"LIST": ["Intros", "list_intros"]},
                        "shadow": False, "topLevel": False},
        "i_lv2": {"opcode": "data_variable", "next": None, "parent": "i_desc_item",
                  "inputs": {}, "fields": {"VARIABLE": ["Level", "var_level"]},
                  "shadow": False, "topLevel": False},
        # wait 2.5s so player can read intro; broadcastandwait completes here
        "i_wait": {"opcode": "control_wait", "next": None, "parent": "i_say_info",
                   "inputs": {"DURATION": [1, [4, "2.5"]]},
                   "fields": {}, "shadow": False, "topLevel": False},
        # AllClear → say victory (board still visible over solar-system bg)
        "i_all": {"opcode": "event_whenbroadcastreceived", "next": "i_victory", "parent": None,
                  "inputs": {}, "fields": {"BROADCAST_OPTION": ["AllClear", "bc_all_clear"]},
                  "shadow": False, "topLevel": True, "x": 20, "y": 400},
        "i_victory": {"opcode": "looks_say", "next": None, "parent": "i_all",
                      "inputs": {"MESSAGE": [1, [10, "You protected all 8 planets! \u2605"]]},
                      "fields": {}, "shadow": False, "topLevel": False},
    }

    return project


def package_project_dir(project_dir: Path, out_sb3: Path) -> None:
    project_json = project_dir / "project.json"
    if not project_json.exists():
        raise FileNotFoundError(f"Missing required file: {project_json}")

    with zipfile.ZipFile(out_sb3, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(project_json, arcname="project.json")
        for item in project_dir.iterdir():
            if item.is_file() and item.name != "project.json":
                zf.write(item, arcname=item.name)

    print(f"Created: {out_sb3}")


def cmd_template(out_sb3: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="scratch_template_") as td:
        tmp = Path(td)
        project = make_template_project()
        asset_map = write_assets(tmp)
        normalize_project_assets(project, asset_map)
        write_text(tmp / "project.json", json.dumps(project, ensure_ascii=False, separators=(",", ":")))
        package_project_dir(tmp, out_sb3)
    print("Template generated.")


def cmd_game(out_sb3: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="scratch_game_") as td:
        tmp = Path(td)
        project = make_playable_project()
        asset_map = write_assets(tmp)
        normalize_project_assets(project, asset_map)
        write_text(tmp / "project.json", json.dumps(project, ensure_ascii=False, separators=(",", ":")))
        package_project_dir(tmp, out_sb3)
    print("Playable game generated.")


def cmd_package(project_dir: Path, out_sb3: Path) -> None:
    package_project_dir(project_dir, out_sb3)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build or package Scratch 3 .sb3 files")
    sub = parser.add_subparsers(dest="command", required=True)

    p_package = sub.add_parser("package", help="Package existing project.json + assets to .sb3")
    p_package.add_argument("--project-dir", required=True, help="Directory containing project.json")
    p_package.add_argument("--out", required=True, help="Output .sb3 path")

    p_template = sub.add_parser("template", help="Generate editable template .sb3")
    p_template.add_argument("--out", required=True, help="Output .sb3 path")

    p_game = sub.add_parser("game", help="Generate playable solar-system game .sb3")
    p_game.add_argument("--out", required=True, help="Output .sb3 path")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "package":
        cmd_package(Path(args.project_dir).resolve(), Path(args.out).resolve())
    elif args.command == "template":
        cmd_template(Path(args.out).resolve())
    elif args.command == "game":
        cmd_game(Path(args.out).resolve())
    else:
        raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
