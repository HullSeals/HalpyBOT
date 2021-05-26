# HAPIC Info

Routes for setting VHOSTS via HalpyBOT.

# Routes

***

## POST `/tail`

### Description:

Set a user's VHOST via SETALL commands by looking up the user's names in the database as provided.

On success, a 200 is returned.

### Usage:

```json
{
    "rank": "The level at which the user is being set, ex seal or pup.",
    "subject": "The name of the Seal - preferably the main/primary name in use."
}```

### Example:

```json
{
    "rank": "seal",
    "subject": "Rixxan"
}```

Outputs:

On success, a 200: OK is returned.

***
