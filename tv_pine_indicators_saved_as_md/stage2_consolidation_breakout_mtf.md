//@version=6
indicator("Stage 2 Consolidation (MTF + only W base invalidation)", overlay=true, precision=2, max_lines_count=500)

// =========================================================================
// 1. LIQUIDITY & GENERAL INPUTS
// =========================================================================
group_gen   = "General & Liquidity"
bench       = input.string("NSE:CNX500", "Benchmark", group=group_gen)
multiplier  = input.float(10.0, "Mansfield Multiplier", group=group_gen)
min_mc_cr   = input.float(500.0, "Min Market Cap (Cr)", group=group_gen)
min_vol     = input.int(250000, "Min Avg Volume (10W)", group=group_gen)
min_to_cr   = input.float(20.0, "Min Avg Turnover (Cr, 10W)", group=group_gen)

// =========================================================================
// 2. STAGE 2 CONSOLIDATION INPUTS
// =========================================================================
group_s2       = "Stage 2 Anchor Logic"
s2_sma_fast    = input.int(10, "Fast MA (Weeks)", group=group_s2)
s2_sma_slow    = input.int(30, "Slow MA (Weeks)", group=group_s2)
s2_bounce_wks  = input.int(52, "Bounce Lookback (Weeks)", group=group_s2)
s2_bounce_pct  = input.float(30.0, "Min Bounce % (Above Low)", group=group_s2)
s2_rs_slp_wks  = input.int(4, "RS Slope Length (Weeks)", group=group_s2)
s2_rs_slp_thr  = input.float(0.30, "RS Slope Threshold", group=group_s2)
s2_rs_val_thr  = input.float(0.0, "RS Zero Threshold", group=group_s2)
s2_conf_wks    = input.int(4, "Confirmation Period (Weeks)", group=group_s2)
s2_max_dd_pct  = input.float(40.0, "Max Drawdown %", group=group_s2)

// =========================================================================
// 3. SHARED DATA FETCHING
// =========================================================================
w_bench_close = request.security(bench, "W", close)
w_tso = request.financial(syminfo.tickerid, "TOTAL_SHARES_OUTSTANDING", "FQ", ignore_invalid_symbol=true)

// =========================================================================
// 4. UDT DEFINITION FOR WEEKLY STATE EXPORT
// =========================================================================
type WeeklyData
    bool  in_s2
    float anchor
    float max_dd
    int   base_len
    int   anchor_time
    bool  liq_vol
    bool  liq_to
    bool  liq_mc
    bool  s2_bounce
    bool  s2_trend
    bool  s2_rs_abs
    bool  s2_rs_slp
    bool  s2_held_below
    bool  s2_dd_held
    bool  s2_timing

