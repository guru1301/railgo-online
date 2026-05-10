import pkg_resources

with open("pip_freeze_utf8.txt", "w", encoding="utf-8") as f:
    for dist in pkg_resources.working_set:
        f.write(f"{dist.key}=={dist.version}\n")
