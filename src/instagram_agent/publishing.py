from dataclasses import dataclass
from typing import Protocol


class InstagramClient(Protocol):
    def create_container(self, video_url: str, caption: str) -> str: ...
    def container_status(self, container_id: str) -> str: ...
    def publish(self, container_id: str) -> str: ...


@dataclass(frozen=True)
class PublishRequest:
    package_id: int
    video_url: str
    caption: str
    approved: bool
    render_valid: bool
    unsupported_claims: list[str]


def publish_reel(
    request: PublishRequest, client: InstagramClient, published_package_ids: set[int]
) -> tuple[str, str]:
    if not request.approved or not request.render_valid or request.unsupported_claims:
        raise PermissionError("Publication gates are not satisfied")
    if request.package_id in published_package_ids:
        raise ValueError("Package has already been published")
    container = client.create_container(request.video_url, request.caption)
    if client.container_status(container) != "FINISHED":
        raise RuntimeError("Media container is not ready")
    media_id = client.publish(container)
    published_package_ids.add(request.package_id)
    return container, media_id
