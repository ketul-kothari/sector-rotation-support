// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © O'Neil CAN SLIM Style Dashboard 

//@version=6
indicator("Fundamentals Dashboard", overlay=false, max_labels_count=100)

// ═══════════════════════════════════════════════════════════════════════════════
// INPUTS
// ═══════════════════════════════════════════════════════════════════════════════
grpG           = "General Settings"
quartersToShow = input.int(4,   'Quarters to Display', minval=4, maxval=8, group=grpG)
tableY         = input.string('bottom', 'Vertical',   options=['top','middle','bottom'], group=grpG)
tableX         = input.string('left',   'Horizontal', options=['left','center','right'], group=grpG)
TextSize       = input.string('normal', 'Text Size',  options=['tiny','small','normal','large'], group=grpG)
showRawVal     = input.bool(false, 'Show Raw Values in Brackets', group=grpG)

grpT           = "Thresholds"
// step=0.1 ensures inputs respect 1 decimal logic
threshLow      = input.float(30.0, "52-Week Low Min (%)", step=0.1, group=grpT)
threshHigh     = input.float(25.0, "52-Week High Max (%)", step=0.1, group=grpT)
threshEps      = input.float(18.0, "EPS YoY Min (%)", step=0.1, group=grpT)
threshSales    = input.float(20.0, "Sales YoY Min (%)", step=0.1, group=grpT)
threshRoe      = input.float(17.0, "ROE Min (%)", step=0.1, group=grpT)
threshAnn      = input.float(25.0, "Annual EPS Growth Min (%)", step=0.1, group=grpT)
threshRawEps   = input.float(2.0,  "Min Raw Qtr EPS (₹)", step=0.1, group=grpT)
threshRawSales = input.float(50.0, "Min Raw Qtr Sales (Cr)", step=0.1, group=grpT)

