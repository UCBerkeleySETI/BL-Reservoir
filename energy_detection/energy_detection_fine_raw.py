import numpy as np
import pandas as pd
from scipy import stats
from matplotlib import pyplot as plt
from bisect import bisect_left
from tqdm import tqdm
import h5py
import hdf5plugin
from time import time
from multiprocessing import Pool, current_process
import pickle

from utils import read_header, norm_test, remove_channel_bandpass
import sys
import os

# if "cupy" in sys.modules:
#     import cupy as np
#     print("Using cupy")

# Hyperparameters
coarse_channel_width = 2 ** 20
threshold = 1e-80
stat_threshold = 2048
save_png = False
save_npy = True

if __name__ == "__main__":
    g_start = time()
    input_file = sys.argv[1]
    if len(sys.argv) == 2:
        out_dir = input_file.split(".")[0]
    else:
        out_dir = sys.argv[2]

    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    # read and store the header
    header = read_header(input_file)
    n_chans = header["nchans"]
    i_vals = np.arange(n_chans)
    freqs = header["foff"] * i_vals + header["fch1"]
    with open(out_dir+"/header.pkl", "wb") as f:
        pickle.dump(header, f)
        print("Header saved to "+out_dir+"/header.pkl")

    # calculate number of coarse channels
    n_coarse_chans = int(n_chans // coarse_channel_width)
    for i in range(32, 0, -1):
        if n_coarse_chans % i == 0:
            parallel_coarse_chans = i
            print(f"Processing {parallel_coarse_chans} in parallel")
            break
    num_blocks = int(n_coarse_chans // parallel_coarse_chans)
    block_width = coarse_channel_width * parallel_coarse_chans

    frame_list = []
    stack_list = []

    for block_num in tqdm(range(num_blocks)):
        print(f"Processing coarse channels {block_num * parallel_coarse_chans}-{(block_num + 1) * parallel_coarse_chans}")
        start = time()

        def read_coarse_channel(channel_num):
            hf = h5py.File(input_file, "r")
            read_data = hf["data"][:, 0, channel_num * coarse_channel_width: (channel_num+1) * coarse_channel_width]
            hf.close()
            return read_data

        with Pool(min(parallel_coarse_chans, os.cpu_count())) as p:
            block_data = np.concatenate(p.map(read_coarse_channel,
                                              range(block_num * parallel_coarse_chans, (block_num + 1) * parallel_coarse_chans)), axis=1)
        end = time()
        print(f"Data loaded in {end - start:.4f} seconds, processing")

        start = time()
        half_chan = coarse_channel_width/2
        for i in range(parallel_coarse_chans):      # remove dc spike
            dc_ind = int(i*coarse_channel_width + half_chan)
            block_data[:, dc_ind] = (block_data[:, dc_ind+1] + block_data[:, dc_ind-3])/2
            block_data[:, dc_ind-1] = (block_data[:, dc_ind+2] + block_data[:, dc_ind-2])/2

        integrated = np.mean(block_data, axis=0)
        channels = np.reshape(integrated, (-1, coarse_channel_width))

        def clean(channel_ind):
            # print("%s processing channel %d of %s" % (current_process().name, channel_ind, block_file))
            cleaned_block = remove_channel_bandpass(block_data[:, coarse_channel_width*(channel_ind):coarse_channel_width*(channel_ind+1)],
                                                    channels[channel_ind], coarse_channel_width)
            return cleaned_block

        def clean_block_bandpass():
            with Pool(min(parallel_coarse_chans, os.cpu_count())) as p:
                cleaned = p.map(clean, range(parallel_coarse_chans))
            return cleaned

        cleaned_block_data = clean_block_bandpass()
        cleaned_block_data = np.concatenate(cleaned_block_data, axis=1)
        # np.save(out_dir+"/cleaned/" + block_file, normalized)

        end = time()
        print("Bandpass cleaned in %.4f seconds." % (end - start))


        # actual energy detection
        def threshold_hits(channel_ind):
            res = list()
            channel_data = cleaned_block_data[:, coarse_channel_width*(channel_ind):coarse_channel_width*(channel_ind+1)]
            for i in range(0, coarse_channel_width - 128, 128):
                test_window = channel_data[:, i:i+256]
                s, p = norm_test(test_window)
                if s > stat_threshold:
                    res.append([coarse_channel_width*(channel_ind) + i, s, p])
            return res

        start = time()
        with Pool(min(parallel_coarse_chans, os.cpu_count())) as p:
            chan_hits = p.map(threshold_hits, range(parallel_coarse_chans))
        end = time()
        print("Stamps filtered in %.4f seconds" % (end-start))

        vals_frame = pd.DataFrame(sum(chan_hits, []), columns=["index", "statistic", "pvalue"])
        vals_frame["index"] += block_num*block_width
        vals_frame["freqs"] = vals_frame["index"].map(lambda x: freqs[x])
        frame_list.append(vals_frame)

        print("Saving results")
        # def save_stamps(channel_ind):
        #     # print("%s processing channel %d of %s" % (current_process().name, channel_ind, block_file))
        #     for res in chan_hits[channel_ind]:
        #         i, s, p = res
        #         plt.imsave((filtered_dir+"%d/%d.png" % (block_num, block_num*block_width + i)), cleaned_block_data[:, i:i+256])
        #         # np.save((filtered_dir+"%d/%d.npy" % (block_num, block_num*block_width + i)), data[:, i:i+200])

        def aggregate_npy(channel_ind):
            inds = map(lambda x: x[0], chan_hits[channel_ind])
            return np.array([block_data[:, ind:ind+256] for ind in inds])

        start = time()
        with Pool(min(parallel_coarse_chans, os.cpu_count())) as p:
            # if save_png:
            #     p.map(save_stamps, range(parallel_coarse_chans))
            if save_npy:
                stack = p.map(aggregate_npy, range(parallel_coarse_chans))
                stack = [e for e in stack if e.size != 0]
                if stack:
                    stack_list.append(np.concatenate(stack, axis=0))
        end = time()
        print("Results aggregated in %.4f seconds" % (end - start))
        del integrated
        del channels
        del block_data
        del cleaned_block_data

    # returns dataframe of 3*n filtered images
    def filter_images(df, n):
        # filter 1000 to 1400 freqs
        freq_1000_1400 = df[(df["freqs"] >= 1000) & (df["freqs"] <= 1400)]
        freq_1000_1400 = freq_1000_1400.sort_values("statistic", ascending=False).head(n)

        # filter 1400 to 1700 freqs
        freq_1400_1700 = df[(df["freqs"] > 1400) & (df["freqs"] <= 1700)]
        freq_1400_1700 = freq_1400_1700.sort_values("statistic", ascending=False).head(n)

        # filter 1700 plus freqs
        freq_1700 = df[df["freqs"] > 1700]
        freq_1700 = freq_1700.sort_values("statistic", ascending=False).head(n)

        extr_all = pd.concat([freq_1000_1400, freq_1400_1700, freq_1700])
        return extr_all

    full_df = pd.concat(frame_list, ignore_index=True)
    full_df.set_index("index")
    full_df.to_pickle(out_dir + "/info_df.pkl")

    if n_coarse_chans == 308:
        filtered_df = filter_images(full_df.reset_index(), 4)
        filtered_stack = np.array([])

    if stack_list:
        full_stack = np.concatenate(stack_list)
        filtered_stack = full_stack[filtered_df.index.values]
        # for i in np.arange(0, len(full_stack)):
        #     if i in filtered_df.index.values:
        #         filtered_stack = np.append(filtered_stack, full_stack[i])

        np.save(out_dir + "/filtered.npy", full_stack)
        if n_coarse_chans == 308:
            np.save(out_dir + "/best_hits.npy", filtered_stack)

    g_end = time()
    print("Finished Energy Detection on %s in %.4f seconds" % (os.path.basename(input_file), g_end - g_start))
