# TinyTroupe Bulk Simulation System  
A full multi-scenario bulk simulation framework built with **TinyTroupe**, designed to run persona-based user feedback tests at scale.

This project allows you to:

- Generate diverse simulated user personas  
- Run multiple simulations in bulk  
- Store each simulation's state  
- Customize behavior using `config.ini`  
- Debug TinyTroupe with various test scripts  
- View structured simulation output (Rich UI version included)

---

# deliverable-2-bulk-sim
.gitignore 
    .env
    *.cache.json
    *.pickle
    __pycache__/

# bulk_simulation.py
import os
from tinytroupe.environment.tiny_world import TinyWorld
from tinytroupe.factory.tiny_person_factory import TinyPersonFactory
from tinytroupe import control

def run_user_feedback_simulation(sim_name, description, context, num_users=3):
    """
    Run a single TinyTroupe simulation safely for bulk runs.
    """
    cache_file = f"{sim_name.replace(' ', '_')}.cache.json"

    # Begin simulation safely
    try:
        control.begin(cache_file)
    except ValueError:
        # Reset simulation state if needed
        print(f"⚠️ Simulation '{sim_name}' control state was not clean. Resetting...")
        try:
            control.end()
        except ValueError:
            pass
        control.begin(cache_file)

    # Create simulation world
    world = TinyWorld(sim_name)

    # Persona factory
    factory = TinyPersonFactory(
        sampling_space_description=description,
        total_population_size=num_users,
        context=context
    )

    # Generate personas safely
    users = []
    for i in range(num_users):
        try:
            person = factory.generate_person()
            if person is None:
                print(f"⚠️ Could not generate persona #{i+1}, skipping.")
                continue
            # Avoid duplicate names in the same world
            if any(u.name == person.name for u in users):
                print(f"⚠️ Duplicate persona name '{person.name}' detected, skipping.")
                continue
            users.append(person)
            print(f"✅ Created persona: {person.name}")
        except Exception as e:
            print(f"⚠️ Error generating persona #{i+1}: {e}")

    # Add users to the world
    for user in users:
        world.add_agent(user)

    # Run simulation phases
    world.run(3)  # Phase 1
    control.checkpoint()
    world.run(3)  # Phase 2

    # End simulation safely
    try:
        control.end()
    except ValueError:
        print(f"⚠️ Simulation '{sim_name}' was already stopped.")

    return world

# bulk_user_feedback_simulation_fixed.py
import os
from tinytroupe.environment.tiny_world import TinyWorld
from tinytroupe.factory.tiny_person_factory import TinyPersonFactory
from tinytroupe import control

# =============================================
# 🧹 Optional cache clearing before run
# =============================================
if os.getenv("RESET_CACHE", "false").lower() == "true":
    for cache_file in ["bulk_user_feedback_simulation.cache.json", "openai_api_cache.pickle"]:
        if os.path.exists(cache_file):
            os.remove(cache_file)
            print(f"🧹 Cleared cache: {cache_file}")

# =============================================
# ⚠️ Make sure your OpenAI API key is set in .env
# =============================================
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("Please set the OPENAI_API_KEY environment variable before running the simulation.")

# =============================================
# Helper: Generate personas safely
# =============================================
def generate_personas(factory, n=3):
    personas = []
    for i in range(n):
        try:
            person = factory.generate_person()
            if person is None:
                print(f"⚠️ Persona #{i+1} could not be generated, skipping.")
                continue
            personas.append(person)
            print(f"✅ Created persona: {getattr(person, 'name', 'Unknown')}")
        except Exception as e:
            print(f"⚠️ Error generating persona #{i+1}: {e}")
    return personas

# =============================================
# Helper: Run a single simulation
# =============================================
def run_simulation(sim_id, n_steps=3):
    print(f"\n🚀 Starting simulation #{sim_id}\n")
    
    control.begin(f"bulk_user_feedback_simulation_{sim_id}.cache.json")

    # Create world
    world = TinyWorld(f"Simulation World #{sim_id}")

    # Create factory
    factory = TinyPersonFactory(
        sampling_space_description=(
            "Users with diverse experiences testing a new productivity app."
        ),
        total_population_size=3,
        context="Simulated users provide feedback on first week using new app features."
    )

    # Generate personas
    users = generate_personas(factory, n=3)

    # Fallback: use manual personas if factory fails
    if not users:
        from tinytroupe.agent import TinyPerson
        users = [
            TinyPerson(name="Alice"),
            TinyPerson(name="Bob"),
            TinyPerson(name="Carol")
        ]
        print("⚠️ Using manual personas due to generation failure.")

    # Add personas to the world
    for user in users:
        world.add_agent(user)

    # Run simulation phases
    print("\n💬 Phase 1...")
    world.run(n_steps)

    print("\n💾 Checkpointing...")
    control.checkpoint()

    print("\n💬 Phase 2...")
    world.run(n_steps)

    print("\n🏁 Ending simulation...")
    control.end()

    return f"bulk_user_feedback_simulation_{sim_id}.cache.json"

