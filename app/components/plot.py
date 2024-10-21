import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import io
import time
import psutil



def plot_interactive_coverage_from_session(selected_sample, threshold=400, highlight=True):
    """
    Creates an interactive coverage depth plot using data stored in Streamlit's session state.
    Highlights all regions below the coverage threshold, respecting gaps between non-contiguous positions
    and maintaining the real coverage values for the highlight.
    
    Parameters:
    - selected_sample (str): The sample name to visualize coverage data.
    - threshold (int): The coverage depth threshold for highlighting low coverage regions.
    - highlight (bool): Whether to highlight regions below the threshold (default: True).
    """
    # Access data from Streamlit session state
    bed_content = st.session_state.get('filtered_bed', '')
    depth_dict = st.session_state.get('depth_output', {})

    if not bed_content:
        st.error("No filtered BED content found in session state.")
        return

    if not depth_dict:
        st.error("No depth data found in session state.")
        return

    if selected_sample not in depth_dict:
        st.error(f"No data found for the selected sample: {selected_sample}")
        return

    # Load the depth data and filtered BED data
    depth_df = pd.read_csv(io.StringIO(depth_dict[selected_sample]), sep='\t', header=None, names=['CHROM', 'POS', 'DEPTH'])
    bed_df = pd.read_csv(io.StringIO(bed_content), sep='\t', header=None, names=['CHROM', 'START', 'END', 'GENE', 'EXON', 'SIZE'])

    # Add gene and exon information to the depth DataFrame without using merge_asof
    depth_df['Gene'] = 'Unknown'
    depth_df['Exon'] = 'Unknown'
    for _, row in bed_df.iterrows():
        mask = (depth_df['POS'] >= row['START']) & (depth_df['POS'] <= row['END'])
        depth_df.loc[mask, 'Gene'] = row['GENE']
        depth_df.loc[mask, 'Exon'] = row['EXON']

    # Prepare for plotting
    plot_x, plot_y, hover_text = [], [], []
    positions, depths = depth_df['POS'].values, depth_df['DEPTH'].values
    gene_info, exon_info = depth_df['Gene'].values, depth_df['Exon'].values

    # Fill lists, adding gaps (None) where positions are non-continuous
    for i in range(len(positions)):
        plot_x.append(positions[i])
        plot_y.append(depths[i])
        hover_text.append(f"Gene: {gene_info[i]}<br>Exon: {exon_info[i]}<br>Pos: {positions[i]}<br>Depth: {depths[i]}")
        if i < len(positions) - 1 and positions[i + 1] - positions[i] > 1:
            plot_x.append(None)  # Add gap (None) between non-continuous positions
            plot_y.append(None)
            hover_text.append(None)

    # Create main coverage trace
    coverage_trace = go.Scatter(
        x=plot_x,
        y=plot_y,
        mode='lines',
        name='Depth',
        text=hover_text,
        hoverinfo='text',
        line=dict(color='blue'),
        connectgaps=False  # Do NOT connect gaps
    )

    # Create mean coverage line
    mean_coverage = depth_df['DEPTH'].mean()
    mean_line = go.Scatter(
        x=[min(positions), max(positions)],
        y=[mean_coverage, mean_coverage],
        mode='lines',
        name=f'Average Read Depth: {mean_coverage:.1f}X',
        line=dict(color='green'),
        connectgaps=False  # Constant horizontal line
    )

    # Create threshold line
    threshold_line = go.Scatter(
        x=[min(positions), max(positions)],
        y=[threshold, threshold],
        mode='lines',
        name=f'Threshold: {threshold}X',
        line=dict(color='red'),
        connectgaps=False  # Constant horizontal line
    )

    # Highlight regions below the threshold
    highlight_traces, highlight_x, highlight_y = [], [], []
    show_legend_once = True  # Control to show "Below Threshold" legend only once

    for i in range(len(positions)):
        pos, depth = plot_x[i], plot_y[i]
        if depth is not None and depth <= threshold:
            highlight_x.append(pos)
            highlight_y.append(depth)
        else:
            if highlight_x:
                highlight_traces.append(
                    go.Scatter(
                        x=highlight_x,
                        y=[threshold if v is not None else None for v in plot_y],
                        fill='tozeroy',
                        mode='lines',
                        fillcolor='rgba(255, 0, 0, 0.2)',  # Highlight color
                        line=dict(color='rgba(255,0,0,0)'),
                        name='Below Threshold' if show_legend_once else None,
                        showlegend=show_legend_once,
                        connectgaps=False  # Do NOT connect gaps in the highlight
                    )
                )
                # Reset highlight lists for the next segment
                highlight_x, highlight_y = [], []
                show_legend_once = False  # Disable further legend entries

    # Add the last highlight trace if applicable
    if highlight_x:
        highlight_traces.append(
            go.Scatter(
                x=highlight_x,
                y=highlight_y,
                fill='tozeroy',
                mode='lines',
                fillcolor='rgba(255, 0, 0, 0.2)',
                line=dict(color='rgba(255,0,0,0)'),
                name='Below Threshold' if show_legend_once else None,
                showlegend=show_legend_once,
                connectgaps=False
            )
        )

    # Define shapes for exon regions
    exon_shapes = [
        dict(
            type="rect",
            xref="x",
            yref="paper",
            x0=row['START'],
            x1=row['END'],
            y0=0,
            y1=1,
            fillcolor="LightSkyBlue",
            opacity=0.3,
            layer="below",  # Render exon regions behind highlights
            line_width=0
        ) for _, row in bed_df.iterrows()
    ]

    # Set up the layout
    layout = go.Layout(
        title=f'Depth of Coverage Plot for {selected_sample}',
        xaxis=dict(title='Position', rangeslider=dict(visible=True)),
        yaxis=dict(title='Depth'),
        hovermode='closest',
        shapes=exon_shapes  # Add exon region shapes
    )

    # Create an invisible trace for the exon legend
    exon_legend_trace = go.Scatter(
        x=[None], y=[None],
        mode='lines',
        line=dict(color='LightSkyBlue'),
        fillcolor='LightSkyBlue',
        name='Exon',
        showlegend=True
    )
    
    # Compile all traces
    traces = [coverage_trace, mean_line, threshold_line, exon_legend_trace] + highlight_traces


    # Create and display the figure
    fig = go.Figure(data=traces, layout=layout)
    st.plotly_chart(fig, use_container_width=True)

@st.fragment
def display_graphs():
    """
    Main function to display the coverage graphs. Prompts the user to select a sample
    and input a coverage threshold, then generates the corresponding coverage plot.
    """
    # Ensure data exists in session_state
    if 'depth_output' not in st.session_state or not st.session_state['depth_output']:
        st.error("No depth data found in session state.")
        return

    # List available sample names from the depth output
    sample_names = list(st.session_state['depth_output'].keys())
    
    if not sample_names:
        st.error("No samples available for visualization.")
        return

    # Select sample to visualize
    selected_sample = st.selectbox("Select Sample to Visualize", sample_names, key="sample_plot")

    # Input for threshold adjustment
    threshold = st.number_input('Depth of Coverage Threshold', min_value=0, max_value=1000, value=500, step=10)

    # Call the function to plot the selected sample's coverage graph
    with st.spinner('Wait for it... Getting plot ready...'):
        plot_interactive_coverage_from_session(selected_sample, threshold, True)
