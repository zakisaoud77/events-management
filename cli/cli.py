import click
import asyncio
from app.crud import events_crud
from app.models.events import *
from app.db.mongodb import create_mongodb_connection, close_mongodb_connection

@click.group()
def cli():
    pass

@cli.command("add-event")
@click.option("--start", required=True, help="Start datetime")
@click.option("--stop", default=None, help="Stop datetime")
@click.option("--tags", multiple=True, help="Tags for the event")
def add_event_command(start, stop, tags):
    try:
        asyncio.run(add_event(start, stop, tags))
    except Exception as e:
        click.echo(f"Failed: {e}", err=True)
        raise SystemExit(1)

async def add_event(start, stop, tags):
    await create_mongodb_connection()
    try:
        event = EventCreate(
            start=start,
            stop=stop if stop else None,
            tags=list(tags)
        )
        new_event = await events_crud.create_event(event)
        click.echo(f"Created new event: {new_event}")
    finally:
        await close_mongodb_connection()

@cli.command("list-all-events")
@click.option("--skip", default=0)
@click.option("--limit", default=10)
def list_all_events_command(skip, limit):
    try:
        asyncio.run(list_events(skip, limit))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

async def list_events(skip, limit):
    await create_mongodb_connection()
    try:
        events = await events_crud.get_all_events(skip=skip, limit=limit)
        for event in events['results']:
            click.echo(f"Event with ID: {event.id}, Start time: {event.start} "
                       f"- Stop time: {event.stop} | Tags: {event.tags}")
    finally:
        await close_mongodb_connection()

@cli.command("list-running-events")
@click.option("--skip", default=0)
@click.option("--limit", default=10)
def list_running_events_command(skip, limit):
    try:
        asyncio.run(list_running_events(skip, limit))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

async def list_running_events(skip, limit):
    await create_mongodb_connection()
    try:
        events = await events_crud.get_running_events(skip=skip, limit=limit)
        for event in events['results']:
            click.echo(f"Running event with ID: {event.id}, Start time: {event.start} "
                       f"- Stop time: {event.stop} | Tags: {event.tags}")
    finally:
        await close_mongodb_connection()

@cli.command("delete-event")
@click.option("--event_id")
@click.option("--force_delete", default=False)
def delete_event_command(event_id, force_delete):
    try:
        asyncio.run(delete_event_from_id(event_id, force_delete))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

async def delete_event_from_id(event_id, force_delete):
    await create_mongodb_connection()
    try:
        event_deleted = await events_crud.delete_event(event_id, force_delete)
        if event_deleted:
            click.echo(f"Event with ID {event_id}, has been deleted successfully")
        else:
            click.echo(f"Event with ID {event_id}, cannot be deleted")
    finally:
        await close_mongodb_connection()

@cli.command("delete-all-events")
@click.option("--force_delete", default=False)
def delete_all_events_command(force_delete):
    try:
        asyncio.run(delete_events(force_delete))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

async def delete_events(force_delete):
    await create_mongodb_connection()
    try:
        total_events, deleted_events = await events_crud.delete_all_events(force_delete)
        if total_events == deleted_events > 0:
            click.echo(f"All of {deleted_events} events have been deleted successfully")
        elif total_events > deleted_events > 0:
            click.echo(f"All of {deleted_events} stopped events have been deleted successfully")
        elif total_events == deleted_events == 0:
            click.echo(f"There is no events to delete ! all events have been deleted")
        else:
            click.echo(f"We cannot delete events, because there is only running events and force_delete=False")
    finally:
        await close_mongodb_connection()

@cli.command("search-event")
@click.option("--skip", default=0)
@click.option("--limit", default=10)
@click.option("--tags", multiple=True, help="Tags used for searching events")
def searching_event_command(tags, skip, limit):
    try:
        asyncio.run(searching_event(tags, skip, limit))
    except Exception as e:
        click.echo(f"Failed: {e}", err=True)
        raise SystemExit(1)

async def searching_event(tags, skip, limit):
    await create_mongodb_connection()
    try:
        events = await events_crud.search_event(tags, skip, limit)
        for event in events['results']:
            click.echo(f"Found event with ID: {event.id}, Start time: {event.start} "
                       f"- Stop time: {event.stop} | Tags: {event.tags}")
    finally:
        await close_mongodb_connection()

@cli.command("update-event-tags")
@click.option("--event_id")
@click.option("--replace", default=False)
@click.option("--tags", multiple=True, help="Tags used for searching events")
def updating_event_tags_command(event_id, replace, tags):
    try:
        asyncio.run(updating_event_tags(event_id, replace, tags))
    except Exception as e:
        click.echo(f"Failed: {e}", err=True)
        raise SystemExit(1)

async def updating_event_tags(event_id, replace, tags):
    await create_mongodb_connection()
    try:
        updated_event = await events_crud.updating_event_tags(event_id, tags, replace)
        click.echo(f"Updated event: {updated_event}")
    finally:
        await close_mongodb_connection()

@cli.command("update-event-datetime")
@click.option("--event_id")
@click.option("--start", required=True, help="Start datetime")
@click.option("--stop", default=None, help="Stop datetime")
def updating_event_datetime_command(event_id, start, stop):
    try:
        asyncio.run(updating_event_date(event_id, start, stop))
    except Exception as e:
        click.echo(f"Failed: {e}", err=True)
        raise SystemExit(1)

async def updating_event_date(event_id, start, stop):
    await create_mongodb_connection()
    try:
        updated_event = await events_crud.updating_event_datetime(event_id, start, stop)
        click.echo(f"Updated event: {updated_event}")
    finally:
        await close_mongodb_connection()

@cli.command("update-event-datetime-by-tags")
@click.option("--tags", multiple=True, help="Tags used for searching events")
@click.option("--start", required=True, help="Start datetime")
@click.option("--stop", default=None, help="Stop datetime")
def updating_event_datetime_by_tags_command(tags, start, stop):
    try:
        asyncio.run(updating_event_date_by_tags(list(tags), start, stop))
    except Exception as e:
        click.echo(f"Failed: {e}", err=True)
        raise SystemExit(1)

async def updating_event_date_by_tags(tags, start, stop):
    await create_mongodb_connection()
    try:
        updated_events_count, matched_events_count = await events_crud.update_events_based_on_tags(tags, start, stop)
        if updated_events_count > 0:
            click.echo(f"{updated_events_count} events datetime have been updated successfully")
        elif updated_events_count == 0 and matched_events_count > 0:
            click.echo(f"Events with tags {tags} have been already updated with the same start and stop times")
        else:
            click.echo(f"There is no events to update with the tags {tags}")
    finally:
        await close_mongodb_connection()

if __name__ == "__main__":
    cli()