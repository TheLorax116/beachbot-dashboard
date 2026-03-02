import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Polymarket Bot", layout="wide")

st.title("📊 Polymarket Copy Trading Bot")
st.markdown("---")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "copybot.sqlite")

if not os.path.exists(DB_PATH):
    st.error(f"Database not found: {DB_PATH}")
    st.stop()

try:
    conn = sqlite3.connect(DB_PATH)
    
    # Show available tables
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
    st.sidebar.success(f"Tables: {', '.join(tables['name'].tolist())}")
    
    # SUMMARY METRICS
    st.subheader("📊 Summary")
    
    # Get counts by action type
    action_counts = pd.read_sql_query("""
        SELECT action, COUNT(*) as count, SUM(usd) as total 
        FROM ledger 
        GROUP BY action
    """, conn)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    buys = action_counts[action_counts['action'] == 'BUY']
    sells = action_counts[action_counts['action'] == 'SELL']
    redeems = action_counts[action_counts['action'] == 'REDEEM']
    expires = action_counts[action_counts['action'] == 'EXPIRE']
    
    col1.metric("📝 Total Trades", len(action_counts))
    col2.metric("🟢 Buys", buys['count'].iloc[0] if not buys.empty else 0)
    col3.metric("🔴 Sells", sells['count'].iloc[0] if not sells.empty else 0)
    col4.metric("🏆 Redeems", redeems['count'].iloc[0] if not redeems.empty else 0)
    col5.metric("💔 Expires", expires['count'].iloc[0] if not expires.empty else 0)
    
    col1.metric("💰 Total Bought", f"${buys['total'].iloc[0]:,.2f}" if not buys.empty else "$0")
    col2.metric("💵 Total Sold", f"${sells['total'].iloc[0]:,.2f}" if not sells.empty else "$0")
    col3.metric("🏆 Total Redeemed", f"${redeems['total'].iloc[0]:,.2f}" if not redeems.empty else "$0")
    
    st.markdown("---")
    
    # RECENT LEDGER
    st.subheader("📝 Recent Activity")
    ledger_df = pd.read_sql_query("""
        SELECT 
            datetime(ts, 'unixepoch') as time,
            action,
            price,
            size,
            usd,
            note
        FROM ledger 
        ORDER BY ts DESC 
        LIMIT 50
    """, conn)
    
    if not ledger_df.empty:
        st.dataframe(ledger_df, use_container_width=True)
    else:
        st.info("No ledger entries")
    
    st.markdown("---")
    
    # ACTIVE POSITIONS
    st.subheader("📈 Active Positions")
    positions_df = pd.read_sql_query("""
        SELECT 
            token_id,
            entry_price,
            size,
            datetime(entry_time, 'unixepoch') as entry_time
        FROM my_positions 
        WHERE status = 'ACTIVE'
        ORDER BY size DESC
    """, conn)
    
    if not positions_df.empty:
        positions_df['value'] = positions_df['size'] * positions_df['entry_price']
        st.dataframe(positions_df, use_container_width=True)
        st.metric("Total Exposure", f"${positions_df['value'].sum():,.2f}")
    else:
        st.info("No active positions")
    
    conn.close()
    
except Exception as e:
    st.error(f"Error: {e}")
    st.exception(e)

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
