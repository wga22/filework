import mailbox
import sys
import os
import getpass

def clean():
    if len(sys.argv) < 2:
        print("Usage: sudo python3 deleteMailBySubject.py 'Subject Substring'")
        sys.exit(1)

    # Use a substring approach to bypass line-wrap issues
    target_substring = sys.argv[1].strip().lower()
    # Identify the user (root in this case)
    current_user = getpass.getuser()
    mbox_path = f'/var/mail/{current_user}'
    if not os.path.exists(mbox_path):
        print(f"Error: {mbox_path} not found.")
        sys.exit(1)

    mbox = mailbox.mbox(mbox_path)
    mbox.lock()
    try:
        keys_to_remove = []
        for key, msg in mbox.items():
            # Get the subject, handle None types, and normalize
            msg_subject = str(msg.get('subject', '')).replace('\n', ' ').strip().lower()
            # Check if our target exists anywhere in the subject
            if target_substring in msg_subject:
                keys_to_remove.append(key)
        for key in keys_to_remove:
            mbox.remove(key)
        mbox.flush()
        print(f"Matched and removed {len(keys_to_remove)} messages containing '{target_substring}'.")
    finally:
        mbox.unlock()

if __name__ == "__main__":
    clean()
