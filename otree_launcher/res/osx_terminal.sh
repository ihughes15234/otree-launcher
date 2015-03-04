#!/bin/sh


frontWindow=$(
  echo '
  on run argv
    if length of argv is equal to 0
      set command to ""
    else
      set command to item 1 of argv
    end if
    runSimple(command)
  end run

  on runSimple(command)
    tell application "Terminal"
      activate
      do script(command)
      set frontWindow to window 1
    end tell
    return frontWindow
    
  end runSimple

  ' | osascript - "$@"
)




