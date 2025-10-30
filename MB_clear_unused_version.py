# -*- coding: utf-8 -*-

import hiero.core
import hiero.ui
import nuke


def get_all_bin_items(current_bin, found_items):
    """
    Recursively scans bins and collects all bin items (hiero.core.BinItem).

    Args:
        current_bin (hiero.core.Bin): The bin to be scanned.
        found_items (list): The list to which found items are added.
    """
    for item in current_bin.items():
        if isinstance(item, hiero.core.Bin):
            get_all_bin_items(item, found_items)
        elif isinstance(item, hiero.core.BinItem):
            found_items.append(item)


def find_and_delete_unused_versions():
    """
    Main function for Nuke.
    Finds and deletes unused versions by removing their BinItems from bins.
    """
    print("Running script to find and delete unused versions.")

    try:
        project = hiero.core.projects()[-1]
    except IndexError:
        print("Error: No project is open.")
        nuke.alert("Error", "No project is open.")
        return

    print(f"Processing project: {project.name()}")

    # Get all items from the bins
    all_bin_items = []
    root_bin = project.clipsBin()
    get_all_bin_items(root_bin, all_bin_items)

    if not all_bin_items:
        print("No items found in the project bins.")
        return

    # A set to track scanners we have already processed to avoid duplicate work
    processed_scanners = set()
    deleted_count = 0

    print(f"Found {len(all_bin_items)} items to analyze for versions.")

    # Iterate through all items and analyze their versions
    for bin_item in all_bin_items:
        version = bin_item.activeItem()
        if not isinstance(version, hiero.core.Version):
            continue

        # Get the scanner for the given version
        scanner = hiero.core.VersionScanner.versionScannerFor(version)
        if not scanner or scanner in processed_scanners:
            continue

        # Mark the scanner as processed
        processed_scanners.add(scanner)

        all_versions_from_scanner = scanner.versions()

        # Safety check: Never process clips with only a single version
        if len(all_versions_from_scanner) <= 1:
            continue

        print(f"Checking file: {scanner.pattern()} ({len(all_versions_from_scanner)} versions)")

        # For each found version, check its usage
        for version_to_check in all_versions_from_scanner:
            usages = project.findItems(version_to_check)

            # Separate timeline usages (TrackItem) from bin items (BinItem)
            track_items = [u for u in usages if isinstance(u, hiero.core.TrackItem)]
            bin_items_of_this_version = [u for u in usages if isinstance(u, hiero.core.BinItem)]

            # If the version is not used on any timeline, we can delete its BinItem
            if not track_items:
                print(f"Version '{version_to_check.name()}' is unused on timelines.")

                # Delete all BinItems that reference this unused version
                for item_to_delete in bin_items_of_this_version:
                    try:
                        parent_bin = item_to_delete.parentBin()
                        if parent_bin:
                            print(f"Removing item '{item_to_delete.name()}' from bin '{parent_bin.name()}'.")
                            parent_bin.removeItem(item_to_delete)
                            deleted_count += 1
                    except Exception as e:
                        print(f"Error removing item '{item_to_delete.name()}': {e}")
            else:
                print(f"Version '{version_to_check.name()}' is used ({len(track_items)}x) and will be kept.")

    if deleted_count > 0:
        message = f"Operation complete. A total of {deleted_count} unused version items were deleted from bins."
        print(message)
        nuke.alert(message)
    else:
        message = "Operation complete. No unused versions were found to delete."
        print(message)
        nuke.alert(message)

# --- Example Usage (for testing directly in the Nuke Studio Script Editor) ---
# To test the script, uncomment the following line and execute it.
#
# find_and_delete_unused_versions()
