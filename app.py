import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import time

# Page config MUST be the first Streamlit command
st.set_page_config(
    page_title="BeachBot ULTRA",
    page_icon="🍓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Password protection
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["DASHBOARD_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("""
        <style>
        .password-box {
            background: #003b6f;
            padding: 2rem;
            border-radius: 10px;
            border: 2px solid #fff200;
            max-width: 400px;
            margin: 100px auto;
            text-align: center;
        }
        .password-box h2 {
            color: #fff200 !important;
            margin-bottom: 1rem;
        }
        .password-box p {
            color: white;
            margin-bottom: 2rem;
        }
        </style>
        <div class="password-box">
            <h2>🍓 BeachBot ULTRA</h2>
            <p>Enter password to access dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        st.text_input("Password", type="password", on_change=password_entered, key="password", label_visibility="collapsed")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("""
        <style>
        .password-box {
            background: #003b6f;
            padding: 2rem;
            border-radius: 10px;
            border: 2px solid #ff3333;
            max-width: 400px;
            margin: 100px auto;
            text-align: center;
        }
        .password-box h2 {
            color: #fff200 !important;
            margin-bottom: 1rem;
        }
        .password-box p {
            color: #ff3333;
            margin-bottom: 2rem;
        }
        </style>
        <div class="password-box">
            <h2>🍓 BeachBot ULTRA</h2>
            <p>❌ Incorrect password</p>
        </div>
        """, unsafe_allow_html=True)
        st.text_input("Password", type="password", on_change=password_entered, key="password", label_visibility="collapsed")
        return False
    return True

if not check_password():
    st.stop()

# Custom CSS for ultra theme
st.markdown("""
<style>
    .stApp { background: #2c2c2c !important; }
    section[data-testid="stSidebar"] { background: #1e1e1e !important; border-right: 2px solid #fff200; }
    
    .beach-header {
        background: #003b6f;
        padding: 1rem 2rem;
        border-radius: 0;
        margin: -1rem -1rem 2rem -1rem;
        border-bottom: 4px solid #fff200;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
    }
    
    .header-drink {
        width: 60px;
        height: 60px;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3));
        animation: sway 3s ease-in-out infinite;
    }
    
    @keyframes sway {
        0%, 100% { transform: rotate(-5deg); }
        50% { transform: rotate(5deg); }
    }
    
    .beach-header h1 {
        color: #fff200 !important;
        font-size: 3.5rem;
        text-shadow: 2px 2px 0px #002b4f;
        margin: 0;
        font-family: 'Arial Black', sans-serif;
    }
    
    .beach-header h3 {
        color: #ffffff !important;
        font-size: 1.2rem;
        font-style: italic;
        margin: 0.25rem 0 0 0;
        text-transform: uppercase;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #39ff14 !important;
        font-weight: 600 !important;
        text-shadow: 0 0 5px rgba(57, 255, 20, 0.3);
    }
    
    [data-testid="stMetricLabel"] {
        color: #39ff14 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        text-transform: uppercase;
    }
    
    [data-testid="stMetricValue"] {
        color: #fff200 !important;
        font-weight: 700 !important;
        font-size: 1.8rem !important;
    }
    
    .profit { color: #00ff00 !important; font-weight: bold; }
    .loss { color: #ff4444 !important; font-weight: bold; }
    .fee { color: #39ff14 !important; font-size: 0.8rem; }
    
    div[data-testid="stDataFrame"] {
        background: #1e1e1e !important;
        border: 1px solid #3a3a3a;
        border-radius: 5px;
    }
    
    .stDataFrame th {
        color: #39ff14 !important;
        background-color: #2a2a2a !important;
        border-bottom: 2px solid #fff200 !important;
    }
    
    .stDataFrame td {
        color: #e0e0e0 !important;
        background-color: #1e1e1e !important;
    }
    
    .footer {
        text-align: center;
        padding: 2rem 0.5rem 0.5rem;
        color: #39ff14;
        border-top: 2px solid #fff200;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Beach Header
st.markdown("""
<div class="beach-header">
    <img class="header-drink" src="https://cdn-icons-png.flaticon.com/512/2935/2935448.png" alt="Strawberry Margarita">
    <div class="header-text">
        <h1>BeachBot ULTRA</h1>
        <h3>HIGH-FREQUENCY POLYMARKET TRADING</h3>
    </div>
    <img class="header-drink" src="https://cdn-icons-png.flaticon.com/512/2935/2935448.png" alt="Strawberry Margarita">
</div>
""", unsafe_allow_html=True)

# Database path
# Database path - handle cloud vs local
import tempfile

# Try local path first
local_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "copybot.sqlite")
cloud_path = "/mount/src/copybot.sqlite"

if os.path.exists(local_path):
    DB_PATH = local_path
    st.info("📁 Using local database")
elif os.path.exists(cloud_path):
    DB_PATH = cloud_path
    st.info("☁️ Using cloud database")
else:
    st.info("🌊 BeachBot ULTRA - Fresh Start March 2, 2026")
    # Create a temporary database for demo
    demo_db = tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False)
    DB_PATH = demo_db.name
    # Initialize empty tables with correct schema
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ledger (
            ts INTEGER,
            token_id TEXT,
            condition_id TEXT,
            action TEXT,
            price REAL,
            size REAL,
            usd REAL,
            note TEXT,
            source TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS my_positions (
            token_id TEXT PRIMARY KEY,
            condition_id TEXT,
            entry_price REAL,
            size REAL,
            entry_time INTEGER,
            status TEXT DEFAULT 'ACTIVE'
        )
    """)
    # Insert clean start message only - no demo data
    conn.execute("""
        INSERT INTO ledger (ts, action, price, size, usd, note) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (int(time.time()), 'INFO', 0, 0, 0, 'BeachBot ULTRA - Fresh Start March 2, 2026'))
    conn.commit()
    conn.close()

    conn = sqlite3.connect(DB_PATH)
    
    # ===== TOP METRICS ROW =====
    st.subheader("📊 ULTRA METRICS")
    
    # Get all time stats
    all_time = pd.read_sql_query("""
        SELECT 
            COUNT(*) as total_trades,
            SUM(CASE WHEN action='BUY' THEN usd ELSE 0 END) as total_bought,
            SUM(CASE WHEN action='SELL' THEN usd ELSE 0 END) as total_sold,
            SUM(CASE WHEN action='REDEEM' THEN usd ELSE 0 END) as total_won,
            SUM(CASE WHEN action='EXPIRE' THEN usd ELSE 0 END) as total_lost
        FROM ledger
    """, conn).iloc[0]
    
    # Get fee stats (from notes column)
    fee_data = pd.read_sql_query("""
        SELECT note FROM ledger WHERE note LIKE '%fee:%'
    """, conn)
    
    total_fees = 0
    for note in fee_data['note']:
        try:
            fee_str = note.split('fee:')[1].split('bps')[0]
            total_fees += float(fee_str)
        except:
            pass
    
    # Calculate P&L
    total_profit = (all_time['total_won'] or 0) - (all_time['total_lost'] or 0)
    win_rate = ( (all_time['total_won'] or 0) / ((all_time['total_won'] or 0) + (all_time['total_lost'] or 0)) * 100 ) if ((all_time['total_won'] or 0) + (all_time['total_lost'] or 0)) > 0 else 0
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("💰 Total P&L", f"${total_profit:,.2f}")
    col2.metric("📈 Win Rate", f"{win_rate:.1f}%")
    col3.metric("🔄 Total Trades", f"{all_time['total_trades']}")
    col4.metric("💸 Total Fees", f"{total_fees} bps")
    col5.metric("🏆 Wins", f"${all_time['total_won'] or 0:,.2f}")
    
    st.markdown("---")
    
    # ===== PROFIT CHART =====
    st.subheader("📈 Profit/Loss Over Time")
    
    daily_pnl = pd.read_sql_query("""
        SELECT 
            date(datetime(ts, 'unixepoch')) as day,
            SUM(CASE WHEN action='REDEEM' THEN usd ELSE 0 END) as won,
            SUM(CASE WHEN action='EXPIRE' THEN usd ELSE 0 END) as lost
        FROM ledger
        WHERE ts > strftime('%s', 'now', '-30 days')
        GROUP BY day
        ORDER BY day
    """, conn)
    
    if not daily_pnl.empty:
        daily_pnl['profit'] = daily_pnl['won'] - daily_pnl['lost']
        fig = px.bar(daily_pnl, x='day', y='profit', 
                     title='Daily P&L - Last 30 Days',
                     color=daily_pnl['profit'] > 0,
                     color_discrete_map={True: '#39ff14', False: '#ff4444'})
        fig.update_layout(
            plot_bgcolor='#1e1e1e',
            paper_bgcolor='#1e1e1e',
            font_color='#39ff14',
            title_font_color='#fff200'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No P&L data available")
    
    # ===== ACTIVE POSITIONS WITH P&L =====
    st.subheader("📊 Active Positions with Real-time P&L")
    
    positions = pd.read_sql_query("""
        SELECT 
            token_id,
            entry_price,
            size,
            datetime(entry_time, 'unixepoch') as entry_time,
            (SELECT price FROM (
                SELECT ts, price FROM ledger WHERE token_id = my_positions.token_id AND action='BUY' ORDER BY ts DESC LIMIT 1
            )) as current_price
        FROM my_positions 
        WHERE status = 'ACTIVE'
        ORDER BY size DESC
    """, conn)
    
    if not positions.empty:
        positions['value'] = positions['size'] * positions['entry_price']
        positions['current_value'] = positions['size'] * positions['current_price'].fillna(positions['entry_price'])
        positions['pnl'] = positions['current_value'] - positions['value']
        positions['pnl_pct'] = (positions['pnl'] / positions['value'] * 100).round(1)
        
        # Color code P&L
        def color_pnl(val):
            return f'<span class="profit">+${val:,.2f}</span>' if val > 0 else f'<span class="loss">-${abs(val):,.2f}</span>'
        
        positions['pnl_display'] = positions.apply(lambda x: color_pnl(x['pnl']), axis=1)
        
        display_cols = ['token_id', 'size', 'entry_price', 'value', 'pnl_display', 'pnl_pct', 'entry_time']
        st.write(positions[display_cols].to_html(escape=False, index=False), unsafe_allow_html=True)
        
        total_exposure = positions['value'].sum()
        total_pnl = positions['pnl'].sum()
        
        col1, col2 = st.columns(2)
        col1.metric("💰 Total Exposure", f"${total_exposure:,.2f}")
        col2.metric("📈 Unrealized P&L", f"${total_pnl:,.2f}", delta=f"{total_pnl/total_exposure*100:.1f}%" if total_exposure > 0 else None)
    else:
        st.info("No active positions")
    
    st.markdown("---")
    
    # ===== RECENT TRADES WITH FEES =====
    st.subheader("📝 Recent Trades")
    
    trades = pd.read_sql_query("""
        SELECT 
            datetime(ts, 'unixepoch') as time,
            action,
            price,
            size,
            usd,
            note,
            CASE 
                WHEN note LIKE '%fee:%' THEN 
                    CAST(SUBSTR(note, INSTR(note, 'fee:')+4, INSTR(note, 'bps')-INSTR(note, 'fee:')-4) as INTEGER)
                ELSE 0 
            END as fee_bps
        FROM ledger 
        WHERE action IN ('BUY', 'SELL')
        ORDER BY ts DESC 
        LIMIT 25
    """, conn)
    
    if not trades.empty:
        # Format for display
        trades['fee_display'] = trades.apply(lambda x: f"{x['fee_bps']} bps" if x['fee_bps'] > 0 else "", axis=1)
        trades['action'] = trades['action'].apply(lambda x: f"🔴 {x}" if x == 'BUY' else f"🟢 {x}")
        trades['usd'] = trades['usd'].apply(lambda x: f"${x:,.2f}")
        
        st.dataframe(trades[['time', 'action', 'price', 'size', 'usd', 'fee_display']], use_container_width=True)
    else:
        st.info("No recent trades")
    
    # ===== PERFORMANCE METRICS =====
    st.markdown("---")
    st.subheader("🎯 Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Average win/loss
    avg_stats = pd.read_sql_query("""
        SELECT 
            AVG(CASE WHEN action='REDEEM' THEN usd END) as avg_win,
            AVG(CASE WHEN action='EXPIRE' THEN usd END) as avg_loss,
            COUNT(CASE WHEN action='REDEEM' THEN 1 END) as wins,
            COUNT(CASE WHEN action='EXPIRE' THEN 1 END) as losses
        FROM ledger
    """, conn).iloc[0]
    
    col1.metric("🏆 Avg Win", f"${avg_stats['avg_win']:,.2f}" if avg_stats['avg_win'] else "$0")
    col2.metric("💔 Avg Loss", f"${avg_stats['avg_loss']:,.2f}" if avg_stats['avg_loss'] else "$0")
    col3.metric("🎯 Win/Loss Ratio", f"{(avg_stats['avg_win']/avg_stats['avg_loss']):.2f}" if avg_stats['avg_win'] and avg_stats['avg_loss'] else "N/A")
    col4.metric("📊 Total Events", f"{avg_stats['wins'] + avg_stats['losses']}")
    
    # Market filter stats
    market_stats = pd.read_sql_query("""
        SELECT note FROM ledger WHERE note LIKE '%preferred%' OR note LIKE '%filter%'
    """, conn)
    
    if not market_stats.empty:
        st.info(f"🎯 Market filters active - {len(market_stats)} filtered trades")
    
    conn.close()
    
except Exception as e:
    st.error(f"Error: {e}")
    st.exception(e)

# Footer
st.markdown("""
<div class="footer">
    🌊 ULTRA MODE • WebSocket • Fee-Aware • {} • 🏖️
</div>
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)
