#!/usr/bin/env python3
"""
Roblox Tweet Processing Script - Fixed Version
Handles timezone issues, syntax errors, and missing dependencies
"""

import json
import sys
from datetime import datetime, timedelta, timezone
import pytz
from typing import List, Dict

def load_json_data(json_str: str) -> List[Dict]:
    """Safely load JSON data"""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}", file=sys.stderr)
        return []

def parse_twitter_timestamp(timestamp_str: str) -> datetime:
    """Parse Twitter timestamp with proper timezone handling"""
    try:
        # Twitter timestamps are typically in ISO format with timezone
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt
    except ValueError as e:
        print(f"Timestamp parse error: {e}", file=sys.stderr)
        # Fallback to current time if parsing fails
        return datetime.now(timezone.utc)

def filter_new_tweets(tweets: List[Dict], last_run_time: datetime) -> List[Dict]:
    """Filter tweets newer than last run time with proper timezone handling"""
    new_tweets = []
    
    # Ensure last_run_time is timezone-aware (UTC)
    if last_run_time.tzinfo is None:
        last_run_time = last_run_time.replace(tzinfo=timezone.utc)
    
    for tweet in tweets:
        try:
            created_at = parse_twitter_timestamp(tweet.get('created_at', ''))
            
            # Ensure created_at is timezone-aware
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            
            # Compare timezone-aware datetimes
            if created_at > last_run_time:
                new_tweets.append(tweet)
                
        except Exception as e:
            print(f"Error processing tweet: {e}", file=sys.stderr)
            continue
    
    return new_tweets

def main():
    """Main processing function"""
    try:
        # Read input from stdin
        input_data = sys.stdin.read()
        
        # Parse JSON input
        tweets = load_json_data(input_data)
        
        # Get last run time (would be passed as argument or from state file)
        # For now, use 6 hours ago as default
        last_run_time = datetime.now(timezone.utc) - timedelta(hours=6)
        
        # Filter new tweets
        new_tweets = filter_new_tweets(tweets, last_run_time)
        
        # Output filtered tweets as JSON
        print(json.dumps(new_tweets, indent=2))
        
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
