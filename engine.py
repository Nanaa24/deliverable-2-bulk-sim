import json
from tinytroupe.environment.tiny_world import TinyWorld
from tinytroupe.agent import TinyPerson
from tinytroupe import control

def create_persona(name, data):
    """Convert persona dictionary to TinyPerson object."""
    p = TinyPerson(name=name)
    for k, v in data.items():
        p.define(k, v)
    return p

def run_bulk_simulation(selected_personas, rounds):
    """Run TinyTroupe simulation for selected personas and rounds."""
    with open("personas.json", "r") as f:
        persona_db = json.load(f)

    # Initialize simulation
    cache_file = "web_simulation.cache.json"
    try:
        control.begin(cache_file)
    except ValueError:
        try:
            control.end()
        except ValueError:
            pass
        control.begin(cache_file)

    world = TinyWorld("Web Simulation World")

    # Add selected personas
    persona_objects = []
    for name in selected_personas:
        if name in persona_db:
            persona_objects.append(create_persona(name, persona_db[name]))
            world.add_agent(persona_objects[-1])

    # Run simulation rounds
    all_actions = {p.name: [] for p in persona_objects}
    for _ in range(rounds):
        step_actions = world.run(1)
        for agent, actions in zip(world.agents, step_actions or []):
            all_actions[agent.name].extend(actions or [])

    # End simulation
    control.end()

    return all_actions