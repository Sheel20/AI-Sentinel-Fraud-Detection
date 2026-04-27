import streamlit as st
import pandas as pd # Added for better ledger handling
from langchain_core.messages import HumanMessage
from datetime import datetime

# Initialize session state for the Ledger at the very top
if "demo_log" not in st.session_state:
    st.session_state.demo_log = []

# Try to import graph logic
try:
    from graph_logic import graph
except ImportError as e:
    st.error(f"⚠️ Critical Error: graph_logic.py not found or contains errors: {e}")
    st.stop()

# 1. Page Configuration
st.set_page_config(page_title="AI Sentinel | Fraud Engine", page_icon="🛡️", layout="wide")

# 2. Sidebar Branding
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=60)
    st.title("AI Sentinel")
    st.markdown("### National Hackathon 2026")
    st.info("System Status: **Live & Operational**")
    st.divider()
    
    st.subheader("🛠️ Control Panel")
    if st.button("🔄 Reset Session", use_container_width=True):
        st.session_state.demo_log = []
        st.rerun()
    
    st.divider()
    st.markdown("**Core Tech Stack:**\n- LangGraph\n- Llama 3.2\n- RAG (Behavioral Context)")

# 3. Main Interface Header
st.title("🛡️ Fraud Detection & Behavioral Analytics")
st.markdown("##### Agentic RAG System for Real-Time Transaction Verification")

# 4. User Input Area
user_input = st.text_area("Input Transaction Stream:", height=100, 
                          placeholder="Example: User 405 is sending ₹15,000 using a VPN...")

# 5. Execution Logic
if st.button("🚀 Execute Forensic Analysis", type="primary", use_container_width=True):
    if not user_input:
        st.warning("Please enter transaction details.")
    else:
        try:
            with st.status("🕵️ Investigating...", expanded=True) as status:
                # 1. Run Graph
                final_state = graph.invoke({"messages": [HumanMessage(content=user_input)]})
                
                # 2. Extract Data
                score = final_state.get("risk_score", 0.0)
                verdict = final_state.get("final_verdict", "PENDING")
                history = final_state.get("user_history", {"profile": {"user_id": "Unknown"}})
                reasoning = final_state.get("reasoning", [])
                
                # FIX: Append to Ledger so it shows up in the table below
                st.session_state.demo_log.append({
                    "Timestamp": datetime.now().strftime("%H:%M:%S"),
                    "User ID": history.get("profile", {}).get("user_id", "405"),
                    "Verdict": verdict.upper(),
                    "Risk Score": f"{int(score * 100)}%",
                    "Input": user_input[:50] + "..."
                })
                
                status.update(label="Analysis Complete", state="complete")

            # 3. Decision Result (Box Display)
            st.markdown("---")
            col1, col2, col3 = st.columns([1.5, 1, 1.5])

            with col1:
                st.subheader("Decision Result")
                display_verdict = str(verdict).strip().upper()
                
                if display_verdict == "APPROVED":
                    st.success("✅ Transaction Cleared")
                elif display_verdict == "BLOCKED":
                    st.error("🚫 Transaction Blocked")
                else:
                    st.warning("⏳ Pending Human Review")
            
            with col2:
                st.subheader("Risk Metrics")
                # Handle both 0.95 and 95 formats
                raw_score = final_state.get("risk_score",0.0)
                display_pct = min(int(raw_score * 100),100)
                
                st.metric(
                    label="Probability", 
                    value=f"{display_pct}%", 
                    delta="HIGH RISK" if raw_score >= 0.7 else "STABLE", 
                    delta_color="inverse" if raw_score >= 0.7 else "normal"
                )

            with col3:
                st.subheader("User Context")
                profile = history.get("profile", {})
                
                # Create a clean Profile Card
                with st.container(border=True):
                    st.markdown(f"👤 **User ID:** `{profile.get('user_id', '405')}`")
                    st.markdown(f"📍 **Home City:** `{profile.get('home_city', 'MUMBAI')}`")
                    st.markdown(f"📝 **Notes:** {profile.get('notes', 'N/A')}")
                    st.markdown("---")
                    st.caption("✅ Data retrieved from Behavioral RAG")
                    if verdict == "BLOCKED":
                      st.info("💡 **Analyst Action:** Fraud detected. Would you like to initiate a customer callback?")
                if st.button("📞 Trigger Secure Call", use_container_width=True):
                    st.toast("Connecting to User 405...", icon="📲")

            # 4. Technical Deep-Dive
            tab1, tab2 = st.tabs(["🧠 Agent Reasoning", "📊 System State"])
            with tab1:
                st.markdown("#### 🧠 Multi-Agent Analysis Trace")
                
                # Display reasoning items as "Alerts"
                for item in reasoning:
                    if "✅" in item:
                        st.success(item, icon="✔️")
                    elif "ℹ️" in item:
                        st.info(item, icon="ℹ️")
                    elif "⚠️" in item:
                        st.warning(item, icon="⚠️")
                    elif "🚨" in item or "❌" in item:
                        st.error(item, icon="🚨")

            with tab2:
                st.write("Full State Object (JSON):")
                # Filter out messages for a cleaner JSON view
                st.json({k: v for k, v in final_state.items() if k != "messages"})

        except Exception as e:
            st.error(f"Execution Error: {e}")

# 6. LIVE TRANSACTION LEDGER
if st.session_state.demo_log:
    st.divider()
    st.subheader("📜 System Audit Log (Live)")
    
    df = pd.DataFrame(st.session_state.demo_log)
    
    # Custom styling for the table
    def highlight_verdict(val):
        # Red for Blocked, Green for Approved
        color = '#ff4b4b' if val == "BLOCKED" else '#09ab3b'
        return f'background-color: {color}; color: white; font-weight: bold'

    # CHANGE: .applymap -> .map
    st.dataframe(
        df.style.map(highlight_verdict, subset=['Verdict']),
        use_container_width=True,
        hide_index=True
    )

st.divider()
st.caption("© 2026 AI Sentinel | Developed for National Technology Hackathon | Team Agentic Forge")