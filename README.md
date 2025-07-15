# Correction Chicken
Simple dictation error correction commands. Depends on community.

## Toggling
Saying "correction chicken" toggles the commands on and off. 

## Interface
The last text dictated using the phrase community history is shown. The display can be moved to the current cursor position with the command `correction chicken move`. The display will temporarily disappear after a time out if the user does not dictate text or make corrections. The timeout can be adjusted by changing the `user.correction_chicken_graphics_time_out` setting. 

## Homophones
A word recognized as a homophone will be shown in the interface with an exclamation mark or star after its number. An exclamation mark means that there is only one known alternative. 

Example:

<img width="130" height="108" alt="example of how homophones are denoted" src="https://github.com/user-attachments/assets/d59bebcd-9366-4071-9d3e-2f6bfe99dd28" />

One has an exclamation mark because there is only one alternative word. too has a star because there is more than one alternative. 

Dictating `phony` followed by the number of a homophone will replace it with the next homophone in the list. This can be done multiple times to cycle through the homophones. 

Dictating `phony (user.letter) (word number)` will replace the homophone with the alternative that has the specified letter the most number of times. 

Multiple letters can be dictated to use an alternative with that sequence of letters.

The word number can be omitted for the last homophone dictated. If the word number is omitted when using multiple letters, the last word with an alternative containing that sequence of letters will be used.

## Saving Manual Corrections
A correction rule can be manually added to the correction_data directory in a .csv file. The first colum is the text to replace and the second column is the replacement text. 

Example:
```
man,main,
and put,input,
wive,with,
docks,docs,
as,is,
shodan,chicken,
pole,pull,
avoid,void,
your,year,
moth,month,
```

It would be inconvenient to have to open a file every time you want to save a correction, so there are commands for saving manual corrections documented below.

Possible corrections using your manual rules will show up in the interface and can be accepted with `court (correction number)`. 

Example:

<img width="130" height="108" alt="example of how homophones are denoted" src="https://github.com/user-attachments/assets/d59bebcd-9366-4071-9d3e-2f6bfe99dd28" />

`court 2` would replace too with tool.

