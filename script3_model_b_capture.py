#!/usr/bin/env python3
"""
Script 3 - Model B Transcript Capture

This script:
1. Captures transcript/log from Script 2 (Model B run)
2. Saves before code state, after code state, and git_diff.patch in session folder
3. Finalizes the annotation workflow

Usage: python script3_model_b_capture.py
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from utils import (
    get_current_timestamp, create_code_snapshot, create_git_diff,
    save_session_metadata, load_session_metadata,
    validate_git_repository, reset_git_to_commit, extract_claude_transcript_data
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


def print_final_summary(session_a_id: str, session_b_id: str, task_id: str):
    """Print final workflow summary."""
    print("\n" + "="*80)
    print("ANNOTATION WORKFLOW COMPLETE")
    print("="*80)
    print(f"Task ID: {task_id}")
    print(f"Model A Session: {session_a_id}/")
    print(f"Model B Session: {session_b_id}/")
    print("\nSession Directories Created:")
    print(f"📁 TASK-{task_id}/")
    print(f"   ├── {session_a_id}/            # Model A Session")
    print(f"   │   ├── session_metadata.json")
    print(f"   │   ├── claude_transcript.log")
    print(f"   │   └── snapshots/")
    print(f"   │       ├── before_code_state/")
    print(f"   │       ├── after_code_state/")
    print(f"   │       └── git_diff.patch")
    print(f"   └── {session_b_id}/            # Model B Session")
    print(f"       ├── session_metadata.json")
    print(f"       ├── claude_transcript.log")
    print(f"       └── snapshots/")
    print(f"           ├── before_code_state/")
    print(f"           ├── after_code_state/")
    print(f"           └── git_diff.patch")
    print("\nNext Steps:")
    print(f"1. Upload the entire TASK-{task_id}/ folder to Google Drive:")
    print("   https://drive.google.com/drive/folders/1xZom5X3iCFjVcQzsXJfuJw96RGWpkowd?usp=drive_link")
    print("2. Log session details in Airtable")
    print("3. Include Drive link to the uploaded task folder in Airtable")
    print("="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Capture Model B transcript and finalize annotation workflow")
    
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
        
        if len(session_dirs) < 2:
            raise Exception(f"Need 2 sessions in task {task_id}. Please run script1_model_a_init.py and script2_model_b_init.py first.")
        
        # Sort by modification time - Model B should be the most recent
        session_dirs.sort(key=lambda d: d.stat().st_mtime)
        session_a_dir = session_dirs[-2]  # Second most recent (Model A)
        session_b_dir = session_dirs[-1]  # Most recent (Model B)
        
        session_a_id = session_a_dir.name
        session_b_id = session_b_dir.name
        
        print(f"📁 Found Model A session: {session_a_id}")
        print(f"📁 Found Model B session: {session_b_id}")

        transcript_file = session_b_dir / "claude_transcript.log"
    
        if not transcript_file.exists():
            raise Exception(f"Claude transcript file not found: {transcript_file}.")
        
        # Load Model B session metadata
        session_b_metadata = load_session_metadata(str(session_b_dir))
        task_id = session_b_metadata["task_id"]
        base_commit = session_b_metadata["base_commit"]
        timestamp_start_b = session_b_metadata["timestamp_start"]
        
        print(f"📋 Finalizing Model B session...")
        print(f"Model B Session ID: {session_b_id}")
        print(f"Model A Session ID: {session_a_id}")
        print(f"Task ID: {task_id}")
        print(f"Base Commit: {base_commit}")
        
        # session_b_dir and session_b_metadata already loaded above
        
        # Finalize Model B session
        timestamp_end_b = get_current_timestamp()
        duration_b = calculate_duration(timestamp_start_b, timestamp_end_b)
        code_changes_b = count_code_changes(base_commit)
        
        # Create after snapshot for Model B
        after_snapshot_path_b = session_b_dir / "snapshots" / "after_code_state"
        create_code_snapshot(str(after_snapshot_path_b))
        
        # Create git diff for Model B
        diff_path_b = session_b_dir / "snapshots" / "git_diff.patch"
        create_git_diff(str(diff_path_b), base_commit)
        
        # Extract transcript data for Model B
        turns_b, transcript_b = extract_transcript_for_session(session_b_dir)
        
        # Update Model B metadata FIRST
        session_b_metadata.update({
            "timestamp_end": timestamp_end_b,
            "total_duration": duration_b,
            "total_code_changes": code_changes_b,
            "workflow_stage": "model_b_complete",
            "turns": turns_b,
            "transcript": transcript_b
        })
        
        save_session_metadata(str(session_b_dir), session_b_metadata)
        
        # Also update Model A session metadata with transcript data if not already done
        try:
            session_a_metadata = load_session_metadata(str(session_a_dir))
            
            # Check if transcript data is already present
            if "turns" not in session_a_metadata or "transcript" not in session_a_metadata:
                print(f"📝 Updating Model A session metadata with transcript data...")
                turns_a, transcript_a = extract_transcript_for_session(session_a_dir)
                
                session_a_metadata.update({
                    "turns": turns_a,
                    "transcript": transcript_a
                })
                
                save_session_metadata(str(session_a_dir), session_a_metadata)
                print(f"✅ Model A session metadata updated with transcript data")
            else:
                print(f"✅ Model A session already has transcript data")
                
        except Exception as e:
            print(f"⚠️  Could not update Model A session metadata: {e}")
        
        print(f"✅ Model B session finalized:")
        print(f"   Duration: {duration_b} seconds")
        print(f"   Code changes: {code_changes_b} files")
        print(f"   Turns: {turns_b}")
        print(f"   Transcript interactions: {len(transcript_b)}")
        
        
        
        # Print final summary
        print_final_summary(session_a_id, session_b_id, task_id)
        
        print(f"\n✅ Script 3 completed successfully!")
        print(f"🎉 Annotation workflow complete for task: {task_id}")
        
        # Provide Airtable logging template
        print("\n📝 Airtable Logging Information:")
        print(f"Task ID: {task_id}")
        print(f"Base Commit: {base_commit}")
        print(f"Model A Session ID: {session_a_id}")
        print(f"Model B Session ID: {session_b_id}")
        print(f"Model A Directory: TASK-{task_id}/{session_a_id}/")
        print(f"Model B Directory: TASK-{task_id}/{session_b_id}/")
        print("(Add Drive links after uploading)")
        
        # Reset repository to base commit for next task
        print(f"\n🔄 Resetting repository for next task...")
        reset_git_to_commit(base_commit)
        print(f"✅ Repository reset to base commit - ready for next task!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
