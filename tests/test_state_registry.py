"""
The routing table is the product surface. Pin it.

WHY THIS FILE EXISTS
--------------------
On 2026-08-12 every New Jersey form was unreachable in production. Not
broken — unreachable. The 11 generators had shipped with the NY/NJ merge,
were importable, and had just been QA'd to the same layout standard as New
York (cde44ca). But STATE_CONFIGS listed only 'ny', so get_generator()
raised "Unsupported state: nj" before any of that code was ever asked to
run, and POST /generate/nj/<form> answered 400 for months.

Nothing caught it, because every existing test either called a generator
function DIRECTLY (bypassing the registry) or asserted on New York. The gap
was between "the code exists" and "the service will route to it" — and that
gap is exactly one dict.

THE STANDARD: every state the service claims to support must resolve every
form it advertises, through the same import path the HTTP route uses. A
generator that exists but is not registered is a generator that does not
exist, and this file says so out loud.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import STATE_CONFIGS, get_generator  # noqa: E402


# The two states the product actually sells. Pinned by name so that DELETING
# a state is a deliberate act that turns this file red, not a silent
# regression like the one above.
EXPECTED_STATES = {"ny", "nj"}

ALL_FORMS = [
    (state, form)
    for state, config in STATE_CONFIGS.items()
    for form in config["forms"]
]


def test_expected_states_are_registered():
    assert EXPECTED_STATES <= set(STATE_CONFIGS), (
        "a state the product sells is missing from the routing table: "
        f"{EXPECTED_STATES - set(STATE_CONFIGS)}"
    )


@pytest.mark.parametrize("state,form", ALL_FORMS, ids=lambda v: str(v))
def test_every_registered_form_resolves(state, form):
    """The registry's promise, checked through the route's own import path."""
    fn = get_generator(state, form)
    assert callable(fn), f"{state}/{form} resolved to something uncallable"


@pytest.mark.parametrize("state", sorted(STATE_CONFIGS))
def test_phase_lists_only_reference_registered_forms(state):
    config = STATE_CONFIGS[state]
    known = set(config["forms"])
    for phase in ("phase1", "phase2", "phase3"):
        unknown = set(config.get(phase, [])) - known
        assert not unknown, f"{state}.{phase} names unregistered forms: {unknown}"


@pytest.mark.parametrize("state", sorted(STATE_CONFIGS))
def test_no_form_appears_in_more_than_one_phase(state):
    """A form listed twice prints twice in the packet the client is handed.

    Deliberately NOT asserting the converse. New York registers 'complaint',
    'stipulation' and 'ud4' outside phase1/2/3 on purpose: the phases are the
    UD packet, and those three are filed on their own. "Registered but
    unphased" is a legitimate shape, so only DOUBLE-listing is an error here.
    """
    config = STATE_CONFIGS[state]
    counts = {form: 0 for form in config["forms"]}
    for phase in ("phase1", "phase2", "phase3"):
        for form in config.get(phase, []):
            counts[form] += 1

    duplicated = sorted(f for f, n in counts.items() if n > 1)
    assert not duplicated, f"{state}: in more than one phase: {duplicated}"


def test_unknown_state_and_unknown_form_still_refuse():
    """The negative case, so registering NJ did not loosen the guard."""
    with pytest.raises(ValueError):
        get_generator("pa", "complaint")
    with pytest.raises(ValueError):
        get_generator("nj", "ud6")  # a NY form name, on the NJ side
