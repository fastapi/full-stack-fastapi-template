#!/usr/bin/env python3
"""
Script 1 - Model A Initialization

This script:
1. Takes the initial checkpoint (records the initial before code state)
2. Records the most recent commit ID in transcript/log metadata
3. Sets up Claude Model A (model_id: A)
4. Starts a new Claude Code session for the task
5. Stores transcript/log + before/after code states + diff inside the session ID folder

Usage: python script1_model_a_init.py [task_id]
"""

import sys
import argparse
from pathlib import Path
from utils import (
    generate_session_id, generate_uuid, get_current_timestamp,
    get_git_commit_hash, create_code_snapshot, create_session_directory,
    save_session_metadata, print_session_summary, validate_git_repository,
    check_git_status, initialize_claude_code, select_random_model
)


def main():
    parser = argparse.ArgumentParser(description="Initialize Model A session for Claude Code annotation")
    parser.add_argument("task_id", help="Task ID for this annotation session")
    
    args = parser.parse_args()
    
    # Randomly select Model A
    model_a = select_random_model()
    print(f"🎲 Randomly selected Model A: {model_a}")
    
    args.model_id = model_a
    
    try:
        # Validate we're in a git repository
        validate_git_repository()
        
        # Generate session identifiers
        session_id = generate_session_id()
        session_uuid = generate_uuid()
        base_commit = get_git_commit_hash()
        timestamp_start = get_current_timestamp()
        
        print(f"🚀 Initializing Model A session...")
        print(f"Task ID: {args.task_id}")
        print(f"Session ID: {session_id}")
        print(f"Model ID: {args.model_id}")
        print(f"Base Commit: {base_commit}")
        
        # Check for uncommitted changes
        if check_git_status():
            print("⚠️  Warning: You have uncommitted changes in your repository.")
            response = input("Do you want to continue? (y/N): ")
            if response.lower() != 'y':
                print("❌ Aborting...")
                return 1
        
        # Create session directory structure under task folder
        session_dir = create_session_directory(session_id, args.task_id, "modelA")
        snapshots_dir = Path(session_dir) / "snapshots"
        
        # Create initial code snapshot (before state)
        before_snapshot_path = snapshots_dir / "before_code_state"
        create_code_snapshot(str(before_snapshot_path))
        
        # Prepare session metadata
        metadata = {
            "task_id": args.task_id,
            "session_id": session_id,
            "uuid": session_uuid,
            "base_commit": base_commit,
            "model_id": args.model_id,
            "timestamp_start": timestamp_start,
            "timestamp_end": None,  # Will be filled by script 2
            "total_duration": None,  # Will be calculated by script 2
            "total_cost": None,  # To be filled manually or by transcript analysis
            "total_code_changes": None,  # Will be calculated by script 2
            "snapshot_paths": {
                "before": f"TASK-{args.task_id}/{session_id}/snapshots/before_code_state/",
                "after": f"TASK-{args.task_id}/{session_id}/snapshots/after_code_state/",
                "diff": f"TASK-{args.task_id}/{session_id}/snapshots/git_diff.patch"
            },
            "transcript": [],  # Will be filled when transcript is captured
            "turns": 0,  # Will be filled when transcript is captured
            "script_version": "1.0",
            "workflow_stage": "model_a_init"
        }
        
        # Save session metadata
        save_session_metadata(session_dir, metadata)
        
        # Create placeholder files for later stages
        (snapshots_dir / "after_code_state").mkdir(exist_ok=True)
        (snapshots_dir / "git_diff.patch").touch()
        
        # Initialize Claude Code session
        claude_initialized = initialize_claude_code(args.model_id, session_id)
        
        # Print session summary and next steps
        print_session_summary(session_id, args.model_id, base_commit)
        
        
        if claude_initialized:
            print("Run script2_model_b_init.py when ready")
            print("=" * 50)
        
        print(f"\n✅ Script 1 completed successfully!")
        print(f"📁 Session directory: {session_dir}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
