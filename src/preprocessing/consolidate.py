import json
from pathlib import Path
from time import perf_counter
from tqdm.auto import tqdm


def append_to_file(data: list, path: Path):
    with open(path, "w", encoding="utf-8") as outfile:
        for item in data:
            json.dump(item, outfile)
            outfile.write("\n")


def folder_to_json(folder_in: Path, folder_out: Path, json_file_name: str):
    """
    Process JSON lines from files in a given folder and write processed data to new ndjson files.
    Parameters:
    folder_in (Path): Path to the input folder containing the JSON files to process.
    folder_out (Path): Path to the output folder for processed ndjson
    json_file_name (str): Filename The files will be named as
                           {json_base_path}_1.ndjson, {json_base_path}_2.ndjson, and so on.
    Example:
    folder_to_json(Path("/path/to/input/folder"), Path("/path/to/output/folder"), "ar_wiki")
    """

    json_out = []  # Initialize list to hold processed JSON data from all files
    file_counter = 1  # Counter to increment file names

    process_start = perf_counter()
    all_files = sorted(folder_in.rglob("*wiki*"), key=str)

    with tqdm(total=len(all_files), desc="Processing", unit="file") as pbar:
        for file_path in all_files:
            pbar.set_postfix_str(f"File: {file_path.name} | Dir: {file_path.parent}", refresh=True)

            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    article: dict = json.loads(line)
                    # Restructure the article into haystack's format, separating content and meta data.
                    restructured_articles = {
                        "content": article["text"],
                        "meta": {k: v for k, v in article.items() if k != "text"},
                    }
                    json_out.append(restructured_articles)

                    # If size of json_out is 100,000, dump to file and clear list
                    if len(json_out) == 100_000:
                        append_to_file(json_out, folder_out / f"{json_file_name}_{file_counter}.ndjson")
                        json_out.clear()
                        file_counter += 1

            pbar.update(1)

    if json_out:  # Dump any remaining items in json_out to file
        append_to_file(json_out, folder_out / f"{json_file_name}_{file_counter}.ndjson")

    time_taken_to_process = perf_counter() - process_start
    pbar.write(f"Wiki processed in {round(time_taken_to_process, 2)} seconds!")
