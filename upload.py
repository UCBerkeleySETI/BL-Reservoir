from google.cloud import storage
import os
from tqdm import tqdm
from multiprocessing import Pool, current_process
import time

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

def upload_dir_energy_detection(bucket_name, dir_name):
    start = time.time()
    paths = []
    for root, dirs, files in os.walk(os.path.join(dir_name, "filtered")):
        paths_temp = filter(lambda x: x.endswith(".png"), files)
        paths_temp = [os.path.join(root, path) for path in paths_temp]
        paths.extend(paths_temp)

    print(f"Found {len(paths)} stamps in {dir_name}, uploading")

    global upload_file
    def upload_file(path):
        upload_blob(bucket_name, path, "/".join(path.split("/")[-4:]))

    start_png = time.time()
    with Pool(os.cpu_count()) as p:
        p.map(upload_file, paths)
    del upload_file

    end_png = time.time()

    print(f"Uploaded {len(paths)} stamps in {end_png-start_png} seconds")
    print(f"Average upload time: {(end_png-start_png) / len(paths)}")

    print(f"Uploading metadata")

    upload_blob("bl-scale", os.path.join(dir_name, "header.pkl"),
                os.path.join(os.path.basename(dir_name), "header.pkl"))
    upload_blob("bl-scale", os.path.join(dir_name, "info_df.pkl"),
                os.path.join(os.path.basename(dir_name), "info_df.pkl"))

    end = time.time()

    print(f"Metadata uploaded")
    print(f"Outputs for {os.path.basename(dir_name)} uploaded in {end-start} seconds")

def upload_dir(bucket_name, dir_name):
    start = time.time()
    source_paths, dest_paths = [], []
    for root, dirs, files in tqdm(os.walk(dir_name)):
        for file in files:
            source_paths.append(os.path.join(root, file))
            dest_paths.append(os.path.join(os.path.basename(dir_name),
             os.path.relpath(os.path.join(root, file), start=dir_name)))

    print(f"Found {len(source_paths)} files in {dir_name}, uploading")

    global upload_file
    def upload_file(source_dest_pair):
        source_name, dest_name = source_dest_pair
        upload_blob(bucket_name, source_name, dest_name)

    with Pool(min(len(source_paths), os.cpu_count())) as p:
        p.map(upload_file, zip(source_paths, dest_paths))

    end = time.time()
    print(f"Outputs for {dir_name} uploaded in {end-start} seconds")
