import streamlit as st
import requests
import json
from datetime import datetime
from io import BytesIO
import zipfile

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="Invoice Reimbursement System", layout="wide")

st.title("🧾 Invoice Reimbursement System")
st.markdown("An intelligent system for analyzing and querying employee reimbursement invoices.")

# Sidebar Navigation
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", ["📤 Upload & Analyze", "💬 Chatbot Query"])

# ========== SECTION 1: Upload & Analyze ==========
if section == "📤 Upload & Analyze":
    st.header("📄 Upload Policy and Invoices for Analysis")
    with st.form(key="upload_form"):
        col1, col2 = st.columns(2)
        with col1:
            policy_pdf = st.file_uploader("Upload HR Reimbursement Policy (PDF)", type=["pdf"])
        with col2:
            invoice_zip = st.file_uploader("Upload Employee Invoice ZIP", type=["zip"])

        employee_name = st.text_input("Employee Name")
        submit_button = st.form_submit_button("🔍 Analyze Invoices")

    if submit_button:
        if not policy_pdf or not invoice_zip or not employee_name.strip():
            st.error("Please provide all required inputs.")
        else:
            with st.spinner("Processing invoices..."):
                files = {
                    "policy_pdf": ("policy.pdf", policy_pdf, "application/pdf"),
                    "invoices_zip": ("invoices.zip", invoice_zip, "application/zip"),
                }
                data = {"employee_name": employee_name.strip()}
                try:
                    res = requests.post(f"{API_BASE}/analyze/upload", files=files, data=data)
                    res.raise_for_status()
                    response = res.json()

                    # Success check based on presence of analysis_results
                    if "analysis_results" in response:
                        st.success("✅ Invoices analyzed and stored successfully!")
                        st.markdown(f"**👤 Employee Name:** `{response['employee_name']}`")
                        st.markdown(f"**📄 Policy Summary Preview:**\n```{response['policy_summary'][:500]}...```")
                        st.markdown(f"**📦 Invoices Processed:** `{response.get('num_invoices', 0)}`")

                        st.markdown("### 🧾 Detailed Invoice Analysis")
                        for invoice_name, result in response["analysis_results"].items():
                            status_emoji = {
                                "Fully Reimbursed": "✅",
                                "Partially Reimbursed": "🟡",
                                "Declined": "❌"
                            }.get(result["status"], "📄")
                            with st.expander(f"{status_emoji} {invoice_name}"):
                                st.markdown(f"**Status:** `{result['status']}`")
                                st.markdown(f"**Reason:**\n{result['reason']}")
                    else:
                        st.error("⚠️ Analysis failed or malformed response.")
                        st.json(response)
                except Exception as e:
                    st.error(f"🚨 API Error: {e}")

# ========== SECTION 2: Chatbot ==========
elif section == "💬 Chatbot Query":
    st.header("🤖 Ask a Question about Reimbursements")

    with st.expander("🔍 Optional Filters"):
        col1, col2, col3 = st.columns(3)
        employee_name = col1.text_input("Employee Name (optional)")
        invoice_date = col2.date_input("Invoice Date (optional)", format="YYYY-MM-DD")
        status = col3.selectbox("Reimbursement Status", ["", "Fully Reimbursed", "Partially Reimbursed", "Declined"])

    query = st.text_area("Ask a question (e.g., Why was Sonya's invoice rejected?)", height=100)

    if st.button("💬 Submit Query"):
        if not query.strip():
            st.warning("⚠️ Please enter a valid query.")
        else:
            filters = {}
            if employee_name.strip():
                filters["employee_name"] = employee_name.strip()
            if invoice_date:
                filters["date"] = invoice_date.strftime("%Y-%m-%d")
            if status:
                filters["status"] = status

            payload = {
                "query": query,
                "filters": filters
            }

            with st.spinner("💡 Querying the chatbot..."):
                try:
                    res = requests.post(f"{API_BASE}/chatbot/query", json=payload)
                    res.raise_for_status()
                    result = res.json()
                    st.markdown("### 📜 Response")
                    st.markdown(result.get("response_markdown", "_No response received._"))
                except Exception as e:
                    st.error(f"🚨 Chatbot Error: {e}")