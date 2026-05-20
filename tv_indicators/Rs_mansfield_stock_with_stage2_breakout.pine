//@version=6
indicator("RS Mansfield & Stage 2 Breakout Alerts", overlay=false, precision=2)

// --- 1. GENERAL INPUTS ---
bench           = input.string("NSE:CNX500", "Benchmark")
multiplier      = input.float(10.0, "Mansfield Multiplier")

// --- 2. ALERT PARAMETER INPUTS ---
slope_weeks     = input.int(4, "Stage 2: Slope Length (Weeks)") 
slope_thresh    = input.float(0.30, "Stage 2: Slope Threshold")
rs_thresh     = input.float(0, "Stage 2: RS threshold") 

// --- 3. BULLETPROOF TIMEFRAME ENGINE ---
// Defaults set to institutional weekly standards
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

// --- 4. DATA FETCHING & MATH ---
bench_c        = request.security(bench, timeframe.period, close)
stage2_ma_val  = ta.sma(close, final_stage2_ma) 

ratio       = close / nz(bench_c, 1)
m_rs        = ((ratio / ta.sma(ratio, final_rs_len)) - 1) * multiplier
rs_slope    = (m_rs - m_rs[final_slope_len]) / final_slope_len

// --- 5. LOGIC: STAGE 2 BREAKOUT (Green Star) ---
bool s2_rs_pass     = m_rs > rs_thresh
bool s2_slope_pass  = rs_slope > slope_thresh
bool s2_price_pass  = close > stage2_ma_val
bool s2_ma_rising   = stage2_ma_val > stage2_ma_val[1] // Safety: Ensure trend isn't declining

// Breakout logic: Price is above rising MA, and RS is positive OR strongly sloping
bool s2_condition   = s2_price_pass and (s2_rs_pass or s2_slope_pass) and s2_ma_rising
bool s2_trigger     = s2_condition and not s2_condition[1]

// --- 6. HIDDEN PLOTS FOR WATCHLIST ALERTS ---
plot(s2_trigger ? 1 : 0, title="Alert: Stage 2", display=display.none)

// --- 7. VISUALS & STYLING ---
z_plot = plot(0, "Zero Line", color=color.new(color.gray, 50), display=display.pane)
rs_plot = plot(m_rs, "Mansfield RS", color=color.rgb(135, 133, 133), linewidth=1, display=display.all)

fill(rs_plot, z_plot, m_rs >= 0 ? m_rs : 0, 0, color.new(#098b76, 25), color.new(#098b76, 60), title="Bullish Zone")
fill(rs_plot, z_plot, 0, m_rs < 0 ? m_rs : 0, color.new(#850812, 25), color.new(#850813, 60), title="Bearish Zone")

// Plots the green star at the bottom of the indicator pane when the transition happens
plotchar(s2_trigger ? -2 : na, title="Stage 2 Marker", char='*', location=location.absolute, color=color.rgb(12, 12, 222), size=size.small)

// Status Line Data
plot(rs_slope, "RS Slope", color=color.rgb(23, 10, 201), display=display.status_line + display.data_window)

// --- 8. ON-SCREEN TABLE ---
var table info_tab = table.new(position.top_right, 4, 2, bgcolor=color.white, border_width=1, border_color=color.black)
color header_bg = color.rgb(173, 216, 230) 
color header_fg = color.black

if barstate.islast
    table.cell(info_tab, 1, 0, "Date", text_color=header_fg, bgcolor=header_bg, text_size=size.small)
    table.cell(info_tab, 2, 0, "RS > 0", text_color=header_fg, bgcolor=header_bg, text_size=size.small)
    table.cell(info_tab, 3, 0, "Slope > " + str.tostring(slope_thresh), text_color=header_fg, bgcolor=header_bg, text_size=size.small)
    
    color rs_color = s2_rs_pass ? color.green : color.red
    color slope_color = s2_slope_pass ? color.green : color.red
    
    table.cell(info_tab, 1, 1, "Latest", text_color=color.black, bgcolor=color.white, text_size=size.small)
    table.cell(info_tab, 2, 1, str.tostring(m_rs, "#.##"), text_color=rs_color, bgcolor=color.white, text_size=size.small)
    table.cell(info_tab, 3, 1, str.tostring(rs_slope, "#.##"), text_color=slope_color, bgcolor=color.white, text_size=size.small)