"""Registry of brands Caveate knows about, with cited official channels,
canonical domains, known good sender identifiers, and documented 'never' rules.
Every entry carries prose_keys and src links so the user can see the source."""

# Restructured, all entries source-cited. Trust tier: 1=impossible to be a
# trusted channel, 2=weaker, 3=strong. rasa: policy text; phone/website/
# smscode are canonical and must be derived from official pages only.

# The 'never' keys are phrases that a legitimate message from this brand would
# not contain (see DECISION.md section 3 points 3 and 5). The 'sender_ids'
# list and 'short_codes' are the identifiers this brand actually uses when it does
# text you (sources listed per brand).

BRANDS = {
    # --- Banking ---
    "chase": {
        "name": "Chase",
        "canonical_site": "https://www.chase.com",
        "canonical_phone": "1-800-935-9935",
        "phone_source": "https://www.chase.com/digital/resources/privacy-security/security/self-service-text-messages.html",
        "short_codes": ["24273", "28107", "36640", "72166", "60969", "242733",
                        "21541", "41868", "63202", "85640", "98324", "74869",
                        "76577", "58501", "227777", "207207", "33172", "96619",
                        "35603", "64840", "23175", "24546", "55985"],
        "sender_ids": [],
        "sector": "bank",
        "never": {
            "otp": True,          # Chase never asks you to read a code back
            "move_money": True,    # no bank tells you to move money to protect it
            "gift_card": False,    # Chase doesn't buy gift cards; keep for banks generally
            "crypto": False,       # Chase never asks you to convert cash to crypto
            "verification": True,   # Chase alerts ask reply YES/NO, not 'verify account'
        },
        "policy_urls": [
            "https://www.chase.com/digital/resources/privacy-security/security/self-service-text-messages.html",
            "https://www.consumer.ftc.gov/articles/how-recognize-and-avoid-phishing-scams",
        ],
    },
    "wellsfargo": {
        "name": "Wells Fargo",
        "canonical_site": "https://www.wellsfargo.com",
        "canonical_phone": "1-800-869-3557",
        "phone_source": "https://www.wellsfargo.com/help/",
        "short_codes": ["93557"],
        "sender_ids": [],
        "sector": "bank",
        "never": {
            "otp": True,
            "move_money": True,
            "gift_card": False,
            "crypto": False,
            "verification": True,
        },
        "policy_urls": [
            "https://www.ftc.gov/news-events/news/press-releases/2026/06/ftc-data-show-people-reported-losing-3-point-5-billion-imposter-scams-2025",
        ],
    },
    "bankofamerica": {
        "name": "Bank of America",
        "canonical_site": "https://www.bankofamerica.com",
        "canonical_phone": "1-800-432-1000",
        "phone_source": "https://www.bankofamerica.com/security-center/",
        "short_codes": ["73981", "53849"],
        "sender_ids": [],
        "sector": "bank",
        "never": {
            "otp": True,
            "move_money": True,
            "gift_card": False,
            "crypto": False,
            "verification": True,
        },
        "policy_urls": [
            "https://www.bankofamerica.com/security-center/",
        ],
    },
    "paypal": {
        "name": "PayPal",
        "canonical_site": "https://www.paypal.com",
        "canal_phones": ["1-888-221-1161"],
        "phone_source": "https://www.paypal.com/us/support/",
        "short_codes": ["72975"],
        "sender_ids": ["PAYPAL"],
        "sector": "fintech",
        "never": {
            "otp": True,
            "move_money": True,
            "gift_card": False,
            "crypto": False,
            "verification": True,
        },
        "policy_urls": ["https://www.ftc.gov/news-events/news/press-releases/2026/06/ftc-data-show-people-reported-losing-3-point-5-billion-imposter-scams-2025"],
    },
    # --- Delivery / parcels ---
    "usps": {
        "name": "USPS",
        "canonical_site": "https://www.usps.com",
        "canal_phones": ["1-800-275-8777"],
        "phone_source": "https://www.uspis.gov/news/scam-article/smishing-package-tracking-text-scams",
        "short_codes": ["28777"],
        "sender_ids": ["USPS"],
        "sector": "delivery",
        "never": {
            "fee": True,      # USPS will not text you a redelivery or customs fee link
            "verify_link": True,  # USPS texts contain no link unless you signed up
        },
        "policy_urls": [
            "https://www.uspis.gov/news/scam-article/smishing-package-tracking-text-scams",
        ],
    },
    "fedex": {
        "name": "FedEx",
        "canonical_site": "https://www.fedex.com",
        "canal_phones": ["1-800-463-3339"],
        "phone_source": "https://www.fedex.com/en-us/home.html",
        "short_codes": ["46339"],
        "sender_ids": ["FEDEX"],
        "sector": "delivery",
        "never": {
            "fee": False,     # FedEx does collect customs fees legitimately (via official site)
            "verify_link": True,
        },
        "policy_urls": ["https://www.uspis.gov/news/scam-article/smishing-package-tracking-text-scams"],
    },
    "dhl": {
        "name": "DHL",
        "canonical_site": "https://www.dhl.com",
        "canal_phones": ["1-800-225-5345"],
        "phone_source": "https://www.dhl.com/us-en/home.html",
        "short_codes": [],
        "sender_ids": ["DHL"],
        "sector": "delivery",
        "never": {
            "fee": False,     # DHL DOES sometimes collect real customs duty (documented)
            "verify_link": True,
        },
        "policy_urls": ["https://www.tuteladigitalis.com/impersonation-index"],
    },
    # --- Government ---
    "irs": {
        "name": "Internal Revenue Service (IRS)",
        "canonical_site": "https://www.irs.gov",
        "canal_phones": ["1-800-829-1040"],
        "phone_source": "https://www.irs.gov/newsroom/ways-to-tell-if-the-irs-is-reaching-out-or-if-its-a-scammer",
        "short_codes": [],
        "sender_ids": [],
        "sector": "government",
        "never": {
            "first_contact": True,   # IRS first contact is a letter, not a text
            "otp": False,
            "move_money": False,
            "gift_card": True,       # IRS never asks for gift cards (common scam)
            "crypto": False,
            "verification": False,
        },
        "policy_urls": ["https://www.irs.gov/newsroom/ways-to-tell-if-the-irs-is-reaching-out-or-if-its-a-scammer"],
    },
    "ssa": {
        "name": "Social Security Administration (SSA)",
        "canonical_site": "https://www.ssa.gov",
        "canal_phones": ["1-800-772-1213"],
        "phone_source": "https://www.ssa.gov/fraud/",
        "short_codes": [],
        "sender_ids": [],
        "sector": "government",
        "never": {
            "first_contact": True,
            "otp": False,
            "gift_card": True,
            "move_money": False,
            "crypto": False,
            "verification": False,
        },
        "policy_urls": ["https://www.ssa.gov/fraud/"],
    },
    # --- E-commerce / big tech ---
    "amazon": {
        "name": "Amazon",
        "canonical_site": "https://www.amazon.com",
        "canal_phones": ["1-888-280-4331"],
        "phone_source": "https://www.amazon.com/help",
        "short_codes": ["262966", "25392"],
        "sender_ids": ["AMAZON"],
        "sector": "ecommerce",
        "never": {
            "fee": False,
            "verify_link": True,
            "gift_card": False,
            "otp": True,          # delivery OTP is legit-ish; sign-in OTP is not
            "verification": False,
        },
        "policy_urls": ["https://www.ftc.gov/news-events/news/press-releases/2026/06/ftc-data-show-people-reported-losing-3-point-5-billion-imposter-scams-2025"],
    },
    "geeksquad": {
        "name": "Best Buy / Geek Squad",
        "canonical_site": "https://www.bestbuy.com",
        "canal_phones": ["1-888-237-8289"],
        "phone_source": "https://www.bestbuy.com/site/contact",
        "short_codes": [],
        "sender_ids": [],
        "sector": "ecommerce",
        "never": {
            "fee": False,
            "verify_link": True,
            "otp": False,
            "gift_card": True,      # Geek Squad requires gift cards = classic scam
            "crypto": False,
            "verification": False,
        },
        "policy_urls": ["https://www.ftc.gov/news-events/news/press-releases/2026/06/ftc-data-show-people-reported-losing-3-point-5-billion-imposter-scams-2025"],
    },
    "apple": {
        "name": "Apple",
        "canonical_site": "https://www.apple.com",
        "canal_phones": ["1-800-275-2273"],
        "phone_source": "https://support.apple.com/en-us/100660",
        "short_codes": [],
        "sender_ids": [],
        "sector": "bigtech",
        "never": {
            "otp": True,
            "move_money": False,
            "gift_card": True,
            "crypto": False,
            "verification": False,
        },
        "policy_urls": ["https://www.ftc.gov/news-events/news/press-releases/2026/06/ftc-data-show-people-reported-losing-3-point-5-billion-imposter-scams-2025"],
    },
    "microsoft": {
        "name": "Microsoft",
        "canonical_site": "https://www.microsoft.com",
        "canal_phones": ["1-800-642-7676"],
        "phone_source": "https://support.microsoft.com/en-us/contactus",
        "short_codes": ["87892", "69525", "26096", "6245"],
        "sender_ids": ["MSFT"],
        "sector": "bigtech",
        "never": {
            "otp": True,
            "gift_card": True,
            "crypto": False,
            "verification": False,
            "move_money": False,
        },
        "policy_urls": ["https://support.microsoft.com/en-us/topic/how-to-report-internet-phishing-scams"],
    },
    # --- Toll / transit ---
    "easypass": {
        "name": "E-ZPass",
        "canonical_site": "https://www.e-zpassny.com",
        "canal_phones": ["1-800-333-8655"],
        "phone_source": "https://www.e-zpassny.com/",
        "short_codes": [],
        "sender_ids": [],
        "sector": "toll",
        "never": {
            "fee": True,     # toll-texting 'you owe an overdue toll' is a standard scam
            "verify_link": True,
            "gift_card": False,
            "crypto": False,
            "verification": False,
        },
        "policy_urls": ["https://www.tuteladigitalis.com/impersonation-index"],
    },
    # --- Utilities ---
    "pgande": {
        "name": "PG&E",
        "canonical_site": "https://www.pge.com",
        "canal_phones": ["1-800-743-5000"],
        "phone_source": "https://www.pge.com/en/help.html",
        "short_codes": [],
        "sender_ids": [],
        "sector": "utility",
        "never": {
            "gift_card": True,
            "disconnect": True,     # utility-disconnect-in-1-hour + gift card = top scam
            "verify_link": False,
            "crypto": False,
            "verification": False,
        },
        "policy_urls": ["https://www.ftc.gov/news-events/news/press-releases/2026/06/ftc-data-show-people-reported-losing-3-point-5-billion-imposter-scams-2025"],
    },
}

