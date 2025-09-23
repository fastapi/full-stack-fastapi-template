#!/usr/bin/env python3
"""
Shared utility functions for Claude Code annotation scripts.
"""

import os
import re
import json
import uuid
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return f"S{uuid.uuid4().hex[:8]}"


def generate_uuid() -> str:
    """Generate a UUID for the session."""
    return str(uuid.uuid4())


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.utcnow().isoformat() + "Z"


def get_available_models() -> Dict[str, str]:
    """Get the available Claude models for annotation."""
    return {
        "claude-brocade-v22-p": "claude-brocade-v22-p",
        "claude-opus-4-1-20250805": "claude-opus-4-1-20250805"
    }


def select_random_model() -> str:
    """Randomly select a model for Model A."""
    import random
    models = get_available_models()
    return random.choice(list(models.keys()))


def get_opposite_model(model_id: str) -> str:
    """Get the opposite model for Model B given Model A."""
    models = get_available_models()
    for model_name in models.keys():
        if model_name != model_id:
            return model_name
    raise Exception(f"Could not find opposite model for: {model_id}")


def get_git_commit_hash() -> str:
    """Get the current git commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to get git commit hash: {e}")


def reset_git_to_commit(commit_hash: str) -> None:
    """Reset git repository to a specific commit and clean all changes, but preserve annotation scripts."""
    try:
        print(f"🔄 Resetting repository to base commit: {commit_hash}")
        
        # List of annotation scripts to preserve
        script_files = [
            'script1_model_a_init.py',
            'script2_model_b_init.py', 
            'script3_model_b_capture.py',
            'utils.py',
            'README.md'  # In case it's the annotation README
        ]
        
        # Backup annotation scripts to parent directory (outside repo)
        backup_dir = Path("../.annotation_scripts_backup")
        backup_dir.mkdir(exist_ok=True)
        
        for script_file in script_files:
            if Path(script_file).exists():
                shutil.copy2(script_file, backup_dir / script_file)
        
        print("   ✅ Annotation scripts backed up")
        
        # Hard reset to the base commit (removes staged and unstaged changes)
        subprocess.run(
            ["git", "reset", "--hard", commit_hash],
            check=True,
            capture_output=True
        )
        
        # Clean untracked files and directories (removes new files)
        subprocess.run(
            ["git", "clean", "-fd"],
            check=True,
            capture_output=True
        )
        
        # Restore annotation scripts
        print("   🔄 Restoring annotation scripts...")
        for script_file in script_files:
            backup_path = backup_dir / script_file
            if backup_path.exists():
                shutil.copy2(backup_path, script_file)
                print(f"      ✅ Restored {script_file}")
        
        print(f"✅ Repository completely reset to commit: {commit_hash}")
        print("   - All staged changes removed")
        print("   - All modifications reverted") 
        print("   - All new files removed")
        print("   - Annotation scripts preserved")
        print("   - Working directory clean")
        
        # Clean up backup directory
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
            print("   ✅ Backup directory cleaned up")
        
    except subprocess.CalledProcessError as e:
        # Clean up backup directory if it exists
        backup_dir = Path("../.annotation_scripts_backup")
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        raise Exception(f"Failed to reset git to commit {commit_hash}: {e}")
    except Exception as e:
        # Clean up backup directory if it exists
        backup_dir = Path("../.annotation_scripts_backup")
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        raise Exception(f"Failed to reset git to commit {commit_hash}: {e}")


def create_code_snapshot(snapshot_path: str) -> None:
    """Create a complete snapshot of the entire repository using simple mkdir and cp."""
    snapshot_dir = Path(snapshot_path)
    current_repo = Path.cwd()
    
    print(f"📦 Creating complete repository snapshot...")
    
    # Create the snapshot directory
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    # Simple cp command to copy everything
    result = subprocess.run([
        'cp', '-r', '.', str(snapshot_dir)
    ], cwd=str(current_repo), capture_output=True, text=True)
    
    # Remove annotation script files from the snapshot
    script_files = [
        'script1_model_a_init.py',
        'script2_model_b_init.py', 
        'script3_model_b_capture.py',
        'utils.py'
    ]
    
    for script_file in script_files:
        script_path = snapshot_dir / script_file
        if script_path.exists():
            script_path.unlink()
    
    print(f"✅ Complete repository snapshot created at: {snapshot_path}")
    
    # Count files for verification
    try:
        result = subprocess.run(['find', str(snapshot_dir), '-type', 'f'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            file_count = len(result.stdout.strip().split('\n'))
            print(f"   📁 {file_count} files captured")
    except:
        print(f"   📁 Repository snapshot completed")


def create_git_diff(output_path: str, base_commit: str) -> None:
    """Create a git diff patch file including all changes from base commit to current state."""
    try:
        print(f"📦 Creating git diff from base commit...")
        
        # Stage ALL changes first (modified + new files)
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        print("   ✅ All changes staged")
        
        # Get complete diff from staged area
        result = subprocess.run(
            ["git", "diff", "--cached", base_commit],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Filter out annotation scripts from the diff
        if result.stdout.strip():
            lines = result.stdout.split('\n')
            filtered_lines = []
            skip_file = False
            
            for line in lines:
                # Check if this is a diff header for annotation scripts or unwanted files
                if line.startswith('diff --git'):
                    # Extract filename from diff header: diff --git a/file b/file
                    if any(script in line for script in [
                        'script1_model_a_init.py', 'script2_model_b_init.py', 
                        'script3_model_b_capture.py', 'utils.py', 'README.md',
                        '.claude/', '__pycache__', '.pyc', 'node_modules', '.DS_Store']):
                        skip_file = True
                        continue
                    else:
                        skip_file = False
                
                if not skip_file:
                    filtered_lines.append(line)
            
            filtered_diff = '\n'.join(filtered_lines)
        else:
            filtered_diff = ""
        
        # Write filtered diff to file
        with open(output_path, 'w') as f:
            f.write(filtered_diff)
        
        # Check if file has content
        if Path(output_path).stat().st_size > 0:
            print(f"✅ Git diff created at: {output_path}")
            
            # Count changes for verification
            diff_lines = filtered_diff.count('\ndiff --git')
            if diff_lines > 0:
                print(f"   📊 {diff_lines} files changed")
        else:
            print(f"⚠️  Git diff created but no changes detected: {output_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Error creating git diff: {e}")
        # Create empty file so script doesn't fail
        with open(output_path, 'w') as f:
            f.write(f"# Error creating git diff: {e}\n")
    except Exception as e:
        print(f"⚠️  Error creating git diff: {e}")
        with open(output_path, 'w') as f:
            f.write(f"# Error creating git diff: {e}\n")


def save_session_metadata(session_dir: str, metadata: Dict[str, Any]) -> None:
    """Save session metadata to JSON file."""
    metadata_path = Path(session_dir) / "session_metadata.json"
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Session metadata saved to: {metadata_path}")


def load_session_metadata(session_dir: str) -> Dict[str, Any]:
    """Load session metadata from JSON file."""
    metadata_path = Path(session_dir) / "session_metadata.json"
    
    if not metadata_path.exists():
        raise FileNotFoundError(f"Session metadata not found at: {metadata_path}")
    
    with open(metadata_path, 'r') as f:
        return json.load(f)


def create_session_directory(session_id: str, task_id: str, model_label: str) -> str:
    """Create session directory structure under TASK-<task_id> folder parallel to the repository."""
    # Create task folder with TASK- prefix parallel to current repository
    current_repo = Path.cwd()
    parent_dir = current_repo.parent
    task_dir_name = f"TASK-{task_id}"
    task_dir = parent_dir / task_dir_name
    task_dir.mkdir(exist_ok=True)
    
    # Create session directory with model label (modelA or modelB)
    session_dir_name = f"{session_id}-{model_label}"
    session_dir = task_dir / session_dir_name
    session_dir.mkdir(exist_ok=True)
    
    # Create snapshots subdirectory
    snapshots_dir = session_dir / "snapshots"
    snapshots_dir.mkdir(exist_ok=True)
    
    print(f"✅ Task directory created: {task_dir}")
    print(f"✅ Session directory created: {session_dir}")
    return str(session_dir)






def print_session_summary(session_id: str, model_id: str, base_commit: str) -> None:
    """Print a summary of the session setup."""
    print("\n" + "="*60)
    print(f"SESSION SETUP COMPLETE")
    print("="*60)
    print(f"Session ID: {session_id}")
    print(f"Model ID: {model_id}")
    print(f"Base Commit: {base_commit}")
    print(f"Session Directory: {session_id}/")
    print("="*60)
    print(f"4. Run the next script when ready")
    print("="*60 + "\n")


def validate_git_repository() -> None:
    """Validate that we're in a git repository."""
    if not Path('.git').exists():
        raise Exception("Not in a git repository. Please run this script from the root of your git repository.")


