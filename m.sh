nohup sh -c "while true; do (chmod +x main.sh && ./main.sh) || true; echo 'Retrying main.sh in 30s...'; sleep 30; done" > mainout.log 2>&1 &
