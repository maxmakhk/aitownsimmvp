from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Dict, List


MAX_REST = 100
MAX_FOOD = 100
MAX_MONEY = 9999

HOURLY_REST_DECAY = 7
HOURLY_FOOD_DECAY = 10


@dataclass
class AbilityValues:
    rest: int = MAX_REST
    food: int = 80
    money: int = 0

    def clamp(self) -> None:
        self.rest = max(0, min(MAX_REST, self.rest))
        self.food = max(0, min(MAX_FOOD, self.food))
        self.money = max(0, min(MAX_MONEY, self.money))

    def hourly_decay(self) -> None:
        self.rest -= HOURLY_REST_DECAY
        self.food -= HOURLY_FOOD_DECAY
        self.clamp()


@dataclass
class LocationEffect:
    name: str
    money_delta: int = 0
    food_delta: int = 0
    rest_full: bool = False

    def apply(self, abilities: AbilityValues) -> None:
        if self.rest_full:
            abilities.rest = MAX_REST
        else:
            abilities.rest += 0

        abilities.money += self.money_delta
        abilities.food += self.food_delta
        abilities.clamp()


LOCATIONS: Dict[str, LocationEffect] = {
    "tavern": LocationEffect(name="tavern", money_delta=-50, food_delta=100),
    "home": LocationEffect(name="home", rest_full=True),
    "working": LocationEffect(name="working", money_delta=20),
}


@dataclass
class NPC:
    name: str
    location: str
    default_location: str
    abilities: AbilityValues = field(default_factory=AbilityValues)

    def choose_next_location(self) -> str:
        weights: Dict[str, float] = {
            self.default_location: 100.0,
        }

        rest_need = max(0, 50 - self.abilities.rest)
        if rest_need > 0:
            weights["home"] = weights.get("home", 0.0) + (rest_need / 50) * 100

        hungry_need = max(0, 50 - self.abilities.food)
        if hungry_need > 0:
            weights["tavern"] = weights.get("tavern", 0.0) + (hungry_need / 50) * 100

        if hungry_need > 0 and self.abilities.money < 50:
            weights["working"] = weights.get("working", 0.0) + (hungry_need / 50) * 100

        choices = list(weights.keys())
        probs = list(weights.values())
        return random.choices(choices, weights=probs, k=1)[0]

    def hourly_update(self) -> None:
        self.abilities.hourly_decay()
        LOCATIONS[self.location].apply(self.abilities)


def group_check(npcs: List[NPC]) -> None:
    groups: Dict[str, List[NPC]] = {}
    for npc in npcs:
        groups.setdefault(npc.location, []).append(npc)

    for location, members in groups.items():
        if len(members) > 1:
            names = ", ".join(n.name for n in members)
            print(f"[GroupChat] {location}: {names}")


def solo_chat(npc: NPC) -> None:
    print(f"[SoloChat] {npc.name} at {npc.location}")


def simulate(hours: int = 24) -> None:
    npcs = [
        NPC(name="Alya", location="home", default_location="working"),
        NPC(name="Borin", location="working", default_location="working"),
        NPC(name="Cira", location="tavern", default_location="working"),
    ]

    for hour in range(1, hours + 1):
        print(f"\n=== Hour {hour} ===")

        for npc in npcs:
            npc.hourly_update()
            print(
                f"{npc.name} | {npc.location} | rest {npc.abilities.rest}/100 | "
                f"food {npc.abilities.food}/100 | money {npc.abilities.money}/9999"
            )

        group_check(npcs)
        for npc in npcs:
            solo_chat(npc)

        for npc in npcs:
            npc.location = npc.choose_next_location()


if __name__ == "__main__":
    simulate(hours=24)
