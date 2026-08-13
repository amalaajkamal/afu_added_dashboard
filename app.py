import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import os
import re
from collections import Counter

# ── App Init ──────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    title="AFU Global Network Dashboard"
)
server = app.server

# ── Colours ───────────────────────────────────────────────────────────────────
REGION_COLORS = {
    "North America": "#E63946",
    "Europe":        "#4FC3F7",
    "Asia":          "#FFB300",
    "Oceania":       "#AB47BC",
    "South America": "#26A69A",
}

# ── Data ──────────────────────────────────────────────────────────────────────
def country_data():
    return pd.DataFrame([
        ("United States","North America",105,37.09,-95.71),
        ("Canada","North America",12,56.13,-106.35),
        ("Mexico","North America",1,23.63,-102.55),
        ("Ireland","Europe",9,53.41,-8.24),
        ("United Kingdom","Europe",2,55.37,-3.43),
        ("Portugal","Europe",2,39.39,-8.22),
        ("Spain","Europe",2,40.46,-3.74),
        ("Croatia","Europe",1,45.10,15.20),
        ("Czech Republic","Europe",1,49.81,15.47),
        ("Hungary","Europe",1,47.16,19.50),
        ("Israel","Europe",1,31.04,34.85),
        ("Slovakia","Europe",1,48.66,19.69),
        ("Slovenia","Europe",1,46.15,14.99),
        ("Switzerland","Europe",1,46.81,8.22),
        ("South Korea","Asia",3,35.90,127.76),
        ("Turkey","Asia",1,39.92,32.85),
        ("China","Asia",1,35.86,104.19),
        ("Philippines","Asia",1,12.87,121.77),
        ("Hong Kong SAR","Asia",1,22.39,114.10),
        ("Australia","Oceania",2,-25.27,133.77),
        ("Brazil","South America",3,-14.23,-51.92),
        ("Chile","South America",2,-35.67,-71.54),
    ], columns=["Country","Region","AFU_Members","Latitude","Longitude"])

def regional_data():
    return pd.DataFrame([
        ("North America",3,23,118),
        ("Europe",13,44,22),
        ("Asia",5,48,7),
        ("Oceania",1,14,2),
        ("South America",2,12,5),
    ], columns=["Region","Countries_in_AFU","Total_Countries","AFU_Institutions"])

def principles_data():
    return pd.DataFrame([
        (1,"P1: Older Adult Participation",20,71.0,"Well Implemented"),
        (2,"P2: Personal & Career Dev.",9,32.0,"Moderately Implemented"),
        (3,"P3: Educational Needs",8,29.0,"Moderately Implemented"),
        (4,"P4: Intergenerational Learning",15,54.0,"Well Implemented"),
        (5,"P5: Online Access",4,14.0,"Underimplemented"),
        (6,"P6: Research & Aging Agenda",14,50.0,"Well Implemented"),
        (7,"P7: Student & Longevity",5,18.0,"Underimplemented"),
        (8,"P8: Health & Wellness",13,46.0,"Well Implemented"),
        (9,"P9: Retired Community",7,25.0,"Moderately Implemented"),
        (10,"P10: Aging Organisations",6,21.0,"Underimplemented"),
    ], columns=["Principle_Number","Label","Mentions","Pct","Status"])

