nohup "while true; do ./main.sh || true; echo 'Retrying main.sh in 30s...'; sleep 30; done" > mainout.log 2>&1 &
