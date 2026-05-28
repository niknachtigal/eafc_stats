import streamlit as st
import pandas as pd
import datetime
from supabase import create_client, Client

# Configuração da página
st.set_page_config(page_title="FIFA - Nik vs Digo", page_icon="🎮", layout="wide")

# ==============================================================================
# ESTÉTICA PRETO FOSCO (DARK MODE CUSTOMIZADO)
# ==============================================================================
st.markdown("""
    <style>
        /* Fundo principal e texto */
        .stApp {
            background-color: #121212;
            color: #E0E0E0;
        }
        /* Cor de fundo para os containers e métricas */
        div[data-testid="stMetric"], div[data-testid="stContainer"] {
            background-color: #1E1E1E;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #333333;
        }
        /* Ajuste do topo das abas para ficarem harmoniosas */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #121212;
        }
        .stTabs [data-baseweb="tab"] {
            color: #A0A0A0;
        }
        .stTabs [aria-selected="true"] {
            color: #4DE17C !important;
            border-bottom-color: #4DE17C !important;
        }
        
        /* RESPONSIVIDADE: Oculta a legenda sanfona no PC, mostra apenas no celular */
        @media (min-width: 768px) {
            details.mobile-legend { display: none !important; }
        }
        
        /* RESPONSIVIDADE: Histórico (PC vs Celular) */
        .hist-desktop { display: flex; align-items: center; justify-content: space-between; width: 100%; padding: 5px 0; }
        .hist-mobile { display: none; }
        @media (max-width: 768px) {
            .hist-desktop { display: none !important; }
            .hist-mobile { display: block !important; padding: 5px 0; }
        }
    </style>
""", unsafe_allow_html=True)

# Inicializa o estado de autenticação
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

# ==============================================================================
# CONEXÃO COM SUPABASE
# ==============================================================================
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

def salvar_partida(versao_jogo, data, j_casa, t_casa, g_casa, j_fora, g_fora, t_fora, foi_pen, venc_pen):
    nova_partida = {
        "versao_jogo": versao_jogo,
        "data": data,
        "jogador_casa": j_casa,
        "time_casa": t_casa,
        "gols_casa": g_casa,
        "jogador_fora": j_fora,
        "gols_fora": g_fora,
        "time_fora": t_fora,
        "foi_penaltis": foi_pen,
        "vencedor_penaltis": venc_pen
    }
    supabase.table("partidas").insert(nova_partida).execute()

def excluir_partida(partida_id):
    supabase.table("partidas").delete().eq("id", partida_id).execute()

def ler_partidas():
    response = supabase.table("partidas").select("*").execute()
    if response.data:
        return pd.DataFrame(response.data)
    else:
        return pd.DataFrame(columns=["id", "versao_jogo", "data", "jogador_casa", "time_casa", "gols_casa", "jogador_fora", "gols_fora", "time_fora", "foi_penaltis", "vencedor_penaltis"])

# ==============================================================================
# LÓGICA DE VITÓRIAS E GAMIFICAÇÃO
# ==============================================================================
def obter_vencedor(row):
    if row['gols_casa'] > row['gols_fora']: return row['jogador_casa']
    if row['gols_fora'] > row['gols_casa']: return row['jogador_fora']
    if row['foi_penaltis'] == "Sim": return row['vencedor_penaltis']
    return "Empate"

