#!/usr/bin/env python3
"""
Simple /metrics HTTP exporter
Exposes Prometheus metrics via HTTP server
"""

import argparse
import os
import time
from prometheus_client import start_http_server
from observability.collector import metrics_enabled


def serve(port: int = 9108, addr: str = "0.0.0.0"):
    """Start the Prometheus metrics HTTP server"""
    start_http_server(port, addr=addr)
    print(f"[obs] Prometheus exporter on http://{addr}:{port}/metrics")
    
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("[obs] exporter stopped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AdvancedRules Metrics Exporter")
    parser.add_argument(
        "--port", 
        type=int, 
        default=int(os.getenv("AR_METRICS_PORT", "9108")),
        help="Port to serve metrics on (default: 9108)"
    )
    parser.add_argument(
        "--addr", 
        default=os.getenv("AR_METRICS_ADDR", "0.0.0.0"),
        help="Address to bind to (default: 0.0.0.0)"
    )
    
    args = parser.parse_args()
    
    if not metrics_enabled():
        print("AR_ENABLE_METRICS!=1 → metrics disabled (exporter will still serve empty registry)")
    
    serve(args.port, args.addr)