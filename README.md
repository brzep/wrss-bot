# wrss-bot
Discord bot enchancing WRSS WIET &amp; WI workflow


## functions:

### seen
- adding `seen` reaction to every post on main channel in order to easily show that user has read the message

### threads
- opening thread with name specified in message
- syntax for opening thread with `[thread name]`
```
[thread name]
Lorem ipsum dolor sit amet, consectetur adipiscing elit.
```

### doodle hub
- searches for doodle links in all messages and forwards them do channel begin doodle hub along with reference to original message
- makes sure all doodles are in one place, so you can fill them easily :)
- adds `checkbox` reaction to all doodles on doodle channel to allow you for easily marking filled in doodles
- supported doodle links can be specified in `config.py` file

### reaction message
- starts every thread with message showing all reactions to original posts
- made because on mobile devices it was impossible to see reactions to original post while reading thread

### [cd]
- adds `seen` reaction to message with `[cd]` in it even if it is inside of a thread
- made when I was posting messages extending discord message length limit, so I had to continue them in threads, but still wanted people to be able to react with `seen` to them

### polls
- automatically adds survey-reactions to post based on message content
- syntax:
```
> - emote0 option-0-description
> - emote1 option-1-description
```

### all-message-notification
- automatically pings users with specified rank in all threads to allow them for receiving notifications about all new messages
