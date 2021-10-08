def route_tags() -> str:
    return "/tags/"


def route_tag(tag_id: int) -> str:
    return route_tags() + str(tag_id)
