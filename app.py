import streamlit as st
from engine import run_bulk_simulation
import json
import pandas as pd

st.set_page_config(page_title="TinyTroupe Bulk Simulation", layout="wide")

st.title("🧠 TinyTroupe Bulk Simulation Dashboard")
st.write(
    "Run persona-based simulations with 50 diverse personas. "
    "Select personas and number of rounds to generate realistic feedback."
)

# Load persona database
with open("personas.json", "r") as f:
    persona_db = json.load(f)

# Sidebar options
st.sidebar.header("Simulation Options")
selected_personas = st.sidebar.multiselect(
    "Choose Personas",
    options=list(persona_db.keys()),
    default=list(persona_db.keys())[:5]
)
num_rounds = st.sidebar.slider("Simulation Rounds", 1, 10, 3)

if st.button("Run Simulation"):
    if not selected_personas:
        st.error("Please select at least one persona.")
    else:
        with st.spinner("Running simulation..."):
            results = run_bulk_simulation(selected_personas, num_rounds)

        st.success("Simulation Complete!")

        # ===== Persona Summary Table =====
        st.subheader("👥 Persona Summary")
        summary_data = []
        for name in selected_personas:
            persona = persona_db[name]
            summary_data.append({
                "Name": name,
                "Description": persona.get("description", ""),
                "Traits": ", ".join(persona.get("traits", [])),
                "Age Group": persona.get("demographics", {}).get("age_group", ""),
                "Profession": persona.get("demographics", {}).get("profession", ""),
                "Behavior": persona.get("behavior", "")
            })
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, use_container_width=True)

        # Download Persona Summary
        csv_summary = df_summary.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Persona Summary (CSV)",
            data=csv_summary,
            file_name="persona_summary.csv",
            mime="text/csv"
        )

        # ===== Detailed Simulation Actions =====
        st.subheader("💬 Simulation Actions")
        all_actions_combined = []
        for agent_name, actions in results.items():
            st.markdown(f"### 👤 {agent_name}")
            if not actions:
                st.write("No actions recorded.")
                continue
            action_data = []
            for i, action in enumerate(actions, 1):
                action_data.append({
                    "Persona": agent_name,
                    "Step": i,
                    "Role": action.get("role", "-"),
                    "Content": action.get("content", "-")
                })
            all_actions_combined.extend(action_data)
            df_actions = pd.DataFrame(action_data)
            st.dataframe(df_actions, use_container_width=True)

        # Download Simulation Actions (CSV)
        df_all_actions = pd.DataFrame(all_actions_combined)
        csv_actions = df_all_actions.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Simulation Actions (CSV)",
            data=csv_actions,
            file_name="simulation_actions.csv",
            mime="text/csv"
        )

        # Download Simulation Actions (JSON)
        json_data = json.dumps(results, indent=2)
        st.download_button(
            label="📥 Download Simulation Actions (JSON)",
            data=json_data,
            file_name="simulation_actions.json",
            mime="application/json"
        )