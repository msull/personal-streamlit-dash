from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from auth_helpers import set_page_config
from scipy.optimize import curve_fit

set_page_config("Water Data Exploration", requires_auth=False)


def calculate_rmse(y_actual, y_pred):
    return np.sqrt(np.mean((y_actual - y_pred) ** 2))


@dataclass
class FitResult:
    model: np.poly1d or callable
    stage_fit: np.ndarray
    discharge_fit: np.ndarray
    label: str
    rmse: float

    def predict(self, stage):
        return self.model(stage)


def fit_power_law(stage, discharge):
    params, _ = curve_fit(power_law, stage, discharge, maxfev=5000)
    model = lambda x: power_law(x, *params)
    stage_fit = np.linspace(stage.min(), stage.max(), 100)
    discharge_fit = model(stage_fit)
    label = f"Fit: a={params[0]:.3f}, b={params[1]:.3f}"
    rmse = calculate_rmse(discharge, model(stage))
    return FitResult(model, stage_fit, discharge_fit, label, rmse)


def fit_polynomial(stage, discharge, fit_degree: int):
    params = np.polyfit(stage, discharge, fit_degree)
    model = np.poly1d(params)
    stage_fit = np.linspace(stage.min(), stage.max(), 100)
    discharge_fit = model(stage_fit)
    label = f"Fit: {model}"
    rmse = calculate_rmse(discharge, model(stage))
    return FitResult(model, stage_fit, discharge_fit, label, rmse)


DATA_PATH = Path(__file__).parent.parent / "static_data" / "waterdata2008.tsv"


@st.cache_data
def load_water_data():
    df = pd.read_csv(DATA_PATH, sep="\t", dtype=str, low_memory=False)
    df = df.groupby(["begin_yr", "month_nu", "day_nu"], as_index=False).aggregate(list)
    df["date"] = pd.to_datetime(
        df[["begin_yr", "month_nu", "day_nu"]].rename(
            columns={"begin_yr": "year", "month_nu": "month", "day_nu": "day"}
        )
    )
    df[["discharge_rate", "stage_val"]] = df["mean_va"].apply(pd.Series)
    df["discharge_rate"] = df["discharge_rate"].astype(int)
    df["stage_val"] = df["stage_val"].astype(float)
    df = df.dropna(subset=["discharge_rate", "stage_val"])
    # Normalize the stage and discharge values
    df["stage_val_norm"] = (df["stage_val"] - df["stage_val"].min()) / (df["stage_val"].max() - df["stage_val"].min())
    df["discharge_rate_norm"] = (df["discharge_rate"] - df["discharge_rate"].min()) / (
        df["discharge_rate"].max() - df["discharge_rate"].min()
    )

    df = df.sort_values(by=["date"])

    return df


def main():
    st.title("Water Data Exploration")
    # Assume some arbitrary stage and discharge values
    water_data = load_water_data()
    # draw date select box
    options = [water_data.iloc[0]["date"].to_pydatetime(), water_data.iloc[-1]["date"].to_pydatetime()]

    slider_from, slider_to = st.slider("Dates", options[0], options[1], value=options)
    filter_from = pd.to_datetime(datetime.fromisoformat(slider_from.isoformat()))
    filter_to = pd.to_datetime(datetime.fromisoformat(slider_to.isoformat()) + timedelta(days=1))
    del slider_from
    del slider_to

    df = water_data
    water_data = df[(df["date"] >= filter_from) & (df["date"] <= filter_to)]

    stage = water_data["stage_val"].values
    discharge = water_data["discharge_rate"].values

    with st.expander("Data"):
        st.write("Data for USGS 12080010 DESCHUTES RIVER AT E ST BRIDGE AT TUMWATER, WA")
        st.write(
            "Sourced from https://waterdata.usgs.gov/nwis/dvstat?referred_module=sw&search_site_no=12080010&format=sites_selection_links"
        )
        st.dataframe(water_data[["date", "stage_val", "discharge_rate"]])

    with st.expander("Daily Stage and Discharge", expanded=True):
        chart_type = st.selectbox("View Option", ("Normalized", "Raw"), label_visibility="collapsed")

        fig = go.Figure()
        stage_key = "stage_val"
        discharge_key = "discharge_rate"
        if chart_type == "Normalized":
            stage_key += "_norm"
            discharge_key += "_norm"

        fig.add_trace(go.Bar(x=water_data["date"], y=water_data[stage_key], name="Stage", marker_color="blue"))

        fig.add_trace(
            go.Scatter(
                x=water_data["date"],
                y=water_data[discharge_key],
                name="Discharge",
                line=dict(color="red"),
                yaxis="y2",
            )
        )

        fig.update_layout(
            xaxis=dict(domain=[0.3, 0.7]),
            yaxis=dict(title="Stage (f)", titlefont=dict(color="blue"), tickfont=dict(color="blue")),
            yaxis2=dict(
                title="Discharge (f^3/s)",
                titlefont=dict(color="red"),
                tickfont=dict(color="red"),
                # anchor="free",
                overlaying="y",
                side="right",
                # position=1,
            ),
            legend=dict(
                yanchor="top", y=-0.3, xanchor="left", x=0.25  # adjust these as needed  # adjust these as needed
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Stage Vs Discharge", expanded=True):
        fit_type = st.selectbox("fit-type", ("Polynomial Model", "None", "Power Law"))
        model_fit = None
        if fit_type == "Power Law":
            model_fit = fit_power_law(stage, discharge)
        elif fit_type == "Polynomial Model":
            degree = st.number_input("fit-degree", min_value=2, max_value=5, value=2)
            model_fit = fit_polynomial(stage, discharge, fit_degree=degree)

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=stage, y=discharge, mode="markers", name="Data"))

        if model_fit is not None:
            fig.add_trace(
                go.Scatter(x=model_fit.stage_fit, y=model_fit.discharge_fit, mode="lines", name=model_fit.label)
            )

        # fig.update_layout(xaxis_title="Stage (f)", yaxis_title="Discharge (f^3/s)", title="Stage Level and Discharge")
        fig.update_layout(
            xaxis_title="Stage (f)",
            yaxis_title="Discharge (f^3/s)",
            title="Hydrology Rating Curve",
            legend=dict(
                yanchor="top", y=-0.3, xanchor="left", x=-0.1  # adjust these as needed  # adjust these as needed
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

        if model_fit is not None:
            st.metric("RMSE", model_fit.rmse)

    if model_fit:
        with st.expander("Rating Table", expanded=True):
            min_stage = float(water_data["stage_val"].min() // 5 * 5)  # nearest lower 5
            min_val = round(water_data["stage_val"].min(), 1)
            max_stage = float(water_data["stage_val"].max() // 5 * 5 + 5)  # nearest upper 5
            columns = iter(st.columns(2))
            with next(columns):
                start = st.number_input(
                    "Start Stage Level", min_value=min_stage - 25, max_value=max_stage + 25, value=min_val, step=0.1
                )
            with next(columns):
                stop = st.number_input(
                    "Stop Stage Level", min_value=min_stage - 25, max_value=max_stage + 25, value=max_stage, step=0.1
                )

            stages = np.arange(start, stop + 0.1, 0.1)
            discharges = model_fit.predict(stages)
            rating_table = pd.DataFrame({"Stage Level": stages, "Predicted Discharge": discharges})
            st.dataframe(rating_table)


def power_law(x, a, b):
    return a * np.power(x, b)


main()
