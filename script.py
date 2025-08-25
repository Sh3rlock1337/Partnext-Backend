//@version=5
strategy("Tutrtle Surge Bitvoin", percision=2, overlay=true, initial_capital=10000, commission_type=strategy.commission.percent,
         commission_value=0.18, slippage=3,pyramiding=5,close_entries_rule="ANY")


//-------DEFINIOTION-------------//
t1 = "prozentualer Anteil, den man pro Trade riskiert"
t2 = "ATR Länge"
t3 = "Vielfaches des ATR für den Stop-loss"
t4 = "ATR basiertes Level wo man Positionen ausbaut"
t5 = "System 1 geht Long wenn diese Periode ein neues Hoch macht"
t6 = "System 2 geht Long wenn diese Periode ein neues Hoch macht"
t7 = "Long Exit von System 1 wenn diese Periode ein neues Tief macht"
t8 = "Long Exit von System 2 wenn diese Periode ein neues Tief macht"
t9 = "System 1 geht short wenn diese Periode ein neues Tief macht"
t10 = "System 2 geht short wenn diese Periode ein neues Tief macht"
t11 = "Short Exit von System 1 wenn diese Periode ein neues Hoch macht"
t12 = "Short Exit von System 2 wenn diese Periode ein neues Hoch macht"

//-------Funktionen-------------//

//@function Text Anzeige
debugLabel(txt, color) =>
    label.new(bar_index, high, text=txt, color=color, style=label.style_label_lower_right, textcolor=color.black, size=size.small)

//@function Überprüfen ob Tag im Backtest Zeitraum liegt
inBacktestPeriod(start, end) => (time >= start) and (time <= end)

//function Funktion zum runden auf eine bestimme anzahl von nachkommastellen ( ich hab 2 gewählt)
roundToDecimals(value, decimals) =>
    math.round(value*math.pow(10, decimals))/math.pow(10, decimals)

// Nutzer EIngaben
//Risikomanagement inputs
percentage_to_risk = input.float(2, "Risk % of capital", maxval=100, minval=0, group="TurtleParameters", tooltip=t1)
atr_period = input.int(20, "ATR period", minval=1, group="Turtle Parameters", tooltip=t2)
stop_N_multiplier = input.float(1, "Stop ATR", minval=0.1, group="Turtle Parameters", tooltip=t3)
pyramid_profit = input.float(0.5, "pyramid Profit", minval=0.01, group="Turtle Parameters", tooltop=t4)
S1_long = input.int(20, "S1 Long", minval=1, gorup="Turtle Parameters", tooltop=t5)
S2_long = input.int(55, "S2 Long", minval=1, group="Turtle Parameters", tooltop=t6)
S1_long_exit = input.int(10, "S1 Long Exit", minval=1, group="Turtle Parameters", tooltop=t7)
S2_long_exit = input.int(20, "S2 Long Exit", minval=1, group="Turtle Parameters", tooltop=t8)
S1_short = input.int(15, "S1 Short", minval=1, group="Turtle Parameters", tooltop=t9)
S2_short = input.int(55, "S2 Short", minval=1, group="Turtle Parameters", tooltop=t10)


