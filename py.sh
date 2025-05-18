nohup "while true; do ./pypya.sh || true; echo 'Retrying pypya.sh in 30s...'; sleep 30; done" > pyout.log 2>&1 &
