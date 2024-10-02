import streamlit as st
from components import streamlit_page_config

# Set Streamlit page configuration
streamlit_page_config.set_page_configuration()

sidebar_logo = "data/img/unilabs_logo.png"
main_body_logo = "data/img/thumbnail_image001.png"
st.logo(sidebar_logo, size="large", icon_image=main_body_logo)

# Authors Section
st.title("Authors")
st.write("- **Pedro Filipe Carneiro Venâncio** | [pedrofcvenancio@ua.pt](mailto:pedrofcvenancio@ua.pt)")
st.write("- **Contributors**: Alexandra Lopes, Gabriela Moura, Ricardo Pais, Béryl Royer-Bertrand, Alberto Pessoa, Unilabs Genetics Team")

# Divider for visual separation
st.markdown("---")

# Changelog Section
st.subheader("Changelog")
st.write("""
- **v1.0.0**: Initial release of the Metrics App.
""")

# Divider for visual separation
st.markdown("---")

# Resources Section
st.subheader("Resources")
st.write("""
- **Documentation**: [Link to detailed documentation]
- **Repository**: [GitHub Repository](https://github.com/pfcv99/metrics_app)
- **Contact Support**: For support, please contact [pedrofcvenancio@ua.pt](mailto:pedrofcvenancio@ua.pt).
""")

# Footer Section (optional)
st.markdown("---")
st.write("© 2024 Metrics App | Developed by Pedro Filipe Carneiro Venâncio")
