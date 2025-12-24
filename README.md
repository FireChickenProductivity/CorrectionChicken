# Correction Chicken
Simple dictation error correction commands. Depends on community.

## Toggling
Saying "correction chicken" toggles the commands on and off. 

## Interface
The last text dictated using the phrase community history is shown. The display can be moved to the current cursor position with the command `correction chicken move`. The display will temporarily disappear after a time out if the user does not dictate text or make corrections. The timeout can be adjusted by changing the `user.correction_chicken_graphics_time_out` setting. 

To customize the interface, see settings.talon.

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

Manual corrections require specifying what part of the text to replace and what to replace it with.

`spelling (word number)` specifies the word to replace. `spelling (word number) through (word number)` specifies a range of words to replace.

`spelling (letters)` specifies the replacement word. You can alternatively use `wording (word)` to avoid having to spell the word if it is in your vocabulary. `phrasing (phrase)` uses the dictated phrase for the correction.

`replace` makes the correction without saving it, and `replace save` makes and saves the correction. 

For convenience, a single word correction can be done with `spelling (word number) (letters)` or `wording (word number) (word)`.

When words match a correction rule, the rule is only shown as a correction option if the number of the characters in the relevant words that match the rule divided by the total number of characters in the relevant words exceeds the `user.correction_chicken_correction_percentage_match_threshold` setting. This is 0.5 by default requiring more than half of the characters in the relevant words match. If a correction rule matches only a single word, then more than that percentage of a word must match for the corresponding correction option to be shown. 

## Convenience Commands for Common Misrecognition Patterns
`trim (word number)` removes the last letter of the word. This is useful for situations where a word gets misrecognized as having an extra d or s at the end, such as "an" getting misrecognized as "and".

`chop (word number)` removes the last 2 letters of the word. 

`eddy (word number)` makes the specified word end with "ed". 

`plural (word number)` makes the specified word end with "s".

`dual (word number)` makes the specified word end with "es".

`remove (token number)` removes the specified token from the text.