ALIASES = {
    "usps": "usps",
    "geek squad": "geeksquad",
    "best buy": "geeksquad",
    "geeksquad": "geeksquad",
    "us postal": "usps",
    "united states postal": "usps",
    "boa": "bankofamerica",
    "wells fargo": "wellsfargo",
    "wells": "wellsfargo",
    "chase": "chase",
    "paypal": "paypal",
    "fedex": "fedex",
    "ups": None,          # canonical data not yet resolved; reserved so alias maps to unhandled
    "dhl": "dhl",
    "amazon": "amazon",
    "apple": "apple",
    "microsoft": "microsoft",
    "e-zpass": "easypass",
    "ezpass": "easypass",
    "ez pass": "easypass",
    "ssa": "ssa",
    "social security": "ssa",
    "irs": "irs",
    "internal revenue": "irs",
    "pg&e": "pgande",
    "pge": "pgande",
}

# Generic short codes / sender IDs that multiple banks and delivery firms use.
# These are NOT canonical; they are only for the 'register says this is 2FA' check.
GENERIC_2FA_SHORT_CODES = {
    "22395": "Twilio/Authy/Shop Pay/Mailchimp shared verification code",
    "65821": "Okta identity verification",
    "22000": "Google verification",
    "86434": "Q2 Text Banking Alerts (shared by multiple banks/credit unions)",
}
