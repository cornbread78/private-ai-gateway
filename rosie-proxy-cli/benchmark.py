#!/usr/bin/env python3
"""
Rosie AI Gateway - Latency & Throughput Benchmark Tool
Measures request latency, throughput (requests/sec), and status code distribution.
"""

import time
import json
import urllib.request
import urllib.error
import argparse
import concurrent.futures
import os

def send_request(url, api_key, payload):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    start_time = time.perf_counter()
    status_code = 0
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.status
            _ = response.read()
    except urllib.error.HTTPError as e:
        status_code = e.code
    except Exception:
        status_code = 500

    latency_ms = (time.perf_counter() - start_time) * 1000
    return status_code, latency_ms

def run_benchmark(target_url, api_key, total_requests, concurrency):
    print(f"[+] Target: {target_url}")
    print(f"[+] Total Requests: {total_requests} | Concurrency Level: {concurrency}\n")

    payload = {
        "model": "rosie-private",
        "messages": [{"role": "user", "content": "Benchmark test request."}]
    }

    latencies = []
    status_counts = {}

    start_total_time = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [
            executor.submit(send_request, target_url, api_key, payload)
            for _ in range(total_requests)
        ]

        for future in concurrent.futures.as_completed(futures):
            code, latency = future.result()
            latencies.append(latency)
            status_counts[code] = status_counts.get(code, 0) + 1

    total_duration = time.perf_counter() - start_total_time

    # Calculate statistics
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    min_latency = min(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0
    rps = total_requests / total_duration if total_duration > 0 else 0

    print("--- Benchmark Results ---")
    print(f"Total Time Elapsed:   {total_duration:.2f} s")
    print(f"Throughput:           {rps:.2f} req/sec")
    print(f"Average Latency:      {avg_latency:.2f} ms")
    print(f"Min Latency:          {min_latency:.2f} ms")
    print(f"Max Latency:          {max_latency:.2f} ms")
    print("\nStatus Codes Breakdown:")
    for code, count in status_counts.items():
        print(f"  HTTP {code}: {count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rosie AI Gateway Benchmark Tool")
    parser.add_argument("--url", default="http://localhost:8080/v1/chat/completions", help="Gateway URL")
    parser.add_argument("--key", default=os.environ.get("ROSIE_API_KEY", "rosie-secret-key-123"), help="API Key")
    parser.add_argument("-n", "--requests", type=int, default=50, help="Total number of requests")
    parser.add_argument("-c", "--concurrency", type=int, default=5, help="Number of concurrent workers")

    args = parser.parse_args()
    run_benchmark(args.url, args.key, args.requests, args.concurrency)
