zsh -hold -title "Peer 2" -e "python3 p2p.py 2 4 5 20" &
zsh -hold -title "Peer 3" -e "python3 p2p.py 4 5 8 20" &
zsh -hold -title "Peer 4" -e "python3 p2p.py 5 8 9 20" &
zsh -hold -title "Peer 5" -e "python3 p2p.py 8 9 14 20" &
zsh -hold -title "Peer 8" -e "python3 p2p.py 9 14 19 20" &
zsh -hold -title "Peer 10" -e "python3 p2p.py 14 19 2 20" &
zsh -hold -title "Peer 12" -e "python3 p2p.py 19 2 4 20" &
