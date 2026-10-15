import sqlite3

conn = sqlite3.connect('backend/time_machine.db')
c = conn.cursor()

# Clear stale empty cache entries
c.execute("DELETE FROM snapshot_cache_meta")
c.execute("DELETE FROM snapshots")
conn.commit()

print("Cleared all cache entries. Fresh CDX calls will be made on next request.")

conn.close()
