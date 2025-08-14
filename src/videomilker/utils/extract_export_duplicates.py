import argparse
import configparser
import logging
import os
import shutil
import sys
from datetime import datetime

import parso
from redbaron import RedBaron


# Configure logging
logger = logging.getLogger("DuplicateArchiver")
logger.setLevel(logging.DEBUG)  # Capture all levels of logs

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler("../dupe_ext_cli/duplicate_archiver.log")

c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.DEBUG)

# Create formatters and add them to handlers
c_format = logging.Formatter("%(levelname)s - %(message)s")
f_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)


def load_config(config_path=None):
    """
    Loads configuration from a config file.

    Args:
        config_path (str, optional): Path to the configuration file.

    Returns:
        config (ConfigParser): Parsed configuration object.
    """
    config = configparser.ConfigParser()
    if config_path:
        if not os.path.exists(config_path):
            logger.error("Configuration file %s does not exist.", config_path)
            sys.exit(1)
        config.read(config_path)
        logger.info("Loaded configuration from %s.", config_path)
    else:
        # Default config path: config.ini in the current directory
        default_path = os.path.join(os.getcwd(), "config.ini")
        if os.path.exists(default_path):
            config.read(default_path)
            logger.info("Loaded configuration from %s.", default_path)
        else:
            # Use default settings if no config file is found
            config["DEFAULT"] = {
                "archive_dir": "archives",
                "parser": "redbaron",
                "type_specific": "True",
                "log_file": "duplicate_archiver.log",
                "log_level": "INFO",
                "include_nested_definitions": "True",
                "duplicate_separator": "# Duplicate Definition",
                "date_format": "%Y-%m-%d %H:%M:%S",
                "backup_before_overwrite": "True",
                "backup_suffix": ".bak",
                "file_extensions": ".py",
                "exclude_paths": "tests/, docs/, __pycache__/",
                "timestamp_metadata": "True",
                "search_default_type": "both",
            }
            logger.info("No configuration file found. Using default settings.")
    return config


def setup_logging(config):
    """
    Sets up logging based on configuration.

    Args:
        config (ConfigParser): Parsed configuration object.
    """
    log_file = config["DEFAULT"].get("log_file", "duplicate_archiver.log")
    log_level = config["DEFAULT"].get("log_level", "INFO").upper()

    # Update log level for handlers
    numeric_level = getattr(logging, log_level, None)
    if not isinstance(numeric_level, int):
        logger.error("Invalid log level: %s", log_level)
        numeric_level = logging.INFO

    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.setLevel(numeric_level)
        elif isinstance(handler, logging.FileHandler):
            handler.setLevel(logging.DEBUG)  # File handler always logs DEBUG and above

    existing_f_handler = next(
        (handler for handler in logger.handlers if isinstance(handler, logging.FileHandler)),
        None,
    )
    if existing_f_handler and existing_f_handler.baseFilename != os.path.abspath(log_file):
        _remove_legacy_file_handler(existing_f_handler, log_file)
    logger.debug("Logging configured. Log file: %s, Log level: %s", log_file, log_level)


def _remove_legacy_file_handler(existing_f_handler, log_file):
    # Remove the old file handler
    logger.removeHandler(existing_f_handler)
    existing_f_handler.close()
    # Add a new file handler with the updated log_file
    f_handler_new = logging.FileHandler(log_file)
    f_handler_new.setLevel(logging.DEBUG)
    f_handler_new.setFormatter(f_format)
    logger.addHandler(f_handler_new)
    logger.debug("Logging file handler updated to %s.", log_file)


def prompt_user(prompt_text, default=None, validator=None):
    """
    Prompts the user for input, providing a default value and optional validation.

    Args:
        prompt_text (str): The prompt message to display.
        default (str, optional): The default value if the user provides no input.
        validator (callable, optional): A function to validate the input.

    Returns:
        user_input (str): The validated user input.
    """
    while True:
        prompt = f"{prompt_text} [{default}]: " if default else f"{prompt_text}: "
        try:
            user_input = input(prompt).strip()
        except EOFError:
            user_input = ""
        if not user_input and default is not None:
            user_input = default
        if not validator:
            return user_input
        try:
            if validator(user_input):
                return user_input
        except Exception as e:
            logger.error("Invalid input: %s", e)