def calcular_estatisticas(df):
    if df.empty: return None
    
    df['vencedor'] = df.apply(obter_vencedor, axis=1)
    vencedores_lista = df.sort_values('id')['vencedor'].tolist()
    
    ultima = vencedores_lista[-1]
    seq_at_p, seq_at_q = (ultima, 0)
    if ultima != "Empate":
        for v in reversed(vencedores_lista):
            if v == ultima: seq_at_q += 1
            else: break
            
    max_n, max_r, cur_n, cur_r = 0, 0, 0, 0
    for v in vencedores_lista:
        if v == "Nikolas": 
            cur_n += 1; cur_r = 0
            if cur_n > max_n: max_n = cur_n
        elif v == "Rodrigo":
            cur_r += 1; cur_n = 0
            if cur_r > max_r: max_r = cur_r
        else: cur_n, cur_r = 0, 0
            
    df['dif'] = (df['gols_casa'] - df['gols_fora']).abs()
    df['soma'] = df['gols_casa'] + df['gols_fora']
    top_5 = df.sort_values(by=['dif', 'soma'], ascending=[False, False]).head(5)
    
    nik_times = pd.concat([df[df['jogador_casa']=='Nikolas']['time_casa'], df[df['jogador_fora']=='Nikolas']['time_fora']])
    rod_times = pd.concat([df[df['jogador_casa']=='Rodrigo']['time_casa'], df[df['jogador_fora']=='Rodrigo']['time_fora']])
    
    total_jogos = len(df)
    v_nik = len(df[df['vencedor'] == 'Nikolas'])
    v_rod = len(df[df['vencedor'] == 'Rodrigo'])
    emp = len(df[df['vencedor'] == 'Empate'])
    
    g_nik = df[df['jogador_casa']=='Nikolas']['gols_casa'].sum() + df[df['jogador_fora']=='Nikolas']['gols_fora'].sum()
    g_rod = df[df['jogador_casa']=='Rodrigo']['gols_casa'].sum() + df[df['jogador_fora']=='Rodrigo']['gols_fora'].sum()
    pen_nik = len(df[(df['foi_penaltis'] == 'Sim') & (df['vencedor_penaltis'] == 'Nikolas')])
    pen_rod = len(df[(df['foi_penaltis'] == 'Sim') & (df['vencedor_penaltis'] == 'Rodrigo')])
    pen_disputados = len(df[df['foi_penaltis'] == 'Sim'])

    # Cálculo Saldo de Gols nas Vitórias (Amasso)
    df_v_nik = df[df['vencedor'] == 'Nikolas']
    media_saldo_nik = df_v_nik['dif'].mean() if not df_v_nik.empty else 0.0
    
    df_v_rod = df[df['vencedor'] == 'Rodrigo']
    media_saldo_rod = df_v_rod['dif'].mean() if not df_v_rod.empty else 0.0

    avg_nik = g_nik / total_jogos if total_jogos > 0 else 0
    avg_rod = g_rod / total_jogos if total_jogos > 0 else 0

    # -- Lógica dos Badges (Medalhas) --
    cs_nik = len(df[((df['jogador_casa']=='Nikolas') & (df['gols_fora']==0)) | ((df['jogador_fora']=='Nikolas') & (df['gols_casa']==0))])
    cs_rod = len(df[((df['jogador_casa']=='Rodrigo') & (df['gols_fora']==0)) | ((df['jogador_fora']=='Rodrigo') & (df['gols_casa']==0))])
    
    badges_nik, badges_rod = [], []
    
    # Rei do FIFA
    is_nik_rei = (v_nik > v_rod) and (avg_nik > avg_rod) and (max_n > max_r) and (media_saldo_nik > media_saldo_rod)
    is_rod_rei = (v_rod > v_nik) and (avg_rod > avg_nik) and (max_r > max_n) and (media_saldo_rod > media_saldo_nik)

    if is_nik_rei: badges_nik.append("👑")
    elif is_rod_rei: badges_rod.append("👑")

    # Muralha
    if cs_nik > cs_rod and cs_nik > 0: badges_nik.append("🛡️")
    elif cs_rod > cs_nik and cs_rod > 0: badges_rod.append("🛡️")
    # Pênaltis
    if pen_disputados > 0:
        tx_nik = pen_nik / pen_disputados
        tx_rod = pen_rod / pen_disputados
        if tx_nik > tx_rod and tx_nik > 0: badges_nik.append("🎯")
        elif tx_rod > tx_nik and tx_rod > 0: badges_rod.append("🎯")
    # Máquina de Gols
    if avg_nik > avg_rod and avg_nik > 0: badges_nik.append("⚽")
    elif avg_rod > avg_nik and avg_rod > 0: badges_rod.append("⚽")
        
    # Pato
    if seq_at_p == 'Rodrigo' and seq_at_q >= 10: badges_nik.append("🦆")
    elif seq_at_p == 'Nikolas' and seq_at_q >= 10: badges_rod.append("🦆")

    # Sequência Atual Sem Tomar Gol
    cur_cs_nik, cur_cs_rod = 0, 0
    for _, row in df.sort_values('id', ascending=False).iterrows():
        if (row['jogador_casa'] == 'Nikolas' and row['gols_fora'] == 0) or (row['jogador_fora'] == 'Nikolas' and row['gols_casa'] == 0): cur_cs_nik += 1
        else: break
    for _, row in df.sort_values('id', ascending=False).iterrows():
        if (row['jogador_casa'] == 'Rodrigo' and row['gols_fora'] == 0) or (row['jogador_fora'] == 'Rodrigo' and row['gols_casa'] == 0): cur_cs_rod += 1
        else: break

    return {
        "total_jogos": total_jogos,
        "v_nik": v_nik,
        "v_rod": v_rod,
        "emp": emp,
        "g_nik": g_nik, "g_rod": g_rod,
        "pen_nik": pen_nik, "pen_rod": pen_rod,
        "seq_at_p": seq_at_p, "seq_at_q": seq_at_q,
        "max_nik": max_n, "max_rod": max_r,
        "media_saldo_nik": media_saldo_nik,
        "media_saldo_rod": media_saldo_rod,
        "top_5": top_5,
        "nik_top_teams": nik_times.value_counts().head(3).to_dict() if not nik_times.empty else {},
        "rod_top_teams": rod_times.value_counts().head(3).to_dict() if not rod_times.empty else {},
        "badges_nik": badges_nik, "badges_rod": badges_rod,
        "cur_cs_nik": cur_cs_nik, "cur_cs_rod": cur_cs_rod,
        "df_completo": df
    }

# Lemos os dados para poder usar as informações no título
df_partidas = ler_partidas()
stats_globais = calcular_estatisticas(df_partidas)

# ==============================================================================
# CABEÇALHO E LOGIN (Canto Superior Direito)
# ==============================================================================
col_title, col_login = st.columns([5, 1])

