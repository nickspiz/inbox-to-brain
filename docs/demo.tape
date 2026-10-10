# Same demo as demo.gif, for charmbracelet/vhs:  vhs docs/demo.tape
# (docs/render_demo.py draws the committed GIF without needing vhs.)
Output docs/demo.gif
Set Shell "bash"
Set FontSize 15
Set Width 1000
Set Height 540
Set Padding 20
Set TypingSpeed 35ms
Set Theme "Dracula"
Hide
Type "D=$(mktemp -d) && R=$PWD && cp -r $R/starter-vault $D/my-vault && cp $R/examples/sample-inbox/*.md $D/my-vault/00_Inbox/ && cp $R/router.py $R/validator.py $R/notes.py $D/ && cd $D && PS1='$ ' && clear"
Enter
Show
Type "ls my-vault/00_Inbox"
Enter
Sleep 2s
Hide
Type "clear"
Enter
Show
Type "python3 router.py --vault my-vault"
Enter
Sleep 3s
Hide
Type "clear"
Enter
Show
Type "python3 router.py --vault my-vault --apply"
Enter
Sleep 2s
Hide
Type "clear"
Enter
Show
Type "cd my-vault && find Projects Knowledge 00_Inbox -name '*.md' | sort"
Enter
Sleep 3s
