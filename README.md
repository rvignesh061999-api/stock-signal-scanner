# Stock Signal Scanner (GitHub-only edition)

Runs entirely on GitHub — no Replit, no separate hosting account needed.
Candle patterns + support/resistance + volume confirmation, for a US and
India stock watchlist. Scans hourly, alerts BUY/SHORT signals to Telegram,
shows results on a free GitHub Pages dashboard. Backtesting sends a PDF
report to Telegram on demand.

**Educational tool — not financial advice.**

## How it works

- **GitHub Actions** runs `scan_and_alert.py` every hour on GitHub's own
  servers (see `.github/workflows/scan.yml`). No server of yours needs to
  stay on.
- Results are saved to `docs/data.json` and committed back to the repo.
- **GitHub Pages** serves `docs/index.html`, a static dashboard that reads
  `docs/data.json` — this becomes your live dashboard URL.
- New BUY/SHORT signals are sent to Telegram automatically, one
  consolidated message per scan (BUY section, then SHORT section).
- **Backtesting** is a separate on-demand workflow (`.github/workflows/backtest.yml`)
  — trigger it manually from the Actions tab with a symbol, duration, and
  holding period; it runs the backtest and sends a PDF report to Telegram.

## One-time setup

### 1. Push this code to your GitHub repo
Upload all these files to your repo (keep the folder structure, especially
`.github/workflows/` and `docs/`).

### 2. Add repo Secrets
Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**.
Add:
- `TD_API_KEY` — your Twelve Data API key (fallback data source)
- `TELEGRAM_BOT_TOKEN` — your bot token from @BotFather
- `TELEGRAM_CHAT_ID` — your Telegram chat ID

### 3. Enable GitHub Pages
Go to **Settings → Pages**. Under "Source," choose **Deploy from branch**,
branch `main`, folder `/docs`. Save. GitHub will give you a URL like:
```
https://<your-username>.github.io/<repo-name>/
```
That's your permanent dashboard link.

### 4. Enable the scheduled workflow
Workflows are enabled by default once pushed. To confirm, go to the
**Actions** tab — you should see "Scheduled Stock Scan" and "Backtest a
Stock" listed. The scheduled one runs automatically every hour; you can
also click **Run workflow** to trigger it immediately for a first test.

### 5. Test the backtest workflow
Go to **Actions → Backtest a Stock → Run workflow**. Fill in:
- Symbol: e.g. `RELIANCE.NS`
- Duration: 12
- Holding: 10

Click **Run workflow**, wait ~1 minute, then check Telegram for the PDF.

## Files

```
config.py                  Watchlist definition
data_fetch.py               Yahoo Finance + Twelve Data fetching
signal_engine.py             Candle + support/resistance + volume signal logic
backtest.py                  Historical backtest engine
report_pdf.py                 PDF report builder
telegram_alert.py             Telegram message + document sending
scan_and_alert.py              Scheduled scan script (run by scan.yml)
run_backtest_and_send.py        Manual backtest script (run by backtest.yml)
docs/index.html                 GitHub Pages dashboard
docs/data.json                   Latest scan results (auto-updated)
alerted_keys.json                 Dedup tracking so you don't get repeat alerts
.github/workflows/scan.yml         Hourly scheduled scan
.github/workflows/backtest.yml      Manual backtest trigger
requirements.txt                     Python dependencies
```

## Editing the watchlist

Edit `config.py`:
```python
WATCHLIST = {
    "US": ["AAPL", "MSFT", "TSLA"],
    "IN": ["RELIANCE.NS", "TCS.NS"],   # .NS suffix for NSE tickers
}
```
Commit the change — the next scheduled run picks it up automatically.

## Adjusting scan frequency

Edit the cron schedule in `.github/workflows/scan.yml`:
```yaml
- cron: '0 * * * *'   # every hour, at minute 0
```
GitHub Actions cron is in UTC. Free tier gives ~2,000 minutes/month for
private repos (unlimited for public repos) — a watchlist of ~18 stocks
scanning hourly uses only a small fraction of that.

## Honest limitations

- GitHub Actions schedules aren't perfectly on-the-minute — expect a few
  minutes of drift, which doesn't matter for a daily-candle strategy.
- The dashboard updates only when a workflow run commits new data — if
  you disable the scheduled workflow, the dashboard goes stale.
- Signal logic uses fixed thresholds (volume ratio, level tolerance, R:R)
  — use the backtest workflow regularly to check whether they're actually
  working for your specific watchlist before trusting live signals.
- Not financial advice. Consider paper-testing before using real money.
