# iRoboCity2030 Summer School 2026 — ROS 2 Summer School

Teaching demos for the University of Gothenburg summer school on ROS 2, AI, and Field Robotics.

**Prerequisites:** Python 3 (DEMO0), Docker & Docker Compose (DEMO2).

---

## DEMO0 — Custom HTTP Server

A barebones HTTP/1.1 server built from scratch in Python using only the standard library. Serves static files from `public/` and echoes POST data at `/echo`.

```bash
cd DEMO0
python3 server.py
# Open http://localhost:8080
```
```bash
# filter traffic with:
http 
http || tcp
```

---

## DEMO1 — MATLAB ROS 1 Talker & Listener

ROS 1 publisher and subscriber written in MATLAB, each bound to a fixed port for easy Wireshark filtering.

**Prerequisites:** MATLAB with ROS Toolbox, a running ROS 1 master on `http://localhost:11311`.

```matlab
% Terminal 1: start talker (port 9090)
>> run DEMO1/talker.m

% Terminal 2: start listener (port 9091)
>> run DEMO1/listener.m

% Filter in Wireshark:
tcp.port == 9090 || tcp.port == 9091
```

---

## DEMO2 — ROS 2 Talker / Listener with Docker Compose

A containerized ROS 2 (Jazzy) pub/sub pair with `/toggle_talker` and `/toggle_listener` services, orchestrated via Docker Compose.

```bash
cd DEMO2
docker compose up -d
docker attach node1
```

```bash
source ../ros_entrypoint.sh
read -p "Press enter to continue"
ros2 node list
ros2 topic list
read -p "Press enter to continue"
ros2 service call /toggle_talker std_srvs/srv/Trigger
read -p "Press enter to continue"
ros2 service call /toggle_listener std_srvs/srv/Trigger
read -p "Press enter to continue"
ros2 service call /toggle_talker std_srvs/srv/Trigger
read -p "Press enter to continue"
ros2 service call /toggle_listener std_srvs/srv/Trigger
read -p "Press enter to continue"
```

```bash
cd DEMO2
docker compose down
```