pop65 = {
    "Ireland":10.13,"Slovenia":2.11,"United States":1.67,"Canada":1.42,
    "Croatia":1.09,"Slovakia":0.97,"Israel":0.78,"Portugal":0.74,
    "Chile":0.69,"Hong Kong SAR":0.56,"Switzerland":0.54,"Hungary":0.50,
    "Czech Republic":0.43,"Australia":0.40,"South Korea":0.29,"Spain":0.19,
    "Philippines":0.15,"United Kingdom":0.15,"Brazil":0.12,"Turkey":0.11,
    "Mexico":0.102,"China":0.005,
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
sidebar = html.Div([
    html.Div([
        html.Span("🎓", style={"fontSize":"1.8rem"}),
        html.H5("AFU GN Dashboard", className="mb-0 ms-2",
                style={"color":"#4FC3F7","fontWeight":"800","letterSpacing":"0.04em"}),
    ], className="d-flex align-items-center mb-4 mt-2"),

    html.P("NAVIGATE", style={"color":"#546E7A","fontSize":"0.7rem",
                               "letterSpacing":"0.12em","fontWeight":"700"}),
    dbc.Nav([
        dbc.NavLink([html.I(className="fa fa-globe me-2"), "Global Overview"],
                    href="/", active="exact", id="nav-overview"),
        dbc.NavLink([html.I(className="fa fa-chart-bar me-2"), "Principle Analysis"],
                    href="/principles", active="exact"),
        dbc.NavLink([html.I(className="fa fa-map me-2"), "Regional Equity"],
                    href="/regional", active="exact"),
        dbc.NavLink([html.I(className="fa fa-star me-2"), "Best Practices"],
                    href="/bestpractices", active="exact"),
        dbc.NavLink([html.I(className="fa fa-earth-americas me-2"), "Impact Map"],
                    href="/impactmap", active="exact"),
        dbc.NavLink([html.I(className="fa fa-book-open me-2"), "Literature Search"],
                    href="/literature", active="exact",
                    style={"color":"#FFB300","fontWeight":"700"}),
    ], vertical=True, pills=True, className="mb-4"),

    html.Hr(style={"borderColor":"#1e3a5f"}),
    html.P("DATA SOURCES", style={"color":"#546E7A","fontSize":"0.7rem",
                                   "letterSpacing":"0.12em","fontWeight":"700"}),
    html.Ul([
        html.Li("AFU GN Website (June 2026)", style={"fontSize":"0.78rem","color":"#90a4ae"}),
        html.Li("AFU Best Practices Database", style={"fontSize":"0.78rem","color":"#90a4ae"}),
        html.Li("World Bank SP.POP.65UP.TO (2025)", style={"fontSize":"0.78rem","color":"#90a4ae"}),
        html.Li("UN Population Division WPP 2025", style={"fontSize":"0.78rem","color":"#90a4ae"}),
        html.Li("Semantic Scholar API", style={"fontSize":"0.78rem","color":"#90a4ae"}),
    ], style={"paddingLeft":"1rem"}),

    html.Hr(style={"borderColor":"#1e3a5f"}),
    html.P([
        html.I(className="fa fa-file-alt me-1"),
        html.Em("Mapping the AFU GN: A Population-Adjusted Analysis", style={"fontSize":"0.72rem","color":"#546E7A"}),
    ]),
    html.P("Generations at Work, DCU, Oct 2026",
           style={"fontSize":"0.7rem","color":"#546E7A"}),
], style={
    "position":"fixed","top":0,"left":0,"bottom":0,"width":"240px",
    "backgroundColor":"#0a1628","padding":"20px 16px","overflowY":"auto",
    "borderRight":"1px solid #1e3a5f","zIndex":1000,
})

# ── KPI Card ──────────────────────────────────────────────────────────────────
def kpi_card(value, label, color="#4FC3F7", border_color=None):
    return dbc.Card([
        dbc.CardBody([
            html.H3(value, style={"color":color,"fontWeight":"900","marginBottom":"2px"}),
            html.P(label, style={"color":"#546E7A","fontSize":"0.68rem",
                                  "textTransform":"uppercase","letterSpacing":"0.1em","marginBottom":0}),
        ], className="text-center p-2"),
    ], style={"backgroundColor":"#0d1b2a","border":f"1px solid {border_color or '#1e3a5f'}",
              "borderTop":f"3px solid {color}"})

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — GLOBAL OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
def page_overview():
    df = country_data()
    dr = regional_data()

    # World bubble map
    fig_map = px.scatter_geo(
        df, lat="Latitude", lon="Longitude",
        size="AFU_Members", color="Region",
        color_discrete_map=REGION_COLORS,
        hover_name="Country",
        hover_data={"AFU_Members":True,"Latitude":False,"Longitude":False},
        size_max=55, projection="natural earth",
    )
    fig_map.update_geos(
        bgcolor="#050e1a", landcolor="#0d2137", oceancolor="#060f1c",
        showocean=True, showland=True,
        coastlinecolor="#1e3a5f", countrycolor="#1e3a5f", showframe=False,
    )
    fig_map.update_layout(
        height=420, margin=dict(l=0,r=0,t=0,b=0),
        paper_bgcolor="#050e1a", plot_bgcolor="#050e1a",
        legend=dict(orientation="h", y=-0.05, font=dict(size=11,color="#cce4ff"),
                    bgcolor="rgba(0,0,0,0)"),
    )

    # Donut
    fig_donut = px.pie(
        dr, values="AFU_Institutions", names="Region",
        color="Region", color_discrete_map=REGION_COLORS, hole=0.55,
    )
    fig_donut.update_traces(textposition="outside", textfont_size=10)
    fig_donut.update_layout(
        height=280, margin=dict(l=10,r=10,t=10,b=10),
        paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
    )

    # Bar
    fig_bar = px.bar(
        dr.sort_values("AFU_Institutions"),
        x="AFU_Institutions", y="Region", orientation="h",
        color="Region", color_discrete_map=REGION_COLORS, text="AFU_Institutions",
    )
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(
        height=280, margin=dict(l=10,r=10,t=10,b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False, xaxis=dict(color="#546E7A"), yaxis=dict(color="#cce4ff"),
    )

    return html.Div([
        # Header
        dbc.Row([
            dbc.Col(html.Div([
                html.Span("🌍 ", style={"fontSize":"1.2rem"}),
                html.Span("AFU GLOBAL NETWORK — IMPLEMENTATION GAP ANALYSIS",
                          style={"color":"#4FC3F7","fontWeight":"800","letterSpacing":"0.06em","fontSize":"1.05rem"}),
                html.Span("  Geographic & Thematic Analysis • June 2026",
                          style={"color":"#37474F","fontSize":"0.78rem","marginLeft":"12px"}),
            ], style={"backgroundColor":"#0d1b2a","padding":"8px 16px","borderRadius":"6px"}))
        ], className="mb-3"),

        # KPIs
        dbc.Row([
            dbc.Col(kpi_card("154","Member Institutions","#4FC3F7"), width=2),
            dbc.Col(kpi_card("77%","North America Share","#E63946"), width=2),
            dbc.Col(kpi_card("22","Countries","#26A69A"), width=2),
            dbc.Col(kpi_card("28","Best Practices","#FFB300"), width=2),
            dbc.Col(kpi_card("14%/18%","P5 & P7 Rate","#EF5350","#EF5350"), width=2),
            dbc.Col(kpi_card("13%","Submission Rate","#AB47BC"), width=2),
        ], className="mb-3 g-2"),

        # Map + Charts
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_map, config={"displayModeBar":False}), width=8),
            dbc.Col([
                html.P("REGIONAL SHARE", style={"color":"#4FC3F7","fontSize":"0.72rem",
                                                 "fontWeight":"700","letterSpacing":"0.1em"}),
                dcc.Graph(figure=fig_donut, config={"displayModeBar":False}),
                html.P("INSTITUTIONS PER REGION", style={"color":"#4FC3F7","fontSize":"0.72rem",
                                                          "fontWeight":"700","letterSpacing":"0.1em"}),
                dcc.Graph(figure=fig_bar, config={"displayModeBar":False}),
            ], width=4),
        ]),
    ])

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — PRINCIPLE ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
def page_principles():
    df = principles_data()
    df_sorted = df.sort_values("Pct", ascending=True)

    color_map = {"Well Implemented":"#4CAF50","Moderately Implemented":"#FFB300","Underimplemented":"#EF5350"}

    fig = px.bar(
        df_sorted, x="Pct", y="Label", orientation="h",
        color="Status", color_discrete_map=color_map,
        text=df_sorted["Pct"].apply(lambda x: f"{x:.0f}%"),
    )
    fig.add_vline(x=50, line_dash="dot", line_color="#546E7A", line_width=1)
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=420, margin=dict(l=10,r=60,t=20,b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(color="#546E7A",range=[0,85]),
        yaxis=dict(color="#cce4ff"),
        legend=dict(orientation="h", y=-0.12, font=dict(color="#cce4ff")),
    )

    return html.Div([
        dbc.Row([
            dbc.Col(html.Div([
                html.Span("📐 ", style={"fontSize":"1.2rem"}),
                html.Span("AFU PRINCIPLE IMPLEMENTATION GAP ANALYSIS",
                          style={"color":"#4FC3F7","fontWeight":"800","letterSpacing":"0.06em","fontSize":"1.05rem"}),
                html.Span("  Based on 28 Best Practice submissions from 20 institutions",
                          style={"color":"#37474F","fontSize":"0.78rem","marginLeft":"12px"}),
            ], style={"backgroundColor":"#0d1b2a","padding":"8px 16px","borderRadius":"6px"}))
        ], className="mb-3"),

        # KPIs
        dbc.Row([
            dbc.Col(kpi_card("4","Well Implemented","#4CAF50"), width=3),
            dbc.Col(kpi_card("3","Moderately Implemented","#FFB300"), width=3),
            dbc.Col(kpi_card("3","Underimplemented","#EF5350"), width=3),
            dbc.Col(kpi_card("P5 Only 14% | P7 Only 18%","Most Critical Gap","#EF5350","#EF5350"), width=3),
        ], className="mb-3 g-2"),

        dbc.Row([
            dbc.Col([
                html.P("PRINCIPLE CITATION FREQUENCY (% of 28 submissions)",
                       style={"color":"#4FC3F7","fontSize":"0.72rem","fontWeight":"700","letterSpacing":"0.1em"}),
                dcc.Graph(figure=fig, config={"displayModeBar":False}),
                dbc.Alert([
                    html.I(className="fa fa-triangle-exclamation me-2"),
                    "P5 (Online access) cited in only 14% and P7 (Longevity dividend) in only 18% of submissions — the most underimplemented principles across the network.",
                ], color="danger", className="mt-2", style={"fontSize":"0.82rem"}),
            ], width=12),
        ]),
    ])

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — REGIONAL EQUITY
# ══════════════════════════════════════════════════════════════════════════════
def page_regional():
    dr = regional_data()
    df = country_data()

    # Coverage gap chart
    dr["Countries_Missing"] = dr["Total_Countries"] - dr["Countries_in_AFU"]
    df_melt = dr.melt(id_vars="Region", value_vars=["Countries_in_AFU","Countries_Missing"],
                      var_name="Type", value_name="Count")
    df_melt["Type"] = df_melt["Type"].map({"Countries_in_AFU":"In AFU GN","Countries_Missing":"Not in AFU GN"})

    fig_cov = px.bar(df_melt, x="Count", y="Region", color="Type", orientation="h",
                     color_discrete_map={"In AFU GN":"#2E6DA4","Not in AFU GN":"#1e3a5f"},
                     barmode="stack", text="Count")
    fig_cov.update_traces(textposition="inside")
    fig_cov.update_layout(
        height=300, margin=dict(l=10,r=10,t=10,b=30),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.2, font=dict(color="#cce4ff")),
        xaxis=dict(color="#546E7A"), yaxis=dict(color="#cce4ff"),
    )

    # Density chart
    dens_data = [(c, pop65[c], r) for _, (c, r, *_) in df.iterrows() if c in pop65]
    df_dens = pd.DataFrame(dens_data, columns=["Country","Density","Region"])
    df_dens = df_dens.sort_values("Density", ascending=False)

    fig_dens = px.bar(df_dens, x="Country", y="Density", color="Region",
                      color_discrete_map=REGION_COLORS,
                      text=df_dens["Density"].apply(lambda x: f"{x:.2f}"),)
    fig_dens.update_traces(textposition="outside", textfont_size=8)
    fig_dens.update_layout(
        height=300, margin=dict(l=10,r=10,t=10,b=120),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickangle=-45, color="#546E7A"),
        yaxis=dict(color="#cce4ff", title="AFU per Million Seniors"),
        legend=dict(orientation="h", y=-0.45, font=dict(color="#cce4ff",size=10)),
    )

    # Table
    df_table = dr[["Region","Countries_in_AFU","Total_Countries","Countries_Missing"]].copy()
    df_table.columns = ["Region","In AFU GN","Total","Not Represented"]
    df_table["Coverage %"] = (df_table["In AFU GN"] / df_table["Total"] * 100).round(1)

    return html.Div([
        html.Div([
            html.Span("🗺️ ", style={"fontSize":"1.2rem"}),
            html.Span("GEOGRAPHIC EQUITY & POPULATION-ADJUSTED ANALYSIS",
                      style={"color":"#4FC3F7","fontWeight":"800","letterSpacing":"0.06em","fontSize":"1.05rem"}),
            html.Span("  Country coverage gaps and age-adjusted AFU density",
                      style={"color":"#37474F","fontSize":"0.78rem","marginLeft":"12px"}),
        ], style={"backgroundColor":"#0d1b2a","padding":"8px 16px","borderRadius":"6px","marginBottom":"12px"}),

        dbc.Row([
            dbc.Col([
                html.P("COUNTRY COVERAGE GAP BY REGION",
                       style={"color":"#4FC3F7","fontSize":"0.72rem","fontWeight":"700","letterSpacing":"0.1em"}),
                dcc.Graph(figure=fig_cov, config={"displayModeBar":False}),
                dash_table.DataTable(
                    data=df_table.to_dict("records"),
                    columns=[{"name":c,"id":c} for c in df_table.columns],
                    style_table={"overflowX":"auto"},
                    style_header={"backgroundColor":"#0d1b2a","color":"#4FC3F7","fontWeight":"700","fontSize":"0.75rem"},
                    style_cell={"backgroundColor":"#050e1a","color":"#cce4ff","fontSize":"0.78rem","padding":"6px"},
                    style_data_conditional=[{"if":{"row_index":"odd"},"backgroundColor":"#0a1628"}],
                ),
            ], width=6),
            dbc.Col([
                html.P("AFU DENSITY PER MILLION SENIORS (2025)",
                       style={"color":"#4FC3F7","fontSize":"0.72rem","fontWeight":"700","letterSpacing":"0.1em"}),
                dcc.Graph(figure=fig_dens, config={"displayModeBar":False}),
                dbc.Alert([
                    "💡 ",
                    html.B("Ireland (10.13)"), " leads due to DCU founder effect. ",
                    html.B("China (0.005)"), " — 209.74M seniors — is most underserved: a ",
                    html.B("2,000-fold gap"), ".",
                ], color="danger", style={"fontSize":"0.8rem"}),
            ], width=6),
        ]),
    ])

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — BEST PRACTICES
# ══════════════════════════════════════════════════════════════════════════════
def page_bestpractices():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "Form_Data_Entry-Grid_view.csv")
    try:
        df = pd.read_csv(csv_path)
        df.columns = [c.strip() for c in df.columns]
        pcol = [c for c in df.columns if "Principle" in c][0]
        ucol = [c for c in df.columns if "Submitting" in c or "Institution" in c][0]
        acol = [c for c in df.columns if "Audience" in c or "Target" in c]
        acol = acol[0] if acol else None

        principles = sorted(set(
            p.strip() for vals in df[pcol].dropna() for p in str(vals).split(",")
        ))
        universities = sorted(df[ucol].dropna().unique())

        return html.Div([
            html.Div([
                html.Span("📋 ", style={"fontSize":"1.2rem"}),
                html.Span("BEST PRACTICES EXPLORER",
                          style={"color":"#4FC3F7","fontWeight":"800","letterSpacing":"0.06em","fontSize":"1.05rem"}),
            ], style={"backgroundColor":"#0d1b2a","padding":"8px 16px","borderRadius":"6px","marginBottom":"12px"}),

            html.P(f"All {len(df)} submissions from the AFU GN Best Practices Database",
                   style={"color":"#546E7A","fontStyle":"italic"}),

            dbc.Row([
                dbc.Col([
                    html.Label("Filter by Principle", style={"color":"#cce4ff","fontSize":"0.8rem"}),
                    dcc.Dropdown(principles, multi=True, id="bp-principle-filter",
                                 style={"backgroundColor":"#0d1b2a","color":"#000"},
                                 placeholder="Choose principles..."),
                ], width=6),
                dbc.Col([
                    html.Label("Filter by University", style={"color":"#cce4ff","fontSize":"0.8rem"}),
                    dcc.Dropdown(universities, multi=True, id="bp-uni-filter",
                                 style={"backgroundColor":"#0d1b2a"},
                                 placeholder="Choose universities..."),
                ], width=6),
            ], className="mb-3"),

            html.Div(id="bp-stats", className="mb-3"),
            html.Div(id="bp-table"),

            # Store data
            dcc.Store(id="bp-data", data=df.to_dict("records")),
            dcc.Store(id="bp-cols", data={"pcol":pcol,"ucol":ucol}),
        ])
    except Exception as e:
        return dbc.Alert(f"Could not load Best Practices data: {e}", color="warning")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — IMPACT MAP
