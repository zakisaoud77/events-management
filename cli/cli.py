import click
import asyncio
from app.crud.events_crud import *
from app.db.mongodb import create_mongodb_connection, close_mongodb_connection

@click.group()
def cli():
    pass

@cli.command("add-event")
@click.option("--start", required=True, help="Start datetime in ISO format")
@click.option("--stop", default=None, help="Stop datetime in ISO format")
@click.option("--tags", multiple=True, help="Tags for the event")
def add_event(start, stop, tags):
    try:
        asyncio.run(add_event_command(start, stop, tags))
    except Exception as e:
        click.echo(f"Failed: {e}", err=True)
        raise SystemExit(1)

async def add_event_command(start, stop, tags):
    await create_mongodb_connection()
    try:
        event = EventCreate(
            start=start,
            stop=stop if stop else None,
            tags=list(tags)
        )
        new_event = await create_event(event)
        click.echo(f"Created new event: {new_event}")
    finally:
        await close_mongodb_connection()


@cli.command("list-all-events")
@click.argument("skip", type=int)
@click.argument("limit", type=int)
def list_all_events_command(skip, limit):
    try:
        asyncio.run(list_events(skip, limit))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

async def list_events(skip, limit):
    await create_mongodb_connection()
    try:
        events = await get_all_events(skip=skip, limit=limit)
        for event in events['results']:
            click.echo(f"Event with ID {event.id}: Start time{event.start} - Stop time {event.stop} | Tags: {event.tags}")
    finally:
        await close_mongodb_connection()

if __name__ == "__main__":
    cli()