def extract_definitions_redbaron(source_code, include_nested=True):
    """
    Extracts all function and class definitions from the source code using RedBaron,
    including nested definitions, and preserves their exact formatting.

    Args:
        source_code (str): The Python source code to parse.
        include_nested (bool): Whether to include nested definitions.

    Returns:
        definitions_dict (dict): Mapping from definition names to lists of their RedBaron nodes.
        node_positions (dict): Mapping from definition names to lists of (start, end) line numbers.
    """
    try:
        red = RedBaron(source_code)
        definitions_dict = {}
        node_positions = {}

        def recurse_nodes(nodes):
            for node in nodes:
                if node.type in ("def", "class"):
                    def_name = node.name
                    start_lineno = node.absolute_bounding_box.top_left.line - 1  # 0-based
                    end_lineno = node.absolute_bounding_box.bottom_right.line - 1

                    definitions_dict.setdefault(def_name, []).append(node)
                    node_positions.setdefault(def_name, []).append((start_lineno, end_lineno))

                    # Recursively handle nested definitions
                    if include_nested and hasattr(node, "value") and node.value:
                        recurse_nodes(node.value)

        recurse_nodes(red)

        logger.debug("Successfully extracted definitions using RedBaron.")
        return definitions_dict, node_positions
    except Exception as e:
        logger.error("Error extracting definitions with RedBaron: %s", e)
        sys.exit(1)


def remove_definitions_redbaron(source_code, node_positions):
    """
    Removes the lines corresponding to extracted definitions from the source code using RedBaron.

    Args:
        source_code (str): The original Python source code.
        node_positions (dict): Mapping from definition names to lists of (start, end) line numbers.

    Returns:
        modified_source (str): The source code with definitions removed.
    """
    try:
        red = RedBaron(source_code)
        all_nodes = []

        # Flatten all line ranges
        for name, ranges in node_positions.items():
            all_nodes.extend((start, end) for start, end in ranges)
        # Sort by start line descending to avoid messing up line numbers when removing
        all_nodes.sort(reverse=True, key=lambda r: r[0])

        for start, end in all_nodes:
            # Remove nodes within the specified line range
            nodes_to_remove = red.find_all(
                lambda node: node.absolute_bounding_box.top_left.line - 1 >= start
                and node.absolute_bounding_box.bottom_right.line - 1 <= end
            )
            for node in nodes_to_remove:
                logger.debug("Removing %s '%s' from lines %s to %s", node.type, node.name, start + 1, end + 1)
                node.parent.remove(node)

        modified_source = red.dumps()
        logger.debug("Successfully removed definitions using RedBaron.")
        return modified_source
    except Exception as e:
        logger.error("Error removing definitions with RedBaron: %s", e)
        sys.exit(1)


def write_definitions_to_files_redbaron(
    definitions_dict,
    output_dir="archives/classes",
    timestamp_metadata=True,
    date_format="%Y-%m-%d %H:%M:%S",
    duplicate_separator="# Duplicate Definition",
):
    """
    Writes each group of definitions (by name) to its own Python file using RedBaron.
    Checks for existing files and appends duplicates if necessary.

    Args:
        definitions_dict (dict): Mapping from definition names to lists of their RedBaron nodes.
        output_dir (str): Directory where the archived definitions will be stored.
        timestamp_metadata (bool): Whether to include archive date metadata.
        date_format (str): Format of the archive date.
        duplicate_separator (str): Text to separate duplicate definitions.
    """
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info("Created archive directory: %s", output_dir)

        for def_name, nodes in definitions_dict.items():
            safe_name = "".join([c if c.isalnum() or c == "_" else "_" for c in def_name])
            # Determine if the definition is a class or function
            def_type = nodes[0].type  # Assuming all nodes with the same name are of the same type

            # Corrected the type_dir paths to ensure they are relative to archive_dir
            if def_type == "def":
                type_dir = "archives/functions/functions"  # Fixed incorrect path
            elif def_type == "class":
                type_dir = "classes"
            else:
                type_dir = "others"  # For any other types if needed

            type_dir_path = os.path.join(os.path.dirname(output_dir), type_dir)
            if not os.path.exists(type_dir_path):
                os.makedirs(type_dir_path)
                logger.info("Created type-specific directory: %s", type_dir_path)

            filepath = os.path.join(type_dir_path, f"{safe_name}.py")

            # Open the file in append mode if it exists, else create it
            mode = "a" if os.path.exists(filepath) else "w"
            with open(filepath, mode, encoding="utf-8") as f:
                for idx, node in enumerate(nodes):
                    # Write a separator for duplicates only between duplicates
                    if mode == "a" and idx > 0:
                        f.write(f"\n\n{duplicate_separator}\n\n")
                    # Append metadata (e.g., date archived)
                    if timestamp_metadata:
                        f.write(f"# Archived on {datetime.now().strftime(date_format)}\n")
                    f.write(node.dumps() + "\n")
            logger.info("Saved %s '%s' to %s", "function" if def_type == "def" else "class", def_name, filepath)
    except Exception as e:
        logger.error("Error writing definitions with RedBaron: %s", e)
        sys.exit(1)


