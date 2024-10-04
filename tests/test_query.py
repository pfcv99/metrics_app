import pytest
import streamlit as st
from unittest.mock import MagicMock, patch
from app.app_pages.query import panel
from app.components import forms

@pytest.fixture
def mock_session_state(monkeypatch):
    """Fixture to mock session state for different scenarios."""
    session_state_mock = MagicMock()
    session_state_mock.analysis = None
    monkeypatch.setattr(st, 'session_state', session_state_mock)
    return session_state_mock

@pytest.fixture
def mock_tabs(monkeypatch):
    """Fixture to mock Streamlit tabs."""
    tab_mock = MagicMock()
    monkeypatch.setattr(st, 'tabs', lambda titles: [tab_mock, tab_mock, tab_mock])
    return tab_mock

def test_page_setup(mock_session_state, mock_tabs, monkeypatch):
    """Test the page configuration and main page setup."""
    
    # Mock the set_page_configuration and logo rendering
    monkeypatch.setattr('components.streamlit_page_config.set_page_configuration', lambda: None)
    monkeypatch.setattr(st, 'logo', lambda *args, **kwargs: None)

    # Mock forms
    monkeypatch.setattr(forms, 'single_gene', lambda: None)
    monkeypatch.setattr(forms, 'gene_panel', lambda: None)
    monkeypatch.setattr(forms, 'exome', lambda: None)
    
    # Mock genome panel
    monkeypatch.setattr('components.genome.panel', lambda: ['BRCA1', 'BRCA2', 'TP53'])

    # Import and run the query page
    from app_pages import query

    # Assertions
    assert st.session_state.analysis == 'Single Gene'
    
    # Check if forms.single_gene() is called in tab1
    forms.single_gene.assert_called_once()

    # Switch to tab2 (Gene Panel)
    assert st.session_state.analysis == 'Gene Panel'
    forms.gene_panel.assert_called_once()

    # Switch to tab3 (Exome)
    assert st.session_state.analysis == 'Exome'
    forms.exome.assert_called_once()

def test_tab_rendering(mock_session_state, mock_tabs, monkeypatch):
    """Test rendering of the three tabs and session state updates."""
    # Mock the forms
    monkeypatch.setattr(forms, 'single_gene', lambda: None)
    monkeypatch.setattr(forms, 'gene_panel', lambda: None)
    monkeypatch.setattr(forms, 'exome', lambda: None)
    
    # Import and run the query page
    from app_pages import query
    
    # Assert tabs and session state values after switching tabs
    assert st.session_state.analysis == 'Single Gene'
    forms.single_gene.assert_called_once()

    # Simulate switching to tab2
    st.session_state.analysis = 'Gene Panel'
    forms.gene_panel.assert_called_once()

    # Simulate switching to tab3
    st.session_state.analysis = 'Exome'
    forms.exome.assert_called_once()