# =============================================
# Run multiple simulations in bulk
# =============================================
def bulk_simulations(total_simulations=3):
    all_checkpoints = []
    for sim_id in range(1, total_simulations + 1):
        checkpoint_file = run_simulation(sim_id, n_steps=3)
        all_checkpoints.append(checkpoint_file)
    return all_checkpoints

# =============================================
if __name__ == "__main__":
    checkpoints = bulk_simulations(total_simulations=3)
    print("\n✅ All simulations complete! Checkpoints:")
    for c in checkpoints:
        print(f" - {c}")

config.ini
[OpenAI]
api_type = openai
model = gpt-4o-mini
reasoning_model = gpt-4o-mini
embedding_model = text-embedding-3-small
max_tokens = 4000
temperature = 1.0
freq_penalty = 0.3
presence_penalty = 0.5
timeout = 120
max_attempts = 5
waiting_time = 10
exponential_backoff_factor = 3
reasoning_effort = high
cache_api_calls = True
cache_file_name = openai_api_cache.pickle
max_content_display_length = 4000

; ⚠ Removed 'response_format = json_schema' because GPT-3.5-turbo does not support structured outputs

[Simulation]
parallel_agent_generation = False
parallel_agent_actions = False
num_agents = 5  
rai_harmful_content_prevention = True
rai_copyright_infringement_prevention = True

[Cognition]
enable_memory_consolidation = True
min_episode_length = 25
max_episode_length = 80
episodic_memory_fixed_prefix_length = 10
episodic_memory_lookback_length = 20
enable_self_reflection = True

[ActionGenerator]
max_attempts = 2
enable_quality_checks = False
enable_regeneration = True
enable_direct_correction = False
enable_quality_check_for_persona_adherence = True
enable_quality_check_for_selfconsistency = False
enable_quality_check_for_fluency = False
enable_quality_check_for_suitability = False
enable_quality_check_for_similarity = False
continue_on_failure = True
quality_threshold = 5

[Logging]
loglevel = DEBUG

#requirements.txt
tinytroupe
python-dotenv

# run_bulk_simulations.py
from bulk_simulation import run_user_feedback_simulation
from scenarios import SCENARIOS

def run_all():
    for scenario in SCENARIOS:
        print(f"\n🔹 Running simulation: {scenario['sim_name']}\n")
        run_user_feedback_simulation(
            sim_name=scenario["sim_name"],
            description=scenario["description"],
            context=scenario["context"],
            num_users=scenario.get("num_users", 3)
        )

if __name__ == "__main__":
    run_all()

# scenarios.py
SCENARIOS = [
    {
        "sim_name": "Productivity App Beta Test 1",
        "description": "Users with diverse experiences testing a new productivity app.",
        "context": "Simulating beta testers' first week using new mobile productivity app features.",
        "num_users": 3
    },
    {
        "sim_name": "Productivity App Beta Test 2",
        "description": "Experienced professionals exploring app workflow features.",
        "context": "Users report feedback after the second week of app usage.",
        "num_users": 4
    },
    # Add more scenarios as needed
]

#test_api_key.py
from openai import OpenAI
client = OpenAI()
try:
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say hello!"}]
    )
    print("✅ API key works! Response:")
    print(resp.choices[0].message.content)
except Exception as e:
    print("❌ Error:", e)


#tinyworld_test.py
import os
from dotenv import load_dotenv

