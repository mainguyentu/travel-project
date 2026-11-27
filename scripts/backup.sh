# Backup Postgres hàng ngày (U6 — RPO 24h, giữ 7 bản, on-call: project owner).
# Chạy từ host có docker compose:  sh scripts/backup.sh
# Lịch gợi ý (cron host): 0 2 * * * cd /path/travel-project && sh scripts/backup.sh
# Khôi phục: docker compose exec -T postgres psql -U postgres travel < backups/travel-YYYYMMDD-HHMMSS.sql
set -eu
KEEP="${BACKUP_KEEP:-7}"
DIR="${BACKUP_DIR:-./backups}"
mkdir -p "$DIR"
STAMP="$(date +%Y%m%d-%H%M%S)"
FILE="$DIR/travel-$STAMP.sql"
docker compose exec -T postgres pg_dump -U postgres travel > "$FILE"
ls -1t "$DIR"/travel-*.sql | tail -n +$((KEEP + 1)) | xargs -r rm -f
echo "backup ok: $FILE (giữ tối đa $KEEP bản)"