// ═══════════════════════════════════════════════════════════════════════════════
// THEME & COLORS
// ═══════════════════════════════════════════════════════════════════════════════
HeaderBG   = color.new(#1a365d, 5)
RowBG      = color.new(#0d1117, 10)
TrendBG    = color.new(#0f2040, 10)
AnnualBG   = color.new(#2d1b4e, 15)

GoodColor = color.lime
BadColor  = color.red
FlatColor = color.gray

// ═══════════════════════════════════════════════════════════════════════════════
// PRICE STRUCTURE & TECHNICALS (Rounded to 1 Decimal)
// ═══════════════════════════════════════════════════════════════════════════════
dailyClose  = request.security(syminfo.tickerid, "D", close)
week52High  = request.security(syminfo.tickerid, "D", ta.highest(high, 252))
week52Low   = request.security(syminfo.tickerid, "D", ta.lowest(low,  252))

totalShares = request.financial(syminfo.tickerid, "TOTAL_SHARES_OUTSTANDING", "FY", ignore_invalid_symbol=true)
floatShares = request.financial(syminfo.tickerid, "FLOAT_SHARES_OUTSTANDING", "FY", ignore_invalid_symbol=true)

mcapCr      = (dailyClose * totalShares) / 10000000
floatCr     = floatShares / 10000000
floatPct    = math.round((floatShares / totalShares) * 100, 1)
floatMcapCr = floatCr * dailyClose

pctAbove52Low  = math.round((dailyClose - week52Low)  / week52Low  * 100, 1)
pctBelow52High = math.round((week52High - dailyClose) / week52High * 100, 1)

passLow  = pctAbove52Low  >= threshLow
passHigh = pctBelow52High <= threshHigh

// ═══════════════════════════════════════════════════════════════════════════════
// INSTITUTIONAL SPONSORSHIP & TURNOVER (LOCKED TO DAILY TIMEFRAME)
// ═══════════════════════════════════════════════════════════════════════════════
calcUDRatio() =>
    upV   = close > close[1] ? volume : 0
    downV = close < close[1] ? volume : 0
    sUp   = math.sum(upV, 50)
    sDown = math.sum(downV, 50)
    sDown == 0 ? na : math.round(sUp / sDown, 1)

udRatio = request.security(syminfo.tickerid, "D", calcUDRatio())

weeklyTurnoverCr = request.security(syminfo.tickerid, "W", ta.sma(volume * close, 10)) / 10000000
weeklyVol        = request.security(syminfo.tickerid, "W", ta.sma(volume, 10))

turnoverPctFloat = not na(weeklyTurnoverCr) and floatMcapCr > 0 ? math.round((weeklyTurnoverCr / floatMcapCr) * 100, 1) : na

// ═══════════════════════════════════════════════════════════════════════════════
// FINANCIAL DATA (Continuous Series - Rounded to 1 Decimal)
// ═══════════════════════════════════════════════════════════════════════════════
eps_c    = request.financial(syminfo.tickerid, 'EARNINGS_PER_SHARE_DILUTED', "FQ", ignore_invalid_symbol=true)
sales_c  = request.financial(syminfo.tickerid, 'TOTAL_REVENUE', "FQ", ignore_invalid_symbol=true)
roe_c    = request.financial(syminfo.tickerid, 'RETURN_ON_EQUITY', "FQ", ignore_invalid_symbol=true)
net_inc_c= request.financial(syminfo.tickerid, 'NET_INCOME', "FQ", ignore_invalid_symbol=true)

// Calculate Net Profit Margin % (Rounded to 1 decimal)
margin_c = (not na(sales_c) and sales_c > 0 and not na(net_inc_c)) ? math.round((net_inc_c / sales_c) * 100, 1) : na

annEps_c = request.financial(syminfo.tickerid, 'EARNINGS_PER_SHARE_DILUTED', "FY", ignore_invalid_symbol=true)

// ═══════════════════════════════════════════════════════════════════════════════
// ARRAYS & BULLETPROOF SHIFT LOGIC
// ═══════════════════════════════════════════════════════════════════════════════
datasize = quartersToShow + 6

var array<int>   qDates    = array.new_int(datasize,   0)
var array<float> epsArr    = array.new_float(datasize, na)
var array<float> salesArr  = array.new_float(datasize, na)
var array<float> roeArr    = array.new_float(datasize, na)
var array<float> marginArr = array.new_float(datasize, na)

// Increased to 6 to safely calculate acceleration for older years
var array<float> annArr   = array.new_float(6, na)
var array<int>   annDates = array.new_int(6, 0)

eps_changed = not na(eps_c) and eps_c != eps_c[1]

if eps_changed
    array.unshift(qDates,    time)
    array.unshift(epsArr,    eps_c)
    array.unshift(salesArr,  sales_c / 10000000)
    array.unshift(roeArr,    roe_c)
    array.unshift(marginArr, margin_c)

    array.pop(qDates)
    array.pop(epsArr)
    array.pop(salesArr)
    array.pop(roeArr)
    array.pop(marginArr)

if array.size(epsArr) > 0
    array.set(epsArr,    0, eps_c)
    array.set(salesArr,  0, sales_c / 10000000)
    // Applying round to raw ROE to maintain 1 decimal comparison
    array.set(roeArr,    0, not na(roe_c) ? math.round(roe_c, 1) : na)
    array.set(marginArr, 0, margin_c)

ann_changed = not na(annEps_c) and annEps_c != annEps_c[1]

if ann_changed
    array.unshift(annArr,   annEps_c)
    array.unshift(annDates, time)
    array.pop(annArr)
    array.pop(annDates)

if array.size(annArr) > 0
    array.set(annArr, 0, annEps_c)

// ═══════════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS (Rounded to 1 Decimal)
// ═══════════════════════════════════════════════════════════════════════════════
yoyChg(arr, idx) =>
    v = array.get(arr, idx)
    c = idx + 4 < array.size(arr) ? array.get(arr, idx + 4) : na
    na(v) or na(c) or c == 0 ? na : math.round((v - c) / math.abs(c) * 100, 1)

accelDir(arr, idx) =>
    g0 = yoyChg(arr, idx)
    g1 = yoyChg(arr, idx + 1)
    if na(g0) or na(g1)
        ""
    else if g0 > g1
        " ▲"
    else if g0 < g1
        " ▼"
    else
        ""

isAccel(arr, idx) =>
    g0 = yoyChg(arr, idx)
    g1 = yoyChg(arr, idx + 1)
    not na(g0) and not na(g1) and g0 > g1

marginExp(idx) =>
    m0 = array.get(marginArr, idx)
    m4 = idx + 4 < array.size(marginArr) ? array.get(marginArr, idx + 4) : na
    not na(m0) and not na(m4) and m0 > m4

marginDir(idx) =>
    m0 = array.get(marginArr, idx)
    m4 = idx + 4 < array.size(marginArr) ? array.get(marginArr, idx + 4) : na
    if na(m0) or na(m4)
        ""
    else if m0 > m4
        " ▲"
    else if m0 < m4
        " ▼"
    else
        ""

// Annual EPS YoY Growth
annGrowth(idx) =>
    curr = array.get(annArr, idx)
    prev = array.get(annArr, idx + 1)
    na(curr) or na(prev) or prev == 0 ? na : math.round((curr - prev) / math.abs(prev) * 100, 1)

// Up/Down Arrows for Annual EPS
annAccelDir(idx) =>
    g0 = annGrowth(idx)
    g1 = annGrowth(idx + 1)
    if na(g0) or na(g1)
        ""
    else if g0 > g1
        " ▲"
    else if g0 < g1
        " ▼"
    else
        ""

isCode33(idx) =>
    isAccel(epsArr, idx) and isAccel(epsArr, idx + 1) and isAccel(epsArr, idx + 2) and isAccel(salesArr, idx) and isAccel(salesArr, idx + 1) and isAccel(salesArr, idx + 2) and marginExp(idx) and marginExp(idx + 1) and marginExp(idx + 2)

// Formatting string updated to #.# for exactly 1 decimal place
fmtPct(v) => na(v) ? "-" : (v >= 0 ? "+" : "") + str.tostring(v, "#.#") + "%"
fmtVal(v) => na(v) ? "-" : str.tostring(math.round(v, 1), "#.#")
fmtMCap(v)=> na(v) ? "N/A" : str.tostring(math.round(v, 1), "#.#") + " Cr"
fmtVol(v) => na(v) ? "N/A" : str.tostring(math.round(v / 100000, 1), "#.#") + " L"

getCapCat(v) => na(v) ? "" : v >= 105000 ? "Large" : v >= 34700 ? "Mid" : v >= 1000 ? "Small" : "Micro"
getFloatMcapLabel(v) => na(v) ? "" : v < 500 ? "Micro Supply" : v <= 5000 ? "Agile Supply" : v <= 25000 ? "Moderate Supply" : "Heavy Supply"
getAdLabel(ratio) => na(ratio) ? "N/A" : ratio >= 1.5 ? "Heavy Acc" : ratio >= 1.0 ? "Accumulation" : "Distribution"

c_eps(v)   => na(v) ? FlatColor : v >= threshEps   ? GoodColor : BadColor
c_sales(v) => na(v) ? FlatColor : v >= threshSales ? GoodColor : BadColor
c_roe(v)   => na(v) ? FlatColor : v >= threshRoe   ? GoodColor : BadColor
c_ann(v)   => na(v) ? FlatColor : v >= threshAnn   ? GoodColor : BadColor
c_ad(ratio) => na(ratio) ? FlatColor : ratio >= 1.0 ? GoodColor : BadColor
c_margin(idx) => 
    m0 = array.get(marginArr, idx)
    m4 = idx + 4 < array.size(marginArr) ? array.get(marginArr, idx + 4) : na
    na(m0) or na(m4) ? FlatColor : m0 >= m4 ? GoodColor : BadColor

// ═══════════════════════════════════════════════════════════════════════════════
// TABLE RENDER
// ═══════════════════════════════════════════════════════════════════════════════
numCols   = quartersToShow + 1
totalRows = 14  

var table t = table.new(tableY + '_' + tableX, numCols, totalRows,
    bgcolor=RowBG, frame_color=color.gray, border_color=color.gray, border_width=1)

fullRow(r, txt, bg, tc) =>
    table.cell(t, 0, r, txt, bgcolor=bg, text_color=tc, text_size=TextSize, text_halign=text.align_left)
    table.merge_cells(t, 0, r, numCols - 1, r)

if barstate.islast
    row = 0

    // Market Cap
    mcapTxt = "Mkt Cap:  " + fmtMCap(mcapCr) + "  (" + getCapCat(mcapCr) + ")"
    fullRow(row, mcapTxt, HeaderBG, color.white)
    row += 1

    // Free Float Market Cap
    floatMcapTxt = "Float Mkt Cap:  " + fmtMCap(floatMcapCr) + "  (" + str.tostring(floatPct, "#.#") + "%)  [" + getFloatMcapLabel(floatMcapCr) + "]"
    floatMcapColor = floatMcapCr < 500 ? BadColor : GoodColor
    fullRow(row, floatMcapTxt, HeaderBG, floatMcapColor)
    row += 1

    // Turnover Row
    turnoverTxt = "Avg Weekly Turnover:  " + (na(weeklyTurnoverCr) ? "N/A" : str.tostring(math.round(weeklyTurnoverCr, 1), "#.#") + " Cr  (" + str.tostring(turnoverPctFloat, "#.#") + "% of Float)")
    turnoverColor = weeklyTurnoverCr > 25 ? GoodColor : BadColor
    fullRow(row, turnoverTxt, HeaderBG, turnoverColor)
    row += 1

    // Volume Row
    volTxt = "Avg Weekly Volume:  " + (na(weeklyVol) ? "N/A" : fmtVol(weeklyVol))
    volColor = weeklyVol >= 250000 ? GoodColor : BadColor
    fullRow(row, volTxt, HeaderBG, volColor)
    row += 1
    
    // Institutional Sponsorship
    adTxt = "Inst. Sponsorship:  " + str.tostring(udRatio, "#.#") + " U/D Ratio  [" + getAdLabel(udRatio) + "]"
    fullRow(row, adTxt, HeaderBG, c_ad(udRatio))
    row += 1

    // 52W Technicals & Raw Financials
    latestRawEps   = array.get(epsArr, 0)
    latestRawSales = array.get(salesArr, 0)
    colSplit = math.max(1, numCols - 2)

    cP_L = passLow ? GoodColor : BadColor
    cR_Eps = na(latestRawEps) ? FlatColor : latestRawEps >= threshRawEps ? GoodColor : BadColor
    
    table.cell(t, 0, row, "52w L ≥ " + str.tostring(threshLow, "#.#") + "%", bgcolor=TrendBG, text_color=color.white, text_size=TextSize, text_halign=text.align_left)
    table.cell(t, 1, row, "+" + str.tostring(pctAbove52Low,  "#.#") + "%", bgcolor=TrendBG, text_color=cP_L, text_size=TextSize, text_halign=text.align_center)
    if colSplit > 1
        table.merge_cells(t, 1, row, colSplit - 1, row)
    
    table.cell(t, colSplit, row, "EPS: " + fmtVal(latestRawEps), bgcolor=TrendBG, text_color=cR_Eps, text_size=TextSize, text_halign=text.align_center)
    if colSplit < numCols - 1
        table.merge_cells(t, colSplit, row, numCols - 1, row)
    row += 1

    cP_H = passHigh ? GoodColor : BadColor
    cR_Sales = na(latestRawSales) ? FlatColor : latestRawSales >= threshRawSales ? GoodColor : BadColor

    table.cell(t, 0, row, "52w H ≤ " + str.tostring(threshHigh, "#.#") + "%", bgcolor=TrendBG, text_color=color.white, text_size=TextSize, text_halign=text.align_left)
    table.cell(t, 1, row, "-" + str.tostring(pctBelow52High, "#.#") + "%", bgcolor=TrendBG, text_color=cP_H, text_size=TextSize, text_halign=text.align_center)
    if colSplit > 1
        table.merge_cells(t, 1, row, colSplit - 1, row)
        
    table.cell(t, colSplit, row, "Sales: " + fmtVal(latestRawSales) + " Cr", bgcolor=TrendBG, text_color=cR_Sales, text_size=TextSize, text_halign=text.align_center)
    if colSplit < numCols - 1
        table.merge_cells(t, colSplit, row, numCols - 1, row)
    row += 1

    latestAnn = annGrowth(0)
    latestAnnMatch = not na(latestAnn) and latestAnn >= threshAnn

    // Fundamentals Headers
    table.cell(t, 0, row, "METRIC", bgcolor=HeaderBG, text_color=color.white, text_size=TextSize)
    for i = 0 to quartersToShow - 1
        _idx   = quartersToShow - 1 - i
        _qd    = array.get(qDates, _idx)
        
        _qEps   = yoyChg(epsArr, _idx)
        _qSales = yoyChg(salesArr, _idx)
        _qRoe   = array.get(roeArr, _idx)
        
        _isC33   = isCode33(_idx)
        _isOneil = not na(_qEps) and _qEps >= threshEps and not na(_qSales) and _qSales >= threshSales and not na(_qRoe) and _qRoe >= threshRoe and latestAnnMatch
        
        _qlbl = na(_qd) or _qd == 0 ? "Q" + str.tostring(i + 1) : str.format("{0, date, MMM-yy}", _qd)
        
        if _isC33
            _qlbl := _qlbl + " ⭐"
        if _isOneil
            _qlbl := _qlbl + " ✅"
            
        table.cell(t, i + 1, row, _qlbl, bgcolor=HeaderBG, text_color=color.white, text_size=TextSize)
    row += 1

    // EPS Row
    table.cell(t, 0, row, "EPS YoY", bgcolor=RowBG, text_color=color.white, text_size=TextSize)
    for i = 0 to quartersToShow - 1
        _idx   = quartersToShow - 1 - i
        _currEps = array.get(epsArr, _idx)
        _yoy   = yoyChg(epsArr, _idx)
        _suf   = accelDir(epsArr, _idx)
        _rawStr = showRawVal and not na(_currEps) ? " (" + fmtVal(_currEps) + ")" : ""
        _dispTxt = fmtPct(_yoy) + _rawStr + _suf
        table.cell(t, i + 1, row, _dispTxt, bgcolor=RowBG, text_color=c_eps(_yoy), text_size=TextSize)
    row += 1

    // Sales Row
    table.cell(t, 0, row, "Sales YoY", bgcolor=RowBG, text_color=color.white, text_size=TextSize)
    for i = 0 to quartersToShow - 1
        _idx   = quartersToShow - 1 - i
        _currSales = array.get(salesArr, _idx)
        _yoy   = yoyChg(salesArr, _idx)
        _suf   = accelDir(salesArr, _idx)
        _rawStr = showRawVal and not na(_currSales) ? " (" + fmtVal(_currSales) + " Cr)" : ""
        _dispTxt = fmtPct(_yoy) + _rawStr + _suf
        table.cell(t, i + 1, row, _dispTxt, bgcolor=RowBG, text_color=c_sales(_yoy), text_size=TextSize)
    row += 1

    // Margin Row
    table.cell(t, 0, row, "Margin%", bgcolor=RowBG, text_color=color.white, text_size=TextSize)
    for i = 0 to quartersToShow - 1
        _idx   = quartersToShow - 1 - i
        _m0    = array.get(marginArr, _idx)
        _suf   = marginDir(_idx)
        _dispTxt = fmtVal(_m0) + (na(_m0) ? "" : "%") + _suf
        table.cell(t, i + 1, row, _dispTxt, bgcolor=RowBG, text_color=c_margin(_idx), text_size=TextSize)
    row += 1

    // ROE Row
    table.cell(t, 0, row, "ROE%", bgcolor=RowBG, text_color=color.white, text_size=TextSize)
    for i = 0 to quartersToShow - 1
        _idx = quartersToShow - 1 - i
        _rv  = array.get(roeArr, _idx)
        table.cell(t, i + 1, row, fmtVal(_rv) + (na(_rv) ? "" : "%"), bgcolor=RowBG, text_color=c_roe(_rv), text_size=TextSize)
    row += 1

    // Annual Year Header
    table.cell(t, 0, row, "Year", bgcolor=AnnualBG, text_color=color.white, text_size=TextSize)
    for j = 0 to quartersToShow - 1
        if j <= 3
            _rj  = 3 - j
            _ad  = array.get(annDates, _rj)
            _yr  = _ad == 0 ? "FY-" + str.tostring(_rj) : str.format("{0, date, yyyy}", _ad)
            table.cell(t, j + 1, row, _yr, bgcolor=AnnualBG, text_color=color.white, text_size=TextSize)
        else
            table.cell(t, j + 1, row, "", bgcolor=AnnualBG, text_color=FlatColor, text_size=TextSize)
    row += 1

    // Annual EPS% Row (Now with arrows!)
    table.cell(t, 0, row, "Ann EPS%", bgcolor=RowBG, text_color=color.white, text_size=TextSize)
    for j = 0 to quartersToShow - 1
        if j > 3
            table.cell(t, j + 1, row, "", bgcolor=RowBG, text_color=FlatColor, text_size=TextSize)
        else
            _rj     = 3 - j
            _a_curr = array.get(annArr, _rj)
            _ag     = annGrowth(_rj)
            _suf    = annAccelDir(_rj)
            _rawStr = showRawVal and not na(_a_curr) ? " (" + fmtVal(_a_curr) + ")" : ""
            _dispTxt = fmtPct(_ag) + _rawStr + _suf
            table.cell(t, j + 1, row, _dispTxt, bgcolor=RowBG, text_color=c_ann(_ag), text_size=TextSize)
    row += 1

plot(na, display=display.none)