# Load your API key from .env
load_dotenv()
print("DEBUG: OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))

from tinytroupe.environment.tiny_world import TinyWorld
from tinytroupe.agent import TinyPerson
from tinytroupe import control

# === Start recording (this allows saving & restoring simulation state) ===
control.begin("simulation.cache.json")

# === Define your agents ===
alice = TinyPerson(name="Alice")
alice.define("description", "Curious engineer who loves AI simulations and exploring virtual societies.")
alice.define("traits", ["curious", "analytical", "friendly"])

bob = TinyPerson(name="Bob")
bob.define("description", "Skeptical philosopher interested in human behavior and technology ethics.")
bob.define("traits", ["skeptical", "thoughtful", "empathetic"])

carol = TinyPerson(name="Carol")
carol.define("description", "Playful artist who expresses creativity through digital mediums.")
carol.define("traits", ["imaginative", "open-minded", "expressive"])

# === Create a tiny world ===
world = TinyWorld(agents=[alice, bob, carol])

print("\n🌍 Starting TinyWorld simulation...\n")

# === Run first phase of the simulation ===
world.run(3)

# === Save a checkpoint (you can resume from this later) ===
control.checkpoint()
print("\n💾 Simulation checkpoint saved!\n")

# === Continue simulation ===
world.run(3)

# === End recording and save everything ===
control.end()
print("\n✅ Simulation complete. State saved to simulation.cache.json.\n")

# user_feedback_simulation_rich.py
import os
from tinytroupe.environment.tiny_world import TinyWorld
from tinytroupe.factory.tiny_person_factory import TinyPersonFactory
from tinytroupe import control
from rich.console import Console
from rich.table import Table

console = Console()

# =============================================
# 🧹 Optional cache clearing before run
# =============================================
if os.getenv("RESET_CACHE", "false").lower() == "true":
    for cache_file in ["user_feedback_simulation.cache.json", "openai_api_cache.pickle"]:
        if os.path.exists(cache_file):
            os.remove(cache_file)
            console.print(f"🧹 Cleared cache: {cache_file}", style="yellow")

# =============================================
# ⚠️ Make sure your OpenAI API key is set
# =============================================
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("Please set the OPENAI_API_KEY environment variable before running the simulation.")

# =============================================
# ✅ Force GPT-4 for structured outputs
# =============================================
import tinytroupe
tinytroupe.config.OPENAI_MODEL = "gpt-4"
tinytroupe.config.OPENAI_REASONING_MODEL = "gpt-4"

console.print("\n🚀 Starting user feedback simulation...\n", style="bold green")
control.begin("user_feedback_simulation.cache.json")

# =============================================
# 🌍 Create world
# =============================================
console.print("🌍 Creating simulation world...\n", style="bold cyan")
world = TinyWorld("User Feedback Simulation World")

# =============================================
# 👥 Generate personas
# =============================================
console.print("👥 Generating user personas...\n", style="bold cyan")
factory = TinyPersonFactory(
    sampling_space_description=(
        "A mix of new and experienced users testing a beta productivity app, "
        "including people from different professional and cultural backgrounds."
    ),
    total_population_size=3,
    context="Each simulated user provides feedback on their first week using the new app features."
)

users = []
for i in range(3):
    try:
        person = factory.generate_person()
        if person is None:
            console.print(f"⚠️ Could not generate persona #{i+1}, skipping.", style="red")
            continue
        # Enable structured output
        person.action_generator.use_json_schema = True
        users.append(person)
        console.print(f"✅ Created persona: {getattr(person, 'name', 'Unknown')}", style="green")
    except Exception as e:
        console.print(f"⚠️ Error generating persona #{i+1}: {e}", style="red")

# Add agents to world
for u in users:
    world.add_agent(u)

# =============================================
# Function to run simulation phase and display table
# =============================================
def run_simulation_phase(world, phase_name, steps=3):
    console.print(f"\n💬 Running {phase_name}...\n", style="bold magenta")
    for step in range(steps):
        try:
            actions = world.run(1)
        except Exception as e:
            console.print(f"⚠️ Error in simulation step {step+1}: {e}", style="red")
            actions = []

        table = Table(title=f"{phase_name} - Step {step+1}")
        table.add_column("Persona", style="cyan", no_wrap=True)
        table.add_column("Action", style="green")
        table.add_column("Content", style="white")

        for agent, agent_actions in zip(world.agents, actions or []):
            agent_name = getattr(agent, "name", "Unknown")
            if not agent_actions:
                table.add_row(agent_name, "-", "No action this step")
                continue
            for act in agent_actions:
                table.add_row(agent_name, act.get("role", "-"), act.get("content", "-"))

        console.print(table)

# =============================================
# Run phases
run_simulation_phase(world, "Phase 1 (initial experiences)")
console.print("\n💾 Saving checkpoint...\n", style="bold yellow")
control.checkpoint()
run_simulation_phase(world, "Phase 2 (continued feedback)")

# =============================================
console.print("\n🏁 Ending simulation and saving state...\n", style="bold green")
control.end()

# =============================================
# 👥 Summary of Personas
console.print("\n👥 Summary of Personas in Simulation:\n", style="bold cyan")
summary_table = Table(title="Simulation Personas")
summary_table.add_column("No.", style="magenta")
summary_table.add_column("Name", style="cyan")
summary_table.add_column("Traits", style="green")

for i, u in enumerate(users, 1):
    summary_table.add_row(str(i), getattr(u, "name", "Unknown"), str(getattr(u, "traits", "N/A")))

console.print(summary_table)
console.print("\n✅ Simulation complete! All results saved to user_feedback_simulation.cache.json.\n", style="bold green")