with col_title:
    if stats_globais:
        seq_perdedor = stats_globais['seq_at_q']
        
        badges_desc = {
            "👑": "Rei do Fifa: Maior número de vitórias, média de gols, sequência histórica de vitórias, saldo de gols nas vitórias",        
            "🛡️": "Muralha: Maior número de jogos sem sofrer gols",
            "🎯": "Frio e Calculista: Maior taxa de vitória nos pênaltis",
            "⚽": "Máquina de Gols: Maior média de gols marcados",
            "🦆": f"Pato: Perdeu os últimos {seq_perdedor} jogos."
        }
        nik_badges_html = "".join([f"<span title='{badges_desc.get(b, b)}' style='cursor:help; margin: 0 2px;'>{b}</span>" for b in stats_globais['badges_nik']]) if stats_globais['badges_nik'] else ""
        rod_badges_html = "".join([f"<span title='{badges_desc.get(b, b)}' style='cursor:help; margin: 0 2px;'>{b}</span>" for b in stats_globais['badges_rod']]) if stats_globais['badges_rod'] else ""

        # HTML COLADO NA MARGEM PARA EVITAR BUG DO MARKDOWN
        title_html = f"""
<div style='display: flex; align-items: flex-start; justify-content: flex-start; gap: 15px; font-size: 2.2rem; font-weight: bold; margin-bottom: 10px;'>
    <span style='line-height: 1.2;'>🎮 FIFA EA FC -</span>
    <div style='text-align: center; display: inline-flex; flex-direction: column; align-items: center;'>
        <span style='line-height: 1.2;'>Nikolas</span>
        <span style='font-size: 1.3rem; margin-top: 2px;'>{nik_badges_html}</span>
    </div>
    <span style='line-height: 1.2; margin: 0 5px;'>vs</span>
    <div style='text-align: center; display: inline-flex; flex-direction: column; align-items: center;'>
        <span style='line-height: 1.2;'>Rodrigo</span>
        <span style='font-size: 1.3rem; margin-top: 2px;'>{rod_badges_html}</span>
    </div>
</div>
"""
        st.markdown(title_html, unsafe_allow_html=True)

        active_badges = set(stats_globais['badges_nik'] + stats_globais['badges_rod'])
        if active_badges:
            legend_items = ""
            for b, desc in badges_desc.items():
                if b in active_badges:
                    if ":" in desc:
                        nome, texto = desc.split(":", 1)
                        legend_items += f"<p style='margin: 0 0 8px 0;'>{b} <b style='color:#E0E0E0;'>{nome}</b>:{texto}</p>"
                    else:
                        legend_items += f"<p style='margin: 0 0 8px 0;'>{b} {desc}</p>"
                        
            # HTML COLADO NA MARGEM
            legend_html = f"""
<details class="mobile-legend" style="background-color: #1E1E1E; padding: 10px 15px; border-radius: 8px; border: 1px solid #333333; margin-bottom: 15px;">
    <summary style="cursor: pointer; font-weight: bold; color: #E0E0E0; font-size: 14px; outline: none;">ℹ️ Significado das Medalhas</summary>
    <div style="margin-top: 12px; font-size: 13px; color: #A0A0A0; line-height: 1.4;">
        {legend_items}
    </div>
</details>
"""
            st.markdown(legend_html, unsafe_allow_html=True)
            
    else:
        st.title("🎮 FIFA EA FC - Nikolas vs Rodrigo")

with col_login:
    # Espaçamento para alinhar o botão de login com o título
    st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
    
    if not st.session_state["autenticado"]:
        with st.popover("🔐 Acesso Restrito", use_container_width=True):
            senha_digitada = st.text_input("Senha", type="password", placeholder="Digite a senha...", label_visibility="collapsed")
            if st.button("Entrar", use_container_width=True):
                if senha_digitada == st.secrets["APP_PASSWORD"]:
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("Incorreta!")
    else:
        if st.button("🔓 Sair do Painel", use_container_width=True):
            st.session_state["autenticado"] = False
            st.rerun()

st.markdown("---")

