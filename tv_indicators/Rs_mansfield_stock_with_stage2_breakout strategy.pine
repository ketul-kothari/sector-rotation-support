//@version=6
strategy(" RS Mansfield & Stage 2 Breakout Alerts Strategy", overlay=true, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=95)

// ==========================================
// 1. INPUT DEFINITIONS
// ==========================================
grp_gen = "General Settings"
bench           = input.string("NSE:CNX500", "Benchmark", group=grp_gen)
multiplier      = input.float(10.0, "Mansfield Multiplier", group=grp_gen)

grp_s2 = "Stage 2 Parameters"
slope_weeks     = input.int(4, "Slope Length (Weeks)", group=grp_s2)
slope_thresh    = input.float(0.30, "Slope Threshold", group=grp_s2)
rs_thresh       = input.float(0.0, "RS threshold", group=grp_s2)

grp_strat = "Strategy Risk Settings"
sl_pct          = input.float(8.0, "Stop Loss (%)", group=grp_strat, step=0.5)

// ==========================================
// 2. TIMEFRAME ENGINE
// ==========================================
int final_rs_len    = 52
int final_slope_len = slope_weeks 
int final_stage2_ma = 30

if timeframe.isdaily
    final_rs_len    := 252 
    final_slope_len := slope_weeks * 5 
    final_stage2_ma := 150 
else if timeframe.isweekly
    final_rs_len    := 52  
    final_slope_len := slope_weeks     
    final_stage2_ma := 30  
else if timeframe.ismonthly
    final_rs_len    := 12  
    final_slope_len := math.max(1, math.round(slope_weeks / 4.333)) 
    final_stage2_ma := 7   

// ==========================================
// 3. DATA FETCHING & MATH
// ==========================================
bench_c       = request.security(bench, timeframe.period, close)
stage2_ma_val = ta.sma(close, final_stage2_ma) 

ratio       = close / nz(bench_c, 1)
m_rs        = ((ratio / ta.sma(ratio, final_rs_len)) - 1) * multiplier
rs_slope    = (m_rs - m_rs[final_slope_len]) / slope_weeks

// ==========================================
// 4. BREAKOUT LOGIC
// ==========================================
bool s2_rs_pass     = m_rs > rs_thresh
bool s2_slope_pass  = rs_slope > slope_thresh
bool s2_price_pass  = close > stage2_ma_val
bool s2_ma_rising   = stage2_ma_val > stage2_ma_val[1]

bool s2_condition   = s2_price_pass and (s2_rs_pass or s2_slope_pass) and s2_ma_rising
// Strict Trigger: True now, False on the previous bar
bool s2_trigger     = s2_condition and not s2_condition[1]

// ==========================================
// 5. STRATEGY EXECUTION (FIXED STATE)
// ==========================================
var float sl_price = na

// --- ENTRY ---
if s2_trigger
    strategy.entry("S2_Long", strategy.long)

// --- STATEFUL STOP LOSS ---
// Calculate Stop Loss ONLY once on the exact bar the position actually fills
if strategy.position_size > 0 and strategy.position_size[1] == 0
    sl_price := strategy.position_avg_price * (1 - (sl_pct / 100))

// Reset the stop loss variable when flat
if strategy.position_size == 0
    sl_price := na

// --- EXITS ---
if strategy.position_size > 0
    // 1. Percentage Stop Loss
    strategy.exit("8% SL", from_entry="S2_Long", stop=sl_price)
    
    // 2. Moving Average Breakdown
    bool ma_breakdown = close < stage2_ma_val
    if ma_breakdown
        strategy.close("S2_Long", comment="MA Breakdown")

// ==========================================
// 6. VISUALS (Overlay on Price Chart)
// ==========================================
plot(stage2_ma_val, "Stage 2 MA", color=color.blue, linewidth=2)
plot(strategy.position_size > 0 ? sl_price : na, "Active Stop Loss", color=color.red, style=plot.style_linebr, linewidth=1)

plotshape(s2_trigger, title="Breakout Entry", style=shape.triangleup, location=location.belowbar, color=color.new(color.green, 0), size=size.small)
plotshape(strategy.position_size > 0 and close < stage2_ma_val, title="MA Exit", style=shape.triangledown, location=location.abovebar, color=color.new(color.red, 0), size=size.small)