import streamlit as st

def form():
    
    st.markdown(
            "## **Average read depth and coverage calculator**\n"
        )
    with st.form("form"):
        
        st.markdown(
                    "### Analysis Type",
                    help=(
                        "**Please select the type of analysis.**\n"
                        "- This will be mandatory to know where your data is    located.\n"
                        "- The analysis will be performed on data within this   selected analysis.\n"
                        "- Make sure the necessary files for analysis are in the    respective directory."
                    )
                )
        st.radio(
                "Select an option",
                ["Single Gene", "Gene Panel", "Exome"],
                key="analysis",
                label_visibility="visible",
                disabled=False,
                horizontal=True
                )
        
        
        
        
        
        st.markdown(
                    "### Genome Assembly",
                    help=(
                        "**Please select the genome assembly.**\n"
                        "- The selection of a :red[genome assembly] is crucial  for analyzing the sequencing data.\n"
                        "- A :red[genome assembly] defines the reference genome     used for aligning the sequencing reads.\n"
                        "- Ensure that the selected :red[genome assembly]   corresponds to the reference genome used for aligning the     sequencing reads."
                    )
                )
        st.radio(
                "Select an option",
                ["GRCh37/hg19", "GRCh38/hg38"],
                key="assembly",
                label_visibility="visible",
                disabled=False,
                horizontal=True, index=1
                )
        
        
        
        st.markdown(
                        "### Gene of Interest",
                        help=(
                            "**Please select a Gene of Interest.**\n"
                            "- The selection of a :red[Gene of Interest] is     crucial for calculating the :red[average read depth].   \n"
                            "- A :red[Gene of Interest] defines the genomic     region of interest.\n"
                            "- The :red[read depth] will be calculated  specifically for these region.\n"
                            "- Ensure that the selected :red[Gene of Interest]  corresponds to the genomic region you want to analyze.   "
                        )
                    )
        st.selectbox('Select a Gene of Interest', ["x","y","z"], key="gene", index=None, label_visibility="collapsed",placeholder="Select a Gene of Interest")

        
        
        st.markdown(
                    "### BAM file",
                    help=(
                        "**Please select a BAM file.**\n"
                        "- The selection of a :red[BAM file] is essential for   analyzing the sequencing data.\n"
                        "- A :red[BAM file] contains aligned sequencing reads on    the reference genome.\n"
                        "- Ensure that the selected :red[BAM file] corresponds to   the sequencing data you want to analyze."
                    )
                )


    

       # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
    if submitted:
        st.write("slider", "checkbox")

form()