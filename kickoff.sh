#!/bin/bash

WIN_MAIN="main"
WIN_GIT="git"

DIRNAME=$(dirname $0)
BASENAME=$(basename ${DIRNAME})  # parent directory name, e.g. "myproject"
PYVENV="${HOME}/venvs/${BASENAME}"
SOURCE_VENV="source ${PYVENV}/bin/activate"
COMBO="cd ${DIRNAME} && ${SOURCE_VENV} && clear"

# Start Kate editor with BASENAME session (or open existing).
kate -s $BASENAME

# Exit if tmux session already exists
tmux has-session -t $BASENAME 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Session already exists. Attaching..."
    tmux attach -t $BASENAME
    exit 0
fi

# Start a new detached (-d) tmux session (-s) named $BASENAME with main window.
tmux new-session -d -s $BASENAME -n $WIN_MAIN
tmux send-keys -t $BASENAME:$WIN_MAIN "$COMBO" C-m
tmux send-keys -t $BASENAME:$WIN_0 "python3 main.py" #C-m

tmux new-window -t $BASENAME -n $WIN_GIT
tmux send-keys -t $BASENAME:$WIN_GIT "cd $DIRNAME && clear" C-m
tmux send-keys -t $BASENAME:$WIN_GIT "git status" C-m

tmux select-window -t $BASENAME:$WIN_MAIN
tmux attach-session -t $BASENAME

exit 0