# ==============================================================================
# DICIONÁRIO DE TIMES E LOGOS
# ==============================================================================
TEAMS = {
    # Premier League
    "Arsenal": "https://crests.football-data.org/57.png",
    "Aston Villa": "https://crests.football-data.org/58.png",
    "Bournemouth": "https://crests.football-data.org/1044.png",
    "Brentford": "https://crests.football-data.org/402.png",
    "Brighton": "https://crests.football-data.org/397.png",
    "Chelsea": "https://crests.football-data.org/61.png",
    "Crystal Palace": "https://crests.football-data.org/354.png",
    "Everton": "https://crests.football-data.org/62.png",
    "Fulham": "https://crests.football-data.org/63.png",
    "Ipswich Town": "https://crests.football-data.org/349.png",
    "Leicester City": "https://crests.football-data.org/338.png",
    "Liverpool": "https://crests.football-data.org/64.png",
    "Manchester City": "https://crests.football-data.org/65.png",
    "Manchester United": "https://crests.football-data.org/66.png",
    "Newcastle United": "https://crests.football-data.org/67.png",
    "Nottingham Forest": "https://crests.football-data.org/68.png",
    "Southampton": "https://crests.football-data.org/340.png",
    "Tottenham Hotspur": "https://crests.football-data.org/73.png",
    "West Ham United": "https://crests.football-data.org/563.png",
    "Wolverhampton": "https://crests.football-data.org/76.png",

    # La Liga
    "Alavés": "https://crests.football-data.org/263.png",
    "Athletic Club": "https://crests.football-data.org/77.png",
    "Atlético Madrid": "https://crests.football-data.org/78.png",
    "Celta de Vigo": "https://crests.football-data.org/558.png",
    "Espanyol": "https://crests.football-data.org/80.png",
    "FC Barcelona": "https://crests.football-data.org/81.png",
    "Getafe": "https://crests.football-data.org/82.png",
    "Girona": "https://crests.football-data.org/298.png",
    "Las Palmas": "https://crests.football-data.org/275.png",
    "Leganés": "https://crests.football-data.org/745.png",
    "Mallorca": "https://crests.football-data.org/89.png",
    "Osasuna": "https://crests.football-data.org/79.png",
    "Rayo Vallecano": "https://crests.football-data.org/87.png",
    "Real Betis": "https://crests.football-data.org/90.png",
    "Real Madrid": "https://crests.football-data.org/86.png",
    "Real Sociedad": "https://crests.football-data.org/92.png",
    "Real Valladolid": "https://crests.football-data.org/250.png",
    "Sevilla FC": "https://crests.football-data.org/559.png",
    "Valencia CF": "https://crests.football-data.org/95.png",
    "Villarreal CF": "https://crests.football-data.org/94.png",

    # Serie A
    "Atalanta": "https://crests.football-data.org/102.png",
    "Bologna": "https://crests.football-data.org/103.png",
    "Cagliari": "https://crests.football-data.org/104.png",
    "Como": "https://crests.football-data.org/105.png",
    "Empoli": "https://crests.football-data.org/107.png",
    "Fiorentina": "https://crests.football-data.org/99.png",
    "Genoa": "https://crests.football-data.org/106.png",
    "Inter de Milão": "https://crests.football-data.org/108.png",
    "Juventus": "https://crests.football-data.org/109.png",
    "Lazio": "https://crests.football-data.org/110.png",
    "Lecce": "https://crests.football-data.org/112.png",
    "Milan": "https://crests.football-data.org/98.png",
    "Monza": "https://crests.football-data.org/5911.png",
    "Napoli": "https://crests.football-data.org/113.png",
    "Parma": "https://crests.football-data.org/115.png",
    "Roma": "https://crests.football-data.org/100.png",
    "Torino": "https://crests.football-data.org/586.png",
    "Udinese": "https://crests.football-data.org/115.png",
    "Venezia": "https://crests.football-data.org/117.png",
    "Verona": "https://crests.football-data.org/450.png",

    # Bundesliga
    "Bayer Leverkusen": "https://crests.football-data.org/3.png",
    "Bayern de Munique": "https://crests.football-data.org/5.png",
    "Borussia Dortmund": "https://crests.football-data.org/4.png",
    "Borussia M'gladbach": "https://crests.football-data.org/18.png",
    "Eintracht Frankfurt": "https://crests.football-data.org/19.png",
    "Freiburg": "https://crests.football-data.org/17.png",
    "Heidenheim": "https://crests.football-data.org/44.png",
    "Hoffenheim": "https://crests.football-data.org/2.png",
    "Holstein Kiel": "https://crests.football-data.org/32.png",
    "Mainz 05": "https://crests.football-data.org/15.png",
    "RB Leipzig": "https://crests.football-data.org/721.png",
    "St. Pauli": "https://crests.football-data.org/35.png",
    "Stuttgart": "https://crests.football-data.org/10.png",
    "Werder Bremen": "https://crests.football-data.org/12.png",
    "Wolfsburg": "https://crests.football-data.org/11.png",

    # Ligue 1
    "Auxerre": "https://crests.football-data.org/510.png",
    "Angers": "https://crests.football-data.org/532.png",
    "AS Monaco": "https://crests.football-data.org/548.png",
    "Brest": "https://crests.football-data.org/512.png",
    "Le Havre": "https://crests.football-data.org/533.png",
    "Lens": "https://crests.football-data.org/546.png",
    "Lille": "https://crests.football-data.org/521.png",
    "Lyon": "https://crests.football-data.org/523.png",
    "Marseille": "https://crests.football-data.org/516.png",
    "Montpellier": "https://crests.football-data.org/518.png",
    "Nantes": "https://crests.football-data.org/543.png",
    "Nice": "https://crests.football-data.org/522.png",
    "Paris SG": "https://crests.football-data.org/524.png",
    "Reims": "https://crests.football-data.org/547.png",
    "Rennes": "https://crests.football-data.org/529.png",
    "Saint-Étienne": "https://crests.football-data.org/527.png",
    "Strasbourg": "https://crests.football-data.org/576.png",
    "Toulouse": "https://crests.football-data.org/511.png",

    # Liga Portugal
    "Braga": "https://crests.football-data.org/560.png",
    "FC Porto": "https://crests.football-data.org/503.png",
    "Gil Vicente": "https://crests.football-data.org/5568.png",
    "Guimarães": "https://crests.football-data.org/5543.png",
    "SL Benfica": "https://crests.football-data.org/1903.png",
    "Sporting CP": "https://upload.wikimedia.org/wikipedia/pt/thumb/3/3e/Sporting_Clube_de_Portugal.png/120px-Sporting_Clube_de_Portugal.png",

    # Eredivisie
    "Ajax": "https://crests.football-data.org/678.png",
    "AZ Alkmaar": "https://upload.wikimedia.org/wikipedia/pt/thumb/e/e0/AZ_Alkmaar.svg/250px-AZ_Alkmaar.svg.png",
    "Feyenoord": "https://crests.football-data.org/675.png",
    "PSV Eindhoven": "https://crests.football-data.org/682.png",
    "Twente": "https://crests.football-data.org/666.png",

    # Outros
    "Al Ahli": "https://upload.wikimedia.org/wikipedia/en/thumb/b/b5/Al-Ahli_Saudi_FC_logo.svg/200px-Al-Ahli_Saudi_FC_logo.svg.png",
    "Al Hilal": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Al_Hilal_SFC_Logo.svg/120px-Al_Hilal_SFC_Logo.svg.png",
    "Al Ittihad": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a3/Al-Ittihad_Club_%2Saudi_Arabia%29_logo.svg/200px-Al-Ittihad_Club_%2Saudi_Arabia%29_logo.svg.png",
    "Al Nassr": "https://upload.wikimedia.org/wikipedia/en/3/3f/Nassr_FC_Logo.svg",
    "Boca Juniors": "https://crests.football-data.org/1127.png",
    "River Plate": "https://crests.football-data.org/1128.png",
    "Inter Miami CF": "https://upload.wikimedia.org/wikipedia/pt/thumb/c/c1/Inter_Miami_CF.png/250px-Inter_Miami_CF.png",
    "LA Galaxy": "https://upload.wikimedia.org/wikipedia/en/thumb/1/1a/LA_Galaxy_logo.svg/200px-LA_Galaxy_logo.svg.png",
    "Los Angeles FC": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f5/Los_Angeles_FC_logo.svg/200px-Los_Angeles_FC_logo.svg.png",
    "Galatasaray": "https://crests.football-data.org/611.png",
    "Fenerbahçe": "https://crests.football-data.org/610.png",
    
    # Brasileiro
    "Internacional":"https://logodetimes.com/times/internacional/logo-internacional-4096.png",
    "Grêmio":"https://logodetimes.com/times/gremio/logo-gremio-4096.png",
    
    # Seleções
    "Itália": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Logo_Italy_National_Football_Team_-_2023.svg/120px-Logo_Italy_National_Football_Team_-_2023.svg.png",
    "Brasil": "https://logodetimes.com/times/selecao-brasileira-brasil-novo-logo-2019-com-estrelas-e-nome/logo-selecao-brasileira-brasil-novo-logo-2019-com-estrelas-e-nome-4096.png",
    "Portugal": "https://upload.wikimedia.org/wikipedia/pt/7/75/Portugal_FPF.png",
    "Argentina": "https://logodetimes.com/times/argentina/selecao-argentina-de-futebol-256.png",
    "Alemanha": "https://logodetimes.com/times/alemanha/selecao-alema-de-futebol-256.png",
    "Espanha": "https://logodownload.org/wp-content/uploads/2022/08/spain-national-football-team-logo-0.png",
    "França": "https://logodownload.org/wp-content/uploads/2022/07/france-national-football-team-logo.png",    
}
TEAMS = dict(sorted(TEAMS.items()))

