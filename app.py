import streamlit as st
import pandas as pd
import random
import itertools
import time
import re
from supabase import create_client, Client

st.set_page_config(page_title="FIFA Tournaments", page_icon="🏆", layout="wide", initial_sidebar_state="collapsed")

# ==============================================================================
# ⚠️ CONFIGURAÇÕES DA SUA TABELA DE X1
# ==============================================================================
NOME_TABELA_X1 = "partidas"

# ==============================================================================
# ESTÉTICA PRETO FOSCO E MÁGICA DA TABELA CENTRALIZADA
# ==============================================================================
st.markdown("""
    <style>
        .stApp { background-color: #121212; color: #E0E0E0; }
        div[data-testid="stMetric"], div[data-testid="stContainer"] {
            background-color: #1E1E1E; border-radius: 8px; padding: 15px; border: 1px solid #333333;
        }
        .stTabs [data-baseweb="tab-list"] { background-color: #121212; }
        .stTabs [data-baseweb="tab"] { color: #A0A0A0; font-weight: bold; }
        .stTabs [aria-selected="true"] { color: #4DE17C !important; border-bottom-color: #4DE17C !important; }
        div.stButton > button { margin-top: 15px; }
        
        [data-testid="stTable"] table { width: 100%; }
        [data-testid="stTable"] th { text-align: center !important; }
        [data-testid="stTable"] td { text-align: center !important; }
        [data-testid="stTable"] th:nth-child(2), [data-testid="stTable"] td:nth-child(2) { 
            text-align: left !important; padding-left: 15px !important;
        }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# SISTEMA DE LOGIN DISCRETO (BARRA LATERAL)
# ==============================================================================
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

with st.sidebar:
    if not st.session_state["autenticado"]:
        with st.expander("🔐 Acesso Restrito", expanded=False):
            with st.form("form_login_admin", border=False):
                senha_digitada = st.text_input("Senha", type="password", placeholder="Digite a senha...", label_visibility="collapsed")
                btn_entrar = st.form_submit_button("Entrar", use_container_width=True)
                
                if btn_entrar:
                    senha_correta = st.secrets.get("APP_PASSWORD", "admin123") 
                    if senha_digitada == senha_correta:
                        st.session_state["autenticado"] = True
                        st.toast("Login realizado com sucesso!", icon="🔓")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Senha Incorreta!")
    else:
        with st.expander("🔐 Acesso Restrito", expanded=True):
            st.success("Modo Edição Ativado! 🟢")
            if st.button("Sair (Logout)", use_container_width=True):
                st.session_state["autenticado"] = False
                st.rerun()

# ==============================================================================
# DICIONÁRIO DE TIMES E LOGOS COMPLETAS
# ==============================================================================
TEAMS = {
    "Arsenal": "https://crests.football-data.org/57.png", "Aston Villa": "https://crests.football-data.org/58.png",
    "Bournemouth": "https://crests.football-data.org/1044.png", "Brentford": "https://crests.football-data.org/402.png",
    "Brighton": "https://crests.football-data.org/397.png", "Chelsea": "https://crests.football-data.org/61.png",
    "Crystal Palace": "https://crests.football-data.org/354.png", "Everton": "https://crests.football-data.org/62.png",
    "Fulham": "https://crests.football-data.org/63.png", "Ipswich Town": "https://crests.football-data.org/349.png",
    "Leicester City": "https://crests.football-data.org/338.png", "Liverpool": "https://crests.football-data.org/64.png",
    "Manchester City": "https://crests.football-data.org/65.png", "Manchester United": "https://crests.football-data.org/66.png",
    "Newcastle United": "https://crests.football-data.org/67.png", "Nottingham Forest": "https://crests.football-data.org/68.png",
    "Southampton": "https://crests.football-data.org/340.png", "Tottenham Hotspur": "https://crests.football-data.org/73.png",
    "West Ham United": "https://crests.football-data.org/563.png", "Wolverhampton": "https://crests.football-data.org/76.png",
    "Alavés": "https://crests.football-data.org/263.png", "Athletic Club": "https://crests.football-data.org/77.png",
    "Atlético Madrid": "https://crests.football-data.org/78.png", "Celta de Vigo": "https://crests.football-data.org/558.png",
    "Espanyol": "https://crests.football-data.org/80.png", "FC Barcelona": "https://crests.football-data.org/81.png",
    "Getafe": "https://crests.football-data.org/82.png", "Girona": "https://crests.football-data.org/298.png",
    "Las Palmas": "https://crests.football-data.org/275.png", "Leganés": "https://crests.football-data.org/745.png",
    "Mallorca": "https://crests.football-data.org/89.png", "Osasuna": "https://crests.football-data.org/79.png",
    "Rayo Vallecano": "https://crests.football-data.org/87.png", "Real Betis": "https://crests.football-data.org/90.png",
    "Real Madrid": "https://crests.football-data.org/86.png", "Real Sociedad": "https://crests.football-data.org/92.png",
    "Real Valladolid": "https://crests.football-data.org/250.png", "Sevilla FC": "https://crests.football-data.org/559.png",
    "Valencia CF": "https://crests.football-data.org/95.png", "Villarreal CF": "https://crests.football-data.org/94.png",
    "Atalanta": "https://crests.football-data.org/102.png", "Bologna": "https://crests.football-data.org/103.png",
    "Cagliari": "https://crests.football-data.org/104.png", "Como": "https://crests.football-data.org/105.png",
    "Empoli": "https://crests.football-data.org/107.png", "Fiorentina": "https://crests.football-data.org/99.png",
    "Genoa": "https://crests.football-data.org/106.png", "Inter de Milão": "https://crests.football-data.org/108.png",
    "Juventus": "https://crests.football-data.org/109.png", "Lazio": "https://crests.football-data.org/110.png",
    "Lecce": "https://crests.football-data.org/112.png", "Milan": "https://crests.football-data.org/98.png",
    "Monza": "https://crests.football-data.org/5911.png", "Napoli": "https://crests.football-data.org/113.png",
    "Parma": "https://crests.football-data.org/115.png", "Roma": "https://crests.football-data.org/100.png",
    "Torino": "https://crests.football-data.org/586.png", "Udinese": "https://crests.football-data.org/115.png",
    "Venezia": "https://crests.football-data.org/117.png", "Verona": "https://crests.football-data.org/450.png",
    "Bayer Leverkusen": "https://crests.football-data.org/3.png", "Bayern de Munique": "https://crests.football-data.org/5.png",
    "Borussia Dortmund": "https://crests.football-data.org/4.png", "Borussia M'gladbach": "https://crests.football-data.org/18.png",
    "Eintracht Frankfurt": "https://crests.football-data.org/19.png", "Freiburg": "https://crests.football-data.org/17.png",
    "Heidenheim": "https://crests.football-data.org/44.png", "Hoffenheim": "https://crests.football-data.org/2.png",
    "Holstein Kiel": "https://crests.football-data.org/32.png", "Mainz 05": "https://crests.football-data.org/15.png",
    "RB Leipzig": "https://crests.football-data.org/721.png", "St. Pauli": "https://crests.football-data.org/35.png",
    "Stuttgart": "https://crests.football-data.org/10.png", "Werder Bremen": "https://crests.football-data.org/12.png",
    "Wolfsburg": "https://crests.football-data.org/11.png",
    "Paris SG": "https://crests.football-data.org/524.png", "Marseille": "https://crests.football-data.org/516.png",
    "Lyon": "https://crests.football-data.org/523.png", "Lille": "https://crests.football-data.org/521.png",
    "AS Monaco": "https://crests.football-data.org/548.png",
    "FC Porto": "https://crests.football-data.org/503.png", "SL Benfica": "https://crests.football-data.org/1903.png",
    "Sporting CP": "https://upload.wikimedia.org/wikipedia/pt/thumb/3/3e/Sporting_Clube_de_Portugal.png/120px-Sporting_Clube_de_Portugal.png",
    "Ajax": "https://crests.football-data.org/678.png", "PSV Eindhoven": "https://crests.football-data.org/682.png",
    "Feyenoord": "https://crests.football-data.org/675.png",
    "Boca Juniors": "https://crests.football-data.org/1127.png", "River Plate": "https://crests.football-data.org/1128.png",
    "Inter Miami CF": "https://upload.wikimedia.org/wikipedia/pt/thumb/c/c1/Inter_Miami_CF.png/250px-Inter_Miami_CF.png",
    "Galatasaray": "https://crests.football-data.org/611.png", "Fenerbahçe": "https://crests.football-data.org/610.png",
    "Internacional":"https://logodetimes.com/times/internacional/logo-internacional-4096.png",
    "Grêmio":"https://logodetimes.com/times/gremio/logo-gremio-4096.png",
    "Brasil": "https://logodetimes.com/times/selecao-brasileira-brasil-novo-logo-2019-com-estrelas-e-nome/logo-selecao-brasileira-brasil-novo-logo-2019-com-estrelas-e-nome-4096.png",
    "Argentina": "https://logodetimes.com/times/argentina/selecao-argentina-de-futebol-256.png",
    "França": "https://logodownload.org/wp-content/uploads/2022/07/france-national-football-team-logo.png",
    "Alemanha": "https://logodetimes.com/times/alemanha/selecao-alema-de-futebol-256.png",
    "Espanha": "https://logodownload.org/wp-content/uploads/2022/08/spain-national-football-team-logo-0.png",
    "Portugal": "https://upload.wikimedia.org/wikipedia/pt/7/75/Portugal_FPF.png",
    "Itália": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Logo_Italy_National_Football_Team_-_2023.svg/120px-Logo_Italy_National_Football_Team_-_2023.svg.png"
}
TEAMS = dict(sorted(TEAMS.items()))
LISTA_TIMES = list(TEAMS.keys())

# ==============================================================================
# CONEXÃO SUPABASE
# ==============================================================================
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# ==============================================================================
# FUNÇÕES BÁSICAS DE BANCO DE DADOS E PAGINAÇÃO (COM CACHE!)
# ==============================================================================
def formatar_data(data_str):
    if not data_str: return "N/A"
    try:
        partes = data_str.split('-')
        if len(partes) == 3: return f"{partes[2]}/{partes[1]}/{partes[0]}"
    except:
        pass
    return data_str

def estilizar_tabela(df):
    if df.empty: return df
    styler = df.style.set_properties(**{'text-align': 'center !important'})
    if 'Jogador' in df.columns:
        styler = styler.set_properties(subset=['Jogador'], **{'text-align': 'left !important'})
    styler = styler.set_table_styles([
        dict(selector='th', props=[('text-align', 'center !important')]),
        dict(selector='td', props=[('text-align', 'center !important')])
    ])
    if '%' in df.columns:
        styler = styler.format({'%': '{:.1f}%'})
    return styler

@st.cache_data
def get_todas_partidas_concluidas():
    todas_partidas = []
    start = 0
    step = 1000
    while True:
        try:
            res = supabase.table("tour_partidas").select("*").range(start, start + step - 1).execute()
            if not res.data: break
            todas_partidas.extend(res.data)
            if len(res.data) < step: break
            start += step
        except Exception:
            time.sleep(1) 
    return [p for p in todas_partidas if p['gols_casa'] is not None]

@st.cache_data
def get_jogadores():
    res = supabase.table("jogadores").select("*").execute()
    return [j['nome'] for j in res.data] if res.data else []

def add_jogador(nome):
    supabase.table("jogadores").insert({"nome": nome}).execute()
    st.cache_data.clear() 

@st.cache_data
def get_todas_edicoes():
    res = supabase.table("tour_edicoes").select("*").order("id", desc=True).execute()
    return res.data if res.data else []

@st.cache_data
def get_edicoes_abertas():
    res = supabase.table("tour_edicoes").select("*").eq("status", "Aberto").execute()
    return res.data if res.data else []

@st.cache_data
def get_edicoes_andamento():
    res = supabase.table("tour_edicoes").select("*").eq("status", "Em Andamento").order("id", desc=True).execute()
    return res.data if res.data else []

@st.cache_data
def get_edicoes_finalizadas():
    res = supabase.table("tour_edicoes").select("*").eq("status", "Finalizado").order("id", desc=True).execute()
    return res.data if res.data else []

def criar_edicao(nome, formato, qtd_grupos, ida_volta_grp, ida_volta_semi, ida_volta_final):
    data_atual = time.strftime("%Y-%m-%d")
    nova_edicao = {
        "nome": nome, "formato": formato, "qtd_grupos": qtd_grupos if formato.startswith("Grupos") else None,
        "ida_e_volta_grupos": ida_volta_grp, "ida_e_volta_semi": ida_volta_semi,
        "ida_e_volta_final": ida_volta_final, "status": "Aberto"
    }
    try:
        nova_edicao_com_data = nova_edicao.copy()
        nova_edicao_com_data["data_inicio"] = data_atual
        nova_edicao_com_data["data_fim"] = ""
        supabase.table("tour_edicoes").insert(nova_edicao_com_data).execute()
    except Exception:
        supabase.table("tour_edicoes").insert(nova_edicao).execute()
    st.cache_data.clear()

def finalizar_edicao(edicao_id):
    data_atual = time.strftime("%Y-%m-%d")
    try:
        supabase.table("tour_edicoes").update({"status": "Finalizado", "data_fim": data_atual}).eq("id", edicao_id).execute()
    except Exception:
        supabase.table("tour_edicoes").update({"status": "Finalizado"}).eq("id", edicao_id).execute()
    st.cache_data.clear()

def excluir_edicao(edicao_id):
    res = supabase.table("tour_edicoes").select("nome").eq("id", edicao_id).execute()
    if res.data:
        nome_camp = res.data[0]['nome']
        try:
            padrao = f"Torneio: {nome_camp}%"
            supabase.table(NOME_TABELA_X1).delete().ilike("versao_jogo", padrao).execute()
        except Exception as e:
            pass
            
    supabase.table("tour_partidas").delete().eq("torneio_id", edicao_id).execute()
    supabase.table("tour_participantes").delete().eq("torneio_id", edicao_id).execute()
    supabase.table("tour_edicoes").delete().eq("id", edicao_id).execute()
    st.cache_data.clear()

def registrar_sorteio(torneio_id, participantes_por_grupo):
    dados_insert = []
    for grupo, jogadores in participantes_por_grupo.items():
        for jog in jogadores:
            dados_insert.append({"torneio_id": torneio_id, "jogador_nome": jog, "grupo": grupo})
    supabase.table("tour_participantes").insert(dados_insert).execute()
    st.cache_data.clear()

def gerar_confrontos_automaticos(edicao):
    participantes = supabase.table("tour_participantes").select("*").eq("torneio_id", edicao['id']).execute().data
    grupos = {}
    for p in participantes:
        grupos.setdefault(p['grupo'], []).append(p['jogador_nome'])
    
    novas_partidas = []
    for grupo, jogs in grupos.items():
        fase_nome = f"Grupo {grupo}" if edicao['formato'].startswith('Grupos') else "Fase Única"
        confrontos = list(itertools.combinations(jogs, 2))
        for j1, j2 in confrontos:
            novas_partidas.append({"torneio_id": edicao['id'], "fase": fase_nome, "jogador_casa": j1, "jogador_fora": j2})
            if edicao['ida_e_volta_grupos']:
                novas_partidas.append({"torneio_id": edicao['id'], "fase": fase_nome, "jogador_casa": j2, "jogador_fora": j1})
    if novas_partidas:
        supabase.table("tour_partidas").insert(novas_partidas).execute()
    st.cache_data.clear()

@st.cache_data
def get_partidas(edicao_id):
    res = supabase.table("tour_partidas").select("*").eq("torneio_id", edicao_id).order("id").execute()
    return res.data if res.data else []

def salvar_placar(partida_id, t_casa, g_casa, t_fora, g_fora, foi_pen, venc_pen):
    atualizacao = {
        "time_casa": t_casa, "gols_casa": g_casa, "time_fora": t_fora, "gols_fora": g_fora,
        "foi_penaltis": foi_pen, "vencedor_penaltis": venc_pen
    }
    supabase.table("tour_partidas").update(atualizacao).eq("id", partida_id).execute()

    res_p = supabase.table("tour_partidas").select("*").eq("id", partida_id).execute()
    if res_p.data:
        p = res_p.data[0]
        jogadores = [p['jogador_casa'], p['jogador_fora']]
        
        jogadores_limpos = [j.strip().lower() for j in jogadores]
        
        if "nikolas" in jogadores_limpos and "rodrigo" in jogadores_limpos:
            res_ed = supabase.table("tour_edicoes").select("nome").eq("id", p['torneio_id']).execute()
            nome_camp = res_ed.data[0]['nome'] if res_ed.data else "Campeonato"
            
            if "Simulada" not in nome_camp and "simulada" not in nome_camp.lower():
                origem_detalhada = f"Torneio: {nome_camp} ({p['fase']})"
                data_atual = time.strftime("%Y-%m-%d")
                
                # TRADUÇÃO EXCLUSIVA PARA O IDIOMA DO SEU X1
                foi_pen_texto = "Sim" if foi_pen else "Não"
                venc_pen_texto = venc_pen if venc_pen else ""
                
                dados_x1 = {
                    "versao_jogo": origem_detalhada, 
                    "data": data_atual,
                    "jogador_casa": p['jogador_casa'],
                    "time_casa": t_casa,
                    "gols_casa": g_casa,
                    "jogador_fora": p['jogador_fora'],
                    "time_fora": t_fora,
                    "gols_fora": g_fora,
                    "foi_penaltis": foi_pen_texto,
                    "vencedor_penaltis": venc_pen_texto
                }
                try:
                    supabase.table(NOME_TABELA_X1).insert(dados_x1).execute()
                    st.toast("⚔️ Resultado espelhado no X1 com sucesso!", icon="🔥")
                except Exception as e:
                    st.error(f"Erro ao salvar no X1: {e}")
                    
    st.cache_data.clear()

def render_form_placar(p, precisa_desempate=False):
    idx_c = LISTA_TIMES.index(p['time_casa']) if p['time_casa'] in LISTA_TIMES else 0
    idx_f = LISTA_TIMES.index(p['time_fora']) if p['time_fora'] in LISTA_TIMES else 0
    chave_c = f"tc_{p['id']}_{p.get('time_casa', 'vazio')}"
    chave_f = f"tf_{p['id']}_{p.get('time_fora', 'vazio')}"
    
    g_c_atual = int(p['gols_casa']) if p['gols_casa'] is not None else 0
    g_f_atual = int(p['gols_fora']) if p['gols_fora'] is not None else 0
    
    titulo_exp = f"⚠️ DESEMPATE AGREGADO | ⚽ {p['jogador_casa']} x {p['jogador_fora']} | {p['fase']}" if precisa_desempate else f"⚽ {p['jogador_casa']} x {p['jogador_fora']} | {p['fase']}"
    
    with st.expander(titulo_exp, expanded=precisa_desempate):
        if precisa_desempate:
            st.error("A soma dos placares (Ida e Volta) terminou empatada! Informe quem venceu nos pênaltis.")
            
        with st.form(f"form_placar_{p['id']}"):
            cf1, cf2 = st.columns(2)
            with cf1:
                st.markdown(f"**🏠 {p['jogador_casa']}**")
                time_c = st.selectbox("Time", LISTA_TIMES, index=idx_c, key=chave_c)
                gol_c = st.number_input("Gols", min_value=0, value=g_c_atual, key=f"gc_{p['id']}")
            with cf2:
                st.markdown(f"**✈️ {p['jogador_fora']}**")
                time_f = st.selectbox("Time ", LISTA_TIMES, index=idx_f, key=chave_f)
                gol_f = st.number_input("Gols ", min_value=0, value=g_f_atual, key=f"gf_{p['id']}")
                
            foi_p, venc_p = p.get('foi_penaltis', False), p.get('vencedor_penaltis', None)
            is_mata_mata = any(x in p['fase'] for x in ['Quartas', 'Semifinal', 'Final', '3º', 'Oitavas', '16-avos'])
            
            if is_mata_mata or (gol_c == gol_f) or precisa_desempate:
                st.info("Houve pênaltis? (Marque apenas se este foi o jogo decisivo do confronto)")
                teve_p = st.checkbox("Sim, vitória nos pênaltis", value=bool(foi_p), key=f"cp_{p['id']}")
                
                idx_venc = 0
                if venc_p == p['jogador_fora']: idx_venc = 1
                venc_p_selecionado = st.radio("Quem venceu nos pênaltis?", [p['jogador_casa'], p['jogador_fora']], index=idx_venc, key=f"vp_{p['id']}")
                    
            if st.form_submit_button("💾 Salvar Placar", use_container_width=True):
                if 'teve_p' in locals() and teve_p:
                    foi_p = True
                    venc_p = venc_p_selecionado
                else:
                    foi_p = False
                    venc_p = None
                    
                salvar_placar(p['id'], time_c, gol_c, time_f, gol_f, foi_p, venc_p)
                st.toast("Placar Registrado!", icon="⚽")
                time.sleep(1)
                st.rerun()

def render_partida_somente_leitura(p):
    logo_c = f'<img src="{TEAMS.get(p["time_casa"], "")}" width="20" style="margin-left:8px;">' if p.get('time_casa') else ""
    logo_f = f'<img src="{TEAMS.get(p["time_fora"], "")}" width="20" style="margin-right:8px;">' if p.get('time_fora') else ""
    st.markdown(f"""
    <div style="background-color: #1a1a1a; padding: 12px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #333;">
        <span style="font-size: 13px; color: #a0a0a0;">{p['fase']}</span><br>
        <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 5px;">
            <div style="display:flex; align-items:center; width: 45%; justify-content: flex-end;">
                <b style="font-size: 16px;">{p['jogador_casa']}</b>{logo_c}
            </div>
            <span style="font-size: 14px; color: #666; width: 10%; text-align: center;"> x </span>
            <div style="display:flex; align-items:center; width: 45%; justify-content: flex-start;">
                {logo_f}<b style="font-size: 16px;">{p['jogador_fora']}</b>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# INTELIGÊNCIA DINÂMICA DE CHAVEAMENTO (A MÁQUINA DE MATA-MATA)
# ==============================================================================
def get_regras_edicao(edicao):
    fmt = edicao.get('formato', '')
    if fmt.startswith("Grupos"):
        parts = fmt.split('|')
        if len(parts) >= 5:
            return {"tipo": "Grupos", "classificados": int(parts[1]), "ida_oitavas": bool(int(parts[2])), "ida_quartas": bool(int(parts[3])), "ida_16avos": bool(int(parts[4]))}
        else:
            qg = edicao.get('qtd_grupos', 1)
            return {"tipo": "Grupos", "classificados": 2 if qg in [2,4] else (4 if qg == 1 else 1), "ida_oitavas": False, "ida_quartas": False, "ida_16avos": False}
    return {"tipo": "Pontos Corridos"}

def get_ida_volta(fase_nome, edicao, regras):
    if fase_nome == "16-avos": return regras.get("ida_16avos", False)
    if fase_nome == "Oitavas": return regras.get("ida_oitavas", False)
    if fase_nome == "Quartas": return regras.get("ida_quartas", False)
    if fase_nome == "Semifinal": return edicao['ida_e_volta_semi']
    if fase_nome == "Final": return edicao['ida_e_volta_final']
    return False

def obter_resultado_mata_mata(partidas_fase):
    if not partidas_fase or any(p['gols_casa'] is None for p in partidas_fase): return None, None
    p1, p2 = partidas_fase[0]['jogador_casa'], partidas_fase[0]['jogador_fora']
    gols_p1, gols_p2 = 0, 0
    venc_pen = None
    for p in partidas_fase:
        if p['jogador_casa'] == p1: gols_p1 += p['gols_casa']; gols_p2 += p['gols_fora']
        else: gols_p1 += p['gols_fora']; gols_p2 += p['gols_casa']
        if p['foi_penaltis']: venc_pen = p['vencedor_penaltis']
    if gols_p1 > gols_p2: return p1, p2
    if gols_p2 > gols_p1: return p2, p1
    if venc_pen == p1: return p1, p2
    if venc_pen == p2: return p2, p1
    return None, None

def get_confrontos_iniciais(total, qg, tab):
    c = []
    def get_p(grp, pos):
        if len(tab[grp]) >= pos: return tab[grp].iloc[pos-1]['Jogador']
        return f"Vazio ({grp}{pos})"

    if total == 32:
        if qg == 1:
            seq = [1,32, 16,17, 9,24, 8,25, 4,29, 13,20, 12,21, 5,28, 2,31, 15,18, 10,23, 7,26, 3,30, 14,19, 11,22, 6,27]
            c = [(get_p('A', seq[i]), get_p('A', seq[i+1])) for i in range(0, 32, 2)]
        elif qg == 2:
            c = [(get_p('A',1), get_p('B',16)), (get_p('B',8), get_p('A',9)), (get_p('A',5), get_p('B',12)), (get_p('B',4), get_p('A',13)), (get_p('A',3), get_p('B',14)), (get_p('B',6), get_p('A',11)), (get_p('A',7), get_p('B',10)), (get_p('B',2), get_p('A',15)), (get_p('B',1), get_p('A',16)), (get_p('A',8), get_p('B',9)), (get_p('B',5), get_p('A',12)), (get_p('A',4), get_p('B',13)), (get_p('B',3), get_p('A',14)), (get_p('A',6), get_p('B',11)), (get_p('B',7), get_p('A',10)), (get_p('A',2), get_p('B',15))]
        elif qg == 4:
            c = [(get_p('A',1), get_p('B',8)), (get_p('C',4), get_p('D',5)), (get_p('A',3), get_p('B',6)), (get_p('C',2), get_p('D',7)), (get_p('B',1), get_p('A',8)), (get_p('D',4), get_p('C',5)), (get_p('B',3), get_p('A',6)), (get_p('D',2), get_p('C',7)), (get_p('C',1), get_p('D',8)), (get_p('A',4), get_p('B',5)), (get_p('C',3), get_p('D',6)), (get_p('A',2), get_p('B',7)), (get_p('D',1), get_p('C',8)), (get_p('B',4), get_p('A',5)), (get_p('D',3), get_p('C',6)), (get_p('B',2), get_p('A',7))]
        elif qg == 8:
            c = [(get_p('A',1), get_p('B',4)), (get_p('C',2), get_p('D',3)), (get_p('E',1), get_p('F',4)), (get_p('G',2), get_p('H',3)), (get_p('B',1), get_p('A',4)), (get_p('D',2), get_p('C',3)), (get_p('F',1), get_p('E',4)), (get_p('H',2), get_p('G',3)), (get_p('C',1), get_p('D',4)), (get_p('A',2), get_p('B',3)), (get_p('G',1), get_p('H',4)), (get_p('E',2), get_p('F',3)), (get_p('D',1), get_p('C',4)), (get_p('B',2), get_p('A',3)), (get_p('H',1), get_p('G',4)), (get_p('F',2), get_p('E',3))]
    elif total == 16:
        if qg == 1:
            seq = [1,16, 8,9, 4,13, 5,12, 2,15, 7,10, 3,14, 6,11]
            c = [(get_p('A', seq[i]), get_p('A', seq[i+1])) for i in range(0, 16, 2)]
        elif qg == 2:
            c = [(get_p('A',1), get_p('B',8)), (get_p('B',4), get_p('A',5)), (get_p('A',3), get_p('B',6)), (get_p('B',2), get_p('A',7)), (get_p('B',1), get_p('A',8)), (get_p('A',4), get_p('B',5)), (get_p('B',3), get_p('A',6)), (get_p('A',2), get_p('B',7))]
        elif qg == 4:
            c = [(get_p('A',1), get_p('B',4)), (get_p('C',2), get_p('D',3)), (get_p('B',1), get_p('A',4)), (get_p('D',2), get_p('C',3)), (get_p('C',1), get_p('D',4)), (get_p('A',2), get_p('B',3)), (get_p('D',1), get_p('C',4)), (get_p('B',2), get_p('A',3))]
        elif qg == 8:
            c = [(get_p('A',1), get_p('B',2)), (get_p('C',1), get_p('D',2)), (get_p('E',1), get_p('F',2)), (get_p('G',1), get_p('H',2)), (get_p('B',1), get_p('A',2)), (get_p('D',1), get_p('C',2)), (get_p('F',1), get_p('E',2)), (get_p('H',1), get_p('G',2))]
    elif total == 8:
        if qg == 1:
            seq = [1,8, 4,5, 2,7, 3,6]
            c = [(get_p('A', seq[i]), get_p('A', seq[i+1])) for i in range(0, 8, 2)]
        elif qg == 2:
            c = [(get_p('A',1), get_p('B',4)), (get_p('B',2), get_p('A',3)), (get_p('B',1), get_p('A',4)), (get_p('A',2), get_p('B',3))]
        elif qg == 4:
            c = [(get_p('A',1), get_p('B',2)), (get_p('C',1), get_p('D',2)), (get_p('B',1), get_p('A',2)), (get_p('D',1), get_p('C',2))]
    elif total == 4:
        if qg == 1: c = [(get_p('A',1), get_p('A',4)), (get_p('A',2), get_p('A',3))]
        elif qg == 2: c = [(get_p('A',1), get_p('B',2)), (get_p('B',1), get_p('A',2))]
    elif total == 2:
        if qg == 1: c = [(get_p('A',1), get_p('A',2))]
        elif qg == 2: c = [(get_p('A',1), get_p('B',1))]
    return c

def gerar_fase_mata_mata_dinamica(edicao, tabelas, partidas_bd, regras, fase_nova):
    ida_e_volta = get_ida_volta(fase_nova, edicao, regras)
    fases_ordem = []
    total = edicao['qtd_grupos'] * regras['classificados']
    if total == 32: fases_ordem = ["16-avos", "Oitavas", "Quartas", "Semifinal", "Final"]
    elif total == 16: fases_ordem = ["Oitavas", "Quartas", "Semifinal", "Final"]
    elif total == 8: fases_ordem = ["Quartas", "Semifinal", "Final"]
    elif total == 4: fases_ordem = ["Semifinal", "Final"]
    elif total == 2: fases_ordem = ["Final"]
    
    idx_fase = fases_ordem.index(fase_nova)
    novas_partidas = []
    
    if idx_fase == 0:
        confrontos = get_confrontos_iniciais(total, edicao['qtd_grupos'], tabelas)
        for i, (j1, j2) in enumerate(confrontos):
            nome_chave = f"{fase_nova} {i+1}" if total > 2 else fase_nova
            if fase_nova == "Semifinal": nome_chave = f"Semifinal {i+1}"
            novas_partidas.append({"torneio_id": edicao['id'], "fase": nome_chave, "jogador_casa": j1, "jogador_fora": j2})
            if ida_e_volta: novas_partidas.append({"torneio_id": edicao['id'], "fase": nome_chave, "jogador_casa": j2, "jogador_fora": j1})
    else:
        fase_ant = fases_ordem[idx_fase - 1]
        jogos_atuais = [p for p in partidas_bd if fase_ant in p['fase'] and '3º' not in p['fase']]
        
        def get_num(s):
            nums = re.findall(r'\d+', s)
            return int(nums[-1]) if nums else 0
            
        nomes_fases = sorted(list(set([p['fase'] for p in jogos_atuais])), key=get_num)
        
        vencedores = []
        for nf in nomes_fases:
            v, _ = obter_resultado_mata_mata([p for p in jogos_atuais if p['fase'] == nf])
            vencedores.append(v)
            
        for i in range(0, len(vencedores), 2):
            idx_nova_chave = (i // 2) + 1
            nome_chave = f"{fase_nova} {idx_nova_chave}" if len(vencedores) > 2 else fase_nova
            if fase_nova == "Semifinal": nome_chave = f"Semifinal {idx_nova_chave}"
            j1, j2 = vencedores[i], vencedores[i+1]
            
            novas_partidas.append({"torneio_id": edicao['id'], "fase": nome_chave, "jogador_casa": j1, "jogador_fora": j2})
            if ida_e_volta: novas_partidas.append({"torneio_id": edicao['id'], "fase": nome_chave, "jogador_casa": j2, "jogador_fora": j1})
        
        if fase_nova == "Final":
            perdedores = []
            for nf in nomes_fases:
                _, p_loss = obter_resultado_mata_mata([p for p in jogos_atuais if p['fase'] == nf])
                perdedores.append(p_loss)
            nome_3l = "Disputa 3º Lugar"
            novas_partidas.append({"torneio_id": edicao['id'], "fase": nome_3l, "jogador_casa": perdedores[0], "jogador_fora": perdedores[1]})
            if ida_e_volta: novas_partidas.append({"torneio_id": edicao['id'], "fase": nome_3l, "jogador_casa": perdedores[1], "jogador_fora": perdedores[0]})
                
    supabase.table("tour_partidas").insert(novas_partidas).execute()
    st.cache_data.clear()

# ==============================================================================
# O CÉREBRO DO PANDAS (CLASSIFICAÇÃO E ESTATÍSTICAS GERAIS)
# ==============================================================================
@st.cache_data
def calcular_classificacao(edicao_id):
    participantes = supabase.table("tour_participantes").select("*").eq("torneio_id", edicao_id).execute().data
    if not participantes: return {}
    
    stats, grupos_dict = {}, {}
    for p in participantes:
        jog, grupo = p['jogador_nome'], p['grupo']
        grupos_dict[jog] = grupo
        stats[jog] = {'Jogador': jog, 'Pts': 0, 'J': 0, 'V': 0, 'E': 0, 'D': 0, 'GP': 0, 'GC': 0, 'SG': 0}
        
    partidas = get_partidas(edicao_id)
    for p in partidas:
        if p['gols_casa'] is not None and ('Grupo' in p['fase'] or p['fase'] == 'Fase Única'):
            j_c, j_f, g_c, g_f = p['jogador_casa'], p['jogador_fora'], p['gols_casa'], p['gols_fora']
            if j_c in stats: stats[j_c]['J'] += 1; stats[j_c]['GP'] += g_c; stats[j_c]['GC'] += g_f
            if j_f in stats: stats[j_f]['J'] += 1; stats[j_f]['GP'] += g_f; stats[j_f]['GC'] += g_c
            if g_c > g_f:
                if j_c in stats: stats[j_c]['Pts'] += 3; stats[j_c]['V'] += 1
                if j_f in stats: stats[j_f]['D'] += 1
            elif g_f > g_c:
                if j_f in stats: stats[j_f]['Pts'] += 3; stats[j_f]['V'] += 1
                if j_c in stats: stats[j_c]['D'] += 1
            else:
                if j_c in stats: stats[j_c]['Pts'] += 1; stats[j_c]['E'] += 1
                if j_f in stats: stats[j_f]['Pts'] += 1; stats[j_f]['E'] += 1
                    
    for jog, s in stats.items():
        s['SG'] = s['GP'] - s['GC']; s['%'] = round((s['Pts'] / (s['J'] * 3)) * 100, 1) if s['J'] > 0 else 0.0
        
    tabelas_finais = {}
    for jog, s in stats.items():
        g = grupos_dict[jog]
        tabelas_finais.setdefault(g, []).append(s)
        
    dfs = {}
    for g, lista in tabelas_finais.items():
        df = pd.DataFrame(lista)
        df = df.sort_values(by=['Pts', 'SG', 'GP'], ascending=[False, False, False]).reset_index(drop=True)
        df.insert(0, 'Pos', range(1, len(df) + 1))
        dfs[g] = df
    return dfs

@st.cache_data
def calcular_classificacao_geral_edicao(edicao_id):
    participantes = supabase.table("tour_participantes").select("*").eq("torneio_id", edicao_id).execute().data
    if not participantes: return pd.DataFrame()
    
    stats = {}
    for p in participantes:
        jog = p['jogador_nome']
        stats[jog] = {'Jogador': jog, 'Pts': 0, 'J': 0, 'V': 0, 'E': 0, 'D': 0, 'GP': 0, 'GC': 0, 'SG': 0}
        
    partidas = get_partidas(edicao_id)
    for p in partidas:
        if p['gols_casa'] is not None:
            j_c, j_f, g_c, g_f = p['jogador_casa'], p['jogador_fora'], p['gols_casa'], p['gols_fora']
            if j_c in stats:
                stats[j_c]['J'] += 1; stats[j_c]['GP'] += g_c; stats[j_c]['GC'] += g_f
            if j_f in stats:
                stats[j_f]['J'] += 1; stats[j_f]['GP'] += g_f; stats[j_f]['GC'] += g_c
                
            if g_c > g_f:
                if j_c in stats: stats[j_c]['Pts'] += 3; stats[j_c]['V'] += 1
                if j_f in stats: stats[j_f]['D'] += 1
            elif g_f > g_c:
                if j_f in stats: stats[j_f]['Pts'] += 3; stats[j_f]['V'] += 1
                if j_c in stats: stats[j_c]['D'] += 1
            else:
                if j_c in stats: stats[j_c]['Pts'] += 1; stats[j_c]['E'] += 1
                if j_f in stats: stats[j_f]['Pts'] += 1; stats[j_f]['E'] += 1
                    
    lista_stats = []
    for jog, s in stats.items():
        s['SG'] = s['GP'] - s['GC']
        s['%'] = round((s['Pts'] / (s['J'] * 3)) * 100, 1) if s['J'] > 0 else 0.0
        lista_stats.append(s)
        
    df = pd.DataFrame(lista_stats)
    if not df.empty:
        df = df.sort_values(by=['Pts', 'SG', 'GP', 'V'], ascending=[False, False, False, False]).reset_index(drop=True)
        df.insert(0, 'Pos', range(1, len(df) + 1))
    return df

@st.cache_data
def calcular_hall_da_fama():
    edicoes_finalizadas = supabase.table("tour_edicoes").select("*").eq("status", "Finalizado").order("id").execute().data
    campeoes_count, lista_campeoes_historico = {}, []

    for ed in edicoes_finalizadas:
        partidas = get_partidas(ed['id'])
        campeao = None
        if ed['formato'] == 'Pontos Corridos':
            tabelas = calcular_classificacao(ed['id'])
            if 'Único' in tabelas and not tabelas['Único'].empty: campeao = tabelas['Único'].iloc[0]['Jogador']
        else:
            finais = [p for p in partidas if 'Final' in p['fase'] and '3º' not in p['fase']]
            if finais: campeao, _ = obter_resultado_mata_mata(finais)

        if campeao:
            campeoes_count[campeao] = campeoes_count.get(campeao, 0) + 1
            dt_fim = formatar_data(ed.get('data_fim', ''))
            dt_ini = formatar_data(ed.get('data_inicio', ''))
            dt_exibicao = dt_fim if dt_fim != "N/A" else (dt_ini if dt_ini != "N/A" else 'Sem data')
            lista_campeoes_historico.append({'Edição': ed['nome'], 'Campeão': campeao, 'Data': dt_exibicao})

    todas_partidas = get_todas_partidas_concluidas()
    
    stats_geral, participacoes = {}, {}
    for p in todas_partidas:
        jc, jf, gc, gf, tid = p['jogador_casa'], p['jogador_fora'], p['gols_casa'], p['gols_fora'], p['torneio_id']
        if jc not in stats_geral: stats_geral[jc] = {'J':0, 'V':0, 'E':0, 'D':0, 'GP':0, 'GC':0}; participacoes[jc] = set() 
        if jf not in stats_geral: stats_geral[jf] = {'J':0, 'V':0, 'E':0, 'D':0, 'GP':0, 'GC':0}; participacoes[jf] = set()

        stats_geral[jc]['J'] += 1; stats_geral[jc]['GP'] += gc; stats_geral[jc]['GC'] += gf
        stats_geral[jf]['J'] += 1; stats_geral[jf]['GP'] += gf; stats_geral[jf]['GC'] += gc
        participacoes[jc].add(tid); participacoes[jf].add(tid)

        if gc > gf: stats_geral[jc]['V'] += 1; stats_geral[jf]['D'] += 1
        elif gf > gc: stats_geral[jf]['V'] += 1; stats_geral[jc]['D'] += 1
        else: stats_geral[jc]['E'] += 1; stats_geral[jf]['E'] += 1

    lista_stats = []
    for jog, s in stats_geral.items():
        s['Jogador'] = jog; s['🏆 Títulos'] = campeoes_count.get(jog, 0)
        s['🕹️ Edições'] = len(participacoes.get(jog, set())) 
        s['SG'] = s['GP'] - s['GC']; s['Pts'] = (s['V'] * 3) + s['E']
        s['%'] = round((s['Pts'] / (s['J'] * 3)) * 100, 1) if s['J'] > 0 else 0.0
        lista_stats.append(s)

    if not lista_stats: return pd.DataFrame(), []
    df = pd.DataFrame(lista_stats)
    df = df[['Jogador', '🏆 Títulos', '🕹️ Edições', 'J', 'V', 'E', 'D', 'GP', 'GC', 'SG', '%', 'Pts']]
    df = df.sort_values(by=['🏆 Títulos', 'Pts', 'SG', 'V'], ascending=[False, False, False, False]).reset_index(drop=True)
    df.insert(0, 'Pos', range(1, len(df) + 1))
    return df, lista_campeoes_historico

# ==============================================================================
# ROTEAMENTO DE ABAS E SEGURANÇA
# ==============================================================================
st.title("🏆 FIFA Tournaments - Central")

if st.session_state["autenticado"]:
    tabs = st.tabs(["📊 Torneio Atual", "📜 Histórico", "⚔️ Confronto Direto", "🏆 Hall da Fama", "📈 Estatísticas", "⚙️ Administração"])
    tab_atual, tab_hist, tab_h2h, tab_hall, tab_stats, tab_admin = tabs[0], tabs[1], tabs[2], tabs[3], tabs[4], tabs[5]
else:
    tabs = st.tabs(["📊 Torneio Atual", "📜 Histórico", "⚔️ Confronto Direto", "🏆 Hall da Fama", "📈 Estatísticas"])
    tab_atual, tab_hist, tab_h2h, tab_hall, tab_stats = tabs[0], tabs[1], tabs[2], tabs[3], tabs[4]
    tab_admin = None

# ==============================================================================
# ABA 1: TORNEIO ATUAL 
# ==============================================================================
with tab_atual:
    edicoes_andamento = get_edicoes_andamento() 
    if not edicoes_andamento:
        st.info("Nenhum torneio 'Em Andamento' no momento.")
    else:
        opcoes = {f"{ed['nome']}": ed for ed in edicoes_andamento}
        ed_selecionada_nome = st.selectbox("Selecione o Torneio Atual", list(opcoes.keys()))
        ed_atual = opcoes[ed_selecionada_nome]
        
        dt_ini = formatar_data(ed_atual.get('data_inicio', ''))
        if dt_ini != "N/A": st.caption(f"📅 **Início:** {dt_ini}")
        
        partidas_bd = get_partidas(ed_atual['id'])
        tabelas = calcular_classificacao(ed_atual['id'])
        
        if not partidas_bd:
            st.warning("Os grupos foram sorteados, mas a tabela de jogos ainda não foi gerada.")
            if st.session_state["autenticado"]:
                if st.button("🗓️ Gerar Confrontos Automaticamente", type="primary"):
                    gerar_confrontos_automaticos(ed_atual); st.toast("Tabela gerada!", icon="✅"); time.sleep(1); st.rerun()
        else:
            fases_mata_mata_bd = set([p['fase'] for p in partidas_bd if any(x in p['fase'] for x in ['Quartas', 'Semifinal', 'Final', '3º', 'Oitavas', '16-avos'])])
            jogos_para_desempate = []
            
            for nf in fases_mata_mata_bd:
                jogos_desta_chave = sorted([p for p in partidas_bd if p['fase'] == nf], key=lambda x: x['id'])
                if len(jogos_desta_chave) > 0 and all(p['gols_casa'] is not None for p in jogos_desta_chave):
                    v, _ = obter_resultado_mata_mata(jogos_desta_chave)
                    if v is None:
                        jogos_para_desempate.append(jogos_desta_chave[-1])
            
            pendentes = [p for p in partidas_bd if p['gols_casa'] is None or p in jogos_para_desempate]
            finalizadas = [p for p in partidas_bd if p['gols_casa'] is not None and p not in jogos_para_desempate]
            
            pendentes_grupos = [p for p in pendentes if 'Grupo' in p['fase'] or p['fase'] == 'Fase Única']
            pendentes_mata = [p for p in pendentes if p not in pendentes_grupos]
            
            st.markdown("---")
            c_jogos, c_classificacao = st.columns([1, 1.2])
            
            with c_jogos:
                st.subheader("🗓️ Partidas Pendentes")
                
                if st.session_state["autenticado"] and pendentes:
                    with st.expander("🎲 Draft de Times Fixo (Opcional)", expanded=False):
                        fase_alvo = st.selectbox("Fase para sortear", ["Fase de Grupos / Pontos Corridos", "16-avos", "Oitavas", "Quartas", "Semifinal", "Final / 3º Lugar"])
                        
                        jog_draft = set()
                        parts_draft = []
                        for p in pendentes:
                            if (fase_alvo == "Fase de Grupos / Pontos Corridos" and ('Grupo' in p['fase'] or p['fase'] == 'Fase Única')) or \
                               (fase_alvo == "16-avos" and '16-avos' in p['fase']) or \
                               (fase_alvo == "Oitavas" and 'Oitavas' in p['fase']) or \
                               (fase_alvo == "Quartas" and 'Quartas' in p['fase']) or \
                               (fase_alvo == "Semifinal" and 'Semifinal' in p['fase']) or \
                               (fase_alvo == "Final / 3º Lugar" and ('Final' in p['fase'] or '3º' in p['fase'])):
                                jog_draft.add(p['jogador_casa']); jog_draft.add(p['jogador_fora']); parts_draft.append(p)
                        
                        jog_draft = list(jog_draft)
                        if not jog_draft: st.info(f"Sem jogos pendentes para {fase_alvo}.")
                        else:
                            modo_draft = "Global"
                            if fase_alvo == "Fase de Grupos / Pontos Corridos" and ed_atual['formato'].startswith('Grupos') and ed_atual['qtd_grupos'] > 1:
                                tipo_sorteio = st.radio("Modo de Sorteio:", ["Sorteio Global (Times diferentes para todos)", "Sorteio Espelhado (Os mesmos times em cada grupo)"])
                                if "Espelhado" in tipo_sorteio: modo_draft = "Espelhado"

                            if modo_draft == "Global":
                                st.caption(f"**Jogadores:** {', '.join(jog_draft)}")
                                times_sel = st.multiselect(f"Selecione exatamente {len(jog_draft)} times únicos:", LISTA_TIMES, max_selections=len(jog_draft))
                                if len(times_sel) == len(jog_draft):
                                    if st.button("🎲 Distribuir Times Aleatoriamente", type="primary"):
                                        random.shuffle(times_sel)
                                        sorteio_map = dict(zip(jog_draft, times_sel))
                                        for p in parts_draft:
                                            tc = sorteio_map.get(p['jogador_casa'], p['time_casa'])
                                            tf = sorteio_map.get(p['jogador_fora'], p['time_fora'])
                                            supabase.table("tour_partidas").update({"time_casa": tc, "time_fora": tf}).eq("id", p['id']).execute()
                                            if f"tc_{p['id']}" in st.session_state: del st.session_state[f"tc_{p['id']}"]
                                            if f"tf_{p['id']}" in st.session_state: del st.session_state[f"tf_{p['id']}"]
                                        st.cache_data.clear()
                                        st.success("Draft Concluído! Atualizando..."); time.sleep(1.5); st.rerun()
                            else:
                                grupos_do_draft = {}
                                for p in parts_draft:
                                    fase_str = p['fase']
                                    if fase_str not in grupos_do_draft: grupos_do_draft[fase_str] = set()
                                    grupos_do_draft[fase_str].add(p['jogador_casa'])
                                    grupos_do_draft[fase_str].add(p['jogador_fora'])
                                
                                tamanho_max = max(len(jogadores) for jogadores in grupos_do_draft.values())
                                st.caption(f"Os grupos têm até {tamanho_max} jogadores. Os times selecionados serão embaralhados **dentro de cada grupo separadamente**.")
                                
                                times_sel = st.multiselect(f"Selecione {tamanho_max} times para espelhar:", LISTA_TIMES, max_selections=tamanho_max)
                                if len(times_sel) == tamanho_max:
                                    if st.button("🎲 Espelhar Times nos Grupos", type="primary"):
                                        sorteio_map = {}
                                        for grp, jogadores in grupos_do_draft.items():
                                            jogs_list = list(jogadores)
                                            times_embaralhados = times_sel.copy() 
                                            random.shuffle(times_embaralhados) 
                                            for i, jog in enumerate(jogs_list): sorteio_map[jog] = times_embaralhados[i]
                                                
                                        for p in parts_draft:
                                            tc = sorteio_map.get(p['jogador_casa'], p['time_casa'])
                                            tf = sorteio_map.get(p['jogador_fora'], p['time_fora'])
                                            supabase.table("tour_partidas").update({"time_casa": tc, "time_fora": tf}).eq("id", p['id']).execute()
                                            if f"tc_{p['id']}" in st.session_state: del st.session_state[f"tc_{p['id']}"]
                                            if f"tf_{p['id']}" in st.session_state: del st.session_state[f"tf_{p['id']}"]
                                        st.cache_data.clear()
                                        st.success("Draft Espelhado Concluído! Atualizando..."); time.sleep(1.5); st.rerun()

                    with st.expander("🧪 Simular Resultados (Teste)", expanded=False):
                        st.write("Cansado de digitar? Preencha todos os jogos pendentes da tela atual com placares aleatórios em 1 clique.")
                        if st.button("🎲 Preencher Placares Automaticamente", type="primary"):
                            for p in pendentes:
                                if p in jogos_para_desempate:
                                    foi_pen = True
                                    venc_pen = random.choice([p['jogador_casa'], p['jogador_fora']])
                                    salvar_placar(p['id'], p['time_casa'], p['gols_casa'], p['time_fora'], p['gols_fora'], foi_pen, venc_pen)
                                else:
                                    gc, gf = random.randint(0, 4), random.randint(0, 4)
                                    tc = random.choice(LISTA_TIMES) if not p.get('time_casa') else p['time_casa']
                                    tf = random.choice(LISTA_TIMES) if not p.get('time_fora') else p['time_fora']
                                    foi_pen, venc_pen = False, None
                                    is_mata_mata = any(x in p['fase'] for x in ['Quartas', 'Semifinal', 'Final', '3º', 'Oitavas', '16-avos'])
                                    if is_mata_mata and gc == gf:
                                        foi_pen = True
                                        venc_pen = random.choice([p['jogador_casa'], p['jogador_fora']])
                                    salvar_placar(p['id'], tc, gc, tf, gf, foi_pen, venc_pen)
                            st.success("Resultados gerados!"); time.sleep(1); st.rerun()

                if not pendentes_grupos and not pendentes_mata: st.success("Todas as partidas foram finalizadas!")
                for p in pendentes_grupos:
                    if st.session_state["autenticado"]: render_form_placar(p, False)
                    else: render_partida_somente_leitura(p)

            with c_classificacao:
                st.subheader("📊 Classificação")
                for grupo_nome, df_grupo in tabelas.items():
                    if grupo_nome != "Único": st.markdown(f"#### Grupo {grupo_nome}")
                    df_grupo = df_grupo.set_index('Pos')
                    st.table(estilizar_tabela(df_grupo))
                
            if ed_atual['formato'].startswith('Grupos'):
                regras = get_regras_edicao(ed_atual)
                total_class = ed_atual['qtd_grupos'] * regras['classificados']
                
                fases_ordem = []
                if total_class == 32: fases_ordem = ["16-avos", "Oitavas", "Quartas", "Semifinal", "Final"]
                elif total_class == 16: fases_ordem = ["Oitavas", "Quartas", "Semifinal", "Final"]
                elif total_class == 8: fases_ordem = ["Quartas", "Semifinal", "Final"]
                elif total_class == 4: fases_ordem = ["Semifinal", "Final"]
                elif total_class == 2: fases_ordem = ["Final"]

                fase_pendente_geracao = None
                for i, fase in enumerate(fases_ordem):
                    jogos_fase = [p for p in partidas_bd if fase in p['fase']]
                    if not jogos_fase:
                        if i == 0:
                            partidas_grupos = [p for p in partidas_bd if 'Grupo' in p['fase'] or p['fase'] == 'Fase Única']
                            if len(partidas_grupos) > 0 and all(p['gols_casa'] is not None for p in partidas_grupos):
                                fase_pendente_geracao = fase
                        else:
                            fase_ant = fases_ordem[i-1]
                            jogos_ant = [p for p in partidas_bd if fase_ant in p['fase'] and '3º' not in p['fase']]
                            if len(jogos_ant) > 0 and all(p['gols_casa'] is not None for p in jogos_ant):
                                nomes_fases_ant = set([p['fase'] for p in jogos_ant])
                                todos_resolvidos = True
                                for nf in nomes_fases_ant:
                                    v, _ = obter_resultado_mata_mata([p for p in jogos_ant if p['fase'] == nf])
                                    if v is None: todos_resolvidos = False
                                if todos_resolvidos:
                                    fase_pendente_geracao = fase
                        break
                    else:
                        finalizada = all(p['gols_casa'] is not None for p in jogos_fase)
                        if not finalizada: break 

                st.markdown("---")
                st.subheader("🔥 Fase Final (Mata-Mata)")
                if fase_pendente_geracao:
                    st.success("A fase anterior foi concluída!")
                    if st.session_state["autenticado"]:
                        btn_nome = "🏆 Gerar Final e Disputa de 3º" if fase_pendente_geracao == "Final" else f"⚔️ Gerar {fase_pendente_geracao}"
                        if st.button(btn_nome, type="primary"):
                            gerar_fase_mata_mata_dinamica(ed_atual, tabelas, partidas_bd, regras, fase_pendente_geracao)
                            st.rerun()
                elif any('Final' in p['fase'] for p in partidas_bd):
                    finais_jogos = [p for p in partidas_bd if 'Final' in p['fase'] and '3º' not in p['fase']]
                    if len(finais_jogos) > 0 and all(p['gols_casa'] is not None for p in finais_jogos):
                        campeao, vice = obter_resultado_mata_mata(finais_jogos)
                        if campeao:
                            st.success(f"🎉 O Torneio Acabou! {campeao} é o Campeão!")
                            if st.session_state["autenticado"]:
                                finalizar_edicao(ed_atual['id']); time.sleep(2.5); st.rerun()
                        else:
                            st.warning("⚠️ A Grande Final está empatada no agregado! Resolva o desempate nos pênaltis.")
                    else:
                        st.info("A Grande Final está rolando!")
                else:
                    st.info("Partidas em andamento...")

                if pendentes_mata:
                    c_m1, c_m2 = st.columns(2)
                    for i, p in enumerate(pendentes_mata):
                        precisa_desempate = p in jogos_para_desempate
                        if i % 2 == 0:
                            with c_m1: 
                                if st.session_state["autenticado"]: render_form_placar(p, precisa_desempate)
                                else: render_partida_somente_leitura(p)
                        else:
                            with c_m2: 
                                if st.session_state["autenticado"]: render_form_placar(p, precisa_desempate)
                                else: render_partida_somente_leitura(p)

            elif ed_atual['formato'] == 'Pontos Corridos':
                if not pendentes and finalizadas:
                    campeao = tabelas['Único'].iloc[0]['Jogador']
                    st.success(f"🎉 **{campeao}** é o GRANDE CAMPEÃO da {ed_atual['nome']}!")
                    if st.session_state["autenticado"]:
                        finalizar_edicao(ed_atual['id']); time.sleep(2.5); st.rerun()
            
            st.markdown("---")
            if finalizadas:
                st.subheader("📜 Resultados Recentes")
                with st.container(height=350):
                    for p in reversed(finalizadas):
                        pen_txt = f" *(Pên: {p['vencedor_penaltis']})*" if p['foi_penaltis'] else ""
                        logo_c = TEAMS.get(p['time_casa'], '')
                        logo_f = TEAMS.get(p['time_fora'], '')
                        st.markdown(f"""
                        <div style="background-color: #1E1E1E; padding: 10px; border-radius: 5px; margin-bottom: 5px; border: 1px solid #333; text-align: center;">
                            <span style="font-size: 12px; color: gray;">{p['fase']}</span><br>
                            <div style="display: flex; align-items: center; justify-content: center; gap: 15px; margin-top: 5px;">
                                <b style="font-size: 16px;">{p['jogador_casa']}</b>
                                <img src="{logo_c}" width="28" title="{p['time_casa']}">
                                <b style="font-size: 18px;">{p['gols_casa']} x {p['gols_fora']}</b>
                                <img src="{logo_f}" width="28" title="{p['time_fora']}">
                                <b style="font-size: 16px;">{p['jogador_fora']}</b>
                            </div>
                            <div style="font-size: 12px; color: #ff4b4b; margin-top: 2px;">{pen_txt}</div>
                        </div>
                        """, unsafe_allow_html=True)

# ==============================================================================
# ABA 2: HISTÓRICO DE TORNEIOS
# ==============================================================================
with tab_hist:
    edicoes_finalizadas = get_edicoes_finalizadas()
    
    if not edicoes_finalizadas:
        st.info("Nenhum torneio foi finalizado ainda. Os dados aparecerão aqui quando o campeão for definido.")
    else:
        opcoes_hist = {f"{ed['nome']}": ed for ed in edicoes_finalizadas}
        ed_hist_nome = st.selectbox("Selecione um Torneio Passado", list(opcoes_hist.keys()))
        ed_hist = opcoes_hist[ed_hist_nome]
        
        dt_ini = formatar_data(ed_hist.get('data_inicio', ''))
        dt_fim = formatar_data(ed_hist.get('data_fim', ''))
        if dt_ini != "N/A" or dt_fim != "N/A":
            st.caption(f"📅 **Início:** {dt_ini} &nbsp;|&nbsp; 🏁 **Finalização:** {dt_fim}")
        
        partidas_hist = get_partidas(ed_hist['id'])
        tabelas_hist = calcular_classificacao(ed_hist['id'])
        
        st.markdown("---")
        
        if ed_hist['formato'].startswith('Grupos'):
            finais_jogos = [p for p in partidas_hist if 'Final' in p['fase'] and '3º' not in p['fase']]
            terceiro_jogos = [p for p in partidas_hist if 'Disputa 3º Lugar' in p['fase']]
            
            campeao, vice = obter_resultado_mata_mata(finais_jogos)
            terceiro, _ = obter_resultado_mata_mata(terceiro_jogos) if terceiro_jogos else ("N/A", "N/A")
            ultimos_dos_grupos = [f"{tabelas_hist[g].iloc[-1]['Jogador']} (Grupo {g})" for g in tabelas_hist if g != 'Único']
            
            st.error(f"🏆 **Campeão: {campeao}**") 
            st.warning(f"🥈 **Vice-campeão:** {vice}")
            if terceiro != "N/A": st.info(f"🥉 **3º Colocado:** {terceiro}")
            st.markdown(f"🔦 **Lanternas dos Grupos:** {', '.join(ultimos_dos_grupos)}")
            
        elif ed_hist['formato'] == 'Pontos Corridos':
            campeao = tabelas_hist['Único'].iloc[0]['Jogador']
            vice = tabelas_hist['Único'].iloc[1]['Jogador'] if len(tabelas_hist['Único']) > 1 else "N/A"
            lanterna = tabelas_hist['Único'].iloc[-1]['Jogador']
            
            st.error(f"🏆 **Campeão: {campeao}**") 
            st.warning(f"🥈 **Vice-campeão:** {vice}")
            st.markdown(f"🔦 **Lanterna da Edição:** {lanterna}")

        st.markdown("---")
        c_tabelas_hist, c_jogos_hist = st.columns([1.2, 1])
        
        with c_tabelas_hist:
            st.subheader("📊 Classificação Final")
            for grupo_nome, df_grupo in tabelas_hist.items():
                if grupo_nome != "Único": st.markdown(f"#### Grupo {grupo_nome}")
                df_grupo = df_grupo.set_index('Pos')
                st.table(estilizar_tabela(df_grupo))
            
            if ed_hist['formato'].startswith('Grupos'):
                st.markdown("---")
                st.markdown("#### 🌍 Classificação Geral (Campanha Completa)")
                df_geral = calcular_classificacao_geral_edicao(ed_hist['id'])
                if not df_geral.empty:
                    df_geral = df_geral.set_index('Pos')
                    st.table(estilizar_tabela(df_geral))
                
        with c_jogos_hist:
            st.subheader("📜 Todos os Resultados")
            with st.container(height=400):
                for p in reversed(partidas_hist):
                    if p['gols_casa'] is not None: 
                        pen_txt = f" *(Pên: {p['vencedor_penaltis']})*" if p['foi_penaltis'] else ""
                        logo_c = TEAMS.get(p['time_casa'], '')
                        logo_f = TEAMS.get(p['time_fora'], '')
                        st.markdown(f"""
                        <div style="background-color: #1E1E1E; padding: 10px; border-radius: 5px; margin-bottom: 5px; border: 1px solid #333; text-align: center;">
                            <span style="font-size: 12px; color: gray;">{p['fase']}</span><br>
                            <div style="display: flex; align-items: center; justify-content: center; gap: 15px; margin-top: 5px;">
                                <b style="font-size: 16px;">{p['jogador_casa']}</b>
                                <img src="{logo_c}" width="28" title="{p['time_casa']}">
                                <b style="font-size: 18px;">{p['gols_casa']} x {p['gols_fora']}</b>
                                <img src="{logo_f}" width="28" title="{p['time_fora']}">
                                <b style="font-size: 16px;">{p['jogador_fora']}</b>
                            </div>
                            <div style="font-size: 12px; color: #ff4b4b; margin-top: 2px;">{pen_txt}</div>
                        </div>
                        """, unsafe_allow_html=True)

# ==============================================================================
# ABA 3: CONFRONTO DIRETO (HEAD-TO-HEAD)
# ==============================================================================
with tab_h2h:
    st.header("⚔️ Confronto Direto (Head-to-Head)")
    st.write("Selecione dois jogadores para ver o raio-x e histórico completo do duelo entre eles.")
    
    jogs_h2h = get_jogadores()
    if len(jogs_h2h) >= 2:
        col1_h2h, col2_h2h = st.columns(2)
        with col1_h2h: j1 = st.selectbox("1º Jogador", jogs_h2h)
        with col2_h2h: j2 = st.selectbox("2º Jogador", [j for j in jogs_h2h if j != j1])
        
        todas_partidas = get_todas_partidas_concluidas()
        
        partidas_duelo = []
        vit_j1, vit_j2, empates, gols_j1, gols_j2 = 0, 0, 0, 0, 0
        maior_goleada = None
        maior_diferenca = -1
        mapa_edicoes = {e['id']: e['nome'] for e in get_todas_edicoes()}
        
        for p in todas_partidas:
            is_j1_casa = (p['jogador_casa'] == j1 and p['jogador_fora'] == j2)
            is_j2_casa = (p['jogador_casa'] == j2 and p['jogador_fora'] == j1)
            
            if is_j1_casa or is_j2_casa:
                partidas_duelo.append(p)
                g1 = p['gols_casa'] if is_j1_casa else p['gols_fora']
                g2 = p['gols_fora'] if is_j1_casa else p['gols_casa']
                
                gols_j1 += g1
                gols_j2 += g2
                if g1 > g2: vit_j1 += 1
                elif g2 > g1: vit_j2 += 1
                else: empates += 1
                
                dif = abs(g1 - g2)
                if dif > maior_diferenca:
                    maior_diferenca = dif
                    maior_goleada = p

        st.markdown("---")
        if not partidas_duelo:
            st.info("Estes jogadores ainda não se enfrentaram oficialmente.")
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric(f"Jogos Totais", len(partidas_duelo))
            c2.metric(f"Vitórias - {j1}", vit_j1)
            c3.metric(f"Empates", empates)
            c4.metric(f"Vitórias - {j2}", vit_j2)
            
            st.markdown("<br>", unsafe_allow_html=True)
            c_g1, c_g2, c_g3 = st.columns(3)
            c_g1.metric(f"⚽ Gols - {j1}", gols_j1)
            c_g2.metric(f"⚽ Gols - {j2}", gols_j2)
            
            if maior_goleada:
                with c_g3:
                    p = maior_goleada
                    logo_c = TEAMS.get(p['time_casa'], '')
                    logo_f = TEAMS.get(p['time_fora'], '')
                    nome_torneio = mapa_edicoes.get(p['torneio_id'], "Torneio")
                    st.markdown(f"""
                    <div style="background-color: #1E1E1E; border-radius: 8px; padding: 15px; border: 1px solid #333333;">
                        <div style="font-size: 14px; color: #A0A0A0; margin-bottom: 8px; text-align: left; width: 100%;">Maior Goleada</div>
                        <div style="text-align: center; line-height: 1.2;">
                            <span style="font-size: 11px; color: #4DE17C;">{nome_torneio}</span> <span style="font-size: 11px; color: gray;">| {p['fase']}</span><br>
                            <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 5px;">
                                <b style="font-size: 14px;">{p['jogador_casa']}</b>
                                <img src="{logo_c}" width="22" title="{p['time_casa']}">
                                <b style="font-size: 16px;">{p['gols_casa']} x {p['gols_fora']}</b>
                                <img src="{logo_f}" width="22" title="{p['time_fora']}">
                                <b style="font-size: 14px;">{p['jogador_fora']}</b>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.subheader("Lista de Confrontos")
            with st.container(height=350):
                for p in reversed(partidas_duelo):
                    pen_txt = f" *(Pên: {p['vencedor_penaltis']})*" if p['foi_penaltis'] else ""
                    logo_c = TEAMS.get(p['time_casa'], '')
                    logo_f = TEAMS.get(p['time_fora'], '')
                    nome_torneio = mapa_edicoes.get(p['torneio_id'], "Torneio")
                    
                    st.markdown(f"""
                    <div style="background-color: #1E1E1E; padding: 10px; border-radius: 5px; margin-bottom: 5px; border: 1px solid #333; text-align: center;">
                        <span style="font-size: 12px; color: #4DE17C;">{nome_torneio}</span> <span style="font-size: 12px; color: gray;">| {p['fase']}</span><br>
                        <div style="display: flex; align-items: center; justify-content: center; gap: 15px; margin-top: 5px;">
                            <b style="font-size: 16px;">{p['jogador_casa']}</b>
                            <img src="{logo_c}" width="28">
                            <b style="font-size: 18px;">{p['gols_casa']} x {p['gols_fora']}</b>
                            <img src="{logo_f}" width="28">
                            <b style="font-size: 16px;">{p['jogador_fora']}</b>
                        </div>
                        <div style="font-size: 12px; color: #ff4b4b; margin-top: 2px;">{pen_txt}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.warning("Cadastre pelo menos 2 jogadores para acessar o confronto direto.")

# ==============================================================================
# ABA 4: O HALL DA FAMA
# ==============================================================================
with tab_hall:
    st.header("🏆 Hall da Fama - Ranking Histórico")
        
    df_hall, lista_campeoes = calcular_hall_da_fama()
    
    if df_hall.empty:
        st.info("Nenhuma partida registrada ou torneio finalizado ainda.")
    else:
        df_hall = df_hall.set_index('Pos')
        st.table(estilizar_tabela(df_hall))
        
        st.markdown("---")
        st.subheader("🏅 Galeria de Campeões (Histórico de Edições)")
        if lista_campeoes:
            for item in lista_campeoes:
                st.markdown(f"• {item['Data']} - {item['Edição']}: 🏆 **{item['Campeão']}**")
        else:
            st.caption("Nenhum campeonato foi finalizado até o momento.")

# ==============================================================================
# ABA 5: ESTATÍSTICAS GLOBAIS
# ==============================================================================
with tab_stats:
    st.header("📈 Estatísticas Globais do Sistema")
    st.write("Raio-x completo de todas as partidas já finalizadas no sistema.")
    st.markdown("---")
    
    todas_partidas = get_todas_partidas_concluidas()
    
    if not todas_partidas:
        st.info("Nenhum dado estatístico disponível. Conclua alguns jogos primeiro!")
    else:
        total_jogos = len(todas_partidas)
        total_gols = sum(p['gols_casa'] + p['gols_fora'] for p in todas_partidas)
        media_gols = round(total_gols / total_jogos, 2) if total_jogos > 0 else 0
        
        times_uso = {}
        times_gols = {}
        penaltis_vencidos = {}
        maior_goleada_abs = None
        maior_dif_abs = -1
        
        for p in todas_partidas:
            tc = p['time_casa']
            tf = p['time_fora']
            gc = p['gols_casa']
            gf = p['gols_fora']
            
            if tc: times_uso[tc] = times_uso.get(tc, 0) + 1
            if tf: times_uso[tf] = times_uso.get(tf, 0) + 1
            
            if tc: times_gols[tc] = times_gols.get(tc, 0) + gc
            if tf: times_gols[tf] = times_gols.get(tf, 0) + gf
            
            if p.get('foi_penaltis') and p.get('vencedor_penaltis'):
                v_p = p['vencedor_penaltis']
                penaltis_vencidos[v_p] = penaltis_vencidos.get(v_p, 0) + 1
            
            dif = abs(gc - gf)
            if dif > maior_dif_abs:
                maior_dif_abs = dif
                maior_goleada_abs = p
                
        time_mais_gols = max(times_gols, key=times_gols.get) if times_gols else "N/A"
        
        df_hall, _ = calcular_hall_da_fama()
        jogador_artilheiro = "N/A"
        gols_artilheiro = 0
        jogador_defesa = "N/A"
        jogador_saco_pancadas = "N/A"
        gols_saco_pancadas = 0
        
        if not df_hall.empty:
            idx_art = df_hall['GP'].idxmax()
            jogador_artilheiro = df_hall.loc[idx_art]['Jogador']
            gols_artilheiro = df_hall.loc[idx_art]['GP']
            
            idx_saco = df_hall['GC'].idxmax()
            jogador_saco_pancadas = df_hall.loc[idx_saco]['Jogador']
            gols_saco_pancadas = df_hall.loc[idx_saco]['GC']
            
            df_defesa = df_hall[df_hall['J'] >= 5].copy()
            if not df_defesa.empty:
                df_defesa['Media_GC'] = df_defesa['GC'] / df_defesa['J']
                jogador_defesa = df_defesa.loc[df_defesa['Media_GC'].idxmin()]['Jogador']
            else:
                jogador_defesa = df_hall.loc[df_hall['GC'].idxmin()]['Jogador']
                
        if penaltis_vencidos:
            rei_penaltis = max(penaltis_vencidos, key=penaltis_vencidos.get)
            qtd_penaltis = penaltis_vencidos[rei_penaltis]
        else:
            rei_penaltis = "Nenhum"
            qtd_penaltis = 0

        st.subheader("📌 Resumo Geral")
        cs1, cs2, cs3 = st.columns(3)
        cs1.metric("Total de Partidas", total_jogos)
        cs2.metric("Gols Marcados", total_gols)
        cs3.metric("Média de Gols/Jogo", media_gols)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🏅 Destaques dos Jogadores")
        cj1, cj2 = st.columns(2)
        with cj1:
            st.info(f"🎯 **Máquina de Gols:** {jogador_artilheiro} ({gols_artilheiro} gols feitos)")
            st.error(f"🥊 **Saco de Pancadas:** {jogador_saco_pancadas} ({gols_saco_pancadas} gols sofridos)")
        with cj2:
            st.success(f"🧱 **Paredão:** {jogador_defesa} (Melhor média defensiva)")
            st.warning(f"🧤 **Rei dos Pênaltis:** {rei_penaltis} ({qtd_penaltis} disputas vencidas)")

        st.markdown("<br>", unsafe_allow_html=True)
        
        col_t1, col_t2 = st.columns([1.2, 1])
        
        with col_t1:
            st.markdown("#### 🔝 Top 5 Times Mais Escolhidos")
            top_5_times = sorted(times_uso.items(), key=lambda x: x[1], reverse=True)[:5]
            
            if top_5_times:
                for pos, (t_nome, t_qtd) in enumerate(top_5_times, 1):
                    logo_t = TEAMS.get(t_nome, '')
                    st.markdown(f"""
                    <div style="background-color: #1E1E1E; padding: 9px 15px; border-radius: 6px; margin-bottom: 7px; border: 1px solid #333; display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <span style="font-size: 14px; font-weight: bold; color: #4DE17C; width: 20px;">#{pos}</span>
                            <img src="{logo_t}" width="26">
                            <b style="font-size: 15px;">{t_nome}</b>
                        </div>
                        <span style="color: #A0A0A0; font-size: 13px;">{t_qtd} jogos</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("Sem dados de times no momento.")
                
        with col_t2:
            st.markdown("#### 🏆 Recordes Absolutos")
            logo_artilheiro = TEAMS.get(time_mais_gols, '')
            st.markdown(f"""
            <div style="background-color: #1E1E1E; border-radius: 8px; padding: 15px; border: 1px solid #333333; text-align: center; margin-bottom: 10px; height: 118px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 13px; color: #A0A0A0; margin-bottom: 6px; font-weight: bold; letter-spacing: 0.5px; text-align: left; width: 100%;">🔥 ATAQUE MAIS MORTAL</div>
                <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
                    <img src="{logo_artilheiro}" width="32">
                    <div style="text-align: left;">
                        <b style="font-size: 16px; display: block;">{time_mais_gols}</b>
                        <span style="color: #4DE17C; font-weight: bold; font-size: 13px;">{times_gols.get(time_mais_gols, 0)} gols marcados</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if maior_goleada_abs:
                p = maior_goleada_abs
                logo_c = TEAMS.get(p['time_casa'], '')
                logo_f = TEAMS.get(p['time_fora'], '')
                mapa_edicoes = {e['id']: e['nome'] for e in get_todas_edicoes()}
                nome_torneio = mapa_edicoes.get(p['torneio_id'], "Torneio")
                
                st.markdown(f"""
                <div style="background-color: #1E1E1E; border-radius: 8px; padding: 15px; border: 1px solid #333333; text-align: center; height: 118px; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-size: 13px; color: #A0A0A0; margin-bottom: 4px; font-weight: bold; letter-spacing: 0.5px; text-align: left; width: 100%;">⚡ A MAIOR GOLEADA DA HISTÓRIA</div>
                    <div style="margin-bottom: 6px;">
                        <span style="font-size: 11px; color: #4DE17C;">{nome_torneio}</span> <span style="font-size: 11px; color: gray;">| {p['fase']}</span>
                    </div>
                    <div style="display: flex; align-items: center; justify-content: center; gap: 12px;">
                        <b style="font-size: 15px;">{p['jogador_casa']}</b>
                        <img src="{logo_c}" width="22" title="{p['time_casa']}">
                        <b style="font-size: 18px;">{p['gols_casa']} x {p['gols_fora']}</b>
                        <img src="{logo_f}" width="22" title="{p['time_fora']}">
                        <b style="font-size: 15px;">{p['jogador_fora']}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ==============================================================================
# ABA 6: ADMINISTRAÇÃO 
# ==============================================================================
if tab_admin:
    with tab_admin:
        st.header("⚙️ Painel do Diretor")
        col_top1, col_top2 = st.columns(2)
        
        with col_top1:
            with st.container(border=True):
                st.subheader("1️⃣ Cadastrar Novo Jogador")
                jogadores_atuais = get_jogadores()
                if jogadores_atuais: st.caption(f"Já cadastrados: {', '.join(jogadores_atuais)}")
                    
                with st.form("form_add_jogador", clear_on_submit=True):
                    novo_nome = st.text_input("Nome do Jogador")
                    if st.form_submit_button("Salvar Jogador", use_container_width=True):
                        if novo_nome and novo_nome not in jogadores_atuais:
                            add_jogador(novo_nome)
                            st.toast(f"{novo_nome} adicionado!", icon="✅")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning("Nome inválido ou já existe.")

        with col_top2:
            with st.container(border=True):
                st.subheader("2️⃣ Criar Nova Edição")
                
                nome_edicao = st.text_input("Nome (Ex: Copa Inverno 2026)")
                formato = st.selectbox("Formato", ["Grupos", "Pontos Corridos"])
                
                if formato == "Grupos":
                    c_g1, c_g2 = st.columns(2)
                    with c_g1: qtd_grupos = st.number_input("Qtd Grupos", min_value=1, max_value=8, value=1)
                    with c_g2: classificados = st.number_input("Classificam por grupo", min_value=1, max_value=8, value=2)
                    
                    total = qtd_grupos * classificados
                    st.info(f"Total de classificados para o Mata-Mata: **{total} jogadores**")
                    
                    if total not in [2, 4, 8, 16, 32]:
                        st.error("⚠️ Para garantir chaveamento perfeito sem 'folgas', classifique 2, 4, 8, 16 ou 32 jogadores.")
                        pode_criar = False
                    else:
                        pode_criar = True
                        st.markdown("**Regras de Ida e Volta:**")
                        c_ida1, c_ida2, c_ida3 = st.columns(3)
                        with c_ida1:
                            ida_volta_grp = st.checkbox("Fase de Grupos", value=True)
                            ida_volta_semi = st.checkbox("Semifinais", value=True) if total >= 4 else False
                        with c_ida2:
                            ida_volta_16avos = st.checkbox("16-avos de Final", value=True) if total == 32 else False
                            ida_volta_oitavas = st.checkbox("Oitavas de Final", value=True) if total >= 16 else False
                        with c_ida3:
                            ida_volta_quartas = st.checkbox("Quartas de Final", value=True) if total >= 8 else False
                            ida_volta_final = st.checkbox("Final e 3º Lugar", value=False)
                            
                        fmt_db = f"Grupos|{classificados}|{int(ida_volta_oitavas)}|{int(ida_volta_quartas)}|{int(ida_volta_16avos)}"
                else:
                    pode_criar = True
                    qtd_grupos = 1
                    classificados = 1
                    ida_volta_grp = st.checkbox("Ida/Volta (Todos contra Todos)", value=True)
                    ida_volta_quartas, ida_volta_semi, ida_volta_final, ida_volta_oitavas, ida_volta_16avos = False, False, False, False, False
                    fmt_db = "Pontos Corridos"
                
                if st.button("Criar Campeonato", type="primary", use_container_width=True, disabled=not pode_criar):
                    if nome_edicao:
                        criar_edicao(nome_edicao, fmt_db, int(qtd_grupos), ida_volta_grp, ida_volta_semi, ida_volta_final)
                        st.toast("Edição Criada!", icon="🏆")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning("Dê um nome para a edição antes de criar!")

        st.markdown("---")
        col_bot1, col_bot2 = st.columns(2)

        with col_bot1:
            st.subheader("3️⃣ Sorteio Oficial")
            edicoes_abertas = get_edicoes_abertas()
            
            if not edicoes_abertas:
                st.info("Nenhuma edição 'Aberta'.")
            else:
                opcoes_edicoes = {ed['nome']: ed for ed in edicoes_abertas}
                nome_edicao_sel = st.selectbox("Selecione para Sorteio", list(opcoes_edicoes.keys()))
                edicao_selecionada = opcoes_edicoes[nome_edicao_sel]
                participantes_selecionados = st.multiselect("Participantes:", jogadores_atuais, placeholder="Escolha a galera...")
                
                if participantes_selecionados:
                    if edicao_selecionada['formato'].startswith('Grupos'):
                        modo_sorteio = st.radio("Método de Definição:", ["Sorteio Automático 🎲", "Definição Manual ✍️"], horizontal=True)
                        
                        if modo_sorteio == "Sorteio Automático 🎲":
                            if st.button("🎲 Sortear Grupos Automaticamente", type="primary", use_container_width=True):
                                random.shuffle(participantes_selecionados)
                                num_grupos = edicao_selecionada['qtd_grupos']
                                letras_grupos = [chr(i) for i in range(65, 65 + num_grupos)]
                                grupos = {letra: [] for letra in letras_Não fui programado para fazer essas coisas.