# ══════════════════════════════════════════════════════════════════════════════
INSTITUTIONS = {
    "United States": ["Arizona State University","University of Southern California","UCLA",
                      "University of Maryland","Fordham University","Boston College",
                      "University of Wisconsin-Green Bay","Middle Tennessee State University",
                      "Towson University","Fairleigh Dickinson University","St Catherine University",
                      "Syracuse University","Temple University","Penn State University",
                      "University of Delaware","Drexel University","George Mason University",
                      "University of Florida","University of Georgia","Emory University"],
    "Canada": ["University of Windsor","University of Manitoba","University of Calgary",
               "Kwantlen Polytechnic University","UBC","McMaster University",
               "Toronto Metropolitan University","Trent University","Ontario Tech University",
               "Niagara College","University of the Fraser Valley","UBC Okanagan"],
    "Mexico": ["ITESO, Universidad Jesuita de Guadalajara"],
    "Ireland": ["Dublin City University","University College Dublin","Trinity College Dublin",
                "University of Galway","University of Limerick","Maynooth University",
                "Technological University Dublin","Cork Institute of Technology","University College Cork"],
    "South Korea": ["Chosun University","Paichai University","Yonsei University"],
    "China": ["Open University of China"],
    "Australia": ["University of Queensland","Monash University"],
    "Brazil": ["University of São Paulo","Federal University of Minas Gerais","PUC-Rio"],
    "Chile": ["Pontifical Catholic University of Chile","University of Chile"],
}