VERSOES = ["EA FC 27", "EA FC 28", "EA FC 29", "EA FC 30"]

# ==============================================================================
# ABAS DINÂMICAS BASEADAS NA AUTENTICAÇÃO
# ==============================================================================
if st.session_state["autenticado"]:
    tabs = st.tabs(["📊 Dashboard Geral", "📝 Registrar Partida", "📜 Histórico de Jogos"])
    tab1, tab2, tab3 = tabs[0], tabs[1], tabs[2]
else:
    tabs = st.tabs(["📊 Dashboard Geral", "📜 Histórico de Jogos"])
    tab1, tab3 = tabs[0], tabs[1]
    tab2 = None

# ----------------- TAB 1: DASHBOARD (Público) -----------------
with tab1:
    if not df_partidas.empty:
        versoes_cadastradas = sorted(df_partidas['versao_jogo'].unique().tolist())
        opcoes_filtro = ["Geral"] + versoes_cadastradas
        
        col_filtro, _ = st.columns([1, 4])
        with col_filtro:
            filtro_selecionado = st.selectbox("Edição:", opcoes_filtro, label_visibility="collapsed")
            
        st.markdown("<br>", unsafe_allow_html=True)
            
        if filtro_selecionado != "Geral":
            df_filtrado = df_partidas[df_partidas['versao_jogo'] == filtro_selecionado].copy()
        else:
            df_filtrado = df_partidas.copy()

        stats = calcular_estatisticas(df_filtrado)
        
        if stats:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total de Jogos", stats['total_jogos'])
            m2.metric("Vitórias Nikolas", stats['v_nik'], f"{stats['g_nik']} Gols")
            m3.metric("Vitórias Rodrigo", stats['v_rod'], f"{stats['g_rod']} Gols")
            m4.metric("Empates", stats['emp'])
            
            c_s1, c_s2 = st.columns(2)
            with c_s1:
                st.subheader("➡️ Sequência Atual")
                if stats['seq_at_q'] >= 10:
                    perdedor = "Rodrigo" if stats['seq_at_p'] == "Nikolas" else "Nikolas"
                    st.warning(f"🦆 **Humilhação:** {stats['seq_at_p']} venceu a(s) última(s) **{stats['seq_at_q']}** partida(s) do seu filho {perdedor}!")
                elif stats['seq_at_q'] > 0:
                    st.info(f"🔵 **{stats['seq_at_p']}** venceu a(s) última(s) **{stats['seq_at_q']}** partida(s)!")
                else:
                    st.info(f"🔘 Última partida foi {stats['seq_at_p']}")

                # Easter Egg Muralha
                if stats['cur_cs_nik'] > 0:
                    st.info(f"🛡️ Nikolas está há **{stats['cur_cs_nik']}** partida(s) sem tomar gol.")
                if stats['cur_cs_rod'] > 0:
                    st.info(f"🛡️ Rodrigo está há **{stats['cur_cs_rod']}** partida(s) sem tomar gol.")
            
            with c_s2:
                st.subheader("🏆 Recordes de Sequência")
                if stats['max_nik'] >= stats['max_rod']:
                    st.success(f"👑 A maior sequência histórica é de **Nikolas** com **{stats['max_nik']}** vitórias seguidas.")
                    st.info(f"A maior sequência histórica de **Rodrigo** é de **{stats['max_rod']}** vitórias seguidas.")
                else:
                    st.success(f"👑 A maior sequência histórica é de **Rodrigo** com **{stats['max_rod']}** vitórias seguidas.")
                    st.info(f"A maior sequência histórica de **Nikolas** é de **{stats['max_nik']}** vitórias seguidas.")

            # GRÁFICO DE CORRIDA DOS CAMPEÕES
            st.markdown("### 📈 Evolução de Vitórias")
            df_chart = stats['df_completo'].copy().sort_values('id')
            df_chart['Vitórias Nikolas'] = (df_chart['vencedor'] == 'Nikolas').cumsum()
            df_chart['Vitórias Rodrigo'] = (df_chart['vencedor'] == 'Rodrigo').cumsum()
            df_chart['Partida'] = range(1, len(df_chart) + 1)
            st.line_chart(df_chart.set_index('Partida')[['Vitórias Nikolas', 'Vitórias Rodrigo']], color=["#4DE17C", "#FF4B4B"])

            st.markdown("### 📊 Estatísticas Detalhadas")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Média de Gols/Jogo:**")
                st.write(f"⚽ Nikolas: {stats['g_nik']/stats['total_jogos']:.2f} por jogo")
                st.write(f"⚽ Rodrigo: {stats['g_rod']/stats['total_jogos']:.2f} por jogo")
            with c2:
                st.markdown("**Decisões por Pênaltis vencidas:**")
                st.write(f"🎯 Nikolas ganhou {stats['pen_nik']} nos pênaltis")
                st.write(f"🎯 Rodrigo ganhou {stats['pen_rod']} nos pênaltis")
            with c3:
                st.markdown("**Aproveitamento Geral:**")
                st.write(f"📈 Nikolas: {(stats['v_nik']/stats['total_jogos'])*100:.1f}%")
                st.write(f"📈 Rodrigo: {(stats['v_rod']/stats['total_jogos'])*100:.1f}%")

            # --- RANKING DE AMASSO (SALDO DE GOLS) ---
            st.markdown("---")
            st.markdown("### ⚽ Saldo de Gols nas Vitórias")
            
            media_saldo_nik = stats['media_saldo_nik']
            media_saldo_rod = stats['media_saldo_rod']
            
            c_gol1, c_gol2 = st.columns(2)
            with c_gol1:
                st.metric("Média de Saldo nas Vitórias (Nikolas)", f"+{media_saldo_nik:.1f} gols")
                if media_saldo_nik > media_saldo_rod and media_saldo_nik > 0:
                    st.caption("💪 Costuma amassar mais nas vitórias!")
            with c_gol2:
                st.metric("Média de Saldo nas Vitórias (Rodrigo)", f"+{media_saldo_rod:.1f} gols")
                if media_saldo_rod > media_saldo_nik and media_saldo_rod > 0:
                    st.caption("💪 Costuma amassar mais nas vitórias!")

            # --- RAIO-X DE CLÁSSICOS & KRYPTONITA ---
            st.markdown("---")
            st.markdown("### 🆚 Raio-X de Clássicos")
            
            df_v_rod_k = df_filtrado[df_filtrado['vencedor'] == 'Rodrigo']
            times_rod_venceu = pd.concat([
                df_v_rod_k[df_v_rod_k['jogador_casa'] == 'Rodrigo']['time_casa'],
                df_v_rod_k[df_v_rod_k['jogador_fora'] == 'Rodrigo']['time_fora']
            ])
            krypto_nik = times_rod_venceu.value_counts().idxmax() if not times_rod_venceu.empty else "Nenhum"
            
            df_v_nik_k = df_filtrado[df_filtrado['vencedor'] == 'Nikolas']
            times_nik_venceu = pd.concat([
                df_v_nik_k[df_v_nik_k['jogador_casa'] == 'Nikolas']['time_casa'],
                df_v_nik_k[df_v_nik_k['jogador_fora'] == 'Nikolas']['time_fora']
            ])
            krypto_rod = times_nik_venceu.value_counts().idxmax() if not times_nik_venceu.empty else "Nenhum"
            
            st.warning(f"☢️ **Kryptonita do Nikolas:** Sempre que o Rodrigo joga de **{krypto_nik}**, a vida do Nikolas fica difícil.")
            st.warning(f"☢️ **Kryptonita do Rodrigo:** Sempre que o Nikolas escolhe o **{krypto_rod}**, o Rodrigo passa mal.")

            st.markdown("<br><b>Filtrar um Clássico Específico:</b>", unsafe_allow_html=True)
            c_rx1, c_rx2 = st.columns(2)
            lista_de_times = list(TEAMS.keys())
            idx_rm = lista_de_times.index("Real Madrid") if "Real Madrid" in lista_de_times else 0
            idx_fcb = lista_de_times.index("FC Barcelona") if "FC Barcelona" in lista_de_times else 0
            
            with c_rx1: rx_time_nik = st.selectbox("Time do Nikolas:", lista_de_times, index=idx_rm, key="rx_n")
            with c_rx2: rx_time_rod = st.selectbox("Time do Rodrigo:", lista_de_times, index=idx_fcb, key="rx_r")
            
            df_rx = df_filtrado[
                ((df_filtrado['jogador_casa'] == 'Nikolas') & (df_filtrado['time_casa'] == rx_time_nik) & 
                 (df_filtrado['jogador_fora'] == 'Rodrigo') & (df_filtrado['time_fora'] == rx_time_rod)) |
                ((df_filtrado['jogador_fora'] == 'Nikolas') & (df_filtrado['time_fora'] == rx_time_nik) & 
                 (df_filtrado['jogador_casa'] == 'Rodrigo') & (df_filtrado['time_casa'] == rx_time_rod))
            ]
            
            if not df_rx.empty:
                rx_v_nik = len(df_rx[df_rx['vencedor'] == 'Nikolas'])
                rx_v_rod = len(df_rx[df_rx['vencedor'] == 'Rodrigo'])
                rx_emp = len(df_rx[df_rx['vencedor'] == 'Empate'])
                
                m_rx1, m_rx2, m_rx3, m_rx4 = st.columns(4)
                m_rx1.metric("Jogos no Clássico", len(df_rx))
                m_rx2.metric("Vitórias Nikolas", rx_v_nik)
                m_rx3.metric("Vitórias Rodrigo", rx_v_rod)
                m_rx4.metric("Empates", rx_emp)
            else:
                st.info("Vocês ainda não jogaram este clássico nesta edição!")

            st.markdown("---")
            
            st.markdown("### 👕 Times mais utilizados")
            c_t1, c_t2 = st.columns(2)
            
            with c_t1:
                st.markdown("**Top 3 - Nikolas**")
                for time, count in stats['nik_top_teams'].items():
                    st.markdown(
                        f"<div style='display: flex; align-items: center; gap: 10px; margin-bottom: 5px;'>"
                        f"<img src='{TEAMS.get(time)}' style='width: 25px; height: 25px; object-fit: contain;'>"
                        f"<span><b>{time}</b> ({count} jogos)</span>"
                        f"</div>", 
                        unsafe_allow_html=True
                    )
                    
            with c_t2:
                st.markdown("**Top 3 - Rodrigo**")
                for time, count in stats['rod_top_teams'].items():
                    st.markdown(
                        f"<div style='display: flex; align-items: center; gap: 10px; margin-bottom: 5px;'>"
                        f"<img src='{TEAMS.get(time)}' style='width: 25px; height: 25px; object-fit: contain;'>"
                        f"<span><b>{time}</b> ({count} jogos)</span>"
                        f"</div>", 
                        unsafe_allow_html=True
                    )

            st.markdown("---")
            st.markdown("### 🔝 Top 5 Maiores Placares")
            for i, row in stats['top_5'].iterrows():
                vencedor = obter_vencedor(row)
                cor_vencedor = "#4de17c"
                
                txt_casa = f"<i>({row['jogador_casa']})</i> {row['time_casa']} {row['gols_casa']}"
                txt_fora = f"{row['gols_fora']} {row['time_fora']} <i>({row['jogador_fora']})</i>"
                
                if vencedor == row['jogador_casa']:
                    txt_casa = f"<span style='color: {cor_vencedor}; font-weight: bold;'>{txt_casa}</span>"
                elif vencedor == row['jogador_fora']:
                    txt_fora = f"<span style='color: {cor_vencedor}; font-weight: bold;'>{txt_fora}</span>"
                    
                st.markdown(f"<h3 style='margin: 5px 0;'>{txt_casa} <span style='color: inherit;'>x</span> {txt_fora}</h3>", unsafe_allow_html=True)
        else:
            st.info(f"Nenhuma partida registrada para {filtro_selecionado}.")
    else:
        st.info("Aguardando o primeiro jogo para gerar estatísticas.")

