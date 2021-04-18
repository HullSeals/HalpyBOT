# Fact syntax

HalpyBOT uses a simple syntax for facts that allow them to be
formatted and customized when creating or editing them. 

## Formatting


### Bold/Italics/Underlined

Pretty straightforward:

`<<BOLD>>text<<BOLD>>`
`<<ITALICS>>text<<ITALICS>>`
`<<UNDERLINED>>text<<UNDERLINED>>`

## No args

Facts can normally be supplied arguments that are placed in front of the 
fact, this is typically used to get the attention of clients. Sometimes, it's
desirable to specify a default argument that's used when no others are supplied
by the user invoking them

`{{default argument, }}Normal fact text`

## Newline

For adding a newline, use `%n%`
