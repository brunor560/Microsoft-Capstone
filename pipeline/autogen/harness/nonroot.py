"""Non-root policy for local Docker and rootless Podman."""
import json
import os

def user_identity():
    uid = getattr(os, "getuid", lambda: 0)()
    gid = getattr(os, "getgid", lambda: 0)()
    if uid <= 0 or gid <= 0:
        raise RuntimeError("Run as a non-root Linux/WSL or macOS user.")
    return f"{uid}:{gid}"

def is_podman(client):
    return "podman" in json.dumps(client.version()).lower()

def create_nonroot(original, collection, image, command, kwargs):
    kwargs.update(
        user=user_identity(), cap_drop=["ALL"],
        security_opt=["no-new-privileges"], privileged=False,
        use_config_proxy=False,
    )
    env = kwargs.get("environment") or {}
    if not isinstance(env, dict):
        env = dict(item.split("=", 1) for item in env)
    kwargs["environment"] = dict(env, HOME="/tmp")

    if not is_podman(collection.client):
        return original(collection, image, command, **kwargs)

    api = collection.client.api
    saved = api.create_container

    def mapped_create(*args, **options):
        options["host_config"]["UsernsMode"] = "keep-id"
        return saved(*args, **options)

    api.create_container = mapped_create
    try:
        return original(collection, image, command, **kwargs)
    finally:
        api.create_container = saved

def cli_options():
    import docker
    identity = user_identity()
    client = docker.from_env()
    try:
        podman = is_podman(client)
    finally:
        client.close()
    options = [
        "--user", identity, "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--env", "HOME=/tmp",
    ]
    if podman:
        options += ["--userns", "keep-id"]
    return options
