{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "df = pd.DataFrame(\n",
    "    {\n",
    "        \"52WeekLow\": [1.21, 0.2006, 0.161, 0.1255, 1.07, 1.46, 1.16, 1.12, 1.82, 0.27],\n",
    "        \"ClosingPrice\": [3.15, 0.21, 0.19, 0.13, 1.73, 3.0, 1.5, 2.98, 2.09, 1.07],\n",
    "        \"52WeekHigh\": [21.0, 13.25, 1.75, 3.45, 5.4, 7.84, 8.7, 71.5, 6.064, 1.75],\n",
    "    }\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "2024-03-05 11:16:56.520 \n",
      "  \u001b[33m\u001b[1mWarning:\u001b[0m to view this Streamlit app on a browser, run it with the following\n",
      "  command:\n",
      "\n",
      "    streamlit run c:\\Users\\ptpedfilven\\AppData\\Local\\anaconda3\\envs\\bioinformatics\\Lib\\site-packages\\ipykernel_launcher.py [ARGUMENTS]\n"
     ]
    },
    {
     "data": {
      "text/plain": [
       "DeltaGenerator()"
      ]
     },
     "execution_count": 8,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "import streamlit as st\n",
    "s = (\n",
    "    df.style.hide(axis=0)\n",
    "        .format({\"ClosingPrice\": \"${:.2f}\"}, precision=2)\n",
    "        .set_properties(subset=[\"ClosingPrice\"], **{\"text-align\": \"right\"})\n",
    ")\n",
    "\n",
    "for r, (l, h) in enumerate(zip(df[\"52WeekLow\"], df[\"52WeekHigh\"])):\n",
    "    s = s.bar(\n",
    "        subset=pd.IndexSlice[r, \"ClosingPrice\"],\n",
    "        vmin=l, vmax=h,\n",
    "        color=\"lightgreen\"\n",
    "    )\n",
    "\n",
    "st.markdown(s.to_html(), unsafe_allow_html=True)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "bioinformatics",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.1"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
