import sqlite3

conn = sqlite3.connect('backend/time_machine.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", [r[0] for r in c.fetchall()])

c.execute("SELECT * FROM snapshot_cache_meta")
rows = c.fetchall()
print(f"\nCache meta entries: {len(rows)}")
for r in rows:
    print(f"  URL: {dict(r)}")

c.execute("SELECT COUNT(*) FROM snapshots")
print(f"\nTotal snapshots: {c.fetchone()[0]}")

c.execute("SELECT url, COUNT(*) as cnt FROM snapshots GROUP BY url")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]} snapshots")

conn.close()
