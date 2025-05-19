import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import json
import os
from fpdf import FPDF
from io import BytesIO

TEMPLATE_FILE = "saved_templates.json"

class HomeostaticResilienceModel:
    def __init__(self):
        self.system_dimensions = {
            'ecological': {},
            'social': {},
            'economic': {},
            'institutional': {}
        }

        self.sdg_targets = {
            'ecological': ['SDG 6', 'SDG 7', 'SDG 12', 'SDG 13', 'SDG 15'],
            'social': ['SDG 1', 'SDG 3', 'SDG 4', 'SDG 5', 'SDG 10', 'SDG 11'],
            'economic': ['SDG 8', 'SDG 9'],
            'institutional': ['SDG 16', 'SDG 17']
        }

        self.feedback_loops = []

        self.thresholds = {
            'carbon_budget': 1.5,
            'housing_affordability_index': 0.3,
            'job_creation_rate': 0.05
        }

        self.system_state = {
            'carbon_emissions': 0,
            'affordable_housing_units': 0,
            'green_jobs_created': 0,
            'policy_adaptability_score': 0,
            'community_participation_score': 0
        }

        self.history = []

    def add_intervention(self, name, impacts):
        intervention_result = {'name': name, 'timestamp': datetime.datetime.now()}
        for key, value in impacts.items():
            if key in self.system_state:
                self.system_state[key] += value
                intervention_result[key] = self.system_state[key]
        self.history.append(intervention_result)

    def assess_homeostasis(self):
        report = {}
        for metric, threshold in self.thresholds.items():
            if metric in self.system_state:
                state_val = self.system_state[metric]
                report[metric] = {
                    'value': state_val,
                    'threshold': threshold,
                    'status': 'stable' if state_val <= threshold else 'unstable'
                }
        return report

    def sdg_alignment_score(self):
        sdg_scores = {sdg: 0 for group in self.sdg_targets.values() for sdg in group}
        sdg_scores['SDG 13'] = max(0, 100 - self.system_state['carbon_emissions'] / 1000)
        sdg_scores['SDG 11'] = self.system_state['affordable_housing_units'] / 100
        sdg_scores['SDG 8'] = self.system_state['green_jobs_created'] / 10
        return sdg_scores

    def get_history_dataframe(self):
        return pd.DataFrame(self.history)

def load_templates():
    if os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_templates(templates):
    with open(TEMPLATE_FILE, 'w') as file:
        json.dump(templates, file, indent=2)

# Streamlit Dashboard
model = HomeostaticResilienceModel()

st.title("Homeostatic Resilience Policy Dashboard")

st.sidebar.header("Select Policy Template")
templates = {
    "Aggressive Decarbonization": {'carbon_emissions': -50000, 'affordable_housing_units': 5000, 'green_jobs_created': 200, 'policy_adaptability_score': 0.3, 'community_participation_score': 0.2},
    "Green Housing & Jobs": {'carbon_emissions': -20000, 'affordable_housing_units': 10000, 'green_jobs_created': 750, 'policy_adaptability_score': 0.15, 'community_participation_score': 0.25},
    "Community-Led Retrofits": {'carbon_emissions': -10000, 'affordable_housing_units': 3000, 'green_jobs_created': 500, 'policy_adaptability_score': 0.2, 'community_participation_score': 0.4}
}
templates.update(load_templates())

custom_template_name = st.sidebar.text_input("Create Custom Template Name")
if custom_template_name:
    if st.sidebar.button("Save Current as Template"):
        templates[custom_template_name] = {
            'carbon_emissions': st.session_state.get('carbon', -10000),
            'affordable_housing_units': st.session_state.get('housing', 5000),
            'green_jobs_created': st.session_state.get('jobs', 300),
            'policy_adaptability_score': st.session_state.get('adaptability', 0.2),
            'community_participation_score': st.session_state.get('participation', 0.2)
        }
        save_templates(templates)
        st.sidebar.success(f"Template '{custom_template_name}' saved.")

edit_template = st.sidebar.selectbox("Edit Existing Template", list(load_templates().keys()) + ["None"])
if edit_template != "None":
    if st.sidebar.button("Delete Selected Template"):
        current_templates = load_templates()
        if edit_template in current_templates:
            del current_templates[edit_template]
            save_templates(current_templates)
            st.sidebar.success(f"Template '{edit_template}' deleted. Please refresh to update template list.")

selected_template = st.sidebar.selectbox("Choose Template", list(templates.keys()))
impacts = templates[selected_template]

carbon = st.sidebar.number_input("Carbon Emissions Reduction", key='carbon', value=impacts['carbon_emissions'])
housing = st.sidebar.number_input("Affordable Housing Units", key='housing', value=impacts['affordable_housing_units'])
jobs = st.sidebar.number_input("Green Jobs Created", key='jobs', value=impacts['green_jobs_created'])
adaptability = st.sidebar.slider("Policy Adaptability", 0.0, 1.0, impacts['policy_adaptability_score'], key='adaptability')
participation = st.sidebar.slider("Community Participation", 0.0, 1.0, impacts['community_participation_score'], key='participation')

if st.sidebar.button("Evaluate Intervention"):
    impacts = {
        'carbon_emissions': carbon,
        'affordable_housing_units': housing,
        'green_jobs_created': jobs,
        'policy_adaptability_score': adaptability,
        'community_participation_score': participation
    }
    model.add_intervention(selected_template, impacts)

    st.subheader("System Homeostasis Status")
    st.json(model.assess_homeostasis())

    st.subheader("SDG Alignment Score")
    sdg_scores = model.sdg_alignment_score()
    st.json(sdg_scores)

    st.subheader("SDG Impact Chart")
    sdg_df = pd.DataFrame.from_dict(sdg_scores, orient='index', columns=['Score'])
    st.bar_chart(sdg_df)

    st.subheader("System State Over Time")
    history_df = model.get_history_dataframe()
    if not history_df.empty:
        for column in ['carbon_emissions', 'affordable_housing_units', 'green_jobs_created']:
            st.line_chart(history_df.set_index('timestamp')[[column]])

    st.subheader("Export Data")
    if st.button("Download CSV Report"):
        csv = history_df.to_csv(index=False)
        st.download_button("Download CSV", data=csv, file_name='hrf_policy_simulation.csv', mime='text/csv')

    if st.button("Download PDF Report"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="HRF Policy Simulation Report", ln=True, align='C')
        for index, row in history_df.iterrows():
            for col in history_df.columns:
                pdf.cell(200, 10, txt=f"{col}: {row[col]}", ln=True)
            pdf.cell(200, 10, txt="---", ln=True)
        buffer = BytesIO()
        pdf.output(buffer)
        st.download_button("Download PDF", data=buffer.getvalue(), file_name="hrf_report.pdf", mime='application/pdf')
