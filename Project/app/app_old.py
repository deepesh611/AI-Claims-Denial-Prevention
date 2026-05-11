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


# Initialize App

dash_app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

server = dash_app.server

def parse_csv(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    return df


# Dummy Claim Results

dummy_results = [
    {
        "claim_id": "CLM-1001",
        "status": "HIGH RISK",
        "score": 0.82,
        "reasons": [
            "Missing supporting diagnosis documentation",
            "Procedure code mismatch detected",
            "High historical denial pattern"
        ],
        "policy": "Incomplete Clinical Documentation Policy",
        "recommendation": (
            "Review supporting documents, validate procedure codes "
            "and ensure diagnosis alignment before submission."
        ),
        "details": (
            "This claim was flagged due to multiple documentation gaps "
            "and inconsistent coding patterns."
        )
    },
    {
        "claim_id": "CLM-1002",
        "status": "RULE FAIL",
        "score": 0.58,
        "reasons": [
            "Authorization reference missing",
            "Claim exceeds policy submission window"
        ],
        "policy": "Timely Filing and Authorization Compliance Rule",
        "recommendation": (
            "Add authorization details and confirm timely filing "
            "requirements before resubmission."
        ),
        "details": (
            "The rule engine detected missing authorization "
            "and filing timeline issues."
        )
    },
    {
        "claim_id": "CLM-1003",
        "status": "LOW RISK",
        "score": 0.12,
        "reasons": [
            "All mandatory fields validated",
            "No coding inconsistencies detected",
            "Strong historical approval rate"
        ],
        "policy": "No active policy violations",
        "recommendation": (
            "Claim is ready for submission with minimal denial risk."
        ),
        "details": (
            "This claim passed all validation and compliance checks."
        )
    }
]


# Badge Helper

def get_badge(status):

    if status == "HIGH RISK":
        return dbc.Badge(
            status,
            color="danger",
            className="mb-2"
        )

    elif status == "RULE FAIL":
        return dbc.Badge(
            status,
            color="warning",
            text_color="dark",
            className="mb-2"
        )

    return dbc.Badge(
        status,
        color="success",
        className="mb-2"
    )



# Layout

dash_app.layout = html.Div(

    id="theme-container",

    children=[

        dbc.Container([

            # Header
            dbc.Row([

                dbc.Col([

                    html.H1(
                        "Claim Denial Prevention System",
                        id="main-title",
                        style={
                            "fontWeight": "bold",
                            "marginTop": "20px"
                        }
                    ),

                    html.P(
                        "Upload claims for risk analysis",
                        id="subtitle",
                        style={
                            "fontSize": "18px"
                        }
                    )

                ], width=10),

                dbc.Col([

                    dbc.Switch(
                        id="theme-toggle",
                        label="Dark Mode",
                        value=False,
                        className="mt-4"
                    )

                ], width=2)

            ]),

            html.Hr(),

            # Single Claim Input
            dbc.Row([
                dbc.Col([

                    html.H4("Enter Single Claim ID"),

                    dbc.Input(
                        id="single-claim-input",
                        type="text",
                        placeholder="Example: CLM-1001",
                        className="mb-4"
                    )

                ])
            ]),

            # Upload Section
            dbc.Row([
                dbc.Col([

                    html.H4("OR Upload Multiple Claim IDs via CSV"),

                    dcc.Upload(
                        id='upload-data',

                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select CSV File')
                        ]),

                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '10px',
                            'textAlign': 'center',
                            'marginBottom': '20px'
                        },

                        multiple=False
                    ),

                    html.Div(id='preview-table'),

                    dbc.Button(
                        "Run Analysis",
                        id="run-analysis-btn",
                        color="primary",
                        className="mt-3"
                    )

                ])
            ]),

            html.Hr(),

            # Results
            dbc.Row([
                dbc.Col([
                    html.Div(id='results-section')
                ])
            ])

        ], fluid=True, className="p-4")

    ]
)



# Theme Callback

@dash_app.callback(
    Output("theme-container", "style"),
    Output("main-title", "style"),
    Output("subtitle", "style"),
    Input("theme-toggle", "value")
)
def toggle_theme(is_dark):

    if is_dark:

        container_style = {
            "backgroundColor": "#121212",
            "minHeight": "100vh",
            "color": "white"
        }

        title_style = {
            "color": "#4DA3FF",
            "fontWeight": "bold",
            "marginTop": "20px"
        }

        subtitle_style = {
            "color": "#CCCCCC",
            "fontSize": "18px"
        }

    else:

        container_style = {
            "backgroundColor": "white",
            "minHeight": "100vh",
            "color": "black"
        }

        title_style = {
            "color": "#1565C0",
            "fontWeight": "bold",
            "marginTop": "20px"
        }

        subtitle_style = {
            "color": "#5F6368",
            "fontSize": "18px"
        }

    return container_style, title_style, subtitle_style


@dash_app.callback(
    Output('loading-status', 'children'),
    Input('run-analysis-btn', 'n_clicks'),
    prevent_initial_call=True
)
def show_loading_text(n_clicks):
    if not n_clicks:
        return ""
    return "Running analysis, please wait..."

# Upload Preview Callback