// =========================================================================
// 5. ISOLATED WEEKLY CALCULATION ENGINE
// =========================================================================
calc_weekly(float bench_close, float tso_data) =>
    w_ratio = close / nz(bench_close, 1)
    m_rs    = ((w_ratio / ta.sma(w_ratio, 52)) - 1) * multiplier

    // --- Liquidity Breakdowns ---
    avg_vol = ta.sma(volume, 10)
    avg_to  = ta.sma((close * volume) / 10000000, 10)
    mc_data = (tso_data * close) / 10000000
    
    bool liq_vol_pass = avg_vol >= min_vol
    bool liq_to_pass  = avg_to >= min_to_cr
    bool liq_mc_pass  = na(mc_data) or mc_data >= min_mc_cr
    bool liq_pass     = liq_vol_pass and liq_to_pass and liq_mc_pass

    // --- Stage 2 Consolidation Core ---
    s2_ma_f   = ta.sma(close, s2_sma_fast)
    s2_ma_s   = ta.sma(close, s2_sma_slow)
    s2_rs_slp = (m_rs - nz(m_rs[s2_rs_slp_wks])) / s2_rs_slp_wks

    s2_cand_low52 = ta.lowest(low, s2_bounce_wks)

    // Component Validations
    bool valid_bounce = close >= (s2_cand_low52 * (1 + (s2_bounce_pct / 100)))
    bool valid_trend  = close > s2_ma_s and close > s2_ma_f
    bool valid_rs_abs = m_rs > s2_rs_val_thr
    bool valid_rs_slp = s2_rs_slp > s2_rs_slp_thr
    
    bool s2_is_potential = valid_bounce and valid_trend and (valid_rs_abs or valid_rs_slp) and liq_pass

    var bool  in_s2_base = false
    var float active_anchor = na
    var int   last_base_end_bar = 0
    var float s2_max_dd_in_base = 0.0
    var int   s2_base_length    = 0
    var int   s2_anchor_time    = na

    bool s2_past_potential = (bar_index >= s2_conf_wks) ? s2_is_potential[s2_conf_wks] : false
    float s2_past_high     = (bar_index >= s2_conf_wks) ? high[s2_conf_wks] : high
    
    bool s2_held_below         = ta.highest(close, math.max(1, s2_conf_wks)) <= s2_past_high 
    float s2_recent_lowest_close = ta.lowest(close, math.max(1, s2_conf_wks))
    bool s2_dd_held            = ((s2_past_high - s2_recent_lowest_close) / s2_past_high) * 100 <= s2_max_dd_pct
    bool s2_valid_timing       = (bar_index >= s2_conf_wks) ? (bar_index[s2_conf_wks] > last_base_end_bar) : false
    float s2_recent_lowest_low   = ta.lowest(low, math.max(1, s2_conf_wks))

    bool s2_confirmed_anchor = s2_past_potential and s2_held_below and s2_dd_held and not in_s2_base and s2_valid_timing

    // Capture state variables to export BEFORE invalidation removes them
    bool  export_in_s2      = in_s2_base
    float export_anchor     = active_anchor
    float export_max_dd     = s2_max_dd_in_base
    int   export_base_len   = s2_base_length
    int   export_anchor_time = s2_anchor_time

    if s2_confirmed_anchor
        in_s2_base := true
        active_anchor := s2_past_high
        s2_base_length := s2_conf_wks
        s2_max_dd_in_base := ((active_anchor - s2_recent_lowest_low) / active_anchor) * 100
        s2_anchor_time := time[s2_conf_wks]
        
        // Export newly created base values
        export_in_s2      := true
        export_anchor     := active_anchor
        export_max_dd     := s2_max_dd_in_base
        export_base_len   := s2_base_length
        export_anchor_time := s2_anchor_time

    else if in_s2_base
        s2_base_length += 1
        current_dd = ((active_anchor - low) / active_anchor) * 100
        s2_max_dd_in_base := math.max(s2_max_dd_in_base, current_dd)
        
        // Export ongoing base values before potential breakout invalidation
        export_max_dd   := s2_max_dd_in_base
        export_base_len := s2_base_length
        
        if close > active_anchor or close <= active_anchor * (1 - (s2_max_dd_pct / 100))
            in_s2_base := false
            active_anchor := na
            last_base_end_bar := bar_index
            s2_anchor_time := na

    WeeklyData.new(export_in_s2, export_anchor, export_max_dd, export_base_len, export_anchor_time, liq_vol_pass, liq_to_pass, liq_mc_pass, valid_bounce, valid_trend, valid_rs_abs, valid_rs_slp, s2_held_below, s2_dd_held, s2_valid_timing)

// =========================================================================
// 6. EXECUTE MTF FETCH
// =========================================================================
raw_w_data = request.security(syminfo.tickerid, "W", calc_weekly(w_bench_close, w_tso), lookahead=barmerge.lookahead_off)
w_data = na(raw_w_data) ? WeeklyData.new(false, float(na), 0.0, 0, int(na), false, false, false, false, false, false, false, false, false, false) : raw_w_data

// =========================================================================
// 7. VISUALS, LINES & LABELS (STRICT WEEKLY STATE)
// =========================================================================
var line  s2_base_line = na
var label s2_base_label = na
var float drawn_anchor = na
var float live_max_dd = 0.0

