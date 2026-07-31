# ==========================================

from scheduler_i18n import tr
# Broadcast Scheduler
# Version 3.0.0
# gui_tree.py
# ==========================================


# =====================================================
# Sort TreeView Column
# =====================================================

def sort_column(tree, column, reverse):
    """
    Sort a TreeView column.
    """

    data = [
        (
            tree.set(item, column),
            item
        )
        for item in tree.get_children("")
    ]

    data.sort(
        reverse=reverse
    )

    for index, (_, item) in enumerate(data):

        tree.move(
            item,
            "",
            index
        )

    tree.heading(
        column,
        command=lambda: sort_column(
            tree,
            column,
            not reverse
        )
    )


# =====================================================
# Populate TreeView
# =====================================================

def populate_tree(
    tree,
    runtimes,
    group="All",
    only_conflicts=False,
    search=""
):
    """
    Fill the TreeView with filtered events.
    """

    tree.delete(*tree.get_children())

    search = search.lower().strip()

    for rt in runtimes:

        # ---------------------------------------------
        # Group Filter
        # ---------------------------------------------

        if (
            group != tr("all")
            and rt.event.group != group
        ):
            continue

        # ---------------------------------------------
        # Conflict Filter
        # ---------------------------------------------

        if (
            only_conflicts
            and not getattr(rt, "conflict", False)
        ):
            continue

        # ---------------------------------------------
        # Search Filter
        # ---------------------------------------------

        if search:

            text = (
                f"{rt.event.name} "
                f"{rt.event.group}"
            ).lower()

            if search not in text:
                continue

        # ---------------------------------------------
        # Status
        # ---------------------------------------------

        conflict = getattr(
            rt,
            "conflict",
            False
        )

        if conflict:

            count = getattr(
                rt,
                "conflict_count",
                2
            )

            status = f"⚠ {count} events"

        else:

            status = "✓ OK"

        tags = (
            ("conflict",)
            if conflict
            else ()
        )

        tree.insert(
            "",
            "end",
            values=(
                status,
                rt.start.strftime("%d.%m.%Y %H:%M:%S"),
                rt.event.group,
                rt.event.name
            ),
            tags=tags
        )
