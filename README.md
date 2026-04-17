# 📡 Network Traffic Classification using Mininet (SDN Project)

## 📌 Problem Statement

The objective of this project is to design and implement a **network traffic classification system** using Software Defined Networking (SDN) concepts. The system classifies network traffic based on protocol type (ICMP, TCP, UDP) and analyzes network behavior.

---

## 🎯 Objectives

* Create a network topology using Mininet
* Capture network traffic using tcpdump
* Classify packets into ICMP, TCP, and UDP
* Analyze network performance (latency and throughput)
* Demonstrate SDN-based traffic observation

---

## 🧠 Concept Used

* Software Defined Networking (SDN)
* OpenFlow-based switching (via Open vSwitch)
* Packet classification
* Network monitoring

---

## 🖥️ Tools & Technologies

* Ubuntu (Virtual Machine)
* Mininet
* tcpdump
* iperf
* Python (for HTTP server)

---

## 🌐 Network Topology

* 2 Hosts: h1, h2
* 1 Switch: s1

Topology:
h1 ---- s1 ---- h2

---

## ⚙️ Setup & Execution Steps

### Step 1: Start Mininet

```bash
sudo mn
```

---

### Step 2: Verify Connectivity

```bash
pingall
```

---

### Step 3: Start Packet Capture (New Terminal)

```bash
sudo tcpdump -i any -n
```

---

### Step 4: Generate ICMP Traffic

```bash
h1 ping h2
```

---

### Step 5: Generate TCP Traffic

```bash
h2 python3 -m http.server 80 &
h1 wget http://10.0.0.2
```

---

### Step 6: Generate UDP Traffic

```bash
h2 iperf -s &
h1 iperf -c h2 -u
```

---

### Step 7: Stop tcpdump

Press:
Ctrl + C

---

## 📊 Expected Output

### ICMP Traffic

* Observed using ping
* tcpdump shows: ICMP echo request/reply

### TCP Traffic

* Generated using HTTP request
* tcpdump shows: TCP packets

### UDP Traffic

* Generated using iperf
* tcpdump shows: UDP packets

---

## 📈 Performance Analysis

### Latency (Ping)

* Measured using ping command
* Shows round-trip time (RTT)
* Indicates network delay

### Throughput (iperf)

* Measured using iperf
* Indicates data transfer rate

---

## 📊 Traffic Classification

| Protocol | Description                        |
| -------- | ---------------------------------- |
| ICMP     | Ping communication                 |
| TCP      | Reliable connection (HTTP)         |
| UDP      | Fast, connectionless communication |

---

## 🔍 Observations

* ICMP traffic shows low latency
* TCP traffic ensures reliable communication
* UDP traffic provides faster transmission
* Packet classification helps analyze network behavior

---

## 📸 Proof of Execution

Include screenshots of:

* Mininet topology
* pingall output
* tcpdump capturing ICMP, TCP, UDP
* iperf results

---

## ✅ Conclusion

This project successfully demonstrates how network traffic can be classified based on protocol type using Mininet and tcpdump. It also shows how SDN concepts help in monitoring and analyzing network behavior.

---

## 📚 References

* Mininet Documentation
* Ubuntu Documentation
* tcpdump Manual
* iperf Documentation

---