def page_impactmap():
    df = country_data()
    regions = ["Asia","Europe","North America","Oceania","South America"]

    return html.Div([
        html.Div([
            html.Span("🌐 ", style={"fontSize":"1.2rem"}),
            html.Span("AFU GLOBAL NETWORK",
                      style={"color":"#4FC3F7","fontWeight":"800","letterSpacing":"0.06em","fontSize":"1.05rem"}),
            html.Span("  Impact Map",
                      style={"color":"#37474F","fontSize":"0.78rem","marginLeft":"12px"}),
        ], style={"backgroundColor":"#0d1b2a","padding":"8px 16px","borderRadius":"6px","marginBottom":"12px"}),

        # Region buttons
        dbc.Row([
            dbc.Col(dbc.Button(
                f"▶ {r}", id={"type":"region-btn","index":r},
                color="secondary", outline=True, size="sm",
                className="me-2 mb-2",
                style={"borderColor":"#1e3a5f","color":"#cce4ff"}
            )) for r in regions
        ], className="mb-2"),

        dbc.Row([
            dbc.Col(html.Div(id="impact-countries"), width=3),
            dbc.Col(dcc.Graph(id="impact-map-fig", config={"displayModeBar":False}), width=6),
            dbc.Col(html.Div(id="impact-institutions"), width=3),
        ]),

        dbc.Row([
            dbc.Col(html.Div(id="impact-stats-left"), width=6),
            dbc.Col(html.Div(id="impact-stats-right"), width=6),
        ], className="mt-2"),

        dcc.Store(id="selected-region", data="North America"),
    ])

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — LITERATURE SEARCH
# ══════════════════════════════════════════════════════════════════════════════
def page_literature():
    return html.Div([
        html.Div([
            html.Span("📚 ", style={"fontSize":"1.2rem"}),
            html.Span("AFU LITERATURE SEARCH ENGINE",
                      style={"color":"#FFB300","fontWeight":"800","letterSpacing":"0.06em","fontSize":"1.05rem"}),
            html.Span("  Powered by Semantic Scholar API",
                      style={"color":"#37474F","fontSize":"0.78rem","marginLeft":"12px"}),
        ], style={"backgroundColor":"#0d1b2a","padding":"8px 16px","borderRadius":"6px","marginBottom":"12px"}),

        dbc.Row([
            dbc.Col([
                dbc.InputGroup([
                    dbc.Input(id="lit-search-input", placeholder="Search AFU literature...",
                              value="Age-Friendly University",
                              style={"backgroundColor":"#0d1b2a","color":"#cce4ff","border":"1px solid #1e3a5f"}),
                    dbc.Button([html.I(className="fa fa-search me-2"), "Search"],
                               id="lit-search-btn", color="primary", n_clicks=0),
                ]),
            ], width=8),
            dbc.Col([
                dbc.Select(id="lit-year-filter",
                           options=[{"label":"All Years","value":"all"},
                                    {"label":"2020-2026","value":"2020"},
                                    {"label":"2015-2019","value":"2015"},
                                    {"label":"Before 2015","value":"before2015"}],
                           value="all",
                           style={"backgroundColor":"#0d1b2a","color":"#cce4ff","border":"1px solid #1e3a5f"}),
            ], width=2),
            dbc.Col([
                dbc.Select(id="lit-sort-filter",
                           options=[{"label":"Most Cited","value":"citationCount"},
                                    {"label":"Most Recent","value":"year"},
                                    {"label":"Relevance","value":"relevance"}],
                           value="citationCount",
                           style={"backgroundColor":"#0d1b2a","color":"#cce4ff","border":"1px solid #1e3a5f"}),
            ], width=2),
        ], className="mb-3"),

        # Quick filter chips
        html.Div([
            html.Span("Quick searches: ", style={"color":"#546E7A","fontSize":"0.8rem"}),
            *[dbc.Badge(t, color="primary", className="me-1 cursor-pointer",
                        id={"type":"quick-search","index":t}, style={"cursor":"pointer"})
              for t in ["Age-Friendly University","AFU Ten Principles","Intergenerational Learning",
                        "Digital Inclusion Older Adults","Longevity Dividend","AFU Global Network"]],
        ], className="mb-3"),

        html.Div(id="lit-results-stats", className="mb-2"),
        dbc.Spinner(html.Div(id="lit-results"), color="primary"),
    ])

