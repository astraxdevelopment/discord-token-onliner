R# Discord Multi-Account RPC & Status Controller

A web dashboard for managing custom Discord Rich Presence (RPC) profiles, statuses, device identifiers, and proxies across multiple accounts at once.

> ⚠️ **Read before using.** This project is for **educational purposes only** and has **not been fully tested or audited**. It may contain bugs.
>
> Automating user accounts ("self-botting") **violates Discord's Terms of Service** and can lead to **account restrictions or permanent bans**. The developer is not responsible for any consequences, damages, or account actions resulting from its use. **Use at your own risk, and preferably on accounts you can afford to lose.**

---

## Features

- **Multi-account support**: run and manage several accounts concurrently
- **Web dashboard**: live management UI, hostable on [bot-hosting.net](https://bot-hosting.net) or locally
- **Custom RPC & status**: configure Rich Presence and status per account
- **Per-account proxies**: route each account through its own HTTP or SOCKS5 proxy
- **Device spoofing**: choose Desktop, Mobile, Web, or Embedded

---

## Requirements

- Python 3.10 or newer
- Dependencies listed in `requirements.txt`

---

## Installation

```bash
git clone https://github.com/astraxdevelopment/discord-token-onliner
cd discord-token-onliner
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

Then open the dashboard in your browser (default: `http://localhost:<port>`) and add your accounts.

## Configuration

Settings are stored in `config.json`. Never share this file or commit it to a public repository, since it may contain account tokens and proxy credentials.

Add `config.json` to your `.gitignore`.

---

## Project Structure

```text
├── main.py             # Application entry point
├── requirements.txt    # Python dependencies
├── config.json         # Account and proxy configuration
├── templates/
│   └── index.html      # Dashboard UI
├── LICENSE
└── README.md
```

---

## Security Tips

- Keep tokens private. Anyone with a token has full access to that account.
- Use a unique proxy per account to avoid linking them by IP.
- Don't run this on your main account.

---

## Community

- 💬 [Discord Server](https://discord.gg/TpHEZKTra)
- 🛒 [Store / Services](https://tocka.mysellauth.com)

## License

See [LICENSE](LICENSE) for details.