def check_git_status() -> bool:
    """Check if there are uncommitted changes."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        return len(result.stdout.strip()) > 0
    except subprocess.CalledProcessError:
        return False


def initialize_claude_code(model_id: str, session_id: str) -> bool:
    """
    Initialize Claude Code session with API key and model name only.
    """
    print(f"🚀 Starting Claude Code session...")
    print(f"Model: {model_id}")
    
    # Set the API key environment variable
    api_key = "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"
    os.environ["ANTHROPIC_API_KEY"] = api_key
    print("🔑 API key exported")
    
    # Create transcript log file in the most recent session directory
    current_repo = Path.cwd()
    parent_dir = current_repo.parent
    
    # Find session directories in task folders
    task_dirs = [d for d in parent_dir.iterdir() if d.is_dir() and d.name.startswith('TASK-')]
    session_dirs = []
    
    for task_dir in task_dirs:
        for item in task_dir.iterdir():
            if item.is_dir() and item.name.startswith('S') and ('-modelA' in item.name or '-modelB' in item.name):
                session_dirs.append(item)
    
    if session_dirs:
        # Use the most recent session directory
        session_dir = max(session_dirs, key=lambda d: d.stat().st_mtime)
        transcript_file = session_dir / "claude_transcript.txt"
    else:
        # Fallback to current directory
        transcript_file = Path("claude_transcript.txt")
    
    # Launch Claude Code and capture output
    try:
        print("🚀 Starting Claude Code...")
        print("💡 After completing your task, exit Claude Code to continue with the next script.")
        print(f"📝 Export the transcript to: {transcript_file}")
        print("\n" + "="*50)
        print("CLAUDE CODE SESSION STARTING")
        print("="*50)
        print(f"Model: {model_id}")
        print("="*50)
        print()
        
        # Start claude command with the environment and capture output
        env = os.environ.copy()
        env["ANTHROPIC_API_KEY"] = api_key
        
        # Use script command to capture terminal session including user input
        claude_cmd = ["claude", "--model", model_id]
        
        # Try with script command first (captures full terminal session)
        try:
            result = subprocess.run(
                claude_cmd,
                cwd=os.getcwd(),
                env=env
            )
            print(f"✅ Claude Code transcript saved to: {transcript_file}")
        except (FileNotFoundError, subprocess.CalledProcessError):
            # Fallback: run claude directly without transcript capture
            print("⚠️  Script command not available, running claude directly...")
            result = subprocess.run(
                claude_cmd,
                cwd=os.getcwd(),
                env=env
            )
            print("⚠️  Transcript capture not available - please manually save conversation if needed")
        
        print("\n" + "="*50)
        print("CLAUDE CODE SESSION ENDED")
        print("="*50)
        print("✅ Claude Code session completed!")
        print("🔄 Ready to proceed to next step...")
        print("="*50)
        
        return True
        
    except FileNotFoundError:
        print("❌ Error: `claude` command not found in PATH")
        print("\nFallback: Run these commands manually:")
        print(f"  cd {os.getcwd()}")
        print(f"  script {transcript_file} claude --model {model_id}  # (captures transcript)")
        print(f"  # OR just: claude --model {model_id}  # (no transcript)")
        return False
        
    except KeyboardInterrupt:
        print("\n⚠️  Claude Code session interrupted by user")
        return True
        
    except Exception as e:
        print(f"❌ Error starting Claude Code: {e}")
        print("\nFallback: Run these commands manually:")
        print(f"  cd {os.getcwd()}")
        print(f"  script {transcript_file} claude --model {model_id}  # (captures transcript)")
        return False


def wait_for_claude_session_start(session_id: str, timeout: int = 30) -> bool:
    """
    Wait for Claude Code session to start by checking for session indicators.
    """
    print(f"⏳ Waiting for Claude Code session to start (timeout: {timeout}s)...")
    
    import time
    start_time = time.time()
    
    # Look for indicators that Claude Code session has started
    session_indicators = [
        f".claude_session_{session_id}.lock",
        ".cursor/claude_active",
        ".vscode/claude_active",
        "claude_session.log"
    ]
    
    while time.time() - start_time < timeout:
        for indicator in session_indicators:
            if Path(indicator).exists():
                print(f"✅ Claude Code session detected via: {indicator}")
                return True
        
        time.sleep(1)
    
    print("⚠️  Could not detect Claude Code session start automatically")
    print("Please ensure Claude Code is running before proceeding")
    return False


def create_claude_prompt_file(session_dir: str, task_id: str) -> str:
    """
    Create a prompt template file for the user to use in Claude Code.
    """
    prompt_file = Path(session_dir) / "task_prompt.txt"
    current_repo = Path.cwd().name
    
    prompt_template = f"""# Task ID: {task_id}