@dash_app.callback(
    Output('preview-table', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_output(contents, filename):

    if contents is not None:

        sample_df = pd.DataFrame({
            'claim_id': [
                'CLM-1001',
                'CLM-1002',
                'CLM-1003'
            ]
        })

        return html.Div([

            html.H5(f"Uploaded File: {filename}"),

            dash_table.DataTable(
                data=sample_df.to_dict('records'),

                columns=[
                    {'name': col, 'id': col}
                    for col in sample_df.columns
                ],

                style_table={
                    'overflowX': 'auto'
                },

                style_header={
                    'backgroundColor': '#1565C0',
                    'color': 'white',
                    'fontWeight': 'bold'
                },

                style_cell={
                    'padding': '10px',
                    'textAlign': 'left'
                }
            )

        ])

    return html.Div(
        "No CSV uploaded. You can still analyze a single claim ID."
    )



# Analysis Callback

@dash_app.callback(
    Output('results-section', 'children'),
    Output('loading-status', 'children'),
    Input('run-analysis-btn', 'n_clicks'),
    State('single-claim-input', 'value'),
    State('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def run_analysis(n_clicks, single_claim, contents, filename):
    if not n_clicks:
        return "", ""

    if single_claim:
        claim_ids = [single_claim.strip()]
    elif contents:
        df = parse_csv(contents)
        claim_ids = df['claim_id'].tolist()
    else:
        return html.P("Please enter a claim ID or upload a CSV."), ""

    # Rule check
    rule_results = run_rule_check(claim_ids)
    passed       = rule_results["passed"]
    failed       = rule_results["failed"]

    # ML scoring
    if passed:
        ml_results, xgb_model, features_df = run_ml_scoring(passed)
    else:
        ml_results, xgb_model, features_df = {}, None, pd.DataFrame()

    # SHAP for high risk claims only
    high_risk_ids = [
        cid for cid in passed
        if ml_results.get(cid, {}).get("risk_label") == "HIGH"
    ]

    if high_risk_ids and xgb_model is not None:
        high_risk_df = features_df[features_df["claim_id"].isin(high_risk_ids)].reset_index(drop=True)
        shap_results = run_shap(xgb_model, high_risk_df)
    else:
        shap_results = {}

    # RAG for high risk claims
    if shap_results:
        rag_results = run_rag(shap_results)
    else:
        rag_results = {}

    # AI Agent summaries
    ai_summaries = run_ai_agent(
        claim_ids    = claim_ids,
        passed       = passed,
        failed       = failed,
        ml_results   = ml_results,
        shap_results = shap_results,
        rag_results  = rag_results
    )

    cards = []

    # RULE FAIL cards
    for claim_id, failures in failed.items():
        ai_summary = ai_summaries.get(claim_id, "")
        card = dbc.Card(
            dbc.CardBody([
                html.H3(claim_id, style={'fontWeight': 'bold', 'color': '#1565C0'}),
                get_badge("RULE FAIL"),
                html.Div([
                    html.B('Rule Failures:'),
                    html.Ul([html.Li(f) for f in failures])
                ]),
                html.Hr(),
                html.Div([
                    html.B('AI Recommendation:'),
                    html.P(ai_summary)
                ])
            ]),
            style={'marginBottom': '20px', 'borderRadius': '12px',
                   'boxShadow': '0px 2px 8px rgba(0,0,0,0.08)'}
        )
        cards.append(card)

    # PASSED claims cards
    for claim_id in passed:
        ml            = ml_results.get(claim_id, {})
        risk_score    = ml.get("risk_score", "N/A")
        risk_label    = ml.get("risk_label", "N/A")
        shap          = shap_results.get(claim_id, {})
        reason_1      = shap.get("reason_1", None)
        reason_2      = shap.get("reason_2", None)
        rag           = rag_results.get(claim_id, {})
        policy_source = rag.get("policy_source", None)
        policy_text   = rag.get("policy_text", None)
        ai_summary    = ai_summaries.get(claim_id, "")

        reasons_section = html.Div([
            html.B('Reasons:'),
            html.Ul([
                html.Li(r) for r in [reason_1, reason_2] if r
            ])
        ]) if reason_1 else html.P(
            "No significant risk factors detected.",
            style={'color': 'gray'}
        )

        policy_section = html.Div([
            html.P([html.B('Policy Violated: '), html.I(policy_source)]),
            html.P(policy_text, style={'fontSize': '12px', 'color': 'gray'})
        ]) if policy_source else html.P(
            "No policy violation detected.",
            style={'color': 'gray'}
        )

        card = dbc.Card(
            dbc.CardBody([
                html.H3(claim_id, style={'fontWeight': 'bold', 'color': '#1565C0'}),
                get_badge(risk_label),
                html.P([html.B('Risk Score: '), str(risk_score)]),
                reasons_section,
                html.Hr(),
                policy_section,
                html.Hr(),
                html.Div([
                    html.B('AI Recommendation:'),
                    html.P(ai_summary)
                ])
            ]),
            style={'marginBottom': '20px', 'borderRadius': '12px',
                   'boxShadow': '0px 2px 8px rgba(0,0,0,0.08)'}
        )
        cards.append(card)

    return html.Div(cards), ""



# Run App

if __name__ == '__main__':
    dash_app.run(debug=True)