#!/usr/bin/env python3

import os
import numpy as np
from text import text_to_char_array, normalize_txt_file

def get_handwriting_and_transcript(txt_files, hw_files, n_input, n_context):
    '''
    Loads handwriting files and text transcriptions from ordered lists of filenames.
    Converts to handwriting to MFCC arrays and text to numerical arrays.
    Returns list of arrays. Returned handwriting array list can be padded with
    pad_sequences function in this same module.
    '''
    handwriting = []
    handwriting_len = []
    transcript = []
    transcript_len = []

    for txt_file, hw_file in zip(txt_files, hw_files):
        # load handwriting and convert to features
        handwriting_data = handwritingfile_to_input_vector(hw_file, n_input, n_context)
        handwriting_data = handwriting_data.astype('float32')

        handwriting.append(handwriting_data)
        handwriting_len.append(np.int32(len(handwriting_data)))

        # load text transcription and convert to numerical array
        
        target=np.load(txt_file,None) # remove the next 2 lines 
     
        transcript.append(target)
        transcript_len.append(len(target))

    handwriting = np.asarray(handwriting)
    handwriting_len = np.asarray(handwriting_len)
    transcript = np.asarray(transcript)
    transcript_len = np.asarray(transcript_len)
    return handwriting, handwriting_len, transcript, transcript_len


def handwritingfile_to_input_vector(handwriting_filename, n_input, numcontext):
    '''
    Turn an handwriting file into feature representation.

    This function has been modified from Mozilla DeepSpeech:
    https://github.com/mozilla/DeepSpeech/blob/master/util/audio.py

    # This Source Code Form is subject to the terms of the Mozilla Public
    # License, v. 2.0. If a copy of the MPL was not distributed with this
    # file, You can obtain one at http://mozilla.org/MPL/2.0/.
    '''

    
    orig_inputs =np.load(handwriting_filename,None)  # (57,20)
   # print('File name',handwriting_filename);

    # We only keep every second feature (BiRNN stride = 2)
    orig_inputs = orig_inputs[::2]

    # For each time slice of the training set, we need to copy the context this makes
    # the n_input dimensions vector into a n_input + 2*n_input*numcontext dimensions
    # because of:
    #  - n_input dimensions for the current mfcc feature set
    #  - numcontext*n_input dimensions for each of the past and future (x2) mfcc feature set
    # => so n_input + 2*numcontext*n_input    
    train_inputs = np.array([], np.float32)
    train_inputs.resize((orig_inputs.shape[0], n_input + 2 * n_input * numcontext))

    # Prepare pre-fix post fix context
    empty_mfcc = np.array([])
    empty_mfcc.resize((n_input))

    # Prepare train_inputs with past and future contexts
    time_slices = range(train_inputs.shape[0])
    context_past_min = time_slices[0] + numcontext
    context_future_max = time_slices[-1] - numcontext
    for time_slice in time_slices:
        # Reminder: array[start:stop:step]
        # slices from indice |start| up to |stop| (not included), every |step|

        # Add empty context data of the correct size to the start and end
        # of the feature matrix

        # Pick up to numcontext time slices in the past, and complete with empty
        # mfcc features
        need_empty_past = max(0, (context_past_min - time_slice))
        empty_source_past = list(empty_mfcc for empty_slots in range(need_empty_past))
        data_source_past = orig_inputs[max(0, time_slice - numcontext):time_slice]
        assert(len(empty_source_past) + len(data_source_past) == numcontext)

        # Pick up to numcontext time slices in the future, and complete with empty
        # mfcc features
        need_empty_future = max(0, (time_slice - context_future_max))
        empty_source_future = list(empty_mfcc for empty_slots in range(need_empty_future))
        data_source_future = orig_inputs[time_slice + 1:time_slice + numcontext + 1]
        assert(len(empty_source_future) + len(data_source_future) == numcontext)

        if need_empty_past:
            past = np.concatenate((empty_source_past, data_source_past))
        else:
            past = data_source_past

        if need_empty_future:
            future = np.concatenate((data_source_future, empty_source_future))
        else:
            future = data_source_future

        past = np.reshape(past, numcontext * n_input)
        now = orig_inputs[time_slice]
        future = np.reshape(future, numcontext * n_input)

        train_inputs[time_slice] = np.concatenate((past, now, future))
        assert(len(train_inputs[time_slice]) == n_input + 2 * n_input * numcontext)

    # Scale/standardize the inputs
    # This can be done more efficiently in the TensorFlow graph
    train_inputs = (train_inputs - np.mean(train_inputs)) / np.std(train_inputs)
    return train_inputs


def pad_sequences(sequences, maxlen=None, dtype=np.float32,
                  padding='post', truncating='post', value=0.):

    '''
    # From TensorLayer:
    # http://tensorlayer.readthedocs.io/en/latest/_modules/tensorlayer/prepro.html

    Pads each sequence to the same length of the longest sequence.

        If maxlen is provided, any sequence longer than maxlen is truncated to
        maxlen. Truncation happens off either the beginning or the end
        (default) of the sequence. Supports post-padding (default) and
        pre-padding.

        Args:
            sequences: list of lists where each element is a sequence
            maxlen: int, maximum length
            dtype: type to cast the resulting sequence.
            padding: 'pre' or 'post', pad either before or after each sequence.
            truncating: 'pre' or 'post', remove values from sequences larger
            than maxlen either in the beginning or in the end of the sequence
            value: float, value to pad the sequences to the desired value.

        Returns:
            numpy.ndarray: Padded sequences shape = (number_of_sequences, maxlen)
            numpy.ndarray: original sequence lengths
    '''
    lengths = np.asarray([len(s) for s in sequences], dtype=np.int64)

    nb_samples = len(sequences)
    if maxlen is None:
        maxlen = np.max(lengths)

    # take the sample shape from the first non empty sequence
    # checking for consistency in the main loop below.
    sample_shape = tuple()
    for s in sequences:
        if len(s) > 0:
            sample_shape = np.asarray(s).shape[1:]
            break

    x = (np.ones((nb_samples, maxlen) + sample_shape) * value).astype(dtype)
    for idx, s in enumerate(sequences):
        if len(s) == 0:
            continue  # empty list was found
        if truncating == 'pre':
            trunc = s[-maxlen:]
        elif truncating == 'post':
            trunc = s[:maxlen]
        else:
            raise ValueError('Truncating type "%s" not understood' % truncating)

        # check `trunc` has expected shape
        trunc = np.asarray(trunc, dtype=dtype)
        if trunc.shape[1:] != sample_shape:
            raise ValueError('Shape of sample %s of sequence at position %s is different from expected shape %s' %
                             (trunc.shape[1:], idx, sample_shape))

        if padding == 'post':
            x[idx, :len(trunc)] = trunc
        elif padding == 'pre':
            x[idx, -len(trunc):] = trunc
        else:
            raise ValueError('Padding type "%s" not understood' % padding)
    return x, lengths