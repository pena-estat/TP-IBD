import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuração da Página
st.set_page_config(page_title="Trabalho Prático 2 - BPS", layout="wide")
st.title("🏥 Banco de Preços em Saúde (BPS)")
st.markdown("Trabalho Prático 2 — Introdução a Banco de Dados")

# 2. Conexão com o Banco de Dados (Aqui é onde a variável 'conn' é criada!)
@st.cache_resource
def conectar_banco():
    return sqlite3.connect('trabalho_pratico_2.db', check_same_thread=False)

conn = conectar_banco()

st.divider()

# 3. Criando as Abas do Aplicativo
aba1, aba2, aba3, aba4, aba5, aba6, aba7, aba8, aba9, aba10, aba11, aba12 = st.tabs([
    "1. Genéricos", 
    "2. Instituições", 
    "3. Volumes de Compras", 
    "4. Variedade Prod.", 
    "5. Desempenho", 
    "6. Detalhamento",
    "7. Modalidades",
    "8. Portfólio Ativo ",
    "9. Status",
    "10. Regional MG",
    "11. Megacompras",
    "12. Fluxo 2026"
])

# ==========================================
# ABA 1: CONSULTA 1 E GRÁFICO INTERATIVO
# ==========================================
with aba1:
    st.header("Consulta 1 — Produtos Genéricos")
    st.markdown("Visão geral sobre a distribuição de produtos genéricos no BPS.")
    
    # Tabela
    query_tabela = """
    SELECT codigo_br, descricao_catmat, unidade_medida
    FROM Produto WHERE generico = 'S' ORDER BY descricao_catmat LIMIT 20;
    """
    df_tabela = pd.read_sql_query(query_tabela, conn)
    
    st.subheader("Amostra de Produtos Genéricos")
    st.dataframe(df_tabela, width="stretch")
    
    st.divider()
    
    # Gráfico (agrupando os dados com SQL)
    query_grafico = """
    SELECT generico, COUNT(*) as quantidade
    FROM Produto
    WHERE generico IN ('S','N')
    GROUP BY generico
    """
    df_grafico = pd.read_sql_query(query_grafico, conn)
    
    st.subheader("Distribuição: Genéricos vs Não Genéricos")
    
    # Criando o gráfico interativo
    fig = px.pie(
        df_grafico, 
        names='generico', 
        values='quantidade',
        title="Proporção de Produtos no Catálogo",
        color_discrete_sequence=['#0083B8', '#ECE81A']
    )
    
    st.plotly_chart(fig, width="stretch")

# ==========================================
# ABA 2: INSTITUIÇÕES POR UF E ESFERA
# ==========================================
with aba2:
    st.header("Consulta 2 — Instituições por UF e Esfera")
    st.markdown("Análise da quantidade de instituições de saúde registradas, detalhando a distribuição por Estado e Esfera governamental.")
    
    # 1. Query e Leitura dos Dados
    query2 = """
    SELECT uf,
           esfera,
           COUNT(*) as total_instituicoes
    FROM Instituicao
    GROUP BY uf, esfera
    ORDER BY total_instituicoes DESC
    LIMIT 20;
    """
    df2 = pd.read_sql_query(query2, conn)
    
    # 2. Exibição da Tabela
    st.subheader("Tabela de Resultados")
    st.dataframe(df2, width="stretch")
    
    st.divider()
    
    # 3. Gráfico Interativo (Treemap)
    st.subheader("Proporção de Instituições (Treemap)")
    
    fig2 = px.treemap(
        df2, 
        path=[px.Constant("Brasil"), 'uf', 'esfera'], # Define a hierarquia de navegação do gráfico
        values='total_instituicoes',                  # Define o tamanho dos blocos
        color='total_instituicoes',                   # Aplica uma escala de cores baseada no total
        color_continuous_scale='Blues',               # Escala de cores profissional
        title="Distribuição de Instituições (UF > Esfera)"
    )
    
    # Pequeno ajuste de margens para o gráfico ocupar bem o espaço
    fig2.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    
    # Renderiza o gráfico
    st.plotly_chart(fig2, width="stretch")

