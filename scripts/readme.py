#!/usr/bin/env python3
"""Writes README.md: every image as <picture> with dark/light sources, plus phone sources (max-width: 600px)
where a compact "-m" variant exists. Edit the text here, then run `make readme`."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "assets")
S = "https://moutazm.com/projects/"
PHONE = "(max-width: 600px)"


def pic(name, alt, width=None, href=None):
    w = f' width="{width}"' if width else ""
    src = []
    if os.path.exists(os.path.join(A, f"{name}-m-dark.svg")):
        src += [f'<source media="{PHONE} and (prefers-color-scheme: dark)" srcset="assets/{name}-m-dark.svg">',
                f'<source media="{PHONE} and (prefers-color-scheme: light)" srcset="assets/{name}-m-light.svg">']
    src += [f'<source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">',
            f'<source media="(prefers-color-scheme: light)" srcset="assets/{name}-light.svg">']
    img = f'<picture>{"".join(src)}<img alt="{alt}" src="assets/{name}-dark.svg"{w}></picture>'
    return f'<a href="{href}">{img}</a>' if href else img


CARDS = [("diag-agent", "diag-agent: a home server that diagnoses its own outages", "https://github.com/moutaz121493/diag-agent"),
         ("can-tools", "CAN FD bit-timing calculator", S + "can-tools/"),
         ("moutaz-home", "Moutaz Home: self-hosted homelab on a Raspberry Pi 5", S + "moutaz-home/"),
         ("paperless-ai", "Paperless AI: German paperwork filed by an LLM", S + "paperless-ai/"),
         ("home-rag", "Home RAG: master's thesis on cross-lingual retrieval", S + "home-rag/"),
         ("moutazm-com", "moutazm.com: trilingual portfolio", "https://github.com/moutaz121493/Moutazm.com")]


def main():
    rows = "".join("<p>\n  " + "\n  ".join(pic("card3d-" + s, a, "49%", h) for s, a, h in CARDS[i:i + 2]) + "\n</p>\n" for i in range(0, 6, 2))
    md = f'''{pic("hero", "Moutaz Mohammad: embedded engineer building intelligent systems, from CAN bits to RAG pipelines. A CAN FD frame travels along a twisted pair into a rotating 3D neural network.", href="https://moutazm.com/3d/")}

<p align="center">
  <a href="https://moutazm.com/3d/"><b>▶ Open the interactive 3D version</b></a>
</p>

<p align="center">
  <a href="https://moutazm.com"><img alt="Website moutazm.com" src="https://img.shields.io/badge/moutazm.com-f5b83f?style=for-the-badge&labelColor=0b1118&logo=googlechrome&logoColor=f5b83f"></a>
  <a href="https://www.linkedin.com/in/moutaz-mohammad-728356347/"><img alt="LinkedIn" src="https://img.shields.io/badge/LinkedIn-4fd1ff?style=for-the-badge&labelColor=0b1118&logo=linkedin&logoColor=4fd1ff"></a>
  <a href="mailto:moutaz@moutazm.com"><img alt="Email moutaz@moutazm.com" src="https://img.shields.io/badge/moutaz@moutazm.com-45e08f?style=for-the-badge&labelColor=0b1118&logo=maildotru&logoColor=45e08f"></a>
  <img alt="Open to embedded, networking and applied-AI roles" src="https://img.shields.io/badge/open_to-embedded_·_networking_·_applied_AI-8d9ca8?style=for-the-badge&labelColor=0b1118">
</p>

{pic("div-about", "About")}

I test, debug and bring up **automotive in-vehicle networks (CAN / CAN FD)** at an ISO/IEC 17025-accredited test house in Germany.
In my own time I run a small **self-hosted infrastructure** on a Raspberry Pi and build **LLM-powered automation** on top of it.
I'm studying for an M.Sc. in Web Technologies, with a thesis on cross-lingual (Arabic / German) **retrieval-augmented generation**.

> **Where I'm heading:** AI engineering, with the discipline of embedded work behind it. Measured, secure, and built to keep running.

{pic("div-now", "Now")}

{pic("now3d", "Now: studying an M.Sc. with a thesis on cross-lingual RAG; learning a structured AI-engineering path; building a measurable RAG system over my own documents")}

{pic("div-homelab", "Homelab")}

{pic("homelab", "Homelab live status, published hourly by the Raspberry Pi itself: uptime, services, backups, 30-day availability, 24-hour CPU and temperature", href=S + "moutaz-home/")}

{pic("div-can-fd", "CAN FD")}

{pic("canfd", "CAN FD decoder: one real base-format frame scrolls past bit by bit, with arbitration at 500 kbit/s, the bit-rate switch to 2 Mbit/s, stuff bits and the CRC-17 marked")}

{pic("div-selected-work", "Selected work")}

{rows}
{pic("div-thesis", "Thesis")}

{pic("trace", "Thesis trace: question in Arabic, routing, keyword and vector retrieval, reciprocal rank fusion, answer with sources, evaluation with Recall@k, MRR, faithfulness, latency and cost")}

{pic("activity", "Latest public GitHub activity: commits in the last 30 days, recently pushed repositories and language mix")}

{pic("div-contributions", "Contributions")}

{pic("skyline", "3D contribution calendar")}

{pic("div-toolbox", "Toolbox")}

{pic("stack", "Toolbox: CAN / CAN FD, ISO 16845-1, MCU drivers, bit timing and TDC, LIN, Automotive Ethernet; Python, test automation; Debian, Docker Compose, systemd, Cloudflare, Tailscale, restic, Uptime Kuma; RAG, Claude, Gemini, structured output, evaluation")}

{pic("div-journey", "Journey")}

{pic("journey", "Journey: B.Sc. Communications and Electronics Engineering 2014 to 2019, Test Engineer for automotive networks since 2022, self-hosted homelab with LLM automation, M.Sc. Web Technologies expected 2027")}

{pic("div-contact", "Contact")}

🌍 Arabic (native) · English (C1) · German (B2)  
📫 [moutazm.com](https://moutazm.com) · [LinkedIn](https://www.linkedin.com/in/moutaz-mohammad-728356347/) · moutaz@moutazm.com · open to conversations about embedded, networking and applied-AI roles in Germany.

{pic("footer", "A CAN frame whose data bytes spell HELLO. Thanks for visiting.")}

<sub>Every image on this page is generated by the scripts in <a href="scripts">/scripts</a> (see its README); the live cards are refreshed by GitHub Actions.</sub>
'''
    with open(os.path.join(ROOT, "README.md"), "w") as f:
        f.write(md)
    print("README.md written")


if __name__ == "__main__":
    main()
