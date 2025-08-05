import streamlit as st
import pandas as pd
from urllib.parse import quote
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
# Usamos o layout "wide" para aproveitar melhor a tela e um ícone personalizado.
st.set_page_config(
    page_title="Catálogo Atacado",
    layout="wide",
    page_icon="assets/logo.png"  # << SUBSTITUA AQUI pelo nome do seu arquivo de logo
)

# --- 2. CABEÇALHO PERSONALIZADO ---
with st.container():
    col1, col2 = st.columns([1, 8])
    with col1:
        # Verifica se o arquivo de logo existe antes de tentar exibi-lo
        if os.path.exists("assets/logo.png"):  # << SUBSTITUA AQUI pelo nome do seu arquivo de logo
            st.image("assets/logo.png", width=100)
    with col2:
        st.title("Jumbo CDP")  # << SUBSTITUA AQUI pelo nome da sua loja
        st.markdown("##### Catálogo de Atacado | Coleção Atual")

# --- 3. REGRA DE NEGÓCIO E VITRINE ---
st.info("💡 **Regra de Atacado:** Pedido mínimo de 3 peças por modelo.")
st.markdown("---")


# --- 4. CARREGAMENTO DE DADOS E ESTADO DO APP ---
@st.cache_data
def carregar_dados():
    """Carrega os dados dos produtos, garantindo que o valor seja numérico."""
    caminho_csv = 'produtos.csv'
    if os.path.exists(caminho_csv):
        df = pd.read_csv(caminho_csv)
        # Garante que a coluna 'valor' seja tratada como número, mesmo que tenha vírgula na planilha
        if 'valor' in df.columns:
            df['valor'] = pd.to_numeric(df['valor'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        return df
    return pd.DataFrame()


# Carrega os dados na inicialização do app
produtos_df = carregar_dados()

# Inicializa o carrinho na memória da sessão, se ele ainda não existir
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = {}

# --- 5. VITRINE DE PRODUTOS ---
if produtos_df.empty:
    st.warning(
        "Arquivo 'produtos.csv' não encontrado ou está vazio. Verifique se o arquivo está na pasta principal do projeto.")
else:
    colunas_vitrine = st.columns(3)

    for index, produto in produtos_df.iterrows():
        # Distribui os produtos pelas colunas
        coluna_atual = colunas_vitrine[index % 3]
        with coluna_atual:

            # Exibe a imagem do produto
            caminho_imagem = os.path.join('assets', str(produto["nome_arquivo_imagem"]))
            if os.path.exists(caminho_imagem):
                st.image(caminho_imagem, use_container_width=True)  # Correção do aviso de deprecation

            # Exibe informações minimalistas
            st.subheader(produto["nome"])
            st.markdown(f"**R$ {produto['valor']:.2f}**")

            # Detalhes ficam "escondidos" em um expansor
            with st.expander("Mais detalhes"):
                st.write(f"**Referência:** {produto['ref']}")
                st.write(produto["desc"])

            st.write("")  # Adiciona um espaço em branco para "respiro"

            # Campo para o usuário definir a quantidade
            quantidade_atual = st.session_state.carrinho.get(produto['ref'], 0)
            quantidade = st.number_input(
                "Quantidade",
                min_value=0,
                max_value=1000,
                value=quantidade_atual,
                step=1,
                key=f"qtd_{produto['ref']}"
            )

            # Botão para adicionar ao pedido com a lógica de validação de mínimo 3 peças
            if st.button("Adicionar ao Pedido 🛒", key=f"btn_{produto['ref']}", use_container_width=True,
                         type="primary"):
                if quantidade == 0:
                    if produto['ref'] in st.session_state.carrinho:
                        del st.session_state.carrinho[produto['ref']]
                        st.toast(f"Removido.", icon="🗑️")
                        st.rerun()
                elif quantidade < 3:
                    st.warning("O pedido mínimo por item é de 3 peças.")
                else:  # Se a quantidade for 3 ou mais
                    st.session_state.carrinho[produto['ref']] = int(quantidade)
                    st.toast(f"Adicionado!", icon="✅")
                    st.rerun()

# --- 6. BARRA LATERAL (CARRINHO DE PEDIDOS) ---
with st.sidebar:
    st.title("🛒 Meu Pedido")
    st.markdown("---")

    if not st.session_state.carrinho or produtos_df.empty:
        st.info("Seu pedido está vazio. Adicione itens da vitrine ao lado.")
    else:
        texto_pedido = "Olá! Gostaria de orçar o seguinte pedido de atacado:\n\n"
        total_pecas = 0
        valor_total = 0.0

        for ref, quantidade in st.session_state.carrinho.items():
            produto_info = produtos_df[produtos_df['ref'] == ref].iloc[0]
            valor_item = quantidade * produto_info['valor']
            st.text(f"{quantidade}x {produto_info['nome']} (Ref: {ref})")
            texto_pedido += f"- {produto_info['nome']} (Ref: {ref}): {quantidade} peças\n"
            total_pecas += quantidade
            valor_total += valor_item

        st.markdown("---")
        st.subheader(f"Total de Peças: **{total_pecas}**")
        st.subheader(f"Valor Estimado: **R$ {valor_total:.2f}**")
        st.markdown("---")

        texto_pedido_final = texto_pedido + f"\nTotal de Peças: {total_pecas}\nValor Estimado: R$ {valor_total:.2f}"

        # --- BOTÕES DE AÇÃO PARA FINALIZAR O PEDIDO ---
        numero_whatsapp = "5511975042124"  # << SUBSTITUA PELO SEU NÚMERO com código do país e DDD
        email = "victor.ralbuquerque@gmail.com"  # << SUBSTITUA PELO SEU EMAIL

        st.link_button("📲 Enviar via WhatsApp", f"https://wa.me/{numero_whatsapp}?text={quote(texto_pedido_final)}",
                       use_container_width=True)
        st.link_button("✉️ Enviar via E-mail",
                       f"mailto:{email}?subject={quote('Pedido de Atacado')}&body={quote(texto_pedido_final)}",
                       use_container_width=True)

        if st.button("Limpar Pedido", use_container_width=True):
            st.session_state.carrinho = {}
            st.rerun()