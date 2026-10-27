import streamlit as st

SERIES_PALETTE = ["#12A150", "#F2711C", "#7C4DFF", "#0EA5B7", "#B4538F", "#8A6D3B", "#2F6FED"]
TOTAL_COLOR = "#12326B"
SPIKE_COLOR = "#E5484D"
DROP_COLOR = "#F5A524"

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');
:root {
    --bi-bg: #F2F5F9;
    --bi-surface: #FFFFFF;
    --bi-border: #DDE3EC;
    --bi-border-strong: #C5CFDD;
    --bi-ink: #0F1E36;
    --bi-muted: #5B6B82;
    --bi-primary: #12326B;
    --bi-primary-hover: #0D2757;
    --bi-accent: #2F6FED;
    --bi-accent-soft: #EAF1FF;
    --bi-ok: #12A150;
}
.stApp, .stApp button, .stApp input, .stApp textarea, .stApp select {
    font-family: 'IBM Plex Sans', -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
}
.stApp { background: var(--bi-bg); color: var(--bi-ink); }
[data-testid="stHeader"] { background: transparent; }
footer { visibility: hidden; }
.block-container { max-width: 1520px; padding: 1.5rem 2.25rem 3.5rem; }
[data-testid="stVerticalBlock"] { gap: 1rem; }

.bi-header { display: flex; align-items: center; gap: 16px; padding: 4px 0 2px; }
.bi-logo {
    width: 52px; height: 52px; border-radius: 12px; background: var(--bi-primary);
    display: flex; align-items: center; justify-content: center; color: #FFFFFF; flex: 0 0 auto;
}
.bi-title { margin: 0; font-size: 1.65rem; font-weight: 700; line-height: 1.2; color: var(--bi-ink); }
.bi-subtitle { margin: 2px 0 0; font-size: 0.92rem; color: var(--bi-muted); }

.bi-pill {
    display: inline-flex; align-items: center; gap: 8px; padding: 7px 14px; border-radius: 999px;
    background: var(--bi-surface); border: 1px solid var(--bi-border); color: var(--bi-muted);
    font-size: 0.84rem; font-weight: 500;
}
.bi-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--bi-ok); }

.bi-kpis { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
@media (max-width: 1000px) { .bi-kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px) { .bi-kpis { grid-template-columns: minmax(0, 1fr); } }
.bi-kpi {
    display: flex; align-items: center; gap: 16px; padding: 18px 22px; background: var(--bi-surface);
    border: 1px solid var(--bi-border); border-radius: 12px; box-shadow: 0 1px 2px rgba(15, 30, 54, 0.04);
}
.bi-kpi-icon {
    width: 48px; height: 48px; border-radius: 10px; background: var(--bi-accent-soft); color: var(--bi-accent);
    display: flex; align-items: center; justify-content: center; flex: 0 0 auto;
}
.bi-kpi-label { font-size: 0.82rem; font-weight: 600; color: var(--bi-muted); }
.bi-kpi-value {
    font-size: 1.7rem; font-weight: 700; line-height: 1.15; color: var(--bi-ink);
    font-variant-numeric: tabular-nums; white-space: nowrap;
}

.bi-section { margin: 0 0 0.6rem; }
.bi-section-title { font-size: 1.12rem; font-weight: 700; color: var(--bi-ink); line-height: 1.3; }
.bi-section-sub { font-size: 0.86rem; color: var(--bi-muted); margin-top: 2px; }

[class*="st-key-card-"] {
    background: var(--bi-surface); border: 1px solid var(--bi-border); border-radius: 12px;
    padding: 20px 24px; box-shadow: 0 1px 2px rgba(15, 30, 54, 0.04);
}
[data-testid="stPlotlyChart"] {
    background: var(--bi-surface); border: 1px solid var(--bi-border); border-radius: 12px;
    padding: 14px 16px 8px; box-shadow: 0 1px 2px rgba(15, 30, 54, 0.04);
}
[data-testid="stTabs"] {
    background: var(--bi-surface); border: 1px solid var(--bi-border); border-radius: 12px;
    padding: 6px 24px 24px; box-shadow: 0 1px 2px rgba(15, 30, 54, 0.04);
}
[data-testid="stTabs"] [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid var(--bi-border); }
[data-testid="stTabs"] button[role="tab"] { padding: 12px 16px; color: var(--bi-muted); }
[data-testid="stTabs"] button[role="tab"] p { font-weight: 600; font-size: 0.95rem; }
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] { color: var(--bi-primary); }
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color: var(--bi-accent); height: 3px; }
[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none; }

