# BlackOut Scripts Collection 🗃️

[![Status: Legacy](https://img.shields.io/badge/Status-Legacy_Archive-orange)](https://github.com/your-username/netkiller-scripts)
[![Python: 3.11.9](https://img.shields.io/badge/Python-3.11.9-blue)](https://python.org)
[![License: Educational Use](https://img.shields.io/badge/License-Educational_Only-lightgrey)](https://opensource.org/licenses)
[![Field: Security Research](https://img.shields.io/badge/Field-Security_Research-red)](https://www.cisecurity.org)

> **⚠️ CRITICAL DISCLAIMER:** This repository contains **historical and legacy proof-of-concept code** from a time when these networking concepts were actively explored. It is **NOT operational** for modern use and is provided **strictly for educational analysis and research purposes** in controlled, isolated lab environments. The code is unmaintained and contains known security flaws inherent to its design.

## 📌 Overview

This archive represents a **comprehensive, multi-vector framework** demonstrating the full lifecycle of complex **Distributed Denial of Service (DDoS)** attack methodologies, from reconnaissance and infrastructure scanning to execution of advanced, protocol-specific floods. The core engine is designed to orchestrate attacks using a network of compromised IoT devices and SOCKS5 proxies.

## 🧰 Conceptual Contents & Functional Breakdown

### I. 💀 Core Execution Engine & Botnet Logic

| Script | Primary Class | Functional Summary |
| :--- | :--- | :--- |
| **`blackout.py`** | `IoTDDoSAttack` | **The central C2 framework.** Coordinates and launches over 40 distinct L3, L4, and L7 attacks. Features include: RAW Socket management for **IP Spoofing** (essential for Amplification/Reflection), **HTTP/2 Rapid Reset**, **BGP Hijacking emulation**, **NGINX Worker/Keepalive Killers**, advanced **DNS Water Torture**, **Zero Trust Bypass** logic, and **WebSocket** attacks. |
| **`quic.py`** | `QUICAttacker` | **HTTP/3 QUIC Flooder. Implements direct UDP floods targeting the QUIC protocol (HTTP/3) on port 443/UDP. Includes logic for both high-speed direct QUIC flood and QUIC Amplification attacks (leveraging connection negotiation). |

### II. 🔍 Reconnaissance & Vulnerability Assessment

This section details tools used for target intelligence gathering and deep vulnerability analysis.

| Script | Primary Focus | Key Functionality |
| :--- | :--- | :--- |
| **`godie.py`** | `AdvancedDDoSScanner` | **Multi-Vector Vulnerability Scanner.** Performs deep checks for **L7 Slow Attacks** (Slowloris/Range Header), **Amplification** (DNS, NTP, SSDP, Memcached), **Application Layer** (CMS/XML-RPC), and **Infrastructure Analysis** (WAF/CDN/Load Balancer Detection, Exposed K8s/Docker/Redis). |
| **`iotscaner.py`** | `IoTScanner` | **IoT Brute Force and Protocol Scanner.** Scans IP ranges for common IoT/Industrial ports (Telnet, SSH, FTP, RTSP, Modbus, MQTT, CoAP, VNC). Performs brute force against detected services and includes integrated checks for **Amplification DDoS** vulnerabilities (DNS, NTP, Memcached, QUIC). |
| **`scan.py`** | `DNS Amp Scanner` | **Real Amplification Factor Measurement.** A scientific scanner to accurately measure the **Amplification Ratio** for different DNS query types (`ANY`, `DNSKEY`, `TXT`). It also verifies if the server is susceptible to **Reflection** (IP Spoofing). |
| **`cl5.py`** | `comprehensive_ip_finder` | **Origin IP Finder (DNS Lookup).** Finds the real Origin IP of a website hidden behind CDNs (like Cloudflare) by performing **MX and TXT record lookups** and checking if the resolved IP is within known CDN ranges. |
| **`cl2.py`** | `check_ip_services` | **Origin IP Finder (Public Services).** Finds historical and current IP addresses using **public OSINT services** (e.g., HackerTarget, ViewDNS IP History) often used to discover the real backend server IP. |
| **`scanbt.py`** | `DHTScanner` | **BitTorrent DHT Network Mapper.** Actively crawls the BitTorrent Distributed Hash Table (DHT) network to build massive lists of active IP addresses (`dht_nodes.txt`) for use as attack infrastructure or targets. |
| **`quic.py`** | `QUICHunter` | **QUIC Protocol Scanner. Dedicated tool for hunting for open QUIC endpoints (port 443/UDP) and reliably measuring the QUIC Amplification Ratio by analyzing the size of the server's Initial packet response. |

### III. 📡 Advanced Layer 3/4 Attacks & Utilities

| Script | Primary Focus | Conceptual Analysis |
| :--- | :--- | :--- |
| **`ampbt.py`** | `DHTAmplificationWindows` | **BitTorrent DHT Amplification Attack.** Specialized module for Windows systems. Uses **RAW sockets** to send spoofed DHT queries (`get_peers`, `find_node`) to BitTorrent nodes, reflecting large responses to the victim's IP. |
| **`dnsamp.py`** | `DNSAmplificationEngine` | **Advanced DNS Reflector Attacker.** Optimized for maximum amplification. Supports multi-type queries (`ANY`, `DNSKEY`, `TXT`), full **RAW socket spoofing** for reflection, multi-threading, and a comprehensive CLI for targeted attacks. |

## 💡 Educational Context

This collection is a powerful resource for **security researchers** and **network defenders** seeking to understand the mechanics of highly effective, multi-layered DDoS attacks. By analyzing the implementation of these techniques, one can better design and deploy defensive measures, especially against **Protocol Exhaustion** (SYN Flood, ICMP Flood, TLS Renegotiation), **Amplification** (Memcached, DNS, NTP), and **Application-Layer Stress** (HTTP/2 Rapid Reset, WebSocket).

**If you find this archive useful for your studies:**

[Donate to the project maintainer](https://donatello.to/Adiru3)
