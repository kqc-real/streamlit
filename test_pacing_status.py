#!/usr/bin/env python3
"""
Test script for pacing status validation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pacing_helper import pacing_status, compute_ideal_times

def test_pacing_status():
    """Test the pacing_status function with various scenarios"""

    # Test case 1: Normal pacing, on track
    ideal_times = [30, 30, 30, 30, 30]  # 5 questions, 30s each
    total_allowed_seconds = 300  # 5 minutes total

    # At question 2 (index 1), elapsed 60s, should be green
    status = pacing_status(60, ideal_times, 1, total_allowed_seconds)
    print(f"Test 1 - On track: {status} (expected: green)")
    assert status == "green", f"Expected green, got {status}"

    # Test case 2: Ahead of schedule
    status = pacing_status(45, ideal_times, 1, total_allowed_seconds)  # 15s ahead
    print(f"Test 2 - Ahead: {status} (expected: ahead)")
    assert status == "ahead", f"Expected ahead, got {status}"

    # Test case 3: Behind schedule but projected to finish on time
    status = pacing_status(90, ideal_times, 1, total_allowed_seconds)  # 30s behind, pct=0.5
    print(f"Test 3 - Behind but on track: {status} (expected: yellow)")
    assert status == "yellow", f"Expected yellow, got {status}"

    # Test case 4: Very low remaining time (should be red)
    status = pacing_status(250, ideal_times, 3, total_allowed_seconds)  # 50s left for 2 questions
    print(f"Test 4 - Low time: {status} (expected: red)")
    assert status == "red", f"Expected red, got {status}"

    # Test case 5: Projected to exceed time
    status = pacing_status(200, ideal_times, 2, total_allowed_seconds)  # 100s left, but 120s needed for remaining 4 questions
    print(f"Test 5 - Projected exceed: {status} (expected: red)")
    assert status == "red", f"Expected red, got {status}"

    print("✅ All pacing status tests passed!")

if __name__ == "__main__":
    test_pacing_status()