## Instructions
Paste your task prompt below this line, then copy the entire content to Claude Code:

---

[PASTE YOUR TASK PROMPT HERE]

---

## Session Info
- Task ID: {task_id}
- Repository: {current_repo}
- Session Directory: {session_dir}
- Timestamp: {get_current_timestamp()}

## Notes
- This file is for reference only
- Copy the prompt section to Claude Code
- Complete the task as requested
- Do not commit changes until instructed by the next script
- Session data is saved parallel to your repository
"""
    
    with open(prompt_file, "w") as f:
        f.write(prompt_template)
    
    print(f"📝 Prompt template created: {prompt_file}")
    return str(prompt_file)

def extract_claude_transcript_data(file_path: str):
    """
    Extract human inputs, AI responses, and tool calls from Claude transcript files.
    Handles ANSI escape sequences, multi-line prompts, and long responses.
    Returns ordered transcript with role and content, including separate tool_call role.
    """
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Step 1: Clean ANSI escape codes and terminal control sequences
    # Remove actual ANSI escape sequences (with \x1B prefix)
    cleaned_content = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', content)
    
    # Remove literal ANSI code strings that appear as text in transcripts
    terminal_patterns = [
        r'\[\?[0-9]+[hl]',  # DEC private mode sequences like [?25l, [?2004h
        r'\[38;2;[0-9]+;[0-9]+;[0-9]+m',  # RGB color codes like [38;2;215;119;87m
        r'\[39m|\[49m',  # Reset foreground/background color
        r'\[1m|\[22m|\[2m|\[23m|\[3m|\[4m|\[24m|\[7m|\[27m',  # Text formatting toggles
        r'\[[0-9]+m',  # Simple color codes
        r'\[[0-9;]+m',  # Multiple parameter color codes
        r'\]0;[^\\]*\\',  # Window title sequences
    ]
    
    for pattern in terminal_patterns:
        cleaned_content = re.sub(pattern, '', cleaned_content)
    
    # Remove control characters and special Unicode symbols
    cleaned_content = re.sub(r'[\x00-\x08\x0B-\x1F\x7F-\x9F]', '', cleaned_content)
    cleaned_content = re.sub(r'[╭╮│╰╯─═║┌┐└┘├┤┬┴┼]', '', cleaned_content)  # Box drawing
    # Note: ⎿ is a tool result marker, not decorative - keep it!
    cleaned_content = re.sub(r'\(B', '', cleaned_content)  # Terminal artifacts
    
    # Clean up excessive whitespace
    cleaned_content = re.sub(r'  +', ' ', cleaned_content)
    cleaned_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_content)
    
    # Step 2: Split content into lines for processing
    lines = cleaned_content.split('\n')
    
    # Step 3: Extract interactions using improved logic
    transcript = []
    # Enhanced status pattern to filter out tool operation noise
    status_pattern = r'(\.\.\.|\…|ing…|ing\.\.\.|esc to interrupt|Forging|Transfiguring|Ideating|Combobulating|Crunching|Accomplishing|Waiting|Running|Total cost|Total duration|Usage by model|ctrl\+o to expand|\(.+\s+tokens\)|\(.+\s+lines\)|Found \d+ files|Found \d+ lines|Found \d+ matches|No content|Error:|Done \(|\.\.\. \+\d+ lines)'
    
    seen_interactions = set()
    current_human = []
    current_ai = []
    current_tool_call = None
    tool_calls = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Human input (starts with >)
        if line.startswith('> '):
            # Save any pending AI content first
            if current_ai:
                ai_text = ' '.join(current_ai).strip()
                if len(ai_text) > 10 and not re.search(status_pattern, ai_text):
                    if ai_text not in seen_interactions:
                        transcript.append({"role": "agent", "content": ai_text})
                        seen_interactions.add(ai_text)
                current_ai = []
            
            # Start collecting human input
            current_human = [line[2:].strip()]
            
        # AI response or tool call (starts with ⏺ or other symbols) - check this first!
        elif re.match(r'^[⏺✻·✽✶✳✢]\s', line):
            # Save any pending human content first
            if current_human:
                human_text = ' '.join(current_human).strip()
                if len(human_text) > 1:
                    if human_text not in seen_interactions:
                        transcript.append({"role": "human", "content": human_text})
                        seen_interactions.add(human_text)
                current_human = []  # Clear human content
            
            # Save any pending tool call first
            if current_tool_call:
                tool_calls.append(current_tool_call)
                if current_tool_call['content'] not in seen_interactions:
                    transcript.append({"role": "tool_call", "content": current_tool_call['content']})
                    seen_interactions.add(current_tool_call['content'])
                current_tool_call = None
            
            # Extract content (remove the symbol prefix)
            content = re.sub(r'^[⏺✻·✽✶✳✢]\s*', '', line).strip()
            if len(content) > 5 and not re.search(status_pattern, content):
                # Check if this is a tool call (has parentheses with parameters)
                tool_match = re.match(r'^(\w+)\(([^)]*)\)$', content)
                if tool_match:
                    # This is a tool call
                    tool_name = tool_match.group(1)
                    parameters = tool_match.group(2)
                    current_tool_call = {
                        'tool_name': tool_name,
                        'parameters': parameters,
                        'output': '',
                        'content': f"{tool_name}({parameters})"
                    }
                else:
                    # This is regular AI narrative
                    current_ai.append(content)
                
        # Tool result (starts with ⎿) - always part of current tool call
        elif line.strip().startswith('⎿') and current_tool_call:
            # Tool result continuation
            result_content = line.strip()[1:].strip()  # Remove ⎿ and whitespace
            if current_tool_call['output']:
                current_tool_call['output'] += '\n' + result_content
            else:
                current_tool_call['output'] = result_content
            current_tool_call['content'] = f"{current_tool_call['tool_name']}({current_tool_call['parameters']}) → {result_content[:100]}{'...' if len(result_content) > 100 else ''}"
                
        # Continuation of human input (indented lines or plain lines after a human prompt)
        elif current_human and (line.startswith('  ') or 
                               (not line.startswith('>') and 
                                not re.match(r'^[⏺✻·✽✶✳✢]', line) and
                                not line.strip().startswith('⎿') and
                                not current_ai and  # Only if we're not in an AI response
                                len(line) > 3)):
            current_human.append(line.strip())
                
        # Continuation of AI response (plain text lines)
        elif (current_ai and 
              not line.startswith('>') and 
              not re.match(r'^[⏺✻·✽✶✳✢]', line) and
              not line.strip().startswith('⎿') and
              not re.search(status_pattern, line) and
              len(line) > 3):
            current_ai.append(line)
    
    # Handle any remaining content
    if current_human:
        human_text = ' '.join(current_human).strip()
        if len(human_text) > 1:
            if human_text not in seen_interactions:
                transcript.append({"role": "human", "content": human_text})
    
    if current_tool_call:
        tool_calls.append(current_tool_call)
        if current_tool_call['content'] not in seen_interactions:
            transcript.append({"role": "tool_call", "content": current_tool_call['content']})
    
    if current_ai:
        ai_text = ' '.join(current_ai).strip()
        if len(ai_text) > 10 and not re.search(status_pattern, ai_text):
            if ai_text not in seen_interactions:
                transcript.append({"role": "agent", "content": ai_text})
    
    # Legacy format for backward compatibility
    human_inputs = [item["content"] for item in transcript if item["role"] == "human"]
    ai_responses = [item["content"] for item in transcript if item["role"] == "agent"]
    
    return {
        'transcript': transcript,
        'human_inputs': human_inputs,
        'ai_responses': ai_responses,
        'tool_calls': tool_calls,
        'human_count': len(human_inputs),
        'ai_count': len(ai_responses),
        'tool_call_count': len(tool_calls)
    }
