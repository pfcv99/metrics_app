import streamlit as st
import json
import os

st.title("Settings")

DEFAULTS_FILE = '.streamlit/defaults.json'

# Original default settings
ORIGINAL_DEFAULTS = {
    'GRCh38_hg38': 'data/regions/genome_exons/hg38_Twist_ILMN_Exome_2.0_Plus_Panel_annotated_modif_nochr.bed',
    'GRCh37_hg19': 'data/regions/genome_exons/hg19_Twist_ILMN_Exome_2.0_Plus_Panel_annotated_modif_nochr.BED',
    'depth_single_gene': 'data/depth/single_gene',
    'depth_gene_panel': 'data/depth/gene_panel',
    'depth_exome': 'data/depth/exome',
    'bam_cram_path': "./data/mapped"
}

def load_defaults():
    # If the defaults file exists, load it
    if os.path.exists(DEFAULTS_FILE):
        with open(DEFAULTS_FILE, 'r') as f:
            defaults = json.load(f)
    else:
        # Otherwise, use the original defaults and save them to file
        defaults = ORIGINAL_DEFAULTS.copy()
        with open(DEFAULTS_FILE, 'w') as f:
            json.dump(defaults, f)
    return defaults

def save_settings():
    # Update defaults and save to file
    keys = ['GRCh38_hg38', 'GRCh37_hg19', 'depth_single_gene', 'depth_gene_panel', 'depth_exome', 'bam_cram_path']
    new_defaults = {key: st.session_state[key] for key in keys}
    with open(DEFAULTS_FILE, 'w') as f:
        json.dump(new_defaults, f)
    st.success('Settings saved successfully!')
    # Update initial_values in session state
    st.session_state['initial_values'] = new_defaults.copy()

def restore_defaults():
    # Restore settings to original defaults
    with open(DEFAULTS_FILE, 'w') as f:
        json.dump(ORIGINAL_DEFAULTS, f)
    # Set a flag to reset session state
    st.session_state['reset_settings'] = True
    st.success('Settings restored to original defaults!')
    # Rerun the app to update widgets
    st.rerun()

# Function to check if settings have changed
def settings_changed():
    initial_values = st.session_state.get('initial_values', {})
    keys = ['GRCh38_hg38', 'GRCh37_hg19', 'depth_single_gene', 'depth_gene_panel', 'depth_exome', 'bam_cram_path']
    for key in keys:
        if st.session_state.get(key, '') != initial_values.get(key, ''):
            return True
    return False

# Initialize session state
if 'reset_settings' in st.session_state and st.session_state['reset_settings']:
    # Reset session state variables to defaults
    defaults = load_defaults()
    for key, value in defaults.items():
        st.session_state[key] = value
    st.session_state['initial_values'] = defaults.copy()
    st.session_state['reset_settings'] = False
else:
    if 'initial_values' not in st.session_state:
        defaults = load_defaults()
        st.session_state['initial_values'] = defaults.copy()
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

# Create text inputs bound to session state
GRCh38_hg38_value = st.text_input(label="GRCh38/hg38 file path", key='GRCh38_hg38')
GRCh37_hg19_value = st.text_input(label="GRCh37/hg19 file path", key='GRCh37_hg19')
depth_single_gene_value = st.text_input(label="Depth Single Gene file path", key='depth_single_gene')
depth_gene_panel_value = st.text_input(label="Depth Gene Panel file path", key='depth_gene_panel')
depth_exome_value = st.text_input(label="Depth Exome file path", key='depth_exome')
bam_cram_value = st.text_input(label="BAM/CRAM file path", key='bam_cram_path')

# Show buttons only if settings have changed
if settings_changed():
    if st.button('Save Settings'):
        save_settings()
    if st.button('Restore Defaults', type='primary'):
        restore_defaults()