.stApp button[data-testid^="stBaseButton"], .stApp [data-testid="stDownloadButton"] button {
    border-radius: 8px; font-weight: 600; min-height: 2.6rem; transition: background 0.12s, border-color 0.12s;
}
.stApp [data-testid="stBaseButton-secondary"] {
    background: var(--bi-surface); color: var(--bi-ink); border: 1px solid var(--bi-border-strong);
}
.stApp [data-testid="stBaseButton-secondary"]:hover {
    border-color: var(--bi-accent); color: var(--bi-accent); background: var(--bi-accent-soft);
}
.stApp [data-testid="stBaseButton-primary"] {
    background: var(--bi-primary); color: #FFFFFF; border: 1px solid var(--bi-primary);
}
.stApp [data-testid="stBaseButton-primary"]:hover {
    background: var(--bi-primary-hover); border-color: var(--bi-primary-hover); color: #FFFFFF;
}
.stApp [data-testid="stBaseButton-primary"] p, .stApp [data-testid="stBaseButton-primary"] span { color: #FFFFFF; }
.stApp button:focus-visible { outline: 2px solid var(--bi-accent); outline-offset: 2px; }

[data-testid="stWidgetLabel"] p { font-size: 0.84rem; font-weight: 600; color: var(--bi-muted); }
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, div[data-baseweb="base-input"] {
    background: var(--bi-surface); border-color: var(--bi-border-strong); border-radius: 8px;
}
[data-baseweb="tag"] { background: var(--bi-accent-soft); border-radius: 6px; }
[data-baseweb="tag"] span { color: var(--bi-primary); font-weight: 500; }
[data-testid="stNumberInput"] button { border-radius: 6px; }

[data-testid="stMetric"] {
    background: #F7F9FC; border: 1px solid var(--bi-border); border-radius: 10px; padding: 12px 16px;
}
[data-testid="stMetricLabel"] p { font-size: 0.82rem; font-weight: 600; color: var(--bi-muted); }
[data-testid="stMetricValue"] { font-weight: 700; font-variant-numeric: tabular-nums; color: var(--bi-ink); }

[data-testid="stDataFrame"] { border: 1px solid var(--bi-border); border-radius: 10px; overflow: hidden; }
[data-testid="stExpander"] {
    background: var(--bi-surface); border: 1px solid var(--bi-border); border-radius: 12px;
    box-shadow: 0 1px 2px rgba(15, 30, 54, 0.04);
}
[data-testid="stExpander"] summary { padding: 14px 20px; font-weight: 600; }
[data-testid="stAlert"] { border-radius: 10px; }
[data-testid="stCaptionContainer"] { color: var(--bi-muted); }
hr { border-color: var(--bi-border); }
</style>
"""

ICON_LOGO = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 20l6.5-11 4 6.5 2.5-4L21 20z"/><path d="M3 20h18"/></svg>'
ICON_RECORDS = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M10 13h6M10 17h6"/></svg>'
ICON_MINES = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 20l6.5-11 4 6.5 2.5-4L21 20z"/></svg>'
ICON_START = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/></svg>'
ICON_END = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4M9.5 15l2 2 3.5-3.5"/></svg>'


def inject_theme() -> None:
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="bi-header"><div class="bi-logo">{ICON_LOGO}</div>'
        f'<div><h1 class="bi-title">{title}</h1><p class="bi-subtitle">{subtitle}</p></div></div>',
        unsafe_allow_html=True,
    )


def render_source_pill(text: str) -> None:
    st.markdown(f'<span class="bi-pill"><span class="bi-dot"></span>{text}</span>', unsafe_allow_html=True)


def render_kpi_cards(items: list) -> None:
    cards = "".join(
        f'<div class="bi-kpi"><div class="bi-kpi-icon">{icon}</div>'
        f'<div><div class="bi-kpi-label">{label}</div><div class="bi-kpi-value">{value}</div></div></div>'
        for icon, label, value in items
    )
    st.markdown(f'<div class="bi-kpis">{cards}</div>', unsafe_allow_html=True)


def section_header(title: str, subtitle: str = "") -> None:
    subtitle_html = f'<div class="bi-section-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div class="bi-section"><div class="bi-section-title">{title}</div>{subtitle_html}</div>',
        unsafe_allow_html=True,
    )


def card(name: str):
    return st.container(key=f"card-{name}")


def series_color(name: str, options: list) -> str:
    if name == "In total":
        return TOTAL_COLOR
    mines = [option for option in options if option != "In total"]
    return SERIES_PALETTE[mines.index(name) % len(SERIES_PALETTE)]


def apply_chart_theme(fig) -> None:
    fig.update_layout(
        font={"family": "IBM Plex Sans, -apple-system, Segoe UI, Roboto, sans-serif", "size": 12, "color": "#0F1E36"},
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        margin={"l": 8, "r": 8, "t": 56, "b": 8},
        title={"font": {"size": 14, "color": "#0F1E36"}, "x": 0, "xanchor": "left"},
        legend={
            "orientation": "v",
            "yanchor": "top",
            "y": 1,
            "xanchor": "left",
            "x": 1.01,
            "font": {"size": 11},
            "title": {"font": {"size": 11, "color": "#5B6B82"}},
            "bgcolor": "rgba(0,0,0,0)",
        },
        hoverlabel={"bgcolor": "#FFFFFF", "bordercolor": "#C5CFDD", "font": {"size": 12, "color": "#0F1E36"}},
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#EEF2F7",
        linecolor="#C5CFDD",
        tickfont={"size": 11, "color": "#5B6B82"},
        title_font={"size": 12, "color": "#5B6B82"},
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#EEF2F7",
        zeroline=False,
        linecolor="#C5CFDD",
        tickfont={"size": 11, "color": "#5B6B82"},
        title_font={"size": 12, "color": "#5B6B82"},
    )