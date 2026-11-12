"""Repository name check. The convention itself is partly judgement: whether a tool repo is named after its area
and piece well is reviewed by people. This module checks only the mechanical part: the form, the org prefix,
the stack-type suffixes, the fixed names (hub, template), the `<slug>-channel` pattern and the workspace
pairing."""

import re

from standards.ci import REPO_NAME

NAME_FORM = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
FORBIDDEN_SUFFIXES = ("-app", "-site", "-landing", "-repo")
EXEMPT_NAMES = (".github",)
HUB_NAME = "workspaces-hub"
TEMPLATE_NAME = "channel-template"
CHANNEL_SUFFIX = "-channel"
PREFIX = "inbetweenlabs-"


def _real_dir(path):
    return path.is_dir() and not path.is_symlink()


def _real_file(path):
    return path.is_file() and not path.is_symlink()


def check_repo_name(root, report, repo_name=None):
    if repo_name is None or REPO_NAME.fullmatch(repo_name) is None or repo_name in (".", ".."):
        report.add("repo-name", "WARN", ".", "no valid --repo-name was given, so the repository name was not checked")
        return
    if repo_name in EXEMPT_NAMES:
        return
    problems = []
    if NAME_FORM.fullmatch(repo_name) is None:
        problems.append("use lowercase letters, digits and single hyphens (^[a-z0-9]+(-[a-z0-9]+)*$)")
    if repo_name.startswith(PREFIX):
        problems.append("drop the inbetweenlabs- prefix: the organization is already the namespace")
    for suffix in FORBIDDEN_SUFFIXES:
        if repo_name.endswith(suffix):
            problems.append("drop the %s suffix: name the thing, not its stack" % suffix)
    is_channel = repo_name.endswith(CHANNEL_SUFFIX) and repo_name != TEMPLATE_NAME
    if repo_name.endswith(CHANNEL_SUFFIX * 2):
        problems.append("a channel is named <slug>-channel with a slug that does not end in -channel")
    if repo_name not in (HUB_NAME, TEMPLATE_NAME) and not is_channel and "-" not in repo_name:
        problems.append("name it %s, %s, <slug>-channel (a channel) or <area>-<piece> (a tool)"
                        % (HUB_NAME, TEMPLATE_NAME))
    has_rules = _real_dir(root / "org-rules")
    if is_channel and not has_rules:
        problems.append("a -channel name needs the workspace layout (an org-rules/ directory)")
    if has_rules and _real_file(root / ".gitmodules") and repo_name != HUB_NAME:
        problems.append("only %s combines org-rules/ and .gitmodules" % HUB_NAME)
    for problem in problems:
        report.add("repo-name", "FAIL", ".", "%s: %s" % (repo_name, problem))
