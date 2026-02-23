from flask import Flask, render_template
import requests
import time

app = Flask(__name__)

# simple cache (5 minutes)
rate_cache = {
    "gold": None,
    "silver": None,
    "last": 0
}

def get_rates():
    try:
        now = time.time()

        # use cache for 5 minutes
        if now - rate_cache["last"] < 300:
            return rate_cache["gold"], rate_cache["silver"]

        res = requests.get("https://api.metals.live/v1/spot", timeout=5)
        data = res.json()

        gold_usd = next(x["gold"] for x in data if "gold" in x)
        silver_usd = next(x["silver"] for x in data if "silver" in x)

        usd_to_inr = 83

        gold_999 = (gold_usd * usd_to_inr) / 31.1035
        silver_999 = (silver_usd * usd_to_inr) / 31.1035

        gold_22k = round(gold_999 * 0.916)
        silver_rate = round(silver_999)

        rate_cache["gold"] = gold_22k
        rate_cache["silver"] = silver_rate
        rate_cache["last"] = now

        return gold_22k, silver_rate

    except Exception as e:
        print("Rate fetch error:", e)
        return None, None


@app.route("/")
def home():
    gold, silver = get_rates()
    return render_template(
        "index.html",
        gold_rate=gold,
        silver_rate=silver
    )


if __name__ == "__main__":
    app.run(debug=True)