import io
import math
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd

from sungan import SunganRiverWaterQualityAnalyzer

analyzer = SunganRiverWaterQualityAnalyzer()

st.set_page_config(page_title="Sungan River WQI", layout="wide")
st.markdown("<h1 style='color:#2dd4bf'>🌊 Sungan River Water Quality Analyzer</h1>", unsafe_allow_html=True)
st.markdown("Mathematical model predictions for parameters vs distance from mining")

# Sidebar controls
st.sidebar.header("Controls")
distance = st.sidebar.number_input("Distance from mining (km)", min_value=0.0, value=0.0, step=0.1, format="%.2f")
max_plot = st.sidebar.number_input("Plot max distance (km)", min_value=1.0, value=15.0, step=1.0, format="%.1f")
batch_text = st.sidebar.text_input("Batch distances (comma-separated)", value="")

# DENR standards below controls
st.sidebar.markdown("---")
st.sidebar.subheader("DENR Water Quality Standards")
for param, (std_min, std_max) in analyzer.standards.items():
    std_max_str = f"{std_max}" if std_max != float('inf') else "No max"
    st.sidebar.markdown(f"**{param}**: Min={std_min}, Max={std_max_str}")

if distance > 0:  # Only show predictions and plots if user entered a distance
    col1, col2 = st.columns([1, 2])

    with col1:
        # --- Overall WQI at the top ---
        preds = analyzer.predict_all_parameters(distance)
        total_wqi = 0.0
        for p, w in analyzer.weights.items():
            val = preds.get(p, 0)
            q = analyzer.get_q_value(p, val)
            total_wqi += q * w
        rating = analyzer.get_wqi_rating(total_wqi)
        st.metric("Overall WQI", f"{total_wqi:.2f}", delta=rating)

        # Prepare the data
        rows = []
        for param, val in preds.items():
            unit = "pH units" if param == "pH" else "NTU" if param == "turbidity" else "mg/L"
            status, sym = analyzer.assess_parameter_quality(param, val)
            rows.append((param, f"{val:.3f}", unit, f"{sym} {status}"))

        # Convert to DataFrame with proper column names
        df = pd.DataFrame(rows, columns=["Parameter", "Value", "Unit", "Status"])

        # Display in Streamlit
        st.dataframe(df)


        # --- Key Issues Section ---
        st.subheader("Key Issues")
        issues = []
        
        for param, val in preds.items():
            std_min, std_max = analyzer.standards.get(param, (None, None))
            if std_min is None:
                continue  # No standard defined
            
            # Check low/high/out-of-range
            if val < std_min:
                issues.append(f"Low {param} ({val:.3f})")
            elif val > std_max:
                issues.append(f"High {param} ({val:.3f})")
        
        if issues:
            for issue in issues:
                st.markdown(f"- {issue}")
        else:
            st.markdown("✅ No major issues detected based on predicted parameters.")




        # Report area
        st.subheader("Report / Log")
        report_text = st.empty()
        initial_report = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nDistance: {distance} km\n"
        for p, v in preds.items():
            initial_report += f"  {p:<10}: {v:.4f}\n"
        initial_report += f"Overall WQI: {total_wqi:.2f} --> {rating}\n"
        report_buffer = st.text_area("Report", value=initial_report, height=300)

        # Export buttons
        col_export1, col_export2 = st.columns(2)
        with col_export1:
            if st.button("Export as TXT"):
                b = report_buffer.encode("utf-8")
                st.download_button("Download TXT", b, file_name="sungan_report.txt", mime="text/plain")
        with col_export2:
            if st.button("Save as PDF"):
                try:
                    from reportlab.lib.pagesizes import A4
                    from reportlab.pdfgen import canvas as pdfcanvas
                    from reportlab.lib.units import mm

                    buffer = io.BytesIO()
                    page_size = A4
                    c = pdfcanvas.Canvas(buffer, pagesize=page_size)
                    width, height = page_size
                    left_margin = 20 * mm
                    top_margin = 20 * mm
                    y = height - top_margin
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(left_margin, y, "Sungan River Water Quality Analysis Report")
                    y -= 12 * mm
                    c.setFont("Helvetica", 9)
                    c.drawString(left_margin, y, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    y -= 8 * mm
                    c.setFont("Helvetica", 10)
                    lines = report_buffer.splitlines()
                    line_height = 10
                    max_chars_per_line = 100
                    for line in lines:
                        while len(line) > max_chars_per_line:
                            part = line[:max_chars_per_line]
                            c.drawString(left_margin, y, part)
                            y -= line_height
                            line = line[max_chars_per_line:]
                            if y < 40 * mm:
                                c.showPage()
                                c.setFont("Helvetica", 10)
                                y = height - top_margin
                        c.drawString(left_margin, y, line)
                        y -= line_height
                        if y < 40 * mm:
                            c.showPage()
                            c.setFont("Helvetica", 10)
                            y = height - top_margin
                    c.save()
                    buffer.seek(0)
                    st.download_button("Download PDF", buffer, file_name="sungan_report.pdf", mime="application/pdf")
                except Exception as e:
                    st.warning("reportlab not installed or PDF generation failed — exporting TXT instead.")
                    b = report_buffer.encode("utf-8")
                    st.download_button("Download TXT", b, file_name="sungan_report.txt", mime="text/plain")

    with col2:
        st.subheader("Parameter Trends")
        distances = np.linspace(1, max_plot, 120)
        params = ['pH', 'turbidity', 'TDS', 'iron', 'phosphate', 'nitrate']
        fig, axs = plt.subplots(2, 3, figsize=(10, 6), constrained_layout=True)
        axs = axs.flatten()
        for i, param in enumerate(params):
            values = [analyzer.predict_all_parameters(d)[param] for d in distances]
            axs[i].plot(distances, values, linewidth=2)
            axs[i].set_title(param)
            axs[i].grid(alpha=0.25)
            if param in analyzer.standards:
                std_min, std_max = analyzer.standards[param]
                if std_max != float('inf'):
                    axs[i].axhline(std_max, linestyle='--', color='r', label='Max Std')
                if std_min > 0:
                    axs[i].axhline(std_min, linestyle=':', color='g', label='Min Std')
            axs[i].legend(fontsize='small')
        st.pyplot(fig)

    # Batch panel at page bottom
    st.markdown("---")
    st.header("Batch analysis")
    if st.button("Run batch from sidebar"):
        text = batch_text.strip()
        if not text:
            st.info("Enter batch distances in the sidebar")
        else:
            parts = [p.strip() for p in text.split(",") if p.strip()]
            lines = []
            for p in parts:
                try:
                    d = float(p)
                    if d <= 0:
                        continue
                    preds = analyzer.predict_all_parameters(d)
                    total_wqi = 0.0
                    for pr, w in analyzer.weights.items():
                        total_wqi += analyzer.get_q_value(pr, preds[pr]) * w
                    lines.append((d, total_wqi, analyzer.get_wqi_rating(total_wqi)))
                except Exception:
                    continue
            st.table(lines)

