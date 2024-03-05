import pandas as pd
import streamlit as st 

df = pd.DataFrame(
    {
        "52WeekLow": [1.21, 0.2006, 0.161, 0.1255, 1.07, 1.46, 1.16, 1.12, 1.82, 0.27],
        "ClosingPrice": [3.15, 0.21, 0.19, 0.13, 1.73, 3.0, 1.5, 2.98, 2.09, 1.07],
        "52WeekHigh": [21.0, 13.25, 1.75, 3.45, 5.4, 7.84, 8.7, 71.5, 6.064, 1.75],
    }
)


s = (
    df.style.hide(axis=0)
        .format({"ClosingPrice": "${:.2f}"}, precision=2)
        .set_properties(subset=["ClosingPrice"], **{"text-align": "right"})
)

for r, (l, h) in enumerate(zip(df["52WeekLow"], df["52WeekHigh"])):
    if r >1:
        s = s.bar(
            subset=pd.IndexSlice[r, "ClosingPrice"],
            vmin=l, vmax=h,
            color="lightgreen"
        )
    elif r <=1:
        s = s.bar(
            subset=pd.IndexSlice[r, "ClosingPrice"],
            vmin=l, vmax=h,
            color="red"
        )

st.markdown(s.to_html(), unsafe_allow_html=True)