# ── Main Layout ───────────────────────────────────────────────────────────────
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    html.Div([
        html.Div(id="page-content", style={"padding":"20px"}),
    ], style={"marginLeft":"240px","minHeight":"100vh","backgroundColor":"#050e1a"}),
], style={"backgroundColor":"#050e1a"})

# ══════════════════════════════════════════════════════════════════════════════
# CALLBACKS
# ══════════════════════════════════════════════════════════════════════════════

# Router
@app.callback(Output("page-content","children"), Input("url","pathname"))
def render_page(pathname):
    if pathname == "/principles":   return page_principles()
    if pathname == "/regional":     return page_regional()
    if pathname == "/bestpractices":return page_bestpractices()
    if pathname == "/impactmap":    return page_impactmap()
    if pathname == "/literature":   return page_literature()
    return page_overview()

# Best Practices filter
@app.callback(
    Output("bp-stats","children"),
    Output("bp-table","children"),
    Input("bp-principle-filter","value"),
    Input("bp-uni-filter","value"),
    State("bp-data","data"),
    State("bp-cols","data"),
    prevent_initial_call=False,
)
def filter_best_practices(principles, unis, data, cols):
    if not data or not cols:
        return "", dbc.Alert("No data loaded.", color="warning")

    df = pd.DataFrame(data)
    pcol = cols["pcol"]; ucol = cols["ucol"]

    if principles:
        df = df[df[pcol].apply(lambda x: any(p in str(x) for p in principles))]
    if unis:
        df = df[df[ucol].isin(unis)]

    stats = dbc.Row([
        dbc.Col(html.H6(f"Showing {len(df)} of 28 submissions",
                        style={"color":"#cce4ff"}), width=12),
    ])

    table = dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"name":c,"id":c,"presentation":"markdown"} for c in df.columns[:6]],
        page_size=10,
        style_table={"overflowX":"auto"},
        style_header={"backgroundColor":"#0d1b2a","color":"#4FC3F7","fontWeight":"700","fontSize":"0.75rem"},
        style_cell={"backgroundColor":"#050e1a","color":"#cce4ff","fontSize":"0.78rem",
                    "padding":"8px","maxWidth":"200px","overflow":"hidden","textOverflow":"ellipsis"},
        style_data_conditional=[{"if":{"row_index":"odd"},"backgroundColor":"#0a1628"}],
        tooltip_data=[{c: {"value":str(row[c]),"type":"markdown"} for c in df.columns} for row in df.to_dict("records")],
        tooltip_duration=None,
    )
    return stats, table