def extract_definitions_parso(source_code, include_nested=True):
    """
    Extracts all function and class definitions from the source code using Parso,
    including nested definitions.

    Args:
        source_code (str): The Python source code to parse.
        include_nested (bool): Whether to include nested definitions.

    Returns:
        definitions_dict (dict): Mapping from definition names to lists of their Parso nodes.
        node_positions (dict): Mapping from definition names to lists of (start, end) line numbers.
    """
    try:
        grammar = parso.load_grammar()
        module = grammar.parse(source_code)
        definitions_dict = {}
        node_positions = {}

        def recurse_nodes(node):
            for child in node.children:
                if child.type in ("funcdef", "classdef"):
                    def_name = child.name.value
                    start_line = child.start_pos[0] - 1  # 0-based
                    end_line = child.end_pos[0] - 1

                    definitions_dict.setdefault(def_name, []).append(child)
                    node_positions.setdefault(def_name, []).append((start_line, end_line))

                    # Recursively handle nested definitions
                    if include_nested:
                        recurse_nodes(child)

        recurse_nodes(module)

        logger.debug("Successfully extracted definitions using Parso.")
        return definitions_dict, node_positions
    except Exception as e:
        logger.error("Error extracting definitions with Parso: %s", e)
        sys.exit(1)


def remove_definitions_parso(source_code, node_positions):
    """
    Removes the lines corresponding to all extracted definitions from the source code using Parso.

    Args:
        source_code (str): The original Python source code.
        node_positions (dict): Mapping from definition names to lists of (start, end) line numbers.

    Returns:
        modified_source (str): The source code with definitions removed.
    """
    try:
        lines = source_code.splitlines()
        ranges = []

        for name, pos_list in node_positions.items():
            ranges.extend((start, end) for start, end in pos_list)
        # Sort ranges in reverse to avoid affecting line numbers when removing
        ranges.sort(reverse=True, key=lambda r: r[0])

        for start, end in ranges:
            logger.debug("Removing lines %s to %s for definition", start + 1, end + 1)
            del lines[start : end + 1]

        modified_source = "\n".join(lines)
        logger.debug("Successfully removed definitions using Parso.")
        return modified_source
    except Exception as e:
        logger.error("Error removing definitions with Parso: %s", e)
        sys.exit(1)


def write_definitions_to_files_parso(
    definitions_dict,
    output_dir="archives/functions",
    timestamp_metadata=True,
    date_format="%Y-%m-%d %H:%M:%S",
    duplicate_separator="# Duplicate Definition",
):
    """
    Writes each group of definitions (by name) to its own Python file using Parso.
    Checks for existing files and appends duplicates if necessary.

    Args:
        definitions_dict (dict): Mapping from definition names to lists of their Parso nodes.
        output_dir (str): Directory where the archived definitions will be stored.
        timestamp_metadata (bool): Whether to include archive date metadata.
        date_format (str): Format of the archive date.
        duplicate_separator (str): Text to separate duplicate definitions.
    """
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info("Created archive directory: %s", output_dir)

        for def_name, nodes in definitions_dict.items():
            safe_name = "".join([c if c.isalnum() or c == "_" else "_" for c in def_name])
            # Determine if the definition is a class or function
            def_type = nodes[0].type  # Assuming all nodes with the same name are of the same type

            # Corrected the type_dir paths to ensure they are relative to archive_dir
            if def_type == "funcdef":
                type_dir = "archives/functions/functions"  # Fixed incorrect path
            elif def_type == "classdef":
                type_dir = "classes"
            else:
                type_dir = "others"  # For any other types if needed

            type_dir_path = os.path.join(os.path.dirname(output_dir), type_dir)
            if not os.path.exists(type_dir_path):
                os.makedirs(type_dir_path)
                logger.info("Created type-specific directory: %s", type_dir_path)

            filepath = os.path.join(type_dir_path, f"{safe_name}.py")

            # Open the file in append mode if it exists, else create it
            mode = "a" if os.path.exists(filepath) else "w"
            with open(filepath, mode, encoding="utf-8") as f:
                for idx, node in enumerate(nodes):
                    # Write a separator for duplicates only between duplicates
                    if mode == "a" and idx > 0:
                        f.write(f"\n\n{duplicate_separator}\n\n")
                    # Append metadata (e.g., date archived)
                    if timestamp_metadata:
                        f.write(f"# Archived on {datetime.now().strftime(date_format)}\n")
                    f.write(node.get_code() + "\n")
            logger.info("Saved %s '%s' to %s", "function" if def_type == "funcdef" else "class", def_name, filepath)
    except Exception as e:
        logger.error("Error writing definitions with Parso: %s", e)
        sys.exit(1)


