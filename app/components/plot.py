import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import io

def plot_interactive_coverage_from_session(selected_sample, threshold=400, highlight=True):
    """
    Cria um gráfico interativo de profundidade de cobertura utilizando os dados armazenados na sessão do Streamlit.
    Destaca apenas as regiões que estão abaixo do threshold, respeitando os gaps entre posições discontínuas, mas mantendo mean coverage e threshold contínuos.
    """

    # Acessa os dados armazenados na sessão do Streamlit
    bed_content = st.session_state.get('filtered_bed', '')
    depth_dict = st.session_state.get('depth_output', {})

    if not bed_content:
        st.error("No filtered BED content found in session state.")
        return

    if not depth_dict:
        st.error("No depth data found in session state.")
        return

    # Verifica se a amostra selecionada está disponível no depth_dict
    if selected_sample not in depth_dict:
        st.error(f"No data found for the selected sample: {selected_sample}")
        return

    # Carrega os dados de profundidade da amostra selecionada
    depth_content = depth_dict[selected_sample]
    depth_df = pd.read_csv(io.StringIO(depth_content), sep='\t', header=None, names=['CHROM', 'POS', 'DEPTH'])

    # Carrega o arquivo .bed filtrado
    bed_df = pd.read_csv(io.StringIO(bed_content), sep='\t', header=None, names=['CHROM', 'START', 'END', 'GENE', 'EXON', 'SIZE'])

    # Mapear os genes e exons para a profundidade
    depth_df['Gene'] = 'Unknown'
    depth_df['Exon'] = 'Unknown'
    for _, row in bed_df.iterrows():
        mask = (depth_df['POS'] >= row['START']) & (depth_df['POS'] <= row['END'])
        depth_df.loc[mask, 'Gene'] = row['GENE']
        depth_df.loc[mask, 'Exon'] = row['EXON']

    # Detectar gaps nas posições: Se a diferença entre posições consecutivas for maior que 1, haverá um gap
    positions = depth_df['POS'].values
    depths = depth_df['DEPTH'].values
    gene_info = depth_df['Gene'].values
    exon_info = depth_df['Exon'].values

    # Inicializar listas para as posições e profundidades que serão plotadas
    plot_x = []
    plot_y = []
    hover_text = []

    # Preencher listas de forma a adicionar gaps (None) onde há saltos nas posições
    for i in range(len(positions)):
        plot_x.append(positions[i])
        plot_y.append(depths[i])
        hover_text.append(f"Gene: {gene_info[i]}<br>Exon: {exon_info[i]}<br>Pos: {positions[i]}<br>Depth: {depths[i]}")
        if i < len(positions) - 1 and positions[i + 1] - positions[i] > 1:
            plot_x.append(None)  # Adicionar um gap (None) entre posições não contínuas
            plot_y.append(None)
            hover_text.append(None)

    # Criar o gráfico de área com gaps
    trace = go.Scatter(
        x=plot_x,
        y=plot_y,
        mode='lines',
        name='Coverage',
        text=hover_text,
        hoverinfo='text',  # Informações a serem exibidas no hover
        line=dict(color='blue'),
        connectgaps=False  # NÃO conectar gaps
    )

    # Linha de cobertura média (continua, preenchida)
    mean_coverage = depth_df['DEPTH'].mean()
    line_mean = go.Scatter(
        x=plot_x,
        y=[mean_coverage if v is not None else None for v in plot_y],  # Linhas contínuas
        mode='lines',
        name=f'Mean coverage: {mean_coverage:.1f}X',
        line=dict(color='green'),  # Linha preenchida, sem estilo tracejado
        connectgaps=True  # Continuar conectando as posições
    )

    # Linha de limite (continua, preenchida)
    line_threshold = go.Scatter(
        x=plot_x,
        y=[threshold if v is not None else None for v in plot_y],  # Linhas contínuas
        mode='lines',
        name=f'Threshold: {threshold}X',
        line=dict(color='red'),  # Linha preenchida, sem estilo tracejado
        connectgaps=True  # Continuar conectando as posições
    )

    # Lógica para o highlight: Adicionando gaps de acordo com o gráfico de cobertura
    highlight_traces = []
    if highlight:
        # Mesma lógica para lidar com gaps
        for _, exon_row in bed_df.iterrows():
            exon_mask = (depth_df['POS'] >= exon_row['START']) & (depth_df['POS'] <= exon_row['END'])
            below_threshold = (depth_df['DEPTH'] < threshold) & exon_mask  # Verifica se está dentro do exon e abaixo do threshold

            highlight_x = []
            highlight_y = []
            is_below = False

            for i in range(len(positions)):
                pos = positions[i]
                depth = depths[i]

                if below_threshold.iloc[i]:
                    if not is_below:
                        # Começamos uma nova área abaixo do threshold
                        highlight_x.append(pos)  # Início da nova área
                        highlight_y.append(threshold)  # Começa no valor do threshold
                    highlight_x.append(pos)
                    highlight_y.append(depth)
                    is_below = True
                else:
                    if is_below:
                        # Fechar a área anterior
                        highlight_x.append(pos)
                        highlight_y.append(threshold)  # Fecha no valor do threshold
                        highlight_traces.append(
                            go.Scatter(
                                x=highlight_x,
                                y=highlight_y,
                                fill='tozeroy',
                                mode='lines',
                                fillcolor='rgba(255, 0, 0, 0.2)',  # Colocar o highlight à frente
                                line=dict(color='rgba(255,0,0,0)'),
                                name=f'Below Threshold (Exon {exon_row["EXON"]})',
                                connectgaps=False  # NÃO conectar gaps no highlight
                            )
                        )
                        # Resetar as listas para a próxima área
                        highlight_x = []
                        highlight_y = []
                        is_below = False

                # Adicionar um gap quando houver uma posição ausente
                if i < len(positions) - 1 and positions[i + 1] - positions[i] > 1:
                    if is_below:
                        highlight_x.append(None)
                        highlight_y.append(None)
                        is_below = False  # Fechar a área anterior corretamente

    # Criar shapes para marcar as regiões dos exons
    exon_shapes = []
    for _, row in bed_df.iterrows():
        exon_shapes.append(
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
                layer="below",  # Colocar as regiões dos exons atrás do highlight
                line_width=0,
            )
        )

    # Layout do gráfico
    layout = go.Layout(
        title=f'Coverage Plot for {selected_sample}',
        xaxis=dict(title='Position', rangeslider=dict(visible=True)),
        yaxis=dict(title='Depth'),
        hovermode='closest',  # Habilita o hover com as informações mais próximas
        shapes=exon_shapes  # Adiciona as formas dos exons
    )

    # Juntar todos os traços
    traces = [trace, line_mean, line_threshold] + highlight_traces

    # Gerar a figura
    fig = go.Figure(data=traces, layout=layout)
    st.plotly_chart(fig, use_container_width=True)

# Função principal para exibir os gráficos com seleção de amostra
def display_graphs():
    # Verifica se existem dados no session_state
    if 'depth_output' not in st.session_state or not st.session_state['depth_output']:
        st.error("No depth data found in session state.")
        return
    
    # Lista de amostras (chaves do depth_output)
    sample_names = list(st.session_state['depth_output'].keys())

    if not sample_names:
        st.error("No samples available for visualization.")
        return

    # Adiciona a selectbox para selecionar a amostra
    selected_sample = st.selectbox("Select Sample to Visualize", sample_names)

    # Slider para o limiar de cobertura
    threshold = st.slider('Coverage Threshold', min_value=0, max_value=1500, value=400)

    # Checkbox para destacar regiões abaixo do limiar
    highlight = st.checkbox('Highlight regions below threshold', value=True)

    # Chamar a função para plotar o gráfico da amostra selecionada
    plot_interactive_coverage_from_session(selected_sample, threshold, highlight)