bool is_new_base = w_data.in_s2 and (na(drawn_anchor) or drawn_anchor != w_data.anchor)

if w_data.in_s2
    if is_new_base
        drawn_anchor := w_data.anchor
        live_max_dd  := w_data.max_dd
        
        s2_base_line := line.new(x1=w_data.anchor_time, y1=w_data.anchor, x2=time, y2=w_data.anchor, xloc=xloc.bar_time, color=color.purple, style=line.style_solid, width=2)
        
        string lbl_text = "DD: " + str.tostring(live_max_dd, "#.##") + "%\nBL: " + str.tostring(w_data.base_len) + "W"
        s2_base_label := label.new(x=w_data.anchor_time, y=w_data.anchor, text=lbl_text, xloc=xloc.bar_time, yloc=yloc.price, color=color.new(color.white, 100), textcolor=color.purple, style=label.style_label_down, size=size.small)
    else
        // Track visual drawdown dynamically based on current timeframe low
        float current_dd = ((w_data.anchor - low) / w_data.anchor) * 100
        live_max_dd := math.max(live_max_dd, current_dd)
        
        line.set_x2(s2_base_line, time)
        
        string lbl_text = "DD: " + str.tostring(live_max_dd, "#.##") + "%\nBL: " + str.tostring(w_data.base_len) + "W"
        label.set_text(s2_base_label, lbl_text)
else
    drawn_anchor := na

// =========================================================================
// 8. ALERTS & SHAPES
// =========================================================================
// Calculate crossovers globally on every bar to prevent historical tracking errors (CW10002)
bool cross_high  = ta.crossover(high, w_data.anchor)
bool cross_close = ta.crossover(close, w_data.anchor)

// 1. High Crosses Anchor (Intraday execution)
bool is_breakout_high = w_data.in_s2 and cross_high

// 2. Close Above Anchor (Confirmed execution)
bool is_breakout_close = w_data.in_s2 and cross_close

plotshape(is_breakout_high, title="Stage 2 Consolidation Breakout", style=shape.triangledown, location=location.abovebar, color=color.purple, size=size.tiny)

alertcondition(is_breakout_high, title="Alert 1: High Crosses Anchor (Intraday)", message="STAGE 2 HIGH BREAKOUT: {{ticker}}")
alertcondition(is_breakout_close, title="Alert 2: Close Above Anchor (Confirmation)", message="STAGE 2 CLOSE BREAKOUT: {{ticker}}")

// =========================================================================
// 9. EXHAUSTIVE DEBUGGING (DATA WINDOW)
// =========================================================================
plot(w_data.liq_vol ? 1 : 0, title="[LIQ] 1. Min Volume Pass", display=display.data_window)
plot(w_data.liq_to ? 1 : 0, title="[LIQ] 2. Min Turnover Pass", display=display.data_window)
plot(w_data.liq_mc ? 1 : 0, title="[LIQ] 3. Min Market Cap Pass", display=display.data_window)
plot(w_data.s2_bounce ? 1 : 0, title="[S2] 4. Bounce Valid", display=display.data_window)
plot(w_data.s2_trend ? 1 : 0, title="[S2] 5. Trend Valid (Above MAs)", display=display.data_window)
plot(w_data.s2_rs_abs ? 1 : 0, title="[S2] 6. RS Absolute Valid", display=display.data_window)
plot(w_data.s2_rs_slp ? 1 : 0, title="[S2] 7. RS Slope Valid", display=display.data_window)
plot(w_data.s2_held_below ? 1 : 0, title="[S2] 8. Price Held Below Anchor", display=display.data_window)
plot(w_data.s2_dd_held ? 1 : 0, title="[S2] 9. Drawdown Limit Held", display=display.data_window)
plot(w_data.s2_timing ? 1 : 0, title="[S2] 10. Timing Sequence Valid", display=display.data_window)
plot(w_data.in_s2 ? 1 : 0, title="[S2] Master: Actively Inside Base", display=display.data_window)
plot(w_data.anchor, title="[S2] Active Anchor Price", display=display.data_window)