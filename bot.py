import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

class TradingBotCore:
    def __init__(self, timeframe="1h"):
        self.timeframe = timeframe
        self.exchange = ccxt.binance({
            'apiKey': os.getenv('BINANCE_TESTNET_API_KEY'),
            'secret': os.getenv('BINANCE_TESTNET_SECRET_KEY'),
            'enableRateLimit': True,
            'options': {'defaultType': 'future', 'adjustForTimeDifference': True},
            'urls': {'api': {'public': 'https://testnet.binancefuture.com/fapi/v1', 'private': 'https://testnet.binancefuture.com/fapi/v1'}}
        })

    def fetch_balance(self):
        try:
            res = self.exchange.fapiPrivateV2GetBalance()
            balances = {wallet['asset']: float(wallet.get('availableBalance', 0.0)) for wallet in res}
            return {"USDT": balances.get('USDT', 0.0), "BTC": balances.get('BTC', 0.0)}
        except Exception:
            return {"USDT": 0.0, "BTC": 0.0}

    def execute_real_market_order(self, symbol, side, capital_usdt):
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            amount = round(capital_usdt / current_price, 4)
            if amount <= 0:
                return {"status": "error", "message": "Capital insuficiente para el lote mínimo."}

            if side.upper() == 'BUY':
                order = self.exchange.create_market_buy_order(symbol, amount)
            else:
                order = self.exchange.create_market_sell_order(symbol, amount)

            return {
                "status": "success", "symbol": symbol, "side": side,
                "invested_usdt": capital_usdt, "execution_price": current_price,
                "amount_executed": amount, "order_id": order.get('id')
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_market_closes(self, symbol, tf, limit=100):
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, tf, limit=limit)
            return [candle[4] for candle in ohlcv]
        except Exception:
            return []

    def calculate_sma(self, prices, period=20):
        if len(prices) < period: return 0
        return sum(prices[-period:]) / period

    def calculate_rsi(self, prices, period=14):
        if len(prices) <= period: return 50
        gains = [prices[i] - prices[i-1] if prices[i] > prices[i-1] else 0 for i in range(1, len(prices))]
        losses = [abs(prices[i] - prices[i-1]) if prices[i] < prices[i-1] else 0 for i in range(1, len(prices))]
        
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
        if avg_loss == 0: return 100
        return 100 - (100 / (1 + (avg_gain / avg_loss)))

    def evaluate_market_signal(self, symbol, allocated_capital_usdt=100.0):
        closes = self.get_market_closes(symbol, self.timeframe, limit=50)
        macro_closes = self.get_market_closes(symbol, "4h", limit=50)
        
        if not closes: return {"action": "HOLD"}

        current_price = closes[-1]
        sma20 = self.calculate_sma(closes, 20)
        rsi14 = self.calculate_rsi(closes, 14)
        
        macro_sma = self.calculate_sma(macro_closes, 20) if macro_closes else current_price
        is_macro_bullish = current_price >= macro_sma

        signal = "HOLD"
        if current_price > sma20 and (30 < rsi14 < 55):
            if is_macro_bullish: signal = "BUY"
        elif current_price < sma20 and rsi14 > 70:
            signal = "SELL"

        return {
            "symbol": symbol, "action": signal, "current_price": current_price,
            "sma20": round(sma20, 2), "rsi14": round(rsi14, 2),
            "macro_bullish": is_macro_bullish,
            "risk_data": self.calculate_risk(current_price, allocated_capital_usdt)
        }

    def calculate_risk(self, entry_price, capital_usdt):
        sl_pct = 0.015  # 1.5% Stop Loss
        tp_pct = 0.030  # 3.0% Take Profit
        trailing_trigger_pct = 0.015
        
        fee_rate = 0.0008  # 0.08% Comisión estimada Binance Futures (Ida y vuelta)
        estimated_fee = capital_usdt * fee_rate

        gross_profit = capital_usdt * tp_pct
        net_profit = gross_profit - estimated_fee
        potential_loss = (capital_usdt * sl_pct) + estimated_fee
        risk_reward_ratio = round(net_profit / potential_loss, 2) if potential_loss > 0 else 0

        return {
            "allocated_capital_usdt": capital_usdt,
            "entry_price": entry_price,
            "stop_loss_price": round(entry_price * (1 - sl_pct), 2),
            "take_profit_price": round(entry_price * (1 + tp_pct), 2),
            "trailing_trigger_price": round(entry_price * (1 + trailing_trigger_pct), 2),
            "risk_pct": sl_pct * 100,
            "reward_pct": tp_pct * 100,
            "estimated_fee_usdt": round(estimated_fee, 2),
            "potential_profit_usdt": round(net_profit, 2),
            "potential_loss_usdt": round(potential_loss, 2),
            "risk_reward_ratio": risk_reward_ratio,
            "asset_lot_size": round(capital_usdt / entry_price, 4) if entry_price > 0 else 0
        }