# ----------------- TAB 2: REGISTRAR (Restrito) -----------------
if tab2:
    with tab2:
                
        mando = st.radio("Mando de Campo:", ["Nikolas em Casa", "Rodrigo em Casa"], horizontal=True)
        jogador_casa = "Nikolas" if mando == "Nikolas em Casa" else "Rodrigo"
        jogador_fora = "Rodrigo" if mando == "Nikolas em Casa" else "Nikolas"
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        lista_de_times = list(TEAMS.keys())
        
        try: idx_real_madrid = lista_de_times.index("Real Madrid")
        except ValueError: idx_real_madrid = 0
            
        try: idx_barcelona = lista_de_times.index("FC Barcelona")
        except ValueError: idx_barcelona = 0

        idx_padrao_casa = idx_real_madrid if jogador_casa == "Nikolas" else idx_barcelona
        idx_padrao_fora = idx_real_madrid if jogador_fora == "Nikolas" else idx_barcelona
        
        col_c, col_d, col_f = st.columns([2, 1, 2])
        
        with col_c:
            st.markdown(f"### 🏠 Casa ({jogador_casa})")
            t_c = st.selectbox("Time", lista_de_times, index=idx_padrao_casa, key="tc")
            st.markdown(f'''
                <div style="height: 100px; display: flex; align-items: center; justify-content: flex-start; margin-bottom: 10px;">
                    <img src="{TEAMS[t_c]}" style="width: 80px; height: 80px; object-fit: contain;">
                </div>
            ''', unsafe_allow_html=True)
            g_c = st.number_input("Gols do Casa", min_value=0, value=0, key="gc")

        with col_d:
            st.markdown("<div style='text-align: center; font-size: 14px; margin-bottom: 5px;'>Data do Jogo</div>", unsafe_allow_html=True)
            d_j = st.date_input("Data", datetime.date.today(), format="DD/MM/YYYY", label_visibility="collapsed")
            
            st.markdown("<div style='text-align: center; font-size: 14px; margin-top: 15px; margin-bottom: 5px;'>Edição</div>", unsafe_allow_html=True)
            v_jogo = st.selectbox("Versão", VERSOES, label_visibility="collapsed")
            
        with col_f:
            st.markdown(f"### ✈️ Fora ({jogador_fora})")
            t_f = st.selectbox("Time ", lista_de_times, index=idx_padrao_fora, key="tf")
            st.markdown(f'''
                <div style="height: 100px; display: flex; align-items: center; justify-content: flex-start; margin-bottom: 10px;">
                    <img src="{TEAMS[t_f]}" style="width: 80px; height: 80px; object-fit: contain;">
                </div>
            ''', unsafe_allow_html=True)
            g_f = st.number_input("Gols do Fora", min_value=0, value=0, key="gf")

        foi_p, venc_p = "Não", ""
        if g_c == g_f:
            st.info("Houve disputa de pênaltis?")
            teve_p = st.checkbox("Sim")
            if teve_p:
                foi_p = "Sim"
                venc_p = st.radio("Quem levou nos pênaltis?", [jogador_casa, jogador_fora])

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Salvar partida 💾", use_container_width=True):
            salvar_partida(v_jogo, str(d_j), jogador_casa, t_c, int(g_c), jogador_fora, int(g_f), t_f, foi_p, venc_p)
            st.success("Gravado!")
            st.rerun()