# ==========================================
# ABA 3: TOP 15 INSTITUIÇÕES COMPRADORAS
# ==========================================
with aba3:
    st.header("Consulta 3 — Top 15 Instituições (Volume de Compras)")
    st.markdown("Ranking das instituições de saúde com o maior número de registros de compras no sistema.")
    
    # 1. Query e Leitura dos Dados
    query3 = """
    SELECT I.nome_instituicao,
           I.uf,
           I.esfera,
           COUNT(C.id_compra) as total_compras
    FROM Instituicao I
    JOIN Compra C ON I.cnpj_instituicao = C.cnpj_instituicao
    GROUP BY I.cnpj_instituicao
    ORDER BY total_compras DESC
    LIMIT 15;
    """
    df3 = pd.read_sql_query(query3, conn)
    
    # 2. Exibição da Tabela
    st.subheader("Tabela do Ranking")
    st.dataframe(df3, width="stretch")
    
    st.divider()
    
    # 3. Gráfico Interativo (Barras Horizontais com legenda de cor)
    st.subheader("Ranking Visual")
    
    # Para o gráfico horizontal ficar do maior (topo) para o menor (base), 
    # precisamos inverter a ordem do dataframe especificamente para o Plotly
    df3_grafico = df3.sort_values('total_compras', ascending=True)
    
    fig3 = px.bar(
        df3_grafico,
        x='total_compras',
        y='nome_instituicao',
        color='esfera',         # Aplica cores diferentes baseadas na esfera (Federal, Estadual, etc)
        orientation='h',        # Transforma em barras horizontais
        title="Volume de Compras por Instituição (Top 15)",
        labels={
            'total_compras': 'Total de Compras', 
            'nome_instituicao': 'Instituição', 
            'esfera': 'Esfera'
        },
        color_discrete_sequence=px.colors.qualitative.Bold # Paleta de cores mais forte
    )
    
    # Ajustes visuais para deixar com cara de ferramenta de BI
    fig3.update_layout(
        height=600,            # Aumenta a altura para os nomes não ficarem espremidos
        xaxis_title="Quantidade de Compras Registradas",
        yaxis_title=None,      # Remove o título do eixo Y para ficar mais limpo
        margin=dict(l=20)      # Ajusta a margem esquerda
    )
    
    # Renderiza o gráfico
    st.plotly_chart(fig3, width="stretch")

# ==========================================
# ABA 4: FABRICANTES POR QUANTIDADE DE PRODUTOS
# ==========================================
with aba4:
    st.header("Consulta 4 — Variedade de Produtos por Fabricante")
    st.markdown("Ranking dos fabricantes que possuem a maior diversidade de produtos cadastrados no sistema.")
    
    # 1. Query e Leitura dos Dados
    query4 = """
    SELECT F.fabricante,
           COUNT(P.codigo_br) as qtd_produtos
    FROM Fabricante F
    JOIN Produto P ON F.cnpj_fabricante = P.cnpj_fabricante
    GROUP BY F.cnpj_fabricante
    ORDER BY qtd_produtos DESC
    LIMIT 15;
    """
    df4 = pd.read_sql_query(query4, conn)
    
    # 2. Exibição da Tabela
    st.subheader("Tabela de Fabricantes")
    st.dataframe(df4, width="stretch")
    
    st.divider()
    
    # 3. Gráfico Interativo (Funil)
    st.subheader("Concentração de Produtos (Funil)")
    
    fig4 = px.funnel(
        df4,
        y='fabricante',        # Eixo vertical com os nomes
        x='qtd_produtos',      # Largura do funil baseada na quantidade
        title="Top 15 Fabricantes no Catálogo",
        labels={
            'fabricante': 'Fabricante', 
            'qtd_produtos': 'Total de Produtos'
        },
        color_discrete_sequence=['#FF7F0E'] # Uma cor alaranjada para dar contraste com os anteriores
    )
    
    # Ajustando a altura para os nomes ficarem bem espaçados e legíveis
    fig4.update_layout(height=600)
    
    # Renderiza o gráfico
    st.plotly_chart(fig4, width="stretch")

