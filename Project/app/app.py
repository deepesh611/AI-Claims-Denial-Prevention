import io
import base64
import pandas as pd
import dash_bootstrap_components as dbc

from pipeline.rag import run_rag
from pipeline.agent import run_ai_agent
from dash import Dash, dcc, html, dash_table
from pipeline.shap_explainer import run_shap
from pipeline.rule_check import run_rule_check
from pipeline.ml_scoring import run_ml_scoring
from dash.dependencies import Input, Output, State

# =========================
# Initialize App
# =========================


dash_app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.LUX]
)

server = dash_app.server


# =========================
# Helpers
# =========================


def parse_csv(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    return df



def get_badge(status):
    if status == "HIGH":
        return dbc.Badge(
            "HIGH RISK",
            color="danger",
            className="mb-2 px-3 py-2"
        )

    elif status == "MEDIUM":
        return dbc.Badge(
            "MEDIUM RISK",
            color="warning",
            text_color="dark",
            className="mb-2 px-3 py-2"
        )

    elif status == "RULE FAIL":
        return dbc.Badge(
            "RULE FAIL",
            color="dark",
            className="mb-2 px-3 py-2"
        )

    return dbc.Badge(
        "LOW RISK",
        color="success",
        className="mb-2 px-3 py-2"
    )



def build_metric_card(title, value, color):

    return dbc.Card(

        dbc.CardBody([

            html.H2(
                str(value),
                className="fw-bold mb-1"
            ),

            html.P(
                title,
                className="mb-0 text-muted"
            )

        ]),

        className="shadow-sm border-0 h-100",

        style={
            "borderRadius": "18px",
            "borderTop": f"5px solid {color}"
        }
    )

# =========================
# Layout
# =========================


dash_app.layout = html.Div(

    id="theme-container",

    children=[

        dbc.Container([
             # =========================
            # Hero Banner
            # =========================

            dbc.Card(
                dbc.CardBody([

                    dbc.Row([

                        dbc.Col([

                            html.H1(
                                "AI Claim Denial Prevention System",
                                className="display-5 fw-bold"
                            ),

                            html.P(
                                "Analyze healthcare claims using rule validation, ML risk scoring, SHAP explainability, policy retrieval and AI-generated recommendations.",
                                className="lead"
                            )

                        ], width=10),

                        dbc.Col([

                            dbc.Switch(
                                id="theme-toggle",
                                label="Dark Mode",
                                value=False,
                                className="mt-3"
                            )

                        ], width=2)

                    ])

                ]),
                className="mb-4 shadow border-0",
                style={
                    "background": "linear-gradient(135deg, #1565C0, #42A5F5)",
                    "color": "white",
                    "borderRadius": "22px"
                }
            ),

            # =========================
            # Input Section
            # =========================

            dbc.Row([

                dbc.Col([

                    dbc.Card([

                        dbc.CardBody([

                            html.H4(
                                "Single Claim Analysis",
                                className="fw-bold mb-3"
                            ),

                            dbc.Input(
                                id="single-claim-input",
                                type="text",
                                placeholder="Example: CLM-1001",
                                className="mb-4"
                            ),

                            html.H4(
                                "OR Upload Multiple Claims",
                                className="fw-bold mb-3"
                            ),

                            dcc.Upload(
                                id='upload-data',

                                children=html.Div([
                                    html.H5("Drag & Drop CSV Here"),
                                    html.P("or click to select file")
                                ]),

                                style={
                                    'width': '100%',
                                    'height': '140px',
                                    'borderWidth': '2px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '18px',
                                    'textAlign': 'center',
                                    'backgroundColor': '#F8FAFC',
                                    },

                                multiple=False
                            ),

                            html.Div(id='preview-table'),

                            dbc.Button(
                                "Run AI Analysis",
                                id="run-analysis-btn",
                                color="primary",
                                size="lg",
                                className="mt-3 w-100"
                            )

                        ])

                    ],
                    className="shadow-sm border-0",
                    style={
                        "borderRadius": "20px"
                    })

                ], width=12)

            ], className="mb-4"),


            # =========================
            # Results Section
            # =========================

            dcc.Loading(
                id="results-loader",
                type="default",
                color="#1565C0",
                children=html.Div(id='results-section')
            )

        ], fluid=True, className="p-4")

    ]
)

            
# =========================
# Theme Callback
# =========================


@dash_app.callback(
    Output("theme-container", "style"),
    Input("theme-toggle", "value")
)

def toggle_theme(is_dark):

    if is_dark:
        return {
            "backgroundColor": "#0F172A",
            "minHeight": "100vh",
            "color": "white",
            "transition": "0.3s"
        }

    return {
        "backgroundColor": "#F5F7FB",
        "minHeight": "100vh",
        "transition": "0.3s"
    }


# =========================
# Upload Preview Callback
# =========================

@dash_app.callback(
    Output('preview-table', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_output(contents, filename):
    if contents is not None:
        df = parse_csv(contents)

        if 'claim_id' not in df.columns:
            return dbc.Alert(
                "Invalid CSV — must contain a 'claim_id' column.",
                color="danger",
                className="mt-3"
            )

        preview_df = df.head(5)
        return html.Div([
            html.H5(
                f"Uploaded: {filename} — {len(df)} claim(s) found",
                className="fw-bold mb-3"
            ),
            dash_table.DataTable(
                data=preview_df.to_dict('records'),
                columns=[{'name': col, 'id': col} for col in preview_df.columns],
                style_table={'overflowX': 'auto', 'borderRadius': '12px'},
                style_header={
                    'backgroundColor': '#1565C0',
                    'color'          : 'white',
                    'fontWeight'     : 'bold',
                    'border'         : 'none'
                },
                style_cell={
                    'padding'  : '12px',
                    'textAlign': 'left',
                    'border'   : '1px solid #E2E8F0'
                },
                style_data={'backgroundColor': 'white'},
                page_size=5
            )
        ])

    return dbc.Alert(
        "No CSV uploaded. You can still analyze a single claim ID.",
        color="light",
        className="mt-3"
    )

# =========================
# Analysis Callback
# =========================


@dash_app.callback(
    Output('results-section', 'children'),
    Input('run-analysis-btn', 'n_clicks'),
    State('single-claim-input', 'value'),
    State('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def run_analysis(n_clicks, single_claim, contents, filename):

    if not n_clicks:

        return dbc.Alert(
            "Upload claims and run analysis to view AI insights.",
            color="light",
            className="text-center mt-4"
        )

    if single_claim:
        claim_ids = [single_claim.strip()]

    elif contents:
        df = parse_csv(contents)
        df.columns = df.columns.str.strip().str.lower()
        if 'claim_id' not in df.columns:
            return dbc.Alert(
                "Invalid CSV — must contain a 'claim_id' column.",
                color="danger"
            )
        claim_ids = df['claim_id'].tolist()

    else:
        return dbc.Alert(
            "Please enter a claim ID or upload a CSV.",
            color="warning"
        )


    # =========================
    # Backend Pipeline
    # =========================

    rule_results = run_rule_check(claim_ids)

    passed = rule_results["passed"]
    failed = rule_results["failed"]


    if passed:
        ml_results, xgb_model, features_df = run_ml_scoring(passed)
    else:
        ml_results, xgb_model, features_df = {}, None, pd.DataFrame()


    high_risk_ids = [
        cid for cid in passed
        if ml_results.get(cid, {}).get("risk_label") == "HIGH"
    ]


    if high_risk_ids and xgb_model is not None:

        high_risk_df = features_df[
            features_df["claim_id"].isin(high_risk_ids)
        ].reset_index(drop=True)

        shap_results = run_shap(xgb_model, high_risk_df)

    else:
        shap_results = {}


    if shap_results:
        rag_results = run_rag(shap_results)
    else:
        rag_results = {}


    ai_summaries = run_ai_agent(
        claim_ids=claim_ids,
        passed=passed,
        failed=failed,
        ml_results=ml_results,
        shap_results=shap_results,
        rag_results=rag_results
    )


    # =========================
    # Metrics
    # =========================

    total_claims = len(claim_ids)
    total_failed = len(failed)
    total_high_risk = len(high_risk_ids)
    total_passed = len(passed)


    metrics_row = dbc.Row([

        dbc.Col(
            build_metric_card(
                "Claims Processed",
                total_claims,
                "#1565C0"
            ),
            md=3
        ),

        dbc.Col(
            build_metric_card(
                "High Risk Claims",
                total_high_risk,
                "#DC3545"
            ),
            md=3
        ),

        dbc.Col(
            build_metric_card(
                "Rule Failures",
                total_failed,
                "#FFC107"
            ),
            md=3
        ),

        dbc.Col(
            build_metric_card(
                "Passed Validation",
                total_passed,
                "#198754"
            ),
            md=3
        )

    ], className="mb-4")


    # =========================
    # Result Cards
    # =========================

    cards = []


    # RULE FAIL CARDS

    for claim_id, failures in failed.items():

        ai_summary = ai_summaries.get(claim_id, "")

        card = dbc.Card(
            dbc.CardBody([

                dbc.Row([

                    dbc.Col([
                        html.H3(
                            claim_id,
                            className="fw-bold text-primary"
                        )
                    ], width=8),

                    dbc.Col([
                        get_badge("RULE FAIL")
                    ], width=4, className="text-end")

                ]),

                html.Hr(),

                html.H5("Rule Validation Issues", className="fw-bold"),

                html.Ul([
                    html.Li(f) for f in failures
                ]),

                html.Hr(),

                html.H5("AI Recommendation", className="fw-bold"),

                html.P(ai_summary)

            ]),

            className="shadow-sm border-0 mb-4",
            style={
                'borderRadius': '20px',
                'padding': '8px'
            }
        )

        cards.append(card)


    # PASSED CLAIM CARDS

    for claim_id in passed:

        ml = ml_results.get(claim_id, {})

        risk_score = ml.get("risk_score", 0)
        risk_label = ml.get("risk_label", "LOW")

        shap = shap_results.get(claim_id, {})

        reason_1 = shap.get("reason_1", None)
        reason_2 = shap.get("reason_2", None)

        rag = rag_results.get(claim_id, {})

        policy_source = rag.get("policy_source", None)
        policy_text = rag.get("policy_text", None)

        ai_summary = ai_summaries.get(claim_id, "")


        progress_color = (
            "danger" if risk_score >= 0.75
            else "warning" if risk_score >= 0.4
            else "success"
        )


        reasons_section = html.Div([

            html.H5("Top Risk Factors", className="fw-bold"),

            html.Ul([
                html.Li(r)
                for r in [reason_1, reason_2]
                if r
            ])

        ]) if reason_1 else dbc.Alert(
            "No major risk factors detected.",
            color="success"
        )


        policy_section = html.Div([

            html.H5("Relevant Policy", className="fw-bold"),

            html.P([
                html.B("Policy Source: "),
                html.I(policy_source)
            ]),

            html.P(
                policy_text,
                style={
                    'fontSize': '14px',
                    'color': 'gray'
                }
            )

        ]) if policy_source else dbc.Alert(
            "No policy violations detected.",
            color="light"
        )


        card = dbc.Card(

            dbc.CardBody([

                dbc.Row([

                    dbc.Col([
                        html.H3(
                            claim_id,
                            className="fw-bold text-primary"
                        )
                    ], width=8),

                    dbc.Col([
                        get_badge(risk_label)
                    ], width=4, className="text-end")

                ]),

                html.Hr(),

                html.H5("Risk Score", className="fw-bold"),

                dbc.Progress(
                    value=int(risk_score * 100),
                    label=f"{int(risk_score * 100)}%",
                    color=progress_color,
                    striped=True,
                    animated=True,
                    className="mb-4",
                    style={
                        'height': '24px'
                    }
                ),

                reasons_section,

                html.Hr(),

                policy_section,

                html.Hr(),

                html.H5("AI Recommendation", className="fw-bold"),

                html.P(ai_summary)

            ]),

            className="shadow-sm border-0 mb-4",
            style={
                'borderRadius': '20px',
                'padding': '8px'
            }
        )

        cards.append(card)


    return html.Div([

        metrics_row,

        html.H3(
            "Analysis Results",
            className="fw-bold mb-4"
        ),

        html.Div(cards)

    ])


# =========================
# Run App
# =========================


if __name__ == '__main__':
    dash_app.run(debug=True)