# Impact Map
@app.callback(
    Output("impact-countries","children"),
    Output("impact-map-fig","figure"),
    Output("impact-institutions","children"),
    Output("impact-stats-left","children"),
    Output("impact-stats-right","children"),
    Output("selected-region","data"),
    Input({"type":"region-btn","index":dash.ALL},"n_clicks"),
    State("selected-region","data"),
    prevent_initial_call=True,
)
def update_impact_map(n_clicks, current_region):
    ctx = dash.callback_context
    if not ctx.triggered:
        region = current_region
    else:
        region = ctx.triggered[0]["prop_id"].split('"index":"')[1].split('"')[0]

    df = country_data()
    region_df = df[df["Region"] == region]
    countries = region_df["Country"].tolist()
    total_inst = region_df["AFU_Members"].sum()

    # Map
    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lat=region_df["Latitude"], lon=region_df["Longitude"],
        mode="markers",
        marker=dict(size=region_df["AFU_Members"]*8+8,
                    color=REGION_COLORS.get(region,"#4FC3F7"), opacity=0.8),
        text=region_df["Country"], hoverinfo="text+name",
        name=region,
    ))
    fig.update_geos(
        bgcolor="#050e1a", landcolor="#0d2137", oceancolor="#060f1c",
        showocean=True, showland=True,
        coastlinecolor="#1e3a5f", countrycolor="#1e3a5f",
        showframe=False,
        lataxis_range=[-60,80] if region not in ["Oceania"] else [-50,0],
    )
    fig.update_layout(
        height=400, margin=dict(l=0,r=0,t=0,b=0),
        paper_bgcolor="#050e1a", showlegend=False,
    )

    # Countries list
    country_list = html.Div([
        html.P("COUNTRIES", style={"color":"#FF9800","fontSize":"0.72rem",
                                    "fontWeight":"700","letterSpacing":"0.1em"}),
        *[html.Div(f"▶ {c}", style={"color":"#FF9800","fontSize":"0.82rem",
                                     "padding":"4px 0","borderLeft":"2px solid #FF9800",
                                     "paddingLeft":"8px","marginBottom":"3px"})
          for c in countries],
    ], style={"backgroundColor":"#0a1628","padding":"12px","borderRadius":"6px"})

    # Institutions list
    all_insts = []
    for c in countries:
        if c in INSTITUTIONS:
            all_insts.extend(INSTITUTIONS[c])

    inst_list = html.Div([
        html.P(f"INSTITUTIONS ({len(all_insts)})",
               style={"color":"#4FC3F7","fontSize":"0.72rem","fontWeight":"700","letterSpacing":"0.1em"}),
        *[html.Div([html.I(className="fa fa-graduation-cap me-2",
                           style={"color":"#FF9800","fontSize":"0.7rem"}),
                    inst],
                   style={"color":"#cce4ff","fontSize":"0.78rem","padding":"4px 0",
                          "borderLeft":"2px solid #1e3a5f","paddingLeft":"8px","marginBottom":"2px"})
          for inst in all_insts[:15]],
    ], style={"backgroundColor":"#0a1628","padding":"12px","borderRadius":"6px","maxHeight":"400px","overflowY":"auto"})

    # Stats
    stats_left = dbc.Card([
        dbc.CardBody([
            html.H3(total_inst, style={"color":"#FF9800","fontWeight":"900"}),
            html.P("AFU MEMBERS", style={"color":"#546E7A","fontSize":"0.68rem",
                                          "letterSpacing":"0.1em","textTransform":"uppercase"}),
        ], className="text-center p-2"),
    ], style={"backgroundColor":"#0d1b2a","border":"1px solid #1e3a5f"})

    stats_right = dbc.Card([
        dbc.CardBody([
            html.H5(f"{region} — {region}",
                    style={"color":"#FF9800","fontWeight":"700"}),
            html.P("REGION", style={"color":"#546E7A","fontSize":"0.68rem",
                                     "letterSpacing":"0.1em","textTransform":"uppercase"}),
        ], className="text-center p-2"),
    ], style={"backgroundColor":"#0d1b2a","border":"1px solid #1e3a5f"})

    return country_list, fig, inst_list, stats_left, stats_right, region

