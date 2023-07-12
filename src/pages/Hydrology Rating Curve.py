import streamlit as st
from auth_helpers import set_page_config
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

set_page_config("Hydrology Rating Curve Explorations", requires_auth=False)


@st.cache_data
def fit_power_law(stage, discharge):
    params, params_covariance = curve_fit(power_law, stage, discharge)
    stage_fit = np.linspace(stage.min(), stage.max(), 100)
    discharge_fit = power_law(stage_fit, params[0], params[1])
    label="Fit: a=%5.3f, b=%5.3f" % tuple(params)
    return params, stage_fit, discharge_fit, label


@st.cache_data
def fit_polynomial(stage, discharge, fit_degree: int):
    params = np.polyfit(stage, discharge, fit_degree)

    # Generate a polynomial function from the fit parameters
    polynomial = np.poly1d(params)

    # Generate a range of stage values and calculate the corresponding discharge values using the polynomial function
    stage_fit = np.linspace(stage.min(), stage.max(), 100)
    discharge_fit = polynomial(stage_fit)
    label = 'Fit: %s' % polynomial
    return params, stage_fit, discharge_fit, label


def main():
    # Assume some arbitrary stage and discharge values
    stage = np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0])  # e.g., in meters
    discharge = np.array([0.2, 0.8, 2.1, 4.0, 6.9, 10.5, 15.2, 21.0])  # e.g., in cubic meters per second

    fit_type = st.selectbox("fit-type", ("Power Law", "Polynomial Model"))
    if fit_type == "Power Law":
        params, stage_fit, discharge_fit, label = fit_power_law(stage, discharge)

    elif fit_type == "Polynomial Model":
        degree = st.number_input("fit-degree", min_value=2, value=2)
        params, stage_fit, discharge_fit, label = fit_polynomial(stage, discharge, fit_degree=degree)
    else:
        raise ValueError("Bad fit_type")

    plt.scatter(stage, discharge, label="Data")
    plt.plot(stage_fit, discharge_fit, label=label)
    plt.xlabel("Stage (m)")
    plt.ylabel("Discharge (m^3/s)")
    plt.legend(loc="best")
    st.pyplot(plt)


def power_law(x, a, b):
    return a * np.power(x, b)


main()
