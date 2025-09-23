#!/usr/bin/env python3
"""
Script 2 - Model B Initialization

This script:
1. Captures transcript/log from Script 1 (Model A)
2. Saves snapshot: before code state, after code state, and git_diff.patch
3. Resets git state to the base commit (fresh start)
4. Starts a new Claude Code session with Model B (model_id: B)
5. Stores transcript/log + before/after code states + diff inside the session ID folder

Usage: python script2_model_b_init.py
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from utils import (
    generate_session_id, generate_uuid, get_current_timestamp,
    reset_git_to_commit, create_code_snapshot, create_git_diff,
    create_session_directory, save_session_metadata, load_session_metadata,
    print_session_summary, validate_git_repository,
    initialize_claude_code, get_opposite_model, extract_claude_transcript_data
)


def calculate_duration(start_time: str, end_time: str) -> int:
    """Calculate duration in seconds between two ISO timestamps."""
    start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    return int((end - start).total_seconds())


def count_code_changes(base_commit: str) -> int:
    """Count the number of files changed from base commit."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base_commit],
            capture_output=True,
            text=True,
            check=True
        )
        files_changed = result.stdout.strip().split('\n') if result.stdout.strip() else []
        return len(files_changed)
    except subprocess.CalledProcessError:
        return 0


def extract_transcript_for_session(session_dir: Path) -> tuple:
    """
    Extract transcript data from claude_transcript.log in session directory.
    Returns (turns, transcript) tuple.
    """
    transcript_file = session_dir / "claude_transcript.log"
    
    if not transcript_file.exists():
        print(f"⚠️  Transcript file not found: {transcript_file}")
        return 0, []
    
    try:
        print(f"📝 Extracting transcript data from: {transcript_file}")
        transcript_data = extract_claude_transcript_data(str(transcript_file))
        turns = transcript_data['human_count']
        transcript = transcript_data['transcript']
        
        print(f"   ✅ Extracted {turns} human turns and {len(transcript)} total interactions")
        return turns, transcript
        
    except Exception as e:
        print(f"⚠️  Error extracting transcript data: {e}")
        return 0, []