# ==========================================
# ABA 5: DESEMPENHO DOS FORNECEDORES
# ==========================================
with aba5:
    st.header("Consulta 5 — Faturamento e Pedidos por Fornecedor")
    st.markdown("Análise dos 15 maiores fornecedores em faturamento, relacionando o volume de pedidos e o preço médio dos produtos.")
    
    # 1. Query e Leitura dos Dados
    query5 = """
    SELECT F.fornecedor,
           COUNT(IC.id_compra)    as total_pedidos,
           SUM(IC.preco_total)    as faturamento_total,
           AVG(IC.preco_unitario) as preco_medio_unitario
    FROM Fornecedor F
    JOIN Item_Compra IC ON F.cnpj_fornecedor = IC.cnpj_fornecedor
    GROUP BY F.cnpj_fornecedor
    ORDER BY faturamento_total DESC
    LIMIT 15;
    """
    df5 = pd.read_sql_query(query5, conn)
    
    # Arredondando os valores financeiros
    df5['faturamento_total'] = df5['faturamento_total'].round(2)
    df5['preco_medio_unitario'] = df5['preco_medio_unitario'].round(2)
    
    # 2. Exibição da Tabela (com formatação de moeda)
    st.subheader("Tabela de Faturamento")
    st.dataframe(
        df5, 
        width="stretch",
        column_config={
            "faturamento_total": st.column_config.NumberColumn("Faturamento Total (R$)", format="R$ %.2f"),
            "preco_medio_unitario": st.column_config.NumberColumn("Preço Médio (R$)", format="R$ %.2f")
        }
    )
    
    st.divider()
    
    # 3. Gráfico Interativo (Bolhas)
    st.subheader("Relação: Pedidos vs Faturamento (Tamanho = Preço Médio)")
    
    fig5 = px.scatter(
        df5,
        x='total_pedidos',
        y='faturamento_total',
        size='preco_medio_unitario',     # O preço médio define o tamanho da bolha
        color='faturamento_total',       # Aplica um gradiente de cor baseado em quem fatura mais
        hover_name='fornecedor',         # Mostra o nome do fornecedor ao passar o mouse
        color_continuous_scale='Teal',   # Paleta de cores em tons de verde/azul
        title="Top 15 Fornecedores (Bolhas maiores = Preço Médio maior)",
        labels={
            'total_pedidos': 'Volume de Pedidos',
            'faturamento_total': 'Faturamento Total (R$)',
            'preco_medio_unitario': 'Preço Médio (R$)'
        },
        size_max=40 # Tamanho máximo para a maior bolha não cobrir a tela toda
    )
    
    # Ajustes visuais
    fig5.update_layout(height=600)
    
    # Renderiza o gráfico
    st.plotly_chart(fig5, width="stretch")

# ==========================================
# ABA 6: DETALHAMENTO DAS MAIORES COMPRAS
# ==========================================
with aba6:
    st.header("Consulta 6 — Raio-X das Maiores Compras")
    st.markdown("Análise detalhada dos maiores gastos: navegando da Instituição compradora, passando pelo Fabricante, até o Produto específico.")
    
    # 1. Query e Leitura dos Dados
    query6 = """
    SELECT I.nome_instituicao,
           I.uf,
           P.descricao_catmat,
           F.fabricante,
           SUM(IC.qtd_itens_comprados) as qtd_total,
           ROUND(SUM(IC.preco_total), 2) as gasto_total
    FROM Item_Compra IC
    JOIN Compra      C ON IC.id_compra       = C.id_compra
    JOIN Instituicao I ON C.cnpj_instituicao = I.cnpj_instituicao
    JOIN Produto     P ON IC.codigo_br       = P.codigo_br
    JOIN Fabricante  F ON P.cnpj_fabricante  = F.cnpj_fabricante
    GROUP BY I.cnpj_instituicao, P.codigo_br, F.cnpj_fabricante
    ORDER BY gasto_total DESC
    LIMIT 15;
    """
    df6 = pd.read_sql_query(query6, conn)
    
    # 2. Exibição da Tabela com Formatação
    st.subheader("Tabela Consolidada (Top 15 Gastos)")
    st.dataframe(
        df6, 
        width="stretch",
        column_config={
            "gasto_total": st.column_config.NumberColumn("Gasto Total (R$)", format="R$ %.2f")
        }
    )
    
    st.divider()
    
    # 3. Gráfico Interativo (Sunburst)
    st.subheader("Fluxo de Gastos (Clique nas fatias para explorar)")
    
    # O px.sunburst cria a hierarquia de dentro para fora
    fig6 = px.sunburst(
        df6,
        path=['nome_instituicao', 'fabricante', 'descricao_catmat'], # Caminho da navegação
        values='gasto_total',                                        # Tamanho das fatias
        color='gasto_total',                                         # Cor baseada no valor
        color_continuous_scale='Purpor',                             # Paleta em tons de roxo
        title="Distribuição do Gasto: Instituição > Fabricante > Produto"
    )
    
    # Ajustes visuais para melhorar a leitura dos textos longos
    fig6.update_layout(
        height=700,
        margin=dict(t=40, l=10, r=10, b=10)
    )
    
    # Renderiza o gráfico
    st.plotly_chart(fig6, width="stretch")

