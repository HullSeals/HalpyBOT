import mysql

async def createDelayedCase(ctx, casestat, message):
    in_args = [casestat, message, ctx.author]
    