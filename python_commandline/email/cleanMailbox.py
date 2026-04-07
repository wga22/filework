import mailbox

def clean():
    mbox = mailbox.mbox('/var/mail/will')
    mbox.lock()
    try:
        keys_to_remove = []
#        target_subject = 'Cron <will@spiderman> /junk/scripts/generals.sh'
#        target_subject = 'Cron <will@spiderman> /junk/scripts/generals.sh'
#        target_subject = 'Cron <will@spiderman> /junk/scripts/generals.sh'
        target_subject = 'Cron <will@spiderman> /opt/tasmota/landscapeLights.sh'
        for key, msg in mbox.items():
            if msg['subject'] == target_subject:
                keys_to_remove.append(key)
        for key in keys_to_remove:
            mbox.remove(key)
            print(f"Remove {key}")
        mbox.flush()
        print(f"Successfully removed {len(keys_to_remove)} messages.")
    finally:
        mbox.unlock()

clean()