def create_backup(outfile, backup_before_overwrite, backup_suffix):
    """
    Creates a backup of the original file before overwriting.

    Args:
        outfile (str): Path to the output file.
        backup_before_overwrite (bool): Whether to create a backup.
        backup_suffix (str): Suffix to append to the backup file.
    """
    if backup_before_overwrite and outfile and os.path.exists(outfile):
        backup_file = f"{outfile}{backup_suffix}"
        try:
            shutil.copy2(outfile, backup_file)
            logger.info("Backup created: %s", backup_file)
        except Exception as e:
            logger.error("Failed to create backup: %s", e)
            sys.exit(1)


def consolidate_definitions_redbaron(
    infile,
    outfile=None,
    archive_dir="archives",
    type_specific=True,
    include_nested=True,
    timestamp_metadata=True,
    date_format="%Y-%m-%d %H:%M:%S",
    duplicate_separator="# Duplicate Definition",
):
    """
    Consolidates function and class definitions from the input file using RedBaron:
    - Extracts all definitions, including nested ones.
    - Writes them to separate files in the archive directory, handling duplicates.
    - Removes them from the original source code.
    - Writes the modified source to the output file.

    Args:
        infile (str): Path to the input Python file.
        outfile (str, optional): Path to the output Python file. Overwrites infile if None.
        archive_dir (str): Directory where the archived definitions will be stored.
        type_specific (bool): If True, separate directories for classes and functions.
        include_nested (bool): Whether to include nested definitions.
        timestamp_metadata (bool): Whether to include archive date metadata.
        date_format (str): Format of the archive date.
        duplicate_separator (str): Text to separate duplicate definitions.
    """
    try:
        with open(infile, encoding="utf-8") as f:
            source_code = f.read()

        logger.info("Opened input file: %s", infile)

        # Extract definitions
        definitions_dict, node_positions = extract_definitions_redbaron(source_code, include_nested=include_nested)

        if not definitions_dict:
            logger.warning("No definitions found to archive.")
        elif type_specific:
            # Separate directories for classes and functions
            classes_dir = os.path.join(archive_dir, "classes")
            functions_dir = os.path.join(archive_dir, "functions")
            write_definitions_to_files_redbaron(
                definitions_dict,
                output_dir=classes_dir,
                timestamp_metadata=timestamp_metadata,
                date_format=date_format,
                duplicate_separator=duplicate_separator,
            )
            write_definitions_to_files_redbaron(
                definitions_dict,
                output_dir=functions_dir,
                timestamp_metadata=timestamp_metadata,
                date_format=date_format,
                duplicate_separator=duplicate_separator,
            )
        else:
            # All definitions in a single directory
            write_definitions_to_files_redbaron(
                definitions_dict,
                output_dir=archive_dir,
                timestamp_metadata=timestamp_metadata,
                date_format=date_format,
                duplicate_separator=duplicate_separator,
            )

        # Remove definitions from source
        modified_source = remove_definitions_redbaron(source_code, node_positions)

        # Backup before overwriting if needed
        backup_before_overwrite = config["DEFAULT"].getboolean("backup_before_overwrite", True)
        backup_suffix = config["DEFAULT"].get("backup_suffix", ".bak")
        if backup_before_overwrite and outfile and os.path.exists(outfile):
            create_backup(outfile, backup_before_overwrite, backup_suffix)

        # Write modified source
        target = outfile or infile
        with open(target, "w", encoding="utf-8") as f:
            f.write(modified_source)
        logger.info("Modified source written to %s", target)
    except Exception as e:
        logger.error("Error consolidating definitions with RedBaron: %s", e)
        sys.exit(1)


