# 🔄 Sync Database from Replit to Local

## Current Status:
✅ Local database backed up to analytics.db.local-backup
✅ .gitignore is ready (database tracking temporarily enabled)
⏳ Waiting for Replit to push its database

---

## ⚡ STEP 1: IN REPLIT SHELL - RUN THESE COMMANDS:

```bash
git pull origin main
git add analytics.db
git commit -m "Add Replit production database with real analytics data"
git push origin main
```

---

## ⚡ STEP 2: BACK HERE LOCALLY - RUN:

```bash
git pull origin main
ls -lh analytics.db
```

---

## ⚡ STEP 3: RE-ENABLE PROTECTION - Uncomment lines in .gitignore then:

```bash
git add .gitignore
git commit -m "Re-enable database protection"
git push origin main
```
