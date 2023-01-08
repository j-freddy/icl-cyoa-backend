import pytest

from src.analyser import is_duplicate


@pytest.mark.parametrize(
    "first_text, second_text, expected_result",
    [
        (
            "You're at a party, and you see someone you don't recognize. They're wearing a mask, and they're holding a "
            "knife. You watch as they move around the room, talking to people and laughing. But there's something "
            "off about their laugh. It's too loud, and it sounds forced. You start to feel uneasy.You keep an eye on the "
            "person in the mask, but you lose track of them for a few minutes.  \n  When you find them again, "
            "they're standing in a corner with another person. The two of them are arguing, and the masked person is gesturing angrily with the knife. Suddenly, the other person falls to the ground with a scream.The masked person looks around wildly, before realizing that everyone is staring at them. They drop the knife and run out of the room.You follow them, but they're gone by the time you get outside. You look down at the body of the other person lying on the ground.. who was killed by someone wearing a mask at this party tonight?",
            "You are at a party and you see someone you don't recognize. They're wearing a mask, and they're holding "
            "a knife. You watch as they move around the room, talking to people and laughing. But there's something "
            "off about their laugh. It's too loud, and it sounds forced. You start to feel uneasy. You keep an eye on the person in the mask, but you lose track of them for a few minutes. When you find them again, they're standing in a corner with another person. The two of them are arguing, and the masked person is gesturing angrily with the knife. Suddenly, the other person falls to the ground with a scream. The masked person looks around wildly, before realizing that everyone is staring at them. They drop the knife and run out of the room. You follow them, but they're gone by the time you get outside. You look down at the body of the other person  lying on the ground.. who was killed by someone wearing a mask at this party tonight?",
            True,
        ),
        (
            "You are a chicken. You love to eat seeds and scratch in the dirt. You are happy living on the farm with all of "
            "your friends. You don't mind being dirty, and you love nothing more than a good meal. You choose to stay on the farm and continue to live a happy life eating seeds and scratching in the dirt.",
            "You are a chicken. You love to eat seeds and scratch around in the dirt. You are content living on the farm with all of your friends. You don't mind being dirty, and you love nothing more than a good meal. You choose to stay on the farm and continue to live a happy life eating seeds and scratching around in the dirt. You choose to go to the slaughterhouse and be turned into chicken nuggets.",
            True,
        ),
        (
            "A few days later, the police announce that they have arrested the person who killed the other person at "
            "the party. They tell you that it was someone you didn't know - they were wearing a mask so that no one would be able to identify them. You're relieved that the killer has been caught, but you can't help but feel sorry for the person who was killed. It's tragic that they lost their life in such a senseless act of violence.",
            "A few days later, the police announce that they have arrested the person who killed the other person at "
            "the party. They tell you that it was someone you didn't know - they were wearing a mask so that no one would be able to identify them. You're relieved that the killer has been caught, but you can't help but feel sorry for the person who was killed. It's tragic that they lost their life in such a senseless act of violence. You choose to forget about what happened and move on with your life",
            True,
        ),
        (
            "Try to fight off the attacker.",
            "Give in and let the attacker take you.",
            False,
        ),
        (
            "Stay in bed and hope it goes away.",
            "Stay in bed and hope it goes away.",
            True,
        ),
        (
            "You ignore the noise and try to sleep.",
            "You can continue to try to ignore the noise and go back to sleep.",
            True,
        ),
    ],
)
def test_duplicate_strings_are_being_flagged_correctly(
    first_text: str, second_text: str, expected_result: bool
):
    assert is_duplicate(first_text, second_text) == expected_result
