import streamlit as st
import pandas as pd
import datetime
from supabase import create_client, Client

# Configuração da página
st.set_page_config(page_title="FIFA - Nik vs Digo", page_icon="🎮", layout="wide")

# Inicializa o estado de autenticação
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

# ==============================================================================
# CABEÇALHO E LOGIN (Canto Superior Direito)
# ==============================================================================
col_title, col_login = st.columns([5, 1])

with col_title:
    st.title("🎮 FIFA EA FC - Nikolas vs Rodrigo")

with col_login:
    # Espaçamento para alinhar o botão de login com o título
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    
    if not st.session_state["autenticado"]:
        # Popover que imita o menu dropdown da sua imagem
        with st.popover("🔐 Acesso Restrito", use_container_width=True):
            senha_digitada = st.text_input("Senha", type="password", placeholder="Digite a senha...", label_visibility="collapsed")
            if st.button("Entrar", use_container_width=True):
                if senha_digitada == st.secrets["APP_PASSWORD"]:
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("Incorreta!")
    else:
        # Botão de Logout se já estiver autenticado
        if st.button("🔓 Sair do Painel", use_container_width=True):
            st.session_state["autenticado"] = False
            st.rerun()

st.markdown("---")

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
    "Al Ittihad": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a3/Al-Ittihad_Club_%28Saudi_Arabia%29_logo.svg/200px-Al-Ittihad_Club_%28Saudi_Arabia%29_logo.svg.png",
    "Al Nassr": "https://upload.wikimedia.org/wikipedia/pt/thumb/2/26/Al-Nassr_FC.png/250px-Al-Nassr_FC.png",
    "Boca Juniors": "https://crests.football-data.org/1127.png",
    "River Plate": "https://crests.football-data.org/1128.png",
    "Inter Miami CF": "https://upload.wikimedia.org/wikipedia/pt/thumb/c/c1/Inter_Miami_CF.png/250px-Inter_Miami_CF.png",
    "LA Galaxy": "https://upload.wikimedia.org/wikipedia/en/thumb/1/1a/LA_Galaxy_logo.svg/200px-LA_Galaxy_logo.svg.png",
    "Los Angeles FC": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f5/Los_Angeles_FC_logo.svg/200px-Los_Angeles_FC_logo.svg.png",
    "Galatasaray": "https://crests.football-data.org/611.png",
    "Fenerbahçe": "https://crests.football-data.org/610.png",
    
    # Seleções
    "Itália": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Logo_Italy_National_Football_Team_-_2023.svg/120px-Logo_Italy_National_Football_Team_-_2023.svg.png",
    "Brasil": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Brazilian_Football_Confederation_logo.svg/250px-Brazilian_Football_Confederation_logo.svg.png",
    "Portugal": "https://upload.wikimedia.org/wikipedia/pt/thumb/7/75/Portugal_FPF.png/250px-Portugal_FPF.png",
    "Argentina": "https://upload.wikimedia.org/wikipedia/pt/thumb/f/fc/230px-Afa_logo.svg.png/250px-230px-Afa_logo.svg.png",
    "Alemanha": "https://upload.wikimedia.org/wikipedia/pt/thumb/a/a9/DFBEagle.png/250px-DFBEagle.png",
    "Espanha": "https://upload.wikimedia.org/wikipedia/pt/3/31/Spain_National_Football_Team_badge.png",
    "França": "https://upload.wikimedia.org/wikipedia/pt/thumb/f/fb/France_national_football_team_seal.png/120px-France_national_football_team_seal.png",    
}
TEAMS = dict(sorted(TEAMS.items()))

VERSOES = ["EA FC 27", "EA FC 28", "EA FC 29", "EA FC 30", "EA FC 24", "EA FC 25", "EA FC 26"]

# ==============================================================================
# LÓGICA DE VITÓRIAS E SEQUÊNCIAS
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
    
    return {
        "total_jogos": len(df),
        "v_nik": len(df[df['vencedor'] == 'Nikolas']),
        "v_rod": len(df[df['vencedor'] == 'Rodrigo']),
        "emp": len(df[df['vencedor'] == 'Empate']),
        "g_nik": df[df['jogador_casa']=='Nikolas']['gols_casa'].sum() + df[df['jogador_fora']=='Nikolas']['gols_fora'].sum(),
        "g_rod": df[df['jogador_casa']=='Rodrigo']['gols_casa'].sum() + df[df['jogador_fora']=='Rodrigo']['gols_fora'].sum(),
        "pen_nik": len(df[(df['foi_penaltis'] == 'Sim') & (df['vencedor_penaltis'] == 'Nikolas')]),
        "pen_rod": len(df[(df['foi_penaltis'] == 'Sim') & (df['vencedor_penaltis'] == 'Rodrigo')]),
        "seq_at_p": seq_at_p, "seq_at_q": seq_at_q,
        "max_nik": max_n, "max_rod": max_r,
        "top_5": top_5,
        "nik_top_teams": nik_times.value_counts().head(3).to_dict() if not nik_times.empty else {},
        "rod_top_teams": rod_times.value_counts().head(3).to_dict() if not rod_times.empty else {}
    }

# ==============================================================================
# ABAS DINÂMICAS BASEADAS NA AUTENTICAÇÃO
# ==============================================================================
df_partidas = ler_partidas()

