# Fact syntax

HalpyBOT uses a simple syntax for facts that allow them to be
formatted and customized when creating or editing them. 

## Formatting

### Colour (NOT SUPPORTED YET)

HalpyBOT will support three IRC colours: red, green, and blue.

`<<RED>>text<<RED>>`
`<<GREEN>>text<<GREEN>>`
`<<BLUE>>text<<BLUE>>`

### Bold

Text can be made bold:

`<<BOLD>>text<<BOLD>>`

## No args

Facts can normally be supplied arguments that are placed in front of the 
fact, this is typically used to get the attention of clients. Sometimes, it's
desirable to specify a default argument that's used when no others are supplied
by the user invoking them

`{{default argument, }}Normal fact text`

## Newline

For adding a newline, use `%n%`