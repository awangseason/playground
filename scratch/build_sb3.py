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


def svg_circle(size: int, fill: str, stroke: str = "#ffffff") -> str:
    c = size // 2
    r = c - 4
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
        f'<circle cx="{c}" cy="{c}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="4"/>'
        "</svg>"
    )


def write_assets(out_dir: Path) -> dict:
    assets = {
        "bg_space.svg": svg_rect(480, 360, "#0b1020", "Solar System Guardian"),
        "bg_full_solar_system.svg": svg_rect(480, 360, "#101a38", "Full Solar System"),
        "hero.svg": svg_circle(80, "#21d4fd"),
        "trash_1.svg": svg_circle(48, "#7f8c8d"),
        "trash_2.svg": svg_circle(48, "#95a5a6"),
        "trash_3.svg": svg_circle(48, "#bdc3c7"),
        "planet_mercury.svg": svg_circle(90, "#9e7c63"),
        "planet_venus.svg": svg_circle(90, "#d8b27a"),
        "planet_earth.svg": svg_circle(90, "#3c9ee7"),
        "planet_mars.svg": svg_circle(90, "#c1442e"),
        "planet_jupiter.svg": svg_circle(90, "#d9a066"),
        "planet_saturn.svg": svg_circle(90, "#d7c18f"),
        "planet_uranus.svg": svg_circle(90, "#86d1d3"),
        "planet_neptune.svg": svg_circle(90, "#4062d8"),
        "intro_board.svg": svg_rect(280, 90, "#1f2a44", "Planet Briefing"),
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
                "rotationCenterX": 40,
                "rotationCenterY": 40,
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
            {"assetId": "planet_mercury", "name": "Mercury", "md5ext": "planet_mercury.svg", "dataFormat": "svg", "rotationCenterX": 45, "rotationCenterY": 45},
            {"assetId": "planet_venus", "name": "Venus", "md5ext": "planet_venus.svg", "dataFormat": "svg", "rotationCenterX": 45, "rotationCenterY": 45},
            {"assetId": "planet_earth", "name": "Earth", "md5ext": "planet_earth.svg", "dataFormat": "svg", "rotationCenterX": 45, "rotationCenterY": 45},
            {"assetId": "planet_mars", "name": "Mars", "md5ext": "planet_mars.svg", "dataFormat": "svg", "rotationCenterX": 45, "rotationCenterY": 45},
            {"assetId": "planet_jupiter", "name": "Jupiter", "md5ext": "planet_jupiter.svg", "dataFormat": "svg", "rotationCenterX": 45, "rotationCenterY": 45},
            {"assetId": "planet_saturn", "name": "Saturn", "md5ext": "planet_saturn.svg", "dataFormat": "svg", "rotationCenterX": 45, "rotationCenterY": 45},
            {"assetId": "planet_uranus", "name": "Uranus", "md5ext": "planet_uranus.svg", "dataFormat": "svg", "rotationCenterX": 45, "rotationCenterY": 45},
            {"assetId": "planet_neptune", "name": "Neptune", "md5ext": "planet_neptune.svg", "dataFormat": "svg", "rotationCenterX": 45, "rotationCenterY": 45},
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
        "x": 0,
        "y": 120,
        "size": 100,
        "direction": 90,
        "draggable": False,
        "rotationStyle": "all around",
    }

    return {
        "targets": [stage, hero, trash, planet, intro],
        "monitors": [],
        "extensions": [],
        "meta": {"semver": "3.0.0", "vm": "0.2.0", "agent": "Python builder"},
    }


def make_playable_project() -> dict:
    project = make_template_project()

    # ── STAGE ────────────────────────────────────────────────────────────────
    # Flag → set bg/score/level=1 → repeat until Level > 8 → level body → next level
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
    sb["s_target"] = {"opcode": "data_setvariableto", "next": "s_spawn", "parent": "s_reset_hp",
                      "inputs": {"VALUE": [1, [4, "6"]]}, "fields": {"VARIABLE": ["Target", "var_target"]},
                      "shadow": False, "topLevel": False}
    sb["s_spawn"] = {"opcode": "data_setvariableto", "next": "s_speed", "parent": "s_target",
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
    sb["s_intro"] = {"opcode": "event_broadcast", "next": "s_game_on", "parent": "s_setplanet",
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
        "t_move": {"opcode": "motion_changexby", "next": None, "parent": "t_repeat",
                   "inputs": {"DX": [1, [4, "-5"]]}, "fields": {}, "shadow": False, "topLevel": False},
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
    }

    # ── INTRO BOARD ──────────────────────────────────────────────────────────
    intro = project["targets"][4]
    intro["blocks"] = {
        "i_top": {"opcode": "event_whenflagclicked", "next": "i_hide", "parent": None,
                  "inputs": {}, "fields": {}, "shadow": False, "topLevel": True, "x": 20, "y": 20},
        "i_hide": {"opcode": "looks_hide", "next": None, "parent": "i_top",
                   "inputs": {}, "fields": {}, "shadow": False, "topLevel": False},
        "i_recv": {"opcode": "event_whenbroadcastreceived", "next": "i_show", "parent": None,
                   "inputs": {}, "fields": {"BROADCAST_OPTION": ["ShowIntro", "bc_show_intro"]},
                   "shadow": False, "topLevel": True, "x": 20, "y": 180},
        "i_show": {"opcode": "looks_show", "next": "i_say1", "parent": "i_recv",
                   "inputs": {}, "fields": {}, "shadow": False, "topLevel": False},
        "i_say1": {"opcode": "looks_sayforsecs", "next": "i_say2", "parent": "i_show",
                   "inputs": {"MESSAGE": [1, [10, "Protect this planet!"]], "SECS": [1, [4, "2"]]},
                   "fields": {}, "shadow": False, "topLevel": False},
        "i_say2": {"opcode": "looks_sayforsecs", "next": "i_hide2", "parent": "i_say1",
                   "inputs": {"MESSAGE": [1, [10, "Block space trash from right to left."]], "SECS": [1, [4, "2"]]},
                   "fields": {}, "shadow": False, "topLevel": False},
        "i_hide2": {"opcode": "looks_hide", "next": None, "parent": "i_say2",
                    "inputs": {}, "fields": {}, "shadow": False, "topLevel": False},
        "i_all": {"opcode": "event_whenbroadcastreceived", "next": "i_showall", "parent": None,
                  "inputs": {}, "fields": {"BROADCAST_OPTION": ["AllClear", "bc_all_clear"]},
                  "shadow": False, "topLevel": True, "x": 20, "y": 380},
        "i_showall": {"opcode": "looks_show", "next": "i_end", "parent": "i_all",
                      "inputs": {}, "fields": {}, "shadow": False, "topLevel": False},
        "i_end": {"opcode": "looks_sayforsecs", "next": None, "parent": "i_showall",
                  "inputs": {"MESSAGE": [1, [10, "You protected all 8 planets!"]], "SECS": [1, [4, "4"]]},
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
