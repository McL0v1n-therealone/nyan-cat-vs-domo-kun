#!/usr/bin/env bash
# Copies the vidya to a real PSP connected in USB mode, then safely ejects it.
# usage: ./deploy-psp.sh [wait_seconds]   (default: wait up to 120 s for the PSP)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
EBOOT="$HERE/build/EBOOT.PBP"
GAME_DIR_NAME="NyanCatVsDomo"
WAIT="${1:-120}"

[ -f "$EBOOT" ] || { echo "No build found at $EBOOT - run 'make' in build/ first." >&2; exit 1; }

# find the PSP's partition by its USB model string ("PSP")
find_psp() {
    lsblk -rno NAME,TYPE,MODEL | awk '$2=="disk" && $3 ~ /PSP/ {print $1}' | head -1
}

echo "Waiting for the PSP (Settings > USB Connection on the PSP)..."
DISK=""
for ((i = 0; i < WAIT; i++)); do
    DISK="$(find_psp)"
    [ -n "$DISK" ] && break
    sleep 1
done
[ -n "$DISK" ] || { echo "PSP not found after ${WAIT}s." >&2; exit 1; }

PART="/dev/${DISK}1"
[ -b "$PART" ] || PART="/dev/$DISK"     # some sticks have no partition table
sleep 1

MNT="$(lsblk -rno MOUNTPOINT "$PART" | head -1)"
if [ -z "$MNT" ]; then
    udisksctl mount -b "$PART" >/dev/null
    MNT="$(lsblk -rno MOUNTPOINT "$PART" | head -1)"
fi
echo "PSP memory stick mounted at: $MNT"

DEST="$MNT/PSP/GAME/$GAME_DIR_NAME"
mkdir -p "$DEST"
cp "$EBOOT" "$DEST/EBOOT.PBP"
sync
echo "Copied: $DEST/EBOOT.PBP ($(du -h "$EBOOT" | cut -f1))"

udisksctl unmount -b "$PART" >/dev/null && echo "Unmounted - safe to exit USB mode on the PSP."