# Literature Search
@app.callback(
    Output("lit-results","children"),
    Output("lit-results-stats","children"),
    Input("lit-search-btn","n_clicks"),
    Input({"type":"quick-search","index":dash.ALL},"n_clicks"),
    State("lit-search-input","value"),
    State("lit-year-filter","value"),
    State("lit-sort-filter","value"),
    prevent_initial_call=False,
)
def search_literature(btn_clicks, quick_clicks, query, year_filter, sort_by):
    ctx = dash.callback_context
    # Check if quick search triggered
    if ctx.triggered and "quick-search" in ctx.triggered[0]["prop_id"]:
        idx = ctx.triggered[0]["prop_id"].split('"index":"')[1].split('"')[0]
        query = idx

    if not query:
        query = "Age-Friendly University"

    try:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": 20,
            "fields": "title,authors,year,abstract,citationCount,externalIds,venue,url",
        }
        if sort_by in ["citationCount","year"]:
            params["sort"] = sort_by

        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        papers = data.get("data", [])

        # Year filter
        if year_filter == "2020":
            papers = [p for p in papers if p.get("year",0) and p["year"] >= 2020]
        elif year_filter == "2015":
            papers = [p for p in papers if p.get("year",0) and 2015 <= p["year"] < 2020]
        elif year_filter == "before2015":
            papers = [p for p in papers if p.get("year",0) and p["year"] < 2015]

        if not papers:
            return dbc.Alert("No papers found. Try a different search term.", color="warning"), ""

        stats = html.P(f"Found {len(papers)} papers for '{query}'",
                       style={"color":"#4FC3F7","fontSize":"0.85rem","fontWeight":"600"})

        cards = []
        for p in papers:
            authors = ", ".join([a.get("name","") for a in p.get("authors",[])[:3]])
            if len(p.get("authors",[])) > 3:
                authors += " et al."
            year = p.get("year","N/A")
            title = p.get("title","Untitled")
            abstract = p.get("abstract","No abstract available.")
            citations = p.get("citationCount", 0)
            venue = p.get("venue","")
            doi = p.get("externalIds",{}).get("DOI","")
            paper_url = p.get("url","")

            card = dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6(title, style={"color":"#4FC3F7","fontWeight":"700",
                                                   "fontSize":"0.9rem","marginBottom":"4px"}),
                            html.P(authors, style={"color":"#FFB300","fontSize":"0.78rem","marginBottom":"2px"}),
                            html.P([
                                dbc.Badge(str(year), color="primary", className="me-2"),
                                dbc.Badge(venue[:40] if venue else "Unknown Venue",
                                          color="secondary", className="me-2"),
                                dbc.Badge(f"📖 {citations} citations",
                                          color="success" if citations > 10 else "secondary"),
                            ], className="mb-2"),
                            html.P(
                                abstract[:250] + "..." if abstract and len(abstract) > 250 else abstract,
                                style={"color":"#90a4ae","fontSize":"0.78rem","marginBottom":"4px"}
                            ),
                            html.Div([
                                dbc.Button("View Paper", href=paper_url, target="_blank",
                                           color="primary", size="sm", className="me-2",
                                           external_link=True) if paper_url else None,
                                dbc.Button(f"DOI: {doi[:30]}", href=f"https://doi.org/{doi}",
                                           target="_blank", color="secondary", size="sm",
                                           external_link=True) if doi else None,
                            ]),
                        ]),
                    ]),
                ], className="p-3"),
            ], style={"backgroundColor":"#0d1b2a","border":"1px solid #1e3a5f",
                      "marginBottom":"10px","borderLeft":f"4px solid #4FC3F7"})
            cards.append(card)

        return html.Div(cards), stats

    except Exception as e:
        return dbc.Alert(f"Search error: {str(e)}. Check your internet connection.", color="danger"), ""

# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=8050)