def main():
    parser = argparse.ArgumentParser(description="Initialize Model B session after completing Model A")
    
    args = parser.parse_args()
    
    
    try:
        # Validate we're in a git repository
        validate_git_repository()
        
        # Find the most recent TASK- directory
        current_repo = Path.cwd()
        parent_dir = current_repo.parent
        
        # Find directories that start with TASK-
        task_dirs = [d for d in parent_dir.iterdir() 
                    if d.is_dir() and d.name.startswith('TASK-')]
        
        if not task_dirs:
            raise Exception("No TASK- directories found. Please run script1_model_a_init.py first.")
        
        # Use the most recently modified TASK- directory
        task_dir = max(task_dirs, key=lambda d: d.stat().st_mtime)
        task_id = task_dir.name.replace('TASK-', '')  # Extract actual task ID
        
        print(f"📁 Using most recent task directory: TASK-{task_id}")
        
        # Find session directories in this task directory (with model identifier)
        session_dirs = [item for item in task_dir.iterdir() 
                       if item.is_dir() and item.name.startswith('S') and ('-modelA' in item.name or '-modelB' in item.name)]
        
        if not session_dirs:
            raise Exception(f"No Model A session found in task directory {task_id}. Please run script1_model_a_init.py first.")
        
        # Use the most recent session directory (should be Model A)
        session_a_dir = max(session_dirs, key=lambda d: d.stat().st_mtime)
        session_a_id = session_a_dir.name
        
        print(f"📁 Found Model A session: {session_a_id}")

        transcript_file = session_a_dir / "claude_transcript.log"
    
        if not transcript_file.exists():
            raise Exception(f"Claude transcript file not found: {transcript_file}.")
        
        # Load session metadata
        session_a_metadata = load_session_metadata(str(session_a_dir))
        task_id = session_a_metadata["task_id"]
        base_commit = session_a_metadata["base_commit"]
        timestamp_start_a = session_a_metadata["timestamp_start"]
        model_a_id = session_a_metadata["model_id"]
        
        # Determine Model B (opposite of Model A)
        model_b_id = get_opposite_model(model_a_id)
        
        print(f"🔄 Model A was: {model_a_id}")
        print(f"🎯 Model B will be: {model_b_id}")
        
        args.model_id = model_b_id
        
        print(f"🔄 Transitioning from Model A to Model B...")
        print(f"Model A Session ID: {session_a_id}")
        print(f"Task ID: {task_id}")
        print(f"Base Commit: {base_commit}")
        
        # session_a_dir and session_a_metadata already loaded above
        
        # Finalize Model A session
        timestamp_end_a = get_current_timestamp()
        duration_a = calculate_duration(timestamp_start_a, timestamp_end_a)
        code_changes_a = count_code_changes(base_commit)
        
        # Create after snapshot for Model A
        after_snapshot_path_a = session_a_dir / "snapshots" / "after_code_state"
        create_code_snapshot(str(after_snapshot_path_a))
        
        # Create git diff for Model A
        diff_path_a = session_a_dir / "snapshots" / "git_diff.patch"
        create_git_diff(str(diff_path_a), base_commit)
        
        # Extract transcript data for Model A
        turns_a, transcript_a = extract_transcript_for_session(session_a_dir)
        
        # Update Model A metadata FIRST
        session_a_metadata.update({
            "timestamp_end": timestamp_end_a,
            "total_duration": duration_a,
            "total_code_changes": code_changes_a,
            "workflow_stage": "model_a_complete",
            "turns": turns_a,
            "transcript": transcript_a
        })
        
        save_session_metadata(str(session_a_dir), session_a_metadata)
        
        
        print(f"✅ Model A session finalized:")
        print(f"   Duration: {duration_a} seconds")
        print(f"   Code changes: {code_changes_a} files")
        print(f"   Turns: {turns_a}")
        print(f"   Transcript interactions: {len(transcript_a)}")
        
        # Reset git to base commit for fresh start
        print(f"\n🔄 Resetting repository to base commit...")
        reset_git_to_commit(base_commit)
        
        # Generate new session for Model B
        session_b_id = generate_session_id()
        session_b_uuid = generate_uuid()
        timestamp_start_b = get_current_timestamp()
        
        print(f"\n🚀 Initializing Model B session...")
        print(f"Session ID: {session_b_id}")
        print(f"Model ID: {args.model_id}")
        
        # Create Model B session directory structure in the same task folder
        session_b_dir = create_session_directory(session_b_id, task_id, "modelB")
        snapshots_b_dir = Path(session_b_dir) / "snapshots"
        
        # Create initial code snapshot for Model B (should be same as Model A's before state)
        before_snapshot_path_b = snapshots_b_dir / "before_code_state"
        create_code_snapshot(str(before_snapshot_path_b))
        
        # Prepare Model B session metadata
        metadata_b = {
            "task_id": task_id,
            "session_id": session_b_id,
            "uuid": session_b_uuid,
            "base_commit": base_commit,
            "model_id": args.model_id,
            "timestamp_start": timestamp_start_b,
            "timestamp_end": None,  # Will be filled by script 3
            "total_duration": None,  # Will be calculated by script 3
            "total_cost": None,  # To be filled manually or by transcript analysis
            "total_code_changes": None,  # Will be calculated by script 3
            "snapshot_paths": {
                "before": f"TASK-{task_id}/{session_b_id}/snapshots/before_code_state/",
                "after": f"TASK-{task_id}/{session_b_id}/snapshots/after_code_state/",
                "diff": f"TASK-{task_id}/{session_b_id}/snapshots/git_diff.patch"
            },
            "transcript": [],  # Will be filled when transcript is captured
            "turns": 0,  # Will be filled when transcript is captured
            "script_version": "1.0",
            "workflow_stage": "model_b_init",
            "related_session": {
                "model_a_session_id": session_a_id,
                "comparison_pair": True
            }
        }
        
        # Save Model B session metadata
        save_session_metadata(session_b_dir, metadata_b)
        
        # Create placeholder files for later stages
        (snapshots_b_dir / "after_code_state").mkdir(exist_ok=True)
        (snapshots_b_dir / "git_diff.patch").touch()
        
        # Initialize Claude Code session for Model B
        claude_initialized = initialize_claude_code(args.model_id, session_b_id)
        
        # Print session summary and next steps
        print_session_summary(session_b_id, args.model_id, base_commit)
        
        if claude_initialized:
            print(f"\n🎯 READY FOR MODEL B TASK!")
            print("=" * 50)
            print("1. Claude Code should now be running (fresh session)")
            print("2. Repository has been reset to base commit")
            print("3. Use the SAME task prompt as Model A")
            print("4. Enter the prompt directly in Claude Code")
            print("5. Complete the task with Model B")
            print(f"6. Export the transcript to: {session_b_dir}/claude_transcript.log")
            print("7. Exit Claude Code when done")
            print("8. Run script3_model_b_capture.py when ready")
            print("=" * 50)
        
        print(f"\n✅ Script 2 completed successfully!")
        print(f"📁 Model A session: {session_a_dir}")
        print(f"📁 Model B session: {session_b_dir}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