# ==========================================
# ABA 7: MODALIDADE DE COMPRA POR UF
# ==========================================
with aba7:
    st.header("Consulta 7 — Gastos por Modalidade e UF")
    st.markdown("Cruzamento das modalidades de licitação/compra com os Estados (UF), destacando onde há maior concentração de gastos.")
    
    # 1. Query e Leitura dos Dados
    query7 = """
    SELECT C.modalidade_compra,
           I.uf,
           COUNT(IC.id_compra)           as total_itens,
           ROUND(AVG(IC.preco_unitario), 2) as preco_medio,
           ROUND(SUM(IC.preco_total), 2)    as gasto_total
    FROM Item_Compra IC
    JOIN Compra      C ON IC.id_compra       = C.id_compra
    JOIN Instituicao I ON C.cnpj_instituicao = I.cnpj_instituicao
    GROUP BY C.modalidade_compra, I.uf
    ORDER BY gasto_total DESC
    LIMIT 20;
    """
    df7 = pd.read_sql_query(query7, conn)
    
    # 2. Exibição da Tabela com múltiplas formatações numéricas
    st.subheader("Tabela de Modalidades (Top 20 Gastos)")
    st.dataframe(
        df7, 
        width="stretch",
        column_config={
            "preco_medio": st.column_config.NumberColumn("Preço Médio (R$)", format="R$ %.2f"),
            "gasto_total": st.column_config.NumberColumn("Gasto Total (R$)", format="R$ %.2f"),
            "total_itens": st.column_config.NumberColumn("Qtd. de Itens")
        }
    )
    
    st.divider()
    
    # 3. Gráfico Interativo (Mapa de Calor)
    st.subheader("Concentração Financeira: Modalidade vs Estado")
    
    # px.density_heatmap funciona perfeitamente como uma matriz visual para os dados agrupados
    fig7 = px.density_heatmap(
        df7,
        x='uf',                      # Eixo X para os Estados
        y='modalidade_compra',       # Eixo Y para os tipos de compra
        z='gasto_total',             # A cor será baseada no valor do gasto total
        histfunc='sum',              # Mantém o valor exato, já que somamos no SQL
        color_continuous_scale='Viridis', # Paleta de cores clássica para mapas de calor
        title="Intensidade de Gasto (Cores mais claras = Maior Gasto)",
        labels={
            'uf': 'Estado (UF)',
            'modalidade_compra': 'Modalidade',
            'gasto_total': 'Gasto Total (R$)'
        }
    )
    
    # Ajustes visuais para melhorar os blocos do mapa de calor
    fig7.update_layout(
        height=600,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    # Renderiza o gráfico
    st.plotly_chart(fig7, width="stretch")

# ==========================================
# ABA 8: FABRICANTES ATIVOS E PRODUTOS
# ==========================================
with aba8:
    st.header("Consulta 8 — Portfólio de Fabricantes Ativos")
    st.markdown("Análise dos fabricantes que se mantiveram ativos no último ano e possuem um portfólio amplo (mais de 10 produtos distintos cadastrados).")
    
    # 1. Query e Leitura dos Dados
    query8 = """
    SELECT cnpj_fabricante, 
           fabricante, 
           qtd_produtos_distintos
    FROM Fabricante
    WHERE ativo_ano_anterior = 'Sim' 
      AND qtd_produtos_distintos > 10
    ORDER BY qtd_produtos_distintos DESC;
    """
    df8 = pd.read_sql_query(query8, conn)
    
    # 2. Exibição da Tabela Completa
    st.subheader("Lista Completa de Fabricantes")
    st.dataframe(
        df8, 
        width="stretch",
        column_config={
            "qtd_produtos_distintos": st.column_config.NumberColumn("Qtd. de Produtos")
        }
    )
    
    st.divider()
    
    # 3. Gráfico Interativo (Barras Polares)
    st.subheader("Top 15 Maiores Portfólios (Gráfico Polar)")
    
    # Separamos os 15 primeiros apenas para o gráfico ficar legível e elegante
    df8_grafico = df8.head(15)
    
    # px.bar_polar desenha as barras em um eixo circular
    fig8 = px.bar_polar(
        df8_grafico, 
        r='qtd_produtos_distintos',   # O tamanho da barra saindo do centro (Raio)
        theta='fabricante',           # A categoria ao redor do círculo (Ângulo)
        color='qtd_produtos_distintos', # A cor baseada no tamanho do portfólio
        color_continuous_scale='Magma', # Uma paleta vibrante de fogo/roxo
        title="Volume de Produtos Distintos (Top 15)",
        labels={
            'fabricante': 'Fabricante',
            'qtd_produtos_distintos': 'Qtd. de Produtos'
        }
    )
    
    # Ajustes de design para o gráfico preencher bem a tela
    fig8.update_layout(
        height=650,
        polar=dict(
            radialaxis=dict(visible=True, showticklabels=True)
        )
    )
    
    # Renderiza o gráfico
    st.plotly_chart(fig8, width="stretch")
# ==========================================
# ABA 9: PRODUTOS E STATUS DO FABRICANTE
# ==========================================
with aba9:
    st.header("Consulta 9 — Produtos e Status do Fabricante")
    st.markdown("Listagem de produtos detalhando seus fabricantes e o status de atividade no ano anterior.")
    
    # 1. Query e Leitura dos Dados
    query9 = """
    SELECT P.codigo_br, 
           P.descricao_catmat, 
           F.fabricante, 
           F.ativo_ano_anterior
    FROM Produto P
    JOIN Fabricante F ON P.cnpj_fabricante = F.cnpj_fabricante
    WHERE F.fabricante IS NOT NULL
    LIMIT 20;
    """
    df9 = pd.read_sql_query(query9, conn)
    
    # 2. Exibição da Tabela de Dados
    st.subheader("Lista de Produtos (Amostra de 20 itens)")
    st.dataframe(df9, width="stretch")
    
    st.divider()
    
    # 3. Resumo Analítico (KPIs e Gráfico)
    st.subheader("Resumo do Status (Ativo no Ano Anterior)")
    
    # Fazendo a contagem dos status usando o Pandas
    df9_status = df9['ativo_ano_anterior'].value_counts().reset_index()
    df9_status.columns = ['Status', 'Quantidade']
    
    # Dividindo a tela em duas colunas para colocar os cartões ao lado do gráfico
    col1, col2 = st.columns([1, 2]) # A coluna 2 será o dobro do tamanho da 1
    
    with col1:
        # Calculando os números para os cartões
        total_produtos = len(df9)
        ativos = df9[df9['ativo_ano_anterior'] == 'Sim'].shape[0]
        inativos = total_produtos - ativos
        
        # st.metric cria os cartões de KPI clássicos de BI
        st.metric(label="Total na Amostra", value=total_produtos)
        st.metric(label="Fabricantes Ativos", value=ativos)
        st.metric(label="Fabricantes Inativos", value=inativos)
        
    with col2:
        # Criando o Gráfico de Rosca (Donut Chart) com o buraco no meio (hole=0.6)
        fig9 = px.pie(
            df9_status,
            names='Status',
            values='Quantidade',
            hole=0.6,
            color='Status',
            color_discrete_map={'Sim': '#2CA02C', 'Não': '#D62728'}, # Força Verde p/ Sim e Vermelho p/ Não
            title="Proporção de Status dos Fabricantes"
        )
        
        # Ajusta para os textos aparecerem dentro das partes da rosca
        fig9.update_traces(textposition='inside', textinfo='percent+label')
        fig9.update_layout(margin=dict(t=40, b=10, l=10, r=10))
        
        # Renderiza o gráfico
        st.plotly_chart(fig9, width="stretch")
# ==========================================
# ABA 10: RECORTES REGIONAIS (MINAS GERAIS)
# ==========================================
with aba10:
    st.header("Consulta 10 — Recorte Regional (Minas Gerais)")
    st.markdown("Mapeamento das compras mais recentes realizadas por instituições mineiras. O gráfico abaixo ilustra as conexões entre o ano, o município sede e a instituição compradora.")
    
    # 1. Query e Leitura dos Dados
    query10 = """
    SELECT C.id_compra, 
           C.ano_compra, 
           I.nome_instituicao, 
           I.municipio_instituicao
    FROM Compra C
    JOIN Instituicao I ON C.cnpj_instituicao = I.cnpj_instituicao
    WHERE I.uf = 'MG'
    ORDER BY C.ano_compra DESC
    LIMIT 20;
    """
    df10 = pd.read_sql_query(query10, conn)
    
    # 2. Exibição da Tabela
    st.subheader("Últimos 20 Registros de Compras (MG)")
    
    # Usamos o st.column_config para forçar o ano a ser tratado como texto,
    # evitando que o Streamlit coloque um ponto de milhar (ex: 2.023)
    st.dataframe(
        df10, 
        width="stretch",
        column_config={
            "ano_compra": st.column_config.TextColumn("Ano da Compra")
        }
    )
    
    st.divider()
    
    # 3. Gráfico Interativo (Categorias Paralelas)
    st.subheader("Mapeamento Multidimensional de Vínculos")
    
    # Criamos uma cópia do dataframe e transformamos o ano em string 
    # para garantir que o Plotly não crie uma escala numérica, e sim faixas isoladas
    df10_grafico = df10.copy()
    df10_grafico['ano_compra'] = df10_grafico['ano_compra'].astype(str)
    
    # px.parallel_categories desenha as faixas conectando os dados da esquerda para a direita
    fig10 = px.parallel_categories(
        df10_grafico, 
        dimensions=['ano_compra', 'municipio_instituicao', 'nome_instituicao'],
        title="Fluxo de Entidades: Ano > Município > Instituição",
        labels={
            'ano_compra': 'Ano de Referência',
            'municipio_instituicao': 'Município Base',
            'nome_instituicao': 'Instituição Compradora'
        }
    )
    
    # Ajustes visuais para melhorar a disposição das faixas
    fig10.update_layout(margin=dict(l=40, r=40, t=50, b=20))
    
    # Renderiza o gráfico
    st.plotly_chart(fig10, width="stretch")
# ==========================================
# ABA 11: MEGACOMPRAS (> R$ 100k)
# ==========================================
with aba11:
    st.header("Consulta 11 — Raio-X das Megacompras")
    st.markdown("Análise das transações de altíssimo valor (superiores a R$ 100.000,00), destacando os fornecedores e o impacto de cada pedido.")
    
    # 1. Query e Leitura dos Dados
    query11 = """
    SELECT IC.id_compra, 
           IC.codigo_br, 
           F.fornecedor, 
           IC.qtd_itens_comprados, 
           IC.preco_total
    FROM Item_Compra IC
    JOIN Fornecedor F ON IC.cnpj_fornecedor = F.cnpj_fornecedor
    WHERE IC.preco_total > 100000.0
    ORDER BY IC.preco_total DESC
    LIMIT 20;
    """
    df11 = pd.read_sql_query(query11, conn)
    
    # 2. Exibição da Tabela
    st.subheader("Tabela de Transações de Alto Valor")
    st.dataframe(
        df11, 
        width="stretch",
        column_config={
            "preco_total": st.column_config.NumberColumn("Preço Total (R$)", format="R$ %.2f"),
            "qtd_itens_comprados": st.column_config.NumberColumn("Quantidade Comprada"),
            "id_compra": st.column_config.TextColumn("ID da Compra") # Evita formatação de milhar no ID
        }
    )
    
    st.divider()
    
    # 3. Gráfico Interativo (Cascata / Waterfall)
    st.subheader("Composição do Volume Financeiro (Cascata)")
    
    # Preparando rótulos curtos para o eixo X não ficar poluído
    # Pegamos os 15 primeiros caracteres do fornecedor + o ID da compra
    rotulos_x = df11['fornecedor'].str[:15] + "... (" + df11['id_compra'].astype(str) + ")"
    
    # O gráfico_objects (go) permite uma construção mais manual e detalhada
    fig11 = go.Figure(go.Waterfall(
        orientation="v",
        measure=["relative"] * len(df11),          # Define que cada barra é um valor relativo que se soma ao anterior
        x=rotulos_x,                               # Eixo X com os nomes curtos
        y=df11['preco_total'],                     # Valores financeiros
        text=df11['preco_total'].apply(lambda x: f"R$ {x/1000:.0f}k"), # Formata o texto flutuante para "R$ Xk"
        textposition="outside",
        increasing={"marker": {"color": "#0083B8"}}, # Cor das barras subindo
        hoverinfo="x+y"
    ))
    
    # Ajustes visuais
    fig11.update_layout(
        title="Acumulação das 20 Maiores Transações",
        waterfallgap=0.3, # Espaço entre as barras
        height=650,
        margin=dict(b=150) # Margem inferior maior para caber os textos inclinados
    )
    
    # Renderiza o gráfico
    st.plotly_chart(fig11, width="stretch")
# ==========================================
# ABA 12: FLUXO DE COMPRAS (2026)
# ==========================================
with aba12:
    st.header("Consulta 12 — Fluxo Financeiro (2026)")
    st.markdown("Mapeamento avançado do fluxo de capital: conectando os Fornecedores aos Produtos adquiridos no ano de 2026.")
    
    # 1. Query e Leitura dos Dados
    query12 = """
    SELECT C.ano_compra,
           C.id_compra,
           P.descricao_catmat,
           F.fornecedor,
           IC.preco_total
    FROM Item_Compra IC
    JOIN Compra C     ON IC.id_compra = C.id_compra
    JOIN Produto P    ON IC.codigo_br = P.codigo_br
    JOIN Fornecedor F ON IC.cnpj_fornecedor = F.cnpj_fornecedor
    WHERE C.ano_compra = 2026
    ORDER BY IC.preco_total DESC
    LIMIT 15;
    """
    df12 = pd.read_sql_query(query12, conn)
    
    # 2. Exibição da Tabela com a nova sintaxe do Streamlit (width='stretch')
    st.subheader("Maiores Transações de 2026")
    st.dataframe(
        df12, 
        width='stretch', 
        column_config={
            "preco_total": st.column_config.NumberColumn("Preço Total (R$)", format="R$ %.2f"),
            "ano_compra": st.column_config.TextColumn("Ano"),
            "id_compra": st.column_config.TextColumn("ID Compra")
        }
    )
    
    st.divider()
    
    # 3. Gráfico Interativo (Sankey Diagram)
    st.subheader("Mapeamento Fornecedor → Produto")
    
    if df12.empty:
        st.warning("⚠️ O banco não retornou dados para este filtro.")
    else:
        # Tratamento rigoroso: remove nulos e força o tipo texto para evitar falhas silenciosas
        df12_clean = df12.dropna(subset=['fornecedor', 'descricao_catmat', 'preco_total']).copy()
        
        fornecedores = df12_clean['fornecedor'].astype(str).str[:30].tolist()
        produtos = df12_clean['descricao_catmat'].astype(str).str[:30].tolist()
        
        labels_unicos = list(dict.fromkeys(fornecedores + produtos))
        
        source_indices = [labels_unicos.index(f) for f in fornecedores]
        target_indices = [labels_unicos.index(p) for p in produtos]
        valores = df12_clean['preco_total'].tolist()
        
        fig12 = go.Figure(data=[go.Sankey(
            node = dict(
                pad = 20,
                thickness = 30,
                line = dict(color = "black", width = 0.5),
                label = labels_unicos,
                color = "#2E86AB"
            ),
            link = dict(
                source = source_indices,
                target = target_indices,
                value = valores,
                color = "rgba(46, 134, 171, 0.4)"
            )
        )])
        
        fig12.update_layout(
            height=600,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        # Renderiza o gráfico sem forçar parâmetros antigos
        st.plotly_chart(fig12)