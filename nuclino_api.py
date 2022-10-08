from typing import Optional, cast
import nuclino
import nuclino.objects


def init_client(nuclino_key: str) -> nuclino.Nuclino:
    return nuclino.Nuclino(nuclino_key)


async def find_nuclino_item(
    nuclino_client: nuclino.Nuclino,
    workspace_id: str,
    text: str,
) -> Optional[nuclino.objects.Item]:
    items = cast("list[nuclino.objects.Item]", nuclino_client.get_items(
        workspace_id=workspace_id,
        search=text,
        limit=1,
    ))
    if len(items) == 0:
        return None
    return cast(nuclino.objects.Item, nuclino_client.get_item(items[0].id))


async def create_nuclino_item(
    nuclino_client: nuclino.Nuclino,
    parent_id: str,
    title: str,
    content: str,
) -> nuclino.objects.Item:
    return cast(nuclino.objects.Item, nuclino_client.create_item(
        parent_id=parent_id,
        object="item",
        title=title,
        content=content,
    ))