def consolidate_definitions_parso(
    infile,
    outfile=None,
    archive_dir="archives",
    type_specific=True,
    include_nested=True,
    timestamp_metadata=True,
    date_format="%Y-%m-%d %H:%M:%S",
    duplicate_separator="# Duplicate Definition",
):
    """
    Consolidates function and class definitions from the input file using Parso:
    - Extracts all definitions, including nested ones.
    - Writes them to separate files in the archive directory, handling duplicates.
    - Removes them from the original source code.
    - Writes the modified source to the output file.

    Args:
        infile (str): Path to the input Python file.
        outfile (str, optional): Path to the output Python file. Overwrites infile if None.
        archive_dir (str): Directory where the archived definitions will be stored.
        type_specific (bool): If True, separate directories for classes and functions.
        include_nested (bool): Whether to include nested definitions.
        timestamp_metadata (bool): Whether to include archive date metadata.
        date_format (str): Format of the archive date.
        duplicate_separator (str): Text to separate duplicate definitions.
    """
    try:
        with open(infile, encoding="utf-8") as f:
            source_code = f.read()

        logger.info("Opened input file: %s", infile)

        # Extract definitions
        definitions_dict, node_positions = extract_definitions_parso(source_code, include_nested=include_nested)

        if not definitions_dict:
            logger.warning("No definitions found to archive.")
        elif type_specific:
            # Separate directories for classes and functions
            classes_dir = os.path.join(archive_dir, "classes")
            functions_dir = os.path.join(archive_dir, "functions")
            write_definitions_to_files_parso(
                definitions_dict,
                output_dir=classes_dir,
                timestamp_metadata=timestamp_metadata,
                date_format=date_format,
                duplicate_separator=duplicate_separator,
            )
            write_definitions_to_files_parso(
                definitions_dict,
                output_dir=functions_dir,
                timestamp_metadata=timestamp_metadata,
                date_format=date_format,
                duplicate_separator=duplicate_separator,
            )
        else:
            # All definitions in a single directory
            write_definitions_to_files_parso(
                definitions_dict,
                output_dir=archive_dir,
                timestamp_metadata=timestamp_metadata,
                date_format=date_format,
                duplicate_separator=duplicate_separator,
            )

        # Remove definitions from source
        modified_source = remove_definitions_parso(source_code, node_positions)

        # Backup before overwriting if needed
        backup_before_overwrite = config["DEFAULT"].getboolean("backup_before_overwrite", True)
        backup_suffix = config["DEFAULT"].get("backup_suffix", ".bak")
        if backup_before_overwrite and outfile and os.path.exists(outfile):
            create_backup(outfile, backup_before_overwrite, backup_suffix)

        # Write modified source
        target = outfile or infile
        with open(target, "w", encoding="utf-8") as f:
            f.write(modified_source)
        logger.info("Modified source written to %s", target)
    except Exception as e:
        logger.error("Error consolidating definitions with Parso: %s", e)
        sys.exit(1)


def consolidate_definitions(infile, outfile=None, archive_dir="archives", parser_choice="redbaron", type_specific=True):
    """
    Consolidates function and class definitions from the input file:
    - Parses the input file using the specified parser ('redbaron' or 'parso').
    - Extracts all top-level and nested definitions.
    - Writes them to separate files in the archive directory, handling duplicates.
    - Removes them from the original source code.
    - Writes the modified source to the output file.

    Args:
        infile (str): Path to the input Python file.
        outfile (str, optional): Path to the output Python file. Overwrites infile if None.
        archive_dir (str): Directory where the archived definitions will be stored.
        parser_choice (str): Parsing tool to use ('redbaron' or 'parso').
        type_specific (bool): If True, separate directories for classes and functions.
    """
    # Retrieve additional settings from config
    include_nested = config["DEFAULT"].getboolean("include_nested_definitions", True)
    duplicate_separator = config["DEFAULT"].get("duplicate_separator", "# Duplicate Definition")
    date_format = config["DEFAULT"].get("date_format", "%Y-%m-%d %H:%M:%S")
    timestamp_metadata = config["DEFAULT"].getboolean("timestamp_metadata", True)

    if parser_choice == "redbaron":
        consolidate_definitions_redbaron(
            infile,
            outfile,
            archive_dir,
            type_specific,
            include_nested,
            timestamp_metadata,
            date_format,
            duplicate_separator,
        )
    elif parser_choice == "parso":
        consolidate_definitions_parso(
            infile,
            outfile,
            archive_dir,
            type_specific,
            include_nested,
            timestamp_metadata,
            date_format,
            duplicate_separator,
        )
    else:
        logger.error("Unsupported parser. Choose 'redbaron' or 'parso'.")
        sys.exit(1)


def search_archives(archive_dir, name=None, date=None, type_filter=None):
    """
    Searches the archive directories for definitions matching the criteria.

    Args:
        archive_dir (str): Path to the archive directory.
        name (str, optional): Name or partial name of the definition to search for.
        date (str, optional): Date in 'YYYY-MM-DD' format to filter definitions archived on that date.
        type_filter (str, optional): Type of definition to search for ('class', 'function').

    Returns:
        results (list): List of dictionaries containing search results.
    """
    results = []

    # Determine subdirectories based on type_filter
    subdirs = []
    if type_filter == "class":
        subdirs = [os.path.join(archive_dir, "classes")]
    elif type_filter == "function":
        subdirs = [os.path.join(archive_dir, "functions")]
    else:
        # Search both classes and functions
        subdirs = [os.path.join(archive_dir, "classes"), os.path.join(archive_dir, "functions")]

    for subdir in subdirs:
        if not os.path.exists(subdir):
            logger.warning("Archive subdirectory does not exist: %s", subdir)
            continue
        for filename in os.listdir(subdir):
            if not filename.endswith(".py"):
                continue
            def_name = os.path.splitext(filename)[0]
            # Check name criteria
            if name and name.lower() not in def_name.lower():
                continue
            filepath = os.path.join(subdir, filename)
            # Get file modification date
            mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            mod_date_str = mod_time.strftime("%Y-%m-%d")
            # Check date criteria
            if date and date != mod_date_str:
                continue
            # Determine type based on subdir
            if "classes" in subdir:
                def_type = "class"
            elif "functions" in subdir:
                def_type = "function"
            else:
                def_type = "other"
            # Append to results
            results.append({"name": def_name, "type": def_type, "file": filepath, "date_archived": mod_date_str})

    return results