# Se autenticado, mostra as 3 abas. Se não, mostra só 2.
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
                if stats['seq_at_q'] > 0:
                    st.info(f"🔵 **{stats['seq_at_p']}** venceu a(s) última(s) **{stats['seq_at_q']}** partida(s)!")
                else:
                    st.info(f"🔘 Última partida foi {stats['seq_at_p']}")
            
            with c_s2:
                st.subheader("🏆 Recordes de Sequência")
                if stats['max_nik'] >= stats['max_rod']:
                    st.success(f"👑 A maior sequência histórica é de **Nikolas** com **{stats['max_nik']}** vitórias seguidas.")
                    st.info(f"A maior sequência histórica de **Rodrigo** é de **{stats['max_rod']}** vitórias seguidas.")
                else:
                    st.success(f"👑 A maior sequência histórica é de **Rodrigo** com **{stats['max_rod']}** vitórias seguidas.")
                    st.info(f"A maior sequência histórica de **Nikolas** é de **{stats['max_nik']}** vitórias seguidas.")

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
                
            st.markdown("---")
            
            st.markdown("### 👕 Times mais utilizados")
            c_t1, c_t2 = st.columns(2)
            
            with c_t1:
                st.markdown("**Top 3 - Nikolas**")
                for time, count in stats['nik_top_teams'].items():
                    st.markdown(
                        f"<div style='display: flex; align-items: center; gap: 10px; margin-bottom: 5px;'>"
                        f"<img src='{TEAMS.get(time)}' width='25' style='object-fit: contain;'>"
                        f"<span><b>{time}</b> ({count} jogos)</span>"
                        f"</div>", 
                        unsafe_allow_html=True
                    )
                    
            with c_t2:
                st.markdown("**Top 3 - Rodrigo**")
                for time, count in stats['rod_top_teams'].items():
                    st.markdown(
                        f"<div style='display: flex; align-items: center; gap: 10px; margin-bottom: 5px;'>"
                        f"<img src='{TEAMS.get(time)}' width='25' style='object-fit: contain;'>"
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
        
        # --- Identificação dinâmica do índice para o Real Madrid e FC Barcelona ---
        lista_de_times = list(TEAMS.keys())
        
        try: idx_real_madrid = lista_de_times.index("Real Madrid")
        except ValueError: idx_real_madrid = 0
            
        try: idx_barcelona = lista_de_times.index("FC Barcelona")
        except ValueError: idx_barcelona = 0

        # Onde Nikolas estiver, o padrão é Real Madrid. Onde Rodrigo estiver, o padrão é FC Barcelona.
        idx_padrao_casa = idx_real_madrid if jogador_casa == "Nikolas" else idx_barcelona
        idx_padrao_fora = idx_real_madrid if jogador_fora == "Nikolas" else idx_barcelona
        
        col_c, col_d, col_f = st.columns([2, 1, 2])
        
        with col_c:
            st.markdown(f"### 🏠 Casa ({jogador_casa})")
            t_c = st.selectbox("Time", lista_de_times, index=idx_padrao_casa, key="tc")
            st.markdown(f'''
                <div style="height: 100px; display: flex; align-items: center; justify-content: flex-start; margin-bottom: 10px;">
                    <img src="{TEAMS[t_c]}" style="max-height: 80px; max-width: 80px; object-fit: contain;">
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
                    <img src="{TEAMS[t_f]}" style="max-height: 80px; max-width: 80px; object-fit: contain;">
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
                
                with st.container(border=True):
                    c_dt, c_casa, c_placar, c_fora, c_del = st.columns([1.5, 3.5, 1.5, 3.5, 0.5])
                    
                    with c_dt:
                        st.markdown(f"<p style='margin-top: 15px;'>📅 <b>{data_br}</b><br><small style='color: gray;'>🎮 {row['versao_jogo']}</small></p>", unsafe_allow_html=True)
                    
                    with c_casa:
                        tc = row['time_casa']
                        st.markdown(
                            f"<div style='display: flex; align-items: center; justify-content: flex-end; gap: 15px; height: 100%; margin-top: 10px;'>"
                            f"<span style='font-size: 16px; font-weight: bold;'>{row['jogador_casa']} ({tc})</span>"
                            f"<img src='{TEAMS.get(tc)}' width='30' style='object-fit: contain;'>"
                            f"</div>", 
                            unsafe_allow_html=True
                        )
                        
                    with c_placar:
                        st.markdown(
                            f"<h3 style='text-align: center; margin-top: 10px;'>{row['gols_casa']} x {row['gols_fora']}</h3>", 
                            unsafe_allow_html=True
                        )
                        if row['foi_penaltis'] == "Sim":
                            st.markdown(f"<p style='text-align:center; font-size:12px; color:gray; margin-top: -10px;'>🎯 Pênaltis: {row['vencedor_penaltis']}</p>", unsafe_allow_html=True)
                        
                    with c_fora:
                        tf = row['time_fora']
                        st.markdown(
                            f"<div style='display: flex; align-items: center; justify-content: flex-start; gap: 15px; height: 100%; margin-top: 10px;'>"
                            f"<img src='{TEAMS.get(tf)}' width='30' style='object-fit: contain;'>"
                            f"<span style='font-size: 16px; font-weight: bold;'>({tf}) {row['jogador_fora']}</span>"
                            f"</div>", 
                            unsafe_allow_html=True
                        )
                        
                    with c_del:
                        # O BOTÃO DE LIXEIRA SÓ APARECE SE ESTIVER AUTENTICADO
                        if st.session_state["autenticado"]:
                            st.markdown("<style>div.stButton > button {margin-top: 10px;}</style>", unsafe_allow_html=True)
                            if st.button("🗑️", key=f"del_{row['id']}"):
                                excluir_partida(row['id'])
                                st.rerun()
        else:
            st.warning("Nenhum jogo encontrado para o período selecionado.")
    else:
        st.warning("Histórico vazio. Registre a primeira partida para começar.")