# ----------------- TAB 3: HISTÓRICO (Híbrido) -----------------
with tab3:
    st.subheader("📜 Histórico de Jogos")
    
    if not df_partidas.empty:
        df_partidas['data_dt'] = pd.to_datetime(df_partidas['data'])
        
        c_tog, c_dat, _ = st.columns([1.5, 3, 3])
        with c_tog:
            st.markdown("<br>", unsafe_allow_html=True)
            ativar_filtro = st.toggle("Filtrar por Período", key="toggle_filtro")
            
        df_historico = df_partidas.copy()
        
        if ativar_filtro:
            with c_dat:
                min_date = df_partidas['data_dt'].min().date()
                max_date = df_partidas['data_dt'].max().date()
                datas = st.date_input("Selecione o intervalo", value=(min_date, max_date), min_value=min_date, max_value=max_date, format="DD/MM/YYYY")
            
            if isinstance(datas, tuple) and len(datas) == 2:
                start_d, end_d = datas
                df_historico = df_partidas[(df_partidas['data_dt'].dt.date >= start_d) & (df_partidas['data_dt'].dt.date <= end_d)].copy()
                
                stats_hist = calcular_estatisticas(df_historico)
                if stats_hist:
                    st.markdown("#### 📊 Resumo do Período Filtrado")
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Jogos no Período", stats_hist['total_jogos'])
                    m2.metric("Vitórias Nikolas", stats_hist['v_nik'], f"{stats_hist['g_nik']} Gols")
                    m3.metric("Vitórias Rodrigo", stats_hist['v_rod'], f"{stats_hist['g_rod']} Gols")
                    m4.metric("Empates", stats_hist['emp'])
                    st.markdown("---")
        else:
            st.markdown("<br>", unsafe_allow_html=True)

        if not df_historico.empty:
            for _, row in df_historico.iloc[::-1].iterrows():
                data_br = row['data_dt'].strftime("%d/%m/%Y")
                tc = row['time_casa']
                tf = row['time_fora']
                
                pen_html = f"🎯 Pên: {row['vencedor_penaltis']}" if row['foi_penaltis'] == "Sim" else "&nbsp;"
                
                with st.container(border=True):
                    c_hist, c_del = st.columns([9.5, 0.5])
                    
                    with c_hist:
                        # BLOCO HTML SEM IDENTAÇÃO (MARGEM ESQUERDA) PARA EVITAR BUG DO MARKDOWN NO STREAMLIT
                        html_hist = f"""
<div class="hist-desktop">
    <div style="flex: 1.5;">
        <p style='margin: 0;'>📅 <b>{data_br}</b><br><small style='color: gray;'>🎮 {row['versao_jogo']}</small></p>
    </div>
    <div style="flex: 3.5; display: flex; align-items: center; justify-content: flex-end; gap: 15px;">
        <span style='font-size: 16px; font-weight: bold;'>{row['jogador_casa']} ({tc})</span>
        <img src='{TEAMS.get(tc)}' style='width: 30px; height: 30px; object-fit: contain;'>
    </div>
    <div style="flex: 1.5; text-align: center;">
        <h3 style='margin: 0;'>{row['gols_casa']} x {row['gols_fora']}</h3>
        <p style='margin: 0; font-size:12px; color:gray; min-height: 14px;'>{pen_html}</p>
    </div>
    <div style="flex: 3.5; display: flex; align-items: center; justify-content: flex-start; gap: 15px;">
        <img src='{TEAMS.get(tf)}' style='width: 30px; height: 30px; object-fit: contain;'>
        <span style='font-size: 16px; font-weight: bold;'>({tf}) {row['jogador_fora']}</span>
    </div>
</div>

<div class="hist-mobile" style="padding: 10px 0;">
    <div style="text-align: center; margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 8px;">
        <span style="font-size: 13px; color: #E0E0E0;">📅 <b>{data_br}</b></span>
        <span style="font-size: 12px; color: gray; margin-left: 10px;">🎮 {row['versao_jogo']}</span>
    </div>
    <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
        <div style="flex: 1; display: flex; flex-direction: column; align-items: center; text-align: center;">
            <img src="{TEAMS.get(tc)}" style="width: 45px; height: 45px; object-fit: contain; margin-bottom: 5px;">
            <span style="font-size: 14px; font-weight: bold; color: #E0E0E0; line-height: 1.2;">{row['jogador_casa']}</span>
            <span style="font-size: 11px; color: #A0A0A0; line-height: 1.2;">{tc}</span>
        </div>
        
        <div style="flex: 0.8; display: flex; flex-direction: column; align-items: center; text-align: center;">
            <span style="font-size: 28px; font-weight: 900; color: #ffffff; letter-spacing: 1px;">{row['gols_casa']} x {row['gols_fora']}</span>
            <span style="font-size: 11px; color: #A0A0A0; margin-top: 4px;">{pen_html}</span>
        </div>
        
        <div style="flex: 1; display: flex; flex-direction: column; align-items: center; text-align: center;">
            <img src="{TEAMS.get(tf)}" style="width: 45px; height: 45px; object-fit: contain; margin-bottom: 5px;">
            <span style="font-size: 14px; font-weight: bold; color: #E0E0E0; line-height: 1.2;">{row['jogador_fora']}</span>
            <span style="font-size: 11px; color: #A0A0A0; line-height: 1.2;">{tf}</span>
        </div>
    </div>
</div>
"""
                        st.markdown(html_hist, unsafe_allow_html=True)
                        
                    with c_del:
                        if st.session_state["autenticado"]:
                            st.markdown("<style>div.stButton > button {margin-top: 15px;}</style>", unsafe_allow_html=True)
                            if st.button("🗑️", key=f"del_{row['id']}"):
                                excluir_partida(row['id'])
                                st.rerun()
        else:
            st.warning("Nenhum jogo encontrado para o período selecionado.")
    else:
        st.warning("Histórico vazio. Registre a primeira partida para começar.")