def write_search_results(results):
    """
    Writes search results to the console.

    Args:
        results (list): List of dictionaries containing search results.
    """
    if not results:
        print("No matching definitions found.")
        return

    for res in results:
        print(f"Name           : {res['name']}")
        print(f"Type           : {res['type'].capitalize()}")
        print(f"File Location  : {res['file']}")
        print(f"Date Archived  : {res['date_archived']}")
        print("-" * 40)


def main():
    """
    Main function to parse command-line arguments and initiate consolidation or search.
    Includes interactive prompts for missing information.
    """
    global config  # Make config accessible globally
    config = load_config()

    setup_logging(config)

    parser = argparse.ArgumentParser(description="Consolidate and search Python definitions into a duplicate archive.")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands: archive, search")

    # Archive subcommand
    archive_parser = subparsers.add_parser("archive", help="Archive definitions from a Python file or folder.")
    archive_parser.add_argument("input", nargs="?", help="Path to the input Python file or folder.")
    archive_parser.add_argument(
        "output", nargs="?", default=None, help="Path to the output Python file. Overwrites input if not specified."
    )
    archive_parser.add_argument("--archive_dir", help="Directory to store archived definitions.")
    archive_parser.add_argument("--parser", choices=["redbaron", "parso"], help="Parser to use for processing.")
    archive_parser.add_argument(
        "--type_specific", action="store_true", help="Organize archives into 'classes' and 'functions' directories."
    )
    archive_parser.add_argument("--config", help="Path to the configuration file.")

    # Search subcommand
    search_parser = subparsers.add_parser("search", help="Search archived definitions.")
    search_parser.add_argument("--archive_dir", help="Directory where archived definitions are stored.")
    search_parser.add_argument("--name", help="Name or partial name of the definition to search for.")
    search_parser.add_argument(
        "--date", help="Date in 'YYYY-MM-DD' format to filter definitions archived on that date."
    )
    search_parser.add_argument(
        "--type", choices=["class", "function"], help="Type of definition to search for ('class', 'function')."
    )
    search_parser.add_argument("--config", help="Path to the configuration file.")

    args = parser.parse_args()

    if args.command == "archive":
        # Interactive prompts for missing arguments
        infile = args.input
        if not infile:
            infile = prompt_user(
                "Enter the path to the input Python file or folder",
                default=os.getcwd(),
                validator=lambda x: os.path.isfile(x) or os.path.isdir(x),
            )
            if not (os.path.isfile(infile) or os.path.isdir(infile)):
                logger.error("The path %s does not exist.", infile)
                sys.exit(1)

        outfile = args.output
        if not outfile and os.path.isfile(infile):
            overwrite = prompt_user("Do you want to overwrite the input file? (yes/no)", default="yes").lower()
            if overwrite in ["yes", "y"]:
                outfile = infile
            else:
                outfile = prompt_user(
                    "Enter the path for the output Python file",
                    default=os.path.join(
                        os.path.dirname(infile), f"{os.path.splitext(os.path.basename(infile))[0]}_cleaned.py"
                    ),
                )

        archive_dir = args.archive_dir or config["DEFAULT"].get("archive_dir", "archives")

        parser_choice = args.parser or config["DEFAULT"].get("parser", "redbaron")
        while parser_choice not in ["redbaron", "parso"]:
            logger.warning("Invalid parser choice. Please choose 'redbaron' or 'parso'.")
            parser_choice = prompt_user("Choose a parser ('redbaron' or 'parso')", default="redbaron")

        type_specific = args.type_specific
        if not type_specific:
            default_type_specific = config["DEFAULT"].getboolean("type_specific", True)
            prompt_type_specific = prompt_user(
                "Do you want to organize archives into 'classes' and 'functions' directories? (yes/no)",
                default=str(default_type_specific),
            ).lower()
            type_specific = True if prompt_type_specific in ["yes", "y"] else False
        # Retrieve additional settings from config
        include_nested = config["DEFAULT"].getboolean("include_nested_definitions", True)
        duplicate_separator = config["DEFAULT"].get("duplicate_separator", "# Duplicate Definition")
        date_format = config["DEFAULT"].get("date_format", "%Y-%m-%d %H:%M:%S")
        backup_before_overwrite = config["DEFAULT"].getboolean("backup_before_overwrite", True)
        backup_suffix = config["DEFAULT"].get("backup_suffix", ".bak")
        file_extensions = [ext.strip() for ext in config["DEFAULT"].get("file_extensions", ".py").split(",")]
        exclude_paths = [p.strip() for p in config["DEFAULT"].get("exclude_paths", "").split(",")]
        timestamp_metadata = config["DEFAULT"].getboolean("timestamp_metadata", True)

        # Backup before overwriting if needed
        if backup_before_overwrite and outfile and os.path.exists(outfile):
            create_backup(outfile, backup_before_overwrite, backup_suffix)

        # Determine if input is file or folder
        if os.path.isfile(infile):
            consolidate_definitions(
                infile=infile,
                outfile=outfile,
                archive_dir=archive_dir,
                parser_choice=parser_choice,
                type_specific=type_specific,
            )
        elif os.path.isdir(infile):
            # Process all files in the directory
            for root, dirs, files in os.walk(infile):
                # Exclude specified directories
                dirs[:] = [
                    d for d in dirs if not any(os.path.join(root, d).startswith(exclude) for exclude in exclude_paths)
                ]
                for file in files:
                    if not file.endswith(tuple(file_extensions)):
                        continue
                    file_path = os.path.join(root, file)
                    logger.info("Processing file: %s", file_path)
                    # Determine output path
                    consolidate_definitions(
                        infile=file_path,
                        outfile=None,
                        archive_dir=archive_dir,
                        parser_choice=parser_choice,
                        type_specific=type_specific,
                    )
        else:
            logger.error("The path %s is neither a file nor a directory.", infile)
            sys.exit(1)

        logger.info("Definitions archived successfully using %s.", parser_choice)

    elif args.command == "search":
        # Interactive prompts for missing arguments
        archive_dir = args.archive_dir or config["DEFAULT"].get("archive_dir", "archives")
        if not os.path.exists(archive_dir):
            logger.error("The archive directory %s does not exist.", archive_dir)
            sys.exit(1)

        name = args.name or prompt_user("Enter the name or partial name of the definition to search for", default=None)

        date_input = args.date or prompt_user(
            "Enter the date (YYYY-MM-DD) to filter definitions archived on that date or leave blank", default=None
        )
        if date_input:
            # Validate date format
            try:
                datetime.strptime(date_input, "%Y-%m-%d")
                date = date_input
            except ValueError:
                logger.error("Incorrect date format. Please use 'YYYY-MM-DD'.")
                sys.exit(1)
        else:
            date = None

        type_filter = args.type
        if not type_filter:
            type_filter = prompt_user(
                "Enter the type of definition to search for ('class', 'function') or leave blank for both",
                default=config["DEFAULT"].get("search_default_type", "both"),
            ).lower()
            if type_filter not in ["class", "function", ""]:
                logger.error("Invalid type filter. Choose 'class', 'function', or leave blank.")
                sys.exit(1)
            if type_filter == "both" or type_filter == "":
                type_filter = None

        # Proceed with search
        results = search_archives(archive_dir, name=name, date=date, type_filter=type_filter)
        write_search_results(results)

    else:
        # If no subcommand is provided, prompt the user to choose
        print("No subcommand provided. Please choose either 'archive' or 'search'.")
        user_choice = prompt_user(
            "Do you want to 'archive' or 'search'? (archive/search)",
            validator=lambda x: x.lower() in ["archive", "search"],
        ).lower()
        if user_choice == "archive":
            # Interactive Archive
            infile = prompt_user(
                "Enter the path to the input Python file or folder",
                default=os.getcwd(),
                validator=lambda x: os.path.isfile(x) or os.path.isdir(x),
            )
            if not (os.path.isfile(infile) or os.path.isdir(infile)):
                logger.error("The path %s does not exist.", infile)
                sys.exit(1)

            if os.path.isfile(infile):
                overwrite = prompt_user("Do you want to overwrite the input file? (yes/no)", default="yes").lower()
                if overwrite in ["yes", "y"]:
                    outfile = infile
                else:
                    outfile = prompt_user(
                        "Enter the path for the output Python file",
                        default=os.path.join(
                            os.path.dirname(infile), f"{os.path.splitext(os.path.basename(infile))[0]}_cleaned.py"
                        ),
                    )
            else:
                outfile = None  # Not applicable for directories

            archive_dir = prompt_user(
                "Enter the archive directory", default=config["DEFAULT"].get("archive_dir", "archives")
            )

            parser_choice = prompt_user(
                "Choose a parser ('redbaron' or 'parso')", default=config["DEFAULT"].get("parser", "redbaron")
            )
            while parser_choice not in ["redbaron", "parso"]:
                logger.warning("Invalid parser choice. Please choose 'redbaron' or 'parso'.")
                parser_choice = prompt_user("Choose a parser ('redbaron' or 'parso')", default="redbaron")

            type_specific_input = prompt_user(
                "Do you want to organize archives into 'classes' and 'functions' directories? (yes/no)",
                default=str(config["DEFAULT"].getboolean("type_specific", True)),
            ).lower()
            type_specific = True if type_specific_input in ["yes", "y"] else False

            # Retrieve additional settings from config
            include_nested = config["DEFAULT"].getboolean("include_nested_definitions", True)
            duplicate_separator = config["DEFAULT"].get("duplicate_separator", "# Duplicate Definition")
            date_format = config["DEFAULT"].get("date_format", "%Y-%m-%d %H:%M:%S")
            backup_before_overwrite = config["DEFAULT"].getboolean("backup_before_overwrite", True)
            backup_suffix = config["DEFAULT"].get("backup_suffix", ".bak")
            file_extensions = [ext.strip() for ext in config["DEFAULT"].get("file_extensions", ".py").split(",")]
            exclude_paths = [p.strip() for p in config["DEFAULT"].get("exclude_paths", "").split(",")]
            timestamp_metadata = config["DEFAULT"].getboolean("timestamp_metadata", True)

            # Backup before overwriting if needed
            if backup_before_overwrite and outfile and os.path.exists(outfile):
                create_backup(outfile, backup_before_overwrite, backup_suffix)

            # Determine if input is file or folder
            if os.path.isfile(infile):
                consolidate_definitions(
                    infile=infile,
                    outfile=outfile,
                    archive_dir=archive_dir,
                    parser_choice=parser_choice,
                    type_specific=type_specific,
                )
            elif os.path.isdir(infile):
                # Process all files in the directory
                for root, dirs, files in os.walk(infile):
                    # Exclude specified directories
                    dirs[:] = [
                        d
                        for d in dirs
                        if not any(os.path.join(root, d).startswith(exclude) for exclude in exclude_paths)
                    ]
                    for file in files:
                        if not file.endswith(tuple(file_extensions)):
                            continue
                        file_path = os.path.join(root, file)
                        logger.info("Processing file: %s", file_path)
                        # Determine output path
                        consolidate_definitions(
                            infile=file_path,
                            outfile=None,
                            archive_dir=archive_dir,
                            parser_choice=parser_choice,
                            type_specific=type_specific,
                        )
            else:
                logger.error("The path %s is neither a file nor a directory.", infile)
                sys.exit(1)

            logger.info("Definitions archived successfully using %s.", parser_choice)

        elif user_choice == "search":
            # Interactive Search
            archive_dir = prompt_user(
                "Enter the archive directory", default=config["DEFAULT"].get("archive_dir", "archives")
            )
            if not os.path.exists(archive_dir):
                logger.error("The archive directory %s does not exist.", archive_dir)
                sys.exit(1)

            name = prompt_user("Enter the name or partial name of the definition to search for", default=None)

            if date_input := prompt_user(
                "Enter the date (YYYY-MM-DD) to filter definitions archived on that date or leave blank",
                default=None,
            ):
                # Validate date format
                try:
                    datetime.strptime(date_input, "%Y-%m-%d")
                    date = date_input
                except ValueError:
                    logger.error("Incorrect date format. Please use 'YYYY-MM-DD'.")
                    sys.exit(1)
            else:
                date = None

            type_filter = prompt_user(
                "Enter the type of definition to search for ('class', 'function') or leave blank for both",
                default=config["DEFAULT"].get("search_default_type", "both"),
            ).lower()
            if type_filter not in ["class", "function", "both", ""]:
                logger.error("Invalid type filter. Choose 'class', 'function', or leave blank.")
                sys.exit(1)
            if type_filter == "both" or type_filter == "":
                type_filter = None

            # Proceed with search
            results = search_archives(archive_dir, name=name, date=date, type_filter=type_filter)
            write_search_results(results)
        else:
            # Invalid subcommand
            logger.error("Invalid subcommand. Please choose either 'archive' or 'search'.")
            parser.print_help()
            sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
        sys.exit(1)
